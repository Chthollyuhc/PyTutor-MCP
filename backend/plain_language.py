"""Lời thường cho màn sinh viên và giảng viên (v5.9): hàm thuần, tất định, không DB, không LLM.

Chỉ đổi cách NÓI, không đổi cách TÍNH. Số liệu đầu vào lấy từ get_class_insights, get_exercise_journey,
get_student_journey_overview, mô hình người học và lộ trình lớp có sẵn. Đây là nơi DUY NHẤT sinh câu nhận xét;
giao diện chỉ hiển thị nguyên văn các trường *_vi.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Optional

from backend.class_overview import OVERVIEW_THRESHOLDS
from pytutor_shared.learner_model import PROCESS_PROGRESS_WINDOW, PROCESS_STUCK_MIN_ATTEMPTS

PLAIN_VERSION = "1"
PASS_GROUPS = ("independent_pass", "retry_pass", "hint_pass")
NEAR_PASS_MIN_SHARE = 0.5      # đúng từ một nửa số trường hợp trở lên thì nói "sắp xong" (quy tắc trình bày)
PERSISTENCE_MIN_ATTEMPTS = 5   # từ 5 lần thử trở lên mới khen "không bỏ cuộc"
MOMENT_WINDOW_DAYS = 7
STORY_VISIBLE_STEPS = 8
RUNS_CONDENSE_MIN = 3

KC_PLAIN = {
    "io_format": "In và nhập dữ liệu",
    "conditional": "Câu lệnh if",
    "loop": "Vòng lặp",
    "accumulator": "Cộng dồn trong vòng lặp",
    "string": "Xử lý chuỗi",
    "recursion": "Đệ quy",
}
GROUP_TITLES_VI = {"check_in": "Nên hỏi thăm", "trying": "Đang cố gắng", "doing_well": "Đang ổn",
                   "not_started": "Chưa bắt đầu"}
NOTE_STUDENT_VI = "Nhận xét tự động từ các lần bạn chạy thử và nộp bài, có thể chưa chính xác."
FEW_DATA_VI = "Lớp mới có ít hoạt động nên nhận xét có thể chưa chính xác."

# Từ cấm trong MỌI câu do module này sinh ra (test kiểm tra). Tên bài, tên sinh viên và mô tả test do giảng viên
# viết được chèn nguyên văn nên không thuộc phạm vi kiểm tra.
BANNED_WORDS = (
    "khái niệm", "trạng thái", "bằng chứng", "quy ước", "hiệu chuẩn", "trung vị", "tự lực", "nhóm quá trình",
    "mắc kẹt", "đạt độc lập", "thử–sửa", "thử-sửa", "dữ liệu hạn chế", "mẫu nhỏ", "heuristic", "lượt", "xếp hạng",
    "kém", "yếu", "thất bại", "expected", "≥", "≤", "%", "#", "n=", " sv ", "kc", "test",
)

REASON_BY_CODE = {
    "unresolved_recurring": "Bạn đã thử bài này vài lần mà chưa xong. Thử lại với cách nghĩ mới nhé.",
    "in_progress": "Bạn đã nộp bài này nhưng chưa đúng hết. Sửa thêm một chút nhé.",
    "next_unattempted": "Đây là bài tiếp theo bạn chưa làm.",
    "retry_for_autonomy": "Bạn đã xong bài này nhờ gợi ý. Thử tự làm lại để chắc tay hơn.",
}
BUTTON_BY_CODE = {"next_unattempted": "Bắt đầu", "retry_for_autonomy": "Làm lại"}


# ------------------------------------------------------------------ tiện ích
def kc_name(kc: Optional[str], label_vi: Optional[str] = None) -> str:
    """Tên kỹ năng bằng từ của môn học; kỹ năng do giảng viên tự thêm thì giữ tên giảng viên đặt."""
    return KC_PLAIN.get(kc or "") or label_vi or kc or ""


def first_name(full_name: Optional[str]) -> Optional[str]:
    """'Trần Minh Khánh - SV K65' -> 'Khánh'; 'SV An (giả lập)' -> 'An'."""
    if not full_name:
        return None
    base = re.sub(r"\(.*?\)", " ", str(full_name).split(" - ")[0])
    parts = base.split()
    return parts[-1] if parts else None


def _parse_ts(ts: Any) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.strptime(str(ts).replace("T", " ")[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def format_when(ts: Any) -> Optional[str]:
    """'2026-11-20 09:05:33' -> '20/11 09:05'."""
    d = _parse_ts(ts)
    return d.strftime("%d/%m %H:%M") if d else None


def _correct(passed: Any, total: Any) -> str:
    return f"đúng {int(passed or 0)} trên {int(total or 0)}"


# ------------------------------------------------------------------ sinh viên: chặng đường học phần
def build_course_path(class_exercises: Optional[list[dict]], class_id: Optional[str],
                      class_name: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Chặng đường từ get_class_exercises(class_id, username) (đã có status và stars_earned)."""
    indexed = sorted(enumerate(class_exercises or []), key=lambda x: (x[1].get("order_idx") or 0, x[0]))
    items = [it for _, it in indexed]
    if not items:
        return None
    statuses = [it.get("status") for it in items]
    current = next((i for i, s in enumerate(statuses) if s == "IN_PROGRESS"), None)
    if current is None:
        current = next((i for i, s in enumerate(statuses) if s == "AVAILABLE"), None)
    steps = []
    for i, it in enumerate(items):
        s = statuses[i]
        if s == "MASTERED":
            kind = "done"
        elif i == current:
            kind = "current"
        elif s == "LOCKED":
            kind = "locked"
        else:
            kind = "open"
        eid = it.get("exercise_id") or it.get("id")
        steps.append({"exercise_id": eid, "title": it.get("title") or eid, "number": i + 1, "kind": kind,
                      "stars": int(it.get("stars_earned") or 0) if kind == "done" else 0})
    total = len(steps)
    done = sum(1 for st in steps if st["kind"] == "done")
    remaining = total - done
    caption = (f"Bạn đã xong cả {total} bài của học phần." if remaining == 0
               else f"Còn {remaining} bài nữa là xong học phần.")
    return {"class_id": class_id, "class_name": class_name or "", "steps": steps, "total": total,
            "done": done, "remaining": remaining, "caption_vi": caption}


