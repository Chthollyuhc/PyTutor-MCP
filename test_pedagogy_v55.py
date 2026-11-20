"""Kiểm thử các chỉnh sửa sư phạm v5.5 rút ra từ việc đọc 22 phản hồi của mô hình thật.

Chạy:  py -m unittest test_pedagogy_v55 -v      (không dùng DB, không gọi LLM)

Các ca C1/R1 (gia sư chỉ hỏi ngược khi người học hỏi khái niệm chung), R3 (không nói rõ khi không có tài liệu
lớp) và I1 (gọi "cặp sinh viên–bài" là "sinh viên") nằm trong `evaluation/real_llm_results.json`.
Kiểm thử ở đây chỉ khóa NỘI DUNG PROMPT và phần hậu xử lý tất định; việc mô hình thật có làm theo prompt mới
hay không CHƯA được đo.
"""
import json
import unittest
from pathlib import Path

from backend.llm_service import PROCESS_UNIT_NOTE, add_process_unit_note, reply_says_no_source
from backend.prompt_templates import render_instructor_prompt, render_socratic_prompt

ROOT = Path(__file__).resolve().parent


def chat_prompt(scope: str) -> str:
    return render_socratic_prompt(exercise={"title": "Bài thử"}, code="MA_BAI_LAM = 1", user_message="range là gì?",
                                  history="", chat_scope=scope)


class ConceptExplanationPromptTests(unittest.TestCase):
    def test_concept_scope_asks_for_direct_explanation_then_one_check_question(self):
        prompt = chat_prompt("concept_only")
        self.assertIn("CÁCH TRẢ LỜI CÂU HỎI KHÁI NIỆM", prompt)
        self.assertIn("giải thích trực tiếp", prompt)
        self.assertIn("đúng MỘT câu hỏi", prompt)
        self.assertNotIn("Chỉ gợi mở khái niệm bằng câu hỏi", prompt)  # không còn ép "chỉ hỏi ngược"

    def test_concept_scope_still_protects_the_current_exercise(self):
        prompt = chat_prompt("concept_only")
        self.assertNotIn("MA_BAI_LAM", prompt)  # khóa phạm vi S1.4 không đổi: không có code bài làm
        self.assertIn("Không chẩn đoán dòng lỗi", prompt)
        self.assertIn("KHÔNG dùng khối code nhiều dòng", prompt)  # khớp bộ lọc: khối code >= 3 dòng bị chặn
        self.assertIn("inline", prompt)
        self.assertIn("TỐI ĐA HAI đoạn code inline", prompt)  # R1: nhiều đoạn inline kiểu `x = 10` bị bộ lọc đếm như lời giải

    def test_other_scopes_keep_previous_instructions(self):
        for scope in ("code_review", "legacy"):
            prompt = chat_prompt(scope)
            self.assertNotIn("CÁCH TRẢ LỜI CÂU HỎI KHÁI NIỆM", prompt)
            self.assertIn("Chỉ gợi mở khái niệm bằng câu hỏi", prompt)

    def test_prompt_requires_saying_when_no_document_matches(self):
        self.assertIn("không tìm thấy tài liệu nội bộ về ý này", chat_prompt("concept_only"))


class ProcessGroupUnitTests(unittest.TestCase):
    SUMMARY = {"process_groups": {"pairs": 12}}

    def test_instructor_prompt_states_the_counting_unit(self):
        prompt = render_instructor_prompt(summary={}, user_message="Lớp thế nào?")
        self.assertIn("CẶP sinh viên–bài", prompt)

    def test_note_added_when_groups_are_called_students(self):
        reply = "Lớp có 4 sinh viên đạt độc lập, 7 sinh viên đang tiến triển và 1 sinh viên chỉ chạy thử."
        out = add_process_unit_note(reply, self.SUMMARY)
        self.assertTrue(out.startswith(reply))  # không sửa câu chữ của mô hình
        self.assertIn("cặp sinh viên–bài", out)
        self.assertEqual(add_process_unit_note(out, self.SUMMARY), out)  # không gắn hai lần

    def test_no_note_when_unit_is_right_or_groups_absent(self):
        correct = "Có 4 cặp sinh viên–bài đạt độc lập; 5 sinh viên có hoạt động trên 7 sinh viên ghi danh."
        self.assertEqual(add_process_unit_note(correct, self.SUMMARY), correct)
        wrong_but_no_groups = "Lớp có 4 sinh viên đạt độc lập."
        self.assertEqual(add_process_unit_note(wrong_but_no_groups, {"process_groups": {}}), wrong_but_no_groups)

    def test_recorded_gemini_reply_i1_gets_the_note(self):
        path = ROOT / "evaluation" / "real_llm_results.json"
        if not path.exists():
            self.skipTest("Chưa có evaluation/real_llm_results.json")
        cases = json.loads(path.read_text(encoding="utf-8"))["results"]["gemini"]
        reply = next(c["reply"] for c in cases if c["id"] == "I1")
        self.assertIn("4 sinh viên đạt độc lập", reply)  # bằng chứng: mô hình thật gọi nhầm đơn vị
        self.assertTrue(add_process_unit_note(reply, self.SUMMARY).endswith(PROCESS_UNIT_NOTE.strip()))


