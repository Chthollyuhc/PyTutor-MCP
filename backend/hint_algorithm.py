"""Thuật toán chi tiết bằng LỜI cho gợi ý Mức 3 (v5.12). Hàm thuần: không gọi mô hình, không DB.

Ranh giới của Mức 3 sau v5.12: cho CẤU TRÚC và THUẬT TOÁN viết bằng lời; KHÔNG cho mã Python của phần logic.
Nguồn thuật toán, theo thứ tự ưu tiên:
  1. ghi chú `algorithm_notes` do giảng viên viết cho bài (chỉ Mức 3 nhận; sinh viên không bao giờ thấy trường này);
  2. khuôn thuật toán theo DẠNG BÀI (tổng/tích lũy, tích, số nguyên tố, đảo chuỗi, đếm, hoặc khuôn chung theo chủ đề).
Khuôn theo dạng bài là heuristic nhận diện qua tiêu đề/chủ đề của bài, không bảo đảm đúng cho mọi đề; khi không có ghi chú
của giảng viên, phản hồi phải nói rõ đây là thuật toán tổng quát theo dạng bài.
Mọi câu chỉ nêu việc cần làm bằng lời: không viết biểu thức/điều kiện Python (xem `guardrails.enforce_level3_prose`).
"""
from __future__ import annotations

import re
from typing import Optional

from backend import exercise_brief

_MAX_NOTE_SENTENCES = 8
_MAX_SENTENCE_CHARS = 220
_CODE_LINE = re.compile(r"^\s*(?:def\s|for\s.+\sin\s|while\s|if\s.+:|elif\s|else\s*:|return\b|print\s*\(|\w+(?:\s*,\s*\w+)*\s*(?:\+=|-=|\*=|//=|=)(?!=))")

# (lead, [bước con]) cho 4 bước. {goal} là tên mục tiêu của bài.
_Step = tuple[str, list[str]]

