"""v5.7: tóm tắt "Tình hình lớp". Phần thuần không cần DB; phần tích hợp cần PYTUTOR_DB_PATH (DB tạm)."""
from __future__ import annotations

import os
import unittest

from backend.class_overview import build_class_overview


def insights(**kw):
    base = {
        "data_status": "sufficient",
        "bottlenecks": [{"exercise_id": "e1", "title": "Bài 1", "submissions": 10, "unsuccessful": 7, "unsuccessful_percent": 70.0}],
        "students": [],
        "process_groups": {"by_exercise": []},
        "kc_overview": {"modeled_students": 4, "items": []},
        "failing_tests_by_exercise": [],
        "error_breakdown_by_exercise": [],
    }
    base.update(kw)
    return base


class OverviewPureTests(unittest.TestCase):
    def codes(self, ov, key):
        return [x["code"] for x in ov[key]]

    def test_bottleneck_threshold(self):
        ov = build_class_overview(insights())
        self.assertIn("bottleneck", self.codes(ov, "class_issues"))
        self.assertIn("70.0%", ov["class_issues"][0]["text_vi"])
        low = insights(bottlenecks=[{"exercise_id": "e1", "title": "B", "submissions": 10, "unsuccessful": 3, "unsuccessful_percent": 30.0}])
        self.assertNotIn("bottleneck", self.codes(build_class_overview(low), "class_issues"))

    def test_limited_gives_no_class_conclusion(self):
        st = [{"username": "a", "full_name": "A", "stuck_exercises": [{"exercise_id": "e1", "title": "Bài 1"}], "process_by_exercise": {"e1": "stuck"}}]
        ov = build_class_overview(insights(data_status="limited", students=st))
        self.assertEqual(ov["class_issues"], [])
        self.assertIn("insufficient_reason_vi", ov)
        self.assertEqual(self.codes(ov, "attention"), ["stuck"])  # nói về từng SV nên vẫn hiển thị

    def test_no_data(self):
        ov = build_class_overview(insights(data_status="no_data"))
        self.assertEqual((ov["class_issues"], ov["positives"]), ([], []))

    def test_attention_rules(self):
        st = [{"username": "b", "full_name": "B", "stuck_exercises": [],
               "process_by_exercise": {"e1": "hint_pass", "e2": "hint_pass", "e3": "practice_only", "e4": "practice_only"}}]
        ov = build_class_overview(insights(students=st))
        self.assertEqual(sorted(self.codes(ov, "attention")), ["hint_dependence", "practice_only"])
        one = [{"username": "c", "full_name": "C", "stuck_exercises": [], "process_by_exercise": {"e1": "hint_pass"}}]
        self.assertEqual(build_class_overview(insights(students=one))["attention"], [])

    def test_kc_and_positives(self):
        kc = {"modeled_students": 4, "items": [
            {"kc": "loop", "label_vi": "Vòng lặp", "students": {"struggling": 2, "developing": 1, "secure": 0, "no_evidence": 1}},
            {"kc": "string", "label_vi": "Xử lý chuỗi", "students": {"struggling": 0, "developing": 1, "secure": 2, "no_evidence": 1}}]}
        ov = build_class_overview(insights(kc_overview=kc, bottlenecks=[],
                                           process_groups={"by_exercise": [{"exercise_id": "e1", "title": "B1", "groups": {"independent_pass": 3}}]}))
        self.assertIn("kc_struggling", self.codes(ov, "class_issues"))
        self.assertIn("2/3", ov["class_issues"][0]["text_vi"])
        self.assertEqual(sorted(self.codes(ov, "positives")), ["independent_pass", "kc_secure"])

    def test_failing_test_and_format(self):
        f = [{"exercise_id": "e1", "title": "B1", "tests": [{"test_idx": 3, "attempts": 6, "students": 3, "description": "n = 0"}]}]
        eb = [{"exercise_id": "e1", "title": "B1", "submit": {"logic_partial": 4}, "run": {"logic_none": 2}, "format_only_submit": 2, "format_only_run": 1}]
        ov = build_class_overview(insights(failing_tests_by_exercise=f, error_breakdown_by_exercise=eb))
        codes = self.codes(ov, "class_issues")
        self.assertIn("failing_test", codes)
        self.assertIn("format_mismatch", codes)

    def test_empty(self):
        self.assertEqual(build_class_overview({})["attention"], [])


