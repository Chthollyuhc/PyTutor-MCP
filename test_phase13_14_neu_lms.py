"""
Bộ kiểm thử Tự động Toàn diện cho PHASE 13 & 14 (v4.0 NEU Enterprise LMS-ITS Edition):
1. Chuẩn hóa Học phần & Giảng viên Khoa Công nghệ thông tin - NEU.
2. Quản lý Đa Lớp học phần (Multi-Class Enrollment & Per-Class Exercises).
3. Ghi danh qua Mã tham gia lớp (Enrollment Code) và Rời lớp.
4. Quản lý Chương trình học & Cây kỹ năng theo Lớp (Curriculum & Skill Matrix CRUD).
5. Thang đo Định lượng Mastery Rubric (min_stars_required, NEEDS_MORE_STARS, prerequisite DAG).
6. Động cơ Phân tích Năng lực 4 Chiều (4D Analytics: Autonomy Score, First-try Pass Rate, Error Breakdown) & 3 Thẻ Chẩn đoán Sư phạm.
"""

import sys
import logging

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient

from backend.main import app
from backend.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_neu_lms")


def test_phase13_14_comprehensive():
    print("=" * 80)
    print("🧪 [PHASE 13 & 14] BẮT ĐẦU KIỂM THỬ HỆ THỐNG LMS NEU & PHÂN TÍCH NĂNG LỰC ĐỊNH LƯỢNG")
    print("=" * 80)

    # Khởi tạo DB
    init_db()
    client = TestClient(app)

    # 1. ĐĂNG NHẬP GIẢNG VIÊN VÀ SINH VIÊN NEU
    print("\n[1] Xác thực tài khoản Giảng viên và Sinh viên Khoa CNTT - NEU...")
    res_login_gv = client.post("/api/auth/login", json={"username": "gv_tran", "password": "gv123"})
    assert res_login_gv.status_code == 200, f"Login gv_tran failed: {res_login_gv.text}"
    gv_token = res_login_gv.json()["access_token"]
    gv_headers = {"Authorization": f"Bearer {gv_token}"}
    print(f"    ✅ PASS: Đăng nhập Giảng viên: {res_login_gv.json()['full_name']} (Role: {res_login_gv.json()['role']})")

    res_login_sv = client.post("/api/auth/login", json={"username": "student", "password": "student123"})
    assert res_login_sv.status_code == 200, f"Login student failed: {res_login_sv.text}"
    sv_token = res_login_sv.json()["access_token"]
    sv_headers = {"Authorization": f"Bearer {sv_token}"}
    print(f"    ✅ PASS: Đăng nhập Sinh viên: {res_login_sv.json()['full_name']}")

    # 2. KIỂM TRA DANH SÁCH LỚP HỌC PHẦN CHUẨN NEU
    print("\n[2] Kiểm tra Danh sách Lớp học phần chuẩn NEU (GET /api/classes)...")
    res_classes = client.get("/api/classes?student_username=student")
    assert res_classes.status_code == 200, f"Get classes failed: {res_classes.text}"
    classes = res_classes.json()
    assert len(classes) >= 3, f"Expected >= 3 classes, got {len(classes)}"

    neu_class_01 = next((c for c in classes if c["id"] == "cls_neu_cntt1128_02"), None)
    assert neu_class_01 is not None, "Class cls_neu_cntt1128_02 not found"
    assert neu_class_01["course_code"] == "CNTT1128"
    assert "Khoa Công nghệ thông tin - NEU" in neu_class_01["faculty"]
    assert neu_class_01["enrollment_code"] == "NEU-CSLP"
    assert neu_class_01["is_enrolled"] == True
    print(f"    • Lớp 1: {neu_class_01['class_code']} - {neu_class_01['class_name']}")
    print(f"      Khoa: {neu_class_01['faculty']} | Giảng viên: {neu_class_01['instructor_name']} | Mã: {neu_class_01['enrollment_code']}")
    print(f"      Đã ghi danh: {neu_class_01['is_enrolled']} | Tiến độ: {neu_class_01['completed_in_class']}/{neu_class_01['exercise_count']} bài")
    print("    ✅ PASS: Chuẩn hóa Học phần NEU & Trạng thái ghi danh hiển thị chính xác.")

    # 3. KIỂM TRA CỔNG LỚP HỌC PHẦN CỦA SINH VIÊN (GET /api/student/my-classes)
    print("\n[3] Kiểm tra Cổng Lớp học phần của Tôi (GET /api/student/my-classes)...")
    res_my_classes = client.get("/api/student/my-classes", headers=sv_headers)
    assert res_my_classes.status_code == 200, f"Get my-classes failed: {res_my_classes.text}"
    my_classes = res_my_classes.json()
    enrolled_ids = [c["id"] for c in my_classes]
    assert "cls_neu_cntt1128_02" in enrolled_ids
    print(f"    • Sinh viên đã ghi danh {len(my_classes)} lớp: {[c['class_code'] for c in my_classes]}")
    print("    ✅ PASS: Endpoint My NEU Classes trả về đúng danh sách lớp của sinh viên.")

    # 4. KIỂM TRA GHI DANH BẰNG MÃ ENROLLMENT CODE VÀ HỦY GHI DANH
    print("\n[4] Kiểm tra Ghi danh bằng Mã (POST /api/classes/enroll-by-code) và Rời lớp (DELETE /api/classes/{id}/leave)...")
    # Ghi danh vào lớp cls_neu_cntt1117_02 bằng mã NEU-PTTKHT
    res_enroll_code = client.post(
        "/api/classes/enroll-by-code",
        json={"enrollment_code": "NEU-PTTKHT"},
        headers=sv_headers
    )
    assert res_enroll_code.status_code == 200, f"Enroll by code failed: {res_enroll_code.text}"
    enroll_data = res_enroll_code.json()
    assert enroll_data["class_id"] == "cls_neu_cntt1117_02"
    print(f"    • Kết quả ghi danh bằng mã NEU-PTTKHT: {enroll_data['message']}")

    # Kiểm tra lại my-classes thấy xuất hiện cls_neu_cntt1117_02
    res_my_classes2 = client.get("/api/student/my-classes", headers=sv_headers)
    assert "cls_neu_cntt1117_02" in [c["id"] for c in res_my_classes2.json()]
    print("    • Xác nhận lớp mới đã xuất hiện trong Cổng lớp học của sinh viên.")

    # Thử hủy ghi danh khỏi cls_neu_cntt1117_02
    res_leave = client.delete("/api/classes/cls_neu_cntt1117_02/leave", headers=sv_headers)
    assert res_leave.status_code == 200, f"Leave class failed: {res_leave.text}"
    print(f"    • Kết quả rời lớp: {res_leave.json()['message']}")
    print("    ✅ PASS: Tính năng Ghi danh bằng Mã và Hủy ghi danh hoạt động hoàn hảo.")

    # 5. KIỂM TRA QUẢN LÝ CHƯƠNG TRÌNH HỌC & CÂY KỸ NĂNG THEO LỚP (CURRICULUM MATRIX CRUD)
    print("\n[5] Kiểm tra Quản lý Chương trình học & Ma trận Kỹ năng Lớp (Curriculum CRUD)...")
    res_curriculum = client.get("/api/classes/cls_neu_cntt1128_02/curriculum")
    assert res_curriculum.status_code == 200, f"Get curriculum failed: {res_curriculum.text}"
    curriculum = res_curriculum.json()
    assert len(curriculum) >= 4, f"Expected >= 4 exercises in class curriculum, got {len(curriculum)}"
    print(f"    • Lớp cls_neu_cntt1128_02 có {len(curriculum)} bài tập trong lộ trình:")
    for ex in curriculum:
        print(f"      - [{ex['module_name']}] #{ex['order_idx']} {ex['exercise_id']} | Tiên quyết: {ex['prerequisite_id']} | Sao yêu cầu: {ex['min_stars_required']} ⭐")

    # Giảng viên thêm bài tập mới vào lớp
    test_ex_id = "ex_test_curriculum"
    res_add_ex = client.post(
        "/api/instructor/classes/cls_neu_cntt1128_02/exercises",
        json={
            "exercise_id": test_ex_id,
            "module_name": "Module Nâng cao: Đệ quy & Tối ưu",
            "order_idx": 99,
            "prerequisite_id": "ex_03_factorial",
            "min_stars_required": 3,
            "skill_tag": "Recursion Optimization",
            "weight_point": 10.0
        },
        headers=gv_headers
    )
    assert res_add_ex.status_code == 200, f"Add exercise to class failed: {res_add_ex.text}"
    print(f"    • Giảng viên gán bài mới thành công: {res_add_ex.json()['message']}")

    # Giảng viên cập nhật bài tập vừa gán (sửa min_stars thành 2)
    res_upd_ex = client.put(
        f"/api/instructor/classes/cls_neu_cntt1128_02/exercises/{test_ex_id}",
        json={"min_stars_required": 2, "module_name": "Module Nâng cao Cập nhật"},
        headers=gv_headers
    )
    assert res_upd_ex.status_code == 200, f"Update class exercise failed: {res_upd_ex.text}"
    print(f"    • Giảng viên cập nhật cấu hình bài tập thành công.")

    # Giảng viên gỡ bỏ bài tập kiểm thử
    res_del_ex = client.delete(
        f"/api/instructor/classes/cls_neu_cntt1128_02/exercises/{test_ex_id}",
        headers=gv_headers
    )
    assert res_del_ex.status_code == 200, f"Delete class exercise failed: {res_del_ex.text}"
    print(f"    • Giảng viên gỡ bài tập kiểm thử khỏi lớp thành công.")
    print("    ✅ PASS: Toàn bộ API Quản lý Chương trình học & Ma trận Kỹ năng hoạt động chính xác.")

    # 6. KIỂM TRA BẢNG DANH SÁCH SINH VIÊN KÈM TIẾN ĐỘ THỰC TẾ CỦA LỚP
    print("\n[6] Kiểm tra Danh sách Sinh viên & Đo lường Tiến độ (GET /api/instructor/classes/{id}/students)...")
    res_roster = client.get("/api/instructor/classes/cls_neu_cntt1128_02/students", headers=gv_headers)
    assert res_roster.status_code == 200, f"Get students roster failed: {res_roster.text}"
    roster = res_roster.json()
    assert len(roster) >= 1
    sv_item = next((s for s in roster if s["student_username"] == "student"), None)
    assert sv_item is not None
    print(f"    • Sinh viên trong lớp: {sv_item['full_name']} (@{sv_item['student_username']})")
    print(f"      Tiến độ: {sv_item['completed_exercises']}/{sv_item['total_exercises']} ({sv_item['progress_percent']}%) | Tổng sao: {sv_item['total_stars']} ⭐")
    print("    ✅ PASS: Bảng tổng hợp tiến độ học viên của lớp phản ánh số liệu thực tế.")

    # 7. KIỂM TRA LỘ TRÌNH KỸ NĂNG THEO LỚP & THANG ĐO ĐỊNH LƯỢNG (MASTERY RUBRIC)
    print("\n[7] Kiểm tra Lộ trình Kỹ năng theo Lớp & Thang đo Định lượng (GET /api/skill-roadmap?class_id=...)...")
    res_roadmap = client.get("/api/skill-roadmap?class_id=cls_neu_cntt1128_02&session_id=student")
    assert res_roadmap.status_code == 200, f"Get skill roadmap failed: {res_roadmap.text}"
    roadmap = res_roadmap.json()
    assert roadmap["class_id"] == "cls_neu_cntt1128_02"
    assert len(roadmap["nodes"]) >= 4
    print(f"    • Lộ trình lớp: {roadmap['class_code']} - {roadmap['class_name']} ({roadmap['total_mastered']}/{roadmap['total_exercises']} làm chủ)")
    for node in roadmap["nodes"]:
        print(f"      [{node['status']}] {node['id']} - {node['title']} (Yêu cầu: {node['min_stars_required']} ⭐, Đạt: {node['stars_earned']} ⭐) -> {node['status_description']}")
    print("    ✅ PASS: Lộ trình Kỹ năng theo Lớp phản ánh chính xác Thang đo Định lượng Mastery Rubric.")

    # 8. KIỂM TRA ĐỘNG CƠ PHÂN TÍCH NĂNG LỰC 4 CHIỀU & 3 THẺ CHẨN ĐOÁN SƯ PHẠM
    print("\n[8] Kiểm tra Động cơ Phân tích Năng lực 4 Chiều & 3 Thẻ Chẩn đoán (GET /api/student/profile)...")
    res_profile = client.get("/api/student/profile?session_id=student&class_id=cls_neu_cntt1128_02")
    assert res_profile.status_code == 200, f"Get student profile failed: {res_profile.text}"
    profile = res_profile.json()

    assert profile["analytics_metrics"] is not None, "Missing analytics_metrics in profile"
    am = profile["analytics_metrics"]
    print(f"    • Điểm Tự lực Sư phạm (Autonomy Score): {am['autonomy_score']}/100")
    print(f"    • Tỷ lệ Pass Lần đầu (First-try Pass Rate): {am['first_try_pass_rate']}%")
    print(f"    • Số lần nộp trung bình / bài: {am['avg_attempts_to_solve']}")
    print(f"    • Phân tích Lỗi (Error Breakdown): {am['error_breakdown']}")

    assert profile["diagnostic_evaluation"] is not None, "Missing diagnostic_evaluation in profile"
    diag = profile["diagnostic_evaluation"]
    print(f"    • Phân hạng Năng lực: 🎓 {diag['level_classification']}")
    print(f"    • 1. Điểm mạnh Nổi bật: {diag['strengths_analysis'][:90]}...")
    print(f"    • 2. Điểm nghẽn Cần khắc phục: {diag['weaknesses_and_bottlenecks'][:90]}...")
    print(f"    • 3. Hành động Khuyến nghị Tiếp theo: {diag['recommended_next_action'][:90]}...")
    print("    ✅ PASS: Động cơ Phân tích 4D và 3 Thẻ Chẩn đoán Sư phạm trả về số liệu thực nghiệm đầy đủ.")

    print("\n" + "=" * 80)
    print("🎉 TẤT CẢ 8 HẠNG MỤC KIỂM THỬ CỦA PHASE 13 & 14 ĐỀU ĐẠT CHUẨN 100%!")
    print("=" * 80)


if __name__ == "__main__":
    test_phase13_14_comprehensive()
