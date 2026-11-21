"""Gợi ý 3 mức theo luật (nhánh offline / khi bộ lọc chặn) dựa trên bằng chứng tất định (v5.10).

Cùng ranh giới ba mức với nhánh Gemini:
  Mức 1  Socratic về KHÁI NIỆM: gọi tên nhóm khái niệm, giải thích bằng lời, một phép thử người học tự làm, đúng một câu hỏi.
         Không trích dòng code, không nêu đầu vào/đầu ra cụ thể của kiểm thử, không chỉ tham số hay biểu thức sai.
  Mức 2  chẩn đoán có bằng chứng thực thi: đúng MỘT dòng mã của người học + đầu vào/kỳ vọng/thực tế (hoặc lỗi, TIMEOUT, thông báo cú pháp).
         Không nêu cách sửa, điều kiện hay biểu thức thay thế.
  Mức 3  CẤU TRÚC của bài, không phải logic: dàn ý 4 bước theo đề, khung mã bám mã người học (logic đã bị che bằng `enforce_level3_skeleton`),
         bảng chạy tay để trống.
Mọi câu chỉ nêu điều quan sát được từ kiểm thử, AST, traceback hoặc vết chạy; không khẳng định nguyên nhân vượt bằng chứng.
"""
from __future__ import annotations

import ast
import re
from typing import Optional

from backend import exercise_brief
from backend import hint_evidence as he
from backend.guardrails import enforce_level3_skeleton
from backend.hint_evidence import CodeFacts

LEVEL_HEAD = {
    1: "💡 **[MỨC 1: GỢI MỞ TƯ DUY & KHÁI NIỆM]**",
    2: "🔍 **[MỨC 2: CHẨN ĐOÁN CHI TIẾT & KHOANH VÙNG LỖI]**",
    3: "📘 **[MỨC 3: DÀN Ý THUẬT TOÁN CHI TIẾT & KHUNG CODE MẪU]**",
}
KIND_VI = {
    "syntax": "chương trình chưa chạy được vì lỗi cú pháp",
    "runtime": "chương trình dừng giữa chừng với một lỗi khi chạy",
    "timeout": "chương trình chạy quá thời gian cho phép",
    "wrong_output": "chương trình chạy được nhưng kết quả in ra chưa khớp kỳ vọng",
}


# ----------------------------------------------------------------------------------------------
# Hàm dùng chung (trước đây nằm trong llm_service)
# ----------------------------------------------------------------------------------------------
def adaptation(adaptive_strategy: Optional[dict], code: str) -> Optional[dict]:
    return next((a for a in (adaptive_strategy or {}).get("adaptations", []) if a.get("code") == code), None)


def next_step_line(step: str, adaptive_strategy: Optional[dict]) -> str:
    """Dòng 'Bước kế tiếp' theo độ chi tiết đã chọn. Mẫu cố định, chỉ nói về quy trình, không nêu lời giải."""
    gran = (adaptive_strategy or {}).get("granularity")
    if gran == "fine":
        return ("➡️ **Bước kế tiếp (chia nhỏ thành 2 bước):**\n"
                f"1. {step[:1].upper() + step[1:]}\n"
                "2. Sau đó bấm Chạy thử và ghi lại một điều bạn quan sát được (kết quả in ra hoặc thông báo lỗi) trước khi sửa tiếp.")
    if gran == "coarse":
        return ("➡️ **Bước kế tiếp (tự kiểm trước):** hãy tự nêu một câu giả thuyết: *chỗ nào trong chương trình có thể làm kết quả lệch?* "
                "Rồi bấm Chạy thử để tự kiểm giả thuyết đó trước khi đọc thêm.")
    return f"➡️ **Bước kế tiếp:** {step}"


def model_notes(adaptive_strategy: Optional[dict]) -> str:
    """Các câu ghi chú cố định theo mã điều chỉnh của mô hình người học (ngoài khối mã)."""
    notes = []
    bridge = adaptation(adaptive_strategy, "bridge_from_mastered")
    if bridge:
        ctx = bridge.get("context", {})
        notes.append(f"🌉 **Nối với điều bạn đã làm:** nhóm **{ctx.get('kc_label', '')}** bạn đã nộp đạt ở bài "
                     f"**{ctx.get('exercise_title', '')}**. Hãy nhớ lại bạn đã tách phần việc ở bài đó thành những bước nào.")
    rep = adaptation(adaptive_strategy, "repeated_error_type")
    if rep:
        ctx = rep.get("context", {})
        notes.append(f"🔎 **Dạng lỗi lặp lại:** loại lỗi lần này (`{ctx.get('error_class', '')}`) giống loại lỗi bạn từng gặp ở nhóm "
                     f"**{ctx.get('kc_label', '')}**; hãy so sánh với cách bạn đã sửa trước đó.")
    return "\n\n".join(notes)