# ------------------------------------------------------------------ sinh viên: thẻ "Hôm nay của bạn"
def _near_pass(recent: list[dict]):
    for ex in recent:
        best = ex.get("best") or {}
        p, t = int(best.get("passed") or 0), int(best.get("total") or 0)
        if ex.get("group") in PASS_GROUPS or t <= 0 or p >= t:
            continue
        if p / t >= NEAR_PASS_MIN_SHARE:
            return ex, p, t
    return None


def _moments(concepts: list[dict], recent: list[dict], now: datetime) -> list[dict[str, str]]:
    """Tối đa 2 tin vui trong 7 ngày gần nhất. Thứ tự: không bỏ cuộc -> tự làm đúng -> làm tốt một phần."""
    since = now - timedelta(days=MOMENT_WINDOW_DAYS)
    fresh = []
    for ex in recent:
        d = _parse_ts(ex.get("first_pass_at"))
        if d and d >= since and ex.get("group") in PASS_GROUPS:
            fresh.append((d, ex))
    fresh.sort(key=lambda x: x[0], reverse=True)
    out: list[dict[str, str]] = []
    persist = next((ex for _, ex in fresh if ex.get("group") in ("retry_pass", "hint_pass")
                    and int(ex.get("attempts_to_first_pass") or 0) >= PERSISTENCE_MIN_ATTEMPTS), None)
    if persist:
        out.append({"kind": "persistence", "text_vi": (f"Bạn không bỏ cuộc: bài {persist['title']} đúng hết sau "
                                                       f"{int(persist['attempts_to_first_pass'])} lần thử.")})
    indep = next((ex for _, ex in fresh if ex.get("group") == "independent_pass"), None)
    if indep:
        out.append({"kind": "independent", "text_vi": f"Bạn tự làm đúng bài {indep['title']} chỉ sau vài lần thử."})
    fresh_ids = {ex.get("exercise_id") for _, ex in fresh}
    skill = next((c for c in concepts if c.get("state") == "secure"
                  and any(d.get("exercise_id") in fresh_ids for d in (c.get("exercise_details") or []))), None)
    if skill:
        out.append({"kind": "new_skill",
                    "text_vi": f"Bạn đã làm tốt phần {kc_name(skill.get('kc'), skill.get('label_vi'))} rồi."})
    return out[:2]