_TEMPLATES: dict[str, dict] = {
    "sum": {
        "label": "tích lũy bằng phép cộng",
        "idea": "Dùng một biến làm «bộ cộng dồn»: đặt nó ở giá trị trung hòa của phép cộng, rồi lần lượt đưa từng phần tử của miền cần xét "
                "vào bộ cộng dồn đúng một lần. Kết quả cần tìm chính là giá trị của bộ cộng dồn khi đã duyệt hết miền.",
        "steps": [
            ("Đọc dữ liệu đầu vào và đổi sang kiểu số để tính toán được.",
             ["Dữ liệu đọc từ bàn phím luôn là chuỗi: xác định kiểu số mà đề yêu cầu để chuyển dữ liệu sang kiểu đó.",
              "Xác định miền cần xét: phần tử đầu, phần tử cuối, và phần tử cuối có được tính hay không."]),
            ("Chuẩn bị bộ cộng dồn cho «{goal}».",
             ["Chọn tên biến cho bộ cộng dồn và chỗ khai báo nó (trước vòng lặp, không phải bên trong).",
              "Chọn giá trị ban đầu: giá trị mà khi cộng thêm bất kỳ số nào vào vẫn không làm sai kết quả."]),
            ("Duyệt từng phần tử của miền và gộp vào bộ cộng dồn.",
             ["Chọn cách duyệt cho đủ mọi phần tử của miền, không thừa không thiếu phần tử nào ở hai đầu.",
              "Ở mỗi phần tử: lấy giá trị hiện tại của bộ cộng dồn, kết hợp với phần tử đang xét rồi lưu lại vào chính bộ cộng dồn.",
              "Kiểm tra bằng tay ở lần duyệt đầu tiên và lần cuối cùng: bộ cộng dồn phải đúng với tổng của các phần tử đã qua."]),
            ("In kết quả sau khi vòng duyệt đã kết thúc.",
             ["Lệnh in nằm ngoài vòng duyệt (chỉ in một lần, sau khi đã gộp xong mọi phần tử)."]),
        ],
        "edges": ["Đầu vào nhỏ nhất mà đề cho phép: miền chỉ có một phần tử, bộ cộng dồn phải ra đúng phần tử đó.",
                  "Đầu vào lớn nhất: kiểm tra kiểu dữ liệu và thời gian chạy vẫn ổn."],
    },
    "product": {
        "label": "tích lũy bằng phép nhân",
        "idea": "Dùng một biến làm «bộ nhân dồn»: đặt nó ở giá trị trung hòa của phép nhân (không phải giá trị trung hòa của phép cộng), "
                "rồi lần lượt nhân từng phần tử của miền vào đó. Trường hợp miền rỗng thì bộ nhân dồn giữ nguyên giá trị ban đầu.",
        "steps": [
            ("Đọc dữ liệu đầu vào và đổi sang kiểu số nguyên.",
             ["Dữ liệu đọc từ bàn phím là chuỗi: đổi sang kiểu số nguyên theo yêu cầu của đề.",
              "Xác định miền cần nhân: từ phần tử nhỏ nhất đến giá trị đọc vào, và miền này có thể rỗng khi giá trị đọc vào là nhỏ nhất đề cho phép."]),
            ("Chuẩn bị bộ nhân dồn cho «{goal}».",
             ["Chọn giá trị ban đầu sao cho khi nhân thêm bất kỳ số nào vào vẫn không làm đổi số đó; hãy tự thử với giá trị 0 và giá trị 1 để thấy khác biệt.",
              "Khai báo biến này trước khi duyệt."]),
            ("Duyệt miền và nhân từng phần tử vào bộ nhân dồn.",
             ["Chọn cách duyệt đủ mọi phần tử của miền, chú ý hai đầu của miền.",
              "Ở mỗi phần tử: lấy giá trị hiện tại, nhân với phần tử đang xét rồi lưu lại vào chính biến đó.",
              "Tự tính tay ba phần tử đầu để chắc rằng giá trị sau mỗi lần duyệt đúng với tích các phần tử đã qua."]),
            ("In kết quả sau khi duyệt xong.",
             ["Lệnh in nằm ngoài vòng duyệt, chỉ in giá trị cuối cùng."]),
        ],
        "edges": ["Trường hợp miền rỗng (đầu vào nhỏ nhất đề cho phép): không có lần nhân nào, kết quả phải đúng theo quy ước của đề.",
                  "Đầu vào lớn: kết quả tăng rất nhanh, nhưng Python vẫn xử lý số nguyên lớn đúng."],
    },
    "prime": {
        "label": "kiểm tra tính chất bằng cách thử các ước",
        "idea": "Loại các trường hợp chắc chắn không thỏa ngay từ đầu, rồi thử lần lượt các số chia có thể có. Chỉ cần một số chia hết là đủ để kết luận "
                "«không», còn muốn kết luận «có» thì phải thử hết các số chia trong phạm vi cần xét mà không gặp số nào chia hết.",
        "steps": [
            ("Đọc dữ liệu đầu vào và đổi sang kiểu số nguyên.",
             ["Đọc một số nguyên từ bàn phím; chú ý đề cho phép cả số âm và số nhỏ."]),
            ("Xử lý trước các trường hợp biên theo định nghĩa trong đề.",
             ["Theo định nghĩa của đề, số nhỏ hơn một ngưỡng nhất định không thỏa tính chất: viết riêng nhánh này và kết luận ngay.",
              "Xác định các số đặc biệt nhỏ nhất vẫn thỏa tính chất, để chắc rằng bước thử ở sau không làm chúng bị loại nhầm."]),
            ("Thử các số chia trong phạm vi cần xét.",
             ["Xác định phạm vi số chia cần thử: bắt đầu từ số chia nhỏ nhất có nghĩa và dừng ở mốc nào là đủ (không cần thử tới chính số đó).",
              "Với mỗi số chia, kiểm tra xem nó có chia hết số đầu vào không.",
              "Gặp số chia hết đầu tiên thì dừng việc thử ngay và ghi nhận kết luận «không thỏa»; không thể «sửa lại» kết luận này ở các lần thử sau.",
              "Thử hết phạm vi mà không gặp số chia hết nào thì mới kết luận «thỏa»."]),
            ("In đúng kết luận theo định dạng đề yêu cầu.",
             ["Kiểm tra chữ in hoa/in thường và từ ngữ in ra đúng từng ký tự như đề viết; chỉ in một kết luận cho mỗi lần chạy."]),
        ],
        "edges": ["Số nhỏ hơn 2, số bằng 0 và số âm.", "Số nguyên tố nhỏ nhất và số kế tiếp nó.",
                  "Số chính phương của một số nguyên tố (ước duy nhất nằm đúng ở mốc dừng của việc thử)."],
    },
    "reverse": {
        "label": "đảo thứ tự các phần tử của dãy",
        "idea": "Dựng một dãy kết quả mới bắt đầu rỗng, rồi lấy các ký tự của dãy gốc theo thứ tự ngược (từ cuối về đầu) đưa lần lượt vào dãy kết quả. "
                "Cũng có thể dùng cách cắt lát với bước âm để lấy luôn dãy đảo; chọn một trong hai cách và tự giải thích vì sao nó đúng.",
        "steps": [
            ("Đọc chuỗi đầu vào đúng một dòng.",
             ["Đọc nguyên một dòng từ bàn phím và giữ nguyên các ký tự, kể cả khoảng trắng, theo mô tả của đề."]),
            ("Chuẩn bị nơi chứa chuỗi kết quả cho «{goal}».",
             ["Nếu chọn cách xây dựng dần: khai báo chuỗi kết quả bắt đầu rỗng.",
              "Nếu chọn cách cắt lát: bỏ qua bước này và chuyển thẳng sang bước tạo dãy đảo."]),
            ("Lấy các ký tự theo thứ tự từ cuối về đầu.",
             ["Xác định vị trí ký tự đầu tiên cần lấy (ký tự cuối) và vị trí kết thúc, chú ý chỉ mục trong Python bắt đầu từ 0.",
              "Ở mỗi ký tự lấy được, đưa nó vào cuối chuỗi kết quả.",
              "Tự thử với chuỗi ba ký tự để chắc thứ tự đã đảo hoàn toàn."]),
            ("In chuỗi kết quả.",
             ["Chỉ in một lần, sau khi chuỗi đã đảo xong."]),
        ],
        "edges": ["Chuỗi chỉ có một ký tự: kết quả phải giống chuỗi gốc.", "Chuỗi đối xứng: kết quả giống chuỗi gốc.",
                  "Chuỗi có chữ hoa và chữ thường: các ký tự phải được giữ nguyên dạng."],
    },
    "count": {
        "label": "đếm các phần tử thỏa một điều kiện",
        "idea": "Dùng một biến đếm bắt đầu từ 0, duyệt lần lượt từng phần tử của dãy; phần tử nào thỏa điều kiện của đề thì tăng biến đếm lên một. "
                "Kết quả là giá trị của biến đếm sau khi đã xét hết dãy.",
        "steps": [
            ("Đọc chuỗi hoặc dãy đầu vào.",
             ["Đọc nguyên dòng đầu vào và quyết định có cần chuẩn hóa dữ liệu (ví dụ đưa về cùng một dạng chữ) trước khi xét hay không."]),
            ("Chuẩn bị biến đếm cho «{goal}».",
             ["Khai báo biến đếm với giá trị ban đầu là «chưa đếm được gì»; khai báo trước vòng duyệt.",
              "Xác định tập các giá trị được tính là thỏa điều kiện, dựa đúng vào định nghĩa trong đề."]),
            ("Duyệt từng phần tử và quyết định có đếm hay không.",
             ["Duyệt đủ mọi phần tử, không bỏ sót phần tử nào ở đầu hoặc cuối dãy.",
              "Ở mỗi phần tử: kiểm tra phần tử đó có thuộc tập thỏa điều kiện không; nếu có thì tăng biến đếm lên một, nếu không thì không làm gì.",
              "Chú ý việc phân biệt hoa/thường theo yêu cầu của đề."]),
            ("In giá trị của biến đếm.",
             ["Lệnh in nằm ngoài vòng duyệt, chỉ in một lần."]),
        ],
        "edges": ["Dãy không có phần tử nào thỏa điều kiện: kết quả phải là 0.", "Dãy rỗng hoặc chỉ có một phần tử.",
                  "Phần tử thỏa điều kiện nhưng khác dạng chữ hoa/thường."],
    },
    "loop": {
        "label": "xử lý lặp trên một miền dữ liệu",
        "idea": "Xác định rõ miền dữ liệu cần duyệt và đại lượng cần cập nhật qua từng phần tử; đặt giá trị ban đầu cho đại lượng đó, "
                "cập nhật nó ở mỗi lần duyệt, rồi chỉ in kết quả sau khi vòng duyệt kết thúc.",
        "steps": [
            ("Đọc dữ liệu đầu vào đúng kiểu mà đề yêu cầu.", ["Xác định kiểu dữ liệu cần dùng và đổi kiểu ngay sau khi đọc."]),
            ("Chuẩn bị đại lượng kết quả của «{goal}».",
             ["Quyết định biến nào giữ kết quả và giá trị ban đầu hợp lý của nó theo phép toán sẽ dùng."]),
            ("Duyệt miền dữ liệu và cập nhật kết quả.",
             ["Xác định miền cần duyệt và hai đầu của nó.",
              "Ở mỗi phần tử: nói bằng lời điều gì xảy ra với đại lượng kết quả.",
              "Tự tính tay ba lần duyệt đầu để kiểm tra cách cập nhật."]),
            ("In kết quả đúng định dạng đề yêu cầu.", ["Lệnh in nằm ngoài vòng duyệt."]),
        ],
        "edges": ["Đầu vào nhỏ nhất đề cho phép.", "Đầu vào lớn nhất đề cho phép."],
    },
    "branch": {
        "label": "phân loại theo các trường hợp",
        "idea": "Liệt kê đủ các trường hợp mà đề phân biệt, sắp xếp thứ tự xét sao cho không có trường hợp nào bị bỏ sót hoặc bị xét chồng, "
                "rồi mỗi trường hợp cho đúng một kết quả theo đề.",
        "steps": [
            ("Đọc dữ liệu đầu vào đúng kiểu.", ["Đổi kiểu dữ liệu ngay sau khi đọc."]),
            ("Liệt kê các trường hợp của «{goal}».",
             ["Viết ra giấy mọi trường hợp mà đề phân biệt, kể cả các giá trị biên.",
              "Xác định thứ tự xét: trường hợp nào phải xét trước để không bị trường hợp khác che mất."]),
            ("Xét từng trường hợp theo thứ tự đã chọn.",
             ["Với mỗi trường hợp, nói bằng lời điều kiện để rơi vào nó và kết quả tương ứng.",
              "Kiểm tra các giá trị nằm đúng ở ranh giới giữa hai trường hợp."]),
            ("In kết quả của trường hợp đã xác định.", ["Mỗi lần chạy chỉ in đúng một kết quả theo định dạng đề."]),
        ],
        "edges": ["Các giá trị nằm đúng ở ranh giới giữa hai trường hợp.", "Giá trị nhỏ nhất và lớn nhất mà đề cho phép."],
    },
    "recursion": {
        "label": "quy bài toán về bài toán nhỏ hơn",
        "idea": "Xác định trường hợp cơ sở (đủ nhỏ để biết ngay kết quả) và cách quy bài toán hiện tại về một bài toán nhỏ hơn cùng dạng; "
                "đảm bảo mỗi lần quy về thì đầu vào tiến gần hơn tới trường hợp cơ sở.",
        "steps": [
            ("Đọc dữ liệu đầu vào đúng kiểu.", ["Đổi kiểu dữ liệu ngay sau khi đọc."]),
            ("Xác định trường hợp cơ sở của «{goal}».", ["Đầu vào nhỏ nhất nào có kết quả biết ngay mà không cần quy về bài nhỏ hơn."]),
            ("Xác định bước quy về bài toán nhỏ hơn.",
             ["Nói bằng lời kết quả của đầu vào hiện tại được tạo từ kết quả của bài nhỏ hơn như thế nào.",
              "Kiểm tra đầu vào luôn tiến tới trường hợp cơ sở sau hữu hạn bước."]),
            ("Gọi hàm với đầu vào của đề và in kết quả.", ["In đúng một lần, bên ngoài hàm."]),
        ],
        "edges": ["Trường hợp cơ sở.", "Đầu vào lớn nhất đề cho phép (chú ý giới hạn độ sâu đệ quy)."],
    },
}


