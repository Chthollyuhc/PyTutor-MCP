"""Gợi ý bám đề bài và bộ kiểm thử của giảng viên (v5.11). Hàm thuần, không cần DB, không gọi LLM.
Chạy: py -m unittest test_exercise_brief_v511 -v
"""
import os
import unittest

os.environ.setdefault("PYTUTOR_DISABLE_LLM", "1")

from backend import exercise_brief as eb  # noqa: E402
from backend import llm_service  # noqa: E402
from backend.hint_rules import build_offline_hint  # noqa: E402
from mcp_server.exercises_data import EXERCISES  # noqa: E402

EX = {e["id"]: e for e in EXERCISES}
PRIME, SUM = EX["ex_02_prime_check"], EX["ex_01_sum_1_to_n"]
BLANK_TR = {"all_passed": False, "passed_tests": 0, "total_tests": 6, "results": [
    {"test_idx": 1, "status": "FAIL", "input": "7", "expected_output": "YES", "actual_output": "", "description": "Số nguyên tố thông thường (7)"}]}
BLANK_STRATEGY = {"strategy": "conceptual_start", "adaptations": [{"code": "no_code_yet", "reason_vi": "x", "context": {}}]}
WRONG_TR = {"all_passed": False, "passed_tests": 4, "total_tests": 6, "results": [
    {"test_idx": 3, "status": "FAIL", "input": "1", "expected_output": "NO", "actual_output": "YES", "description": "Trường hợp biên (1 không là số nguyên tố)"}]}
AST = {"valid": True, "has_loops": True, "structural_summary": "x"}
CODE = 'n = int(input())\nprint("YES")\n'


class ParseTests(unittest.TestCase):
    def test_parses_objectives_inputs_outputs_and_examples_of_every_seed_exercise(self):
        for ex in EXERCISES:
            info = eb.parse_description(ex["description"])
            self.assertTrue(info["objectives"], ex["id"])
            self.assertTrue(info["inputs"] and info["outputs"], ex["id"])
            self.assertTrue(info["examples"], ex["id"])
            self.assertNotIn("\\", " ".join(info["inputs"] + info["outputs"] + info["objectives"]), ex["id"])
        ex1 = eb.parse_description(SUM["description"])["examples"][0]
        self.assertEqual((ex1["input"], ex1["output"], ex1["explain"]), ("3", "6", "1 + 2 + 3 = 6"))
        self.assertIn("≤", eb.parse_description(SUM["description"])["inputs"][0])

    def test_test_overview_uses_instructors_test_descriptions(self):
        t = eb.test_overview(PRIME)
        self.assertEqual(t["count"], 6)
        for cat in ("trường hợp biên", "số âm"):
            self.assertIn(cat, t["categories"])
        self.assertNotIn("số âm", eb.test_overview(EX["ex_05_count_vowels"])["categories"])  # "nguyên âm" không phải số âm
        self.assertEqual(eb.test_overview({"test_cases": [{"description": "Test case #3"}]})["descriptions"], [])

    def test_safe_objective_drops_solution_technique_details(self):
        """Giảng viên có thể ghi cả kỹ thuật giải trong mục tiêu; gợi ý không được nhắc lại biểu thức đó."""
        self.assertEqual(eb.safe_objective("Thao tác với chuỗi (duyệt ngược hoặc dùng slice [::-1])"), "Thao tác với chuỗi.")
        self.assertEqual(eb.safe_objective("Biến tích lũy cộng dồn (+=)"), "Biến tích lũy cộng dồn.")
        self.assertEqual(eb.safe_objective("Dùng phương thức .lower() để chuẩn hóa"), "Dùng phương thức để chuẩn hóa.")
        self.assertEqual(eb.safe_objective("Biết dùng int(input()) để nhận dữ liệu"), "Biết dùng int(input()) để nhận dữ liệu.")
        self.assertEqual(eb.safe_objective(""), "")
        for ex in EXERCISES:
            for o in eb.parse_description(ex["description"])["objectives"]:
                self.assertNotRegex(eb.safe_objective(o), r"\[|\]|\+=|::|\.lower")

    def test_odd_exercises_do_not_raise(self):
        for odd in (None, {}, {"description": None}, {"description": "chỉ một câu"}, {"description": "### Ví dụ\n| a |\n", "test_cases": [{}]}):
            for level in (1, 2, 3):
                eb.brief_text(odd, level, no_code=True)
        self.assertEqual(eb.brief_text({}, 1), "")

    def test_each_level_gets_only_what_it_may_use(self):
        l1, l2 = eb.brief_text(PRIME, 1), eb.brief_text(PRIME, 2)
        blank = eb.brief_text(PRIME, 2, no_code=True)
        self.assertIn("nhóm", l1)
        self.assertNotIn("#3:", l1)                  # Mức 1: không có mô tả/giá trị từng kiểm thử
        self.assertIn("#3: Trường hợp biên", l2)     # Mức 2–3: mô tả từng kiểm thử
        self.assertNotIn("Ví dụ trong đề", l2)
        self.assertIn("Ví dụ trong đề: đầu vào `7` → đầu ra `YES`", blank)  # chỉ khi chưa viết code
        self.assertIn("Mục tiêu học tập", l1)