def _headline(has_activity: bool, week: dict, near) -> str:
    this, prev = int(week.get("this") or 0), int(week.get("prev") or 0)
    if not has_activity:
        return "Chào mừng bạn! Hãy bắt đầu với bài đầu tiên."
    if this > 0:
        if this > prev:
            return f"Tuần này bạn làm đúng {this} bài mới, nhiều hơn tuần trước {this - prev} bài."
        if this == prev:
            return f"Tuần này bạn làm đúng {this} bài mới, đều tay như tuần trước."
        return f"Tuần này bạn làm đúng {this} bài mới."
    if near:
        ex, p, t = near
        return f"Bạn sắp xong bài {ex['title']} rồi: đã đúng {p} trên {t} trường hợp."
    return "Sẵn sàng làm tiếp chưa? Bài tiếp theo đang chờ bạn."


def _next_step(concepts: list[dict], next_practice: Optional[dict], near) -> Optional[dict[str, str]]:
    if near:
        ex, p, t = near
        return {"exercise_id": ex["exercise_id"], "title": ex["title"], "button_vi": "Làm tiếp",
                "reason_vi": f"Lần trước bạn đã đúng {p} trên {t} trường hợp. Sửa thêm một chút là xong."}
    for c in concepts:
        if c.get("state") != "struggling":
            continue
        target = next((d for d in (c.get("exercise_details") or []) if d.get("status") != "passed"), None)
        if target:
            return {"exercise_id": target["exercise_id"], "title": target.get("title") or target["exercise_id"],
                    "button_vi": "Luyện bài này",
                    "reason_vi": f"Bài này giúp bạn luyện thêm phần {kc_name(c.get('kc'), c.get('label_vi'))}."}
    if next_practice and next_practice.get("exercise_id"):
        code = next_practice.get("reason_code")
        return {"exercise_id": next_practice["exercise_id"],
                "title": next_practice.get("title") or next_practice["exercise_id"],
                "button_vi": BUTTON_BY_CODE.get(code, "Làm tiếp"),
                "reason_vi": REASON_BY_CODE.get(code, "Đây là bài nên làm tiếp.")}
    return None


def _skills(concepts: list[dict]):
    buckets: dict[str, list[str]] = {"good": [], "practicing": [], "needs_practice": []}
    key = {"secure": "good", "developing": "practicing", "struggling": "needs_practice"}
    for c in concepts:
        b = key.get(c.get("state"))
        if b:
            buckets[b].append(kc_name(c.get("kc"), c.get("label_vi")))
    parts = []
    if buckets["good"]:
        parts.append("Bạn làm tốt: " + ", ".join(buckets["good"]))
    if buckets["practicing"]:
        parts.append("Đang luyện: " + ", ".join(buckets["practicing"]))
    if buckets["needs_practice"]:
        parts.append("Nên luyện thêm: " + ", ".join(buckets["needs_practice"]))
    return buckets, (" · ".join(parts) or None)


