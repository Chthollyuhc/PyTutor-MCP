"""v5.9 — Lời thường: câu chữ (thuần, không cần DB) và nối API (DB tạm).

Chạy: .\\.claude\\run_isolated.ps1 test_plain_language_v59
"""
import os
import unittest
from datetime import datetime

from backend.plain_language import (
    BANNED_WORDS, FEW_DATA_VI, NOTE_STUDENT_VI, build_class_plain_view, build_course_path, build_story,
    build_today_card, class_brief_line, first_name, format_when, how_it_works_vi, kc_name, story_one_liner,
)
from pytutor_shared.learner_model import build_journey_points

NOW = datetime(2026, 11, 21, 10, 0, 0)


def ev(kind, passed=0, total=5, all_passed=False, hint=0, ts="2026-11-20 09:00:00", i=1, fmt=False):
    return {"kind": kind, "passed_tests": passed, "total_tests": total, "all_passed": all_passed, "hint_level": hint,
            "timestamp": ts, "id": i, "submission_id": i if kind != "run" else None, "format_only": fmt}


def built(events):
    out = build_journey_points(events)
    return out["points"], out["summary"]


def rec(eid, title, group, passed, total, run=0, ask=0, submit=0, first_pass_at=None, attempts=None):
    return {"exercise_id": eid, "title": title, "group": group, "best": {"passed": passed, "total": total},
            "counts": {"run": run, "ask": ask, "submit": submit}, "first_pass_at": first_pass_at,
            "attempts_to_first_pass": attempts, "points": []}


def today(**kw):
    base = {"full_name": None, "concepts": [], "next_practice": None, "week": {"this": 0, "prev": 0},
            "recent": [], "path": None, "now": NOW}
    base.update(kw)
    return build_today_card(**base)


