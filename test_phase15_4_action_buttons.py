"""
Test Suite: Phase 15.4 Verification
- Tách biệt 3 hành động: Chạy thử, Hỏi Gia sư AI (action_type='ask_ai'), Nộp bài (action_type='submit')
- Kiểm tra tính toán sao tự lực và không lưu sao khi hỏi AI
- Kiểm tra API health compiler_config python_version
"""

import sys
import os
from fastapi.testclient import TestClient

# Đảm bảo UTF-8 output trên Windows console
if sys.platform.startswith("win"):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

from backend.main import app

client = TestClient(app)

def test_phase15_4_actions():
    print("=" * 80)
    print("🧪 [PHASE 15.4] BẮT ĐẦU KIỂM THỬ TÁCH BIỆT 3 NÚT & ĐỒNG BỘ DỮ LIỆU GIAO DIỆN")
    print("=" * 80)

    # 1. Health check & compiler_config python_version
    print("\n[1] Kiểm tra Thông số Môi trường Thực thi (GET /api/health)...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check thất bại: {res.status_code}"
    data = res.json()
    compiler_config = data.get("compiler_config", {})
    assert "python_version" in compiler_config or "version" in compiler_config
    version = compiler_config.get("python_version") or compiler_config.get("version")
    print(f"    ✅ PASS: Python Interpreter Version: {version}")

    # 2. Hỏi Gia sư AI (action_type='ask_ai') với bài làm đúng hoặc sai
    print("\n[2] Kiểm tra Hành động 'Hỏi Gia sư AI' (action_type='ask_ai')...")
    payload_ask = {
        "exercise_id": "ex_01_sum_1_to_n",
        "code": "n = int(input())\ntong = n * 2\nprint(tong)",
        "hint_level": 2,
        "session_id": "test_phase15_4_user",
        "action_type": "ask_ai"
    }
    res_ask = client.post("/api/submit", json=payload_ask)
    assert res_ask.status_code == 200, f"Submit ask_ai thất bại: {res_ask.status_code}"
    ask_data = res_ask.json()
    assert ask_data["stars_earned"] == 0, f"ask_ai không được cấp sao nhưng lại có {ask_data['stars_earned']} sao"
    assert len(ask_data["new_badges"]) == 0, "ask_ai không được mở khóa huy hiệu"
    assert len(ask_data["tutor_hint"]) > 0, "ask_ai phải có tutor_hint"
    print(f"    ✅ PASS: 'ask_ai' trả về gợi ý Mức 2, stars_earned = 0, new_badges = []")

    # 3. Nộp bài chính thức (action_type='submit') với code đúng 100%
    print("\n[3] Kiểm tra Hành động 'Nộp bài chính thức' (action_type='submit')...")
    payload_submit = {
        "exercise_id": "ex_01_sum_1_to_n",
        "code": "n = int(input())\nprint(n * (n + 1) // 2)",
        "hint_level": 1,
        "session_id": "test_phase15_4_user",
        "action_type": "submit"
    }
    res_submit = client.post("/api/submit", json=payload_submit)
    assert res_submit.status_code == 200, f"Submit nộp bài thất bại: {res_submit.status_code}"
    sub_data = res_submit.json()
    assert sub_data["test_results"]["all_passed"] is True, "Bài nộp phải pass 100% test cases"
    # Vì trước đó đã từng hỏi AI ở Mức 2 (ở test 2), sao tự lực phải đạt đúng 2 Sao
    print(f"    • Số sao đạt được: {sub_data['stars_earned']} ⭐ (Do lần trước đó đã dùng gợi ý Mức 2)")
    assert sub_data["stars_earned"] == 2, f"Kỳ vọng 2 sao nhưng nhận được {sub_data['stars_earned']}"
    print(f"    ✅ PASS: 'submit' chính thức cấp sao tự lực dựa trên lịch sử gợi ý: {sub_data['stars_earned']} ⭐")

    # 4. Kiểm tra student roster API
    print("\n[4] Kiểm tra Roster Giảng viên (GET /api/instructor/classes/cls_neu_cntt1128_02/students)...")
    res_login_gv = client.post("/api/auth/login", json={"username": "gv_tran", "password": "gv123"})
    assert res_login_gv.status_code == 200, f"Login gv_tran failed: {res_login_gv.text}"
    gv_token = res_login_gv.json()["access_token"]
    gv_headers = {"Authorization": f"Bearer {gv_token}"}

    res_roster = client.get("/api/instructor/classes/cls_neu_cntt1128_02/students", headers=gv_headers)
    assert res_roster.status_code == 200
    roster = res_roster.json()
    assert len(roster) > 0
    first_st = roster[0]
    assert "student_username" in first_st
    assert "completed_exercises" in first_st
    assert "total_stars" in first_st
    print(f"    ✅ PASS: Roster có đầy đủ student_username (@{first_st['student_username']}), completed_exercises ({first_st['completed_exercises']}), total_stars ({first_st['total_stars']} ⭐)")

    print("\n" + "=" * 80)
    print("🎉 TẤT CẢ CÁC HẠNG MỤC KIỂM THỬ PHASE 15.4 ĐỀU ĐẠT CHUẨN 100%!")
    print("=" * 80)

if __name__ == "__main__":
    test_phase15_4_actions()