def build_today_card(*, full_name: Optional[str], concepts: Optional[list[dict]], next_practice: Optional[dict],
                     week: Optional[dict], recent: Optional[list[dict]], path: Optional[dict],
                     now: datetime) -> dict[str, Any]:
    concepts, recent, week = list(concepts or []), list(recent or []), dict(week or {})
    name = first_name(full_name)
    near = _near_pass(recent)
    has_activity = bool(recent) or int(week.get("this") or 0) > 0 or any(c.get("exercise_details") for c in concepts)
    skills, skills_vi = _skills(concepts)
    return {
        "greeting_vi": f"Chào {name}" if name else "Chào bạn",
        "headline_vi": _headline(has_activity, week, near),
        "moments": _moments(concepts, recent, now) if has_activity else [],
        "next_step": _next_step(concepts, next_practice, near),
        "skills": skills,
        "skills_vi": skills_vi,
        "path": path,
        "note_vi": NOTE_STUDENT_VI,
        "version": PLAIN_VERSION,
    }


# ------------------------------------------------------------------ câu chuyện một bài (sinh viên và giảng viên)
def _condense_runs(points: list[dict]) -> list[dict]:
    """Gộp từ 3 lần chạy thử liên tiếp trở lên thành một bước."""
    out, i = [], 0
    while i < len(points):
        p = points[i]
        if p.get("kind") != "run":
            out.append(dict(p))
            i += 1
            continue
        j = i
        while j < len(points) and points[j].get("kind") == "run":
            j += 1
        group = points[i:j]
        if len(group) >= RUNS_CONDENSE_MIN:
            out.append({"kind": "runs", "count": len(group), "passed": max(int(x.get("passed") or 0) for x in group),
                        "total": group[-1].get("total"), "all_passed": False,
                        "is_new_best": any(x.get("is_new_best") for x in group), "format_only": False,
                        "timestamp": group[0].get("timestamp")})
        else:
            out.extend(dict(x) for x in group)
        i = j
    return out


def _step(p: dict, seen_attempt: bool) -> dict[str, Any]:
    kind = p.get("kind")
    passed, total = p.get("passed"), p.get("total")
    tag, tag_tone, tone = None, None, "neutral"
    if kind == "ask":
        text, icon = f"Hỏi Gia sư AI, gợi ý mức {int(p.get('hint_level') or 0)}", "message"
    elif kind == "runs":
        text, icon = f"Chạy thử {p['count']} lần: tốt nhất {_correct(passed, total)}", "play"
    elif kind == "run":
        text, icon = f"Chạy thử: {_correct(passed, total)}", "play"
    elif p.get("all_passed"):
        text, icon, tone = "Nộp bài: đúng hết", "check", "done"
    else:
        text, icon = f"Nộp bài: {_correct(passed, total)}", "send"
    if kind != "ask" and not p.get("all_passed"):
        if p.get("format_only"):
            tag, tag_tone = "Chỉ sai cách in kết quả", "info"
        elif p.get("is_new_best") and seen_attempt and int(passed or 0) > 0:
            tag, tag_tone = "Đúng thêm", "good"
    step = {"kind": kind, "icon": icon, "tone": tone, "text_vi": text, "tag_vi": tag, "tag_tone": tag_tone,
            "when_vi": format_when(p.get("timestamp"))}
    if p.get("code"):
        step["code"] = p["code"]
    return step