def kind_of(exercise: Optional[dict]) -> str:
    """Dạng bài theo tiêu đề, chủ đề và mô tả (heuristic)."""
    ex = exercise or {}
    text = " ".join(str(ex.get(k, "") or "") for k in ("title", "category")).lower()
    desc = str(ex.get("description", "") or "").lower()
    both = text + " " + desc[:400]
    if re.search(r"nguyên tố|prime", text) or re.search(r"nguyên tố", both):
        return "prime"
    if re.search(r"giai thừa|factorial", text):
        return "product"
    if re.search(r"đảo ngược|reverse|đảo chuỗi", text):
        return "reverse"
    if re.search(r"đếm|count", text):
        return "count"
    if re.search(r"tổng|sum|tích lũy|cộng dồn", text):
        return "sum"
    if re.search(r"đệ quy|recursion", text) and not re.search(r"vòng lặp", text):
        return "recursion"
    if re.search(r"rẽ nhánh|điều kiện|branch", text) and not re.search(r"vòng lặp|chuỗi", text):
        return "branch"
    return "loop"


def clean_notes(notes: Optional[str]) -> list[str]:
    """Câu của ghi chú giảng viên đã làm sạch: bỏ khối code, dòng giống câu lệnh Python, cắt độ dài; tối đa 8 câu."""
    text = re.sub(r"```.*?```", " ", notes or "", flags=re.DOTALL)
    out: list[str] = []
    for raw in re.split(r"\n+|(?<=[.!?])\s+", text):
        s = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", raw).strip()
        if len(re.findall(r"\w+", s)) < 3 or _CODE_LINE.match(s):
            continue
        out.append(s[:_MAX_SENTENCE_CHARS].rstrip())
        if len(out) >= _MAX_NOTE_SENTENCES:
            break
    return out


