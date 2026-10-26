"""
Bộ Kiểm Thử Tự Động QA Audit Hotfix (Phase 15.3) - PyTutor-MCP.
Kiểm tra 5 điểm sửa lỗi logic, API methods, đồng bộ dữ liệu và Mastery Rubric.
"""
import sys
import os
import json
import sqlite3

if sys.platform.startswith("win"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from fastapi.testclient import TestClient
from backend.main import app
from backend.auth import create_token
from backend.database import get_db_connection

client = TestClient(app)

def run_tests():
    print("=" * 80)
    print("🧪 [PHASE 15.3] BẮT ĐẦU KIỂM THỬ QA AUDIT HOTFIX & DATA INTEGRITY")
    print("=" * 80)

    # 1. Kiểm tra GET /api/auth/me
    print("\n[1] Kiểm tra Endpoint GET /api/auth/me (Sửa lỗi NameError: get_db_connection)...")
    student_token = create_token("student", "student", "Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)")
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {student_token}"})
    assert res_me.status_code == 200, f"Expected 200, got {res_me.status_code}: {res_me.text}"
    user_info = res_me.json()
    assert user_info["username"] == "student"
    assert "K65" in user_info["full_name"]
    print(f"    ✅ PASS: GET /api/auth/me trả về HTTP 200: {user_info['full_name']} (Role: {user_info['role']})")

    # 2. Kiểm tra hỗ trợ cả DELETE và POST cho /api/classes/{class_id}/leave
    print("\n[2] Kiểm tra HTTP Methods cho Route Rời Lớp (/api/classes/{id}/leave)...")
    # Ghi danh thử vào một lớp
    client.post("/api/classes/enroll-by-code", json={"enrollment_code": "NEU-PTTKHT"}, headers={"Authorization": f"Bearer {student_token}"})
    # Rời lớp bằng DELETE
    res_del = client.delete("/api/classes/cls_neu_cntt1117_02/leave", headers={"Authorization": f"Bearer {student_token}"})
    assert res_del.status_code == 200, f"Expected 200 for DELETE, got {res_del.status_code}"
    # Ghi danh lại
    client.post("/api/classes/enroll-by-code", json={"enrollment_code": "NEU-PTTKHT"}, headers={"Authorization": f"Bearer {student_token}"})
    # Rời lớp bằng POST
    res_post = client.post("/api/classes/cls_neu_cntt1117_02/leave", headers={"Authorization": f"Bearer {student_token}"})
    assert res_post.status_code == 200, f"Expected 200 for POST, got {res_post.status_code}"
    print("    ✅ PASS: Tuyệt đối tương thích cả DELETE và POST /api/classes/{class_id}/leave.")

    # 3. Kiểm tra Mastery Rubric trong GET /api/classes/{class_id}/curriculum
    print("\n[3] Kiểm tra Mastery Rubric trong Curriculum Matrix...")
    res_curr = client.get("/api/classes/cls_neu_cntt1128_02/curriculum?student_username=student")
    assert res_curr.status_code == 200
    curr_items = {item["exercise_id"]: item for item in res_curr.json()}
    
    # ex_01_sum_1_to_n phải là MASTERED vì đạt 3 sao >= min_stars (2)
    ex1 = curr_items["ex_01_sum_1_to_n"]
    assert ex1["status"] == "MASTERED", f"Expected MASTERED, got {ex1['status']}"
    assert ex1["stars_earned"] == 3
    assert ex1["is_unlocked"] is True
    print(f"    ✅ PASS: ex_01 đạt {ex1['stars_earned']}/{ex1['min_stars_required']} ⭐ -> Trạng thái: {ex1['status']}")

    # ex_03_factorial phải là AVAILABLE vì tiên quyết ex_01 đã MASTERED
    ex3 = curr_items["ex_03_factorial"]
    assert ex3["status"] == "AVAILABLE", f"Expected AVAILABLE, got {ex3['status']}"
    assert ex3["is_unlocked"] is True
    print(f"    ✅ PASS: ex_03 (tiên quyết ex_01) -> Trạng thái: {ex3['status']} ({ex3['status_description']})")

    # ex_04_reverse_string phải là LOCKED vì tiên quyết ex_03 chưa MASTERED
    ex4 = curr_items["ex_04_reverse_string"]
    assert ex4["status"] == "LOCKED", f"Expected LOCKED, got {ex4['status']}"
    assert ex4["is_unlocked"] is False
    print(f"    ✅ PASS: ex_04 (tiên quyết ex_03) -> Trạng thái: {ex4['status']} ({ex4['status_description']})")

    # 4. Kiểm tra Mastery Rubric trong GET /api/skill-roadmap
    print("\n[4] Kiểm tra Mastery Rubric trong Skill Roadmap DAG Tree...")
    res_map = client.get("/api/skill-roadmap?session_id=student&class_id=cls_neu_cntt1128_02")
    assert res_map.status_code == 200
    map_nodes = {n["id"]: n for n in res_map.json()["nodes"]}
    assert map_nodes["ex_01_sum_1_to_n"]["status"] == "MASTERED"
    assert map_nodes["ex_03_factorial"]["status"] == "AVAILABLE"
    assert map_nodes["ex_04_reverse_string"]["status"] == "LOCKED"
    print("    ✅ PASS: Cây Kỹ năng DAG phản ánh 100% nhất quán với Curriculum Matrix.")

    # 5. Kiểm tra trường hợp NEEDS_MORE_STARS
    print("\n[5] Kiểm thử mô phỏng nhánh trạng thái NEEDS_MORE_STARS...")
    # Tạo học sinh tạm thời có 1 sao cho bài yêu cầu 2 sao
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_exercise_stars (username, exercise_id, stars_earned) VALUES ('temp_test_student', 'ex_01_sum_1_to_n', 1)")
    c.execute("INSERT INTO submissions (session_id, exercise_id, code, hint_level, passed_tests, total_tests, all_passed, llm_source, tutor_hint) VALUES ('temp_test_student', 'ex_01_sum_1_to_n', '# pass code', 3, 5, 5, 1, 'test', 'hint')")
    conn.commit()
    conn.close()

    res_needs = client.get("/api/classes/cls_neu_cntt1128_02/curriculum?student_username=temp_test_student")
    assert res_needs.status_code == 200
    temp_items = {item["exercise_id"]: item for item in res_needs.json()}
    ex1_temp = temp_items["ex_01_sum_1_to_n"]
    assert ex1_temp["status"] == "NEEDS_MORE_STARS", f"Expected NEEDS_MORE_STARS, got {ex1_temp['status']}"
    assert ex1_temp["stars_earned"] == 1
    assert ex1_temp["min_stars_required"] == 2
    # Bài ex_03 phụ thuộc ex_01 chưa đạt 2 sao nên phải bị LOCKED!
    ex3_temp = temp_items["ex_03_factorial"]
    assert ex3_temp["status"] == "LOCKED", f"Expected LOCKED for ex_03 when prereq only has 1 star, got {ex3_temp['status']}"
    print(f"    ✅ PASS: Đạt 1/2 ⭐ -> Trạng thái: {ex1_temp['status']} ({ex1_temp['status_description']})")
    print(f"    ✅ PASS: Bài phụ thuộc kế tiếp được khóa chặt (LOCKED) theo đúng quy tắc sư phạm.")

    # Dọn dẹp dữ liệu học sinh tạm
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM user_exercise_stars WHERE username = 'temp_test_student'")
    c.execute("DELETE FROM submissions WHERE session_id = 'temp_test_student'")
    conn.commit()
    conn.close()

    # 6. Kiểm tra Profile Analytics Metrics
    print("\n[6] Kiểm tra Điểm Tự lực trong GET /api/student/profile...")
    res_prof = client.get("/api/student/profile?session_id=student")
    assert res_prof.status_code == 200
    prof_data = res_prof.json()
    assert "analytics_metrics" in prof_data
    assert "autonomy_score" in prof_data["analytics_metrics"]
    autonomy = prof_data["analytics_metrics"]["autonomy_score"]
    print(f"    ✅ PASS: Autonomy Score tồn tại chuẩn xác: {autonomy}/100")

    print("\n" + "=" * 80)
    print("🎉 TẤT CẢ 6 HẠNG MỤC KIỂM THỬ QA AUDIT HOTFIX ĐỀU ĐẠT CHUẨN 100%!")
    print("=" * 80)

if __name__ == "__main__":
    run_tests()
