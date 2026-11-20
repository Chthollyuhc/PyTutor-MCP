"""v5.7: thu thập đặc trưng chẩn đoán (test sai, sai định dạng). Phần thuần không cần DB; phần DB tự bỏ qua
nếu chưa đặt PYTUTOR_DB_PATH (tránh ghi vào pytutor.db thật)."""
from __future__ import annotations

import json
import os
import sqlite3
import unittest

from pytutor_shared.learner_model import normalize_output_for_diagnosis, summarize_attempt_features


def res(idx, status, expected="5", actual="5"):
    return {"test_idx": idx, "status": status, "expected_output": expected, "actual_output": actual}


class PureFeatureTests(unittest.TestCase):
    def test_failed_and_format_mismatch(self):
        tr = {"all_passed": False, "passed_tests": 1, "results": [
            res(1, "PASS"), res(2, "FAIL", "Hello World", "hello   world"), res(3, "FAIL", "5", "6")]}
        f = summarize_attempt_features(tr, {"valid": True})
        self.assertEqual(f["failed_tests"], [2, 3])
        self.assertEqual(f["format_mismatch_tests"], [2])
        self.assertFalse(f["format_only"])
        self.assertEqual(f["feature_version"], "2")

    def test_format_only(self):
        tr = {"all_passed": False, "passed_tests": 0, "results": [res(1, "FAIL", "a b", "a  b "), res(2, "FAIL", "X", "x")]}
        f = summarize_attempt_features(tr, {"valid": True})
        self.assertTrue(f["format_only"])

    def test_skipped_not_counted_as_failed(self):
        tr = {"all_passed": False, "passed_tests": 0, "results": [
            res(1, "SYNTAX_ERROR", "1", ""), res(2, "SKIPPED", "1", ""), res(3, "SKIPPED", "1", "")]}
        f = summarize_attempt_features(tr, {"valid": False})
        self.assertEqual(f["failed_tests"], [1])
        self.assertEqual(f["format_mismatch_tests"], [])
        self.assertEqual(f["error_class"], "syntax")

    def test_error_class_unchanged_by_format_label(self):
        tr = {"all_passed": False, "passed_tests": 0, "results": [res(1, "FAIL", "A", "a")]}
        self.assertEqual(summarize_attempt_features(tr, {"valid": True})["error_class"], "logic_none")

    def test_passed_has_no_failures(self):
        f = summarize_attempt_features({"all_passed": True, "passed_tests": 1, "results": [res(1, "PASS")]}, {"valid": True})
        self.assertEqual(f["failed_tests"], [])
        self.assertFalse(f["format_only"])

    def test_normalize(self):
        self.assertEqual(normalize_output_for_diagnosis("  Hi \n  There "), "hi there")


@unittest.skipUnless(os.environ.get("PYTUTOR_DB_PATH"), "cần PYTUTOR_DB_PATH (DB tạm)")
class DbTests(unittest.TestCase):
    def test_alter_idempotent_on_old_schema_and_save_run(self):
        from backend import database as db
        db.init_db()
        db.init_db()  # idempotent
        db.save_practice_run("v57_user", "ex_x", 1, 3, False, features={
            "error_class": "logic_partial", "failed_tests": [2, 3], "format_mismatch_tests": [2], "feature_version": "2"})
        conn = db.get_db_connection()
        try:
            row = conn.execute("SELECT * FROM practice_runs WHERE username='v57_user'").fetchone()
            self.assertEqual(row["error_class"], "logic_partial")
            self.assertEqual(json.loads(row["failed_tests"]), [2, 3])
            self.assertEqual(json.loads(row["format_mismatch_tests"]), [2])
            cols = {r[1] for r in conn.execute("PRAGMA table_info(attempt_features)").fetchall()}
            self.assertTrue({"failed_tests", "format_mismatch_tests"} <= cols)
        finally:
            conn.close()

    def test_old_run_without_features_still_saves(self):
        from backend import database as db
        db.init_db()
        self.assertTrue(db.save_practice_run("v57_old", "ex_x", 0, 3, False))


if __name__ == "__main__":
    unittest.main()
