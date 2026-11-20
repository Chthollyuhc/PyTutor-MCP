"""Câu chữ cho màn "Hành trình học" của sinh viên (v5.8): hàm thuần, tất định, không DB, không LLM.

Nguyên tắc: nói với sinh viên bằng giọng mô tả kèm bước tiếp theo; chỉ so với chính mình; không gắn nhãn tiêu cực,
không nhắc đầu ra mong đợi hay lời giải (Anti-Spoil). Không bao giờ đề xuất tự đẩy mức gợi ý lên.
"""
from __future__ import annotations

from typing import Any, Optional

from pytutor_shared.learner_model import PROCESS_PROGRESS_WINDOW, STATE_STRUGGLING

NEAR_PASS_MIN_SHARE = 0.5  # đạt >= 1/2 số test thì coi là đang tiến gần (quy ước trình bày, chưa hiệu chuẩn)

# Danh sách từ cấm trong câu chữ gửi sinh viên (test kiểm tra)
FORBIDDEN_STUDENT_WORDS = ("mắc kẹt", "xếp hạng", "kém", "yếu", "thất bại", "expected")

DISCLAIMER_VI = ("Đây là mô tả từ các lượt chạy thử, hỏi Gia sư AI và nộp bài của riêng bạn, theo quy tắc cố định chưa hiệu chuẩn. "
                 "Không phải điểm số hay kết luận về năng lực, và không so sánh với bạn khác.")


def _cta(exercise_id: Optional[str], title: Optional[str]) -> Optional[dict[str, str]]:
    return {"exercise_id": exercise_id, "title": title or exercise_id} if exercise_id else None


def build_student_headline(learner_model: Optional[dict], next_practice: Optional[dict], week: Optional[dict],
                           recent: Optional[list[dict]]) -> dict[str, Any]:
    """Một câu tóm tắt + một nút. Thứ tự ưu tiên: chưa có dữ liệu → khái niệm đang vướng → bài tiến gần → tuần này → bước kế."""
    learner_model, week, recent = learner_model or {}, week or {}, recent or []
    concepts = [c for c in (learner_model.get("concepts") or [])]
    next_cta = _cta((next_practice or {}).get("exercise_id"), (next_practice or {}).get("title"))
    has_data = bool(recent) or any(c.get("exercise_details") for c in concepts)

    if not has_data:
        return {"headline_vi": "Hãy bắt đầu với bài đầu tiên", "tone": "start", "cta": next_cta,
                "detail_vi": "Chạy thử vài lần là đủ để hệ thống bắt đầu vẽ hành trình của bạn. Chưa cần làm đúng ngay."}

    struggling = next((c for c in concepts if c.get("state") == STATE_STRUGGLING), None)
    if struggling:
        target = next((d for d in struggling.get("exercise_details") or [] if d.get("status") != "passed"), None)
        cta = _cta((target or {}).get("exercise_id"), (target or {}).get("title")) or next_cta
        return {"headline_vi": f"Khái niệm “{struggling['label_vi']}” đáng luyện thêm", "tone": "focus", "cta": cta,
                "detail_vi": ("Bạn đã thử nhiều lần ở các bài thuộc khái niệm này mà chưa đạt hết test. "
                              "Thử chạy từng bước, xem lại khái niệm, hoặc hỏi Gia sư AI ở mức bạn chọn.")}

    near = None
    for ex in recent:
        best = ex.get("best") or {}
        total = int(best.get("total") or 0)
        if ex.get("group") not in ("in_progress", "stuck", "practice_only") or total <= 0:
            continue
        if int(best.get("passed") or 0) / total >= NEAR_PASS_MIN_SHARE and best.get("passed") != total:
            near = (ex, best)
            break
    if near:
        ex, best = near
        return {"headline_vi": f"Bạn đang tiến gần ở “{ex['title']}”: đạt {best['passed']}/{best['total']} test",
                "tone": "progress", "cta": _cta(ex["exercise_id"], ex["title"]),
                "detail_vi": "Còn một vài test nữa. Chạy thử để xem test nào chưa qua rồi sửa từng chỗ."}

    if int(week.get("this") or 0) > 0:
        n = int(week["this"])
        detail = (next_practice or {}).get("reason") or "Hãy tiếp tục theo lộ trình của lớp."
        return {"headline_vi": f"Tuần này bạn có thêm {n} bài đạt lần đầu", "tone": "progress", "cta": next_cta,
                "detail_vi": f"Bước tiếp theo gợi ý: {detail}"}

    if next_practice:
        return {"headline_vi": "Bước luyện tập tiếp theo của bạn", "tone": "next", "cta": next_cta,
                "detail_vi": next_practice.get("reason") or "Hãy tiếp tục theo lộ trình của lớp."}
    return {"headline_vi": "Bạn có thể xem lại các bài đã làm", "tone": "next", "cta": None,
            "detail_vi": "Chưa có gợi ý cụ thể từ dữ liệu hiện tại; hãy tiếp tục theo lộ trình của lớp học phần."}


def describe_exercise_journey(points: list[dict], summary: dict) -> str:
    """Một câu mô tả dấu chân của một bài, nói với sinh viên."""
    attempts = [p for p in points if p.get("kind") in ("run", "submit")]
    if not points:
        return "Bạn chưa có lượt nào ở bài này. Chạy thử một lần để bắt đầu."
    best = summary.get("best") or {}
    fp = summary.get("first_pass_index")
    if fp is not None:
        upto = [p for p in points[: fp + 1] if p.get("kind") in ("run", "submit")]
        first_passed = upto[0].get("passed") if upto else None
        total = best.get("total") or (upto[-1].get("total") if upto else 0)
        if len(upto) <= 1:
            return "Bạn đạt ngay ở lượt đầu tiên của bài này."
        return (f"Bạn đã thử–sửa {len(upto)} lượt rồi đạt"
                + (f"; số test đạt tăng từ {first_passed} lên {total}." if first_passed is not None and total and first_passed < total else "."))
    recent = attempts[-PROCESS_PROGRESS_WINDOW:]
    earlier = attempts[:-PROCESS_PROGRESS_WINDOW]
    flat = (len(attempts) >= PROCESS_PROGRESS_WINDOW and earlier
            and max((p.get("passed") or 0) for p in recent) <= max((p.get("passed") or 0) for p in earlier))
    if flat:
        return (f"Bạn đã thử {len(attempts)} lượt, số test đạt tốt nhất là {best.get('passed', 0)}/{best.get('total', 0)} "
                "và mấy lượt gần đây chưa tăng thêm. Có thể chạy từng bước để xem giá trị từng dòng, xem lại khái niệm, "
                "hoặc hỏi Gia sư AI ở mức bạn chọn.")
    if not attempts:
        return "Bạn đã xem gợi ý ở bài này nhưng chưa chạy thử. Thử chạy một lần để xem test nào qua."
    return (f"Bạn đã thử {len(attempts)} lượt; số test đạt tốt nhất hiện là {best.get('passed', 0)}/{best.get('total', 0)}. "
            "Tiếp tục sửa từng chỗ một.")
