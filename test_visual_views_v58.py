"""v5.8: Hành trình học (SV) và Tình hình lớp 3 tầng (GV). Phần thuần không cần DB; phần tích hợp cần PYTUTOR_DB_PATH (DB tạm)."""
from __future__ import annotations

import os
import unittest

from backend.class_overview import ACTION_PRIORITY, build_action_cards, build_class_overview
from backend.student_journey import FORBIDDEN_STUDENT_WORDS, build_student_headline, describe_exercise_journey
from pytutor_shared.learner_model import (
    PROCESS_EVENT_ORDER, build_journey_points, classify_learning_process, process_event_sort_key,
)


def ev(kind, passed=0, total=4, all_passed=False, hint=0, ts="2026-11-01 10:00:00", i=1):
    return {"kind": kind, "passed_tests": passed, "total_tests": total, "all_passed": all_passed, "hint_level": hint,
            "timestamp": ts, "id": i, "submission_id": i if kind != "run" else None}


class JourneyPointsTests(unittest.TestCase):
    def test_empty(self):
        out = build_journey_points([])
        self.assertEqual(out["points"], [])
        self.assertIsNone(out["summary"]["group"])
        self.assertIsNone(out["summary"]["first_pass_index"])
        self.assertIsInstance(describe_exercise_journey([], out["summary"]), str)

    def test_order_key_matches_insights_rule(self):
        events = [ev("submit", 1, ts="t1", i=1), ev("ask", hint=2, ts="t1", i=1), ev("run", 1, ts="t1", i=1)]
        events.sort(key=process_event_sort_key)
        self.assertEqual([e["kind"] for e in events], ["run", "ask", "submit"])
        self.assertEqual(PROCESS_EVENT_ORDER, {"run": 0, "ask": 1, "submit": 2})

    def test_new_best_and_counts(self):
        events = [ev("run", 1), ev("run", 1), ev("submit", 2), ev("ask", hint=2), ev("submit", 4, all_passed=True)]
        out = build_journey_points(events)
        flags = [p["is_new_best"] for p in out["points"]]
        self.assertEqual(flags, [True, False, True, False, True])
        self.assertEqual(out["summary"]["counts"], {"run": 2, "ask": 1, "submit": 2})
        self.assertEqual(out["summary"]["best"], {"passed": 4, "total": 4})
        self.assertEqual(out["summary"]["first_pass_index"], 4)
        self.assertIsNone(out["points"][3]["passed"])
        self.assertEqual(out["points"][3]["hint_level"], 2)

    def test_group_equals_classify(self):
        cases = [
            [ev("run", 1), ev("submit", 4, all_passed=True)],
            [ev("ask", hint=3), ev("submit", 4, all_passed=True)],
            [ev("run", 1)],
            [ev("run", 1, i=k) for k in range(9)] + [ev("submit", 1, i=20)],
        ]
        for events in cases:
            raw = [{"kind": e["kind"], "passed_tests": e["passed_tests"], "all_passed": e["all_passed"], "hint_level": e["hint_level"]}
                   for e in events]
            self.assertEqual(build_journey_points(events)["summary"]["group"], classify_learning_process(raw))


