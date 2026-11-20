"""Kiểm thử các hàm kiểm tra chất lượng gợi ý (hint_quality_checks.py) bằng phản hồi tự soạn: ca đạt và ca trượt.

Mục đích: bảo đảm bộ đo không "đạt giả" hoặc "trượt giả" trước khi dùng nó để so sánh trước/sau. Không cần DB, không gọi LLM.
Chạy: py -m unittest test_hint_quality_v510 -v
"""
import unittest

import hint_quality_checks as hq
from mcp_server.exercises_data import EXERCISES

EX = {e["id"]: e for e in EXERCISES}["ex_01_sum_1_to_n"]
CODE = "n = int(input())\ntong = 0\nfor i in range(1, n):\n    tong += i\nprint(tong)\n"
TR = {"results": [{"status": "FAIL", "input": "1\n", "expected_output": "1", "actual_output": "0", "error_message": ""}]}

L2_GOOD = ("📍 Chú ý dòng: `for i in range(1, n):`\n\n🔎 Với đầu vào `1` kỳ vọng `1` nhưng chương trình in `0`. "
           "Vòng lặp của bạn chạy qua những giá trị i nào khi n = 1? Hãy tự liệt kê rồi so với yêu cầu đề bài.")
L2_TWO_LINES = L2_GOOD + " Còn dòng `tong += i` thì sao?"
L2_FIX = L2_GOOD + " Hãy đổi thành giá trị lớn hơn một đơn vị."
L1_GOOD = ("Vòng lặp for với range dừng trước giá trị cuối cùng của nó, nên cần chú ý biên của phép đếm. "
           "Hãy tự chọn một đầu vào nhỏ, tính tay tổng rồi chạy thử để so sánh. Bạn nghĩ range dừng ở đâu?")


