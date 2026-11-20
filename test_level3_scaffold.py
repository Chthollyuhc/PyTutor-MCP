"""Kiểm thử lớp che logic của khung mã Mức 3 (`enforce_level3_skeleton`).

Chạy:  py -m unittest test_level3_scaffold -v
Không dùng DB, không gọi LLM. Ca `test_real_gemini_h4_reply_is_masked` dùng đúng phản hồi Gemini đã ghi
trong `evaluation/real_llm_results.json` (ca H4, 12/11/2026), nơi mô hình điền sẵn logic lời giải.
"""
import ast
import json
import re
import unittest
from pathlib import Path

from backend.guardrails import check_student_output, enforce_level3_skeleton
from backend.llm_service import generate_rule_based_fallback

ROOT = Path(__file__).resolve().parent

LEAKY = """### Dàn ý
- Bước 2: xử lý biên.

```python
n = int(input())

# Bước 2: trường hợp biên
if n <= 1:
    print("NO")
else:
    la_so_nguyen_to = True
    for i in range(2, n):
        if n % i == 0:
            la_so_nguyen_to = False
            break
    ket_qua = "YES" if la_so_nguyen_to else "NO"
    print(ket_qua)
```
"""

CLEAN = """```python
# Bước 1: đọc dữ liệu
du_lieu = ...          # TODO: đọc và ép kiểu đầu vào
ket_qua = 0
...                    # TODO: vòng lặp cập nhật ket_qua
print(ket_qua)
```"""


def code_block(text: str) -> str:
    return re.search(r"```[^\n]*\n(.*?)```", text, flags=re.DOTALL).group(1)


class Level3SkeletonTests(unittest.TestCase):
    def test_logic_is_masked_and_scaffold_is_kept(self):
        out, masked = enforce_level3_skeleton(LEAKY)
        block = code_block(out)
        self.assertEqual(masked, 4)  # if n <= 1 / for range(2, n) / if n % i == 0 / ket_qua = ...
        for leaked in ("n <= 1", "range(2, n)", "n % i == 0", '"YES" if'):
            self.assertNotIn(leaked, block)
        for kept in ("n = int(input())", "# Bước 2: trường hợp biên", "else:", "la_so_nguyen_to = True",
                     "break", 'print("NO")', "print(ket_qua)"):
            self.assertIn(kept, block)
        self.assertIn("- Bước 2: xử lý biên.", out)  # dàn ý ngoài khối code giữ nguyên
        self.assertIn("🔒", out)

    def test_masked_skeleton_is_still_valid_python(self):
        out, _ = enforce_level3_skeleton(LEAKY)
        ast.parse(code_block(out))  # `...` là biểu thức hợp lệ nên khung vẫn chạy thử được

    def test_clean_skeleton_is_untouched(self):
        out, masked = enforce_level3_skeleton(CLEAN)
        self.assertEqual(masked, 0)
        self.assertEqual(out, CLEAN)

    def test_text_without_code_is_untouched(self):
        text = "Bước 1: đọc n. Bước 2: nếu n <= 1 thì kết luận ngay."
        self.assertEqual(enforce_level3_skeleton(text), (text, 0))

    def test_idempotent(self):
        once, _ = enforce_level3_skeleton(LEAKY)
        twice, masked_again = enforce_level3_skeleton(once)
        self.assertEqual(masked_again, 0)
        self.assertEqual(once, twice)

    def test_real_gemini_h4_reply_is_masked(self):
        path = ROOT / "evaluation" / "real_llm_results.json"
        if not path.exists():
            self.skipTest("Chưa có evaluation/real_llm_results.json")
        cases = json.loads(path.read_text(encoding="utf-8"))["results"]["gemini"]
        reply = next(c["reply"] for c in cases if c["id"] == "H4")
        self.assertIn("n % i == 0", reply)  # bằng chứng: mô hình thật đã điền sẵn logic
        out, masked = enforce_level3_skeleton(reply)
        self.assertGreaterEqual(masked, 1)
        self.assertNotIn("n % i == 0", code_block(out))


