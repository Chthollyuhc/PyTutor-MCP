"""
Kịch bản Kiểm thử Tự động Phase 10: Gamification, 3-Star Autonomy & Senior Pythonic Code Review.
Kiểm tra:
1. calculate_autonomy_stars: Logic tính sao chính xác (0, 1, 2, 3 sao)
2. Huy hiệu không còn được cấp; dữ liệu sao tự lực vẫn được ghi nhận
3. POST /api/tutor/pythonic-review: Senior Reviewer chấm điểm Clean Code (>= 70) và code Pythonic
4. GET /api/leaderboard: Bảng xếp hạng lớp học sắp xếp theo tổng sao giảm dần
5. GET /api/student/achievements: Truy xuất số sao và bài đã hoàn thành
6. POST /api/submit: Tích hợp tính sao tự động khi nộp bài giải đúng 100%
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
from backend.database import (
    init_db,
    calculate_autonomy_stars,
    save_exercise_stars,
    get_user_achievements,
    get_class_leaderboard
)
from backend.auth import create_token

client = TestClient(app)


def test_phase10_comprehensive():
    init_db()
    print("=" * 75)
    print("🧪 [PHASE 10] BẮT ĐẦU KIỂM THỬ GAMIFICATION & PYTHONIC CODE REVIEW")
    print("=" * 75)

    # 1. Kiểm tra Thuật toán Tính Sao Tự Lực
    print("\n[1] Kiểm tra Thuật toán Đánh giá Sao Tự Lực (Autonomy Stars)...")
    assert calculate_autonomy_stars(attempt_count=1, max_hint_level_used=1, all_passed=False) == 0, "Chưa pass phải 0 sao!"
    assert calculate_autonomy_stars(attempt_count=1, max_hint_level_used=1, all_passed=True) == 3, "Hint level 1 phải 3 sao!"
    assert calculate_autonomy_stars(attempt_count=3, max_hint_level_used=2, all_passed=True) == 2, "Hint level 2 phải 2 sao!"
    assert calculate_autonomy_stars(attempt_count=5, max_hint_level_used=3, all_passed=True) == 1, "Hint level 3 phải 1 sao!"
    print("    ✅ PASS: Thuật toán tính sao tự lực đạt chuẩn 100% (0, 1, 2, 3 sao).")

    # 2. Huy hiệu đã bị loại khỏi luồng cấp mới; sao tự lực vẫn được lưu.
    print("\n[2] Kiểm tra không cấp huy hiệu mới và vẫn ghi nhận sao tự lực...")
    test_user = f"gamer_{int(time.time())}"
    test_headers = {"Authorization": f"Bearer {create_token(test_user, 'student', 'Gamer Test')}"}
    # Hoàn thành bài 1 -> mở FIRST_SOLVE
    res1 = save_exercise_stars(test_user, "ex_01_sum_1_to_n", stars=3, clean_score=85)
    assert res1.get("new_badges") == [], "Không được cấp huy hiệu mới"
    assert res1["stars_earned"] == 3

    # Hoàn thành thêm 2 bài 3 sao -> mở INDEPENDENT_HERO
    save_exercise_stars(test_user, "ex_02_prime_check", stars=3, clean_score=88)
    res3 = save_exercise_stars(test_user, "ex_03_factorial", stars=3, clean_score=92)
    assert res3.get("new_badges") == []
    print("    ✅ PASS: Sao được ghi nhận; không có huy hiệu mới được cấp.")

    # 3. Kiểm tra POST /api/tutor/pythonic-review
    print("\n[3] Kiểm tra POST /api/tutor/pythonic-review (Senior Python Reviewer)...")
    good_code = """n = int(input())
tong = 0
for i in range(1, n + 1):
    tong += i
