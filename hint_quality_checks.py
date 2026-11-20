"""Kiểm tra TẤT ĐỊNH chất lượng gợi ý 3 mức (v5.10). Hàm thuần, không gọi mô hình, không dùng DB.

Dùng bởi `evaluate_hint_levels.py` và `test_hint_quality_v510.py`. Mỗi kiểm tra trả True / False / None
(None = không áp dụng cho kịch bản hoặc mức này). Đây là kiểm tra so khớp quy tắc, KHÔNG phải điểm sư phạm:
một câu trả lời qua hết kiểm tra vẫn có thể nhạt hoặc khó làm theo. Điểm 0-5 theo rubric là việc của người chấm.

Ngưỡng (khóa trong plans/PLAN_V510_OVERNIGHT.md mục "Tiêu chí đã chốt"):
  độ dài (số từ): Mức 1 [45, 190], Mức 2 [60, 230], Mức 3 [110, 430] · độ trùng Jaccard 3-gram từ giữa hai gợi ý liên tiếp < 0.30.
"""
from __future__ import annotations

import ast
import builtins
import keyword
import re
from typing import Optional

LENGTH_RANGE = {1: (45, 190), 2: (60, 230), 3: (110, 430)}
OVERLAP_MAX = 0.30
MIN_LINE_CHARS = 5
_TRIVIAL_LINES = {"break", "continue", "pass", "else:", "try:", "finally:", "return"}

_FENCE = re.compile(r"(?:```|~~~)([^\n]*)\n(.*?)(?:```|~~~)", flags=re.DOTALL)
_SPAN = re.compile(r"`([^`\n]+)`")
_FIX_PHRASES = re.compile(
    r"((?<!thay )đổi\s+(?:[^.\n]{0,40}\s)?(?<!trở )thành|sửa\s+(?:[^.\n]{0,40}\s)?(?<!trở )thành|thay\s+(?:[^.\n]{0,40}\s)?(?:bằng|thế bằng)|thay thế\s+(?:[^.\n]{0,40}\s)?bằng|"
    r"nên\s+(?:dùng|viết|đổi|sửa|thêm)\s+(?:điều kiện|dòng|lệnh|biểu thức|`)|hãy\s+(?:viết|sửa|đổi|thêm)\s+(?:dòng|lệnh|`)|cần\s+(?:đổi|sửa|thay)\s|phải\s+là\s+`|đáp án (?:là|đúng là))",
    flags=re.IGNORECASE)
_ABILITY = re.compile(
    r"(\b(?:bạn|em|sinh viên|học viên)\s+(?:đang\s+|còn\s+)?(?:rất\s+|khá\s+|hơi\s+)?(?:giỏi|thông minh|yếu|kém|chậm|lười|ngốc|chưa\s+giỏi|có\s+năng\s+lực|không\s+giỏi)\b|"
    r"(?:năng lực|trình độ)\s+(?:của\s+)?(?:bạn|em)|bạn\s+chưa\s+đủ\s+(?:giỏi|khả năng)|người học\s+yếu)", flags=re.IGNORECASE)
_EVIDENCE_LABEL = re.compile(r"^\s*(input|expected\s+output|actual\s+output|output|đầu vào|kỳ vọng|thực tế)\s*[=:]", flags=re.IGNORECASE)
_LABELED_VALUE = re.compile(r"(input|đầu vào|kỳ vọng|expected|thực tế|actual|nhận được)[^\n`]{0,25}[:=]\s*`", flags=re.IGNORECASE)
_GENERIC_L3 = (
    "nhập dữ liệu đầu vào và chuyển đổi kiểu thích hợp", "khởi tạo biến lưu trữ với giá trị ban đầu chính xác",
    "tổ chức vòng lặp duyệt qua các phần tử và cập nhật kết quả", "in kết quả ra màn hình bằng hàm",
    "đọc dữ liệu đầu vào đúng định dạng đề nêu", "khởi tạo biến lưu kết quả bằng giá trị ban đầu hợp lý",
    "xử lý dữ liệu (rẽ nhánh hoặc lặp) và cập nhật biến kết quả", "in kết quả đúng định dạng đề yêu cầu",
)
_TIMEOUT_WORDS = re.compile(r"(quá\s+(?:thời gian|5\s*giây|năm giây)|không dừng|chạy mãi|vô hạn|time limit|timeout|không kết thúc|không bao giờ dừng|chạy hoài)", flags=re.IGNORECASE)
_EMPTY_ACTUAL = re.compile(r"(không in|không có (?:gì|đầu ra|kết quả)|rỗng|trống|chưa in)", flags=re.IGNORECASE)
_GENERIC_NAMES = {"start", "stop", "step", "sep", "end", "file", "iterable", "key", "reverse", "default", "value", "values",
                  "item", "items", "index", "element", "string", "sub", "old", "new", "count", "obj", "args", "kwargs",
                  "ten", "gia_tri", "ket_qua", "dieu_kien"}