def algorithm_plan(exercise: Optional[dict]) -> dict:
    """Thuật toán chi tiết cho Mức 3.

    Trả về {source: 'instructor'|'template', label, idea, steps: [(lead, [bước con])], edges: [str]}.
    Khi giảng viên có ghi chú: các câu của ghi chú trở thành bước con của Bước 3 (phần xử lý chính); ý tưởng chung, Bước 1, 2, 4
    giữ khung theo dạng bài.
    """
    kind = kind_of(exercise)
    tpl = _TEMPLATES[kind]
    goal = re.sub(r"^\s*B[àa]i\s*\d+\s*[:.\-–]\s*", "", (exercise or {}).get("title", "") or "bài tập").strip() or "bài tập"
    steps: list[_Step] = [(lead.format(goal=goal), [s.format(goal=goal) for s in subs]) for lead, subs in tpl["steps"]]
    edges = list(tpl["edges"])
    cases = [d if len(d) <= 70 else d[:70].rsplit(" ", 1)[0] + "…" for d in exercise_brief.notable_cases(exercise, 3)
             if re.search(r"[A-Za-zÀ-ỹ]{3}", d)]
    if cases:
        edges = [f"Các nhóm trường hợp mà kiểm thử của giảng viên nhắc tới: {'; '.join(cases)}."] + edges
    edges = edges[:4]
    notes = clean_notes((exercise or {}).get("algorithm_notes"))
    if notes:
        # Ghi chú của giảng viên thường đã gồm cả khởi tạo và in kết quả: gộp vào Bước 3 và bỏ ý con trùng ở Bước 2 và Bước 4.
        # Chỉ gộp khi ghi chú đủ dài (>= 4 câu); ghi chú ngắn thì giữ ý con của khuôn để Mức 3 vẫn đủ chi tiết.
        if len(notes) >= 4:
            steps[1] = (steps[1][0], [])
            steps[3] = (steps[3][0], [])
        steps[2] = (steps[2][0] + " Theo ghi chú của giảng viên:", notes)
        return {"source": "instructor", "label": tpl["label"], "idea": tpl["idea"], "steps": steps, "edges": edges, "kind": kind}
    return {"source": "template", "label": tpl["label"], "idea": tpl["idea"], "steps": steps, "edges": edges, "kind": kind}