print(tong)
"""
    rev_res = client.post(
        "/api/tutor/pythonic-review",
        headers=test_headers,
        json={
            "exercise_id": "ex_01_sum_1_to_n",
            "code": good_code,
            "username": test_user
        }
    )
    assert rev_res.status_code == 200, f"Pythonic review thất bại: {rev_res.text}"
    rev_data = rev_res.json()
    assert rev_data["clean_score"] >= 70, f"Điểm Clean Code phải >= 70, thực tế: {rev_data['clean_score']}"
    assert len(rev_data["strengths"]) > 0, "Thiếu nhận xét điểm mạnh!"
    assert len(rev_data["improvements"]) > 0, "Thiếu nhận xét cải thiện!"
    assert len(rev_data["pythonic_code"]) > 0, "Thiếu code Pythonic mẫu!"
    assert len(rev_data["explanation"]) > 0, "Thiếu giải thích!"
    print(f"    ✅ PASS: Clean Code Score: {rev_data['clean_score']}/100 | Pythonic Code:\n    {rev_data['pythonic_code'].strip()}")

    # 4. Kiểm tra GET /api/leaderboard (Bảng Xếp Hạng Lớp Học)
    print("\n[4] Kiểm tra GET /api/leaderboard (Bảng Vàng Lớp Học)...")
    lead_res = client.get("/api/leaderboard?limit=10", headers=test_headers)
    assert lead_res.status_code == 200, f"Leaderboard thất bại: {lead_res.text}"
    lead_data = lead_res.json()
    leaderboard = lead_data.get("leaderboard", [])
    assert len(leaderboard) > 0, "Leaderboard không được rỗng!"

    # Kiểm tra thứ tự giảm dần theo tổng sao
    stars_list = [item["total_stars"] for item in leaderboard]
    assert stars_list == sorted(stars_list, reverse=True), "Leaderboard chưa sắp xếp giảm dần theo tổng sao!"
    top1 = leaderboard[0]
    print(f"    ✅ PASS: Quán quân hiện tại: {top1['full_name']} ({top1['username']}) - {top1['total_stars']} ⭐")

    # 5. Kiểm tra GET /api/student/achievements
    print("\n[5] Kiểm tra GET /api/student/achievements (Hồ sơ Thành tích)...")
    ach_res = client.get("/api/student/achievements", headers=test_headers)
    assert ach_res.status_code == 200, f"Achievements thất bại: {ach_res.text}"
    ach_data = ach_res.json()
    assert ach_data["total_stars"] == 9, f"Kỳ vọng 9 sao (3 bài x 3 sao), thực tế: {ach_data['total_stars']}"
    assert ach_data["completed_count"] == 3
    assert ach_data["badges"] == []
    print(f"    ✅ PASS: Học viên {test_user} đạt {ach_data['total_stars']} ⭐; không có huy hiệu mới.")

    # 6. Kiểm tra POST /api/submit tích hợp tính sao tự động
    print("\n[6] Kiểm tra POST /api/submit tích hợp tính sao tự động khi giải đúng...")
    correct_solution = "n = int(input())\nprint(n * (n + 1) // 2)"
    sub_res = client.post(
        "/api/submit",
        headers=test_headers,
        json={
            "exercise_id": "ex_01_sum_1_to_n",
            "code": correct_solution,
            "hint_level": 1,
            "session_id": test_user
        }
    )
    assert sub_res.status_code == 200, f"Submit thất bại: {sub_res.text}"
    sub_data = sub_res.json()
    assert sub_data["test_results"]["all_passed"] is True
    assert sub_data["stars_earned"] == 3, f"Kỳ vọng 3 sao khi giải đúng với hint level 1, thực tế: {sub_data['stars_earned']}"
    print(f"    ✅ PASS: Nộp bài đúng 100% tự động nhận được {sub_data['stars_earned']} ⭐.")

    print("\n" + "=" * 75)
    print("🎉 TẤT CẢ 6 BÀI KIỂM THỬ TỰ ĐỘNG CỦA PHASE 10 ĐỀU ĐẠT 100% (ALL PASSED)!")
    print("=" * 75)


if __name__ == "__main__":
    test_phase10_comprehensive()
