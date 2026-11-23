"""Tóm tắt "Tình hình lớp" cho giảng viên (v5.7): hàm thuần, tất định, không DB, không LLM.

Đầu vào là kết quả `get_class_insights`; đầu ra là ba danh sách: cần chú ý / vấn đề chung / tiến triển tốt.
Mọi ngưỡng là quy ước vận hành chưa hiệu chuẩn; danh sách "cần chú ý" nêu lý do, không xếp hạng sinh viên.
"""
from __future__ import annotations

from typing import Any

from backend.attention_marks import card_keys

OVERVIEW_THRESHOLDS = {
    "hint_pass_min_exercises": 2,        # >= N bài đạt nhờ gợi ý Mức >= 2
    "practice_only_min_exercises": 2,    # >= N bài chỉ chạy thử, chưa nộp
    "struggling_share": 0.4,             # >= 40% SV có bằng chứng ở KC ở trạng thái "đang vướng"
    "struggling_min_students": 2,
    "bottleneck_unsuccessful_percent": 60.0,
    "bottleneck_min_submissions": 4,
    "failing_test_min_students": 2,
    "failing_test_share": 0.5,           # test sai chiếm >= 50% lượt chưa đạt của bài
    "format_only_share": 0.3,            # >= 30% lượt chưa đạt chỉ sai định dạng
    "format_only_min_attempts": 3,
    "positive_min_independent": 2,
    "note": "Quy ước vận hành, chưa hiệu chuẩn.",
}
T = OVERVIEW_THRESHOLDS


def _insufficient(insights: dict[str, Any]) -> bool:
    return insights.get("data_status") in (None, "no_data", "limited")