def level3_progress_note(code: str, adaptive_strategy: Optional[dict] = None) -> str:
    """Đối chiếu bài làm hiện tại với dàn ý 4 bước và chọn MỘT bước kế tiếp còn thiếu (rút giàn giáo cho phần đã tự viết)."""
    lines = [ln for ln in (code or "").splitlines() if ln.strip() and not ln.strip().startswith("#")]
    has_input = any("input(" in ln for ln in lines)
    has_print = any("print(" in ln for ln in lines)
    has_flow = any(re.match(r"\s*(if|for|while)\b", ln) for ln in lines)
    seen = [name for name, ok in (("Bước 1 (đọc dữ liệu)", has_input), ("Bước 3 (rẽ nhánh/vòng lặp)", has_flow),
                                  ("Bước 4 (in kết quả)", has_print)) if ok]
    observed = (f"👀 **Đã thấy trong bài làm:** {', '.join(seen)}. Hệ thống chỉ thấy các phần này *có mặt*, "
                f"chưa biết chúng đã đúng hay chưa.\n\n") if seen else ""
    if not has_input:
        step = "viết Bước 1 trước, rồi in thử giá trị vừa đọc và bấm Chạy thử để chắc phần nhập đúng."
    elif not has_print:
        step = ("bạn đã có Bước 1. Hãy viết Bước 4 trước (in tạm một giá trị), Chạy thử để chắc phần nhập/xuất "
                "đúng định dạng, rồi mới viết Bước 3.")
    elif not has_flow:
        step = ("phần nhập và in đã có. Giờ tập trung vào Bước 3: tự tính tay với một đầu vào nhỏ, "
                "viết lại các thao tác bạn vừa làm thành lệnh.")
    else:
        step = ("bài làm đã có đủ bốn phần của dàn ý, nên chỗ cần xem lại là Bước 2 và Bước 3. Dùng **Chạy từng bước** "
                "với một đầu vào chưa đạt và tìm dòng đầu tiên mà giá trị biến khác điều bạn dự tính.")
    return f"{observed}{next_step_line(step, adaptive_strategy)}"


def repeat_count(attempt_history: Optional[list], level: int) -> int:
    """Số lần người học đã xin gợi ý ĐÚNG mức này (ask_ai) cho bài hiện tại, theo lịch sử gần nhất."""
    return sum(1 for h in (attempt_history or []) if h.get("action_type") == "ask_ai" and int(h.get("hint_level", 0) or 0) == level)


def classify(failure: Optional[dict], ast_analysis: dict, test_results: dict) -> Optional[str]:
    """syntax | timeout | runtime | wrong_output | None (không có test lỗi)."""
    if not ast_analysis.get("valid", True):
        return "syntax"
    if failure is None:
        return None
    status = failure.get("status")
    if status == "SYNTAX_ERROR":
        return "syntax"
    if status == "TIMEOUT":
        return "timeout"
    if status == "RUNTIME_ERROR":
        return "runtime"
    return "wrong_output"


def _progress_line(title: str, test_results: dict, kind: Optional[str]) -> str:
    p, t = test_results.get("passed_tests", 0), test_results.get("total_tests", 0)
    if kind == "syntax":
        return "🎯 **Đang ở đâu:** chương trình chưa chạy được nên chưa kiểm thử nào được chấm."
    return f"🎯 **Đang ở đâu:** bài **{title}** đang đạt **{p}/{t}** kiểm thử."


