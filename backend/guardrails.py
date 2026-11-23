"""Input/output safety checks for the student-facing AI tutor.

Bộ luật tất định (regex). Hiệu quả được đo bằng `evaluate_guardrails_benchmark.py` trên corpus cố định
`evaluation/guardrail_corpus.json`; kết quả chỉ đúng với corpus đó, không phải bảo đảm tuyệt đối.
"""
from __future__ import annotations

import re

# Phiên bản bộ luật; được ghi trong báo cáo benchmark để kết quả gắn với đúng bộ luật.
# v1: Phase 16 (khối code có rào ≥ 3 dòng, code không rào, cụm từ tiết lộ).
# v2: thêm chương trình một dòng, code chia nhỏ/đánh số/trích dẫn/nối bằng ';', code trong `inline`,
#     rào ~~~ và <pre>; siết mẫu injection để không chặn nhầm câu hỏi về định dạng đầu ra.
# v3 (v5.12): thêm `enforce_level3_prose` (che biểu thức/câu lệnh Python trong phần chữ của gợi ý Mức 3); luật cũ không đổi.
GUARD_RULES_VERSION = "3"

MAX_INPUT_CHARS = 2000

INJECTION_PATTERNS = (
    # Yêu cầu bỏ qua chỉ dẫn (EN/VI)
    r"(ignore|disregard|forget)\s+(all\s+|everything\s+)?(the\s+|your\s+)?(previous|prior|above|earlier)",
    r"(bỏ qua|quên|phớt lờ|lờ đi|bỏ hết)\s+(mọi\s+|các\s+|tất cả\s+|hết\s+)?(chỉ dẫn|hướng dẫn|quy tắc|luật lệ)",
    r"new\s+instructions\s*:",
    # Dò system prompt / chỉ dẫn hệ thống
    r"system\s+prompt",
    r"(chỉ dẫn|hướng dẫn|lời nhắc|quy tắc)\s+hệ thống",
    # Đổi vai / gỡ giới hạn
    r"act\s+as\s+(a\s+)?(different|new)\s+persona",
    r"you\s+are\s+now\b",
    r"\b(dan|jailbreak)\b",
    r"without\s+(any\s+)?(restrictions|rules|limits)",
    r"đóng vai\s+(một\s+)?(ai|trợ lý|chatbot|persona)\s+khác",
    r"không\s+(còn\s+)?(bị\s+)?(giới hạn|ràng buộc)",
    r"(developer\s+mode|chế độ\s+nhà phát triển)",
    # Đòi toàn bộ lời giải (chỉ khi có từ chỉ "toàn bộ/đầy đủ" để không chặn câu hỏi về in kết quả)
    r"(reveal|show|give|print|output)\s+(me\s+)?(the\s+)?(full|complete|entire|whole)\s+(solution|answer|code)",
    r"(in|xuất)\s+(ra\s+)?toàn bộ\s+(đáp án|lời giải)",
)

_OFF_TOPIC = r"\b(politics|politician|election|religion|tôn giáo|chính trị)\b"
_PROGRAMMING_CONTEXT = r"\b(python|code|lập trình|programming|function|hàm|dict|list|vòng lặp|thuật toán)\b"

# Một "dòng trông như câu lệnh Python".
_STATEMENT = re.compile(
    r"\s*(def\s+\w+\s*\(|for\s+.+\s+in\s+|while\s+|return\b|print\s*\(|\w+(?:\s*,\s*\w+)*\s*(?:\+=|-=|\*=|/=|=)(?!=)|if\s+.+:|elif\s+.+:|else\s*:)"
)
_LIST_PREFIX = re.compile(r"^\s*(?:[-*•>]+|\d+[.)])\s+")
_FENCE = re.compile(r"(?:```|~~~)[^\n]*\n(.*?)(?:```|~~~)", flags=re.DOTALL)
_HTML_CODE = re.compile(r"<(?:pre|code)[^>]*>(.*?)</(?:pre|code)>", flags=re.DOTALL | re.IGNORECASE)
_INLINE = re.compile(r"`([^`\n]+)`")
_DISCLOSURE = re.compile(
    r"(đáp án hoàn chỉnh|lời giải hoàn chỉnh|copy\s*[- ]?paste\s+nộp bài|"
    r"(complete|full|entire)\s+(solution|answer)|chép vào là được)", flags=re.IGNORECASE)
_NEGATION = re.compile(r"(không|chưa|chẳng|won't|will not|cannot|can't|don't|do not|not)\W+(\w+\W+){0,4}$", flags=re.IGNORECASE)