_PY_NAMES = (set(dir(builtins)) | set(keyword.kwlist) | set(dir(str)) | set(dir(list)) | set(dir(dict))
             | set(dir(set)) | set(dir(int)) | set(dir(float)) | set(dir(tuple)))


def norm(text: str) -> str:
    return " ".join((text or "").split())


def words(text: str) -> list[str]:
    return re.findall(r"\w+", text or "", flags=re.UNICODE)


def strip_comment(line: str) -> str:
    """Bỏ chú thích cuối dòng, tôn trọng dấu nháy."""
    quote = ""
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
        elif ch == "#":
            return line[:i].rstrip()
    return line


def code_lines(code: str) -> list[str]:
    out = []
    for raw in (code or "").splitlines():
        line = norm(strip_comment(raw))
        if line:
            out.append(line)
    return out


def split_blocks(reply: str) -> tuple[str, list[str]]:
    """(văn bản ngoài khối code, danh sách thân các khối code)."""
    blocks = [m.group(2) for m in _FENCE.finditer(reply or "")]
    return _FENCE.sub(" ", reply or ""), blocks


def quoted_student_lines(reply: str, code: str, starter: str = "") -> list[str]:
    """Các dòng code của người học (đã chuẩn hóa) xuất hiện nguyên văn trong phản hồi; bỏ dòng chỉ là khung mẫu."""
    text = norm(reply)
    starter_lines = set(code_lines(starter))
    found = []
    for line in dict.fromkeys(code_lines(code)):
        if len(line) < MIN_LINE_CHARS or line in _TRIVIAL_LINES or line in starter_lines:
            continue
        if line in text:
            found.append(line)
    return [ln for ln in found if not any(ln != other and ln in other for other in found)]


def _values_in_spans(reply: str, value: str) -> bool:
    val = (value or "").strip()
    if not val:
        return False
    head = val.splitlines()[0].strip()
    def present(needle: str, span: str) -> bool:
        return bool(re.search(rf"(?<![\w.]){re.escape(needle)}(?![\w.])", span))
    for span in _SPAN.findall(reply):
        if present(val, span) or (head and present(head, span)):
            return True
    return False


def first_failures(test_results: dict) -> list[dict]:
    return [r for r in (test_results or {}).get("results", []) if r.get("status") not in ("PASS", "SKIPPED")]


# ----------------------------------------------------------------------------------------------
# Kiểm tra dùng chung
# ----------------------------------------------------------------------------------------------
def check_no_full_program(reply: str, code: str, level: int) -> Optional[bool]:
    from backend.guardrails import check_student_output
    if level == 3:
        return None  # Mức 3 có khối code dài hợp lệ; dùng check_skeleton_not_passing
    safe, _ = check_student_output(reply, quoted_context=code or "")
    return safe


def check_length(reply: str, level: int, passed: bool = False) -> bool:
    """Độ dài theo mức. Bài đã đạt hết kiểm thử dùng khoảng riêng (phản hồi rút giàn giáo ngắn hơn theo thiết kế)."""
    lo, hi = (30, 230) if passed else LENGTH_RANGE[level]
    return lo <= len(words(reply)) <= hi


def check_no_ability_remark(reply: str) -> bool:
    return not _ABILITY.search(reply or "")


