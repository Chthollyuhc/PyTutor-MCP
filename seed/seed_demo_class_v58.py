"""Lớp mẫu TỔNG HỢP cho v5.8 (script dev). Chỉ chạy trên DB tạm: từ chối nếu PYTUTOR_DB_PATH chưa đặt hoặc là pytutor.db.

Tạo lớp `v58_demo` (gv_tran) với 9 sinh viên giả lập, 5 bài theo lộ trình, đủ 6 nhóm quá trình, test cuối sai tập trung
ở bài 3, sai định dạng ở bài 4, và một số lượt cách đây 8-14 ngày để so sánh tuần. Ghi bằng hàm DB sẵn có (save_submission,
save_practice_run), sau đó lùi mốc thời gian.

Dùng:  $env:PYTUTOR_DB_PATH = "$env:TEMP\\pytutor_qa.db"; py seed/seed_demo_class_v58.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CLASS_ID = "v58_demo"
DEMO_PASSWORD = "demo123"  # chỉ cho DB tạm; để QA giao diện bằng tài khoản sinh viên mẫu

STUDENTS = [
    ("v58_an", "An"), ("v58_binh", "Bình"), ("v58_chi", "Chi"), ("v58_dung", "Dũng"), ("v58_giang", "Giang"),
    ("v58_hoa", "Hoa"), ("v58_khanh", "Khánh"), ("v58_lan", "Lan"), ("v58_nam", "Nam"),
]

FULL, ALMOST, LAST = 99, 98, -1  # ký hiệu theo số test của từng bài: đạt hết / đạt hết trừ 1 / test cuối


def refuse_unless_temp_db() -> None:
    path = os.environ.get("PYTUTOR_DB_PATH", "").strip()
    if not path or Path(path).name.lower() == "pytutor.db":
        raise SystemExit("Từ chối chạy: hãy đặt PYTUTOR_DB_PATH tới một DB tạm (không phải pytutor.db).")


# Sự kiện: (loại, số test đạt, ngày trước, mức gợi ý, test sai, test sai định dạng)
def run(p, d, failed=None, fmt=None): return ("run", p, d, 0, failed or [], fmt or [])
def sub(p, d, failed=None, fmt=None): return ("submit", p, d, 0, failed or [], fmt or [])
def ask(level, d): return ("ask", 0, d, level, [], [])


SCENARIO = {
    "v58_an": {0: [run(FULL, 3), sub(FULL, 3)], 1: [run(ALMOST, 2, [LAST]), run(FULL, 2), sub(FULL, 2)],
               2: [sub(FULL, 1)], 3: [run(FULL, 1), sub(FULL, 1)]},
    "v58_binh": {0: [run(1, 9), sub(2, 9, [LAST]), sub(FULL, 9)],
                 1: [run(1, 6), run(2, 6), run(ALMOST, 5, [LAST]), sub(FULL, 5)],
                 2: [run(1, 2, [LAST]), sub(ALMOST, 2, [LAST])]},
    "v58_chi": {0: [sub(1, 10, [LAST]), ask(2, 10), sub(FULL, 10)], 1: [sub(1, 4, [LAST]), ask(3, 4), sub(FULL, 4)],
                2: [sub(0, 1, [LAST]), ask(2, 1)]},
    "v58_dung": {0: [run(FULL, 8), sub(FULL, 8)], 1: [run(FULL, 7), sub(FULL, 7)],
                 2: [run(1, 3, [LAST]), run(1, 3, [LAST]), sub(1, 3, [LAST]), run(1, 2, [LAST]), run(1, 2, [LAST]),
                     sub(1, 2, [LAST]), run(1, 1, [LAST]), run(1, 1, [LAST]), sub(1, 1, [LAST])],
                 3: [sub(ALMOST, 1, [2], [2]), sub(ALMOST, 1, [2], [2])]},
    "v58_giang": {0: [run(FULL, 12), sub(FULL, 12)], 1: [run(1, 9), run(2, 9), sub(FULL, 9)],
                  2: [run(1, 3, [LAST]), run(1, 3, [LAST]), run(1, 2, [LAST]), sub(1, 2, [LAST]), run(1, 2, [LAST]),
                      run(1, 2, [LAST]), sub(1, 1, [LAST]), run(1, 1, [LAST]), run(1, 1, [LAST])],
                  3: [run(ALMOST, 1, [2], [2]), sub(ALMOST, 1, [2], [2])]},
    "v58_hoa": {0: [run(1, 3), run(2, 3)], 1: [run(1, 2), run(1, 2)]},
    "v58_khanh": {0: [run(FULL, 4), sub(FULL, 4)], 1: [sub(FULL, 3)], 2: [run(ALMOST, 2, [LAST]), sub(FULL, 2)],
                  3: [sub(ALMOST, 1, [2], [2]), sub(ALMOST, 1, [2], [2]), sub(FULL, 1)]},
    "v58_lan": {0: [run(1, 13), sub(FULL, 13)], 1: [run(ALMOST, 12, [LAST]), sub(FULL, 12)]},
    "v58_nam": {},
}


def _resolve(value: int, total: int) -> int:
    return total if value == FULL else (total - 1 if value == ALMOST else value)


def build_demo_class(db) -> dict:
    """Tạo lớp mẫu bằng hàm DB sẵn có. `db` là module backend.database đã trỏ tới DB tạm."""
    refuse_unless_temp_db()
    db.init_db()
    conn = db.get_db_connection()
    try:
        rows = conn.execute("SELECT id, test_cases FROM exercises ORDER BY rowid LIMIT 5").fetchall()
        ex_ids = [r["id"] for r in rows]
        totals = {r["id"]: max(2, len(json.loads(r["test_cases"] or "[]"))) for r in rows}
        conn.execute("INSERT OR REPLACE INTO credit_classes (id, class_code, class_name, instructor_username, enrollment_code) "
                     "VALUES (?,?,?,?,?)", (CLASS_ID, "V58DEMO", "Lớp mẫu v5.8 (dữ liệu giả lập)", "gv_tran", "DEMO-V58"))
        for i, eid in enumerate(ex_ids, 1):
            conn.execute("INSERT OR REPLACE INTO class_exercises (class_id, exercise_id, order_idx) VALUES (?,?,?)", (CLASS_ID, eid, i))
        for username, name in STUDENTS:
            conn.execute("INSERT OR IGNORE INTO users (username, password, role, full_name) VALUES (?,?,?,?)",
                         (username, DEMO_PASSWORD, "student", f"SV {name} (giả lập)"))
            conn.execute("INSERT OR IGNORE INTO class_enrollments (class_id, student_username) VALUES (?,?)", (CLASS_ID, username))
        conn.commit()
    finally:
        conn.close()

    stamps: list[tuple[str, int, int, int]] = []  # (bảng, id, ngày trước, phút theo thứ tự trong chuỗi)
    for username, _ in STUDENTS:
        for idx, events in SCENARIO.get(username, {}).items():
            eid = ex_ids[idx]
            total = totals[eid]
            for minute, (kind, passed_raw, days, hint, failed, fmt) in enumerate(events):
                passed = _resolve(passed_raw, total)
                ok = passed >= total
                feats = {"error_class": "passed" if ok else ("logic_none" if passed == 0 else "logic_partial"),
                         "status_counts": {}, "ast_flags": {}, "feature_version": "2",
                         "failed_tests": [] if ok else [total if f == LAST else f for f in failed],
                         "format_mismatch_tests": [] if ok else [total if f == LAST else f for f in fmt]}
                if kind == "run":
                    db.save_practice_run(username, eid, passed, total, ok, features=feats)
                    c = db.get_db_connection()
                    try:
                        stamps.append(("practice_runs", c.execute("SELECT MAX(id) FROM practice_runs").fetchone()[0], days, minute))
                    finally:
                        c.close()
                    continue
                is_ask = kind == "ask"
                sid = db.save_submission(username, eid, "# mã giả lập\nprint('demo')", hint if is_ask else 1, passed, total,
                                         ok and not is_ask, "offline", "", attempt_features=None if is_ask else feats)
                if is_ask:
                    c = db.get_db_connection()
                    try:
                        c.execute("UPDATE submissions SET action_type = 'ask_ai' WHERE id = ?", (sid,))
                        c.commit()
                    finally:
                        c.close()
                stamps.append(("submissions", sid, days, minute))
    conn = db.get_db_connection()
    try:
        for table, rid, days, minute in stamps:
            conn.execute(f"UPDATE {table} SET timestamp = datetime('now', 'localtime', ?, ?) WHERE id = ?",
                         (f"-{days} days", f"+{minute} minutes", rid))
        conn.commit()
    finally:
        conn.close()
    return {"class_id": CLASS_ID, "exercise_ids": ex_ids, "students": [u for u, _ in STUDENTS], "events": len(stamps)}


if __name__ == "__main__":
    refuse_unless_temp_db()
    from backend import database as _db
    print(json.dumps(build_demo_class(_db), ensure_ascii=False))