SOURCE_NOTE = {
    "instructor": "*Thuật toán dưới đây dựa trên ghi chú của giảng viên cho bài này, diễn đạt lại theo bài làm của bạn.*",
    "template": "*Giảng viên chưa viết ghi chú thuật toán cho bài này, nên đây là thuật toán tổng quát theo dạng bài («{label}»); "
                "hãy đối chiếu với đề của bạn.*",
}


def render_algorithm(plan: dict) -> str:
    """Khối Markdown: ý tưởng + Bước 1-4 (kèm bước con) + trường hợp cần xử lý. Chỉ có câu chữ, không có mã Python."""
    out = [SOURCE_NOTE[plan["source"]].format(label=plan["label"]), "", f"🧠 **Ý tưởng:** {plan['idea']}", ""]
    for i, (lead, subs) in enumerate(plan["steps"], 1):
        out.append(f"- **Bước {i}:** {lead}")
        for j, s in enumerate(subs, 1):
            out.append(f"  - {i}.{j} {s}")
    return "\n".join(out)


def render_edge_cases(plan: dict) -> str:
    return "\n".join(f"- {e}" for e in plan["edges"])


def todo_labels(plan: dict) -> list[str]:
    """Nhãn `Bước 3.k` cho các chỗ TODO trong khung mã: k chạy qua các bước con của Bước 3."""
    n = max(1, len(plan["steps"][2][1]))
    return [f"Bước 3.{k}" for k in range(1, n + 1)]