def check_student_input(message: str) -> tuple[bool, str]:
    text = message.strip()
    if not text:
        return False, "empty"
    if len(text) > MAX_INPUT_CHARS:
        return False, "too_long"
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in INJECTION_PATTERNS):
        return False, "prompt_injection"
    if re.search(_OFF_TOPIC, text, flags=re.IGNORECASE):
        # Allow explicit programming concepts that contain otherwise ambiguous words.
        if not re.search(_PROGRAMMING_CONTEXT, text, flags=re.IGNORECASE):
            return False, "out_of_scope"
    return True, "allowed"


def _is_complete_program(snippet: str) -> bool:
    """Đoạn mã vừa đọc đầu vào vừa in kết quả là một chương trình nộp được, dù chỉ một dòng."""
    return "input(" in snippet and "print(" in snippet


def _statement_lines(text: str) -> list[str]:
    """Các dòng trông như câu lệnh, sau khi bỏ tiền tố danh sách/trích dẫn và tách theo ';'."""
    found = []
    for raw in text.splitlines():
        line = _LIST_PREFIX.sub("", raw)
        for part in line.split(";"):
            if _STATEMENT.match(part):
                found.append(part.strip())
    return found


# ---------------------------------------------------------------------------------------------
# Mức 3: khung mã chỉ được cho CẤU TRÚC, không cho LOGIC.
# Mức 3 được phép có khối code dài (dàn ý 4 bước + khung `# TODO`), nên `check_student_output` không
# áp dụng. Thay vì chặn cả phản hồi, hàm dưới đây che tất định các biểu thức mang logic lời giải
# (điều kiện, miền lặp, vế phải phép gán, lời gọi xử lý) và giữ nguyên phần giàn giáo (đọc đầu vào,
# khởi tạo bằng hằng, `print`, `else:`, chú thích, dòng đã có `...`/TODO).
# ---------------------------------------------------------------------------------------------
_L3_FENCE = re.compile(r"(```|~~~)([^\n]*)\n(.*?)(```|~~~)", flags=re.DOTALL)
_L3_COND = re.compile(r"^(\s*)(if|elif|while)\s+(.+?):\s*(#.*)?$")
_L3_FOR = re.compile(r"^(\s*)for\s+(.+?)\s+in\s+(.+?):\s*(#.*)?$")
_L3_ASSIGN = re.compile(r"^(\s*)([A-Za-z_][\w\[\]., ]*?)\s*(\+=|-=|\*=|//=|/=|%=|=)(?!=)\s*(.+?)\s*(#.*)?$")
_L3_RETURN = re.compile(r"^(\s*)return\s+(.+?)\s*(#.*)?$")
_L3_LITERAL = re.compile(r"^(?:-?\d+(?:\.\d+)?|True|False|None|\"[^\"]*\"|'[^']*'|\[\]|\{\}|\(\)|set\(\)|list\(\)|dict\(\))$")
# Đọc dữ liệu thuần: `x = input()`, `n = int(input())`, `a, b = map(int, input().split())`, ...
_L3_PLAIN_INPUT = re.compile(
    r"^\s*[A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*\s*=\s*"
    r"(?:(?:int|float|str)\(\s*input\([^()]*\)(?:\.strip\(\))?\s*\)"
    r"|input\([^()]*\)(?:\.strip\(\))?(?:\.split\([^()]*\))?"
    r"|(?:list\()?map\(\s*(?:int|float|str)\s*,\s*input\([^()]*\)\.split\([^()]*\)\s*\)\)?)\s*(#.*)?$")
# In hằng chuỗi/số hoặc tên biến (không có phép tính, lời gọi hàm, chỉ số, f-string).
_L3_PRINT_ARG = r"(?:\"[^\"{}]*\"|'[^'{}]*'|-?\d+(?:\.\d+)?|[A-Za-z_]\w*)"
_L3_PLAIN_PRINT = re.compile(
    r"^\s*print\(\s*(?:" + _L3_PRINT_ARG + r"(?:\s*,\s*" + _L3_PRINT_ARG + r")*)?"
    r"(?:\s*,\s*(?:sep|end)\s*=\s*(?:\"[^\"]*\"|'[^']*'))*\s*\)\s*(#.*)?$")
_L3_KEEP = re.compile(r"^\s*(else\s*:|try\s*:|finally\s*:|except\b.*:|def\s+\w+\s*\(.*\)\s*(->.*)?:|class\s+\w+.*:|"
                      r"break|continue|pass|return|import\s+.+|from\s+.+\s+import\s+.+)\s*(#.*)?$")