def build_story(points: Optional[list[dict]], summary: Optional[dict], *, audience: str = "student",
                student_name: Optional[str] = None) -> dict[str, Any]:
    """Một câu tóm tắt + các bước. audience='teacher' nói ở ngôi thứ ba và không bao giờ có mã nguồn
    (endpoint giảng viên vốn không trả mã nguồn trong points)."""
    points, summary = list(points or []), dict(summary or {})
    counts = summary.get("counts") or {}
    runs, asks, submits = int(counts.get("run") or 0), int(counts.get("ask") or 0), int(counts.get("submit") or 0)
    attempts = runs + submits
    best = summary.get("best") or {}
    p, t = int(best.get("passed") or 0), int(best.get("total") or 0)
    teacher = audience == "teacher"
    who = (student_name or "Bạn này") if teacher else "Bạn"
    if not points:
        text = (f"{who} chưa làm bài này trong khoảng thời gian đang xem." if teacher
                else "Bạn chưa làm bài này. Bấm “Chạy thử” để bắt đầu.")
    elif summary.get("first_pass_at") or summary.get("first_pass_index") is not None:
        n = int(summary.get("attempts_to_first_pass") or attempts or 1)
        text = f"{who} làm đúng ngay lần đầu." if n <= 1 else f"{who} thử {n} lần rồi làm đúng hết."
    elif attempts == 0:
        text = (f"{who} mới hỏi Gia sư AI, chưa chạy thử lần nào." if teacher
                else "Bạn đã xem gợi ý nhưng chưa chạy thử. Bấm “Chạy thử” để xem kết quả.")
    elif submits == 0:
        text = (f"{who} đã chạy thử {runs} lần, tốt nhất {_correct(p, t)} trường hợp, chưa nộp bài." if teacher
                else f"Bạn đã chạy thử {runs} lần, tốt nhất {_correct(p, t)} trường hợp. Khi thấy ổn, bấm “Nộp bài” nhé.")
    elif summary.get("group") == "stuck":
        text = (f"{who} đã thử {attempts} lần, tốt nhất {_correct(p, t)} trường hợp. Mấy lần gần đây chưa đúng thêm, "
                "bạn ấy có thể cần được hỏi thăm." if teacher else
                f"Bạn đã thử {attempts} lần, tốt nhất {_correct(p, t)} trường hợp. Mấy lần gần đây chưa đúng thêm. "
                "Thử bấm “Chạy từng bước” để xem code chạy thế nào, hoặc hỏi Gia sư AI.")
    else:
        text = (f"{who} đã thử {attempts} lần, tốt nhất {_correct(p, t)} trường hợp." if teacher
                else f"Bạn đã thử {attempts} lần, tốt nhất {_correct(p, t)} trường hợp. Sửa từng chỗ một nhé.")
    if teacher and asks and points:
        text += f" Đã hỏi Gia sư AI {asks} lần."
    steps, seen = [], False
    for q in _condense_runs(points):
        steps.append(_step(q, seen))
        if q.get("kind") in ("run", "runs", "submit"):
            seen = True
    return {"summary_vi": text, "steps": steps, "visible_from": max(0, len(steps) - STORY_VISIBLE_STEPS)}


def story_one_liner(item: dict) -> str:
    """Một câu cho mỗi bài trong danh sách "Các bài gần đây" của sinh viên."""
    counts, best = item.get("counts") or {}, item.get("best") or {}
    if item.get("group") in PASS_GROUPS:
        return "Đã làm đúng hết."
    if int(counts.get("submit") or 0) == 0 and int(counts.get("run") or 0) > 0:
        return f"Đã chạy thử {int(counts['run'])} lần, chưa nộp bài."
    if int(best.get("total") or 0) > 0:
        return f"Đang làm: tốt nhất {_correct(best.get('passed'), best.get('total'))} trường hợp."
    return "Đang làm."


# ------------------------------------------------------------------ giảng viên: bản tin lớp
def _period(days: int):
    days = int(days or 7)
    return ("Tuần này", "tuần này") if days == 7 else (f"Trong {days} ngày qua", f"{days} ngày qua")


def _names(items: list[dict], limit: int = 3) -> str:
    names = [x["full_name"] for x in items[:limit]]
    extra = len(items) - limit
    return ", ".join(names) + (f" và {extra} bạn khác" if extra > 0 else "")


def _sorted_people(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda x: ((x.get("full_name") or "").casefold(), x.get("username") or ""))