def check_frame(reply: str) -> bool:
    """Heuristic từ khóa: có ý 'đang ở đâu', 'bằng chứng', 'bước kế tiếp'. Không đo chất lượng từng ý."""
    t = (reply or "").lower()
    goal = bool(re.search(r"(đang ở đâu|mục tiêu|đề bài yêu cầu|bài yêu cầu|đang đạt|vượt qua|\d+\s*/\s*\d+\s*kiểm thử|đạt \d+\s*/\s*\d+|bài làm hiện|bài của bạn)", t))
    evidence = bool(re.search(r"(bằng chứng|kiểm thử|test|kết quả|quan sát|thông báo|dòng \d+|lỗi)", t))
    nxt = bool(re.search(r"(bước kế tiếp|bước tiếp theo|việc tiếp theo|hãy thử|thử\s|tự kiểm|chạy thử|chạy từng bước|\?)", t))
    return goal and evidence and nxt


def check_single_next_step(reply: str) -> bool:
    """Đúng MỘT dòng nhãn 'Bước kế tiếp' (hoặc ➡️). Là yêu cầu định dạng, không phải chất lượng nội dung."""
    t = reply or ""
    n = len(re.findall(r"(?im)^\W*(?:➡️\s*)?\*{0,2}\s*(?:bước kế tiếp|bước tiếp theo)\b", t)) or t.count("➡️")
    return n == 1


def check_grounded_names(reply: str, code: str, exercise: dict, extra_text: str = "") -> bool:
    # extra_text: văn bản được phép trích nguyên văn (thông báo lỗi của trình thông dịch, traceback) của lần chạy hiện tại.
    """Mọi tên biến/hàm trong `backtick` phải có trong code người học, đề bài, test hoặc là built-in Python."""
    text, _ = split_blocks(reply)
    allowed = set(_PY_NAMES) | _GENERIC_NAMES
    sources = [code or "", exercise.get("title", ""), exercise.get("description", ""), exercise.get("starter_code", "") or "", extra_text]
    for tc in exercise.get("test_cases", []):
        sources += [str(tc.get("input", "")), str(tc.get("expected_output", "")), str(tc.get("description", ""))]
    for src in sources:
        allowed |= set(re.findall(r"[A-Za-z_]\w*", src))
    for span in _SPAN.findall(text):
        if not span.isascii() or len(span) > 60 or _EVIDENCE_LABEL.match(span):
            continue
        if not re.search(r"[()=\[\]._]", span) and not re.fullmatch(r"[A-Za-z_]\w*", span):
            continue
        for name in re.findall(r"[A-Za-z_]\w*", re.sub(r"(\"[^\"]*\"|'[^']*')", " ", span)):
            if len(name) > 2 and name not in allowed:
                return False
    return True


def _without_system_notes(reply: str) -> str:
    """Bỏ các dòng thông báo của chính hệ thống (bắt đầu bằng 🔒), vì đó không phải lời gợi ý của gia sư."""
    return "\n".join(ln for ln in (reply or "").splitlines() if not ln.lstrip(" *_>").startswith("🔒"))


def check_no_fix_phrases(reply: str) -> bool:
    return not _FIX_PHRASES.search(_without_system_notes(reply))


def leaked_core(reply: str, code: str, patterns: list[str]) -> list[str]:
    """Các mẫu biểu thức lời giải xuất hiện trong phản hồi mà KHÔNG nằm sẵn trong code người học."""
    leaks = []
    code_n = norm(code)
    for pat in patterns:
        for m in re.finditer(pat, reply or "", flags=re.IGNORECASE):
            if norm(m.group(0)) not in code_n:
                leaks.append(m.group(0))
                break
    return leaks


# ----------------------------------------------------------------------------------------------
# Mức 1
# ----------------------------------------------------------------------------------------------
def check_l1_no_test_specifics(reply: str, test_results: dict) -> bool:
    """Mức 1 không nêu đầu vào/kỳ vọng/thực tế cụ thể của test fail (nhãn bằng chứng hoặc giá trị trong `backtick`)."""
    text, blocks = split_blocks(reply)
    if _LABELED_VALUE.search(text) or any(_EVIDENCE_LABEL.match(s) for s in _SPAN.findall(text)):
        return False
    for tc in first_failures(test_results):
        for key in ("input", "expected_output", "actual_output"):
            val = (tc.get(key) or "").strip()
            if val and any(span.strip() == val for span in _SPAN.findall(text)):
                return False
    return True


