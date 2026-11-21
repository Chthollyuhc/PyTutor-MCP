"""Tóm tắt đề bài và bộ kiểm thử của giảng viên để gợi ý bám sát ý đồ của bài (v5.11). Hàm thuần, không DB, không LLM.

Từ `exercise` (title, description Markdown, test_cases) rút ra:
  - mục tiêu học tập, đầu vào, đầu ra, ví dụ trong đề (mục "Ví dụ" của đề, vốn đã hiển thị cho sinh viên);
  - tổng quan bộ kiểm thử: số lượng, mô tả từng kiểm thử (giao diện đã hiện cho sinh viên) và nhóm kiểm thử (biên, số âm, giá trị lớn...).

Mỗi mức dùng phần được phép: Mức 1 chỉ dùng mục tiêu học tập và NHÓM kiểm thử (không có giá trị cụ thể); Mức 2 và Mức 3 dùng thêm
mô tả từng kiểm thử; ví dụ trong đề (có giá trị) chỉ dùng khi sinh viên chưa viết code. Đề không theo mẫu thì mọi trường rỗng, không lỗi.
"""
from __future__ import annotations

import re
from typing import Optional

_CATEGORY_RULES = (
    ("trường hợp biên", r"biên|1 ký tự|một ký tự|nhỏ nhất|lớn nhất"),
    ("trường hợp đặc biệt", r"đặc biệt|quy ước"),
    ("số âm", r"số âm|(?<!nguyên )\bâm\b"),
    ("giá trị lớn", r"\blớn\b|phức tạp|\bdài\b"),
    ("đầu vào rỗng", r"rỗng|trống"),
    ("chữ hoa và chữ thường", r"\bhoa\b|chữ thường|hoa thường"),
)


def _clean(text: str) -> str:
    t = (text or "").replace("\\le", "≤").replace("\\ge", "≥").replace("\\", "")
    return re.sub(r"\s+", " ", re.sub(r"[`$*]", "", t)).strip()


def _sections(description: str) -> dict[str, list[str]]:
    """Tách mô tả Markdown theo tiêu đề `#...`; khóa là tiêu đề chữ thường, giá trị là các dòng nội dung."""
    out: dict[str, list[str]] = {}
    current = "_intro"
    for raw in (description or "").splitlines():
        line = raw.rstrip()
        if line.lstrip().startswith("#"):
            current = _clean(line.lstrip("# ")).lower()
            out.setdefault(current, [])
        else:
            out.setdefault(current, []).append(line)
    return out


def _find(sections: dict[str, list[str]], *keys: str) -> list[str]:
    for title, lines in sections.items():
        if any(k in title for k in keys):
            return lines
    return []


def _bullets(lines: list[str]) -> list[str]:
    return [_clean(ln.strip().lstrip("-* ").strip()) for ln in lines
            if ln.strip().startswith(("-", "*")) and _clean(ln.strip().lstrip("-* "))]


def _examples(lines: list[str]) -> list[dict]:
    """Bảng `| Input | Output | Giải thích |` của đề (bỏ dòng tiêu đề và dòng ngăn cách)."""
    rows = []
    for ln in lines:
        s = ln.strip()
        if not (s.startswith("|") and s.endswith("|")):
            continue
        cells = [_clean(c) for c in s.strip("|").split("|")]
        if not cells or all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c) or cells[0].lower() in ("input", "đầu vào"):
            continue
        if len(cells) >= 2:
            rows.append({"input": cells[0], "output": cells[1], "explain": cells[2] if len(cells) > 2 else ""})
    return rows


def safe_objective(text: str) -> str:
    """Mục tiêu học tập đã bỏ phần trong ngoặc và đoạn trông như mã (ví dụ `[::-1]`, `+=`): giảng viên có thể ghi cả kỹ thuật
    giải trong mục tiêu, nhưng gợi ý không được nhắc lại biểu thức đó."""
    t = re.sub(r"\s\([^)]*\)", "", text or "")       # phần chú thích trong ngoặc (có dấu cách trước), vd "(+=)", "(n ≤ 1)"
    t = re.sub(r"\S*[\[\]:+=<>]\S*", "", t)          # đoạn có ký tự của biểu thức
    t = re.sub(r"\S*\.\w+\(\S*\)", "", t)            # lời gọi phương thức, vd ".lower()"
    return re.sub(r"\s+", " ", t).strip(" .;,") + ("." if t.strip() else "")