def _groups(rows: list[dict], ex_ids: list[str], titles: dict[str, str], attention: Optional[list[dict]]):
    """Chia MỌI sinh viên ghi danh vào đúng một trong 4 nhóm, xếp A→Z. Dùng lại nhóm quá trình có sẵn ở matrix."""
    codes: dict[str, set] = {}
    for a in attention or []:
        codes.setdefault(a.get("student"), set()).add(a.get("code"))
    g: dict[str, list[dict]] = {"check_in": [], "trying": [], "doing_well": [], "not_started": []}
    for r in _sorted_people(rows):
        cells = r.get("cells") or {}
        ordered = [(eid, cells.get(eid)) for eid in ex_ids if cells.get(eid)]
        person = {"username": r["username"], "full_name": r.get("full_name") or r["username"]}
        if not ordered:
            g["not_started"].append(person)
            continue
        stuck = [e for e, grp in ordered if grp == "stuck"]
        passes = [e for e, grp in ordered if grp in PASS_GROUPS]
        hints = [e for e, grp in ordered if grp == "hint_pass"]
        practice = [e for e, grp in ordered if grp == "practice_only"]
        c = codes.get(r["username"], set())
        if stuck:
            reason = (f"Đang gặp khó ở bài {titles[stuck[0]]}: thử nhiều lần mà mấy lần gần đây chưa đúng thêm."
                      if len(stuck) == 1 else f"Đang gặp khó ở {len(stuck)} bài, ví dụ bài {titles[stuck[0]]}.")
            g["check_in"].append({**person, "reason_vi": reason, "exercise_id": stuck[0]})
        elif not passes:
            reason = (f"Đã chạy thử {len(practice)} bài nhưng chưa nộp bài nào." if len(practice) == len(ordered)
                      else f"Đang làm {len(ordered)} bài, chưa có bài nào đúng hết.")
            g["trying"].append({**person, "reason_vi": reason, "exercise_id": ordered[0][0]})
        elif "hint_dependence" in c:
            g["trying"].append({**person, "reason_vi": f"Có {len(hints)} bài làm đúng nhờ gợi ý mức 2 hoặc 3.",
                                "exercise_id": (hints or passes)[0]})
        elif "practice_only" in c:
            g["trying"].append({**person, "reason_vi": f"Chạy thử {len(practice)} bài nhưng chưa nộp.",
                                "exercise_id": (practice or [ordered[0][0]])[0]})
        else:
            g["doing_well"].append({**person, "done": len(passes)})
    return g


def _mistake(eid: str, failing_map: dict, error_map: dict) -> Optional[str]:
    tests = sorted(failing_map.get(eid) or [], key=lambda x: (-int(x.get("students") or 0),
                                                              -int(x.get("attempts") or 0), int(x.get("test_idx") or 0)))
    top = next((x for x in tests if int(x.get("students") or 0) >= 2), None)
    if top:
        desc = str(top.get("description") or "").strip().rstrip(".")
        inp = " / ".join(str(top.get("input") or "").split("\n")).strip()
        text = (f"Nhiều bạn sai ở trường hợp “{desc}”" if desc
                else f"Nhiều bạn sai ở trường hợp kiểm tra số {int(top.get('test_idx') or 0)}")
        if inp:
            text += f" (ví dụ đầu vào: {inp})"
        return text + "."
    e = error_map.get(eid)
    if e:
        fail_n = sum(int(n or 0) for src in ("submit", "run") for k, n in (e.get(src) or {}).items() if k != "passed")
        fmt_n = int(e.get("format_only_submit") or 0) + int(e.get("format_only_run") or 0)
        if (fail_n >= OVERVIEW_THRESHOLDS["format_only_min_attempts"]
                and fmt_n / fail_n >= OVERVIEW_THRESHOLDS["format_only_share"]):
            return "Nhiều bạn làm đúng ý nhưng in sai cách trình bày (thừa dấu cách hoặc sai chữ hoa, chữ thường)."
    return None


