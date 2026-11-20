"""Kiểm thử mô hình người học v3 (module dùng chung, đặc trưng lượt, chính sách thích ứng, fallback offline).

BẮT BUỘC chạy trên DB cô lập: đặt PYTUTOR_DB_PATH và PYTUTOR_KNOWLEDGE_DB_PATH tới tệp tạm (xem CLAUDE.md §2).
Module tự bỏ qua nếu hai biến này chưa được đặt. Không gọi LLM thật.
"""
from __future__ import annotations

import itertools
import os
import re
import unittest
from unittest.mock import AsyncMock, patch

os.environ["PYTUTOR_DISABLE_LLM"] = "1"
_ISOLATED = bool(os.getenv("PYTUTOR_DB_PATH")) and bool(os.getenv("PYTUTOR_KNOWLEDGE_DB_PATH"))

from fastapi.testclient import TestClient  # noqa: E402

from backend import database as backend_db  # noqa: E402
from backend.adaptive_policy import select_hint_strategy  # noqa: E402
from backend.auth import create_token  # noqa: E402
from backend.database import compute_student_model, get_db_connection, init_db  # noqa: E402
from backend.guardrails import enforce_level3_skeleton  # noqa: E402
from backend.llm_service import build_pass_feedback, build_scaffolding_prompt, generate_rule_based_fallback  # noqa: E402
from backend.main import app  # noqa: E402
from mcp_server import storage as mcp_storage  # noqa: E402
from pytutor_shared import learner_model as lm  # noqa: E402

EX1, EX2, EX3, EX4 = "ex_01_sum_1_to_n", "ex_02_prime_check", "ex_03_factorial", "ex_04_reverse_string"
ENDPOINT = "/api/instructor/classes/{}/students/{}/learner-model"

FAIL = {
    "all_passed": False, "passed_tests": 1, "total_tests": 3, "summary": "1/3",
    "results": [
        {"test_idx": 1, "status": "PASS", "input": "4", "expected_output": "Chan", "actual_output": "Chan"},
        {"test_idx": 2, "status": "FAIL", "description": "Số lẻ", "input": "7", "expected_output": "Le", "actual_output": "le"},
    ],
}
SYNTAX = {"all_passed": False, "passed_tests": 0, "total_tests": 3,
          "results": [{"test_idx": 1, "status": "SYNTAX_ERROR", "error_message": "invalid syntax"}]}
PASSED = {"all_passed": True, "passed_tests": 3, "total_tests": 3, "results": []}
AST = {"valid": True, "has_loops": True, "has_accumulator": False, "structural_summary": "Có 1 vòng lặp for."}
EXERCISE = {"title": "Bài thử", "description": "Mô tả."}


def setUpModule():
    if not _ISOLATED:
        raise unittest.SkipTest("Cần đặt PYTUTOR_DB_PATH và PYTUTOR_KNOWLEDGE_DB_PATH tới tệp tạm trước khi chạy.")
    init_db()


def headers(username: str, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_token(username, role, username)}"}


def add_sub(user: str, exercise: str, passed: int, total: int = 3, *, hint: int = 1, action: str = "submit",
            llm_source: str = "", ts: str | None = None, features: dict | None = None) -> int:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "INSERT INTO submissions(session_id,exercise_id,code,hint_level,passed_tests,total_tests,all_passed,action_type,llm_source,timestamp) "
            "VALUES(?,?,?,?,?,?,?,?,?,COALESCE(?, datetime('now','localtime')))",
            (user, exercise, "x=1", hint, passed, total, int(passed == total), action, llm_source, ts))
        sid = cur.lastrowid
        if features:
            conn.execute("INSERT INTO attempt_features(submission_id,error_class,status_counts,ast_flags) VALUES(?,?,?,?)",
                         (sid, features["error_class"], "{}", "{}"))
        conn.commit()
        return sid
    finally:
        conn.close()


def add_run(user: str, exercise: str, passed: int, total: int = 3) -> None:
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO practice_runs(username,exercise_id,passed_tests,total_tests,all_passed) VALUES(?,?,?,?,?)",
                     (user, exercise, passed, total, int(passed == total)))
        conn.commit()
    finally:
        conn.close()


def concept(model: dict, kc: str) -> dict:
    return next(c for c in model["learner_model"]["concepts"] if c["kc"] == kc)