def check_l1_no_code_quote(reply: str, code: str, starter: str) -> bool:
    return not quoted_student_lines(reply, code, starter)


def check_no_code_block(reply: str) -> bool:
    return not _FENCE.search(reply or "")


def check_names_concept(reply: str, concept_terms: list[str]) -> bool:
    t = (reply or "").lower()
    return any(term.lower() in t for term in concept_terms)


def check_l1_informative(reply: str, concept_terms: list[str]) -> bool:
    """Không chỉ là câu hỏi suông: có ít nhất một câu KHÔNG phải câu hỏi nêu khái niệm, hoặc một phép thử cụ thể."""
    text, _ = split_blocks(reply)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?:])\s+|\n+", text) if s.strip()]
    declarative = [s for s in sentences if "?" not in s and len(words(s)) >= 6
                   and any(term.lower() in s.lower() for term in concept_terms)]
    probe = bool(re.search(r"(tự tính|tính tay|chạy thử với|thử với một|đầu vào nhỏ|ví dụ nhỏ|chạy từng bước|viết ra giấy|bảng)", text, flags=re.IGNORECASE))
    return bool(declarative) or probe


# ----------------------------------------------------------------------------------------------
# Mức 2
# ----------------------------------------------------------------------------------------------
def check_l2_quotes_one_line(reply: str, code: str, starter: str) -> bool:
    return len(quoted_student_lines(reply, code, starter)) == 1


def check_l2_points_at_expected(reply: str, code: str, starter: str, expected_lines: list[str]) -> Optional[bool]:
    if not expected_lines:
        return None
    quoted = quoted_student_lines(reply, code, starter)
    wanted = [norm(strip_comment(x)) for x in expected_lines]
    return bool(quoted) and all(q in wanted for q in quoted)


def check_l2_evidence(reply: str, test_results: dict, ast_analysis: dict, expect: str) -> Optional[bool]:
    """Mức 2 nêu bằng chứng thực thi của (một) test fail: đầu vào + kỳ vọng + thực tế; hoặc lỗi/TIMEOUT/cú pháp."""
    if expect in ("BLANK", "PASS"):
        return None
    text = reply or ""
    fails = first_failures(test_results)
    if expect == "SYNTAX_ERROR":
        err = (ast_analysis or {}).get("syntax_error") or {}
        line_no = err.get("lineno")
        msg = (err.get("message") or "").strip()
        has_line = bool(line_no) and bool(re.search(rf"dòng\s*\**\s*{line_no}\b", text, flags=re.IGNORECASE))
        return has_line or (bool(msg) and msg in text)
    for tc in fails:
        status = tc.get("status")
        inp_ok = _values_in_spans(text, tc.get("input", ""))
        if status == "TIMEOUT":
            if inp_ok and _TIMEOUT_WORDS.search(text):
                return True
            continue
        if status == "RUNTIME_ERROR":
            etype = (tc.get("error_message") or "").split(":")[0].strip()
            if etype and etype in text and inp_ok:
                return True
            continue
        exp_ok = _values_in_spans(text, tc.get("expected_output", ""))
        act = (tc.get("actual_output") or "").strip()
        act_ok = _values_in_spans(text, act) if act else bool(_EMPTY_ACTUAL.search(text))
        if not act and not act_ok:
            act_ok = False
        if inp_ok and exp_ok and act_ok:
            return True
    return False


# ----------------------------------------------------------------------------------------------
# Mức 3
# ----------------------------------------------------------------------------------------------
def check_l3_steps(reply: str, exercise_terms: list[str]) -> Optional[bool]:
    """Có đủ Bước 1-4, không phải khuôn chung, và nhắc ít nhất hai thuật ngữ riêng của bài."""
    text, _ = split_blocks(reply)
    nums = set(re.findall(r"(?i)b[ưứ][ơớ]c\s*([1-4])\b", text))
    if nums != {"1", "2", "3", "4"}:
        return False
    low = text.lower()
    generic_hits = sum(1 for g in _GENERIC_L3 if g in low)
    specific = sum(1 for term in exercise_terms if term.lower() in low)
    return generic_hits <= 1 and specific >= 2