def collect_vi(obj, out):
    """Gom mọi chuỗi nằm dưới khóa kết thúc bằng _vi (chuỗi, danh sách chuỗi, hoặc dict chuỗi)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.endswith("_vi"):
                if isinstance(v, str):
                    out.append(v)
                elif isinstance(v, list):
                    out.extend(x for x in v if isinstance(x, str))
                elif isinstance(v, dict):
                    out.extend(x for x in v.values() if isinstance(x, str))
            collect_vi(v, out)
    elif isinstance(obj, list):
        for x in obj:
            collect_vi(x, out)
    return out


EX = [{"exercise_id": "e1", "title": "In tam giác", "order_idx": 1, "students_passed": 3, "students_attempted": 5,
       "students_enrolled": 6},
      {"exercise_id": "e2", "title": "Số nguyên tố", "order_idx": 2, "students_passed": 2, "students_attempted": 4,
       "students_enrolled": 6}]
ROWS = [  # cố ý không theo A→Z để kiểm tra hàm tự sắp xếp
    {"username": "u_khoa", "full_name": "Khoa", "cells": {"e1": None, "e2": None}},
    {"username": "u_an", "full_name": "An", "cells": {"e1": "independent_pass", "e2": "stuck"}},
    {"username": "u_binh", "full_name": "Bình", "cells": {"e1": "practice_only", "e2": "practice_only"}},
    {"username": "u_chi", "full_name": "Chi", "cells": {"e1": "in_progress", "e2": None}},
    {"username": "u_dung", "full_name": "Dũng", "cells": {"e1": "hint_pass", "e2": "hint_pass"}},
    {"username": "u_ha", "full_name": "Hà", "cells": {"e1": "independent_pass", "e2": "retry_pass"}},
]
OVERVIEW = {"attention": [{"code": "stuck", "student": "u_an"}, {"code": "hint_dependence", "student": "u_dung"},
                          {"code": "practice_only", "student": "u_binh"}], "class_issues": []}


def make_insights(status="sufficient", rows=ROWS):
    return {
        "data_status": status,
        "matrix": {"exercises": EX, "rows": rows},
        "daily_trend": [{"date": "2026-11-20", "active_students": 4, "first_passes": 3},
                        {"date": "2026-11-21", "active_students": 3, "first_passes": 2}],
        "failing_tests_by_exercise": [{"exercise_id": "e2", "title": "Số nguyên tố", "tests": [
            {"test_idx": 3, "description": "n = 1", "input": "1", "attempts": 6, "students": 3, "format_attempts": 0}]}],
        "error_breakdown_by_exercise": [{"exercise_id": "e1", "title": "In tam giác",
                                         "submit": {"logic_partial": 2, "passed": 3}, "run": {"logic_partial": 2},
                                         "format_only_submit": 1, "format_only_run": 1}],
        "time_to_pass_by_exercise": [{"exercise_id": "e1", "median_minutes": 12.4, "n": 3},
                                     {"exercise_id": "e2", "median_minutes": 0.5, "n": 1}],
        "bottlenecks": [{"exercise_id": "e2", "unsuccessful": 5}, {"exercise_id": "e1", "unsuccessful": 2}],
        "kc_overview": {"items": [
            {"kc": "loop", "label_vi": "Vòng lặp",
             "students": {"secure": 3, "developing": 1, "struggling": 0, "no_evidence": 2}},
            {"kc": "recursion", "label_vi": "Đệ quy",
             "students": {"secure": 0, "developing": 1, "struggling": 2, "no_evidence": 3}}]},
    }


class JourneyPointsKeysTests(unittest.TestCase):
    def test_first_pass_keys(self):
        _, s = built([ev("run", 1, i=1, ts="2026-11-20 09:00:00"), ev("run", 2, i=2, ts="2026-11-20 09:01:00"),
                      ev("submit", 5, all_passed=True, i=3, ts="2026-11-20 09:02:00")])
        self.assertEqual((s["first_pass_at"], s["attempts_to_first_pass"]), ("2026-11-20 09:02:00", 3))
        _, s2 = built([ev("run", 1)])
        self.assertEqual((s2["first_pass_at"], s2["attempts_to_first_pass"]), (None, None))


class TodayCardTests(unittest.TestCase):
    def test_names_and_time(self):
        self.assertEqual(first_name("Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)"), "Khánh")
        self.assertEqual(first_name("SV An (giả lập)"), "An")
        self.assertIsNone(first_name(""))
        self.assertEqual(today(full_name="Trần Minh Khánh")["greeting_vi"], "Chào Khánh")
        self.assertEqual(today()["greeting_vi"], "Chào bạn")
        self.assertEqual(format_when("2026-11-20 09:05:33"), "20/11 09:05")
        self.assertEqual(format_when("2026-11-20T09:05:33"), "20/11 09:05")
        self.assertIsNone(format_when("không phải ngày"))
        self.assertEqual(kc_name("custom_kc", "Tên riêng"), "Tên riêng")

    def test_no_activity(self):
        t = today()
        self.assertEqual(t["headline_vi"], "Chào mừng bạn! Hãy bắt đầu với bài đầu tiên.")
        self.assertEqual(t["moments"], [])
        self.assertIsNone(t["next_step"])
        self.assertIsNone(t["skills_vi"])
        self.assertEqual(t["note_vi"], NOTE_STUDENT_VI)

    def test_headline_week_and_near(self):
        near = [rec("e1", "Tổng số chẵn", "in_progress", 4, 5, run=3, submit=1)]
        t = today(week={"this": 2, "prev": 1}, recent=near)
        self.assertEqual(t["headline_vi"], "Tuần này bạn làm đúng 2 bài mới, nhiều hơn tuần trước 1 bài.")
        self.assertEqual(t["next_step"], {"exercise_id": "e1", "title": "Tổng số chẵn", "button_vi": "Làm tiếp",
                                          "reason_vi": "Lần trước bạn đã đúng 4 trên 5 trường hợp. Sửa thêm một chút là xong."})
        self.assertEqual(today(week={"this": 1, "prev": 1}, recent=near)["headline_vi"],
                         "Tuần này bạn làm đúng 1 bài mới, đều tay như tuần trước.")
        self.assertEqual(today(week={"this": 1, "prev": 3}, recent=near)["headline_vi"], "Tuần này bạn làm đúng 1 bài mới.")
        stuck_near = [rec("e1", "Tổng số chẵn", "stuck", 3, 5, run=8, submit=2)]
        self.assertEqual(today(recent=stuck_near)["headline_vi"],
                         "Bạn sắp xong bài Tổng số chẵn rồi: đã đúng 3 trên 5 trường hợp.")
        far = [rec("e2", "Đệ quy", "in_progress", 1, 5, run=2)]
        self.assertEqual(today(recent=far)["headline_vi"], "Sẵn sàng làm tiếp chưa? Bài tiếp theo đang chờ bạn.")

    def test_moments(self):
        r = [rec("e3", "Số nguyên tố", "retry_pass", 5, 5, run=5, submit=2, first_pass_at="2026-11-20 09:00:00", attempts=7),
             rec("e4", "In tam giác", "independent_pass", 4, 4, run=1, submit=1, first_pass_at="2026-11-19 09:00:00",
                 attempts=2)]
        self.assertEqual([m["text_vi"] for m in today(recent=r)["moments"]],
                         ["Bạn không bỏ cuộc: bài Số nguyên tố đúng hết sau 7 lần thử.",
                          "Bạn tự làm đúng bài In tam giác chỉ sau vài lần thử."])
        old = [rec("e3", "Số nguyên tố", "retry_pass", 5, 5, run=5, submit=2, first_pass_at="2026-11-10 09:00:00",
                   attempts=7)]
        self.assertEqual(today(recent=old)["moments"], [])
        loop = [{"kc": "loop", "label_vi": "Vòng lặp", "state": "secure",
                 "exercise_details": [{"exercise_id": "e4", "status": "passed"}]}]
        moments = today(recent=r[1:], concepts=loop)["moments"]
        self.assertEqual([m["kind"] for m in moments], ["independent", "new_skill"])
        self.assertEqual(moments[1]["text_vi"], "Bạn đã làm tốt phần Vòng lặp rồi.")

    def test_next_step_branches(self):
        acc = [{"kc": "accumulator", "label_vi": "Biến tích lũy", "state": "struggling",
                "exercise_details": [{"exercise_id": "e5", "title": "Tổng các số", "status": "struggling"}]}]
        far = [rec("e5", "Tổng các số", "in_progress", 1, 5, run=2, submit=2)]
        self.assertEqual(today(concepts=acc, recent=far)["next_step"],
                         {"exercise_id": "e5", "title": "Tổng các số", "button_vi": "Luyện bài này",
                          "reason_vi": "Bài này giúp bạn luyện thêm phần Cộng dồn trong vòng lặp."})
        for code, button, reason in (
            ("next_unattempted", "Bắt đầu", "Đây là bài tiếp theo bạn chưa làm."),
            ("retry_for_autonomy", "Làm lại", "Bạn đã xong bài này nhờ gợi ý. Thử tự làm lại để chắc tay hơn."),
            ("in_progress", "Làm tiếp", "Bạn đã nộp bài này nhưng chưa đúng hết. Sửa thêm một chút nhé."),
            ("unresolved_recurring", "Làm tiếp", "Bạn đã thử bài này vài lần mà chưa xong. Thử lại với cách nghĩ mới nhé."),
            ("khac", "Làm tiếp", "Đây là bài nên làm tiếp."),
        ):
            step = today(recent=far, next_practice={"exercise_id": "e6", "title": "Bài mới", "reason_code": code})["next_step"]
            self.assertEqual((step["button_vi"], step["reason_vi"]), (button, reason))

    def test_skills_line(self):
        cs = [{"kc": "io_format", "state": "secure"}, {"kc": "loop", "state": "secure"},
              {"kc": "conditional", "state": "developing"}, {"kc": "recursion", "state": "struggling"},
              {"kc": "string", "state": "no_evidence"}]
        self.assertEqual(today(concepts=cs, recent=[rec("e1", "A", "in_progress", 0, 5, run=1)])["skills_vi"],
                         "Bạn làm tốt: In và nhập dữ liệu, Vòng lặp · Đang luyện: Câu lệnh if · Nên luyện thêm: Đệ quy")

    def test_course_path(self):
        rows = [{"exercise_id": "a", "title": "A", "order_idx": 1, "status": "MASTERED", "stars_earned": 3},
                {"exercise_id": "b", "title": "B", "order_idx": 2, "status": "MASTERED", "stars_earned": 2},
                {"exercise_id": "c", "title": "C", "order_idx": 3, "status": "IN_PROGRESS"},
                {"exercise_id": "d", "title": "D", "order_idx": 4, "status": "AVAILABLE"},
                {"exercise_id": "e", "title": "E", "order_idx": 5, "status": "LOCKED"}]
        p = build_course_path(rows, "cls", "Python K65")
        self.assertEqual([s["kind"] for s in p["steps"]], ["done", "done", "current", "open", "locked"])
        self.assertEqual([s["stars"] for s in p["steps"]], [3, 2, 0, 0, 0])
        self.assertEqual((p["remaining"], p["caption_vi"]), (3, "Còn 3 bài nữa là xong học phần."))
        rows[2]["status"] = "AVAILABLE"
        self.assertEqual([s["kind"] for s in build_course_path(rows, "cls", "Python K65")["steps"]],
                         ["done", "done", "current", "open", "locked"])
        self.assertEqual(build_course_path(rows[:2], "cls", "Python K65")["caption_vi"], "Bạn đã xong cả 2 bài của học phần.")
        self.assertIsNone(build_course_path([], "cls", "x"))


class StoryTests(unittest.TestCase):
    def test_passed_after_tries_and_steps(self):
        pts, summ = built([ev("run", 1, ts="2026-11-20 09:00:00", i=1), ev("run", 3, ts="2026-11-20 09:05:00", i=2),
                           ev("ask", hint=1, ts="2026-11-20 09:06:00", i=3),
                           ev("submit", 5, all_passed=True, ts="2026-11-20 09:10:00", i=4)])
        pts[-1]["code"] = "print(1)"
        s = build_story(pts, summ)
        self.assertEqual(s["summary_vi"], "Bạn thử 3 lần rồi làm đúng hết.")
        self.assertEqual([x["text_vi"] for x in s["steps"]],
                         ["Chạy thử: đúng 1 trên 5", "Chạy thử: đúng 3 trên 5", "Hỏi Gia sư AI, gợi ý mức 1",
                          "Nộp bài: đúng hết"])
        self.assertEqual([x["tag_vi"] for x in s["steps"]], [None, "Đúng thêm", None, None])
        self.assertEqual(s["steps"][3]["tone"], "done")
        self.assertEqual(s["steps"][0]["when_vi"], "20/11 09:00")
        self.assertEqual(s["steps"][3]["code"], "print(1)")
        self.assertNotIn("code", s["steps"][0])
        self.assertEqual(s["visible_from"], 0)
        t = build_story(pts, summ, audience="teacher", student_name="An")
        self.assertEqual(t["summary_vi"], "An thử 3 lần rồi làm đúng hết. Đã hỏi Gia sư AI 1 lần.")

    def test_other_branches(self):
        cases = [
            ([ev("submit", 4, total=4, all_passed=True)], "Bạn làm đúng ngay lần đầu."),
            ([ev("ask", hint=2)], "Bạn đã xem gợi ý nhưng chưa chạy thử. Bấm “Chạy thử” để xem kết quả."),
            ([ev("run", 1, i=1), ev("run", 2, i=2)],
             "Bạn đã chạy thử 2 lần, tốt nhất đúng 2 trên 5 trường hợp. Khi thấy ổn, bấm “Nộp bài” nhé."),
            ([ev("run", 1, i=1), ev("submit", 2, i=2)],
             "Bạn đã thử 2 lần, tốt nhất đúng 2 trên 5 trường hợp. Sửa từng chỗ một nhé."),
        ]
        for events, expected in cases:
            self.assertEqual(build_story(*built(events))["summary_vi"], expected)
        self.assertEqual(build_story([], {})["summary_vi"], "Bạn chưa làm bài này. Bấm “Chạy thử” để bắt đầu.")
        self.assertEqual(build_story([], {}, audience="teacher", student_name="An")["summary_vi"],
                         "An chưa làm bài này trong khoảng thời gian đang xem.")

    def test_stuck_and_condense(self):
        events = [ev("run", 2, i=k, ts=f"2026-11-20 09:0{k}:00") for k in range(8)] + \
                 [ev("submit", 2, i=20, ts="2026-11-20 09:30:00")]
        pts, summ = built(events)
        self.assertEqual(summ["group"], "stuck")
        s = build_story(pts, summ)
        self.assertEqual(s["summary_vi"], "Bạn đã thử 9 lần, tốt nhất đúng 2 trên 5 trường hợp. Mấy lần gần đây chưa đúng "
                                          "thêm. Thử bấm “Chạy từng bước” để xem code chạy thế nào, hoặc hỏi Gia sư AI.")
        self.assertEqual([x["text_vi"] for x in s["steps"]], ["Chạy thử 8 lần: tốt nhất đúng 2 trên 5", "Nộp bài: đúng 2 trên 5"])
        self.assertEqual([x["tag_vi"] for x in s["steps"]], [None, None])
        t = build_story(pts, summ, audience="teacher", student_name="An")
        self.assertEqual(t["summary_vi"], "An đã thử 9 lần, tốt nhất đúng 2 trên 5 trường hợp. Mấy lần gần đây chưa đúng "
                                          "thêm, bạn ấy có thể cần được hỏi thăm.")

    def test_format_tag_visible_from_and_one_liner(self):
        s = build_story(*built([ev("submit", 3, total=4, fmt=True)]))
        self.assertEqual(s["steps"][0]["tag_vi"], "Chỉ sai cách in kết quả")
        many = []
        for k in range(5):
            many += [ev("run", 1, i=2 * k, ts=f"2026-11-20 10:{k}0:00"),
                     ev("submit", 1, i=2 * k + 1, ts=f"2026-11-20 10:{k}5:00")]
        self.assertEqual(build_story(*built(many))["visible_from"], 2)
        self.assertEqual(story_one_liner(rec("e", "A", "retry_pass", 5, 5)), "Đã làm đúng hết.")
        self.assertEqual(story_one_liner(rec("e", "A", "practice_only", 2, 5, run=3)), "Đã chạy thử 3 lần, chưa nộp bài.")
        self.assertEqual(story_one_liner(rec("e", "A", "in_progress", 2, 5, run=1, submit=1)),
                         "Đang làm: tốt nhất đúng 2 trên 5 trường hợp.")


class ClassPlainTests(unittest.TestCase):
    def test_groups(self):
        g = build_class_plain_view(make_insights(), OVERVIEW, 7)["groups"]
        self.assertEqual([p["username"] for p in g["check_in"]], ["u_an"])
        self.assertEqual(g["check_in"][0]["reason_vi"],
                         "Đang gặp khó ở bài Số nguyên tố: thử nhiều lần mà mấy lần gần đây chưa đúng thêm.")
        self.assertEqual(g["check_in"][0]["exercise_id"], "e2")
        self.assertEqual([(p["username"], p["reason_vi"]) for p in g["trying"]], [
            ("u_binh", "Đã chạy thử 2 bài nhưng chưa nộp bài nào."),
            ("u_chi", "Đang làm 1 bài, chưa có bài nào đúng hết."),
            ("u_dung", "Có 2 bài làm đúng nhờ gợi ý mức 2 hoặc 3."),
        ])
        self.assertEqual([p["username"] for p in g["doing_well"]], ["u_ha"])
        self.assertEqual([p["username"] for p in g["not_started"]], ["u_khoa"])

    def test_exercises_and_hardest(self):
        ex = build_class_plain_view(make_insights(), OVERVIEW, 7)["exercises"]
        self.assertEqual(ex[0]["done_vi"], "3 trong 6 bạn đã làm xong, 2 bạn đang làm.")
        self.assertEqual(ex[0]["mistake_vi"],
                         "Nhiều bạn làm đúng ý nhưng in sai cách trình bày (thừa dấu cách hoặc sai chữ hoa, chữ thường).")
        self.assertNotIn("time_vi", ex[0])  # không đưa thời gian làm bài vào câu chữ
        self.assertEqual(ex[1]["mistake_vi"], "Nhiều bạn sai ở trường hợp “n = 1” (ví dụ đầu vào: 1).")
        self.assertEqual([e["hardest"] for e in ex], [False, True])

    def test_brief_and_skills(self):
        v = build_class_plain_view(make_insights(), OVERVIEW, 7)
        self.assertEqual(v["brief_vi"], [
            "Tuần này có 5 trong 6 bạn vào làm bài, làm đúng thêm 5 bài.",
            "Nhiều bạn vẫn đang cố gắng.",
            "1 bạn nên được hỏi thăm: An.",
            "Bài khó nhất lúc này: Số nguyên tố. Nhiều bạn sai ở trường hợp “n = 1” (ví dụ đầu vào: 1).",
            "1 bạn chưa bắt đầu trong tuần này.",
        ])
        self.assertEqual(v["skills_vi"], ["Phần lớn các bạn làm tốt: Vòng lặp.",
                                          "Nên ôn lại trên lớp: Đệ quy (2 bạn cần luyện thêm)."])
        self.assertIsNone(v["few_data_vi"])
        self.assertEqual(build_class_plain_view(make_insights("limited"), OVERVIEW, 7)["few_data_vi"], FEW_DATA_VI)
        self.assertEqual(class_brief_line(v), "1 bạn nên hỏi thăm · bài khó: Số nguyên tố")
        v14 = build_class_plain_view(make_insights(), OVERVIEW, 14)
        self.assertTrue(v14["brief_vi"][0].startswith("Trong 14 ngày qua có 5 trong 6 bạn"))
        self.assertEqual(v14["brief_vi"][-1], "1 bạn chưa bắt đầu trong 14 ngày qua.")

    def test_wording_edge_cases(self):
        # Tên bài kết thúc bằng "!" không sinh ra ".!." ở câu bài khó nhất.
        ins = make_insights()
        ins["matrix"]["exercises"][1]["title"] = "Tính giai thừa n!"
        v = build_class_plain_view(ins, OVERVIEW, 7)
        self.assertIn("Bài khó nhất lúc này: Tính giai thừa n! Nhiều bạn", v["brief_vi"][3])
        self.assertNotIn(".!", " ".join(v["brief_vi"]))
        # Kỹ năng đã nằm ở câu "làm tốt" thì không lặp ở câu "nên ôn lại".
        ins2 = make_insights()
        ins2["kc_overview"]["items"][0]["students"] = {"secure": 3, "developing": 0, "struggling": 2, "no_evidence": 1}
        skills = build_class_plain_view(ins2, OVERVIEW, 7)["skills_vi"]
        self.assertEqual(skills[0], "Phần lớn các bạn làm tốt: Vòng lặp.")
        self.assertTrue(all("Vòng lặp" not in x for x in skills[1:]))

    def test_no_activity(self):
        empty_rows = [{"username": "u1", "full_name": "An", "cells": {"e1": None, "e2": None}}]
        v = build_class_plain_view(make_insights(rows=empty_rows), {"attention": []}, 7)
        self.assertEqual(v["brief_vi"], ["Tuần này chưa có bạn nào vào làm bài."])
        self.assertEqual(v["active"], 0)
        self.assertIsNone(v["few_data_vi"])
        self.assertEqual(class_brief_line(v), "Chưa có hoạt động trong 7 ngày qua.")

    def test_how_it_works_uses_constants(self):
        rules = how_it_works_vi()
        self.assertIn("từ 8 lần trở lên", rules[0])
        self.assertIn("5 lần gần nhất", rules[0])


class BannedWordsTests(unittest.TestCase):
    def test_all_generated_text_is_plain(self):
        texts: list = []
        r = [rec("e1", "Tổng số chẵn", "in_progress", 4, 5, run=3, submit=1),
             rec("e3", "Số nguyên tố", "retry_pass", 5, 5, run=5, submit=2, first_pass_at="2026-11-20 09:00:00", attempts=7),
             rec("e4", "In tam giác", "independent_pass", 4, 4, run=1, submit=1, first_pass_at="2026-11-19 09:00:00",
                 attempts=2)]
        cs = [{"kc": k, "state": s, "exercise_details": [{"exercise_id": "e4", "title": "In tam giác", "status": "struggling"}]}
              for k, s in (("io_format", "secure"), ("loop", "developing"), ("recursion", "struggling"))]
        path = build_course_path([{"exercise_id": "a", "title": "A", "order_idx": 1, "status": "MASTERED", "stars_earned": 3},
                                  {"exercise_id": "b", "title": "B", "order_idx": 2, "status": "AVAILABLE"}], "cls", "Python")
        variants = [{}, {"week": {"this": 2, "prev": 1}, "recent": r, "concepts": cs, "path": path},
                    {"week": {"this": 1, "prev": 1}, "recent": r[:1]}, {"recent": r[:1]}]
        for code in ("next_unattempted", "retry_for_autonomy", "in_progress", "unresolved_recurring", None):
            variants.append({"recent": [rec("e9", "Bài khác", "in_progress", 0, 5, run=1)],
                             "next_practice": {"exercise_id": "e6", "title": "Bài mới", "reason_code": code}})
        for kw in variants:
            collect_vi(today(**kw), texts)
        story_events = [
            [ev("run", 1, i=1), ev("run", 3, i=2), ev("ask", hint=1, i=3), ev("submit", 5, all_passed=True, i=4)],
            [ev("ask", hint=2)], [ev("run", 1, i=1), ev("run", 2, i=2)], [ev("submit", 3, total=4, fmt=True)],
            [ev("run", 2, i=k) for k in range(8)] + [ev("submit", 2, i=20)],
        ]
        for events in story_events:
            for audience in ("student", "teacher"):
                collect_vi(build_story(*built(events), audience=audience, student_name="An"), texts)
        texts.extend(story_one_liner(item) for item in r)
        for days in (7, 14):
            collect_vi(build_class_plain_view(make_insights(), OVERVIEW, days), texts)
        collect_vi(build_class_plain_view(make_insights("limited"), OVERVIEW, 7), texts)
        texts.append(class_brief_line(build_class_plain_view(make_insights(), OVERVIEW, 7)))
        texts.extend(how_it_works_vi())
        self.assertGreater(len(texts), 40)
        for t in texts:
            low = f" {t.lower()} "
            for w in BANNED_WORDS:
                self.assertNotIn(w, low, f"“{t}” chứa từ cấm “{w}”")


@unittest.skipUnless(os.environ.get("PYTUTOR_DB_PATH"), "cần PYTUTOR_DB_PATH (DB tạm)")
class PlainIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from backend import database as db
        from seed.seed_demo_class_v58 import CLASS_ID, build_demo_class
        cls.db, cls.class_id = db, CLASS_ID
        cls.info = build_demo_class(db)
        cls.ex = cls.info["exercise_ids"]

    def h(self, user, role, name=None):
        from backend.auth import create_token
        return {"Authorization": f"Bearer {create_token(user, role, name or user)}"}

    def client(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    def test_student_today_story_and_path(self):
        with self.client() as c:
            r = c.get(f"/api/student/journey?class_id={self.class_id}&exercise_id={self.ex[0]}",
                      headers=self.h("v58_binh", "student", "SV Bình (giả lập)"))
            self.assertEqual(r.status_code, 200, r.text)
            body = r.json()
            card = body["today"]
            self.assertEqual(card["greeting_vi"], "Chào Bình")
            self.assertEqual(card["path"]["class_id"], self.class_id)
            self.assertEqual(len(card["path"]["steps"]), len(self.ex))
            self.assertEqual(card["note_vi"], NOTE_STUDENT_VI)
            self.assertTrue(body["current"]["story"]["steps"])
            self.assertTrue(any(s.get("code") for s in body["current"]["story"]["steps"] if s["kind"] == "submit"))
            self.assertTrue(all(isinstance(e.get("story_vi"), str) for e in body["recent_exercises"]))
            self.assertIn("headline", body)  # khóa cũ v5.8 vẫn còn
            portal = c.get("/api/student/journey", headers=self.h("v58_binh", "student")).json()
            self.assertEqual(portal["today"]["path"]["class_id"], self.class_id)

    def test_instructor_plain_view_consistent(self):
        with self.client() as c:
            body = c.get(f"/api/instructor/classes/{self.class_id}/insights?days=30",
                         headers=self.h("gv_tran", "instructor")).json()
        plain = body["plain"]
        need = {s["username"] for s in body["students"] if s["needs_support"]}
        self.assertEqual({p["username"] for p in plain["groups"]["check_in"]}, need)
        everyone = [p["username"] for k in ("check_in", "trying", "doing_well", "not_started") for p in plain["groups"][k]]
        self.assertEqual(sorted(everyone), sorted(r["username"] for r in body["matrix"]["rows"]))
        self.assertEqual(len(everyone), len(set(everyone)))
        self.assertEqual(len(plain["exercises"]), len(self.ex))
        self.assertTrue(plain["brief_vi"])
        self.assertIn("action_cards", body)  # khóa cũ v5.8 vẫn còn

    def test_instructor_story_has_no_code(self):
        with self.client() as c:
            body = c.get(f"/api/instructor/classes/{self.class_id}/insights?days=30",
                         headers=self.h("gv_tran", "instructor")).json()
            target = (body["plain"]["groups"]["check_in"] or body["plain"]["groups"]["trying"])[0]
            r = c.get(f"/api/instructor/classes/{self.class_id}/students/{target['username']}"
                      f"/exercises/{target['exercise_id']}/journey?days=30", headers=self.h("gv_tran", "instructor"))
            self.assertEqual(r.status_code, 200, r.text)
            story = r.json()["story"]
            self.assertTrue(story["summary_vi"])
            self.assertFalse(any("code" in s for s in story["steps"]))

    def test_classes_attention_brief(self):
        with self.client() as c:
            rows = c.get("/api/instructor/classes-attention", headers=self.h("gv_tran", "instructor")).json()["classes"]
        demo = next(r for r in rows if r["id"] == self.class_id)
        self.assertIsInstance(demo["brief_vi"], str)
        self.assertIn("check_in", demo)


if __name__ == "__main__":
    unittest.main()
