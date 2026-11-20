"""Xin gợi ý khi chưa viết dòng code nào (ask_ai): chiến lược, fallback offline Mức 1-3. Hàm thuần, không cần DB."""
import unittest

from backend.adaptive_policy import is_blank_attempt, select_hint_strategy
from backend.llm_service import generate_rule_based_fallback

EX = {"title": "Bài 01: Tổng hai số", "description": "Đọc hai số, in tổng."}
TESTS = {"all_passed": False, "passed_tests": 0, "total_tests": 2, "results": [
    {"test_idx": 1, "status": "FAIL", "input": "1\n2", "expected_output": "3", "actual_output": "", "description": "cơ bản"}]}


class NoCodeTests(unittest.TestCase):
    def test_blank_detection(self):
        self.assertTrue(is_blank_attempt(""))
        self.assertTrue(is_blank_attempt("# viết ở đây\npass"))
        self.assertTrue(is_blank_attempt("a = int(input())\n", "a = int(input())"))
        self.assertFalse(is_blank_attempt("print(1)", "a = int(input())"))

    def test_strategy_ignores_failed_tests_and_keeps_level(self):
        hist = [{"hint_level": 1, "action_type": "ask_ai"}] * 3
        s = select_hint_strategy(3, TESTS, hist, None, no_code=True)
        self.assertEqual(s["strategy"], "conceptual_start")
        self.assertIn("no_code_yet", s["adaptation_codes"])
        self.assertEqual(s["requested_level"], 3)

    def test_default_unchanged(self):
        s = select_hint_strategy(1, TESTS, [], None)
        self.assertEqual(s["strategy"], "failed_case_diagnosis")
        self.assertNotIn("no_code_yet", s["adaptation_codes"])

    def test_passed_wins_over_no_code(self):
        s = select_hint_strategy(1, {"all_passed": True, "results": []}, [], None, no_code=True)
        self.assertEqual(s["strategy"], "solution_review")

    def test_offline_replies(self):
        strat = select_hint_strategy(1, TESTS, [], None, no_code=True)
        for lvl in (1, 2, 3):
            strat["requested_level"] = lvl
            txt = generate_rule_based_fallback(EX, "", TESTS, {"valid": False, "syntax_error": {"message": "Mã nguồn trống."}}, lvl, adaptive_strategy=strat)
            self.assertIn("chưa viết dòng code nào", txt, lvl)
            self.assertNotIn("0/2", txt, lvl)
            self.assertNotIn("SyntaxError", txt, lvl)
        self.assertIn("```python", txt)  # Mức 3 có khung code
        self.assertIn("TODO", txt)


if __name__ == "__main__":
    unittest.main()