def mask_block(code: str) -> tuple[str, int]:
    out, masked = enforce_level3_skeleton("```python\n" + code + "\n```")
    return code_block(out), masked


class Level3PrintAndInputTests(unittest.TestCase):
    """Lỗ hổng tìm thấy bằng evaluate_level3_skeleton.py: logic nằm trong print(...) hoặc cùng dòng input()."""

    def test_plain_print_and_plain_input_are_scaffold(self):
        code = ('n = int(input())\ns = input().strip()\na, b = map(int, input().split())\n'
                'print("NO")\nprint(ket_qua)\nprint(a, b, sep=" ")\nprint()')
        block, masked = mask_block(code)
        self.assertEqual(masked, 0)
        self.assertEqual(block.strip(), code)

    def test_computed_print_is_masked(self):
        for line in ("print(n * (n + 1) // 2)", "print(s[::-1])", "print(math.factorial(n))",
                     'print(f"{tong}")', 'print("YES" if ok else "NO")', "print(len(ds))",
                     "print(sum(range(1, int(input()) + 1)))", 'print(*reversed(s), sep="")'):
            block, masked = mask_block(line)
            self.assertEqual(masked, 1, line)
            self.assertIn("print(...)", block)
            ast.parse(block)

    def test_input_with_processing_keeps_only_the_variable_name(self):
        block, masked = mask_block("s = input().lower()\ntong = sum(map(int, input().split()))")
        self.assertEqual(masked, 2)
        self.assertNotIn(".lower()", block)
        self.assertNotIn("sum(", block)
        self.assertIn("s = ...", block)
        self.assertIn("tong = ...", block)


EX = {"title": "Bài thử"}
FAIL = {"all_passed": False, "passed_tests": 0, "total_tests": 3,
        "results": [{"test_idx": 1, "status": "FAIL", "input": "7", "expected_output": "YES", "actual_output": ""}]}
AST_OK = {"valid": True, "has_loops": False}


def level3(code: str) -> str:
    return generate_rule_based_fallback(EX, code, FAIL, AST_OK, 3)


class Level3OfflineProgressTests(unittest.TestCase):
    """Gợi ý Mức 3 offline chọn bước kế tiếp theo phần người học đã viết (rút giàn giáo)."""

    def test_empty_code_starts_at_step_1(self):
        text = level3("")
        self.assertIn("viết Bước 1 trước", text)
        self.assertNotIn("Đã thấy trong bài làm", text)

    def test_only_input_points_to_step_4_then_3(self):
        text = level3("n = int(input())\n")
        self.assertIn("Đã thấy trong bài làm:** Bước 1", text)
        self.assertIn("bạn đã có Bước 1", text)

    def test_input_and_print_points_to_step_3(self):
        text = level3("n = int(input())\nprint(n)\n")
        self.assertIn("tập trung vào Bước 3", text)

    def test_all_parts_present_points_to_stepping(self):
        text = level3("n = int(input())\nif n > 1:\n    print('YES')\n")
        self.assertIn("Chạy từng bước", text)
        self.assertIn("chưa biết chúng đã đúng hay chưa", text)  # không khẳng định vượt bằng chứng

    def test_commented_out_code_does_not_count(self):
        text = level3("# n = int(input())\n# print(n)\n")
        self.assertIn("viết Bước 1 trước", text)

    def test_exactly_one_next_step_and_skeleton_kept(self):
        for code in ("", "n = int(input())\n", "n = int(input())\nprint(n)\n"):
            text = level3(code)
            self.assertEqual(text.count("Bước kế tiếp:"), 1)
            self.assertIn("# TODO", text)
            self.assertEqual(enforce_level3_skeleton(text)[1], 0)  # khung offline không chứa logic cần che


if __name__ == "__main__":
    unittest.main()