class HeadlineTests(unittest.TestCase):
    def texts(self, h):
        return " ".join(str(h.get(k) or "") for k in ("headline_vi", "detail_vi")).lower()

    def test_no_data(self):
        h = build_student_headline(None, None, None, [])
        self.assertEqual(h["tone"], "start")
        self.assertIsNone(h["cta"])
        h2 = build_student_headline({"concepts": []}, {"exercise_id": "e1", "title": "Bài 1", "reason": "x"}, {}, [])
        self.assertEqual(h2["cta"], {"exercise_id": "e1", "title": "Bài 1"})

    def test_struggling_concept_first(self):
        lm = {"concepts": [{"kc": "loop", "label_vi": "Vòng lặp", "state": "struggling",
                            "exercise_details": [{"exercise_id": "e2", "title": "Bài 2", "status": "struggling"}]}]}
        recent = [{"exercise_id": "e3", "title": "Bài 3", "group": "in_progress", "best": {"passed": 3, "total": 4}}]
        h = build_student_headline(lm, None, {"this": 2, "prev": 0}, recent)
        self.assertEqual((h["tone"], h["cta"]["exercise_id"]), ("focus", "e2"))
        self.assertIn("Vòng lặp", h["headline_vi"])

    def test_near_pass_then_week_then_next(self):
        lm = {"concepts": [{"kc": "loop", "label_vi": "V", "state": "developing", "exercise_details": [{"exercise_id": "e1", "status": "passed"}]}]}
        recent = [{"exercise_id": "e3", "title": "Bài 3", "group": "in_progress", "best": {"passed": 3, "total": 4}}]
        h = build_student_headline(lm, {"exercise_id": "e9", "title": "B9", "reason": "r"}, {"this": 1, "prev": 0}, recent)
        self.assertIn("3/4", h["headline_vi"])
        self.assertEqual(h["cta"]["exercise_id"], "e3")
        h2 = build_student_headline(lm, {"exercise_id": "e9", "title": "B9", "reason": "r"}, {"this": 1, "prev": 0}, [])
        self.assertIn("1 bài", h2["headline_vi"])
        h3 = build_student_headline(lm, {"exercise_id": "e9", "title": "B9", "reason": "Lý do"}, {"this": 0, "prev": 0}, [])
        self.assertEqual((h3["cta"]["exercise_id"], h3["detail_vi"]), ("e9", "Lý do"))

    def test_no_forbidden_words_anywhere(self):
        lm = {"concepts": [{"kc": "loop", "label_vi": "Vòng lặp", "state": "struggling", "exercise_details": []}]}
        samples = [build_student_headline(None, None, None, []), build_student_headline(lm, None, {}, [])]
        flat = [ev("run", 1, i=k) for k in range(9)]
        built = build_journey_points(flat)
        samples.append({"headline_vi": describe_exercise_journey(built["points"], built["summary"])})
        passed = build_journey_points([ev("run", 1), ev("submit", 4, all_passed=True)])
        samples.append({"headline_vi": describe_exercise_journey(passed["points"], passed["summary"])})
        for h in samples:
            for word in FORBIDDEN_STUDENT_WORDS:
                self.assertNotIn(word, self.texts(h), word)

    def test_describe_branches(self):
        passed = build_journey_points([ev("run", 1), ev("run", 2), ev("submit", 4, all_passed=True)])
        self.assertIn("thử–sửa 3 lượt rồi đạt", describe_exercise_journey(passed["points"], passed["summary"]))
        first = build_journey_points([ev("submit", 4, all_passed=True)])
        self.assertIn("ngay", describe_exercise_journey(first["points"], first["summary"]))
        flat = build_journey_points([ev("run", 2, i=k) for k in range(7)])
        self.assertIn("Gia sư AI", describe_exercise_journey(flat["points"], flat["summary"]))


