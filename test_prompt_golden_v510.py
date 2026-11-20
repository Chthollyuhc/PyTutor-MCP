"""Test vàng cho prompt gợi ý (v5.10): dựng lại prompt từ đầu vào đã lưu và so khớp TỪNG KÝ TỰ.

`evaluation/prompt_golden_v510.json` được sinh từ mã trước khi đổi nội dung prompt. Test này có hai việc:
  1. Trước khi tách khối `build_scaffolding_prompt`: chứng minh việc tách không đổi một ký tự nào.
  2. Sau khi chủ đích đổi nội dung: sinh lại tệp vàng (ghi lý do trong plans/PLAN_V510_OVERNIGHT.md) để mọi thay đổi
     ngoài ý muốn về sau bị phát hiện ngay.
Chạy: py -m unittest test_prompt_golden_v510 -v   (không cần DB, không gọi LLM)
"""
import json
import unittest
from pathlib import Path

from backend.llm_service import build_scaffolding_prompt
from mcp_server.exercises_data import EXERCISES

GOLDEN = Path(__file__).resolve().parent / "evaluation" / "prompt_golden_v510.json"
EX = {e["id"]: e for e in EXERCISES}


class PromptGoldenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(GOLDEN.read_text(encoding="utf-8"))

    def test_fixture_covers_every_level_and_special_cases(self):
        names = {c["name"] for c in self.data["cases"]}
        for lvl in (1, 2, 3):
            self.assertTrue(any(n.endswith(f"_L{lvl}") for n in names))
        self.assertIn("VAR_model_L2", names)
        self.assertIn("VAR_trace_L2", names)
        self.assertTrue(any(n.startswith("D09") for n in names), "ca có lịch sử gợi ý")
        self.assertTrue(any(n.startswith("D10") for n in names), "ca đã đạt")
        self.assertTrue(any(n.startswith("D01") for n in names), "ca chưa viết code")
        self.assertGreaterEqual(len(names), 40)

    def test_prompts_rebuild_character_for_character(self):
        mismatches = []
        for c in self.data["cases"]:
            got = build_scaffolding_prompt(
                exercise=EX[c["exercise_id"]], code=c["code"], test_results=c["test_results"], ast_analysis=c["ast_analysis"],
                hint_level=c["hint_level"], attempt_history=c["attempt_history"], student_model=c["student_model"],
                adaptive_strategy=c["adaptive_strategy"], trace=c.get("trace"))
            if got != c["expected_prompt"]:
                mismatches.append(c["name"])
        self.assertEqual(mismatches, [], f"Prompt đổi so với tệp vàng ở các ca: {mismatches}")


if __name__ == "__main__":
    unittest.main()
