"""Kiểm thử tất định cho gói nâng cấp chuẩn khóa luận & sư phạm (v5.3).

BẮT BUỘC chạy trên DB cô lập: đặt PYTUTOR_DB_PATH và PYTUTOR_KNOWLEDGE_DB_PATH tới tệp tạm (xem CLAUDE.md §2).
Module tự bỏ qua nếu hai biến này chưa được đặt, để không bao giờ ghi vào pytutor.db gốc.
Không gọi LLM thật: PYTUTOR_DISABLE_LLM=1 được đặt ngay khi nạp module.
"""
from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

os.environ["PYTUTOR_DISABLE_LLM"] = "1"
_ISOLATED = bool(os.getenv("PYTUTOR_DB_PATH")) and bool(os.getenv("PYTUTOR_KNOWLEDGE_DB_PATH"))

from fastapi.testclient import TestClient  # noqa: E402

from backend import database as backend_db  # noqa: E402
from backend.adaptive_policy import select_hint_strategy  # noqa: E402
from backend.auth import create_token  # noqa: E402
from backend.database import (  # noqa: E402
    calculate_autonomy_stars, classify_learning_process, compute_student_model, explain_autonomy_stars, get_class_insights,
    get_class_learning_summary, get_db_connection, get_tutor_feedback_summary, init_db,
)
from backend.guardrails import check_student_output  # noqa: E402
from backend.llm_service import (  # noqa: E402
    build_class_summary_answer, build_offline_chat_reply, build_offline_code_review_reply,build_pass_feedback, build_scaffolding_prompt,
    generate_rule_based_fallback,
)
from backend.main import app  # noqa: E402
from backend.rag.retriever import KB_ROOT, ingest_knowledge_base, list_knowledge_documents, retrieve_knowledge  # noqa: E402
from mcp_server import storage as mcp_storage  # noqa: E402  (test được phép import cả hai phía để so khớp)


def setUpModule():
    if not _ISOLATED:
        raise unittest.SkipTest("Cần đặt PYTUTOR_DB_PATH và PYTUTOR_KNOWLEDGE_DB_PATH tới tệp tạm trước khi chạy.")
    init_db()


def headers(username: str, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_token(username, role, username)}"}


def _ts(minutes_ago: int) -> str:
    return (datetime.now() - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M:%S")


def add_submission(user: str, exercise: str, passed: int, total: int, *, hint: int = 1, action: str = "submit",
                   code: str = "x=1", ts: str | None = None) -> None:
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO submissions(session_id,exercise_id,code,hint_level,passed_tests,total_tests,all_passed,action_type,timestamp) "
            "VALUES(?,?,?,?,?,?,?,?,COALESCE(?, datetime('now','localtime')))",
            (user, exercise, code, hint, passed, total, int(passed == total), action, ts))
        conn.commit()
    finally:
        conn.close()


def add_run(user: str, exercise: str, passed: int, total: int, ts: str | None = None) -> None:
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO practice_runs(username,exercise_id,passed_tests,total_tests,all_passed,timestamp) "
                     "VALUES(?,?,?,?,?,COALESCE(?, datetime('now','localtime')))", (user, exercise, passed, total, int(passed == total), ts))
        conn.commit()
    finally:
        conn.close()


def make_class(class_id: str, owner: str, students: list[str], exercises: list[str]) -> None:
    conn = get_db_connection()
    try:
        conn.execute("INSERT OR REPLACE INTO credit_classes(id,class_code,class_name,instructor_username,enrollment_code) "
                     "VALUES(?,?,?,?,?)", (class_id, f"TU-{class_id}", "Lớp kiểm thử", owner, f"C-{class_id}"))
        for student in students:
            conn.execute("INSERT OR IGNORE INTO class_enrollments(class_id,student_username) VALUES(?,?)", (class_id, student))
        for idx, exercise in enumerate(exercises, 1):
            conn.execute("INSERT OR IGNORE INTO class_exercises(class_id,exercise_id,module_name,order_idx) VALUES(?,?,?,?)",
                         (class_id, exercise, "Chương thử nghiệm", idx))
        conn.commit()
    finally:
        conn.close()


FAIL_NO_LOOP = {
    "all_passed": False, "passed_tests": 1, "total_tests": 3, "summary": "1/3",
    "results": [
        {"test_idx": 1, "status": "PASS", "input": "4", "expected_output": "Chan", "actual_output": "Chan"},
        {"test_idx": 2, "status": "FAIL", "description": "Số lẻ", "input": "7", "expected_output": "Le", "actual_output": "le"},
    ],
}
AST_NO_LOOP = {"valid": True, "has_loops": False, "has_accumulator": False, "structural_summary": "Có 1 câu lệnh if/else."}
EXERCISE = {"title": "Chẵn lẻ", "description": "In Chan hoặc Le."}


class StudentModelSyncTests(unittest.TestCase):
    """S2: hai bản compute_student_model phải đồng bộ cả mã nguồn lẫn kết quả."""

    def test_source_of_both_copies_is_identical(self):
        import inspect
        backend_src = inspect.getsource(backend_db.compute_student_model).replace("get_db_connection()", "get_conn()")
        self.assertEqual(backend_src.strip(), inspect.getsource(mcp_storage.compute_student_model).strip())

    def test_learner_model_logic_lives_in_shared_module(self):
        """v5.6: logic mô hình người học nằm ở pytutor_shared (D1); hai bản chỉ đọc SQL rồi gọi hàm chung."""
        import inspect
        import pathlib
        import pytutor_shared.learner_model as shared
        for module in (backend_db, mcp_storage):
            self.assertIs(module.derive_learner_model, shared.derive_learner_model)
            self.assertIn("derive_learner_model(", inspect.getsource(module.compute_student_model))
        self.assertIs(backend_db.classify_learning_process, shared.classify_learning_process)
        self.assertNotRegex(pathlib.Path(shared.__file__).read_text(encoding="utf-8"),
                            r"(?m)^\s*(from|import)\s+(backend|mcp_server|sqlite3)\b")
        user = "tu_sync_shared"
        add_submission(user, "ex_01_sum_1_to_n", 1, 5)
        add_submission(user, "ex_01_sum_1_to_n", 5, 5)
        add_submission(user, "ex_01_sum_1_to_n", 2, 5, hint=2, action="ask_ai")
        self.assertEqual(compute_student_model(user)["learner_model"], mcp_storage.compute_student_model(user)["learner_model"])

    def test_outputs_match_and_report_sparse_data(self):
        user = "tu_sync_student"
        add_submission(user, "ex_01_sum_1_to_n", 2, 5)
        add_submission(user, "ex_01_sum_1_to_n", 3, 5, hint=2)
        add_submission(user, "ex_01_sum_1_to_n", 5, 5, action="ask_ai")  # không được tính
        backend_model = compute_student_model(user)
        mcp_model = mcp_storage.compute_student_model(user)
        self.assertEqual(backend_model["analytics_metrics"], mcp_model["analytics_metrics"])
        self.assertEqual(backend_model["diagnostic_evaluation"], mcp_model["diagnostic_evaluation"])
        metrics = mcp_model["analytics_metrics"]
        self.assertEqual(metrics["total_submissions"], 2)
        self.assertEqual(metrics["data_status"], "limited")
        self.assertIn("Chưa đủ dữ liệu", mcp_model["diagnostic_evaluation"]["level_classification"])

    def test_recurring_difficulty_and_next_practice(self):
        user = "tu_recurring_student"
        add_submission(user, "ex_01_sum_1_to_n", 0, 5)
        add_submission(user, "ex_01_sum_1_to_n", 0, 5)
        add_submission(user, "ex_01_sum_1_to_n", 2, 5)
        metrics = compute_student_model(user)["analytics_metrics"]
        recurring = metrics["recurring_difficulties"]
        self.assertEqual(len(recurring), 1)
        self.assertEqual(recurring[0]["unsuccessful_submissions"], 3)
        self.assertEqual(recurring[0]["dominant_error"], "syntax_or_runtime")
        self.assertFalse(recurring[0]["resolved"])
        self.assertEqual(metrics["next_practice"]["exercise_id"], "ex_01_sum_1_to_n")
        self.assertEqual(metrics["next_practice"]["reason_code"], "unresolved_recurring")

    def test_labels_do_not_overclaim(self):
        for module in (backend_db, mcp_storage):
            import inspect
            source = inspect.getsource(module.compute_student_model)
            self.assertNotIn("Chuẩn A+", source)
            self.assertNotIn("Senior", source)