def _exercises(ex_list: list[dict], rows: list[dict], insights: dict, overview: Optional[dict]) -> list[dict]:
    failing_map = {f["exercise_id"]: f.get("tests") or [] for f in insights.get("failing_tests_by_exercise") or []}
    error_map = {e["exercise_id"]: e for e in insights.get("error_breakdown_by_exercise") or []}
    unsucc = {b["exercise_id"]: int(b.get("unsuccessful") or 0) for b in insights.get("bottlenecks") or []}
    issue_ex = {i.get("exercise_id") for i in (overview or {}).get("class_issues") or []
                if i.get("code") in ("bottleneck", "failing_test", "format_mismatch")}
    items = []
    for idx, e in enumerate(ex_list):
        eid = e["exercise_id"]
        done, attempted = int(e.get("students_passed") or 0), int(e.get("students_attempted") or 0)
        enrolled = int(e.get("students_enrolled") or len(rows))
        working = max(0, attempted - done)
        stuck = sum(1 for r in rows if (r.get("cells") or {}).get(eid) == "stuck")
        done_vi = f"{done} trong {enrolled} bạn đã làm xong" + (f", {working} bạn đang làm" if working else "") + "."
        items.append({"exercise_id": eid, "title": e.get("title") or eid, "number": idx + 1, "done": done,
                      "working": working, "not_started": max(0, enrolled - attempted), "enrolled": enrolled,
                      "stuck": stuck, "done_vi": done_vi, "mistake_vi": _mistake(eid, failing_map, error_map),
                      "hardest": False})
    cands = [x for x in items if x["stuck"] >= 1 or x["exercise_id"] in issue_ex]
    if cands:
        hardest = max(cands, key=lambda x: (x["stuck"], unsucc.get(x["exercise_id"], 0), -x["number"]))
        hardest["hardest"] = True
    return items


def _class_skills(kc_overview: Optional[dict]) -> list[str]:
    good, needs = [], []
    for it in (kc_overview or {}).get("items") or []:
        c = it.get("students") or {}
        secure, struggling = int(c.get("secure") or 0), int(c.get("struggling") or 0)
        with_ev = sum(int(v or 0) for k, v in c.items() if k != "no_evidence")
        name = kc_name(it.get("kc"), it.get("label_vi"))
        if with_ev and secure >= 2 and secure * 2 >= with_ev:
            good.append(name)
        if struggling >= 2 and name not in good:
            needs.append(f"{name} ({struggling} bạn cần luyện thêm)")
    out = []
    if good:
        out.append("Phần lớn các bạn làm tốt: " + ", ".join(good) + ".")
    if needs:
        out.append("Nên ôn lại trên lớp: " + ", ".join(needs) + ".")
    return out


def how_it_works_vi() -> list[str]:
    """Luật chia nhóm nói bằng lời, lấy đúng hằng số đang dùng (không chép tay con số)."""
    t = OVERVIEW_THRESHOLDS
    return [
        (f"Nên hỏi thăm: bạn đã thử một bài từ {PROCESS_STUCK_MIN_ATTEMPTS} lần trở lên (chạy thử và nộp bài) mà "
         f"{PROCESS_PROGRESS_WINDOW} lần gần nhất không đúng thêm trường hợp nào."),
        (f"Đang cố gắng: bạn chưa làm đúng hết bài nào, hoặc có từ {t['hint_pass_min_exercises']} bài làm đúng nhờ "
         f"gợi ý mức 2 hoặc 3, hoặc chạy thử từ {t['practice_only_min_exercises']} bài trở lên mà chưa nộp."),
        "Đang ổn: các bạn còn lại có vào làm bài.",
        "Chưa bắt đầu: chưa chạy thử hay nộp bài nào trong khoảng thời gian đang xem.",
        "Đây là nhận xét tự động theo quy tắc đơn giản, chưa được kiểm chứng. Thầy cô nên xem thêm trước khi kết luận.",
    ]