# ----------------------------------------------------------------------------------------------
# Mức 1
# ----------------------------------------------------------------------------------------------
def _level1(ev: dict, adaptive_strategy: Optional[dict], repeats: int, extra: str) -> str:
    c, kind = ev["concept"], ev["kind"]
    head = [LEVEL_HEAD[1]]
    if repeats:
        head.append(f"↻ Bạn đã xin gợi ý Mức 1 cho bài này trước đó, nên lần này đi tiếp một bước nhỏ, vẫn về **{c['name']}**.")
    parts = [head[0] + ("\n\n" + head[1] if repeats else ""), ev["progress"],
             f"🔎 **Bằng chứng (tổng quát):** {KIND_VI.get(kind, 'chưa có kiểm thử cụ thể nào được ghi nhận là lỗi, nên dữ liệu chưa đủ để khoanh vùng')}."]
    if repeats:
        if c.get("example"):
            parts.append(f"📖 **Ví dụ minh họa (dữ kiện khác bài của bạn):** {c['example']}.")
        else:
            parts.append(f"📖 **Nhắc lại ngắn:** {c['name']}.")
        parts.append("❓ **Câu hỏi mới:** Nếu phải giải thích cho một bạn khác, với đầu vào nhỏ nhất đề cho phép, từng bước chương trình của bạn làm gì, theo thứ tự nào?")
        step = ("viết ra giấy bảng giá trị của các biến sau mỗi bước cho đầu vào nhỏ nhất, rồi so với kết quả chương trình in ra "
                "khi bấm Chạy thử.")
    else:
        if ev.get("objective"):
            parts.append(f"📚 **Mục tiêu của bài (theo đề của giảng viên):** {ev['objective']}")
        parts.append(f"📖 **Khái niệm cần xem lại — {c['name']}:** {c['explain']}")
        parts.append(f"❓ **Câu hỏi để tự kiểm:** {c['question']}")
        step = c["probe"][:1].lower() + c["probe"][1:]
    parts.append(next_step_line(step, adaptive_strategy))
    return "\n\n".join(parts) + extra


# ----------------------------------------------------------------------------------------------
# Mức 2
# ----------------------------------------------------------------------------------------------
def _level2_question(ev: dict) -> str:
    sus, failure, kind = ev["suspect"], ev["failure"] or {}, ev["kind"]
    inp = he.inline_value(failure.get("input", ""))
    if kind == "syntax":
        return "Phần đầu của câu lệnh ở dòng này đã có đủ các thành phần mà quy tắc cú pháp yêu cầu chưa?"
    if kind == "runtime":
        etype = he.error_type(failure.get("error_message", ""))
        return he._RUNTIME_CONCEPTS.get(etype, (None, None, "Ở dòng này, những giá trị nào đang được dùng, và thông báo lỗi nói điều gì sai về chúng?"))[2]
    if kind == "timeout":
        return ev["concept"]["question"]
    basis = sus.basis if sus else ""
    if basis == "block_not_run":
        if "for " in sus.text or "while " in sus.text:
            return f"Với đầu vào `{inp}`, vòng lặp ở dòng này duyệt qua những giá trị nào, và thân vòng lặp chạy mấy lần?"
        return f"Với đầu vào `{inp}`, điều kiện ở dòng này đúng hay sai, và phần thân của nó có được chạy không?"
    if basis == "print_repeated":
        return f"Với đầu vào `{inp}`, lệnh in này chạy mấy lần, còn đề bài yêu cầu in mấy lần và trên mấy dòng?"
    if basis == "echo_output":
        return "Giữa lúc đọc dữ liệu và lúc in ra, chương trình đã thực hiện bước biến đổi nào mà đề yêu cầu?"
    if basis == "no_input":
        return "Dữ liệu mà đề bài đưa vào chương trình ở mỗi lần chạy đi vào chương trình bằng cách nào?"
    if basis == "output_variable":
        exp = he.inline_value(failure.get("expected_output", ""))
        return (f"Với đầu vào `{inp}`, giá trị của `{sus.variable}` sau mỗi lần dòng này chạy là gì, "
                f"và chuỗi giá trị đó có dẫn tới kỳ vọng `{exp}` không?")
    return "Với một đầu vào nhỏ, bạn tự tính tay ra kết quả nào và chương trình in ra kết quả nào?"


