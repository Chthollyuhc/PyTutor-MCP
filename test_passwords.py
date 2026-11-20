"""Kiểm thử băm mật khẩu và xác thực tương thích ngược.

Chạy:  py -m unittest test_passwords -v
Cần đặt PYTUTOR_DB_PATH / PYTUTOR_KNOWLEDGE_DB_PATH tới tệp tạm nếu chạy các ca đăng nhập qua API (tự bỏ qua nếu chưa đặt).
"""
import os
import sqlite3
import unittest

from backend.passwords import hash_password, is_hashed, verify_password


class PasswordHashTests(unittest.TestCase):
    def test_round_trip_and_wrong_password(self):
        stored = hash_password("matkhau-dung", iterations=1000)
        self.assertTrue(is_hashed(stored))
        self.assertTrue(verify_password("matkhau-dung", stored))
        self.assertFalse(verify_password("matkhau-sai", stored))

    def test_salt_makes_hashes_differ_and_plaintext_is_not_stored(self):
        a, b = hash_password("x", iterations=1000), hash_password("x", iterations=1000)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, "x")

    def test_legacy_plaintext_values_are_still_accepted(self):
        self.assertTrue(verify_password("student123", "student123"))
        self.assertFalse(verify_password("student124", "student123"))

    def test_malformed_hash_and_non_strings_are_rejected(self):
        self.assertFalse(verify_password("x", "pbkdf2_sha256$abc$zz$zz"))
        self.assertFalse(verify_password("x", "pbkdf2_sha256$1000$nothex$nothex"))
        self.assertFalse(verify_password(None, "x"))  # type: ignore[arg-type]
        self.assertFalse(verify_password("x", None))  # type: ignore[arg-type]


@unittest.skipUnless(os.getenv("PYTUTOR_DB_PATH"), "Cần DB tạm: đặt PYTUTOR_DB_PATH")
class SeededAccountsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from backend.database import init_db, get_db_connection
        init_db()
        conn = get_db_connection()
        cls.stored = {r["username"]: r["password"] for r in conn.execute("SELECT username, password FROM users")}
        conn.close()

    def test_new_database_stores_hashed_seed_passwords(self):
        for name in ("student", "gv_tran", "gv_tuan"):
            self.assertTrue(is_hashed(self.stored[name]), name)
            self.assertNotIn("123", self.stored[name])

    def test_demo_logins_still_work_and_wrong_password_fails(self):
        from backend.auth import authenticate_user
        self.assertEqual(authenticate_user("student", "student123")["role"], "student")
        self.assertEqual(authenticate_user("gv_tran", "gv123")["role"], "instructor")
        self.assertIsNone(authenticate_user("student", "gv123"))
        self.assertIsNone(authenticate_user("khong_ton_tai", "x"))

    def test_legacy_plaintext_row_can_still_log_in(self):
        from backend.database import get_db_connection
        from backend.auth import authenticate_user
        conn = get_db_connection()
        conn.execute("INSERT OR REPLACE INTO users(username,password,role,full_name) VALUES(?,?,?,?)",
                     ("legacy_pw_user", "plain-old", "student", "Legacy"))
        conn.commit(); conn.close()
        try:
            self.assertEqual(authenticate_user("legacy_pw_user", "plain-old")["username"], "legacy_pw_user")
        finally:
            conn = get_db_connection(); conn.execute("DELETE FROM users WHERE username='legacy_pw_user'"); conn.commit(); conn.close()


if __name__ == "__main__":
    unittest.main()