@unittest.skipUnless(os.environ.get("PYTUTOR_DB_PATH"), "cần PYTUTOR_DB_PATH (DB tạm)")
class OverviewIntegrationTests(unittest.TestCase):
    CLASS_ID = "v57_class"

    @classmethod
    def setUpClass(cls):
        from backend import database as db
        db.init_db()
        conn = db.get_db_connection()
        try:
            conn.execute("INSERT OR REPLACE INTO credit_classes (id, class_code, class_name, instructor_username, enrollment_code) VALUES (?,?,?,?,?)",
                         (cls.CLASS_ID, "V57", "Lớp v57", "gv_tran", "CODE-V57"))
            ex = conn.execute("SELECT id FROM exercises LIMIT 1").fetchone()["id"]
            cls.ex = ex
            conn.execute("INSERT OR IGNORE INTO class_exercises (class_id, exercise_id) VALUES (?,?)", (cls.CLASS_ID, ex))
            for u in ("v57_a", "v57_b", "v57_c"):
                conn.execute("INSERT OR IGNORE INTO class_enrollments (class_id, student_username) VALUES (?,?)", (cls.CLASS_ID, u))
            conn.commit()
        finally:
            conn.close()
        feats = {"error_class": "logic_partial", "status_counts": {"FAIL": 1}, "ast_flags": {}, "feature_version": "2",
                 "failed_tests": [2], "format_mismatch_tests": [2]}
        for u in ("v57_a", "v57_b", "v57_c"):
            db.save_submission(u, ex, "print(1)", 0, 0, 3, False, "offline", "", attempt_features=feats)
            db.save_practice_run(u, ex, 0, 3, False, features=feats)
        db.save_submission("v57_a", ex, "print(2)", 0, 3, 3, True, "offline", "")

    def test_new_keys_and_overview(self):
        from backend import database as db
        out = db.get_class_insights(self.CLASS_ID, 7)
        for key in ("kc_overview", "error_breakdown_by_exercise", "failing_tests_by_exercise",
                    "time_to_pass_by_exercise", "daily_trend", "feature_coverage_percent", "process_groups", "bottlenecks"):
            self.assertIn(key, out)
        self.assertGreater(out["feature_coverage_percent"], 0)
        self.assertEqual(out["kc_overview"]["modeled_students"], 3)
        self.assertGreater(len(out["kc_overview"]["items"]), 0)
        ft = out["failing_tests_by_exercise"][0]["tests"][0]
        self.assertEqual((ft["test_idx"], ft["students"]), (2, 3))
        eb = out["error_breakdown_by_exercise"][0]
        self.assertEqual(eb["format_only_submit"], 3)
        self.assertEqual(eb["format_only_run"], 3)
        self.assertEqual(out["time_to_pass_by_exercise"][0]["n"], 1)
        self.assertTrue(build_class_overview(out)["thresholds"])

    def test_endpoint_rbac(self):
        from fastapi.testclient import TestClient
        from backend.auth import create_token
        from backend.main import app

        def h(u, r):
            return {"Authorization": f"Bearer {create_token(u, r, u)}"}
        url = f"/api/instructor/classes/{self.CLASS_ID}/insights"
        with TestClient(app) as c:
            ok = c.get(url, headers=h("gv_tran", "instructor"))
            self.assertEqual(ok.status_code, 200)
            self.assertIn("overview", ok.json())
            self.assertEqual(c.get(url, headers=h("qa_other_instructor", "instructor")).status_code, 404)
            self.assertEqual(c.get(url, headers=h("student", "student")).status_code, 403)


if __name__ == "__main__":
    unittest.main()
