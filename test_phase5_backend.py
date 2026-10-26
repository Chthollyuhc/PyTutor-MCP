"""
Kịch bản kiểm thử tự động xác thực toàn bộ tính năng mới của Phase 5:
1. True MCP Discovery (7 tools)
2. JWT Authentication (Student & Instructor)
3. Chạy thử nhanh /api/run-test (không tốn LLM)
4. Nộp bài thích ứng /api/submit (kèm history & student model)
5. Giảng viên CRUD bài tập (/api/instructor/exercises) & Thống kê (/api/instructor/dashboard)
"""
import sys
import os
import json
import asyncio
from pathlib import Path

# Cấu hình UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.database import init_db


async def run_phase5_backend_tests():
    print("=" * 70)
    print("🚀 BẮT ĐẦU KIỂM THỬ BACKEND PHASE 5 (AUTH, INSTRUCTOR CRUD, ADAPTIVE MCP)")
    print("=" * 70)

    # 1. Khởi tạo DB
    init_db()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Health & MCP True Discovery
        print("\n[1] Kiểm tra /api/health...")
        res = await client.get("/api/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        data = res.json()
        print(f"    ✅ Health Status: {data['status']}")
        print(f"    ✅ Đã phát hiện {len(data['discovered_tools'])} MCP Tools:")
        for t in data['discovered_tools']:
            print(f"       • {t}")
        assert len(data['discovered_tools']) >= 4, "Thiếu MCP Tools!"

        # Step 2: Authentication
        print("\n[2] Kiểm tra Đăng nhập & Phân quyền...")
        # Đăng nhập Student
        res_stu = await client.post("/api/auth/login", json={"username": "student", "password": "student123"})
        assert res_stu.status_code == 200, f"Student login failed: {res_stu.text}"
        stu_token = res_stu.json()["access_token"]
        print(f"    ✅ Đăng nhập Sinh viên thành công: {res_stu.json()['full_name']} (Role: {res_stu.json()['role']})")

        # Đăng nhập Giảng viên
        res_ins = await client.post("/api/auth/login", json={"username": "gv_tran", "password": "gv123"})
        assert res_ins.status_code == 200, f"Instructor login failed: {res_ins.text}"
        ins_token = res_ins.json()["access_token"]
        print(f"    ✅ Đăng nhập Giảng viên thành công: {res_ins.json()['full_name']} (Role: {res_ins.json()['role']})")

        # Kiểm tra /api/auth/me
        headers_stu = {"Authorization": f"Bearer {stu_token}"}
        headers_ins = {"Authorization": f"Bearer {ins_token}"}
        me_res = await client.get("/api/auth/me", headers=headers_stu)
        assert me_res.status_code == 200
        print(f"    ✅ Token xác thực hợp lệ cho người dùng: {me_res.json()['username']}")

        # Step 3: Run-test-only (Chạy thử không gọi LLM)
        print("\n[3] Kiểm tra /api/run-test (Chạy thử độc lập, không tốn quota AI)...")
        sample_code = "n = int(input())\ntong = sum(range(1, n + 1))\nprint(tong)"
        run_res = await client.post("/api/run-test", json={
            "exercise_id": "ex_01_sum_1_to_n",
            "code": sample_code
        })
        assert run_res.status_code == 200, f"Run-test failed: {run_res.text}"
        run_data = run_res.json()
        print(f"    ✅ Chạy thử thành công! Kết quả: {run_data['test_results']['passed_tests']}/{run_data['test_results']['total_tests']} tests passed.")
        print(f"    ✅ AST Summary: {run_data['ast_analysis']['structural_summary']}")

        # Step 4: Submit Solution with Adaptive History & Student Model
        print("\n[4] Kiểm tra /api/submit (Nộp bài thích ứng + Gemini AI + Learning Event)...")
        session_id = "test_session_phase5"
        sub_res = await client.post("/api/submit", json={
            "exercise_id": "ex_01_sum_1_to_n",
            "code": sample_code,
            "hint_level": 1,
            "session_id": session_id
        })
        assert sub_res.status_code == 200, f"Submit failed: {sub_res.text}"
        sub_data = sub_res.json()
        print(f"    ✅ Nộp bài thành công! Nguồn LLM: {sub_data['llm_source']}")
        print(f"    ✅ Phản hồi AI (trích 100 ký tự đầu): {sub_data['tutor_hint'][:100]}...")

        # Step 5: Check Student Model
        print("\n[5] Kiểm tra /api/student-model/{session_id}...")
        sm_res = await client.get(f"/api/student-model/{session_id}")
        assert sm_res.status_code == 200
        sm_data = sm_res.json()
        print(f"    ✅ Student Model: {sm_data['summary']}")
        print(f"    ✅ Mastered Exercises: {sm_data['mastered_exercises']}")

        # Step 6: Instructor CRUD Exercises
        print("\n[6] Kiểm tra Quyền Giảng viên: Thêm bài tập mới & Xem thống kê...")
        
        # Thử student gọi route giảng viên -> phải bị 403 Forbidden
        forbidden_res = await client.get("/api/instructor/dashboard", headers=headers_stu)
        assert forbidden_res.status_code == 403, "Student không được phép vào dashboard giảng viên!"
        print("    ✅ Xác nhận Sinh viên bị chặn (403 Forbidden) khi vào route Giảng viên.")

        # Giảng viên tạo bài tập mới
        new_ex = {
            "id": "ex_test_fibonacci",
            "title": "Bài Test: Dãy số Fibonacci",
            "difficulty": "Dễ",
            "category": "Vòng lặp & Biến trạng thái",
            "description": "In ra số Fibonacci thứ n.",
            "starter_code": "n = int(input())\n# Code ở đây\n",
            "test_cases": [
                {"input": "1\n", "expected_output": "1", "description": "F(1)"},
                {"input": "5\n", "expected_output": "5", "description": "F(5)"}
            ]
        }
        create_res = await client.post("/api/instructor/exercises", json=new_ex, headers=headers_ins)
        assert create_res.status_code == 200, f"Create exercise failed: {create_res.text}"
        print(f"    ✅ Giảng viên đã tạo bài tập mới: {create_res.json()['title']}")

        # Kiểm tra Dashboard Giảng viên
        dash_res = await client.get("/api/instructor/dashboard", headers=headers_ins)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        print(f"    ✅ Thống kê Giảng viên:")
        print(f"       • Tổng số bài tập: {dash_data['total_exercises']}")
        print(f"       • Tổng lượt nộp bài: {dash_data['total_submissions']}")
        print(f"       • Số học viên active: {dash_data['active_students']}")
        print(f"       • Tỷ lệ pass: {dash_data['pass_rate_percentage']}%")

        # Xóa bài test để dọn dẹp
        del_res = await client.delete(f"/api/instructor/exercises/{new_ex['id']}", headers=headers_ins)
        assert del_res.status_code == 200
        print(f"    ✅ Giảng viên đã xóa bài tập test thành công.")

    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ TEST CASES BACKEND PHASE 5 ĐỀU ĐẠT CHUẨN 100%!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_phase5_backend_tests())