class CheckFunctionTests(unittest.TestCase):
    def test_strip_comment_keeps_hash_in_string(self):
        self.assertEqual(hq.strip_comment('x = "a#b"  # note'), 'x = "a#b"')

    def test_quoted_lines_counts_only_real_student_lines(self):
        self.assertEqual(hq.quoted_student_lines(L2_GOOD, CODE, EX["starter_code"]), ["for i in range(1, n):"])
        self.assertEqual(len(hq.quoted_student_lines(L2_TWO_LINES, CODE, EX["starter_code"])), 2)

    def test_l2_one_line_and_expected(self):
        self.assertTrue(hq.check_l2_quotes_one_line(L2_GOOD, CODE, EX["starter_code"]))
        self.assertFalse(hq.check_l2_quotes_one_line(L2_TWO_LINES, CODE, EX["starter_code"]))
        self.assertTrue(hq.check_l2_points_at_expected(L2_GOOD, CODE, EX["starter_code"], ["for i in range(1, n):"]))
        self.assertFalse(hq.check_l2_points_at_expected(L2_TWO_LINES, CODE, EX["starter_code"], ["for i in range(1, n):"]))

    def test_l2_evidence_needs_all_three_values_in_spans(self):
        self.assertTrue(hq.check_l2_evidence(L2_GOOD, TR, {}, "FAIL"))
        self.assertFalse(hq.check_l2_evidence("Vòng lặp của bạn có vấn đề, hãy xem lại.", TR, {}, "FAIL"))
        self.assertFalse(hq.check_l2_evidence("Với đầu vào `1` kết quả sai.", TR, {}, "FAIL"))

    def test_l2_evidence_timeout_syntax_runtime(self):
        tmo = {"results": [{"status": "TIMEOUT", "input": "1", "expected_output": "1", "actual_output": "", "error_message": "Time Limit Exceeded"}]}
        self.assertTrue(hq.check_l2_evidence("Chương trình chạy quá thời gian, không dừng.", tmo, {}, "TIMEOUT"))
        self.assertFalse(hq.check_l2_evidence("Có lỗi ở vòng lặp.", tmo, {}, "TIMEOUT"))
        ast_err = {"syntax_error": {"lineno": 3, "message": "expected ':'"}}
        self.assertTrue(hq.check_l2_evidence("Thông báo `expected ':'` tại dòng 3.", {}, ast_err, "SYNTAX_ERROR"))
        self.assertFalse(hq.check_l2_evidence("Có lỗi cú pháp.", {}, ast_err, "SYNTAX_ERROR"))
        rte = {"results": [{"status": "RUNTIME_ERROR", "input": "1", "expected_output": "1", "actual_output": "", "error_message": "TypeError: x"}]}
        self.assertTrue(hq.check_l2_evidence("Với đầu vào `1` chương trình báo TypeError.", rte, {}, "RUNTIME_ERROR"))
        self.assertFalse(hq.check_l2_evidence("Chương trình báo lỗi.", rte, {}, "RUNTIME_ERROR"))

    def test_fix_phrases(self):
        self.assertFalse(hq.check_no_fix_phrases(L2_FIX))
        self.assertTrue(hq.check_no_fix_phrases(L2_GOOD))
        self.assertFalse(hq.check_no_fix_phrases("Bạn nên dùng điều kiện n > 1 cho nhánh này."))
        self.assertFalse(hq.check_no_fix_phrases("Hãy thay `range(1, n)` bằng một biểu thức khác."))
        # không báo nhầm: "thay đổi ... trở thành" là mô tả hành vi, không phải chỉ cách sửa
        self.assertTrue(hq.check_no_fix_phrases("Biến nào thay đổi sau mỗi lượt và điều kiện dừng trở thành sai khi nào?"))
        self.assertFalse(hq.check_no_fix_phrases("Bạn cần đổi dòng này thành một phép nhân."))
        # thông báo của chính hệ thống khi che khung mã (🔒 …) không phải lời gợi ý của gia sư
        self.assertTrue(hq.check_no_fix_phrases("Dàn ý ...\n\n🔒 *PyTutor đã thay 3 biểu thức trong khung mã bằng `...` để phần lập luận vẫn là của bạn.*"))

    def test_l1_boundaries(self):
        self.assertTrue(hq.check_l1_no_test_specifics(L1_GOOD, TR))
        self.assertFalse(hq.check_l1_no_test_specifics("Với đầu vào `1` bạn thấy `0` thay vì `1`.", TR))
        self.assertFalse(hq.check_l1_no_test_specifics("Kỳ vọng: `1` nhưng nhận kết quả khác.", TR))
        self.assertTrue(hq.check_l1_no_code_quote(L1_GOOD, CODE, EX["starter_code"]))
        self.assertFalse(hq.check_l1_no_code_quote("Xem lại `for i in range(1, n):` nhé.", CODE, EX["starter_code"]))
        self.assertFalse(hq.check_no_code_block("Ví dụ:\n```python\nx = 1\n```"))

    def test_l1_informative_vs_bare_question(self):
        terms = ["range", "biên", "dừng"]
        self.assertTrue(hq.check_l1_informative(L1_GOOD, terms))
        self.assertFalse(hq.check_l1_informative("Bạn thử nghĩ xem vòng lặp chạy thế nào? Có điều gì lạ không?", terms))

    def test_grounded_names(self):
        self.assertTrue(hq.check_grounded_names("Xem biến `tong` và hàm `range()`.", CODE, EX))
        self.assertFalse(hq.check_grounded_names("Xem biến `ket_qua_cuoi` và hàm `tinh_tong()`.", CODE, EX))
        self.assertTrue(hq.check_grounded_names("Gợi ý `range(start, stop)` hoạt động ra sao.", CODE, EX))

    def test_ability_remarks(self):
        self.assertFalse(hq.check_no_ability_remark("Bạn rất giỏi nhưng hãy chú ý biên."))
        self.assertFalse(hq.check_no_ability_remark("Năng lực của bạn còn yếu."))
        self.assertTrue(hq.check_no_ability_remark("Bài làm đã đúng ở phần đọc dữ liệu, làm tốt lắm."))

    def test_leaked_core_ignores_text_already_in_student_code(self):
        pats = [r"range\(\s*1\s*,\s*n\s*\+\s*1\s*\)", r"range\(\s*1\s*,\s*n\s*\)"]
        self.assertEqual(hq.leaked_core("Dùng `range(1, n + 1)` nhé", CODE, pats), ["range(1, n + 1)"])
        self.assertEqual(hq.leaked_core("Dòng `range(1, n)` của bạn", CODE, pats), [])

    def test_length_and_frame(self):
        self.assertFalse(hq.check_length("quá ngắn", 1))
        self.assertTrue(hq.check_length(L1_GOOD + " " + L1_GOOD, 1))
        self.assertTrue(hq.check_frame("🎯 Đang ở đâu: bài đạt 0/5. 🔎 Bằng chứng: kiểm thử lỗi. ➡️ Bước kế tiếp: hãy thử chạy."))
        self.assertFalse(hq.check_frame("Chào bạn."))
        self.assertTrue(hq.check_single_next_step("a\n➡️ **Bước kế tiếp:** thử."))
        self.assertFalse(hq.check_single_next_step("➡️ **Bước kế tiếp:** a\n➡️ **Bước kế tiếp:** b"))

    def test_level3_steps_and_skeleton(self):
        good = ("- **Bước 1:** Đọc số nguyên n.\n- **Bước 2:** Khởi tạo biến tổng bằng 0.\n- **Bước 3:** Dùng vòng lặp cộng dồn.\n"
                "- **Bước 4:** In tổng.\n```python\nn = int(input())\ntong = 0\nfor i in range(1, ...):  # TODO\n    tong = ...\nprint(tong)\n```")
        self.assertTrue(hq.check_l3_steps(good, ["tổng", "vòng lặp", "cộng dồn"]))
        generic = ("- **Bước 1:** Nhập dữ liệu đầu vào và chuyển đổi kiểu thích hợp.\n- **Bước 2:** Khởi tạo biến lưu trữ với giá trị ban đầu chính xác.\n"
                   "- **Bước 3:** Tổ chức vòng lặp duyệt qua các phần tử và cập nhật kết quả.\n- **Bước 4:** In kết quả ra màn hình bằng hàm print.")
        self.assertFalse(hq.check_l3_steps(generic, ["tổng", "vòng lặp", "cộng dồn"]))
        self.assertTrue(hq.check_l3_has_skeleton(good))
        self.assertTrue(hq.check_l3_skeleton_not_passing(good, EX["test_cases"]))
        spoil = "```python\nn = int(input())\ntong = 0\nfor i in range(1, n + 1):\n    tong += i\nprint(tong)\n```"
        self.assertFalse(hq.check_l3_skeleton_not_passing(spoil, EX["test_cases"]))

    def test_jaccard_and_progress(self):
        self.assertAlmostEqual(hq.jaccard("a b c d e f", "a b c d e f"), 1.0)
        self.assertEqual(hq.jaccard("một hai ba bốn năm", "sáu bảy tám chín mười"), 0.0)
        self.assertTrue(hq.check_progress_l1_to_l2(L1_GOOD, L2_GOOD, TR, {}, "FAIL"))
        self.assertFalse(hq.check_progress_l1_to_l2(L2_GOOD, L2_GOOD, TR, {}, "FAIL"))
        self.assertTrue(hq.check_progress_l2_to_l3(L2_GOOD, "x\n```python\n...  # TODO\n```"))
        self.assertFalse(hq.check_progress_l2_to_l3("```python\nx=1\n```", "x\n```python\n...  # TODO\n```"))


if __name__ == "__main__":
    unittest.main()
