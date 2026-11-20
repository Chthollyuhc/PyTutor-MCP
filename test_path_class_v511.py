"""Chặng đường ở trang chủ phải vẽ đúng học phần (v5.11). Phần thuần không cần DB; phần tích hợp cần DB tạm:
  .\\.claude\\run_isolated.ps1 test_path_class_v511
"""
import os
import unicodedata
import unittest

from backend.student_journey import pick_path_class


def nfc(text):
    return unicodedata.normalize("NFC", text or "")


def cls(cid, name, ex_ids):
    return {"id": cid, "class_name": name, "exercises": [{"exercise_id": e} for e in ex_ids]}


BASIC = cls("c_basic", "Cơ sở lập trình", ["e1", "e2", "e3", "e4", "e5"])
DATA = cls("c_data", "Lập trình phân tích dữ liệu", ["e1", "e4", "e5"])
OOP = cls("c_oop", "Lập trình hướng đối tượng", ["e1", "e2", "e3"])
RECENT = [{"exercise_id": e} for e in ("e5", "e4", "e3", "e2", "e1")]  # bài mới nhất đứng đầu


class PickPathClassTests(unittest.TestCase):
    def test_old_rule_picked_the_first_class_containing_the_latest_exercise(self):
        """Tái hiện lỗi: lớp 'dữ liệu' đứng đầu danh sách và có bài mới nhất nên bị chọn dù sinh viên làm ở 'cơ sở'."""
        loaded = [DATA, BASIC, OOP]
        old = next(c for c in loaded if any(e["exercise_id"] == RECENT[0]["exercise_id"] for e in c["exercises"]))
        self.assertEqual(old["class_name"], "Lập trình phân tích dữ liệu")
        self.assertEqual(pick_path_class(loaded, RECENT)["class_name"], "Cơ sở lập trình")

    def test_class_the_student_just_opened_wins(self):
        self.assertEqual(pick_path_class([DATA, BASIC, OOP], RECENT, "c_oop")["id"], "c_oop")

    def test_unknown_or_foreign_focus_is_ignored(self):
        self.assertEqual(pick_path_class([DATA, BASIC], RECENT, "c_other_students_class")["id"], "c_basic")

    def test_recency_weight_breaks_ties_in_favour_of_the_newest_work(self):
        a, b = cls("a", "A", ["e1", "e2"]), cls("b", "B", ["e3"])
        # a có hai bài cũ (e1, e2) = 1+2 điểm; b có một bài mới nhất (e3) = 3 điểm; hòa → giữ thứ tự (a trước)
        recent = [{"exercise_id": "e3"}, {"exercise_id": "e2"}, {"exercise_id": "e1"}]
        self.assertEqual(pick_path_class([a, b], recent)["id"], "a")
        self.assertEqual(pick_path_class([b, a], recent)["id"], "b")

    def test_no_recent_or_no_match_falls_back_to_first_class(self):
        self.assertEqual(pick_path_class([DATA, BASIC], [])["id"], "c_data")
        self.assertEqual(pick_path_class([DATA, BASIC], [{"exercise_id": "zzz"}])["id"], "c_data")
        self.assertIsNone(pick_path_class([], RECENT))


@unittest.skipIf(not os.environ.get("PYTUTOR_DB_PATH"), "cần PYTUTOR_DB_PATH trỏ tới DB tạm")
class JourneyEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls_):
        from fastapi.testclient import TestClient
        from backend.auth import create_token
        from backend.database import get_db_connection, init_db
        from backend.main import app
        init_db()
        cls_.client = TestClient(app)
        cls_.headers = {"Authorization": f"Bearer {create_token('student', 'student', 'Sinh viên thử')}"}
        conn = get_db_connection()
        try:
            # lớp 'dữ liệu' tạo SAU nên đứng đầu danh sách (ORDER BY created_at DESC)
            conn.execute("UPDATE credit_classes SET created_at='2026-01-01 00:00:00' WHERE id='cls_neu_cntt1128_02'")
            conn.execute("UPDATE credit_classes SET created_at='2026-09-01 00:00:00' WHERE id='cls_neu_cntt1187_01'")
            for i, ex in enumerate(["ex_01_sum_1_to_n", "ex_03_factorial", "ex_02_prime_check", "ex_04_reverse_string", "ex_05_count_vowels"]):
                conn.execute("INSERT INTO submissions(session_id,exercise_id,code,hint_level,passed_tests,total_tests,all_passed,action_type,timestamp) "
                             "VALUES('student',?,?,1,5,5,1,'submit',?)", (ex, "pass", f"2026-11-0{i + 1} 10:00:00"))
            conn.commit()
        finally:
            conn.close()

    def _path(self, **params):
        res = self.client.get("/api/student/journey", headers=self.headers, params=params)
        self.assertEqual(res.status_code, 200, res.text)
        return res.json()["today"]["path"]

    def test_default_path_is_the_course_with_the_most_recent_work(self):
        path = self._path()
        self.assertEqual(nfc(path["class_name"]), nfc("Cơ sở lập trình"))
        self.assertEqual(path["total"], 5)

    def test_focus_class_is_honoured_and_foreign_class_is_ignored(self):
        self.assertEqual(nfc(self._path(focus_class_id="cls_neu_cntt1187_01")["class_name"]), nfc("Lập trình phân tích dữ liệu"))
        self.assertEqual(nfc(self._path(focus_class_id="cls_khong_ton_tai")["class_name"]), nfc("Cơ sở lập trình"))


if __name__ == "__main__":
    unittest.main()