class NoSourceConsistencyTests(unittest.TestCase):
    """R1: câu trả lời nói không có tài liệu thì giao diện không được hiện nguồn."""

    def test_detects_the_phrase_the_prompt_asks_for(self):
        self.assertTrue(reply_says_no_source("Chào bạn! Về khái niệm này, không tìm thấy tài liệu nội bộ về ý này."))
        self.assertTrue(reply_says_no_source("Không tìm thấy tài liệu nào đề cập đến vấn đề này."))

    def test_does_not_trigger_on_grounded_answers(self):
        self.assertFalse(reply_says_no_source("Theo tài liệu của lớp, khối try nên chứa int(input())."))
        self.assertFalse(reply_says_no_source(""))

    def test_recorded_gemini_replies(self):
        path = ROOT / "evaluation" / "real_llm_results_v55b.json"
        if not path.exists():
            self.skipTest("Chưa có evaluation/real_llm_results_v55b.json")
        cases = {c["id"]: c for c in json.loads(path.read_text(encoding="utf-8"))["results"]["gemini"]}
        self.assertTrue(reply_says_no_source(cases["R1"]["reply"]))   # nói không có tài liệu
        self.assertFalse(reply_says_no_source(cases["R2"]["reply"]))  # dùng tài liệu lớp, vẫn hiện nguồn


class Level1BoundaryTests(unittest.TestCase):
    """Ca H2: Mức 1 nêu đầu vào/đầu ra cụ thể của kiểm thử, vốn là bằng chứng của Mức 2."""

    def _prompt(self, level: int) -> str:
        from backend.llm_service import build_scaffolding_prompt
        failed = {"all_passed": False, "passed_tests": 0, "total_tests": 1,
                  "results": [{"test_idx": 1, "status": "FAIL", "input": "3", "expected_output": "6", "actual_output": "3"}]}
        return build_scaffolding_prompt(exercise={"title": "Bài thử", "description": "d"}, code="x = 1",
                                        test_results=failed, ast_analysis={"valid": True}, hint_level=level)

    def test_level1_forbids_quoting_test_io_and_names_the_boundary(self):
        prompt = self._prompt(1)
        self.assertIn("Ranh giới với Mức 2", prompt)
        self.assertIn("KHÔNG nêu đầu vào, đầu ra thực tế hay đầu ra kỳ vọng", prompt)

    def test_level2_quotes_only_one_student_line(self):
        prompt = self._prompt(2)
        self.assertIn("MỘT dòng code của sinh viên", prompt)  # H3: trích nhiều dòng inline bị bộ lọc chặn 5/5 lần
        self.assertIn("không chép lại", prompt)

    def test_level2_diagnoses_but_does_not_state_the_fix(self):
        prompt = self._prompt(2)
        self.assertIn("KHÔNG nêu cách sửa", prompt)
        self.assertIn("đúng MỘT câu hỏi để sinh viên tự đưa ra cách sửa", prompt)
        self.assertNotIn("Nêu rõ cần sửa điều kiện/biểu thức đó như thế nào", prompt)  # cách cũ chỉ thẳng cách sửa

    def test_level2_still_requires_test_evidence(self):
        prompt = self._prompt(2)
        self.assertNotIn("Ranh giới với Mức 2", prompt)
        self.assertIn("Expected Output", prompt)


class QuotedContextGuardTests(unittest.TestCase):
    """H3: chẩn đoán Mức 2 trích dòng của người học + nhãn kiểm thử bị chặn nhầm 4–5/5 lần."""

    STUDENT = ("n = int(input())\n"
               "if n > 1:\n"
               "    for i in range(2, n):\n"
               "        if n % i != 0:\n"
               "            print('YES')\n")
    DIAGNOSIS = ("1. Dòng cần xem: `if n % i != 0:` nằm trong vòng lặp. Với `Input = '2'`, `for i in range(2, 2)` "
                 "không chạy; khối `if n > 1:` cũng chưa xử lý biên, nên `Actual Output = ''`.")

    def test_without_context_the_diagnosis_is_blocked(self):
        from backend.guardrails import check_student_output
        safe, reason = check_student_output(self.DIAGNOSIS)
        self.assertFalse(safe)
        self.assertEqual(reason, "solution_inline_code")

    def test_with_student_code_as_context_it_passes(self):
        from backend.guardrails import check_student_output
        self.assertTrue(check_student_output(self.DIAGNOSIS, quoted_context=self.STUDENT)[0])

    def test_new_solution_lines_are_still_blocked(self):
        from backend.guardrails import check_student_output
        leak = "Hãy viết `if n < 2:` rồi `for i in range(2, int(n ** 0.5) + 1):` và `if n % i == 0:` cùng `ok = False`."
        safe, reason = check_student_output(leak, quoted_context=self.STUDENT)
        self.assertFalse(safe)  # các dòng không nằm trong code của người học vẫn bị đếm

    def test_default_behaviour_is_unchanged_without_context(self):
        from backend.guardrails import check_student_output
        self.assertEqual(check_student_output("Dùng `a = 1`, `b = 2`, `c = 3`."), (False, "solution_inline_code"))


if __name__ == "__main__":
    unittest.main()
