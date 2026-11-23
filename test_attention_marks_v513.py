"""v5.13: dấu "đã xử lý / không cần" cho việc nên xem. Phần thuần không cần DB; phần tích hợp cần DB tạm
(.\\.claude\\run_isolated.ps1 test_attention_marks_v513) và tự dựng lớp mẫu v5.8."""
from __future__ import annotations

import os
import unittest
from datetime import datetime, timedelta

from backend.attention_marks import (
    MARK_VALIDITY_DAYS, annotate_overview, annotate_plain_groups, card_keys, current_signatures, evaluate_mark,
    handled_keys, item_key, item_signature,
)
from backend.class_overview import build_action_cards
from backend.plain_language import BANNED_WORDS, class_brief_line

NOW = datetime(2026, 11, 24, 10, 0, 0)


def ts(days_ago: float) -> str:
    return (NOW - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")


def mark(status="handled", signature="e1", days_ago=1):
    return {"status": status, "signature": signature, "marked_at": ts(days_ago), "marked_by": "gv"}


def stuck(user, ids=("e1",)):
    return {"code": "stuck", "student": user, "student_name": user.upper(), "evidence": {"exercise_ids": list(ids)},
            "text_vi": f"{user} đang kẹt."}


def issue(code="bottleneck", eid="e1"):
    return {"code": code, "exercise_id": eid, "evidence": {}, "text_vi": f"Bài {eid} có nhiều lượt chưa đạt."}


class KeyAndSignatureTests(unittest.TestCase):
    def test_keys(self):
        self.assertEqual(item_key(stuck("an")), "stuck:an")
        self.assertEqual(item_key(issue("failing_test", "e2")), "failing_test:e2")
        self.assertEqual(item_key({"code": "kc_struggling", "kc": "loops"}), "kc_struggling:loops")

    def test_signature_is_sorted_exercise_set_for_student_items_only(self):
        self.assertEqual(item_signature(stuck("an", ("e2", "e1", "e2"))), "e1,e2")
        self.assertEqual(item_signature(issue()), "")


class EvaluateMarkTests(unittest.TestCase):
    def test_no_mark(self):
        self.assertIsNone(evaluate_mark(None, "e1", NOW))
        self.assertIsNone(evaluate_mark({"status": "weird", "signature": "", "marked_at": ts(0)}, "e1", NOW))

    def test_handled_within_window_same_situation(self):
        r = evaluate_mark(mark(days_ago=MARK_VALIDITY_DAYS - 1), "e1", NOW)
        self.assertEqual((r["state"], r["reason"], r["follow_up_vi"]), ("handled", None, None))

    def test_subset_of_marked_exercises_stays_handled(self):
        self.assertEqual(evaluate_mark(mark(signature="e1,e2"), "e1", NOW)["state"], "handled")

    def test_new_exercise_reopens(self):
        r = evaluate_mark(mark(signature="e1"), "e1,e2", NOW)
        self.assertEqual((r["state"], r["reason"]), ("reopened", "changed"))
        self.assertIn("thay đổi", r["follow_up_vi"])

    def test_handled_expires_but_dismissed_does_not(self):
        old = MARK_VALIDITY_DAYS + 1
        h = evaluate_mark(mark("handled", days_ago=old), "e1", NOW)
        self.assertEqual((h["state"], h["reason"]), ("reopened", "expired"))
        self.assertIn("vẫn còn", h["follow_up_vi"])
        self.assertIn(ts(old)[8:10] + "/" + ts(old)[5:7], h["follow_up_vi"])
        self.assertEqual(evaluate_mark(mark("dismissed", days_ago=old), "e1", NOW)["state"], "handled")
        self.assertEqual(evaluate_mark(mark("dismissed", days_ago=old), "e1,e2", NOW)["reason"], "changed")

    def test_unparseable_time_treated_as_expired(self):
        m = mark()
        m["marked_at"] = "không rõ"
        self.assertEqual(evaluate_mark(m, "e1", NOW)["reason"], "expired")

    def test_follow_up_text_has_no_banned_words(self):
        for m, sig in ((mark(days_ago=9), "e1"), (mark(), "e1,e2"), (mark("dismissed"), "e1,e3")):
            text = evaluate_mark(m, sig, NOW)["follow_up_vi"].lower()
            for w in BANNED_WORDS:
                self.assertNotIn(w, text, w)


class OverviewAnnotationTests(unittest.TestCase):
    def make(self):
        return {"attention": [stuck("an"), stuck("binh"), {**stuck("chi"), "code": "practice_only"}],
                "class_issues": [issue("bottleneck", "e1")]}

    def test_counts_exclude_handled(self):
        ov = self.make()
        marks = {"stuck:an": mark(), "bottleneck:e1": mark("dismissed")}
        annotate_overview(ov, marks, NOW)
        self.assertEqual(ov["open_counts"], {"attention": 2, "issues": 0, "handled": 2, "open": 2})
        self.assertEqual(handled_keys(ov), {"stuck:an", "bottleneck:e1"})

    def test_reopened_items_count_as_open(self):
        ov = self.make()
        annotate_overview(ov, {"stuck:an": mark(days_ago=20)}, NOW)
        self.assertEqual(ov["open_counts"]["attention"], 3)
        self.assertEqual(ov["attention"][0]["mark"]["state"], "reopened")

    def test_current_signatures_only_existing_items(self):
        sigs = current_signatures(self.make())
        self.assertEqual(sigs["stuck:an"], "e1")
        self.assertNotIn("stuck:nobody", sigs)

    def test_plain_groups_count_open_check_in(self):
        ov = self.make()
        annotate_overview(ov, {"stuck:an": mark()}, NOW)
        plain = {"groups": {"check_in": [{"username": "an"}, {"username": "binh"}, {"username": "ghost"}]}}
        self.assertEqual(annotate_plain_groups(plain, ov), 2)  # binh + ghost (không có việc tương ứng → vẫn tính là mở)
        g = plain["groups"]["check_in"]
        self.assertEqual(g[0]["key"], "stuck:an")
        self.assertEqual(g[0]["mark"]["state"], "handled")
        self.assertNotIn("key", g[2])  # không có việc `stuck` tương ứng → không có nút đánh dấu


class ActionCardTests(unittest.TestCase):
    def insights(self):
        return {"matrix": {"exercises": [{"exercise_id": "e1", "title": "Bài 1", "students_attempted": 4}]},
                "bottlenecks": [{"exercise_id": "e1", "title": "Bài 1", "submissions": 8, "unsuccessful": 6,
                                 "unsuccessful_percent": 75.0}],
                "sample": {"active_students": 4}}

    def overview(self):
        return {"attention": [stuck("an"), stuck("binh")], "class_issues": [issue("bottleneck", "e1")], "positives": []}

    def test_card_keys(self):
        ov = self.overview()
        annotate_overview(ov, {}, NOW)
        cards = build_action_cards(ov, self.insights())["cards"]
        by_code = {c["code"]: c for c in cards}
        self.assertEqual(sorted(card_keys(by_code["stuck"])), ["stuck:an", "stuck:binh"])
        self.assertEqual(card_keys(by_code["bottleneck"]), ["bottleneck:e1"])

    def test_unmarked_overview_is_unchanged_behaviour(self):
        out = build_action_cards(self.overview(), self.insights())  # chưa annotate → không có khóa, không ẩn thẻ gì
        self.assertEqual(out["handled_cards"], 0)
        self.assertEqual(len(out["cards"]), 2)
        self.assertNotIn("open_keys", out["cards"][0])

    def test_card_hidden_only_when_every_item_handled(self):
        ov = self.overview()
        annotate_overview(ov, {"stuck:an": mark()}, NOW)
        out = build_action_cards(ov, self.insights())
        stuck_card = next(c for c in out["cards"] if c["code"] == "stuck")
        self.assertEqual(stuck_card["open_keys"], ["stuck:binh"])  # còn một bạn chưa đánh dấu → thẻ vẫn hiện
        self.assertEqual(out["handled_cards"], 0)
        ov2 = self.overview()
        annotate_overview(ov2, {"stuck:an": mark(), "stuck:binh": mark(), "bottleneck:e1": mark("dismissed")}, NOW)
        out2 = build_action_cards(ov2, self.insights())
        self.assertEqual(out2["cards"], [])
        self.assertEqual(out2["handled_cards"], 2)

    def test_reopened_note_on_card(self):
        ov = self.overview()
        annotate_overview(ov, {"stuck:an": mark(days_ago=10)}, NOW)
        card = next(c for c in build_action_cards(ov, self.insights())["cards"] if c["code"] == "stuck")
        self.assertIn("vẫn còn", card["reopened_vi"])


class BriefLineTests(unittest.TestCase):
    PLAIN = {"active": 3, "days": 7, "groups": {"check_in": [{"username": "x"}]}, "exercises": []}

    def test_default_unchanged(self):
        self.assertEqual(class_brief_line(self.PLAIN), "1 bạn nên hỏi thăm")

    def test_open_check_in_overrides_total_check_in(self):
        self.assertEqual(class_brief_line(self.PLAIN, open_total=1, check_in_open=0), "1 việc nên xem")

    def test_all_handled(self):
        self.assertEqual(class_brief_line(self.PLAIN, open_total=0, check_in_open=0), "Chưa có bạn nào cần hỏi thăm")


@unittest.skipUnless(os.getenv("PYTUTOR_DB_PATH"), "cần DB tạm: dùng .claude/run_isolated.ps1")
class MarksIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from backend import database as db
        from seed.seed_demo_class_v58 import CLASS_ID, build_demo_class
        cls.db, cls.class_id = db, CLASS_ID
        build_demo_class(db)

    def setUp(self):
        self.db.clear_attention_marks(self.class_id, list(self.db.get_attention_marks(self.class_id)))

    def h(self, user, role):
        from backend.auth import create_token
        return {"Authorization": f"Bearer {create_token(user, role, user)}"}

    def client(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    @property
    def url(self):
        return f"/api/instructor/classes/{self.class_id}/attention-marks"

    def insights(self, c, days=30):
        return c.get(f"/api/instructor/classes/{self.class_id}/insights?days={days}", headers=self.h("gv_tran", "instructor")).json()

    def row(self, c):
        rows = c.get("/api/instructor/classes-attention", headers=self.h("gv_tran", "instructor")).json()["classes"]
        return next(r for r in rows if r["id"] == self.class_id)

    def test_mark_and_undo_student_in_check_in_group(self):
        with self.client() as c:
            before = self.insights(c)
            pile = before["plain"]["groups"]["check_in"]
            self.assertTrue(pile)
            person = next(p for p in pile if p.get("key"))
            r = c.post(self.url, json={"keys": [person["key"]], "status": "handled", "days": 30}, headers=self.h("gv_tran", "instructor"))
            self.assertEqual((r.status_code, r.json()["marked"], r.json()["skipped"]), (200, 1, 0), r.text)
            after = self.insights(c)
            marked = next(p for p in after["plain"]["groups"]["check_in"] if p["username"] == person["username"])
            self.assertEqual(marked["mark"]["state"], "handled")
            self.assertEqual(after["overview"]["open_counts"]["handled"], 1)
            self.assertEqual(after["overview"]["open_counts"]["open"], before["overview"]["open_counts"]["open"] - 1)
            for key in ("overview", "process_groups", "bottlenecks", "students", "action_cards", "plain"):
                self.assertIn(key, after)  # khóa cũ vẫn còn
            u = c.post(self.url + "/undo", json={"keys": [person["key"]]}, headers=self.h("gv_tran", "instructor"))
            self.assertEqual(u.json()["removed"], 1)
            again = self.insights(c)
            self.assertEqual(again["overview"]["open_counts"]["handled"], 0)
            self.assertIsNone(next(p for p in again["plain"]["groups"]["check_in"] if p["username"] == person["username"])["mark"])

    def test_signature_is_computed_by_server_and_unknown_keys_skipped(self):
        with self.client() as c:
            person = next(p for p in self.insights(c)["plain"]["groups"]["check_in"] if p.get("key"))
            r = c.post(self.url, json={"keys": [person["key"], "stuck:nobody", "x" * 10], "status": "dismissed", "days": 30},
                       headers=self.h("gv_tran", "instructor"))
            self.assertEqual((r.json()["marked"], r.json()["skipped"]), (1, 2))
            stored = self.db.get_attention_marks(self.class_id)
            self.assertEqual(set(stored), {person["key"]})
            self.assertEqual(stored[person["key"]]["status"], "dismissed")
            self.assertTrue(stored[person["key"]]["signature"])
            self.assertEqual(stored[person["key"]]["marked_by"], "gv_tran")

    def test_mark_at_7_days_not_reopened_when_viewing_30_days(self):
        with self.client() as c:
            person = next(p for p in self.insights(c, 7)["plain"]["groups"]["check_in"] if p.get("key"))
            c.post(self.url, json={"keys": [person["key"]], "status": "handled", "days": 7}, headers=self.h("gv_tran", "instructor"))
            for d in (7, 30, 90):
                p = next(x for x in self.insights(c, d)["plain"]["groups"]["check_in"] if x["username"] == person["username"])
                self.assertEqual(p["mark"]["state"], "handled", d)

    def test_rbac_and_validation(self):
        with self.client() as c:
            body = {"keys": ["stuck:v58_dung"], "status": "handled", "days": 30}
            self.assertEqual(c.post(self.url, json=body, headers=self.h("qa_other_instructor", "instructor")).status_code, 404)
            self.assertEqual(c.post(self.url, json=body, headers=self.h("v58_an", "student")).status_code, 403)
            self.assertEqual(c.post(self.url + "/undo", json={"keys": ["a"]}, headers=self.h("qa_other_instructor", "instructor")).status_code, 404)
            self.assertEqual(c.post(self.url + "/undo", json={"keys": ["a"]}, headers=self.h("v58_an", "student")).status_code, 403)
            self.assertEqual(c.post(self.url, json={**body, "status": "deleted"}, headers=self.h("gv_tran", "instructor")).status_code, 422)
            self.assertEqual(c.post(self.url, json={**body, "keys": []}, headers=self.h("gv_tran", "instructor")).status_code, 422)
            self.assertEqual(c.post(self.url, json={**body, "keys": [f"k{i}" for i in range(61)]}, headers=self.h("gv_tran", "instructor")).status_code, 422)
            self.assertEqual(c.post(self.url, json={**body, "days": 0}, headers=self.h("gv_tran", "instructor")).status_code, 422)
            self.assertEqual(c.post("/api/instructor/classes/no_such_class/attention-marks", json=body, headers=self.h("gv_tran", "instructor")).status_code, 404)
            self.assertEqual(self.db.get_attention_marks(self.class_id), {})

    def test_other_instructor_cannot_undo_by_guessing(self):
        with self.client() as c:
            person = next(p for p in self.insights(c)["plain"]["groups"]["check_in"] if p.get("key"))
            c.post(self.url, json={"keys": [person["key"]], "status": "handled", "days": 30}, headers=self.h("gv_tran", "instructor"))
            c.post(self.url + "/undo", json={"keys": [person["key"]]}, headers=self.h("qa_other_instructor", "instructor"))
            self.assertIn(person["key"], self.db.get_attention_marks(self.class_id))

    def test_classes_attention_counts_and_brief_follow_marks(self):
        with self.client() as c:
            before = self.row(c)
            ov = self.db.get_class_insights(self.class_id, 7)
            from backend.class_overview import build_class_overview
            items = build_class_overview(ov)["attention"] if ov else []
            if not items:
                self.skipTest("lớp mẫu không có việc theo sinh viên trong 7 ngày")
            keys = list(current_signatures({"attention": items}))
            r = c.post(self.url, json={"keys": keys, "status": "handled", "days": 7}, headers=self.h("gv_tran", "instructor"))
            self.assertEqual(r.json()["marked"], len(keys))
            after = self.row(c)  # bộ đệm 60 giây phải bị xóa khi đánh dấu
            self.assertEqual(after["total"], before["total"] - len(keys))
            self.assertEqual(after["handled"], len(keys))
            if after["total"] == 0:
                self.assertNotIn("việc nên xem", after["brief_vi"])
            c.post(self.url + "/undo", json={"keys": keys}, headers=self.h("gv_tran", "instructor"))
            self.assertEqual(self.row(c)["total"], before["total"])

    def test_brief_counts_open_items_even_without_stuck_students(self):
        with self.client() as c:
            row = self.row(c)
            if row["total"] > 0 and row["check_in"] == 0:
                self.assertIn("việc nên xem", row["brief_vi"])  # lớp nằm trong danh sách thì dòng mô tả không được nói "chưa có việc"

    def test_expired_handled_mark_reopens_with_follow_up(self):
        with self.client() as c:
            person = next(p for p in self.insights(c)["plain"]["groups"]["check_in"] if p.get("key"))
            c.post(self.url, json={"keys": [person["key"]], "status": "handled", "days": 30}, headers=self.h("gv_tran", "instructor"))
            conn = self.db.get_db_connection()
            with conn:
                conn.execute("UPDATE attention_marks SET marked_at = datetime('now','localtime','-8 days') WHERE class_id = ?", (self.class_id,))
            conn.close()
            p2 = next(p for p in self.insights(c)["plain"]["groups"]["check_in"] if p["username"] == person["username"])
            self.assertEqual(p2["mark"]["state"], "reopened")
            self.assertIn("vẫn còn", p2["mark"]["follow_up_vi"])
            self.assertEqual(self.insights(c)["overview"]["open_counts"]["handled"], 0)

    def test_student_cannot_read_instructor_insights_marks(self):
        with self.client() as c:
            self.assertEqual(c.get(f"/api/instructor/classes/{self.class_id}/insights?days=30", headers=self.h("v58_an", "student")).status_code, 403)

    def test_remark_overwrites_single_row(self):
        with self.client() as c:
            person = next(p for p in self.insights(c)["plain"]["groups"]["check_in"] if p.get("key"))
            for status in ("handled", "dismissed"):
                c.post(self.url, json={"keys": [person["key"]], "status": status, "days": 30}, headers=self.h("gv_tran", "instructor"))
            stored = self.db.get_attention_marks(self.class_id)
            self.assertEqual(len(stored), 1)
            self.assertEqual(stored[person["key"]]["status"], "dismissed")


if __name__ == "__main__":
    unittest.main()
