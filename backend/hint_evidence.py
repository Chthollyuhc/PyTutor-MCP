"""Bằng chứng tất định cho gợi ý 3 mức (v5.10). Hàm thuần: không gọi mô hình, không DB, không import `mcp_server`.

Từ kết quả chấm (test_results), phân tích AST, mã người học và (tùy chọn) vết chạy, module này rút ra:
  - test lỗi NÊN dùng làm bằng chứng (đầu vào nhỏ, dễ chạy tay, thay vì mặc định test đầu tiên);
  - MỘT dòng mã đáng xem (từ thông báo cú pháp, traceback, vết chạy hoặc cấu trúc AST) kèm cơ sở quan sát được;
  - nhóm khái niệm gắn với dạng lỗi, câu giải thích ngắn bằng lời và một phép thử người học tự làm;
  - dàn ý 4 bước theo ĐỀ BÀI, bảng chạy tay để trống theo biến trong mã người học.

Giới hạn trung thực: "dòng đáng xem" là điều quan sát được (dòng nơi lỗi được báo, dòng mà thân khối không chạy lần nào
với đầu vào lỗi, dòng cuối cùng cập nhật biến được in ra...), KHÔNG phải kết luận đây là dòng sai. Không nêu cách sửa.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Optional

_TB_LINE = re.compile(r'File "<string>", line (\d+)')


# ----------------------------------------------------------------------------------------------
# Chọn test lỗi và mô tả khác biệt
# ----------------------------------------------------------------------------------------------
def failures(test_results: Optional[dict]) -> list[dict]:
    return [r for r in (test_results or {}).get("results", []) if r.get("status") not in ("PASS", "SKIPPED")]


def pick_failure(test_results: Optional[dict]) -> Optional[dict]:
    """Test lỗi giàu thông tin nhất: ưu tiên đầu vào ngắn (dễ chạy tay) và tránh TIMEOUT khi còn lựa chọn khác."""
    fails = failures(test_results)
    if not fails:
        return None
    return min(fails, key=lambda r: (r.get("status") == "TIMEOUT", len((r.get("input") or "").strip()), r.get("test_idx", 0)))


def observed_difference(expected: str, actual: str) -> str:
    """Khác biệt QUAN SÁT ĐƯỢC giữa đầu ra kỳ vọng và thực tế; không suy đoán nguyên nhân."""
    exp, act = (expected or "").strip(), (actual or "").strip()
    if not act:
        return "chương trình không in ra gì cho đầu vào này"
    if exp.lower() == act.lower():
        return "nội dung trùng nhau nhưng khác chữ hoa/chữ thường"
    if "".join(exp.split()) == "".join(act.split()):
        return "nội dung trùng nhau nhưng khác khoảng trắng hoặc xuống dòng"
    try:
        diff = float(act) - float(exp)
        return f"kết quả là số và lệch {diff:+g} so với kỳ vọng"
    except ValueError:
        pass
    if len(act.splitlines()) != len(exp.splitlines()):
        return f"số dòng in ra khác nhau ({len(act.splitlines())} so với {len(exp.splitlines())} dòng kỳ vọng)"
    return "nội dung in ra khác với kỳ vọng"


def inline_value(value: str) -> str:
    """Giá trị đưa vào `backtick`: gộp nhiều dòng bằng ' ⏎ ', bỏ backtick bên trong."""
    text = " ⏎ ".join(part.strip() for part in (value or "").strip().splitlines()) or "(rỗng)"
    return text.replace("`", "'")


def traceback_line(stderr: str) -> Optional[int]:
    """Số dòng (trong mã người học) ở khung cuối cùng của traceback; None nếu không có."""
    hits = _TB_LINE.findall(stderr or "")
    return int(hits[-1]) if hits else None


def error_type(error_message: str) -> str:
    head = (error_message or "").split(":")[0].strip()
    return head if re.fullmatch(r"[A-Za-z]+(Error|Exception|Exit)", head) else ""


# ----------------------------------------------------------------------------------------------
# Phân tích tĩnh mã người học
# ----------------------------------------------------------------------------------------------
def strip_comment(line: str) -> str:
    """Bỏ chú thích `# ...` cuối dòng, tôn trọng dấu nháy."""
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


@dataclass
class _Block:
    kind: str                    # "for" | "while" | "if"
    lineno: int
    body_lines: set[int]
    test_names: set[str] = field(default_factory=set)
    assigned_in_body: set[str] = field(default_factory=set)


class CodeFacts:
    """Sự kiện cấu trúc rút từ AST: khối lệnh, nơi gán biến, lệnh print. Mã không phân tích được thì mọi danh sách rỗng."""

    def __init__(self, code: str):
        self.lines = (code or "").splitlines()
        self.blocks: list[_Block] = []
        self.assigns: dict[str, list[tuple[int, int]]] = {}   # tên → [(dòng, độ sâu lồng)]
        self.prints: list[tuple[int, int, bool, list[str]]] = []  # (dòng, độ sâu, trong vòng lặp, tên biến in)
        self.assigned_names: list[str] = []
        self.valid = True
        self.reads_input = False
        try:
            tree = ast.parse(code or "")
        except SyntaxError:
            self.valid = False
            return
        self.reads_input = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "input" for n in ast.walk(tree))
        self._walk(tree.body, 0, False)

    def text(self, lineno: int) -> str:
        """Dòng mã đã bỏ chú thích: chú thích của người học là dữ liệu không tin cậy, không bao giờ được chép lại vào gợi ý."""
        return strip_comment(self.lines[lineno - 1]).strip() if 1 <= lineno <= len(self.lines) else ""

    @staticmethod
    def _names(node: ast.AST) -> set[str]:
        return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

    def _assigned(self, stmts: list[ast.stmt]) -> set[str]:
        out: set[str] = set()
        for stmt in stmts:
            for n in ast.walk(stmt):
                if isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                    targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                    for t in targets:
                        out |= {x.id for x in ast.walk(t) if isinstance(x, ast.Name)}
        return out

    def _walk(self, stmts: list[ast.stmt], depth: int, in_loop: bool) -> None:
        for stmt in stmts:
            if isinstance(stmt, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                for t in targets:
                    for x in ast.walk(t):
                        if isinstance(x, ast.Name):
                            self.assigns.setdefault(x.id, []).append((stmt.lineno, depth))
                            if x.id not in self.assigned_names:
                                self.assigned_names.append(x.id)
            if isinstance(stmt, ast.For):
                for x in ast.walk(stmt.target):
                    if isinstance(x, ast.Name):
                        self.assigns.setdefault(x.id, []).append((stmt.lineno, depth))
                        if x.id not in self.assigned_names:
                            self.assigned_names.append(x.id)
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name) \
                    and stmt.value.func.id == "print":
                names = [n.id for a in stmt.value.args for n in ast.walk(a) if isinstance(n, ast.Name)]
                self.prints.append((stmt.lineno, depth, in_loop, names))
            if isinstance(stmt, (ast.For, ast.While, ast.If)):
                kind = "for" if isinstance(stmt, ast.For) else "while" if isinstance(stmt, ast.While) else "if"
                body_nodes = list(stmt.body) + list(getattr(stmt, "orelse", []))
                body_lines = {n.lineno for b in body_nodes for n in ast.walk(b) if hasattr(n, "lineno")}
                test = stmt.test if kind != "for" else stmt.iter
                self.blocks.append(_Block(kind, stmt.lineno, {ln for ln in body_lines if ln != stmt.lineno},
                                          self._names(test), self._assigned(stmt.body)))
                loop = in_loop or kind != "if"
                self._walk(list(stmt.body), depth + 1, loop)
                self._walk(list(getattr(stmt, "orelse", [])), depth + 1, loop)
            elif isinstance(stmt, (ast.FunctionDef, ast.With, ast.Try)):
                inner = list(getattr(stmt, "body", [])) + list(getattr(stmt, "orelse", [])) + list(getattr(stmt, "finalbody", []))
                self._walk(inner, depth + 1, in_loop)


@dataclass
class Suspect:
    lineno: int
    text: str
    basis: str            # mã cơ sở: syntax_error | traceback | loop_control | block_not_run | print_repeated | echo_output | output_variable | print_line
    note: str             # câu quan sát được, không kết luận "dòng này sai"
    variable: str = ""


def suspect_line(code: str, failure: Optional[dict], expect_kind: str, ast_analysis: Optional[dict],
                 trace: Optional[dict] = None) -> Optional[Suspect]:
    """Chọn MỘT dòng đáng xem. `expect_kind`: syntax | runtime | timeout | wrong_output. Trả None nếu không đủ căn cứ."""
    facts = CodeFacts(code)
    ast_analysis = ast_analysis or {}
    failure = failure or {}

    if expect_kind == "syntax":
        err = ast_analysis.get("syntax_error") or {}
        ln = err.get("lineno") if isinstance(err, dict) else None
        if isinstance(ln, int) and 1 <= ln <= max(1, len(facts.lines)) and facts.text(ln):
            return Suspect(ln, facts.text(ln), "syntax_error", f"trình phân tích cú pháp dừng lại ở dòng {ln}")
        return None
    if expect_kind == "runtime":
        ln = traceback_line(failure.get("stderr", ""))
        if ln and facts.text(ln):
            return Suspect(ln, facts.text(ln), "traceback", f"thông báo lỗi chỉ tới dòng {ln}")
        return None
    if not facts.valid:
        return None
    if expect_kind == "timeout":
        whiles = [b for b in facts.blocks if b.kind == "while"]
        # Ưu tiên vòng while mà thân KHÔNG gán lại biến nào trong điều kiện; chỉ khi không có mới xét vòng còn lại.
        for b in sorted(whiles, key=lambda x: bool(x.test_names & x.assigned_in_body)):
            if b.test_names:
                names = ", ".join(f"`{n}`" for n in sorted(b.test_names))
                kept = ", ".join(f"`{n}`" for n in sorted(b.test_names & b.assigned_in_body)) or ""
                note = f"điều kiện của vòng lặp `while` phụ thuộc vào {names}"
                if not (b.test_names & b.assigned_in_body):
                    note += "; trong thân vòng lặp không có lệnh nào gán lại các biến này"
                elif kept:
                    note += f"; thân vòng lặp có gán lại {kept}"
                return Suspect(b.lineno, facts.text(b.lineno), "loop_control", note)
        loop = next((b for b in facts.blocks if b.kind in ("while", "for")), None)
        return Suspect(loop.lineno, facts.text(loop.lineno), "loop_control", "đây là dòng điều khiển vòng lặp") if loop else None

    # wrong_output
    if not facts.reads_input and (failure.get("input") or "").strip() and facts.lines:
        first = next((i for i, ln in enumerate(facts.lines, 1) if facts.text(i)), None)
        if first:
            return Suspect(first, facts.text(first), "no_input",
                           "chương trình không có lệnh `input()` nào để đọc dữ liệu, trong khi kiểm thử cung cấp đầu vào; "
                           "đây là dòng lệnh đầu tiên của chương trình")
    counts: dict[int, int] = {}
    for k, v in ((trace or {}).get("line_counts") or {}).items():  # vết hỏng/không đúng dạng thì bỏ qua từng mục
        try:
            counts[int(k)] = int(v)
        except (TypeError, ValueError):
            continue
    if counts:
        for b in sorted(facts.blocks, key=lambda x: x.lineno):
            if counts.get(b.lineno, 0) > 0 and b.body_lines and all(counts.get(ln, 0) == 0 for ln in b.body_lines):
                what = "vòng lặp" if b.kind in ("for", "while") else "điều kiện"
                return Suspect(b.lineno, facts.text(b.lineno), "block_not_run",
                               f"với đầu vào này, các lệnh bên trong khối của {what} ở dòng {b.lineno} không được chạy lần nào")
    exp_lines = len((failure.get("expected_output") or "").strip().splitlines())
    act = (failure.get("actual_output") or "").strip()
    act_lines = len(act.splitlines()) if act else 0
    last_print = facts.prints[-1] if facts.prints else None
    if act_lines > exp_lines >= 1 and facts.prints:
        loop_prints = [p for p in facts.prints if p[2]]
        p = loop_prints[0] if loop_prints else last_print
        return Suspect(p[0], facts.text(p[0]), "print_repeated",
                       f"chương trình in {act_lines} dòng trong khi kỳ vọng {exp_lines} dòng; lệnh in ở dòng {p[0]} nằm trong khối được lặp"
                       if p[2] else f"chương trình in {act_lines} dòng trong khi kỳ vọng {exp_lines} dòng")
    inp = " ".join((failure.get("input") or "").split())
    printed_has_compute = bool(last_print) and any(
        any("input(" not in facts.text(w[0]) for w in facts.assigns.get(name, [])) for name in last_print[3])
    if act and inp and " ".join(act.split()) == inp and last_print and not printed_has_compute:
        return Suspect(last_print[0], facts.text(last_print[0]), "echo_output",
                       "kết quả in ra y hệt dữ liệu đã đọc vào, nghĩa là chưa có bước biến đổi nào trước lệnh in này")
    if last_print:
        for name in last_print[3]:
            where = facts.assigns.get(name)
            if where and len(where) >= 1:
                real = [w for w in where if facts.text(w[0]) and "input(" not in facts.text(w[0])]
                if real:
                    ln = sorted(real, key=lambda w: (-w[1], -w[0]))[0][0]
                    return Suspect(ln, facts.text(ln), "output_variable",
                                   f"đây là dòng cập nhật `{name}` ở mức lồng sâu nhất, biến được in ra ở cuối chương trình", name)
        return Suspect(last_print[0], facts.text(last_print[0]), "print_line", "đây là lệnh quyết định nội dung in ra")
    return None


# ----------------------------------------------------------------------------------------------
# Khái niệm gắn với dạng lỗi (Mức 1)
# ----------------------------------------------------------------------------------------------
_RUNTIME_CONCEPTS = {
    "TypeError": ("Kiểu dữ liệu và phép toán",
                  "Mỗi giá trị trong Python có một kiểu (số nguyên, số thực, chuỗi, ...). Hàm `input()` luôn trả về chuỗi, và một phép toán chỉ dùng được giữa các kiểu tương thích.",
                  "Giá trị bạn dùng trong phép toán có kiểu gì, và phép toán đó cần kiểu nào?"),
    "ValueError": ("Chuyển đổi kiểu dữ liệu",
                   "Các hàm như `int()` hay `float()` chỉ chuyển được những chuỗi có nội dung đúng định dạng.",
                   "Chuỗi mà chương trình nhận được trông như thế nào, và nó có đúng định dạng của kiểu cần chuyển không?"),
    "NameError": ("Phạm vi và thời điểm của biến",
                  "Một tên biến chỉ dùng được sau khi đã được gán giá trị, và trong đúng phạm vi mà nó được tạo ra.",
                  "Tên biến nào được dùng, và nó đã được gán giá trị ở bước nào trước đó?"),
    "IndexError": ("Chỉ mục và độ dài của dãy",
                   "Chỉ mục của chuỗi hoặc danh sách chạy từ 0 đến độ dài trừ 1; truy cập ngoài khoảng này gây lỗi.",
                   "Dãy đang xét có bao nhiêu phần tử, và chỉ mục được dùng nằm trong khoảng nào?"),
    "ZeroDivisionError": ("Phép chia và giá trị 0",
                          "Phép chia hoặc chia lấy dư cho 0 không xác định, nên giá trị của số chia cần được xét trước.",
                          "Số chia có thể bằng 0 trong trường hợp đầu vào nào?"),
    "AttributeError": ("Phương thức thuộc về kiểu dữ liệu",
                       "Mỗi kiểu dữ liệu có bộ phương thức riêng; phương thức của danh sách không tự có trên chuỗi và ngược lại.",
                       "Giá trị này thuộc kiểu nào, và kiểu đó có những phương thức nào?"),
    "RecursionError": ("Đệ quy cần điểm dừng",
                       "Một hàm gọi lại chính nó phải có trường hợp cơ sở để dừng; nếu không, số lần gọi tăng mãi cho tới khi vượt giới hạn.",
                       "Với giá trị nhỏ nhất đề cho phép, hàm có gọi lại chính nó nữa không, và khi nào nó thôi gọi?"),
    "KeyError": ("Khóa trong từ điển",
                 "Truy cập một khóa chưa có trong từ điển gây lỗi; cần biết khóa đã được thêm vào hay chưa.",
                 "Khóa đang tra cứu đã được thêm vào từ điển ở bước nào?"),
}


def concept_for(kind: str, failure: Optional[dict], suspect: Optional[Suspect], goal: str, has_loops: bool = True) -> dict:
    """Nhóm khái niệm cho Mức 1: {name, explain, question, probe, example}. Không chỉ dòng, không nêu tham số của bài làm."""
    failure = failure or {}
    generic_probe = ("Tự chọn một đầu vào nhỏ nhất hợp lệ theo đề, tính tay kết quả mong đợi, rồi bấm Chạy thử với đúng đầu vào đó "
                     "và so hai kết quả.")
    if kind == "syntax":
        return {"name": "Cú pháp của câu lệnh khối",
                "explain": "Các câu lệnh mở một khối như `for`, `while`, `if`, `def` có quy tắc cú pháp riêng ở phần đầu câu lệnh, và phần thân của chúng phải thụt vào nhất quán.",
                "question": "Một câu lệnh `for` hoàn chỉnh gồm những thành phần nào, theo như ví dụ trong tài liệu?",
                "probe": "Bấm Chạy thử, đọc thông báo lỗi, rồi đối chiếu từng thành phần của câu lệnh được nhắc tới với một ví dụ mẫu.",
                "example": "`for x in range(3):` rồi thân vòng lặp thụt vào một mức"}
    if kind == "runtime":
        etype = error_type(failure.get("error_message", ""))
        name, explain, question = _RUNTIME_CONCEPTS.get(etype, (
            "Đọc thông báo lỗi khi chạy", "Dòng cuối của thông báo lỗi cho biết loại lỗi và lý do ngắn gọn; các dòng phía trên chỉ ra chuỗi lệnh dẫn tới lỗi.",
            "Loại lỗi trong thông báo là gì, và nó thường xảy ra khi nào?"))
        return {"name": name, "explain": explain, "question": question,
                "probe": "Bấm Chạy thử, đọc dòng cuối của thông báo lỗi và tự giải thích bằng một câu lỗi đó nói gì về giá trị đang được dùng.",
                "example": ""}
    if kind == "timeout":
        return {"name": "Điều kiện dừng của vòng lặp",
                "explain": "Vòng lặp `while` chỉ dừng khi điều kiện của nó trở thành sai; muốn vậy, thân vòng lặp phải làm điều kiện tiến dần tới sai sau mỗi lần chạy.",
                "question": "Điều kiện của vòng lặp phụ thuộc vào những giá trị nào, và sau mỗi lần lặp thì các giá trị đó thay đổi ra sao?",
                "probe": "Viết ra giấy giá trị của các biến điều khiển qua ba lần lặp đầu rồi xem điều kiện có tiến tới sai không.",
                "example": "`while k < 3:` chỉ dừng nếu `k` tăng sau mỗi lần lặp"}
    basis = suspect.basis if suspect else ""
    if basis == "no_input":
        return {"name": "Đọc dữ liệu đầu vào",
                "explain": "Mỗi lần chấm, dữ liệu được đưa vào chương trình qua `input()`; một chương trình không đọc dữ liệu thì cho cùng một kết quả với mọi đầu vào.",
                "question": "Dữ liệu mà đề bài đưa vào chương trình ở mỗi lần chạy đi vào bằng cách nào?",
                "probe": generic_probe, "example": "`x = input()` đọc một dòng thành chuỗi"}
    if basis == "block_not_run":
        header = (suspect.text if suspect else "")
        if "range(" in header:
            return {"name": "Số lần lặp và dãy `range`",
                    "explain": "`range(a, b)` sinh các số từ `a` và dừng TRƯỚC `b`; số lần thân vòng lặp chạy phụ thuộc vào dãy mà vòng lặp duyệt, và với đầu vào nhỏ ở biên của đề, dãy này có thể rỗng.",
                    "question": "Với đầu vào nhỏ nhất của đề, vòng lặp duyệt qua những giá trị nào, và thân vòng lặp chạy mấy lần?",
                    "probe": generic_probe, "example": "`list(range(1, 4))` cho `[1, 2, 3]`"}
        return {"name": "Điều kiện rẽ nhánh và trường hợp biên",
                "explain": "Phần thân của `if` chỉ chạy khi điều kiện đúng, và điều kiện cần đúng với mọi dạng dữ liệu hợp lệ của đề (giá trị biên, chữ hoa và chữ thường, số âm, chuỗi rỗng, ...).",
                "question": "Có dạng dữ liệu hợp lệ nào của đề mà điều kiện của bạn không bao phủ?",
                "probe": generic_probe, "example": "`'A' == 'a'` cho `False`"}
    if basis == "print_repeated":
        return {"name": "Vị trí của lệnh in và thụt lề",
                "explain": "Lệnh nằm trong khối thụt lề của vòng lặp chạy ở mỗi lần lặp, và mỗi lệnh `print` mặc định kết thúc bằng một lần xuống dòng; vị trí đặt lệnh in quyết định kết quả hiện ra bao nhiêu lần, trên mấy dòng.",
                "question": "Đề yêu cầu in kết quả mấy lần và trên mấy dòng, còn chương trình thì in ở những thời điểm nào?",
                "probe": generic_probe, "example": "`print('a')` rồi `print('b')` cho hai dòng"}
    if basis == "echo_output":
        return {"name": "Biến đổi dữ liệu trước khi in",
                "explain": f"Đề yêu cầu «{goal}» nên kết quả in ra phải khác dữ liệu đã đọc vào theo một quy tắc nào đó; in thẳng dữ liệu đọc vào nghĩa là chưa có bước biến đổi.",
                "question": "Quy tắc biến đổi mà đề yêu cầu là gì, nói bằng lời với một ví dụ nhỏ?",
                "probe": generic_probe, "example": ""}
    if has_loops:
        return {"name": "Biến tích lũy và phép cập nhật",
                "explain": "Biến kết quả được cập nhật qua từng lần lặp; phép cập nhật phải phản ánh đúng quan hệ giữa kết quả hiện tại và phần tử đang xét, và giá trị ban đầu phải phù hợp với phép toán.",
                "question": "Sau mỗi lần lặp, kết quả mới liên hệ với kết quả cũ và phần tử đang xét như thế nào theo đề bài?",
                "probe": generic_probe, "example": "tính tay ba lần lặp đầu rồi viết giá trị của biến kết quả sau từng lần"}
    return {"name": "Rẽ nhánh và trường hợp biên",
            "explain": "Chương trình cần đúng với mọi đầu vào hợp lệ của đề, kể cả các trường hợp biên và trường hợp đặc biệt mà định nghĩa trong đề nhắc tới.",
            "question": "Có đầu vào hợp lệ nào, nhỏ nhất hoặc đặc biệt, mà chương trình của bạn xử lý khác với điều đề bài mô tả?",
            "probe": generic_probe, "example": ""}


# ----------------------------------------------------------------------------------------------
# Dàn ý theo đề, bảng chạy tay
# ----------------------------------------------------------------------------------------------
def exercise_goal(exercise: dict) -> str:
    """Tiêu đề bài bỏ tiền tố 'Bài NN:'; dùng làm tên mục tiêu trong dàn ý."""
    title = (exercise or {}).get("title", "") or "bài tập"
    return re.sub(r"^\s*B[àa]i\s*\d+\s*[:.\-–]\s*", "", title).strip() or title


def _section_bullets(description: str, heading_words: tuple[str, ...]) -> str:
    """Gạch đầu dòng đầu tiên dưới mục có tiêu đề chứa một trong heading_words (Đầu vào/Đầu ra)."""
    lines = (description or "").splitlines()
    for i, raw in enumerate(lines):
        if raw.strip().startswith("#") and any(w in raw.lower() for w in heading_words):
            for nxt in lines[i + 1:]:
                s = nxt.strip()
                if s.startswith("#"):
                    break
                if s.startswith(("-", "*")):
                    return re.sub(r"[`$]", "", s.lstrip("-* ").strip())
    return ""


def build_outline(exercise: dict, ast_analysis: Optional[dict] = None) -> list[str]:
    """Dàn ý 4 bước sinh theo ĐỀ BÀI (tiêu đề + mục Đầu vào/Đầu ra); chỉ mô tả việc cần làm, không có biểu thức lời giải."""
    goal = exercise_goal(exercise)
    desc = (exercise or {}).get("description", "") or ""
    cat = ((exercise or {}).get("category", "") or "").lower()
    inp = _section_bullets(desc, ("đầu vào", "input"))
    out = _section_bullets(desc, ("đầu ra", "output"))
    step1 = "Đọc dữ liệu đầu vào" + (f" theo mô tả của đề: {inp}" if inp else " theo định dạng đề nêu") + "; chọn kiểu dữ liệu phù hợp với điều đề yêu cầu."
    step2 = f"Chuẩn bị nơi lưu kết quả của «{goal}»: quyết định biến nào giữ kết quả và nó bắt đầu từ giá trị nào."
    if "chuỗi" in cat or "string" in cat:
        how = "duyệt hoặc cắt lát chuỗi theo yêu cầu của đề"
    elif "rẽ nhánh" in cat or "điều kiện" in cat:
        how = "xét các trường hợp bằng rẽ nhánh (và lặp nếu cần) theo định nghĩa trong đề"
    elif "đệ quy" in cat and "vòng lặp" not in cat:
        how = "xác định trường hợp cơ sở và cách quy bài toán về bài toán nhỏ hơn"
    else:
        how = "xác định đối tượng cần duyệt hoặc điều kiện cần xét, rồi cập nhật kết quả cho từng phần tử"
    step3 = f"Xử lý chính của «{goal}»: {how}; ghi vào chú thích bạn định dùng cấu trúc nào."
    step4 = "In kết quả" + (f" theo mô tả của đề: {out}" if out else " đúng định dạng đề yêu cầu") + " bằng `print()`."
    return [step1, step2, step3, step4]


def trace_table(code: str, sample_input: str, starter: str = "") -> str:
    """Bảng chạy tay để trống: cột là biến trong mã người học (hoặc khung mẫu), hàng là các bước; người học tự điền."""
    facts = CodeFacts(code)
    names = [n for n in facts.assigned_names if len(n) <= 20][:4]
    if not names:
        names = [n for n in CodeFacts(starter).assigned_names if len(n) <= 20][:4]
    if not names:
        names = ["biến 1", "biến 2"]
    header = "| Bước | " + " | ".join(f"`{n}`" if n.isidentifier() else n for n in names) + " | Đã in |"
    sep = "|---|" + "---|" * (len(names) + 1)
    rows = [f"| {label} | " + " | ".join(" " for _ in names) + " |   |" for label in ("Sau khi đọc dữ liệu", "Sau lần lặp/bước 1", "Sau lần lặp/bước 2", "Kết quả cuối")]
    return (f"Chạy tay với đầu vào `{inline_value(sample_input)}`: tự điền từng ô theo thứ tự chương trình thực hiện, rồi so với kết quả kiểm thử.\n\n"
            + "\n".join([header, sep] + rows))


# ----------------------------------------------------------------------------------------------
# Chống chép lại chú thích của người học (dữ liệu không tin cậy, có thể chứa lệnh chèn)
# ----------------------------------------------------------------------------------------------
def _word_ngrams(text: str, n: int = 4) -> set:
    toks = re.findall(r"\w+", (text or "").lower())
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def student_comment_texts(code: str, starter: str = "") -> list[str]:
    """Chú thích `# ...` và chuỗi nhiều dòng của người học, trừ những gì đã có sẵn trong khung mẫu của bài."""
    def extract(src: str) -> list[str]:
        out = []
        for raw in (src or "").splitlines():
            tail = raw[len(strip_comment(raw)):].lstrip("# ").strip()
            if tail:
                out.append(tail)
        out += [m.strip() for m in re.findall(r'(?ms)^[ \t]*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')[ \t]*$', src or "") if m.strip()]  # chỉ chuỗi đứng riêng một câu lệnh
        return out
    known = set(extract(starter))
    return [c for c in extract(code) if c not in known]


_INSTRUCTION_LIKE = re.compile(
    r"(bỏ qua|quên (?:hết|mọi)|đáp án|lời giải|in ra toàn bộ|toàn bộ (?:code|mã)|ignore|disregard|system|hệ thống cho phép|giảng viên|"
    r"cho (?:tôi|mình)|xin (?:hãy|bạn)|reveal|solution|answer|jailbreak|từng dòng|dòng cuối)", flags=re.IGNORECASE)


def echoes_student_comment(reply: str, code: str, starter: str = "", n: int = 4, only_suspicious: bool = False) -> bool:
    """True nếu phản hồi chép lại n từ liên tiếp trở lên của một chú thích do người học viết.

    `only_suspicious=True` (dùng trong sản phẩm): chỉ xét chú thích trông như chỉ dẫn/ra lệnh (từ khóa xin đáp án, bỏ qua quy tắc...)
    hoặc dài từ 10 từ trở lên, để chú thích bình thường ("# tính tổng") không làm gợi ý tốt bị thay.
    """
    grams = _word_ngrams(reply, n)
    comments = student_comment_texts(code, starter)
    if only_suspicious:
        comments = [c for c in comments if _INSTRUCTION_LIKE.search(c) or len(re.findall(r"\w+", c)) >= 10]
    return any(_word_ngrams(c, n) & grams for c in comments)