class FormativeFeedbackTests(unittest.TestCase):
    """S1.1: phản hồi theo mục tiêu → bằng chứng → bước kế tiếp; không khẳng định thiếu căn cứ."""

    def test_level2_fallback_only_states_observed_evidence(self):
        text = generate_rule_based_fallback(EXERCISE, "x", FAIL_NO_LOOP, AST_NO_LOOP, 2)
        self.assertIn("`7`", text)
        self.assertIn("`Le`", text)
        self.assertIn("chữ hoa/chữ thường", text)  # khác biệt quan sát được
        for unsupported in ("cận trên", "range(1, n)", "n + 1", "vòng lặp của bạn đang dừng sớm"):
            self.assertNotIn(unsupported, text)
        self.assertIn("Bước kế tiếp", text)

    def test_level1_fallback_does_not_reveal_expected_output(self):
        text = generate_rule_based_fallback(EXERCISE, "x", FAIL_NO_LOOP, AST_NO_LOOP, 1)
        self.assertIn("1/3", text)
        # v5.10: Mức 1 không nêu test nào lỗi (mô tả test có thể lộ dạng đầu vào); chỉ gọi tên khái niệm và dạng lỗi tổng quát.
        self.assertNotIn("Số lẻ", text)
        self.assertIn("Khái niệm cần xem lại", text)
        self.assertNotIn("`Le`", text)
        self.assertNotIn("Vòng lặp của bạn", text)  # AST không có vòng lặp thì không hỏi về vòng lặp
        self.assertTrue(check_student_output(text)[0])

    def test_level3_fallback_keeps_skeleton_with_todo(self):
        text = generate_rule_based_fallback(EXERCISE, "x", FAIL_NO_LOOP, AST_NO_LOOP, 3)
        self.assertIn("# TODO", text)
        self.assertIn("Bước 4", text)
        self.assertNotIn("n + 1", text)

    def test_recurring_strategy_changes_next_step_but_not_level(self):
        strategy = select_hint_strategy(1, FAIL_NO_LOOP, [{"hint_level": 1}, {"hint_level": 1}], {})
        self.assertEqual(strategy["strategy"], "recurring_difficulty")
        self.assertEqual(strategy["requested_level"], 1)
        text = generate_rule_based_fallback(EXERCISE, "x", FAIL_NO_LOOP, AST_NO_LOOP, 1, adaptive_strategy=strategy)
        self.assertIn("Chạy từng bước", text)
        self.assertIn("MỨC 1", text)

    def test_pass_feedback_fades_scaffolding(self):
        text = build_pass_feedback(EXERCISE, {"total_tests": 3, "all_passed": True}, AST_NO_LOOP)
        self.assertIn("3/3", text)
        self.assertIn("Tự kiểm lại", text)
        self.assertIn("tùy chọn", text)
        self.assertNotIn("```", text)

    def test_prompt_contains_formative_contract_and_requested_level(self):
        prompt = build_scaffolding_prompt(EXERCISE, "x", FAIL_NO_LOOP, AST_NO_LOOP, 2,
                                          adaptive_strategy=select_hint_strategy(2, FAIL_NO_LOOP, [], {}))
        self.assertIn("KHUNG PHẢN HỒI HÌNH THÀNH", prompt)
        self.assertIn("Bằng chứng", prompt)
        self.assertIn("Level 2", prompt)
        passed = build_scaffolding_prompt(EXERCISE, "x", {"all_passed": True, "results": []}, AST_NO_LOOP, 1)
        self.assertIn("RÚT GIÀN GIÁO", passed)