def make_class(class_id: str, owner: str, students: list[str], exercises: list[str]) -> None:
    conn = get_db_connection()
    try:
        conn.execute("INSERT OR REPLACE INTO credit_classes(id,class_code,class_name,instructor_username,enrollment_code) "
                     "VALUES(?,?,?,?,?)", (class_id, f"LM-{class_id}", "Lớp kiểm thử mô hình", owner, f"C-{class_id}"))
        for s in students:
            conn.execute("INSERT OR IGNORE INTO class_enrollments(class_id,student_username) VALUES(?,?)", (class_id, s))
        for i, e in enumerate(exercises, 1):
            conn.execute("INSERT OR IGNORE INTO class_exercises(class_id,exercise_id,module_name,order_idx) VALUES(?,?,?,?)",
                         (class_id, e, "Chương thử nghiệm", i))
        conn.commit()
    finally:
        conn.close()


def struggling_loop_user(user: str) -> dict:
    """loop vướng: EX1 nộp sai 2 lần; EX2 đã đạt. (EX3 chưa thử.)"""
    add_sub(user, EX1, 1)
    add_sub(user, EX1, 1)
    add_sub(user, EX2, 3)
    return compute_student_model(user)


def secure_loop_user(user: str) -> dict:
    """loop vững: EX1, EX2 đạt không gợi ý."""
    add_sub(user, EX1, 3)
    add_sub(user, EX2, 3)
    return compute_student_model(user)


def high_reliance_user(user: str) -> dict:
    """>= 3 bài có hỏi gợi ý từ Mức 2 (mô tả quá trình), 3 bài khác nhau có submit (dữ liệu đủ)."""
    for ex in (EX1, EX2, EX4):
        add_sub(user, ex, 1, hint=1)
        add_sub(user, ex, 1, hint=2, action="ask_ai")
        add_sub(user, ex, 3)
    return compute_student_model(user)


class KnowledgeComponentTests(unittest.TestCase):
    def test_kc_assignment_is_deterministic_table(self):
        self.assertEqual(lm.assign_kcs("Vòng lặp & Biến tích lũy"), ["io_format", "loop", "accumulator"])
        self.assertEqual(lm.assign_kcs("Cấu trúc rẽ nhánh & Vòng lặp"), ["io_format", "conditional", "loop"])
        self.assertEqual(lm.assign_kcs("Vòng lặp / Đệ quy"), ["io_format", "loop", "recursion"])
        self.assertEqual(lm.assign_kcs("Chuỗi & Chỉ mục (String Indexing)"), ["io_format", "string"])
        self.assertEqual(lm.assign_kcs("", "Chương 3: Phương thức & Đệ quy", "Đệ quy & Hàm chuẩn"), ["io_format", "recursion"])
        self.assertEqual(lm.assign_kcs("", "Chương 1", "Tư duy thuật toán"), ["io_format"])
        self.assertEqual(lm.assign_kcs(None, None, None), ["io_format"])
        self.assertEqual(lm.assign_kcs("Vòng lặp"), lm.assign_kcs("Vòng lặp"))  # tất định
        self.assertEqual(lm.KC_KEYS, ["io_format", "conditional", "loop", "accumulator", "string", "recursion"])

    def test_model_lists_all_six_kcs_even_without_data(self):
        model = compute_student_model("lm_empty_user")
        learner = model["learner_model"]
        self.assertEqual(learner["model_version"], "3")
        self.assertEqual([c["kc"] for c in learner["concepts"]], lm.KC_KEYS)
        self.assertTrue(all(c["state"] == "no_evidence" for c in learner["concepts"]))
        self.assertEqual(learner["support_profile"]["hint_reliance"], "unknown")
        self.assertIn("chưa hiệu chuẩn", learner["disclaimer"])
        self.assertEqual(model["analytics_metrics"]["metric_definition_version"], "2")

    def test_exercise_kcs_follow_seed_categories(self):
        learner = compute_student_model("lm_empty_user")["learner_model"]
        self.assertIn("loop", learner["exercise_kcs"][EX1])
        self.assertIn("accumulator", learner["exercise_kcs"][EX1])
        self.assertIn("string", learner["exercise_kcs"][EX4])


