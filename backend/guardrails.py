"""Input/output safety checks for the student-facing AI tutor."""
from __future__ import annotations

import re


INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"(bỏ qua|quên)\s+(mọi\s+)?(chỉ dẫn|hướng dẫn|quy tắc)\s+(trước|trên)",
    r"(reveal|print|show)\s+(the\s+)?(full\s+)?(solution|answer|system prompt)",
    r"(in|xuất)\s+(ra\s+)?(toàn bộ\s+)?(đáp án|lời giải|system prompt)",
    r"act\s+as\s+(a\s+)?(different|new)\s+persona",
)


def check_student_input(message: str) -> tuple[bool, str]:
    text = message.strip()
    if not text:
        return False, "empty"
    if len(text) > 2000:
        return False, "too_long"
    if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in INJECTION_PATTERNS):
        return False, "prompt_injection"
    if re.search(r"\b(politics|politician|election|religion|tôn giáo|chính trị)\b", text, flags=re.IGNORECASE):
        # Allow explicit programming concepts that contain otherwise ambiguous words.
        if not re.search(r"\b(python|code|lập trình|programming|function|hàm)\b", text, flags=re.IGNORECASE):
            return False, "out_of_scope"
    return True, "allowed"


def check_student_output(reply: str, *, max_code_lines: int = 3) -> tuple[bool, str]:
    if not reply.strip():
        return False, "empty_output"
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", reply, flags=re.IGNORECASE | re.DOTALL)
    for block in blocks:
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) >= max_code_lines:
            return False, "solution_code_block"
    # Also catch code pasted without fences (common Markdown evasions).
    code_like = [line for line in reply.splitlines() if re.match(
        r"\s*(def\s+\w+\s*\(|for\s+.+\s+in\s+|while\s+|return\b|print\s*\(|\w+\s*(?:\+=|-=|\*=|/=|=)|if\s+.+:)", line
    )]
    if len(code_like) >= max_code_lines:
        return False, "solution_unfenced_code"
    if re.search(r"(đáp án hoàn chỉnh|lời giải hoàn chỉnh|copy\s*[- ]?paste\s+nộp bài)", reply, flags=re.IGNORECASE):
        return False, "solution_disclosure"
    return True, "allowed"