class ActionCardsTests(unittest.TestCase):
    def insights(self):
        return {
            "data_status": "sufficient", "sample": {"active_students": 8},
            "bottlenecks": [{"exercise_id": "e1", "title": "Bài 1", "submissions": 10, "unsuccessful": 8, "unsuccessful_percent": 80.0},
                            {"exercise_id": "e2", "title": "Bài 2", "submissions": 6, "unsuccessful": 1, "unsuccessful_percent": 16.7}],
            "matrix": {"exercises": [{"exercise_id": "e1", "title": "Bài 1", "students_attempted": 6},
                                     {"exercise_id": "e2", "title": "Bài 2", "students_attempted": 4}], "rows": []},
            "students": [
                {"username": "b", "full_name": "Bình", "stuck_exercises": [{"exercise_id": "e1", "title": "Bài 1"}],
                 "process_by_exercise": {"e1": "stuck"}},
                {"username": "a", "full_name": "An", "stuck_exercises": [{"exercise_id": "e1", "title": "Bài 1"}],
                 "process_by_exercise": {"e1": "stuck"}},
                {"username": "c", "full_name": "Chi", "stuck_exercises": [],
                 "process_by_exercise": {"e1": "hint_pass", "e2": "hint_pass"}},
            ],
            "process_groups": {"by_exercise": [{"exercise_id": "e2", "title": "Bài 2", "groups": {"independent_pass": 3}}]},
            "kc_overview": {"modeled_students": 6, "items": [
                {"kc": "loop", "label_vi": "Vòng lặp", "students": {"struggling": 3, "developing": 1, "secure": 0, "no_evidence": 2}}]},
            "failing_tests_by_exercise": [{"exercise_id": "e1", "title": "Bài 1", "tests": [
                {"test_idx": 3, "attempts": 6, "students": 3, "description": "n = 0"}]}],
            "error_breakdown_by_exercise": [],
        }

    def test_priority_grouping_and_evidence(self):
        ins = self.insights()
        cards = build_action_cards(build_class_overview(ins), ins)
        codes = [c["code"] for c in cards["cards"]]
        self.assertEqual(codes, sorted(codes, key=ACTION_PRIORITY.index))
        stuck = cards["cards"][0]
        self.assertEqual(stuck["code"], "stuck")
        self.assertEqual([s["username"] for s in stuck["students"]], ["a", "b"])  # A→Z
        self.assertEqual((stuck["evidence"]["k"], stuck["evidence"]["n"]), (2, 6))
        self.assertFalse(stuck["evidence"]["show_percent"])  # n < 10
        failing = next(c for c in cards["cards"] if c["code"] == "failing_test")
        self.assertEqual((failing["evidence"]["k"], failing["evidence"]["n"]), (3, 6))  # SV bị sai / SV đã thử bài
        self.assertIn("n = 0", failing["title_vi"])
        self.assertEqual(failing["action"]["target"], "exercise_detail")
        self.assertEqual({c["action"]["label_vi"] for c in cards["cards"]}, {"Xem chi tiết"})
        self.assertTrue(all(c["evidence"]["k"] <= c["evidence"]["n"] for c in cards["cards"]))
        self.assertLessEqual(len(cards["positives"]), 2)

    def test_limit_five_and_more_count(self):
        ins = self.insights()
        ins["error_breakdown_by_exercise"] = [{"exercise_id": "e1", "title": "Bài 1", "submit": {"logic_partial": 5},
                                               "run": {}, "format_only_submit": 3, "format_only_run": 0}]
        ins["students"].append({"username": "d", "full_name": "Dũng", "stuck_exercises": [],
                                "process_by_exercise": {"e1": "practice_only", "e2": "practice_only"}})
        out = build_action_cards(build_class_overview(ins), ins, limit=5)
        self.assertLessEqual(len(out["cards"]), 5)
        out2 = build_action_cards(build_class_overview(ins), ins, limit=2)
        self.assertEqual(len(out2["cards"]), 2)
        self.assertGreater(out2["more_count"], 0)

    def test_limited_and_no_data_have_no_class_cards(self):
        ins = self.insights()
        ins["data_status"] = "limited"
        cards = build_action_cards(build_class_overview(ins), ins)["cards"]
        self.assertTrue(all(c["code"] in ("stuck", "hint_dependence", "practice_only") for c in cards))
        ins["data_status"] = "no_data"
        ins["students"] = []
        out = build_action_cards(build_class_overview(ins), ins)
        self.assertEqual((out["cards"], out["more_count"]), ([], 0))
        self.assertTrue(out["empty_vi"])


