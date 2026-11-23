"""Dấu "đã xử lý / không cần" cho các việc giảng viên nên xem (v5.13): hàm thuần, không DB, không LLM.

Một "việc" là một mục của `overview["attention"]` (theo sinh viên) hoặc `overview["class_issues"]` (theo lớp).
Dấu gắn với đúng việc đó, không gắn với cả lớp, và tự mở lại khi:
  - tình hình đổi (sinh viên kẹt thêm bài khác bài đã đánh dấu), hoặc
  - đã đánh dấu "đã xử lý" quá MARK_VALIDITY_DAYS ngày mà việc vẫn còn.
"Không cần" (nhận xét tự động không đúng) chỉ mở lại khi tình hình đổi, không theo thời gian.
Dấu chỉ là ghi chú của giảng viên: không đi vào mô hình người học, Điểm nỗ lực hay số liệu chính thức.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Iterable, Optional

MARK_VALIDITY_DAYS = 7  # quy ước vận hành, chưa hiệu chuẩn
STATUS_HANDLED = "handled"
STATUS_DISMISSED = "dismissed"
MARK_STATUSES = (STATUS_HANDLED, STATUS_DISMISSED)
STATUS_LABEL_VI = {STATUS_HANDLED: "đã xử lý", STATUS_DISMISSED: "không cần"}
MAX_KEYS_PER_REQUEST = 60
_STUDENT_CODES = ("stuck", "hint_dependence", "practice_only")


def item_key(item: dict[str, Any]) -> str:
    """Khóa ổn định của một việc: loại việc + (sinh viên | bài | đơn vị kiến thức)."""
    code = item.get("code") or ""
    target = item.get("student") or item.get("exercise_id") or item.get("kc") or ""
    return f"{code}:{target}"


def item_signature(item: dict[str, Any]) -> str:
    """Chữ ký tình hình lúc đánh dấu: với việc theo sinh viên là tập bài liên quan; việc cấp lớp không có chữ ký."""
    if item.get("student"):
        ids = (item.get("evidence") or {}).get("exercise_ids") or []
        return ",".join(sorted({str(x) for x in ids}))
    return ""


def _parse(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(str(ts)[:19], fmt)
        except ValueError:
            continue
    return None


def _day_month(ts: Optional[str]) -> str:
    dt = _parse(ts)
    return dt.strftime("%d/%m") if dt else "trước đó"


def _ids(signature: Optional[str]) -> set[str]:
    return {x for x in (signature or "").split(",") if x}


def evaluate_mark(mark: Optional[dict[str, Any]], signature: str, now: datetime) -> Optional[dict[str, Any]]:
    """Trả None nếu chưa từng đánh dấu; ngược lại {state: handled|reopened, reason, status, marked_at, follow_up_vi}."""
    if not mark or mark.get("status") not in MARK_STATUSES:
        return None
    status = mark["status"]
    marked_at = _parse(mark.get("marked_at"))
    changed = not _ids(signature) <= _ids(mark.get("signature"))
    expired = status == STATUS_HANDLED and (marked_at is None or now - marked_at >= timedelta(days=MARK_VALIDITY_DAYS))
    state, reason, follow = "handled", None, None
    when = _day_month(mark.get("marked_at"))
    label = STATUS_LABEL_VI[status]
    if changed:
        state, reason = "reopened", "changed"
        follow = f"Thầy/cô đã đánh dấu “{label}” ngày {when}, nhưng sau đó có thay đổi mới."
    elif expired:
        state, reason = "reopened", "expired"
        follow = f"Thầy/cô đã đánh dấu “{label}” ngày {when}; đến nay vẫn còn."
    return {"state": state, "reason": reason, "status": status, "status_vi": label,
            "marked_at": mark.get("marked_at"), "follow_up_vi": follow}


def annotate_overview(overview: dict[str, Any], marks: dict[str, dict[str, Any]], now: datetime) -> dict[str, Any]:
    """Gắn `key`, `signature`, `mark` vào từng việc và tính `open_counts`. Sửa trực tiếp `overview` rồi trả về."""
    counts = {"attention": 0, "issues": 0, "handled": 0}
    for field, bucket in (("attention", "attention"), ("class_issues", "issues")):
        for it in overview.get(field) or []:
            it["key"] = item_key(it)
            it["signature"] = item_signature(it)
            it["mark"] = evaluate_mark(marks.get(it["key"]), it["signature"], now)
            if it["mark"] and it["mark"]["state"] == "handled":
                counts["handled"] += 1
            else:
                counts[bucket] += 1
    counts["open"] = counts["attention"] + counts["issues"]
    overview["open_counts"] = counts
    return overview


def current_signatures(overview: dict[str, Any]) -> dict[str, str]:
    """Khóa → chữ ký hiện tại của mọi việc đang có (dùng để xác thực khóa client gửi lên và ghi chữ ký do server tính)."""
    out: dict[str, str] = {}
    for field in ("attention", "class_issues"):
        for it in overview.get(field) or []:
            out[item_key(it)] = item_signature(it)
    return out


def handled_keys(overview: dict[str, Any]) -> set[str]:
    return {it["key"] for field in ("attention", "class_issues") for it in overview.get(field) or []
            if (it.get("mark") or {}).get("state") == "handled"}


def card_keys(card: dict[str, Any]) -> list[str]:
    """Các khóa việc mà một thẻ "Việc nên xem" đại diện."""
    if card.get("code") in _STUDENT_CODES:
        return [f"{card['code']}:{s['username']}" for s in card.get("students") or []]
    target = card.get("exercise_id") or card.get("kc") or ""
    return [f"{card.get('code')}:{target}"]


def annotate_plain_groups(plain: dict[str, Any], overview: dict[str, Any]) -> int:
    """Gắn `key`/`mark` cho sinh viên ở nhóm "nên hỏi thăm" (việc `stuck`) và trả số bạn còn việc mở ở nhóm đó.

    Chỉ bạn có việc `stuck` tương ứng trong overview mới có `key` (và mới có nút đánh dấu)."""
    items = {it["key"]: it for it in overview.get("attention") or [] if it.get("key")}
    open_n = 0
    for person in (plain.get("groups") or {}).get("check_in", []):
        it = items.get(f"stuck:{person['username']}")
        if it:
            person["key"] = it["key"]
            person["mark"] = it.get("mark")
        if not (person.get("mark") and person["mark"]["state"] == "handled"):
            open_n += 1
    return open_n