class StateRuleTests(unittest.TestCase):
    def test_one_failing_exercise_is_not_enough_to_be_struggling(self):
        user = "lm_state_one"
        add_sub(user, EX1, 1)
        self.assertEqual(concept(compute_student_model(user), "loop")["state"], "developing")
        add_sub(user, EX1, 1)  # lần nộp sai thứ hai trên cùng bài
        model = compute_student_model(user)
        self.assertEqual(concept(model, "loop")["state"], "struggling")
        self.assertEqual(concept(model, "loop")["data_status"], "limited")  # mới 1 bài

    def test_secure_needs_two_passed_exercises(self):
        one, two = "lm_secure_one", "lm_secure_two"
        add_sub(one, EX1, 3)
        self.assertEqual(concept(compute_student_model(one), "loop")["state"], "developing")
        add_sub(two, EX1, 3)
        add_sub(two, EX2, 3)
        model = compute_student_model(two)
        self.assertEqual(concept(model, "loop")["state"], "secure")
        self.assertEqual(concept(model, "loop")["data_status"], "sufficient")
        self.assertIn("tự lực", concept(model, "loop")["explanation"])
        self.assertEqual(concept(model, "string")["state"], "no_evidence")

    def test_ask_ai_does_not_change_official_metrics(self):
        user = "lm_ask_boundary"
        for ex in (EX1, EX2, EX4):
            add_sub(user, ex, 1)
            add_sub(user, ex, 3)
        before = compute_student_model(user)
        for ex in (EX1, EX2, EX4):
            add_sub(user, ex, 0, hint=3, action="ask_ai")
            add_run(user, ex, 2)
        after = compute_student_model(user)
        self.assertEqual(before["analytics_metrics"], after["analytics_metrics"])
        self.assertEqual([c["state"] for c in before["learner_model"]["concepts"]],
                         [c["state"] for c in after["learner_model"]["concepts"]])
        self.assertEqual(before["learner_model"]["support_profile"]["ask_ai_count"], 0)
        self.assertEqual(after["learner_model"]["support_profile"]["ask_ai_count"], 3)
        self.assertEqual(after["learner_model"]["support_profile"]["label"], "descriptive_process")
        self.assertTrue(all(p["label"] == "descriptive_process" for p in after["learner_model"]["process_by_exercise"]))

    def test_exam_mode_guard_asks_are_excluded(self):
        user = "lm_exam_guard"
        add_sub(user, EX1, 0, hint=3, action="ask_ai", llm_source="Exam-Mode-Guard")
        add_sub(user, EX1, 0, hint=2, action="ask_ai", llm_source="Pedagogical-Rule-Engine")
        self.assertEqual(compute_student_model(user)["learner_model"]["support_profile"]["ask_ai_count"], 1)

    def test_hint_reliance_levels(self):
        self.assertEqual(high_reliance_user("lm_reliance_high")["learner_model"]["support_profile"]["hint_reliance"], "high")
        low = secure_loop_user("lm_reliance_low")["learner_model"]["support_profile"]["hint_reliance"]
        self.assertEqual(low, "low")


class SharedModuleSyncTests(unittest.TestCase):
    def test_backend_and_mcp_return_identical_learner_model(self):
        user = "lm_sync_user"
        add_sub(user, EX1, 1, features={"error_class": "logic_partial"})
        add_sub(user, EX1, 0, features={"error_class": "syntax"})
        add_sub(user, EX2, 3)
        add_sub(user, EX2, 1, hint=2, action="ask_ai")
        add_run(user, EX1, 2)
        a, b = compute_student_model(user), mcp_storage.compute_student_model(user)
        self.assertEqual(a["learner_model"], b["learner_model"])
        self.assertEqual(a, b)
        self.assertEqual(a["learner_model"]["error_profile"]["counts"], {"logic_partial": 1, "syntax": 1})

    def test_both_modules_use_the_shared_implementation(self):
        import inspect
        for module in (backend_db, mcp_storage):
            self.assertIn("derive_learner_model", inspect.getsource(module.compute_student_model))
            self.assertIs(module.derive_learner_model, lm.derive_learner_model)

    def test_shared_module_has_no_forbidden_imports(self):
        import pathlib
        source = pathlib.Path(lm.__file__).read_text(encoding="utf-8")
        self.assertNotRegex(source, r"(?m)^\s*(from|import)\s+(backend|mcp_server|sqlite3)\b")