class RagSourceTests(unittest.TestCase):
    """S1.3: nguồn minh bạch; không gắn nguồn khi không có tài liệu phù hợp."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.index = Path(cls.tmp.name) / "kb.sqlite3"
        cls.chunks = ingest_knowledge_base(KB_ROOT, cls.index)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_in_kb_question_returns_named_section(self):
        docs = retrieve_knowledge("range(1, n) có lấy cả số n không?", index_path=self.index)
        self.assertTrue(docs)
        self.assertEqual(docs[0]["section"], "Vòng lặp và điều kiện dừng")
        self.assertEqual(docs[0]["source"], "python_fundamentals.md")

    def test_out_of_kb_question_returns_no_source(self):
        for question in ("Thời tiết Hà Nội hôm nay thế nào?", "Quy chế học vụ NEU quy định cảnh báo học tập thế nào?"):
            self.assertEqual(retrieve_knowledge(question, index_path=self.index), [], question)

    def test_provenance_line_is_not_indexed_as_knowledge(self):
        self.assertEqual(retrieve_knowledge("giáo trình chính thức của NEU", index_path=self.index), [])

    def test_offline_reply_cites_only_what_it_used(self):
        reply, refs = build_offline_chat_reply([])
        self.assertEqual(refs, [])
        self.assertIn("không trích nguồn", reply)
        docs = retrieve_knowledge("Biến tích lũy khởi tạo bằng 0 hay 1 khi tính tích?", index_path=self.index)
        reply, refs = build_offline_chat_reply(docs)
        self.assertEqual(refs, [{"source": "python_core_topics.md", "section": "Biến tích lũy"}])
        self.assertIn("Biến tích lũy", reply)
        self.assertTrue(check_student_output(reply)[0])

    def test_knowledge_catalogue_lists_documents_with_provenance(self):
        documents = list_knowledge_documents()
        self.assertEqual({d["path"] for d in documents}, {"python_fundamentals.md", "python_core_topics.md"})
        self.assertEqual(sum(d["chunk_count"] for d in documents), self.chunks)
        for doc in documents:
            self.assertIn("biên soạn nội bộ", doc["provenance"])


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.client.__enter__()
        self.student = headers("student", "student")
        self.instructor = headers("gv_tran", "instructor")

    def tearDown(self):
        self.client.__exit__(None, None, None)

    # ---- S1.3 chat ----
    def test_chat_reports_sources_or_explicit_no_source(self):
        base = {"exercise_id": "ex_01_sum_1_to_n", "code": "", "history": []}
        grounded = self.client.post("/api/tutor/chat", json={**base, "user_message": "range(1, n) có lấy cả số n không?"},
                                    headers=self.student).json()
        self.assertEqual(grounded["knowledge_status"], "grounded")
        self.assertEqual(grounded["sources"][0]["section"], "Vòng lặp và điều kiện dừng")
        self.assertTrue(grounded["interaction_id"])
        missing = self.client.post("/api/tutor/chat", json={**base, "user_message": "Công thức nấu phở bò"},
                                   headers=self.student).json()
        self.assertEqual(missing["knowledge_status"], "no_source")
        self.assertEqual(missing["sources"], [])

    # ---- S2.1 lý do sao + tách ask_ai/submit ----
    def _pipeline(self, *, all_passed: bool, history: list[dict]) -> dict:
        total = 3
        return {
            "exercise": {"id": "ex_01_sum_1_to_n", "title": "Tổng 1..n", "description": ""},
            "test_results": {"total_tests": total, "passed_tests": total if all_passed else 1,
                             "failed_tests": 0 if all_passed else 2, "all_passed": all_passed, "summary": "", "results": []},
            "ast_analysis": {"valid": True, "structural_summary": "Có 1 vòng lặp for."},
            "attempt_history": history, "student_model": None, "discovered_tools": [], "mcp_trace": [],
        }

    def _submit(self, action: str, *, all_passed: bool, history: list[dict], exercise: str = "ex_01_sum_1_to_n",
                hint_level: int = 1):
        with patch("backend.main.execute_submission_pipeline", new_callable=AsyncMock,
                   return_value=self._pipeline(all_passed=all_passed, history=history)), \
             patch("backend.main.save_learning_event_via_mcp", new_callable=AsyncMock):
            return self.client.post("/api/submit", headers=self.student, json={
                "exercise_id": exercise, "code": "print(1)", "hint_level": hint_level, "action_type": action}).json()

    def test_submit_pass_explains_stars_and_fades_scaffolding(self):
        ex = "tu_ex_star_rationale"
        add_submission("student", ex, 1, 3, hint=2, action="ask_ai")
        add_submission("student", ex, 1, 3, hint=3, action="submit")  # hint_level của lượt submit fail không được gộp
        # attempt_history (LIMIT 5 phía MCP) không còn là nguồn tính sao: để rỗng vẫn phải ra 2 sao từ DB.
        body = self._submit("submit", all_passed=True, history=[], exercise=ex)
        self.assertEqual(body["stars_earned"], 2)
        rationale = body["star_rationale"]
        self.assertEqual(rationale["stars"], 2)
        self.assertEqual(rationale["max_hint_level_used"], 2)
        self.assertEqual(rationale["attempt_count"], 2)  # 1 lượt nộp fail + lượt nộp này; ask_ai không tính
        self.assertFalse(rationale["is_review_resubmission"])
        self.assertIn("Mức 2", rationale["explanation"])
        self.assertIn("3 sao", rationale["how_to_improve"])
        self.assertIn("bài tiếp theo", rationale["how_to_improve"])
        self.assertNotIn("làm lại bài này và", rationale["how_to_improve"])
        self.assertIn("quy ước", rationale["note"])
        self.assertEqual(body["llm_source"], "System-Celebration")
        self.assertIn("Tự kiểm lại", body["tutor_hint"])
        self.assertIsNone(body["interaction_id"])  # không gọi LLM khi nộp bài đã pass

    def test_ask_ai_never_awards_stars_or_rationale(self):
        body = self._submit("ask_ai", all_passed=True, history=[])
        self.assertEqual(body["stars_earned"], 0)
        self.assertIsNone(body["star_rationale"])
        failing = self._submit("ask_ai", all_passed=False, history=[])
        self.assertEqual(failing["hint_level"], 1)
        self.assertEqual(failing["adaptive_strategy"]["requested_level"], 1)
        self.assertTrue(failing["interaction_id"])  # gợi ý ask_ai đánh giá 👍/👎 được

    # ---- S2.4 chống cày sao ----
    def _stored_stars(self, exercise: str):
        conn = get_db_connection()
        try:
            row = conn.execute("SELECT stars_earned FROM user_exercise_stars WHERE username='student' AND exercise_id=?",
                               (exercise,)).fetchone()
        finally:
            conn.close()
        return row["stars_earned"] if row else None

    def test_resubmitting_cannot_wash_out_level3_hint(self):
        ex = "tu_ex_star_farming"
        add_submission("student", ex, 0, 3, hint=3, action="ask_ai")
        first = self._submit("submit", all_passed=True, history=[], exercise=ex)
        self.assertEqual(first["stars_earned"], 1)
        self.assertEqual(self._stored_stars(ex), 1)
        # Ghi lại lượt pass đầu tiên rồi "cày": 7 lượt nộp lại + hỏi AI Mức 1, đủ để đẩy Mức 3 ra khỏi 5 lượt gần nhất.
        for _ in range(7):
            add_submission("student", ex, 3, 3, hint=1, action="submit")
            add_submission("student", ex, 3, 3, hint=1, action="ask_ai")
        recent_only_level1 = [{"hint_level": 1}] * 5
        again = self._submit("submit", all_passed=True, history=recent_only_level1, exercise=ex)
        self.assertEqual(again["stars_earned"], 1)
        self.assertEqual(again["star_rationale"]["max_hint_level_used"], 3)
        self.assertTrue(again["star_rationale"]["is_review_resubmission"])
        self.assertIn("ôn tập", again["star_rationale"]["explanation"])
        self.assertEqual(self._stored_stars(ex), 1)

    def test_hints_after_first_pass_and_submit_levels_do_not_change_stars(self):
        ex = "tu_ex_star_after_pass"
        add_submission("student", ex, 1, 3, hint=3, action="submit")   # nộp fail với hint_level=3: không phải gợi ý
        add_submission("student", ex, 3, 3, hint=1, action="submit")   # lần pass đầu tiên, chưa hỏi AI
        add_submission("student", ex, 3, 3, hint=3, action="ask_ai")   # hỏi Mức 3 SAU khi đã pass: chỉ là ôn tập
        body = self._submit("submit", all_passed=True, history=[{"hint_level": 3}], exercise=ex)
        self.assertEqual(body["stars_earned"], 3)
        self.assertEqual(body["star_rationale"]["max_hint_level_used"], 1)

    # ---- S1.4 khóa phạm vi chat + luật sao ----
    def _chat(self, exercise: str, message: str, code: str = "CLIENT_ONLY_MARKER = 1"):
        with patch("backend.llm_service.call_gemini_with_usage", new_callable=AsyncMock, return_value=(None, {})) as llm:
            response = self.client.post("/api/tutor/chat", headers=self.student, json={
                "exercise_id": exercise, "code": code, "history": [], "user_message": message})
        self.assertEqual(response.status_code, 200, response.text)
        return response.json(), llm.call_args.args[0]

    def test_chat_before_pass_is_concept_only_and_hides_student_code(self):
        ex = "tu_ex_chat_locked"
        add_submission("student", ex, 1, 3, action="submit", code="FAILED_SUBMIT_MARKER = 1")
        add_submission("student", ex, 3, 3, action="ask_ai", code="ASK_AI_MARKER = 1")  # ask_ai pass không mở khóa
        body, prompt = self._chat(ex, "Sửa giúp em lỗi trong code bài này với")
        self.assertEqual(body["chat_scope"], "concept_only")
        self.assertNotIn("<student_code>", prompt)
        for marker in ("CLIENT_ONLY_MARKER", "FAILED_SUBMIT_MARKER", "ASK_AI_MARKER"):
            self.assertNotIn(marker, prompt)
        self.assertIn("khái niệm Python tổng quát", prompt)
        self.assertIn("Hỏi Gia sư AI", prompt)
        self.assertIn("Hỏi Gia sư AI", body["reply"])       # yêu cầu gỡ code được chuyển hướng
        self.assertEqual(body["sources"], [])
        self.assertTrue(check_student_output(body["reply"])[0])
        concept, _ = self._chat(ex, "range(1, n) có lấy cả số n không?")
        self.assertEqual(concept["knowledge_status"], "grounded")  # câu hỏi khái niệm vẫn được trả lời có nguồn

    def test_chat_after_pass_unlocks_submitted_code_only(self):
        ex = "tu_ex_chat_unlocked"
        add_submission("student", ex, 3, 3, action="submit", code="SUBMITTED_PASS_MARKER = 1")
        body, prompt = self._chat(ex, "Vì sao bài mình đã nộp lại chạy đúng?")
        self.assertEqual(body["chat_scope"], "code_review")
        self.assertIn("<student_code>SUBMITTED_PASS_MARKER = 1</student_code>", prompt)
        self.assertNotIn("CLIENT_ONLY_MARKER", prompt)   # ngữ cảnh là code đã nộp trong DB, không phải code client gửi
        self.assertNotIn("khái niệm Python tổng quát", prompt)

    def test_offline_chat_after_pass_summarises_submitted_structure(self):
        """S8a offline: trả lời nhắc tới bài đã nộp bằng tóm tắt AST (qua MCP), không chép lại mã nguồn."""
        ex = "tu_ex_chat_offline_review"
        submitted = "n = int(input())\ntotal_marker = 0\nfor i in range(1, n + 1):\n    total_marker += i\nprint(total_marker)"
        add_submission("student", ex, 3, 3, action="submit", code=submitted)
        body, prompt = self._chat(ex, "Vì sao code mình đã nộp lại chạy đúng?")
        self.assertEqual(body["chat_scope"], "code_review")
        self.assertIn("<ast_summary>", prompt)              # LLM thật cũng nhận tóm tắt cấu trúc
        reply = body["reply"]
        self.assertIn("code bạn đã nộp", reply)
        self.assertIn("1 vòng lặp for", reply)
        self.assertIn("biến tích lũy", reply)
        self.assertIn("5 dòng", reply)
        self.assertNotIn("Hỏi Gia sư AI", reply)            # không còn chuyển hướng như S3
        for leaked in ("range(1, n + 1)", "total_marker += i", "print(total_marker)", "CLIENT_ONLY_MARKER"):
            self.assertNotIn(leaked, reply)
        self.assertTrue(check_student_output(reply)[0])
        self.assertIn(body["knowledge_status"], ("grounded", "not_applicable"))
        if body["knowledge_status"] == "not_applicable":
            self.assertEqual(body["sources"], [])

    def test_offline_code_review_reply_without_ast_is_honest(self):
        reply = build_offline_code_review_reply("Bài X", "")
        self.assertIn("chưa phân tích được cấu trúc", reply)
        self.assertTrue(check_student_output(reply)[0])

    def test_exercise_detail_reports_has_passed_for_official_pass_only(self):
        ex = "tu_ex_detail_has_passed"
        detail = {"id": ex, "title": "T", "difficulty": "Dễ", "category": "C", "description": "D",
                  "starter_code": "", "test_cases": []}

        def fetch(headers):
            with patch("backend.main.get_exercise_details", new_callable=AsyncMock, return_value=dict(detail)):
                response = self.client.get(f"/api/exercises/{ex}", headers=headers)
            self.assertEqual(response.status_code, 200, response.text)
            return response.json()["has_passed"]

        self.assertFalse(fetch(self.student))
        add_submission("student", ex, 3, 3, action="ask_ai")   # hỏi AI pass không tính
        add_submission("student", ex, 1, 3, action="submit")   # nộp chưa đạt không tính
        self.assertFalse(fetch(self.student))
        add_submission("student", ex, 3, 3, action="submit")
        self.assertTrue(fetch(self.student))
        self.assertFalse(fetch(self.instructor))               # không lộ trạng thái của sinh viên cho vai trò khác

    def test_chat_explains_star_rules_from_system_text(self):
        body, prompt = self._chat("tu_ex_chat_rules", "Làm sao để được 3 điểm nỗ lực?")
        self.assertIn("LUẬT HỆ THỐNG PYTUTOR", prompt)
        for required in ("3⭐", "Mức 2", "Mức 3", "lần nộp đạt đầu tiên", "không phải điểm học phần"):
            self.assertIn(required, prompt)
            self.assertIn(required, body["reply"])
        self.assertEqual(body["knowledge_status"], "not_applicable")

    def test_star_rationale_matches_star_rule(self):
        for level in (1, 2, 3):
            stars = calculate_autonomy_stars(4, level, True)
            rationale = explain_autonomy_stars(stars, level, 4)
            self.assertEqual(rationale["stars"], 4 - level)
            self.assertEqual([r["stars"] for r in rationale["rule"]], [3, 2, 1])

    # ---- S1.2 feedback cho ask_ai & Pythonic Review ----
    def test_hint_and_review_feedback_with_owner_check(self):
        hint = self._submit("ask_ai", all_passed=False, history=[])
        ok = self.client.post("/api/tutor/feedback", headers=self.student,
                              json={"interaction_id": hint["interaction_id"], "rating": -1})
        self.assertEqual(ok.status_code, 201)
        with patch("backend.main.get_exercise_details", new_callable=AsyncMock, return_value={"id": "ex", "title": "T"}), \
             patch("backend.main.run_test_only_pipeline", new_callable=AsyncMock,
                   return_value={"test_results": {"all_passed": True}}):
            review = self.client.post("/api/tutor/pythonic-review", headers=self.student,
                                      json={"exercise_id": "ex_01_sum_1_to_n", "code": "print(1)"}).json()
        self.assertTrue(review["interaction_id"])
        self.assertIn("tham khảo", review["explanation"])  # fallback offline nói rõ giới hạn
        other = self.client.post("/api/tutor/feedback", headers=headers("tu_other_student", "student"),
                                 json={"interaction_id": review["interaction_id"], "rating": 1})
        self.assertEqual(other.status_code, 404)
        mine = self.client.post("/api/tutor/feedback", headers=self.student,
                                json={"interaction_id": review["interaction_id"], "rating": 1})
        self.assertEqual(mine.status_code, 201)
        as_instructor = self.client.post("/api/tutor/feedback", headers=self.instructor,
                                         json={"interaction_id": review["interaction_id"], "rating": 1})
        self.assertEqual(as_instructor.status_code, 403)

    # ---- S3 giảng viên ----
    def test_class_insights_bottlenecks_error_mix_and_support_list(self):
        cid = "tu_insight_class"
        make_class(cid, "gv_tran", ["tu_a", "tu_b", "tu_c", "tu_idle"], ["tu_ex_hard", "tu_ex_easy"])
        for student in ("tu_a", "tu_b"):
            add_submission(student, "tu_ex_hard", 0, 4, ts=_ts(40))
            add_submission(student, "tu_ex_hard", 2, 4, ts=_ts(39))
        for minute in range(30, 24, -1):  # tu_b: 6 lượt chạy thử không tiến bộ → tổng 8 lượt, nhóm Mắc kẹt
            add_run("tu_b", "tu_ex_hard", 1, 4, ts=_ts(minute))
        add_submission("tu_a", "tu_ex_hard", 4, 4, ts=_ts(20))
        add_submission("tu_c", "tu_ex_easy", 4, 4)
        add_submission("tu_c", "tu_ex_hard", 4, 4, action="ask_ai")      # không tính
        add_submission("tu_outsider", "tu_ex_hard", 0, 4)                 # không ghi danh → không tính
        data = self.client.get(f"/api/instructor/classes/{cid}/insights?days=30", headers=self.instructor).json()
        self.assertEqual(data["data_status"], "sufficient")
        self.assertEqual(data["sample"], {"submissions": 6, "active_students": 3, "enrolled_students": 4,
                                          "inactive_students": 1, "exercises_attempted": 2, "exercises_in_class": 2})
        top = data["bottlenecks"][0]
        self.assertEqual(top["exercise_id"], "tu_ex_hard")
        self.assertEqual((top["submissions"], top["unsuccessful"], top["students_attempted"], top["students_passed"]), (5, 4, 2, 1))
        self.assertEqual(data["error_mix"]["zero_pass"], 2)
        self.assertEqual(data["error_mix"]["partial"], 2)
        self.assertEqual(data["error_mix"]["passed"], 2)
        needing = [s["username"] for s in data["students"] if s["needs_support"]]
        self.assertEqual(needing, ["tu_b"])
        self.assertEqual({s["username"]: s["data_status"] for s in data["students"]}["tu_b"], "limited")
        self.assertTrue(any("quy ước vận hành" in c for c in data["caveats"]))

    def test_class_insights_enforce_ownership_and_role(self):
        make_class("tu_private_class", "tu_other_instructor", [], [])
        self.assertEqual(self.client.get("/api/instructor/classes/tu_private_class/insights", headers=self.instructor).status_code, 404)
        self.assertEqual(self.client.get("/api/instructor/classes/tu_private_class/insights", headers=self.student).status_code, 403)
        self.assertEqual(self.client.get("/api/instructor/classes/tu_private_class/insights").status_code, 401)
        self.assertEqual(self.client.get("/api/instructor/knowledge-base", headers=self.student).status_code, 403)
        self.assertEqual(self.client.get("/api/instructor/ai/feedback-summary", headers=self.student).status_code, 403)

    def test_empty_class_reports_no_data(self):
        make_class("tu_empty_class", "gv_tran", ["tu_idle"], ["tu_ex_easy"])
        data = self.client.get("/api/instructor/classes/tu_empty_class/insights", headers=self.instructor).json()
        self.assertEqual(data["data_status"], "no_data")
        self.assertEqual(data["bottlenecks"], [])
        chat = self.client.post("/api/instructor/ai/class-chat", headers=self.instructor,
                                json={"class_id": "tu_empty_class", "user_message": "Lớp đang nghẽn ở đâu?"}).json()
        self.assertEqual(chat["data_status"], "no_data")
        self.assertIn("Chưa có lượt nộp bài chính thức", chat["reply"])

    def test_class_chat_cites_sample_and_never_identities(self):
        cid = "tu_chat_class"
        make_class(cid, "gv_tran", ["tu_chat_a", "tu_chat_b"], ["tu_ex_chat"])
        add_submission("tu_chat_a", "tu_ex_chat", 1, 4)
        add_submission("tu_chat_a", "tu_ex_chat", 1, 4)
        add_submission("tu_chat_b", "tu_ex_chat", 4, 4)
        summary = get_class_learning_summary(cid, 14)
        self.assertNotIn("tu_chat_a", str(summary))
        self.assertNotIn("students", summary)
        chat = self.client.post("/api/instructor/ai/class-chat", headers=self.instructor,
                                json={"class_id": cid, "user_message": "Tóm tắt tình hình lớp", "days": 14}).json()
        self.assertEqual(chat["days"], 14)
        self.assertEqual(chat["data_status"], "limited")
        self.assertEqual(chat["sample"]["submissions"], 3)
        reply = chat["reply"]
        for required in ("14 ngày", "3 lượt nộp", "2/2 sinh viên", "Giới hạn"):
            self.assertIn(required, reply)
        self.assertNotIn("tu_chat_a", reply)
        self.assertNotIn("tu_chat_b", reply)
        other = self.client.post("/api/instructor/ai/class-chat", headers=headers("tu_other_instructor", "instructor"),
                                 json={"class_id": cid, "user_message": "Tóm tắt"})
        self.assertEqual(other.status_code, 404)

    def test_knowledge_base_endpoint_shows_sources_and_provenance(self):
        data = self.client.get("/api/instructor/knowledge-base", headers=self.instructor).json()
        self.assertEqual(data["total_documents"], 2)
        self.assertIn("chưa phải giáo trình chính thức của NEU", data["notice"])
        self.assertIn("Biến tích lũy", next(d for d in data["documents"] if d["path"] == "python_core_topics.md")["sections"])

    def test_feedback_summary_is_counts_only_and_scoped_to_own_classes(self):
        make_class("tu_fb_class", "gv_tran", ["tu_fb_student"], [])
        conn = get_db_connection()
        try:
            for idx, rating in enumerate((1, 1, -1)):
                conn.execute("INSERT OR REPLACE INTO llm_interactions(id,username,role,task_type,status) VALUES(?,?,?,?,?)",
                             (f"tu-fb-{idx}", "tu_fb_student", "student", "adaptive_hint", "fallback"))
                conn.execute("INSERT OR REPLACE INTO tutor_feedback(interaction_id,username,rating) VALUES(?,?,?)",
                             (f"tu-fb-{idx}", "tu_fb_student", rating))
            conn.execute("INSERT OR REPLACE INTO llm_interactions(id,username,role,task_type) VALUES('tu-fb-x','tu_unrelated','student','adaptive_hint')")
            conn.commit()
        finally:
            conn.close()
        summary = get_tutor_feedback_summary("gv_tran", 30)
        hint = next(item for item in summary["by_task"] if item["task_type"] == "adaptive_hint")
        self.assertGreaterEqual(hint["helpful"], 2)
        self.assertGreaterEqual(hint["not_helpful"], 1)
        self.assertNotIn("tu_fb_student", str(summary))
        stranger = get_tutor_feedback_summary("tu_instructor_without_classes", 30)
        self.assertEqual(stranger["total_interactions"], 0)
        self.assertEqual(stranger["data_status"], "no_data")


class ClassSummaryAnswerTests(unittest.TestCase):
    def test_limited_sample_is_flagged(self):
        text = build_class_summary_answer({
            "class": {"class_code": "X"}, "days": 7,
            "metrics": {"submissions": 2, "active_students": 1, "enrolled_students": 30, "exercises_attempted": 1,
                        "pass_rate": 50.0, "data_status": "limited"},
            "error_mix": {"passed_percent": 50.0, "partial_percent": 50.0, "zero_pass_percent": 0.0}, "bottlenecks": []})
        self.assertIn("dưới 3 sinh viên", text)
        self.assertIn("1/30", text)


class BenchmarkReleaseGateTests(unittest.TestCase):
    """S4: khóa ngưỡng phát hành trên corpus cố định (không áp dụng cho tập hold-out)."""

    def test_guardrail_corpus_has_no_leak_and_no_false_positive(self):
        from evaluate_guardrails_benchmark import run
        result = run()
        self.assertEqual(result["attack"]["leaked"], 0, result["attack"]["leaked_ids"])
        self.assertEqual(result["injection"]["missed_ids"], [])
        self.assertEqual(result["benign_inputs"]["false_positives"], 0, result["benign_inputs"]["false_positive_ids"])
        self.assertEqual(result["benign_replies"]["false_positives"], 0, result["benign_replies"]["false_positive_ids"])

    def test_rag_retrieval_does_not_regress(self):
        from evaluate_rag_benchmark import run
        result = run()
        self.assertGreaterEqual(result["in_kb"]["hit_at_3_percent"], 90.0)
        self.assertGreaterEqual(result["in_kb"]["hit_at_1_percent"], 80.0)
        self.assertGreaterEqual(result["out_of_kb"]["no_source_accuracy_percent"], 85.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class ProcessGroupTests(unittest.TestCase):
    """v5.4 B2: phân nhóm quá trình tất định, kiểm tra các biên."""

    @staticmethod
    def run_(n: int, *, lo: int = 0):
        return [{"kind": "run", "passed_tests": lo, "all_passed": False} for _ in range(n)]

    @staticmethod
    def sub(passed: int, total: int = 4):
        return {"kind": "submit", "passed_tests": passed, "all_passed": passed == total}

    @staticmethod
    def ask(level: int):
        return {"kind": "ask", "hint_level": level}

    def test_empty_has_no_group(self):
        self.assertIsNone(classify_learning_process([]))

    def test_practice_only(self):
        self.assertEqual(classify_learning_process(self.run_(3)), "practice_only")
        self.assertEqual(classify_learning_process([self.ask(1)]), "practice_only")

    def test_independent_pass_boundaries(self):
        self.assertEqual(classify_learning_process([self.sub(4)]), "independent_pass")
        self.assertEqual(classify_learning_process([self.sub(1), self.sub(4)]), "independent_pass")  # 2 lượt nộp
        self.assertEqual(classify_learning_process([self.ask(1), self.sub(4)]), "independent_pass")  # gợi ý mức 1
        self.assertEqual(classify_learning_process(self.run_(4) + [self.sub(4)]), "independent_pass")  # 4 lượt chạy thử

    def test_retry_pass_boundaries(self):
        self.assertEqual(classify_learning_process([self.sub(0), self.sub(1), self.sub(4)]), "retry_pass")  # 3 lượt nộp
        self.assertEqual(classify_learning_process(self.run_(5) + [self.sub(4)]), "retry_pass")  # đúng 5 lượt chạy thử

    def test_hint_pass_uses_hint_before_first_pass_only(self):
        self.assertEqual(classify_learning_process([self.ask(2), self.sub(4)]), "hint_pass")
        self.assertEqual(classify_learning_process([self.ask(3), self.sub(1), self.sub(4)]), "hint_pass")
        # gợi ý sau lần đạt đầu không làm đổi nhóm
        self.assertEqual(classify_learning_process([self.sub(4), self.ask(3)]), "independent_pass")

    def test_in_progress_when_few_attempts_or_still_improving(self):
        self.assertEqual(classify_learning_process(self.run_(7)), "practice_only")  # chưa nộp bài nào
        self.assertEqual(classify_learning_process(self.run_(6) + [self.sub(0)]), "in_progress")  # 7 lượt < 8
        events = self.run_(5, lo=1) + [self.sub(1), self.sub(1), self.sub(2)]  # 8 lượt, lượt gần nhất tăng 1 → 2
        self.assertEqual(classify_learning_process(events), "in_progress")

    def test_stuck_requires_eight_attempts_and_no_gain_in_last_five(self):
        events = [self.sub(2)] + self.run_(7, lo=1)  # 8 lượt: tốt nhất 2 đạt ở lượt đầu, 5 lượt gần nhất không tăng
        self.assertEqual(classify_learning_process(events), "stuck")
        # đủ 8 lượt nhưng mức tốt nhất mới đạt trong cửa sổ 5 lượt gần nhất → vẫn đang tiến triển
        self.assertEqual(classify_learning_process(self.run_(7, lo=1) + [self.sub(3)]), "in_progress")
        # ask không tính vào số lượt
        self.assertEqual(classify_learning_process([self.sub(2)] + self.run_(6, lo=1) + [self.ask(1)]), "in_progress")


class PracticeRunsAndInsightsV54Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.student = headers("tu_pr_student", "student")
        cls.instructor = headers("gv_tran", "instructor")

    def _run_test(self, who, passed=2, total=4):
        pipeline = {"test_results": {"all_passed": passed == total, "passed_tests": passed, "total_tests": total,
                                     "failed_tests": total - passed, "summary": f"{passed}/{total}", "results": []},
                    "ast_analysis": AST_NO_LOOP, "mcp_trace": []}
        with patch("backend.main.run_test_only_pipeline", new_callable=AsyncMock, return_value=pipeline):
            return self.client.post("/api/run-test", headers=who,
                                    json={"exercise_id": "ex_01_sum_1_to_n", "code": "SECRET_CODE_MARKER = 1"})

    def _count_runs(self, username):
        conn = get_db_connection()
        try:
            return conn.execute("SELECT COUNT(*) FROM practice_runs WHERE username = ?", (username,)).fetchone()[0]
        finally:
            conn.close()

    def test_student_run_test_is_recorded_without_code(self):
        before = self._count_runs("tu_pr_student")
        resp = self._run_test(self.student)
        self.assertEqual(resp.status_code, 200, resp.text)
        self.assertEqual(self._count_runs("tu_pr_student"), before + 1)
        conn = get_db_connection()
        try:
            columns = [row[1] for row in conn.execute("PRAGMA table_info(practice_runs)").fetchall()]
            dump = str([tuple(row) for row in conn.execute("SELECT * FROM practice_runs").fetchall()])
        finally:
            conn.close()
        self.assertNotIn("code", columns)
        self.assertNotIn("SECRET_CODE_MARKER", dump)

    def test_instructor_run_test_is_not_recorded(self):
        before = self._count_runs("gv_tran")
        self.assertEqual(self._run_test(self.instructor).status_code, 200)
        self.assertEqual(self._count_runs("gv_tran"), before)

    def test_practice_run_does_not_touch_official_metrics(self):
        user = "tu_pr_metrics"
        add_submission(user, "ex_01_sum_1_to_n", 2, 5)
        before = compute_student_model(user)["analytics_metrics"]
        for _ in range(3):
            add_run(user, "ex_01_sum_1_to_n", 5, 5)
        self.assertEqual(compute_student_model(user)["analytics_metrics"], before)

    def test_write_failure_is_not_fatal(self):
        with patch("backend.database.get_db_connection", side_effect=RuntimeError("disk")):
            self.assertFalse(backend_db.save_practice_run("tu_pr_student", "ex", 1, 2, False))

    def test_insights_have_process_groups_for_every_group(self):
        cid = "tu_process_class"
        students = ["tu_p_ind", "tu_p_retry", "tu_p_hint", "tu_p_prog", "tu_p_stuck", "tu_p_only"]
        make_class(cid, "gv_tran", students, ["tu_ex_proc"])
        ex = "tu_ex_proc"
        add_submission("tu_p_ind", ex, 4, 4, ts=_ts(50))
        add_submission("tu_p_retry", ex, 0, 4, ts=_ts(50)); add_submission("tu_p_retry", ex, 1, 4, ts=_ts(49))
        add_submission("tu_p_retry", ex, 4, 4, ts=_ts(48))
        add_submission("tu_p_hint", ex, 1, 4, ts=_ts(50)); add_submission("tu_p_hint", ex, 4, 4, hint=1, ts=_ts(48))
        add_submission("tu_p_hint", ex, 4, 4, hint=2, action="ask_ai", ts=_ts(49))
        add_submission("tu_p_prog", ex, 1, 4, ts=_ts(50))
        add_submission("tu_p_stuck", ex, 2, 4, ts=_ts(50))
        for minute in range(45, 38, -1):
            add_run("tu_p_stuck", ex, 1, 4, ts=_ts(minute))
        add_run("tu_p_only", ex, 3, 4, ts=_ts(30))
        data = self.client.get(f"/api/instructor/classes/{cid}/insights?days=30", headers=self.instructor).json()
        groups = data["process_groups"]
        self.assertEqual(groups["overall"], {"independent_pass": 1, "retry_pass": 1, "hint_pass": 1, "in_progress": 1,
                                             "stuck": 1, "practice_only": 1})
        self.assertEqual(groups["by_exercise"][0]["groups"]["stuck"], 1)
        self.assertEqual([d["key"] for d in groups["definitions"]],
                         ["independent_pass", "retry_pass", "hint_pass", "in_progress", "stuck", "practice_only"])
        self.assertEqual(groups["practice_runs"], 8)
        by_user = {s["username"]: s for s in data["students"]}
        self.assertEqual(by_user["tu_p_stuck"]["process_by_exercise"], {ex: "stuck"})
        self.assertEqual([s["username"] for s in data["students"] if s["needs_support"]], ["tu_p_stuck"])
        self.assertIn("pass_rate", data)  # giữ field để không vỡ client/test cũ
        self.assertTrue(any("v5.4" in c for c in data["caveats"]))

    def test_class_summary_has_process_counts_and_no_identities(self):
        cid = "tu_process_summary"
        make_class(cid, "gv_tran", ["tu_ps_a", "tu_ps_b"], ["tu_ex_ps"])
        add_submission("tu_ps_a", "tu_ex_ps", 4, 4, ts=_ts(20))
        add_submission("tu_ps_b", "tu_ex_ps", 1, 4, ts=_ts(20))
        summary = get_class_learning_summary(cid, 14)
        self.assertEqual(summary["process_groups"]["overall"]["independent_pass"], 1)
        self.assertNotIn("tu_ps_a", str(summary))
        self.assertNotIn("by_exercise", summary["process_groups"])
        text = build_class_summary_answer(summary)
        self.assertIn("Quá trình học", text)
        self.assertIn("Đạt độc lập 1", text)
        self.assertNotIn("tu_ps_a", text)


def make_text_pdf(text: str) -> bytes:
    """PDF tối thiểu có lớp chữ (Helvetica, ASCII) để test trích văn bản."""
    stream = f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode("latin-1")
    objs = [b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
            b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    out, offsets = b"%PDF-1.4\n", []
    for i, body in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    out += b"".join(f"{o:010d} 00000 n \n".encode() for o in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    return out


def make_blank_pdf() -> bytes:
    import io
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def make_docx(heading: str, body: str) -> bytes:
    import io
    from docx import Document
    document = Document()
    document.add_heading(heading, level=1)
    document.add_paragraph(body)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


KB_DECL = {"license_type": "own", "provenance": "Giảng viên tự biên soạn, 2026", "no_personal_data": "true"}
QUIB_MD = ("# Tài liệu lớp\n\n## Quibblefrotz\n\nQuibblefrotz là quy ước đặt tên biến riêng của lớp này. "
           "Quibblefrotz giúp mọi bài nộp có tên biến thống nhất, dễ đọc và dễ chấm.\n").encode("utf-8")


class ClassKnowledgeUploadTests(unittest.TestCase):
    """v5.4 C: tải tài liệu theo lớp, kiểm tra tiêu chuẩn và truy xuất theo phạm vi lớp."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.gv = headers("gv_tran", "instructor")
        cls.other_gv = headers("tu_kb_other_gv", "instructor")
        cls.student_a = headers("tu_kb_stu_a", "student")
        cls.student_b = headers("tu_kb_stu_b", "student")
        make_class("tu_kb_a", "gv_tran", ["tu_kb_stu_a"], ["ex_01_sum_1_to_n"])
        make_class("tu_kb_b", "gv_tran", ["tu_kb_stu_b"], ["ex_01_sum_1_to_n"])
        make_class("tu_kb_full", "gv_tran", [], [])
        make_class("tu_kb_foreign", "tu_kb_other_gv", [], [])

    def upload(self, class_id, filename="quib.md", data=QUIB_MD, who=None, **overrides):
        form = {"title": "Quy ước lớp", **KB_DECL}
        form.update(overrides)
        form = {k: v for k, v in form.items() if v is not None}
        return self.client.post(f"/api/instructor/classes/{class_id}/knowledge", headers=who or self.gv,
                                files={"file": (filename, data)}, data=form)

    def test_upload_md_is_scoped_to_its_class_only(self):
        resp = self.upload("tu_kb_a")
        self.assertEqual(resp.status_code, 201, resp.text)
        doc = resp.json()["document"]
        self.assertIn("Quibblefrotz", doc["sections"])
        self.assertEqual(doc["format"], "md")
        self.assertNotIn("content_text", doc)
        self.assertTrue(retrieve_knowledge("Quibblefrotz là gì", class_id="tu_kb_a"))
        self.assertEqual(retrieve_knowledge("Quibblefrotz là gì", class_id="tu_kb_b"), [])
        self.assertEqual(retrieve_knowledge("Quibblefrotz là gì"), [])  # mặc định chỉ tài liệu chung
        hit = retrieve_knowledge("Quibblefrotz là gì", class_id="tu_kb_a")[0]
        self.assertEqual(hit["scope"], "tu_kb_a")

    def test_default_retrieval_is_unchanged_by_class_documents(self):
        before = retrieve_knowledge("vòng lặp for trong Python là gì")
        self.upload("tu_kb_a", filename="loops.md",
                    data="## Vòng lặp for\n\nVòng lặp for của lớp tu_kb_a lặp qua dãy số.\n".encode("utf-8"))
        after = retrieve_knowledge("vòng lặp for trong Python là gì")
        self.assertEqual([(d["id"], d["score"]) for d in before], [(d["id"], d["score"]) for d in after])

    def test_rejections(self):
        self.assertEqual(self.upload("tu_kb_a", filename="virus.exe", data=b"MZ").status_code, 422)
        self.assertEqual(self.upload("tu_kb_a", data=b"").status_code, 422)
        too_big = self.upload("tu_kb_a", filename="big.txt", data=b"a" * (5 * 1024 * 1024 + 1))
        self.assertEqual(too_big.status_code, 422)
        self.assertIn("quá lớn", too_big.json()["detail"])
        long_text = self.upload("tu_kb_a", filename="long.txt", data=("x " * 80_000).encode())
        self.assertEqual(long_text.status_code, 422)
        self.assertIn("quá dài", long_text.json()["detail"])
        scan = self.upload("tu_kb_a", filename="scan.pdf", data=make_blank_pdf())
        self.assertEqual(scan.status_code, 422)
        self.assertIn("lớp chữ", scan.json()["detail"])
        self.assertEqual(self.upload("tu_kb_a", filename="broken.pdf", data=b"not a pdf").status_code, 422)
        self.assertEqual(self.upload("tu_kb_a", filename="broken.docx", data=b"not a docx").status_code, 422)

    def test_missing_declarations_are_rejected(self):
        self.assertEqual(self.upload("tu_kb_a", license_type=None).status_code, 422)
        self.assertEqual(self.upload("tu_kb_a", license_type="stolen").status_code, 422)
        self.assertEqual(self.upload("tu_kb_a", provenance="  ").status_code, 422)
        self.assertEqual(self.upload("tu_kb_a", no_personal_data=None).status_code, 422)
        self.assertEqual(self.upload("tu_kb_a", no_personal_data="false").status_code, 422)
        self.assertEqual(self.upload("tu_kb_a", license_type="open").status_code, 422)  # thiếu tên giấy phép
        ok = self.upload("tu_kb_a", filename="open.md", license_type="open", license_detail="CC BY 4.0")
        self.assertEqual(ok.status_code, 201, ok.text)
        self.assertIn("CC BY 4.0", ok.json()["document"]["provenance"])

    def test_pdf_and_docx_are_extracted(self):
        pdf = self.upload("tu_kb_a", filename="vars.pdf",
                          data=make_text_pdf("Zorbtastic variables hold values inside a Python program for the class"))
        self.assertEqual(pdf.status_code, 201, pdf.text)
        self.assertTrue(retrieve_knowledge("Zorbtastic variables", class_id="tu_kb_a"))
        docx = self.upload("tu_kb_a", filename="doc.docx",
                           data=make_docx("Flumberwick", "Flumberwick là cách chia hàm thành các bước nhỏ trong lớp học Python."))
        self.assertEqual(docx.status_code, 201, docx.text)
        self.assertIn("Flumberwick", docx.json()["document"]["sections"])  # heading → mục
        self.assertTrue(retrieve_knowledge("Flumberwick là gì", class_id="tu_kb_a"))

    def test_heavy_code_document_warns_but_is_saved(self):
        code_doc = ("## Mẫu\n\n```python\n" + "print('x')\n" * 200 + "```\n\nGhi chú ngắn.\n").encode("utf-8")
        resp = self.upload("tu_kb_a", filename="code.md", data=code_doc)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(any("khối code" in w for w in resp.json()["warnings"]))

    def test_access_control(self):
        self.assertEqual(self.upload("tu_kb_foreign", who=self.gv).status_code, 404)  # không sở hữu lớp
        self.assertEqual(self.upload("tu_kb_a", who=self.student_a).status_code, 403)
        self.assertEqual(self.client.get("/api/instructor/classes/tu_kb_a/knowledge", headers=self.student_a).status_code, 403)
        self.assertEqual(self.client.get("/api/instructor/classes/tu_kb_a/knowledge", headers=self.other_gv).status_code, 404)
        self.assertEqual(self.client.get("/api/instructor/classes/tu_kb_a/knowledge").status_code, 401)
        mine = self.upload("tu_kb_a", filename="mine.md")
        doc_id = mine.json()["document"]["id"]
        self.assertEqual(self.client.delete(f"/api/instructor/classes/tu_kb_foreign/knowledge/{doc_id}", headers=self.gv).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/instructor/classes/tu_kb_a/knowledge/{doc_id}", headers=self.other_gv).status_code, 404)
        # tài liệu của lớp A không xóa/bật tắt được qua lớp khác của cùng giảng viên
        self.assertEqual(self.client.delete(f"/api/instructor/classes/tu_kb_b/knowledge/{doc_id}", headers=self.gv).status_code, 404)
        self.assertEqual(self.client.patch(f"/api/instructor/classes/tu_kb_b/knowledge/{doc_id}", headers=self.gv,
                                           json={"is_active": False}).status_code, 404)

    def test_toggle_and_delete_rebuild_the_index(self):
        data = "## Gluonmarble\n\nGluonmarble là thuật ngữ riêng của lớp học này về hàm và tham số.\n".encode("utf-8")
        doc_id = self.upload("tu_kb_a", filename="glu.md", data=data).json()["document"]["id"]
        self.assertTrue(retrieve_knowledge("Gluonmarble là gì", class_id="tu_kb_a"))
        off = self.client.patch(f"/api/instructor/classes/tu_kb_a/knowledge/{doc_id}", headers=self.gv, json={"is_active": False})
        self.assertEqual(off.status_code, 200)
        self.assertEqual(retrieve_knowledge("Gluonmarble là gì", class_id="tu_kb_a"), [])
        listing = self.client.get("/api/instructor/classes/tu_kb_a/knowledge", headers=self.gv).json()
        self.assertFalse(next(d for d in listing["documents"] if d["id"] == doc_id)["is_active"])
        self.client.patch(f"/api/instructor/classes/tu_kb_a/knowledge/{doc_id}", headers=self.gv, json={"is_active": True})
        self.assertTrue(retrieve_knowledge("Gluonmarble là gì", class_id="tu_kb_a"))
        self.assertEqual(self.client.delete(f"/api/instructor/classes/tu_kb_a/knowledge/{doc_id}", headers=self.gv).status_code, 200)
        self.assertEqual(retrieve_knowledge("Gluonmarble là gì", class_id="tu_kb_a"), [])

    def test_per_class_limit(self):
        for i in range(20):
            self.assertEqual(self.upload("tu_kb_full", filename=f"d{i}.md", data=f"## M{i}\n\nNội dung số {i} của lớp.\n".encode()).status_code, 201)
        over = self.upload("tu_kb_full", filename="extra.md")
        self.assertEqual(over.status_code, 422)
        self.assertIn("tối đa 20", over.json()["detail"])

    def test_chat_cites_class_document_only_for_enrolled_class(self):
        self.upload("tu_kb_a", filename="quib2.md")
        body = {"exercise_id": "ex_01_sum_1_to_n", "code": "", "user_message": "Quibblefrotz trong Python là gì?",
                "class_id": "tu_kb_a"}
        mine = self.client.post("/api/tutor/chat", headers=self.student_a, json=body).json()
        self.assertEqual(mine["knowledge_status"], "grounded", mine)
        self.assertTrue(any(src.get("origin") == "class" for src in mine["sources"]))
        self.assertIn("giảng viên lớp cung cấp", mine["reply"])
        other = self.client.post("/api/tutor/chat", headers=self.student_b, json={**body, "class_id": "tu_kb_b"}).json()
        self.assertNotEqual(other["knowledge_status"], "grounded")
        self.assertEqual(other["sources"], [])
        self.assertNotIn("Quibblefrotz là quy ước", other["reply"])
        # không đọc được tài liệu lớp A bằng cách khai class_id của lớp mình chưa ghi danh
        forged = self.client.post("/api/tutor/chat", headers=self.student_b, json={**body, "class_id": "tu_kb_a"})
        self.assertEqual(forged.status_code, 403)