class PromptTests(unittest.TestCase):
    def prompt(self, level, code=CODE, tr=WRONG_TR, strategy=None):
        return llm_service.build_scaffolding_prompt(PRIME, code, tr, AST, level, adaptive_strategy=strategy)

    def test_prompt_carries_the_instructors_brief_at_every_level(self):
        for level in (1, 2, 3):
            p = self.prompt(level)
            self.assertIn("ĐỀ BÀI & KIỂM THỬ CỦA GIẢNG VIÊN", p)
            self.assertIn("Xử lý các trường hợp biên", p)
        self.assertNotIn("#3: Trường hợp biên", self.prompt(1))
        self.assertIn("#3: Trường hợp biên", self.prompt(2))

    def test_blank_attempt_prompt_tells_the_model_how_to_start_from_the_statement(self):
        p1 = self.prompt(1, code="", tr=BLANK_TR, strategy=BLANK_STRATEGY)
        self.assertIn("chưa biết bắt đầu", p1)
        self.assertNotIn("Ví dụ trong đề: đầu vào", p1)   # Mức 1 không nêu giá trị, kể cả ví dụ của đề
        p2 = self.prompt(2, code="", tr=BLANK_TR, strategy=BLANK_STRATEGY)
        self.assertIn("Ví dụ trong đề: đầu vào `7` → đầu ra `YES`", p2)


class OfflineTests(unittest.TestCase):
    def hint(self, level, code="", tr=BLANK_TR, strategy=BLANK_STRATEGY):
        from backend.llm_service import generate_rule_based_fallback
        return generate_rule_based_fallback(PRIME, code, tr, {"valid": False, "syntax_error": "Mã nguồn trống."}, level, adaptive_strategy=strategy)

    def test_blank_level1_uses_objectives_and_statement(self):
        text = self.hint(1)
        self.assertIn("Xử lý các trường hợp biên", text)         # mục tiêu học tập của giảng viên
        self.assertIn("chuỗi YES hoặc NO", text)                  # đầu ra theo đề
        self.assertIn("chưa viết dòng code nào", text)
        self.assertNotIn("`YES`", text)                           # Mức 1: không lộ giá trị ví dụ/kiểm thử
        self.assertNotIn("`7`", text)

    def test_blank_level2_walks_through_the_statements_example_and_test_kinds(self):
        text = self.hint(2)
        self.assertIn("`7`", text)
        self.assertIn("`YES`", text)
        self.assertIn("trường hợp biên", text)
        self.assertNotIn("0/6", text)

    def test_level3_outline_mentions_the_cases_the_tests_cover(self):
        text = build_offline_hint(PRIME, CODE, WRONG_TR, AST, 3)
        self.assertIn("Trường hợp biên", text)  # mô tả kiểm thử của giảng viên được nêu ở bước xử lý
        self.assertEqual(text.count("```"), 2)

    def test_nonblank_level1_mentions_the_teachers_goal_without_test_values(self):
        text = build_offline_hint(PRIME, CODE, WRONG_TR, AST, 1)
        self.assertIn("Mục tiêu của bài", text)
        self.assertNotIn("`NO`", text)


if __name__ == "__main__":
    unittest.main()


class NoCodePromptLayoutTests(unittest.TestCase):
    """Ca thật với Gemini (v5.11): code rỗng ở Mức 2 bị "chẩn đoán" một dòng vì bố cục Mức 2 bắt buộc trích dòng."""

    def prompt(self, level):
        return llm_service.build_scaffolding_prompt(PRIME, "", BLANK_TR, {"valid": False, "syntax_error": "Mã nguồn trống."}, level,
                                                    adaptive_strategy=BLANK_STRATEGY)

    def test_blank_attempt_uses_reading_layout_not_diagnosis(self):
        for level in (1, 2):
            p = self.prompt(level)
            self.assertIn("SINH VIÊN CHƯA VIẾT CODE", p)
            self.assertNotIn("Dòng cần xem (dòng N)", p)
            self.assertNotIn("Input='7'", p)                       # không đưa test lỗi "giả" của mã trống cho mô hình
            self.assertIn("không mang thông tin", p)
        self.assertIn("ví dụ trong đề", self.prompt(2).lower())
        self.assertIn("KHÔNG có mục \"Dòng cần xem\"", self.prompt(2))

    def test_blank_level3_keeps_the_skeleton_layout_and_normal_attempts_are_unchanged(self):
        self.assertIn("KHUNG MÃ", self.prompt(3))
        normal = llm_service.build_scaffolding_prompt(PRIME, CODE, WRONG_TR, AST, 2)
        self.assertIn("Dòng cần xem (dòng N)", normal)
        self.assertNotIn("SINH VIÊN CHƯA VIẾT CODE", normal)