class AttemptFeatureTests(unittest.TestCase):
    def test_summarize_attempt_features_classes(self):
        self.assertEqual(lm.summarize_attempt_features(PASSED, AST)["error_class"], "passed")
        self.assertEqual(lm.summarize_attempt_features(SYNTAX, {"valid": False})["error_class"], "syntax")
        self.assertEqual(lm.summarize_attempt_features(FAIL, AST)["error_class"], "logic_partial")
        self.assertEqual(lm.summarize_attempt_features(
            {"results": [{"status": "TIMEOUT"}]}, AST)["error_class"], "timeout")
        self.assertEqual(lm.summarize_attempt_features(
            {"results": [{"status": "RUNTIME_ERROR"}]}, AST)["error_class"], "runtime")
        self.assertEqual(lm.summarize_attempt_features(
            {"passed_tests": 0, "results": [{"status": "FAIL"}]}, AST)["error_class"], "logic_none")
        flags = lm.summarize_attempt_features(FAIL, AST)["ast_flags"]
        self.assertTrue(flags["has_loops"])
        self.assertFalse(flags["has_recursion"])

    def test_mcp_and_backend_save_submission_write_features(self):
        feats = lm.summarize_attempt_features(FAIL, AST)
        sid_mcp = mcp_storage.save_submission("lm_feat_user", EX1, "x", 1, 1, 3, False, "t", "h", "submit", attempt_features=feats)
        sid_be = backend_db.save_submission("lm_feat_user", EX1, "x", 1, 1, 3, False, "t", "h", attempt_features=feats)
        conn = get_db_connection()
        try:
            rows = {r["submission_id"]: r["error_class"] for r in conn.execute(
                "SELECT submission_id, error_class FROM attempt_features WHERE submission_id IN (?,?)", (sid_mcp, sid_be))}
        finally:
            conn.close()
        self.assertEqual(rows, {sid_mcp: "logic_partial", sid_be: "logic_partial"})
        model = compute_student_model("lm_feat_user")
        self.assertEqual(model["learner_model"]["feature_coverage_percent"], 100.0)

    def test_save_without_features_still_works_and_legacy_rows_reported(self):
        user = "lm_legacy_user"
        add_sub(user, EX1, 1)
        add_sub(user, EX1, 0)
        mcp_storage.save_submission(user, EX1, "x", 1, 1, 3, False, "t", "h")  # không có đặc trưng
        learner = compute_student_model(user)["learner_model"]
        self.assertEqual(learner["feature_coverage_percent"], 0.0)
        self.assertEqual(learner["error_profile"]["counts"], {"logic_partial": 2, "zero_pass": 1})

    def test_get_attempts_reports_action_type(self):
        user = "lm_attempts_user"
        add_sub(user, EX3, 1, action="ask_ai")
        add_sub(user, EX3, 1)
        for module in (backend_db, mcp_storage):
            rows = module.get_attempts(user, EX3)
            self.assertEqual([r["action_type"] for r in rows], ["submit", "ask_ai"])

    def test_init_db_is_idempotent_and_additive(self):
        add_sub("lm_idem_user", EX1, 1, features={"error_class": "logic_partial"})
        conn = get_db_connection()
        before = conn.execute("SELECT COUNT(*) FROM attempt_features").fetchone()[0]
        conn.close()
        init_db()
        init_db()
        conn = get_db_connection()
        try:
            after = conn.execute("SELECT COUNT(*) FROM attempt_features").fetchone()[0]
            cols = [r[1] for r in conn.execute("PRAGMA table_info(attempt_features)")]
        finally:
            conn.close()
        self.assertEqual(before, after)
        self.assertEqual(cols, ["submission_id", "error_class", "status_counts", "ast_flags", "feature_version", "created_at",
                                "failed_tests", "format_mismatch_tests"])  # v5.7: chỉ ADD COLUMN