def _mask_level3_line(line: str) -> tuple[str, bool]:
    """Trả về (dòng sau khi che, có che hay không) cho một dòng trong khung mã Mức 3."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return line, False
    if "..." in line or "TODO" in line:
        return line, False
    indent = line[: len(line) - len(line.lstrip())]
    if _L3_PLAIN_INPUT.match(line) or _L3_PLAIN_PRINT.match(line) or _L3_KEEP.match(line):
        return line, False  # giàn giáo: đọc dữ liệu thuần, in hằng/biến, từ khóa cấu trúc
    if stripped.startswith("print("):
        # in một biểu thức tính toán (công thức, slice, lời gọi hàm, input lồng) chính là lời giải
        return f"{indent}print(...)  # TODO: tự xác định giá trị cần in", True
    if "input(" in line and _L3_ASSIGN.match(line):
        # đọc dữ liệu kèm xử lý trên cùng dòng: giữ tên biến, che phần xử lý
        target = _L3_ASSIGN.match(line).group(2)
        return f"{indent}{target} = ...  # TODO: đọc dữ liệu rồi xử lý", True
    m = _L3_COND.match(line)
    if m:
        return f"{m.group(1)}{m.group(2)} ...:  # TODO: tự viết điều kiện", True
    m = _L3_FOR.match(line)
    if m:
        return f"{m.group(1)}for {m.group(2)} in ...:  # TODO: tự xác định miền lặp", True
    m = _L3_ASSIGN.match(line)
    if m:
        if m.group(3) == "=" and _L3_LITERAL.match(m.group(4)):
            return line, False  # khởi tạo bằng hằng là giàn giáo
        return f"{m.group(1)}{m.group(2)} {m.group(3)} ...  # TODO: tự viết biểu thức", True
    m = _L3_RETURN.match(line)
    if m:
        return f"{m.group(1)}return ...  # TODO: tự viết giá trị trả về", True
    return f"{indent}...  # TODO: tự viết lệnh xử lý", True


def enforce_level3_skeleton(reply: str) -> tuple[str, int]:
    """Che logic lời giải trong các khối code của gợi ý Mức 3.

    Trả về (phản hồi đã che, số dòng bị che). Tất định, không gọi mô hình; văn bản ngoài khối code
    (dàn ý các bước) được giữ nguyên. Chỉ dùng khi bài chưa đạt hết kiểm thử.
    """
    masked_total = 0

    def _mask_block(match: re.Match) -> str:
        nonlocal masked_total
        out = []
        for line in match.group(3).splitlines():
            new_line, masked = _mask_level3_line(line)
            masked_total += int(masked)
            out.append(new_line)
        return f"{match.group(1)}{match.group(2)}\n" + "\n".join(out) + f"\n{match.group(4)}"

    result = _L3_FENCE.sub(_mask_block, reply)
    if masked_total:
        result = result.rstrip() + (
            "\n\n🔒 *PyTutor đã thay " + str(masked_total) + " biểu thức trong khung mã bằng `...` để phần lập luận "
            "vẫn là của bạn. Hãy điền từng chỗ rồi bấm Chạy thử sau mỗi bước.*")
    return result, masked_total


# ---------------------------------------------------------------------------------------------
# Mức 3 (v5.12): thuật toán chi tiết viết bằng LỜI. Phần chữ ngoài khối code không được chứa biểu thức/câu lệnh Python
# của lời giải (ví dụ `range(1, n + 1)`, `tong += i`, `s[::-1]`). Các giá trị đầu vào/đầu ra của kiểm thử (đã hiển thị cho
# sinh viên) và tên biến/hằng thì được giữ.
# ---------------------------------------------------------------------------------------------
_L3_SPAN = re.compile(r"`([^`\n]+)`")
_L3_SAFE_SPAN = re.compile(r"^(?:[A-Za-z_]\w*|-?\d+(?:\.\d+)?|\"[^\"]*\"|'[^']*'|\.{3}|…)$")
_L3_LOGIC_CHARS = re.compile(r"[+*/%<>=\[\]()]|\bfor\b|\bin\b|\bif\b|\band\b|\bor\b|\bnot\b|\w\s-\s\w")


def _prose_span_is_logic(span: str, allowed: set[str]) -> bool:
    s = span.strip()
    if not s or _L3_SAFE_SPAN.match(s) or " ".join(s.split()) in allowed:
        return False
    return bool(_L3_LOGIC_CHARS.search(s))


def enforce_level3_prose(reply: str, allowed: tuple[str, ...] | list[str] = ()) -> tuple[str, int]:
    """Che biểu thức/câu lệnh Python nằm trong PHẦN CHỮ (ngoài khối code) của gợi ý Mức 3.

    `allowed`: các giá trị đầu vào/đầu ra của kiểm thử được phép xuất hiện trong dấu backtick. Trả về (phản hồi, số chỗ bị che).
    Tất định, không gọi mô hình; khối code do `enforce_level3_skeleton` xử lý riêng.
    """
    allowed_n = {" ".join(str(a).split()) for a in allowed if str(a).strip()}
    masked = 0

    def _prose(segment: str) -> str:
        nonlocal masked

        def _span(m: re.Match) -> str:
            nonlocal masked
            if _prose_span_is_logic(m.group(1), allowed_n):
                masked += 1
                return "`…`"
            return m.group(0)

        lines = []
        for line in segment.split("\n"):
            core = _LIST_PREFIX.sub("", line)
            if _STATEMENT.match(core) and not _L3_SPAN.search(line) and len(core.split()) <= 12 and re.search(r"[=()]", core):
                masked += 1
                lines.append("…")
            else:
                lines.append(_L3_SPAN.sub(_span, line))
        return "\n".join(lines)

    out, pos = [], 0
    for m in _L3_FENCE.finditer(reply):
        out.append(_prose(reply[pos:m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(_prose(reply[pos:]))
    result = "".join(out)
    if masked:
        result = result.rstrip() + ("\n\n🔒 *PyTutor đã ẩn " + str(masked) + " đoạn mã giải nằm trong phần mô tả thuật toán; "
                                    "hãy tự diễn đạt phép tính đó bằng lời rồi viết thành lệnh.*")
    return result, masked


_EVIDENCE_LABEL = re.compile(r"^\s*(input|expected\s+output|actual\s+output|output|đầu vào|kỳ vọng|thực tế)\s*[=:]", flags=re.IGNORECASE)


def _is_quoted_context(span: str, quoted_context: str) -> bool:
    """Đoạn inline chỉ trích lại thứ người học đã có: một dòng code của chính họ, hoặc nhãn bằng chứng kiểm thử.

    Chẩn đoán Mức 2 cần trích dòng lỗi của người học và đầu vào/đầu ra của kiểm thử; đó không phải là lời giải.
    """
    text = span.strip()
    if _EVIDENCE_LABEL.match(text):
        return True
    norm = " ".join(text.split())
    return bool(quoted_context) and bool(norm) and norm in " ".join(quoted_context.split())


def check_student_output(reply: str, *, max_code_lines: int = 3, quoted_context: str = "") -> tuple[bool, str]:
    if not reply.strip():
        return False, "empty_output"

    # 1) Khối code có rào (``` hoặc ~~~, mọi nhãn ngôn ngữ) và thẻ <pre>/<code>.
    blocks = _FENCE.findall(reply) + _HTML_CODE.findall(reply)
    fenced_lines = 0
    for block in blocks:
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) >= max_code_lines:
            return False, "solution_code_block"
        if _is_complete_program(block):
            return False, "complete_program"
        fenced_lines += len(lines)
    # Nhiều khối ngắn ghép lại vẫn là lời giải.
    if len(blocks) > 1 and fenced_lines >= max_code_lines:
        return False, "solution_split_blocks"

    # 2) Code không rào: kể cả khi đánh số, gạch đầu dòng, trích dẫn '>' hoặc nối bằng ';'.
    statements = _statement_lines(reply)
    if len(statements) >= max_code_lines:
        return False, "solution_unfenced_code"

    # 3) Code rải trong `inline`: nhiều câu lệnh, hoặc một chương trình đọc-in hoàn chỉnh.
    inline_spans = _INLINE.findall(reply)
    inline_statements = [span for span in inline_spans if _STATEMENT.match(span)
                         and not _is_quoted_context(span, quoted_context)]
    if len(inline_statements) >= max_code_lines:
        return False, "solution_inline_code"
    if any(_is_complete_program(span) for span in inline_spans) or _is_complete_program(" ".join(inline_statements)):
        return False, "complete_program"
    # Một dòng lệnh không rào vừa đọc vừa in (chỉ xét dòng trông như câu lệnh, không xét câu văn giải thích).
    if any(_is_complete_program(line) for line in statements):
        return False, "complete_program"

    # 4) Cụm từ thông báo "đây là lời giải hoàn chỉnh" — bỏ qua khi đang ở thể phủ định (lời từ chối).
    for match in _DISCLOSURE.finditer(reply):
        if not _NEGATION.search(reply[max(0, match.start() - 40):match.start()]):
            return False, "solution_disclosure"
    return True, "allowed"