def _level2(ev: dict, adaptive_strategy: Optional[dict], repeats: int, extra: str) -> str:
    kind, failure, sus = ev["kind"], ev["failure"], ev["suspect"]
    parts = [LEVEL_HEAD[2] + ("\n\n↻ Bạn đã xin gợi ý Mức 2 cho bài này trước đó; lần này gợi ý bám vào một bằng chứng chạy cụ thể hơn." if repeats else ""),
             ev["progress"]]
    if sus:
        parts.append(f"📍 **Dòng cần xem (dòng {sus.lineno}):** `{sus.text}`\n*Cơ sở quan sát:* {sus.note}. "
                     "Đây là nơi đáng quan sát, chưa phải kết luận rằng dòng này sai.")
    if failure:
        idx = failure.get("test_idx", "?")
        inp = he.inline_value(failure.get("input", ""))
        if kind == "syntax":
            err = ev.get("syntax_error") or {}
            msg = err.get("message", "Lỗi cú pháp") if isinstance(err, dict) else str(err)
            line = err.get("lineno", "?") if isinstance(err, dict) else "?"
            parts.append(f"🔎 **Bằng chứng:**\n- **Thông báo của trình phân tích cú pháp:** `{msg}`\n- **Vị trí:** dòng **{line}**")
        elif kind == "runtime":
            parts.append(f"🔎 **Bằng chứng từ kiểm thử #{idx}:**\n- **Đầu vào:** `{inp}`\n"
                         f"- **Lỗi khi chạy:** `{he.inline_value(failure.get('error_message', ''))}`")
        elif kind == "timeout":
            parts.append(f"🔎 **Bằng chứng từ kiểm thử #{idx}:**\n- **Đầu vào:** `{inp}`\n"
                         "- **Kết quả:** chương trình **không dừng trong 5 giây** (quá thời gian cho phép)")
        else:
            exp = he.inline_value(failure.get("expected_output", ""))
            act = (failure.get("actual_output") or "").strip()
            actual = f"`{he.inline_value(act)}`" if act else "(không in ra gì)"
            parts.append(f"🔎 **Bằng chứng từ kiểm thử #{idx}:**\n- **Đầu vào:** `{inp}`\n- **Kỳ vọng:** `{exp}`\n- **Thực tế:** {actual}\n"
                         f"- **Quan sát:** {he.observed_difference(failure.get('expected_output', ''), act)}.")
    else:
        parts.append("🔎 **Bằng chứng:** kết quả chấm chưa cho biết kiểm thử cụ thể nào lỗi, nên chưa thể khoanh vùng dòng lệnh.")
    trace_note = ev.get("trace_note")
    if trace_note:
        parts.append(f"🧵 **Vết chạy:** {trace_note}")
    parts.append(f"❓ **Câu hỏi khoanh vùng:** {_level2_question(ev)}")
    step = {
        "syntax": f"đọc dòng {sus.lineno if sus else '?'} và dòng ngay phía trên, đối chiếu với thông báo của trình phân tích, rồi bấm Chạy thử lại.",
        "runtime": "dùng **Chạy từng bước** với đúng đầu vào trên, tìm giá trị mà dòng đó đang dùng khi lỗi xảy ra và tự giải thích vì sao thông báo lỗi xuất hiện.",
        "timeout": "dùng **Chạy từng bước** với đúng đầu vào trên và ghi lại giá trị của các biến điều khiển vòng lặp qua ba lần lặp đầu.",
    }.get(kind, "dùng **Chạy từng bước** với đúng đầu vào này và dừng ở dòng đầu tiên mà giá trị biến khác với điều bạn dự tính.")
    parts.append(next_step_line(step, adaptive_strategy))
    footer = "*(Gợi ý tự động khi không có mô hình AI: chỉ nêu điều quan sát được, chưa chỉ ra cách sửa.)*"
    return "\n\n".join(parts) + extra + "\n\n" + footer