def _brief(days: int, rows: list[dict], groups: dict, exercises: list[dict], daily_trend: Optional[list[dict]]):
    period, period_lower = _period(days)
    enrolled = len(rows)
    active = enrolled - len(groups["not_started"])
    passes = sum(int(d.get("first_passes") or 0) for d in daily_trend or [])
    s: list[str] = []
    if active == 0:
        s.append(f"{period} chưa có bạn nào vào làm bài.")
        return s, active
    s.append(f"{period} có {active} trong {enrolled} bạn vào làm bài, làm đúng thêm {passes} bài." if passes
             else f"{period} có {active} trong {enrolled} bạn vào làm bài, chưa có bài nào được làm đúng hết.")
    well = len(groups["doing_well"])
    if well * 2 > active:
        s.append("Phần lớn các bạn đang ổn.")
    elif well * 2 == active:
        s.append("Một nửa số bạn đang ổn.")
    else:
        s.append("Nhiều bạn vẫn đang cố gắng.")
    k = len(groups["check_in"])
    s.append(f"{k} bạn nên được hỏi thăm: {_names(groups['check_in'])}." if k else "Chưa có bạn nào cần hỏi thăm ngay.")
    hardest = next((x for x in exercises if x["hardest"]), None)
    if hardest:
        title = str(hardest["title"])
        s.append(f"Bài khó nhất lúc này: {title}{'' if title.endswith(('.', '!', '?')) else '.'}" + (f" {hardest['mistake_vi']}" if hardest["mistake_vi"] else ""))
    ns = len(groups["not_started"])
    if ns:
        s.append(f"{ns} bạn chưa bắt đầu trong {period_lower}.")
    return s, active


def build_class_plain_view(insights: Optional[dict], overview: Optional[dict] = None, days: int = 7) -> dict[str, Any]:
    """Bản tin lớp từ kết quả get_class_insights (+ overview của class_overview). Không tính lại nhóm nào."""
    insights = insights or {}
    matrix = insights.get("matrix") or {}
    ex_list = matrix.get("exercises") or []
    rows = matrix.get("rows") or []
    ex_ids = [e["exercise_id"] for e in ex_list]
    titles = {e["exercise_id"]: e.get("title") or e["exercise_id"] for e in ex_list}
    groups = _groups(rows, ex_ids, titles, (overview or {}).get("attention"))
    exercises = _exercises(ex_list, rows, insights, overview)
    brief, active = _brief(days, rows, groups, exercises, insights.get("daily_trend"))
    status = insights.get("data_status") or "no_data"
    return {
        "brief_vi": brief,
        "few_data_vi": FEW_DATA_VI if active and status in ("no_data", "limited") else None,
        "groups": groups,
        "group_titles_vi": dict(GROUP_TITLES_VI),
        "exercises": exercises,
        "skills_vi": _class_skills(insights.get("kc_overview")),
        "how_it_works_vi": how_it_works_vi(),
        "active": active,
        "enrolled": len(rows),
        "days": int(days or 7),
        "version": PLAIN_VERSION,
    }


def class_brief_line(plain: Optional[dict]) -> str:
    """Một dòng cho thẻ lớp ở danh sách lớp của giảng viên."""
    if not plain or not plain.get("active"):
        return f"Chưa có hoạt động trong {int((plain or {}).get('days') or 7)} ngày qua."
    k = len(plain["groups"]["check_in"])
    parts = [f"{k} bạn nên hỏi thăm" if k else "Chưa có bạn nào cần hỏi thăm"]
    hardest = next((x for x in plain.get("exercises") or [] if x.get("hardest")), None)
    if hardest:
        parts.append(f"bài khó: {hardest['title']}")
    return " · ".join(parts)