def check_l3_has_skeleton(reply: str) -> bool:
    _, blocks = split_blocks(reply)
    return any(("TODO" in b or "..." in b) for b in blocks)


def skeleton_block(reply: str) -> str:
    _, blocks = split_blocks(reply)
    return max(blocks, key=len) if blocks else ""


def check_l3_skeleton_not_passing(reply: str, tests: list[dict]) -> Optional[bool]:
    """Khung (sau khi che) đem chạy với bộ test không được đạt hết. None nếu không có khối code."""
    block = skeleton_block(reply)
    if not block.strip():
        return None
    from mcp_server.sandbox import run_test_cases
    try:
        ast.parse(block)
    except SyntaxError:
        return True
    return not run_test_cases(block, tests).get("all_passed", False)


def check_l3_skeleton_valid_python(reply: str) -> Optional[bool]:
    block = skeleton_block(reply)
    if not block.strip():
        return None
    try:
        ast.parse(block)
        return True
    except SyntaxError:
        return False


def check_l3_has_trace_table(reply: str) -> bool:
    """Bảng chạy tay để trống (v5.10): bảng Markdown có ít nhất 3 cột."""
    return bool(re.search(r"(?m)^\s*\|(?:[^|\n]+\|){3,}\s*$", reply or "")) and bool(re.search(r"(?i)chạy tay|bảng theo dõi|điền", reply or ""))


def check_l3_keeps_student_lines(reply: str, code: str, starter: str) -> bool:
    _, blocks = split_blocks(reply)
    body = norm(" ".join(blocks))
    starter_lines = set(code_lines(starter))
    lines = [ln for ln in code_lines(code) if len(ln) >= MIN_LINE_CHARS and ln not in _TRIVIAL_LINES and ln not in starter_lines]
    return any(ln in body for ln in lines)


# ----------------------------------------------------------------------------------------------
# Tăng tiến & trùng lặp
# ----------------------------------------------------------------------------------------------
def ngram_set(text: str, n: int = 3) -> set[tuple[str, ...]]:
    toks = [w.lower() for w in words(text)]
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def jaccard(a: str, b: str, n: int = 3) -> float:
    sa, sb = ngram_set(a, n), ngram_set(b, n)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def check_progress_l1_to_l2(l1_reply: str, l2_reply: str, test_results: dict, ast_analysis: dict, expect: str) -> Optional[bool]:
    """Mức 2 có bằng chứng thực thi mà Mức 1 không có."""
    if expect in ("BLANK", "PASS"):
        return None
    return bool(check_l2_evidence(l2_reply, test_results, ast_analysis, expect)) and not bool(check_l2_evidence(l1_reply, test_results, ast_analysis, expect))


def check_progress_l2_to_l3(l2_reply: str, l3_reply: str) -> bool:
    """Mức 3 có cấu trúc (dàn ý + khung) mà Mức 2 không có."""
    return check_l3_has_skeleton(l3_reply) and not _FENCE.search(l2_reply or "")


# ----------------------------------------------------------------------------------------------
# Chú thích của người học là dữ liệu không tin cậy: không được chép lại vào gợi ý (v5.10, red-team)
# ----------------------------------------------------------------------------------------------
def student_comments(code: str, starter: str = "") -> list[str]:
    """Văn bản chú thích `# ...` và chuỗi nhiều dòng của người học, trừ những chú thích đã có sẵn trong khung mẫu của bài."""
    def extract(src: str) -> list[str]:
        out = []
        for raw in (src or "").splitlines():
            tail = raw[len(strip_comment(raw)):].lstrip("# ").strip()
            if tail:
                out.append(tail)
        out += [m.strip() for m in re.findall(r'(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', src or "", flags=re.DOTALL) if m.strip()]
        return out
    known = set(extract(starter))
    return [c for c in extract(code) if c not in known]


def check_no_comment_echo(reply: str, code: str, starter: str = "", n: int = 4) -> Optional[bool]:
    """Không chép lại (n từ liên tiếp trở lên) bất kỳ chú thích nào của người học vào phản hồi. None nếu người học không có chú thích."""
    comments = student_comments(code, starter)
    if not comments:
        return None
    reply_grams = ngram_set(reply, n)
    return not any(ngram_set(c, n) & reply_grams for c in comments)
