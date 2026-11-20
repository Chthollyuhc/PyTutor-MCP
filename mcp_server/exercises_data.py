"""
Ngân hàng bài tập mẫu và bộ kiểm thử (Test Cases) chuẩn cho PyTutor.
Gồm 5 bài tập từ cơ bản đến nâng cao:
1. Tính tổng các số từ 1 đến n (Vòng lặp & Biến tích lũy)
2. Kiểm tra số nguyên tố (Điều kiện & Tối ưu lặp)
3. Tính giai thừa n! (Vòng lặp hoặc Đệ quy)
4. Đảo ngược chuỗi (Thao tác chuỗi & Chỉ mục)
5. Đếm số lượng nguyên âm (Duyệt chuỗi & Tập hợp)
"""

import json
from pathlib import Path

# Nguồn dữ liệu duy nhất cho bài tập mẫu: seed/exercises_seed.json.
# Backend đọc cùng file này (dữ liệu, không import mã) để seed SQLite.
_SEED_PATH = Path(__file__).resolve().parent.parent / "seed" / "exercises_seed.json"
EXERCISES = json.loads(_SEED_PATH.read_text(encoding="utf-8"))


def get_all_exercises_summary() -> list[dict]:
    """Trả về danh sách tóm tắt các bài tập phục vụ hiển thị menu/danh sách."""
    return [
        {
            "id": ex["id"],
            "title": ex["title"],
            "difficulty": ex["difficulty"],
            "category": ex["category"],
            "test_cases_count": len(ex["test_cases"])
        }
        for ex in EXERCISES
    ]


def get_exercise_by_id(exercise_id: str) -> dict | None:
    """Tìm chi tiết bài tập theo ID."""
    for ex in EXERCISES:
        if ex["id"] == exercise_id:
            return ex
    return None