def build_class_overview(insights: dict[str, Any]) -> dict[str, Any]:
    status = insights.get("data_status") or "no_data"
    base = {"data_status": status, "thresholds": dict(T), "attention": [], "class_issues": [], "positives": [],
            "note": "Tóm tắt tự động từ số liệu mô tả, ngưỡng quy ước chưa hiệu chuẩn; chỉ gợi ý để giảng viên xem xét."}
    if not insights:
        return base
    titles = {b["exercise_id"]: b.get("title") for b in insights.get("bottlenecks", [])}
    process_titles = {}
    for e in (insights.get("process_groups") or {}).get("by_exercise", []):
        process_titles[e["exercise_id"]] = e.get("title")

    # --- Cần chú ý (theo SV, có lý do và số liệu nguồn; đủ dùng cả khi mẫu lớp nhỏ vì nói về từng SV) ---
    for st in insights.get("students", []):
        pbe = st.get("process_by_exercise") or {}
        name, user = st.get("full_name") or st["username"], st["username"]
        stuck = st.get("stuck_exercises") or []
        if stuck:
            titles_txt = ", ".join(x.get("title") or x["exercise_id"] for x in stuck[:3])
            base["attention"].append({
                "code": "stuck", "student": user, "student_name": name,
                "text_vi": f"{name} đang mắc kẹt ở {len(stuck)} bài ({titles_txt}).",
                "evidence": {"stuck_exercises": len(stuck), "exercise_ids": [x["exercise_id"] for x in stuck]},
                "suggestion_vi": "Mở hồ sơ để xem quá trình thử–sửa; cân nhắc nhắn riêng hoặc gợi ý hướng tiếp cận.",
                "target": "student_profile"})
        hint_n = sum(1 for g in pbe.values() if g == "hint_pass")
        if hint_n >= T["hint_pass_min_exercises"]:
            base["attention"].append({
                "code": "hint_dependence", "student": user, "student_name": name,
                "text_vi": f"{name} đạt nhờ gợi ý Mức 2 trở lên ở {hint_n} bài.",
                "evidence": {"hint_pass_exercises": hint_n,
                             "exercise_ids": sorted(e for e, g in pbe.items() if g == "hint_pass")},
                "suggestion_vi": "Có thể bạn này chưa chắc nền tảng; cân nhắc bài tương tự để tự luyện.",
                "target": "student_profile"})
        practice_n = sum(1 for g in pbe.values() if g == "practice_only")
        if practice_n >= T["practice_only_min_exercises"]:
            base["attention"].append({
                "code": "practice_only", "student": user, "student_name": name,
                "text_vi": f"{name} chạy thử ở {practice_n} bài nhưng chưa nộp bài nào trong số đó.",
                "evidence": {"practice_only_exercises": practice_n,
                             "exercise_ids": sorted(e for e, g in pbe.items() if g == "practice_only")},
                "suggestion_vi": "Có thể ngại nộp bài hoặc chưa tin vào lời giải; nhắc nhẹ rằng nộp bài không bị trừ điểm.",
                "target": "student_profile"})

    if _insufficient(insights):
        base["class_issues"] = []
        base["insufficient_reason_vi"] = "Chưa đủ dữ liệu để kết luận cấp lớp (dưới 3 sinh viên có hoạt động)." \
            if status == "limited" else "Chưa có lượt nộp nào trong khoảng thời gian này."
        return base

    # --- Vấn đề chung ---
    kc = (insights.get("kc_overview") or {})
    modeled = int(kc.get("modeled_students") or 0)
    for item in kc.get("items", []):
        counts = item.get("students") or {}
        with_evidence = sum(v for k, v in counts.items() if k != "no_evidence")
        struggling = int(counts.get("struggling", 0))
        if with_evidence and struggling >= T["struggling_min_students"] and struggling / with_evidence >= T["struggling_share"]:
            base["class_issues"].append({
                "code": "kc_struggling", "kc": item["kc"],
                "text_vi": f"{struggling}/{with_evidence} sinh viên có bằng chứng đang vướng ở “{item['label_vi']}”.",
                "evidence": {"struggling": struggling, "with_evidence": with_evidence},
                "suggestion_vi": "Cân nhắc giảng lại khái niệm hoặc bổ sung tài liệu cho Gia sư AI của lớp.",
                "target": "class_knowledge"})
    for b in insights.get("bottlenecks", []):
        if b["submissions"] >= T["bottleneck_min_submissions"] and b["unsuccessful_percent"] >= T["bottleneck_unsuccessful_percent"]:
            base["class_issues"].append({
                "code": "bottleneck", "exercise_id": b["exercise_id"],
                "text_vi": f"Bài “{b['title']}” có {b['unsuccessful_percent']}% lượt nộp chưa đạt ({b['submissions']} lượt).",
                "evidence": {"unsuccessful_percent": b["unsuccessful_percent"], "submissions": b["submissions"]},
                "suggestion_vi": "Xem lại đề, bài mẫu hoặc thứ tự bài (có thể thiếu bài tiên quyết).",
                "target": "edit_exercise"})
    unsucc = {b["exercise_id"]: b["unsuccessful"] for b in insights.get("bottlenecks", [])}
    for f in insights.get("failing_tests_by_exercise", []):
        tests = f.get("tests") or []
        if not tests:
            continue
        top = tests[0]
        denom = max(1, unsucc.get(f["exercise_id"], 0))
        if top["students"] >= T["failing_test_min_students"] and top["attempts"] / denom >= T["failing_test_share"]:
            base["class_issues"].append({
                "code": "failing_test", "exercise_id": f["exercise_id"],
                "text_vi": f"Ở bài “{f['title']}”, test “{top['description']}” bị sai ở {top['students']} sinh viên ({top['attempts']} lượt).",
                "evidence": {"test_idx": top["test_idx"], "students": top["students"], "attempts": top["attempts"]},
                "suggestion_vi": "Có thể là trường hợp biên mà đề chưa nói rõ; cân nhắc làm rõ đề hoặc thêm ví dụ.",
                "target": "edit_exercise"})
    for e in insights.get("error_breakdown_by_exercise", []):
        fail_n = sum(n for src in ("submit", "run") for c, n in (e.get(src) or {}).items() if c != "passed")
        fmt_n = int(e.get("format_only_submit", 0)) + int(e.get("format_only_run", 0))
        if fail_n >= T["format_only_min_attempts"] and fmt_n / fail_n >= T["format_only_share"]:
            base["class_issues"].append({
                "code": "format_mismatch", "exercise_id": e["exercise_id"],
                "text_vi": f"Ở bài “{e['title']}”, {fmt_n}/{fail_n} lượt chưa đạt chỉ sai định dạng đầu ra (thừa/thiếu khoảng trắng, hoa/thường).",
                "evidence": {"format_only": fmt_n, "unsuccessful": fail_n},
                "suggestion_vi": "Nêu rõ định dạng đầu ra mong muốn trong đề hoặc thêm ví dụ mẫu.",
                "target": "edit_exercise"})

    # --- Tiến triển tốt ---
    for e in (insights.get("process_groups") or {}).get("by_exercise", []):
        ind = int((e.get("groups") or {}).get("independent_pass", 0))
        if ind >= T["positive_min_independent"]:
            base["positives"].append({
                "code": "independent_pass", "exercise_id": e["exercise_id"],
                "text_vi": f"{ind} sinh viên đạt độc lập bài “{e.get('title') or e['exercise_id']}”.",
                "evidence": {"independent_pass": ind}})
    for item in kc.get("items", []):
        counts = item.get("students") or {}
        secure = int(counts.get("secure", 0))
        if secure >= T["positive_min_independent"]:
            base["positives"].append({
                "code": "kc_secure", "kc": item["kc"],
                "text_vi": f"{secure} sinh viên khá vững ở “{item['label_vi']}”.",
                "evidence": {"secure": secure}})
    return base