@unittest.skipUnless(os.environ.get("PYTUTOR_DB_PATH"), "cần PYTUTOR_DB_PATH (DB tạm)")
class JourneyIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from backend import database as db
        from seed.seed_demo_class_v58 import CLASS_ID, build_demo_class
        cls.db, cls.class_id = db, CLASS_ID
        cls.info = build_demo_class(db)
        cls.ex = cls.info["exercise_ids"]

    def h(self, user, role):
        from backend.auth import create_token
        return {"Authorization": f"Bearer {create_token(user, role, user)}"}

    def client(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)

    def test_matrix_complete_sorted_and_ordered(self):
        out = self.db.get_class_insights(self.class_id, 30)
        m = out["matrix"]
        self.assertEqual([e["exercise_id"] for e in m["exercises"]], self.ex)
        self.assertEqual(len(m["rows"]), len(self.info["students"]))  # kể cả SV chưa hoạt động
        names = [r["full_name"].casefold() for r in m["rows"]]
        self.assertEqual(names, sorted(names))
        nam = next(r for r in m["rows"] if r["username"] == "v58_nam")
        self.assertTrue(all(v is None for v in nam["cells"].values()))
        groups = {g for r in m["rows"] for g in r["cells"].values() if g}
        self.assertTrue({"independent_pass", "retry_pass", "hint_pass", "in_progress", "stuck", "practice_only"} <= groups)

    def test_cell_group_equals_journey_equals_process_by_exercise(self):
        days = 30
        out = self.db.get_class_insights(self.class_id, days)
        by_student = {s["username"]: s["process_by_exercise"] for s in out["students"]}
        checked = 0
        for row in out["matrix"]["rows"]:
            for eid, group in row["cells"].items():
                journey = self.db.get_exercise_journey(row["username"], eid, days=days)
                self.assertEqual(journey["summary"]["group"], group, (row["username"], eid))
                self.assertEqual(by_student.get(row["username"], {}).get(eid), group)
                checked += 1
        self.assertGreater(checked, 0)

    def test_action_cards_in_insights_and_stuck_card(self):
        url = f"/api/instructor/classes/{self.class_id}/insights?days=30"
        with self.client() as c:
            body = c.get(url, headers=self.h("gv_tran", "instructor")).json()
        cards = body["action_cards"]
        self.assertLessEqual(len(cards["cards"]), 5)
        stuck = [c for c in cards["cards"] if c["code"] == "stuck"]
        self.assertTrue(stuck)
        self.assertEqual({s["username"] for s in stuck[0]["students"]}, {"v58_dung", "v58_giang"})
        for key in ("overview", "process_groups", "bottlenecks", "students"):  # khóa cũ không đổi
            self.assertIn(key, body)

    def test_instructor_journey_rbac_and_privacy(self):
        eid = self.ex[2]
        url = f"/api/instructor/classes/{self.class_id}/students/v58_dung/exercises/{eid}/journey?days=30"
        with self.client() as c:
            ok = c.get(url, headers=self.h("gv_tran", "instructor"))
            self.assertEqual(ok.status_code, 200)
            body = ok.json()
            self.assertEqual(body["summary"]["group"], "stuck")
            self.assertFalse(any("code" in p for p in body["points"]))
            self.assertEqual(c.get(url, headers=self.h("qa_other_instructor", "instructor")).status_code, 404)
            self.assertEqual(c.get(url, headers=self.h("v58_dung", "student")).status_code, 403)
            bad_student = url.replace("v58_dung", "nobody_here")
            self.assertEqual(c.get(bad_student, headers=self.h("gv_tran", "instructor")).status_code, 404)
            bad_ex = url.replace(eid, "no_such_exercise")
            self.assertEqual(c.get(bad_ex, headers=self.h("gv_tran", "instructor")).status_code, 404)

    def test_student_journey_scope_and_code(self):
        eid = self.ex[0]
        url = f"/api/student/journey?class_id={self.class_id}&exercise_id={eid}"
        with self.client() as c:
            ok = c.get(url, headers=self.h("v58_binh", "student"))
            self.assertEqual(ok.status_code, 200, ok.text)
            body = ok.json()
            self.assertEqual(body["current"]["exercise_id"], eid)
            self.assertTrue(any(p.get("code") for p in body["current"]["points"] if p["kind"] == "submit"))
            self.assertIn("headline_vi", body["headline"])
            self.assertEqual(len(body["concepts"]), 6)
            self.assertLessEqual(len(body["recent_exercises"]), 5)
            # không thấy dữ liệu người khác: SV chưa hoạt động không có dấu chân
            empty = c.get(url, headers=self.h("v58_nam", "student")).json()
            self.assertEqual(empty["current"]["points"], [])
            self.assertEqual(c.get(url, headers=self.h("student", "student")).status_code, 404)  # không ghi danh lớp này
            self.assertEqual(c.get(url, headers=self.h("gv_tran", "instructor")).status_code, 403)
            self.assertEqual(c.get(f"/api/student/journey?class_id={self.class_id}&exercise_id=nope",
                                   headers=self.h("v58_binh", "student")).status_code, 404)

    def test_classes_attention_rbac_and_sorting(self):
        with self.client() as c:
            ok = c.get("/api/instructor/classes-attention", headers=self.h("gv_tran", "instructor"))
            self.assertEqual(ok.status_code, 200)
            body = ok.json()
            self.assertTrue(any(r["id"] == self.class_id for r in body["classes"]))
            totals = [r["total"] for r in body["classes"]]
            self.assertEqual(totals, sorted(totals, reverse=True))
            self.assertEqual(body["needing_attention"], sum(1 for t in totals if t > 0))
            other = c.get("/api/instructor/classes-attention", headers=self.h("qa_other_instructor", "instructor")).json()
            self.assertFalse(any(r["id"] == self.class_id for r in other["classes"]))  # không thấy lớp người khác
            self.assertEqual(c.get("/api/instructor/classes-attention", headers=self.h("v58_an", "student")).status_code, 403)

    def test_week_counts(self):
        o = self.db.get_student_journey_overview("v58_lan", self.class_id)
        self.assertEqual(o["week"], {"this": 0, "prev": 2})
        o2 = self.db.get_student_journey_overview("v58_an", self.class_id)
        self.assertGreaterEqual(o2["week"]["this"], 3)


if __name__ == "__main__":
    unittest.main()
