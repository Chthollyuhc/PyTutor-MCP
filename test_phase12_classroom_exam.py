"""
Kịch bản Kiểm thử Tự động Toàn diện Phase 12 (v3.6 Pro):
1. Cấu hình Trình biên dịch & Sandbox thực tế qua GET /api/health (CompilerConfig)
2. Quản lý Lớp tín chỉ (Credit Classes): GET /api/classes, POST /api/instructor/classes, POST /api/classes/{id}/enroll
3. Quản lý Kỳ thi & Đợt thực hành (Exam Sessions): GET /api/exam-sessions, POST /api/instructor/exam-sessions
4. Chốt chặn bảo mật Chế độ Thi (EXAM Mode Guard):
   - POST /api/submit với exam_session_id: Sandbox vẫn chấm 100% test cases nhưng llm_source='Exam-Mode-Guard' và khóa gợi ý AI
   - POST /api/tutor/chat với exam_session_id: Khóa chat AI và nhắc nhở sinh viên đang trong giờ thi
5. Xóa Kỳ thi / Đợt thực hành: DELETE /api/instructor/exam-sessions/{id}
"""
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db

client = TestClient(app)


def test_phase12_comprehensive():
    init_db()
    print("=" * 80)
    print("🧪 [PHASE 12] BẮT ĐẦU KIỂM THỬ MÔ HÌNH LỚP TÍN CHỈ, KỲ THI & CẤU HÌNH TRÌNH BIÊN DỊCH")
    print("=" * 80)

    # 1. Đăng nhập lấy Token Giảng viên & Sinh viên
    print("\n[1] Xác thực tài khoản Giảng viên và Sinh viên...")
    res_inst = client.post("/api/auth/login", json={"username": "gv_tran", "password": "gv123"})
    assert res_inst.status_code == 200, f"Đăng nhập GV thất bại: {res_inst.text}"
    token_inst = res_inst.json()["access_token"]
    headers_inst = {"Authorization": f"Bearer {token_inst}"}

    res_stu = client.post("/api/auth/login", json={"username": "student", "password": "student123"})
    assert res_stu.status_code == 200, f"Đăng nhập SV thất bại: {res_stu.text}"
    token_stu = res_stu.json()["access_token"]
    headers_stu = {"Authorization": f"Bearer {token_stu}"}
    print("    ✅ PASS: Đăng nhập thành công, đã cấp phát JWT Bearer Tokens.")

    # 2. Kiểm tra Cấu hình Trình biên dịch qua GET /api/health
    print("\n[2] Kiểm tra Cấu hình Trình biên dịch & Sandbox qua GET /api/health...")
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check thất bại: {res_health.text}"
    h_data = res_health.json()
    assert h_data["status"] == "ok"
    assert h_data["version"] == "3.6"
    assert "compiler_config" in h_data, "Thiếu trường compiler_config trong /api/health!"

    c_cfg = h_data["compiler_config"]
    print(f"    • Đường dẫn Trình thông dịch: {c_cfg['executable_path']}")
    print(f"    • Phiên bản Python: {c_cfg['python_version']}")
    print(f"    • Nền tảng: {c_cfg['platform']}")
    print(f"    • Cờ thực thi: {c_cfg['execution_flags']}")
    print(f"    • Bảng mã I/O: {c_cfg['encoding']}")
    print(f"    • Cơ chế cô lập: {c_cfg['isolation_mechanism']}")
    print(f"    • Sandbox Timeout: {c_cfg['sandbox_timeout_seconds']}s")
    print(f"    • Tracer: {c_cfg['tracer_limits']}")
    print(f"    • Database Engine: {c_cfg['database_engine']}")

    assert c_cfg["executable_path"] != ""
    assert c_cfg["sandbox_timeout_seconds"] == 5.0
    print("    ✅ PASS: Cấu hình Trình biên dịch và Sandbox hiển thị minh bạch 100%.")

    # 3. Kiểm tra Quản lý Lớp tín chỉ (Credit Classes)
    print("\n[3] Kiểm tra Quản lý Lớp tín chỉ (GET /api/classes & POST /api/instructor/classes)...")
    res_cls_list = client.get("/api/classes")
    assert res_cls_list.status_code == 200
    classes = res_cls_list.json()
    assert len(classes) >= 2, f"Kỳ vọng ít nhất 2 lớp mẫu, thực tế: {len(classes)}"
    print(f"    • Tìm thấy {len(classes)} lớp tín chỉ ban đầu (cls_it1110_01, cls_it1110_02).")

    # Giảng viên tạo thêm lớp mới
    new_class_payload = {
        "class_code": f"IT1110-TEST-{int(time.time())}",
        "class_name": "Lớp Thực hành Kiểm thử Phase 12",
        "semester": "HK1 2026-2027",
        "description": "Lớp phục vụ automated integration test"
    }
    res_create_cls = client.post("/api/instructor/classes", json=new_class_payload, headers=headers_inst)
    assert res_create_cls.status_code == 200, f"Tạo lớp thất bại: {res_create_cls.text}"
    created_cls = res_create_cls.json()
    assert created_cls["class_code"] == new_class_payload["class_code"]
    test_class_id = created_cls["id"]
    print(f"    ✅ PASS: Giảng viên tạo mới lớp tín chỉ thành công: {created_cls['class_code']} (ID: {test_class_id}).")

    # Sinh viên ghi danh vào lớp
    res_enroll = client.post(f"/api/classes/{test_class_id}/enroll", headers=headers_stu)
    assert res_enroll.status_code == 200
    print(f"    ✅ PASS: Sinh viên ghi danh vào lớp {test_class_id} thành công.")

    # 4. Kiểm tra Quản lý Kỳ thi & Đợt thực hành (Exam Sessions)
    print("\n[4] Kiểm tra Tạo Kỳ thi với Danh sách Bài tập chọn lọc (POST /api/instructor/exam-sessions)...")
    exam_payload = {
        "title": "Kỳ thi Đánh giá Năng lực Giữa kỳ (Chế độ Thi)",
        "class_id": test_class_id,
        "session_type": "EXAM",
        "exercise_ids": ["ex_01_sum_1_to_n", "ex_02_prime_check"],
        "duration_minutes": 45,
        "allow_ai_hints": 0
    }
    res_create_exam = client.post("/api/instructor/exam-sessions", json=exam_payload, headers=headers_inst)
    assert res_create_exam.status_code == 200, f"Tạo kỳ thi thất bại: {res_create_exam.text}"
    created_exam = res_create_exam.json()
    test_exam_id = created_exam["id"]
    assert created_exam["session_type"] == "EXAM"
    assert created_exam["allow_ai_hints"] == 0
    assert len(created_exam["exercise_ids"]) == 2
    assert len(created_exam["exercises"]) == 2
    print(f"    ✅ PASS: Tạo Kỳ thi thành công (ID: {test_exam_id}) với 2 bài tập chọn lọc: {created_exam['exercise_ids']}.")

    # 5. Kiểm tra Chốt chặn Bảo mật Chế độ Thi (EXAM Mode Guard) khi Nộp bài
    print("\n[5] Kiểm tra Chốt chặn Bảo mật Chế độ Thi khi Nộp bài (POST /api/submit)...")
    valid_code = "n = int(input())\ntong = 0\nfor i in range(1, n + 1):\n    tong += i\nprint(tong)"
    submit_payload = {
        "exercise_id": "ex_01_sum_1_to_n",
        "code": valid_code,
        "hint_level": 1,
        "session_id": "test_student_exam",
        "exam_session_id": test_exam_id
    }
    res_submit = client.post("/api/submit", json=submit_payload)
    assert res_submit.status_code == 200, f"Submit thất bại: {res_submit.text}"
    sub_data = res_submit.json()

    # Kiểm tra Sandbox vẫn chấm điểm 100%
    assert sub_data["test_results"]["all_passed"] is True
    assert sub_data["test_results"]["passed_tests"] == 5
    print(f"    • Kết quả chấm Sandbox: {sub_data['test_results']['passed_tests']}/{sub_data['test_results']['total_tests']} tests PASS (All Passed: True)")

    # Kiểm tra Nguồn LLM bị chặn và thay bằng Exam-Mode-Guard
    assert sub_data["llm_source"] == "Exam-Mode-Guard", f"Kỳ vọng Exam-Mode-Guard, thực tế: {sub_data['llm_source']}"
    assert "Chế độ Kỳ thi / Kiểm tra nghiêm ngặt" in sub_data["tutor_hint"], "Gợi ý AI chưa được khóa đúng theo Chế độ Thi!"
    print(f"    • Nguồn sinh gợi ý: {sub_data['llm_source']}")
    print(f"    • Thông báo Sư phạm: {sub_data['tutor_hint'][:90]}...")
    print("    ✅ PASS: MCP Sandbox chấm điểm chính xác 100% nhưng Trợ lý AI bị khóa hoàn toàn theo đúng quy chế thi cử.")

    # 6. Kiểm tra Chốt chặn Bảo mật trong Chatbot làm rõ (POST /api/tutor/chat)
    print("\n[6] Kiểm tra Chốt chặn Bảo mật trong Chat làm rõ (POST /api/tutor/chat)...")
    chat_payload = {
        "exercise_id": "ex_01_sum_1_to_n",
        "code": valid_code,
        "session_id": "test_student_exam",
        "user_message": "Thầy ơi cho em xin đáp án bài này với ạ?",
        "history": [],
        "exam_session_id": test_exam_id
    }
    res_chat = client.post("/api/tutor/chat", json=chat_payload)
    assert res_chat.status_code == 200
    chat_data = res_chat.json()
    assert chat_data["llm_source"] == "Exam-Mode-Guard"
    assert "Chế độ Kỳ thi / Kiểm tra nghiêm ngặt" in chat_data["reply"]
    print(f"    • Phản hồi Chat Guard: {chat_data['reply'][:95]}...")
    print("    ✅ PASS: Chatbot AI từ chối giải thích và giữ nghiêm kỷ luật phòng thi.")

    # 7. Xóa Kỳ thi kiểm thử
    print("\n[7] Kiểm tra Giảng viên xóa Kỳ thi kiểm thử (DELETE /api/instructor/exam-sessions)...")
    res_del = client.delete(f"/api/instructor/exam-sessions/{test_exam_id}", headers=headers_inst)
    assert res_del.status_code == 200
    print(f"    ✅ PASS: Đã xóa thành công Kỳ thi kiểm thử {test_exam_id}.")

    print("\n" + "=" * 80)
    print("🎉 TẤT CẢ 7 HẠNG MỤC KIỂM THỬ CỦA PHASE 12 ĐỀU ĐẠT CHUẨN 100%!")
    print("=" * 80)


if __name__ == "__main__":
    test_phase12_comprehensive()