# ----------------------------------------------------------------------------------------------
# Mức 3
# ----------------------------------------------------------------------------------------------
def _skeleton(code: str, starter: str) -> str:
    """Khung mã từ mã người học (hoặc khung mẫu của bài): giữ giàn giáo, che logic, thêm chỗ trống cho phần còn thiếu.

    Chú thích của người học bị bỏ (dữ liệu không tin cậy, có thể chứa lệnh chèn) và không bao giờ được chép lại vào gợi ý.
    """
    def clean(src: str) -> list[str]:
        lines = []
        for raw in (src or "").splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            quote, cut = "", None
            for i, ch in enumerate(raw):
                if quote:
                    quote = "" if ch == quote else quote
                elif ch in "\"'":
                    quote = ch
                elif ch == "#":
                    cut = i
                    break
            lines.append((raw[:cut] if cut is not None else raw).rstrip())
        return lines[:40]

    from backend.adaptive_policy import is_blank_attempt

    def masked_lines(src_lines: list[str]) -> list[str]:
        text = "\n".join(src_lines)
        if not text:
            return []
        masked_text, _ = enforce_level3_skeleton("```python\n" + text + "\n```")
        body = re.search(r"```python\n(.*?)\n?```", masked_text, flags=re.DOTALL)
        return body.group(1).splitlines() if body and body.group(1).strip() else []

    def parses(lines_: list[str]) -> bool:
        try:
            ast.parse("\n".join(lines_))
            return True
        except SyntaxError:
            return False

    lines = masked_lines(clean(code) if not is_blank_attempt(code, starter) else clean(starter))
    if lines and not parses(lines):
        # mã người học có lỗi cú pháp (hoặc thụt lề lệch) nên khung che xong vẫn không chạy được: dùng khung mẫu của bài
        lines = masked_lines(clean(starter))
        if lines and not parses(lines):
            lines = []
    joined = "\n".join(lines)
    has_input = "input(" in joined
    has_flow = any(re.match(r"\s*(if|for|while)\b", ln) for ln in lines)
    has_print = any(re.match(r"\s*print\(", ln) for ln in lines)
    if not has_input:
        lines.insert(0, "du_lieu = ...  # TODO (Bước 1): đọc và ép kiểu đầu vào")
    if not any("TODO" in ln for ln in lines) and not has_flow:
        lines.append("...  # TODO (Bước 3): phần xử lý chính theo dàn ý")
    elif not has_flow:
        idx = next((i for i in range(len(lines) - 1, -1, -1) if re.match(r"\s*print\(", lines[i])), len(lines))
        lines.insert(idx, "...  # TODO (Bước 3): phần xử lý chính theo dàn ý")
    if not has_print:
        lines.append("print(...)  # TODO (Bước 4): in kết quả")
    if not any("TODO" in ln for ln in lines):
        lines.append("...  # TODO: phần còn lại tự viết theo dàn ý")
    return "\n".join(lines)


def _level3(ev: dict, exercise: dict, code: str, adaptive_strategy: Optional[dict], repeats: int, extra: str) -> str:
    failure = ev["failure"]
    steps = he.build_outline(exercise, ev.get("ast"))
    goal = he.exercise_goal(exercise)
    parts = [LEVEL_HEAD[3] + ("\n\n↻ Bạn đã xin gợi ý Mức 3 cho bài này trước đó; lần này khung bám sát phần bạn đã viết." if repeats else ""),
             ev["progress"]]
    if failure and failure.get("status") == "FAIL":
        parts.append(f"🔎 **Dùng để tự kiểm:** với đầu vào `{he.inline_value(failure.get('input', ''))}` "
                     f"chương trình cần in `{he.inline_value(failure.get('expected_output', ''))}`.")
    outline = "\n".join(f"- **Bước {i}:** {s}" for i, s in enumerate(steps, 1))
    skeleton = _skeleton(code, exercise.get("starter_code", "") or "")
    first_test = next((r for r in ev.get("all_results", []) if (r.get("input") or "").strip()), None)
    sample_input = (failure or first_test or {}).get("input", "")
    table = he.trace_table(code, sample_input, exercise.get("starter_code", "") or "")
    parts.append(f"### 1. Dàn ý các bước theo đề «{goal}»:\n{outline}")
    parts.append("### 2. Khung mã nguồn bám bài làm của bạn (các chỗ `...` hoặc `# TODO` là phần logic bạn tự viết):\n"
                 f"```python\n{skeleton}\n```")
    parts.append(f"### 3. Bảng chạy tay (để trống, bạn tự điền):\n{table}")
    parts.append(level3_progress_note(code, adaptive_strategy))
    return "\n\n".join(parts) + extra