class PolicyTests(unittest.TestCase):
    def test_requested_level_never_changes_for_any_combination(self):
        models = [None, {}, struggling_loop_user("lm_pol_a"), secure_loop_user("lm_pol_b"), high_reliance_user("lm_pol_c"),
                  compute_student_model("lm_pol_empty")]
        tests = [FAIL, SYNTAX, PASSED, {"results": []}, {}]
        histories = [[], [{"hint_level": 1}], [{"hint_level": 3, "action_type": "ask_ai"}, {"hint_level": 1, "action_type": "submit"}],
                     [{"hint_level": 1}] * 5]
        for level, tr, hist, model, use, ex in itertools.product(
                (1, 2, 3), tests, histories, models, (True, False), (None, EX3, "unknown_exercise")):
            result = select_hint_strategy(level, tr, hist, model, exercise_id=ex, use_learner_model=use)
            self.assertEqual(result["requested_level"], level)
            self.assertIn(result["strategy"], {"conceptual_start", "failed_case_diagnosis", "recurring_difficulty", "solution_review"})
            self.assertEqual(result["reason_code"], result["strategy"])
            self.assertEqual(result["policy_version"], "3")
            self.assertFalse(any("hint_level" in str(k) and k != "previous_hint_levels" for k in result))

    def test_concept_recurring_difficulty_uses_other_exercises(self):
        model = struggling_loop_user("lm_pol_concept")
        result = select_hint_strategy(2, FAIL, [], model, exercise_id=EX3)
        self.assertEqual(result["strategy"], "recurring_difficulty")
        self.assertIn("concept_recurring_difficulty", result["adaptation_codes"])
        self.assertTrue(any("concepts[loop]" in f for f in result["model_fields_used"]))
        baseline = select_hint_strategy(2, FAIL, [], model, exercise_id=EX3, use_learner_model=False)
        self.assertEqual(baseline["strategy"], "failed_case_diagnosis")
        self.assertEqual(baseline["adaptations"], [])
        self.assertEqual(baseline["learner_signals"], {})

    def test_evidence_of_current_exercise_is_not_double_counted(self):
        user = "lm_pol_double"
        add_sub(user, EX1, 1)
        add_sub(user, EX1, 1)  # chỉ bài hiện tại có lịch sử sai
        model = compute_student_model(user)
        result = select_hint_strategy(1, FAIL, [], model, exercise_id=EX1)
        self.assertEqual(result["strategy"], "failed_case_diagnosis")
        self.assertNotIn("concept_recurring_difficulty", result["adaptation_codes"])

    def test_gate_closed_for_limited_and_no_data(self):
        user = "lm_pol_limited"
        add_sub(user, EX1, 1)
        add_sub(user, EX1, 1)  # struggling nhưng chỉ có 1 bài khác chung KC với EX2/EX3
        limited = compute_student_model(user)
        empty = compute_student_model("lm_pol_nodata")
        self.assertEqual(limited["analytics_metrics"]["data_status"], "limited")
        self.assertEqual(empty["analytics_metrics"]["data_status"], "no_data")
        for model in (limited, empty):
            result = select_hint_strategy(1, FAIL, [], model, exercise_id=EX2)
            self.assertEqual(result["strategy"], "failed_case_diagnosis")
            self.assertEqual(result["adaptation_codes"], [])
            self.assertEqual(result["model_fields_used"], [])
            self.assertEqual(result["granularity"], "standard")

    def test_policy_runs_without_exercise_id(self):
        model = struggling_loop_user("lm_pol_noex")
        result = select_hint_strategy(1, FAIL, [], model)
        self.assertEqual(result["strategy"], "failed_case_diagnosis")
        self.assertEqual(result["adaptation_codes"], [])

    def test_bridge_from_mastered_and_repeated_error_type(self):
        model = secure_loop_user("lm_pol_bridge")
        start = select_hint_strategy(1, {"results": []}, [], model, exercise_id=EX3)
        self.assertEqual(start["strategy"], "conceptual_start")
        self.assertIn("bridge_from_mastered", start["adaptation_codes"])
        # lỗi lặp: hai bài khác cùng KC đều sai kiểu logic_partial, chưa vướng (mỗi bài chỉ 1 lần nộp sai)
        user = "lm_pol_repeat"
        add_sub(user, EX1, 1, features={"error_class": "logic_partial"})
        add_sub(user, EX2, 1, features={"error_class": "logic_partial"})
        diag = select_hint_strategy(1, FAIL, [], compute_student_model(user), exercise_id=EX3)
        self.assertEqual(diag["strategy"], "failed_case_diagnosis")
        self.assertEqual(diag["diagnosis_focus"], "logic_partial")
        self.assertIn("repeated_error_type", diag["adaptation_codes"])

    def test_granularity_fine_and_coarse_and_independence(self):
        fine_model = high_reliance_user("lm_pol_fine")
        fine = select_hint_strategy(2, FAIL, [], fine_model, exercise_id=EX3)
        self.assertEqual(fine["granularity"], "fine")
        self.assertIn("granularity_fine", fine["adaptation_codes"])
        passed = select_hint_strategy(1, PASSED, [], fine_model, exercise_id=EX3)
        self.assertEqual(passed["strategy"], "solution_review")
        self.assertIn("independence_check", passed["adaptation_codes"])
        self.assertIn("tùy chọn", build_pass_feedback(EXERCISE, PASSED, AST, adaptive_strategy=passed))
        self.assertNotIn("Gợi ý cho bài sau", build_pass_feedback(EXERCISE, PASSED, AST))
        coarse_user = "lm_pol_coarse"
        for ex in (EX1, EX2, EX3, EX4):
            add_sub(coarse_user, ex, 3)
        coarse = select_hint_strategy(1, FAIL, [], compute_student_model(coarse_user), exercise_id=EX1)
        self.assertEqual(coarse["granularity"], "coarse")
        self.assertIn("self_check_first", coarse["adaptation_codes"])
        for result in (fine, coarse):
            self.assertEqual(result["requested_level"], 2 if result is fine else 1)


class PromptAndFallbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.concept_model = struggling_loop_user("lm_txt_concept")
        cls.bridge_model = secure_loop_user("lm_txt_bridge")
        cls.fine_model = high_reliance_user("lm_txt_fine")

    def test_prompt_has_model_section_only_with_model_and_keeps_level(self):
        on = select_hint_strategy(2, FAIL, [], self.concept_model, exercise_id=EX3)
        off = select_hint_strategy(2, FAIL, [], self.concept_model, exercise_id=EX3, use_learner_model=False)
        prompt_on = build_scaffolding_prompt(EXERCISE, "x", FAIL, AST, 2, adaptive_strategy=on, student_model=self.concept_model)
        prompt_off = build_scaffolding_prompt(EXERCISE, "x", FAIL, AST, 2, adaptive_strategy=off, student_model=self.concept_model)
        self.assertIn("[MÔ HÌNH NGƯỜI HỌC", prompt_on)
        self.assertIn("concept_recurring_difficulty", prompt_on)
        self.assertIn("Giữ nguyên cấp độ người học yêu cầu: Level 2", prompt_on)
        self.assertNotIn("[MÔ HÌNH NGƯỜI HỌC", prompt_off)

    def test_fallback_differs_by_profile_but_baseline_is_unchanged(self):
        for level in (1, 2, 3):
            base = generate_rule_based_fallback(EXERCISE, "x", FAIL, AST, level)
            off = select_hint_strategy(level, FAIL, [], self.fine_model, exercise_id=EX3, use_learner_model=False)
            self.assertEqual(generate_rule_based_fallback(EXERCISE, "x", FAIL, AST, level, adaptive_strategy=off), base)
            fine = select_hint_strategy(level, FAIL, [], self.fine_model, exercise_id=EX3)
            fine_text = generate_rule_based_fallback(EXERCISE, "x", FAIL, AST, level, adaptive_strategy=fine)
            self.assertNotEqual(fine_text, base)
            self.assertIn("chia nhỏ thành 2 bước", fine_text)
            self.assertIn(f"MỨC {level}", fine_text)
        concept = select_hint_strategy(1, FAIL, [], self.concept_model, exercise_id=EX3)
        self.assertIn("từng gây vướng", generate_rule_based_fallback(EXERCISE, "x", FAIL, AST, 1, adaptive_strategy=concept))
        bridge = select_hint_strategy(1, {"results": []}, [], self.bridge_model, exercise_id=EX3)
        self.assertIn("Nối với điều bạn đã làm",
                      generate_rule_based_fallback(EXERCISE, "x", {"results": []}, AST, 1, adaptive_strategy=bridge))

    def test_coarse_fallback_is_single_question_with_self_check(self):
        user = "lm_txt_coarse"
        for ex in (EX1, EX2, EX3, EX4):
            add_sub(user, ex, 3)
        coarse = select_hint_strategy(2, FAIL, [], compute_student_model(user), exercise_id=EX1)
        text = generate_rule_based_fallback(EXERCISE, "x", FAIL, AST, 2, adaptive_strategy=coarse)
        self.assertIn("tự kiểm trước", text)
        self.assertIn("MỨC 2", text)

    def test_level3_notes_stay_outside_code_block_and_pass_skeleton_guard(self):
        fenced = re.compile(r"```python\n(.*?)```", re.S)
        base = generate_rule_based_fallback(EXERCISE, "x", FAIL, AST, 3)
        for strategy in (select_hint_strategy(3, FAIL, [], self.fine_model, exercise_id=EX3),
                         select_hint_strategy(3, FAIL, [], self.concept_model, exercise_id=EX3)):
            text = generate_rule_based_fallback(EXERCISE, "x", FAIL, AST, 3, adaptive_strategy=strategy)
            self.assertEqual(fenced.findall(text), fenced.findall(base))  # khối mã y hệt bản gốc
            self.assertEqual(text.count("```"), 2)
            masked_text, masked = enforce_level3_skeleton(text)
            self.assertEqual(masked, 0)
            self.assertEqual(masked_text, text)
            self.assertIn("# TODO", text)
            self.assertIn("MỨC 3", text)

    def test_level3_prompt_still_requires_skeleton(self):
        strategy = select_hint_strategy(3, FAIL, [], self.fine_model, exercise_id=EX3)
        prompt = build_scaffolding_prompt(EXERCISE, "x", FAIL, AST, 3, adaptive_strategy=strategy, student_model=self.fine_model)
        self.assertIn("KHUNG CODE MẪU", prompt)
        self.assertIn("Level 3", prompt)


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.student = headers("lm_api_student", "student")
        cls.owner = headers("gv_tran", "instructor")
        cls.other_instructor = headers("gv_tuan", "instructor")
        make_class("lm_api_class", "gv_tran", ["lm_api_student"], [EX1, EX2, EX3])
        make_class("lm_api_other", "gv_tuan", ["lm_api_other_student"], [EX1])
        add_sub("lm_api_student", EX1, 1)
        add_sub("lm_api_student", EX1, 1)
        add_sub("lm_api_student", EX2, 3)

    def test_instructor_learner_model_endpoint_access_control(self):
        url = ENDPOINT.format("lm_api_class", "lm_api_student")
        ok = self.client.get(url, headers=self.owner)
        self.assertEqual(ok.status_code, 200)
        body = ok.json()
        self.assertEqual(body["class_id"], "lm_api_class")
        self.assertEqual(body["learner_model"]["model_version"], "3")
        self.assertEqual(concept({"learner_model": body["learner_model"]}, "loop")["state"], "struggling")
        self.assertIn("analytics_metrics", body)
        self.assertEqual(self.client.get(url, headers=self.other_instructor).status_code, 404)  # không sở hữu lớp
        self.assertEqual(self.client.get(url, headers=self.student).status_code, 403)  # sinh viên không được
        self.assertEqual(self.client.get(url).status_code in (401, 403), True)
        not_enrolled = ENDPOINT.format("lm_api_class", "lm_api_other_student")
        self.assertEqual(self.client.get(not_enrolled, headers=self.owner).status_code, 404)  # không ghi danh
        self.assertEqual(self.client.get(ENDPOINT.format("khong_ton_tai", "lm_api_student"), headers=self.owner).status_code, 404)

    def test_profile_includes_learner_model_in_both_branches(self):
        model = compute_student_model("lm_api_student", class_id="lm_api_class")
        with patch("backend.main.get_student_profile_via_mcp", new_callable=AsyncMock,
                   return_value={"student_model": model, "recent_attempts": []}):
            via_mcp = self.client.get("/api/student/profile", params={"session_id": "lm_api_student"}, headers=self.student).json()
        self.assertEqual(via_mcp["learner_model"]["model_version"], "3")
        with patch("backend.main.get_student_profile_via_mcp", new_callable=AsyncMock, side_effect=RuntimeError("mcp down")):
            fallback = self.client.get("/api/student/profile", params={"session_id": "lm_api_student"}, headers=self.student).json()
        self.assertEqual(fallback["learner_model"]["model_version"], "3")
        self.assertIn("analytics_metrics", fallback)

    def _pipeline(self):
        return {"exercise": {"id": EX3, "title": "T", "description": ""},
                "test_results": {"total_tests": 3, "passed_tests": 1, "failed_tests": 2, "all_passed": False, "summary": "", "results": []},
                "ast_analysis": {"valid": True, "structural_summary": "s"}, "attempt_history": [], "student_model": None,
                "discovered_tools": [], "mcp_trace": []}

    def _submit(self, **extra):
        with patch("backend.main.execute_submission_pipeline", new_callable=AsyncMock, return_value=self._pipeline()) as pipe, \
             patch("backend.main.save_learning_event_via_mcp", new_callable=AsyncMock) as save:
            resp = self.client.post("/api/submit", headers=self.student, json={
                "exercise_id": EX3, "code": "print(1)", "hint_level": 2, "action_type": "ask_ai", **extra})
        return resp, pipe, save

    def test_submit_passes_only_enrolled_class_and_never_403s(self):
        resp, pipe, save = self._submit(class_id="lm_api_class")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(pipe.call_args.kwargs["class_id"], "lm_api_class")
        features = save.call_args.kwargs["attempt_features"]
        self.assertEqual(features["error_class"], "logic_partial")
        resp, pipe, _ = self._submit(class_id="lm_api_other")  # không ghi danh: bỏ qua lớp
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(pipe.call_args.kwargs["class_id"])
        resp, pipe, _ = self._submit()
        self.assertIsNone(pipe.call_args.kwargs["class_id"])
        body = resp.json()
        self.assertEqual(body["hint_level"], 2)
        self.assertEqual(body["adaptive_strategy"]["requested_level"], 2)
        self.assertIn("policy_version", body["adaptive_strategy"])


class TestDynamicKnowledgeComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.instructor_token = create_token("gv_tran", "instructor", "Giảng viên Trần")
        cls.headers = {"Authorization": f"Bearer {cls.instructor_token}"}

    def test_assign_kcs_with_custom_definitions(self):
        custom_defs = list(lm.KC_DEFINITIONS) + [
            {"kc": "file_io", "label_vi": "Xử lý tệp tin", "keywords": [r"tep tin", r"file", r"open"]}
        ]
        # Thẻ kỹ năng có 'tệp tin'
        kcs = lm.assign_kcs(skill_tag="Đọc ghi tệp tin nâng cao", kc_definitions=custom_defs)
        self.assertIn("io_format", kcs)
        self.assertIn("file_io", kcs)
        self.assertNotIn("loop", kcs)

    def test_derive_learner_model_with_custom_kc(self):
        custom_defs = list(lm.KC_DEFINITIONS) + [
            {"kc": "file_io", "label_vi": "Xử lý tệp tin", "keywords": [r"tep tin", r"file"]}
        ]
        exercises = [{"id": "ex_file_1", "title": "Ghi tệp tin", "skill_tag": "Đọc ghi tệp tin"}]
        res = lm.derive_learner_model(
            exercises=exercises,
            submissions=[],
            asks=[],
            runs=[],
            features={},
            autonomy_by_exercise={},
            kc_definitions=custom_defs,
        )
        kc_keys = [c["kc"] for c in res["concepts"]]
        self.assertIn("file_io", kc_keys)
        file_concept = next(c for c in res["concepts"] if c["kc"] == "file_io")
        self.assertEqual(file_concept["state"], "no_evidence")
        self.assertEqual(file_concept["label_vi"], "Xử lý tệp tin")

    def test_api_knowledge_components_crud(self):
        # 1. GET public knowledge components
        resp = self.client.get("/api/knowledge-components")
        self.assertEqual(resp.status_code, 200)
        items = resp.json()
        self.assertGreaterEqual(len(items), 6)
        kcs = [i["kc"] for i in items]
        self.assertIn("io_format", kcs)
        self.assertIn("loop", kcs)

        # 2. POST create custom KC
        create_resp = self.client.post("/api/instructor/knowledge-components", headers=self.headers, json={
            "kc": "file_io_test",
            "label_vi": "Xử lý Tệp tin Thử nghiệm",
            "keywords": ["tep tin", "file", "open"]
        })
        self.assertEqual(create_resp.status_code, 200)
        created = create_resp.json()
        self.assertEqual(created["kc"], "file_io_test")
        self.assertEqual(created["label_vi"], "Xử lý Tệp tin Thử nghiệm")
        self.assertEqual(created["created_by"], "gv_tran")

        # 3. GET instructor list -> contains new KC
        list_resp = self.client.get("/api/instructor/knowledge-components", headers=self.headers)
        self.assertEqual(list_resp.status_code, 200)
        inst_kcs = [i["kc"] for i in list_resp.json()]
        self.assertIn("file_io_test", inst_kcs)

        # 4. DELETE built-in KC is blocked
        del_builtin = self.client.delete("/api/instructor/knowledge-components/loop", headers=self.headers)
        self.assertEqual(del_builtin.status_code, 400)

        # 5. DELETE custom KC succeeds
        del_custom = self.client.delete("/api/instructor/knowledge-components/file_io_test", headers=self.headers)
        self.assertEqual(del_custom.status_code, 200)


if __name__ == "__main__":
    unittest.main()