# ---------------------------------------------------------------------------
# v5.8: thẻ "Việc nên xem" (tối đa 5). Hàm thuần; ngưỡng vẫn là quy ước vận hành chưa hiệu chuẩn.
# ---------------------------------------------------------------------------
ACTION_PRIORITY = ["stuck", "failing_test", "format_mismatch", "bottleneck", "kc_struggling", "hint_dependence",
                   "practice_only"]
ACTION_TARGETS = {
    # Mọi thẻ dùng một nhãn "Xem chi tiết"; hành động tiếp theo (sửa đề, tài liệu, lộ trình) nằm trong ngăn chi tiết.
    "stuck": ("student_journey", "Xem chi tiết"),
    "failing_test": ("exercise_detail", "Xem chi tiết"),
    "format_mismatch": ("exercise_detail", "Xem chi tiết"),
    "bottleneck": ("exercise_detail", "Xem chi tiết"),
    "kc_struggling": ("concepts", "Xem chi tiết"),
    "hint_dependence": ("student_journey", "Xem chi tiết"),
    "practice_only": ("student_journey", "Xem chi tiết"),
}


def build_action_cards(overview: dict[str, Any], insights: dict[str, Any], limit: int = 5) -> dict[str, Any]:
    """Gom `overview` thành tối đa `limit` thẻ: kết luận + bằng chứng k/n + một nút hành động.

    Thẻ cấp lớp (test sai, định dạng, bài nghẽn, khái niệm) chỉ có khi `overview` đã có mục cấp lớp, tức dữ liệu đủ.
    Không xếp hạng sinh viên; danh sách sinh viên trong thẻ xếp A→Z.
    """
    overview = overview or {}
    insights = insights or {}
    matrix_ex = {e["exercise_id"]: e for e in (insights.get("matrix") or {}).get("exercises", [])}
    titles = {b["exercise_id"]: b.get("title") for b in insights.get("bottlenecks", [])}
    titles.update({eid: e.get("title") for eid, e in matrix_ex.items() if e.get("title")})
    unsucc = {b["exercise_id"]: (b["unsuccessful"], b["submissions"]) for b in insights.get("bottlenecks", [])}
    active = int((insights.get("sample") or {}).get("active_students") or 0)

    def title_of(eid: str) -> str:
        return titles.get(eid) or eid

    def act(code: str) -> dict[str, str]:
        target, label = ACTION_TARGETS[code]
        return {"target": target, "label_vi": label}

    cards: list[dict[str, Any]] = []
    attention = overview.get("attention") or []

    # Mắc kẹt: gộp theo bài.
    stuck_by_ex: dict[str, list[dict[str, str]]] = {}
    for a in attention:
        if a.get("code") != "stuck":
            continue
        for eid in (a.get("evidence") or {}).get("exercise_ids", []):
            stuck_by_ex.setdefault(eid, []).append({"username": a["student"], "full_name": a.get("student_name") or a["student"],
                                                    "exercise_id": eid})
    for eid, studs in stuck_by_ex.items():
        studs = sorted(studs, key=lambda s: (s["full_name"].casefold(), s["username"]))
        n = max(int((matrix_ex.get(eid) or {}).get("students_attempted") or 0), len(studs))
        cards.append({
            "code": "stuck", "title_vi": f"{len(studs)} SV mắc kẹt ở “{title_of(eid)}”",
            "evidence": {"k": len(studs), "n": n, "unit_vi": "SV đã thử bài này"},
            "students": studs, "exercise_id": eid, "kc": None, "action": act("stuck"),
            "_order": (ACTION_PRIORITY.index("stuck"), -len(studs), eid)})

    # Thẻ cấp lớp từ class_issues (đã rỗng khi dữ liệu chưa đủ).
    for i, issue in enumerate(overview.get("class_issues") or []):
        code = issue.get("code")
        if code not in ACTION_TARGETS:
            continue
        ev = issue.get("evidence") or {}
        eid, card = issue.get("exercise_id"), None
        if code == "failing_test":
            # Số lượt sai test gồm cả chạy thử nên không đặt trên mẫu số lượt nộp; dùng số sinh viên (k/n nhất quán).
            n_students = max(int((matrix_ex.get(eid) or {}).get("students_attempted") or 0), int(ev.get("students", 0)))
            test_desc = next((t.get("description") for f in insights.get("failing_tests_by_exercise", [])
                              if f.get("exercise_id") == eid for t in f.get("tests", []) if t.get("test_idx") == ev.get("test_idx")), None)
            card = {"title_vi": f"Test {('“' + test_desc + '”') if test_desc else '#' + str(ev.get('test_idx'))} ở “{title_of(eid)}” bị sai nhiều",
                    "evidence": {"k": int(ev.get("students", 0)), "n": n_students, "unit_vi": "SV đã thử bài bị sai test này"}}
        elif code == "format_mismatch":
            card = {"title_vi": f"“{title_of(eid)}”: nhiều lượt chỉ sai định dạng đầu ra",
                    "evidence": {"k": int(ev.get("format_only", 0)), "n": int(ev.get("unsuccessful", 0)), "unit_vi": "lượt chưa đạt (nộp + chạy thử)"}}
        elif code == "bottleneck":
            sub = int(ev.get("submissions", 0))
            card = {"title_vi": f"“{title_of(eid)}” có nhiều lượt nộp chưa đạt",
                    "evidence": {"k": unsucc.get(eid, (0, sub))[0], "n": unsucc.get(eid, (0, sub))[1] or sub, "unit_vi": "lượt nộp chưa đạt"}}
        elif code == "kc_struggling":
            label = next((it.get("label_vi") for it in (insights.get("kc_overview") or {}).get("items", [])
                          if it.get("kc") == issue.get("kc")), None) or issue.get("kc")
            card = {"title_vi": f"Nhiều SV đang vướng ở “{label}”",
                    "evidence": {"k": int(ev.get("struggling", 0)), "n": int(ev.get("with_evidence", 0)), "unit_vi": "SV có bằng chứng ở khái niệm"}}
        if card:
            card.update({"code": code, "students": [], "exercise_id": eid, "kc": issue.get("kc"), "action": act(code),
                         "text_vi": issue.get("text_vi"), "_order": (ACTION_PRIORITY.index(code), i, eid or "")})
            cards.append(card)

    # Theo từng SV nhưng gộp thành một thẻ mỗi loại.
    for code, ev_key, title in (("hint_dependence", "hint_pass_exercises", "SV đạt nhờ gợi ý từ Mức 2 ở nhiều bài"),
                                ("practice_only", "practice_only_exercises", "SV chạy thử nhiều bài nhưng chưa nộp")):
        studs = sorted(({"username": a["student"], "full_name": a.get("student_name") or a["student"],
                         "exercise_id": next(iter((a.get("evidence") or {}).get("exercise_ids") or []), None)}
                        for a in attention if a.get("code") == code), key=lambda s: (s["full_name"].casefold(), s["username"]))
        if studs:
            cards.append({"code": code, "title_vi": f"{len(studs)} {title}",
                          "evidence": {"k": len(studs), "n": max(active, len(studs)), "unit_vi": "SV có hoạt động"},
                          "students": studs, "exercise_id": None, "kc": None, "action": act(code),
                          "_order": (ACTION_PRIORITY.index(code), 0, "")})

    # v5.13: nếu `overview` đã được gắn dấu (annotate_overview), ẩn thẻ mà mọi việc trong đó đã đánh dấu.
    by_key = {i["key"]: i for f in ("attention", "class_issues") for i in overview.get(f) or [] if i.get("key")}
    hidden_cards = 0
    if by_key:
        visible = []
        for c in cards:
            keys = card_keys(c)
            for s in c.get("students") or []:
                s["key"] = f"{c['code']}:{s['username']}"
                s["mark"] = (by_key.get(s["key"]) or {}).get("mark")
            marks = [(by_key.get(k) or {}).get("mark") for k in keys]
            c["keys"] = keys
            c["open_keys"] = [k for k, m in zip(keys, marks) if not (m and m["state"] == "handled")]
            c["reopened_vi"] = next((m["follow_up_vi"] for m in marks if m and m.get("follow_up_vi")), None)
            if keys and not c["open_keys"]:
                hidden_cards += 1
                continue
            visible.append(c)
        cards = visible
    cards.sort(key=lambda c: c.pop("_order"))
    shown = cards[:limit]
    for c in shown:
        ev = c["evidence"]
        ev["show_percent"] = ev["n"] >= SHARE_PERCENT_MIN_N
    return {
        "cards": shown, "more_count": max(0, len(cards) - len(shown)), "handled_cards": hidden_cards,
        "positives": (overview.get("positives") or [])[:2],
        "priority": ACTION_PRIORITY, "limit": limit,
        "empty_vi": "Không có việc cần xử lý ngay theo quy ước hiện tại.",
        "note": "Thẻ tính lại mỗi lần mở; ngưỡng là quy ước vận hành chưa hiệu chuẩn, không xếp hạng sinh viên.",
    }


SHARE_PERCENT_MIN_N = 10  # quy ước: chỉ hiện % khi mẫu số >= 10, còn lại chỉ k/n