def trace_note(code: str, trace: Optional[dict]) -> str:
    """Một câu từ vết chạy: giá trị các biến của người học ngay trước lệnh cuối cùng được chạy với đầu vào lỗi."""
    locals_ = (trace or {}).get("final_locals") or {}
    if not locals_:
        return ""
    names = [n for n in CodeFacts(code).assigned_names if n in locals_ and not n.startswith("_")][:3]
    if not names:
        return ""
    parts = ", ".join(f"`{n}` có giá trị `{str(locals_[n]).replace(chr(96), chr(39))}`" for n in names)
    inp = he.inline_value((trace or {}).get("input", ""))
    return f"với đầu vào `{inp}`, ngay trước lệnh cuối cùng được chạy, {parts}."


# ----------------------------------------------------------------------------------------------
# Điểm vào
# ----------------------------------------------------------------------------------------------
def _objective(exercise: Optional[dict]) -> str:
    """Mục tiêu học tập đầu tiên mà giảng viên nêu trong đề (rút gọn); rỗng nếu đề không có."""
    objectives = exercise_brief.parse_description((exercise or {}).get("description"))["objectives"]
    if not objectives:
        return ""
    text = exercise_brief.safe_objective(objectives[0])
    return text if len(text) <= 120 else text[:120].rsplit(" ", 1)[0].rstrip(",;: ") + "…"


def build_offline_hint(exercise: dict, code: str, test_results: dict, ast_analysis: Optional[dict], hint_level: int,
                       adaptive_strategy: Optional[dict] = None, attempt_history: Optional[list] = None,
                       trace: Optional[dict] = None) -> str:
    """Gợi ý theo luật cho bài CHƯA đạt hết kiểm thử (đã loại trừ nhánh đạt và nhánh chưa viết code ở llm_service)."""
    ast_analysis = ast_analysis or {}
    title = (exercise or {}).get("title", "Bài tập")
    no_code = bool(adaptation(adaptive_strategy, "no_code_yet"))
    failure = None if no_code else he.pick_failure(test_results)
    kind = None if no_code else classify(failure, ast_analysis, test_results)
    suspect = he.suspect_line(code, failure, kind, ast_analysis, trace) if kind else None
    goal = he.exercise_goal(exercise)
    concept = he.concept_for(kind or "wrong_output", failure, suspect, goal, has_loops=bool(ast_analysis.get("has_loops", True)))
    ev = {"kind": kind, "failure": failure, "suspect": suspect, "concept": concept, "ast": ast_analysis,
          "syntax_error": ast_analysis.get("syntax_error"),
          "progress": (f"🎯 **Đang ở đâu:** bài **{title}**, bạn chưa viết dòng code nào; đây là khung để bắt đầu." if no_code
                       else _progress_line(title, test_results, kind)),
          "objective": _objective(exercise),
          "trace_note": trace_note(code, trace), "all_results": (test_results or {}).get("results", [])}
    repeats = repeat_count(attempt_history, hint_level)

    extra = ""
    strategy = (adaptive_strategy or {}).get("strategy", "")
    concept_rec = adaptation(adaptive_strategy, "concept_recurring_difficulty")
    if concept_rec:
        ctx = concept_rec.get("context", {})
        extra += (f"\n\n🔁 Nhóm kiến thức **{ctx.get('kc_label', '')}** từng gây vướng ở bài **{ctx.get('exercise_title', '')}**. "
                  "Lần này hãy dùng **Chạy từng bước** với đúng đầu vào của kiểm thử chưa đạt và ghi lại giá trị biến ở từng dòng.")
    elif strategy == "recurring_difficulty" and not repeats:
        if hint_level == 2:  # bước kế tiếp của Mức 2 đã nói tới Chạy từng bước nên chỉ nhắc ngắn
            extra += "\n\n🔁 Bạn đã thử bài này vài lần: lần này hãy ghi lại giá trị biến ở từng dòng thay vì sửa tiếp theo cảm tính."
        else:
            extra += ("\n\n🔁 Bạn đã thử bài này vài lần. Thay vì sửa tiếp theo cảm tính, lần này hãy dùng "
                      "**Chạy từng bước** với đúng đầu vào của kiểm thử chưa đạt và ghi lại giá trị biến ở từng dòng.")
    notes = model_notes(adaptive_strategy)
    if notes:
        extra += "\n\n" + notes

    if hint_level == 1:
        return _level1(ev, adaptive_strategy, repeats, extra)
    if hint_level == 2:
        return _level2(ev, adaptive_strategy, repeats, extra)
    return _level3(ev, exercise or {}, code, adaptive_strategy, repeats, extra)