def parse_description(description: Optional[str]) -> dict:
    """{summary, inputs, outputs, examples, objectives}; trường nào không có thì rỗng."""
    sec = _sections(description or "")
    problem = _find(sec, "mô tả bài toán", "mô tả", "đề bài", "_intro")
    prose = [_clean(ln) for ln in problem
             if ln.strip() and not ln.strip().startswith(("|", "-", "*")) and not ln.strip().startswith("$$")]
    return {
        "summary": prose[0] if prose else "",
        "inputs": _bullets(_find(sec, "đầu vào", "input")),
        "outputs": _bullets(_find(sec, "đầu ra", "output")),
        "examples": _examples(_find(sec, "ví dụ")),
        "objectives": _bullets(_find(sec, "mục tiêu")),
    }


def test_overview(exercise: Optional[dict]) -> dict:
    """{count, descriptions: [str], categories: [str]} từ test_cases của giảng viên (mô tả đã hiển thị cho sinh viên)."""
    cases = (exercise or {}).get("test_cases") or []
    descs = []
    for tc in cases:
        d = _clean(str(tc.get("description") or ""))
        descs.append("" if not d or re.fullmatch(r"test case #?\d+", d, flags=re.IGNORECASE) else d)
    cats: list[str] = []
    for label, pattern in _CATEGORY_RULES:
        if any(re.search(pattern, d, flags=re.IGNORECASE) for d in descs) and label not in cats:
            cats.append(label)
    return {"count": len(cases), "descriptions": [d for d in descs if d], "categories": cats}


def notable_cases(exercise: Optional[dict], limit: int = 2) -> list[str]:
    """Mô tả kiểm thử đáng chú ý trước (biên, đặc biệt, số âm, lớn, rỗng, hoa/thường), rồi tới các kiểm thử còn lại."""
    descs = test_overview(exercise)["descriptions"]
    def notable(d: str) -> bool:
        return any(re.search(p, d, flags=re.IGNORECASE) for _, p in _CATEGORY_RULES)
    ordered = [d for d in descs if notable(d)] + [d for d in descs if not notable(d)]
    return ordered[:limit]


def brief_text(exercise: Optional[dict], hint_level: int, no_code: bool = False) -> str:
    """Khối văn bản đưa vào lời nhắc, theo giới hạn của từng mức. Rỗng nếu đề không có gì để tóm tắt."""
    info = parse_description((exercise or {}).get("description"))
    tests = test_overview(exercise)
    lines = []
    if info["objectives"]:
        lines.append("- Mục tiêu học tập (giảng viên nêu trong đề, đã bỏ chi tiết kỹ thuật giải): "
                     + " ".join(safe_objective(o) for o in info["objectives"]))
    if info["inputs"]:
        lines.append("- Đầu vào theo đề: " + "; ".join(info["inputs"]))
    if info["outputs"]:
        lines.append("- Đầu ra theo đề: " + "; ".join(info["outputs"]))
    if tests["count"]:
        lines.append(f"- Bộ kiểm thử của giảng viên: {tests['count']} kiểm thử"
                     + (f", gồm các nhóm: {', '.join(tests['categories'])}" if tests["categories"] else ""))
        if hint_level >= 2 and tests["descriptions"]:
            lines.append("- Mô tả từng kiểm thử (sinh viên cũng thấy trong giao diện): "
                         + "; ".join(f"#{i}: {d}" for i, d in enumerate(tests["descriptions"], 1)))
    if no_code and hint_level >= 2 and info["examples"]:  # Mức 1 không nêu giá trị, kể cả ví dụ của đề
        ex = info["examples"][0]
        lines.append(f"- Ví dụ trong đề: đầu vào `{ex['input']}` → đầu ra `{ex['output']}`"
                     + (f" ({ex['explain']})" if ex["explain"] else ""))
    return "\n".join(lines)
