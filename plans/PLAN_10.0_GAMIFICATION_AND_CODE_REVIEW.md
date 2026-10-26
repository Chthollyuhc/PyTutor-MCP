# 📋 KẾ HOẠCH TRIỂN KHAI CHI TIẾT: PHASE 10.0
# TRÒ CHƠI HÓA HỌC TẬP (GAMIFICATION), ĐÁNH GIÁ SAO TỰ LỰC & THỬ THÁCH TỐI ƯU CODE PYTHONIC
## (AUTONOMY STARS, ACHIEVEMENT BADGES, PYTHONIC CODE REVIEW & LEADERBOARD)

> **Mã kế hoạch:** `PLAN_10.0`  
> **Trạng thái:** ✅ **ĐÃ HOÀN THÀNH 100% (PASSED)**  
> **Áp dụng cho:** `backend/`, `frontend/src/components/`, `frontend/src/pages/`  
> **Định hướng:** Tạo động lực học tập nội tại (Intrinsic Motivation) thông qua cơ chế Đánh giá Sao Tự lực (Autonomy Rating 1-3 Sao), Huy hiệu Thành tích (Badges), Chế độ Review Mã nguồn Chuẩn Pythonic (Post-Acceptance Code Review do Gemini đóng vai Senior Developer) và Bảng Xếp hạng Lớp học (Classroom Leaderboard).

---

## 1. 🔍 BỐI CẢNH KỸ THUẬT & PHÂN TÍCH VẤN ĐỀ

### 1.1. Vấn đề "Giải Xong Là Hết" (The Post-Acceptance Learning Void)
- Trong hầu hết các hệ thống chấm bài tự động hiện nay, khi sinh viên vượt qua 100% test cases (Accepted / All Passed), hệ thống chỉ hiện một câu chúc mừng đơn giản rồi kết thúc.
- **Vấn đề thực tế:** Một sinh viên có thể giải đúng bài toán bằng cách viết 20 dòng code lồng nhau rất rối rắm, dùng biến tạm không cần thiết, hoặc vi phạm các quy chuẩn lập trình hiện đại của Python (PEP 8). Nếu không có người hướng dẫn chỉ ra cách viết gọn gàng hơn, sinh viên sẽ hình thành thói quen viết code cẩu thả.
- **Giải pháp:** Xây dựng tính năng **"🚀 Thử thách Tối ưu Code Chuẩn Pythonic"**: Sau khi sinh viên giải đúng, Gia sư AI Gemini sẽ đóng vai một *Senior Python Architect* để nhận xét phong cách lập trình, chấm điểm Clean Code và gợi ý cách giải tinh hoa (idiomatic Python) như: *dùng `sum()` thay vì vòng lặp `for`, dùng List Comprehension thay vì `append`, dùng `any()` / `all()`, unpacking tuple...*.

### 1.2. Thúc đẩy Tính Tự Lực (Rewarding Intellectual Independence)
- Nếu một sinh viên tự suy nghĩ giải đúng ngay từ lần đầu cũng nhận được kết quả giống hệt một sinh viên phải xem gợi ý chi tiết Level 3 từ đầu đến cuối, điều này sẽ tạo ra tâm lý ỷ lại vào AI.
- **Giải pháp:** Cơ chế **3 Sao Tự lực (Autonomy Stars)**:
  - Càng ít phụ thuộc vào AI hoặc chỉ cần gợi ý nhẹ (Level 1) thì càng nhận được nhiều Sao.
  - Tích lũy sao để mở khóa các Huy hiệu danh giá (Badges) và vinh danh trên Bảng Xếp hạng Lớp học.

---

## 2. 🏛️ THIẾT KẾ KIẾN TRÚC DỮ LIỆU & THUẬT TOÁN TÍNH SAO

### 2.1. Cấu trúc Bảng Cơ sở Dữ liệu Mới (`pytutor.db`)

```sql
-- Bảng lưu trữ số sao đạt được theo từng bài tập của mỗi học viên
CREATE TABLE IF NOT EXISTS user_exercise_stars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    exercise_id TEXT NOT NULL,
    stars_earned INTEGER NOT NULL CHECK (stars_earned BETWEEN 1 AND 3),
    best_submission_id INTEGER,
    highest_clean_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(username, exercise_id)
);

-- Bảng lưu trữ huy hiệu thành tích của học viên
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    badge_code TEXT NOT NULL,
    badge_title TEXT NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(username, badge_code)
);
```

### 2.2. Thuật toán Đánh giá Sao Tự lực (Autonomy Star Algorithm)

```python
def calculate_autonomy_stars(attempt_count: int, max_hint_level_used: int, all_passed: bool) -> int:
    """
    Quy tắc tính sao:
    - Nếu chưa pass 100% test cases: 0 Sao
    - Nếu pass 100% mà:
        + Không dùng gợi ý (chỉ dùng 'Chạy thử') HOẶC chỉ dùng Mức 1: ⭐⭐⭐ 3 SAO (Tự lực Xuất sắc)
        + Dùng gợi ý Mức 2 (Chỉ chỗ sai): ⭐⭐ 2 SAO (Khá giỏi)
        + Cần gợi ý Mức 3 (Hướng dẫn từng bước): ⭐ 1 SAO (Đã hoàn thành)
    """
    if not all_passed:
        return 0
    if max_hint_level_used <= 1:
        return 3
    elif max_hint_level_used == 2:
        return 2
    else:
        return 1
```

### 2.3. Danh mục Huy hiệu Thành tích (Achievement Badges)

| Mã Huy hiệu | Tên Huy hiệu | Biểu tượng | Điều kiện Mở khóa |
|:---|:---|:---:|:---|
| `FIRST_SOLVE` | Bước Chân Đầu Tiên | 🌟 | Hoàn thành bài tập lập trình đầu tiên |
| `INDEPENDENT_HERO` | Bậc Thầy Tự Lực | 🏆 | Đạt 3 Sao ở 3 bài tập liên tiếp |
| `BUG_HUNTER` | Thợ Săn Lỗi Tự Thân | ⚡ | Sửa thành công một bài bị lỗi sau khi chạy thử mà không hỏi AI |
| `PYTHONIC_EXPLORER` | Nhà Khai Phá Pythonic | 🐍 | Đạt điểm Clean Code trên 90 điểm trong một bài tập |
| `MARATHON_CODER` | Kiên Trì Bền Bỉ | 🧗 | Hoàn thành một bài tập sau hơn 5 lần thử mà không bỏ cuộc |

---

## 3. 📋 CHI TIẾT TỪNG NHIỆM VỤ TRIỂN KHAI (TASKS)

### Task 10.1 — Cơ sở Dữ liệu & Schema Backend
- Bổ sung vào [`backend/database.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/database.py):
  - Tạo bảng `user_exercise_stars` và `user_achievements`.
  - Hàm `save_exercise_stars(username, exercise_id, stars, clean_score)`.
  - Hàm `get_user_stars_summary(username)`.
  - Hàm `check_and_unlock_badges(username, context_data)`.
  - Hàm `get_class_leaderboard(limit=20)`: Trả về danh sách học viên sắp xếp theo `total_stars DESC, completed_exercises DESC`.
- Bổ sung vào [`backend/schemas.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/schemas.py):
  - `PythonicReviewRequest`, `PythonicReviewResponse`.
  - `LeaderboardItem`, `AchievementItem`.

### Task 10.2 — Senior Pythonista Review Service (`backend/llm_service.py`)
- Xây dựng hàm `generate_pythonic_review(exercise: dict, student_code: str) -> dict`:
  - **Nhập vai:** Senior Python Tech Lead tận tâm và sâu sắc.
  - **Phân tích:**
    1. Điểm Clean Code (0-100): Đánh giá cấu trúc, đặt tên biến, tuân thủ PEP 8.
    2. Điểm mạnh trong code của sinh viên (động viên, khích lệ).
    3. Điểm cần tối ưu: Chỉ rõ các đoạn viết dài dòng có thể rút gọn bằng các tính năng đặc sắc của Python.
    4. Đoạn mã Pythonic mẫu: Đưa ra phiên bản viết chuẩn mực nhất kèm giải thích từng dòng tại sao lại tối ưu hơn.
  - **Output định dạng JSON có cấu trúc:**
    ```json
    {
      "clean_score": 92,
      "strengths": "Tên biến n và tong đặt rất trực quan, kiểm soát vòng lặp tốt.",
      "improvements": "Vòng lặp for tính tổng có thể được thay thế bằng hàm built-in sum().",
      "pythonic_code": "n = int(input())\nprint(sum(range(1, n + 1)))",
      "explanation": "Hàm sum() trong Python được viết bằng ngôn ngữ C ở tầng thấp, do đó chạy nhanh hơn vòng lặp for thông thường và giảm số dòng code từ 5 dòng xuống còn 2 dòng."
    }
    ```

### Task 10.3 — FastAPI Endpoints Mới (`backend/main.py`)
- Endpoint `POST /api/tutor/pythonic-review`: Nhận code sinh viên đã pass, trả về kết quả review chi tiết.
- Endpoint `GET /api/leaderboard`: Trả về dữ liệu bảng xếp hạng lớp học.
- Endpoint `GET /api/student/achievements`: Trả về danh sách sao và huy hiệu đã mở khóa của người dùng hiện tại.

### Task 10.4 — Giao diện Modal Pythonic Review (`PythonicReviewModal.jsx`)
- Tạo component `frontend/src/components/PythonicReviewModal.jsx`:
  - Hiển thị Điểm Clean Code với vòng tròn tiến trình (Circular Progress Gauge).
  - Khung so sánh: Code của bạn vs Code Chuẩn Pythonic (Diff/Comparison view).
  - Giải thích chi tiết các thành ngữ Python hiện đại.

### Task 10.5 — Bảng Xếp hạng & Vinh danh (`LeaderboardModal.jsx`)
- Tạo component `frontend/src/components/LeaderboardModal.jsx`:
  - Bảng danh sách học viên: Hạng (Top 1, 2, 3 có huy chương Vàng, Bạc, Đồng), Tên học viên, Tổng số Sao ⭐, Số bài đã làm chủ, Danh sách huy hiệu đã đạt.
  - Nút mở nhanh từ thanh Header: `🏆 Bảng vàng Lớp học`.

---

## 4. 🛡️ QUY TẮC SƯ PHẠM & AN TOÀN

1. **Khích lệ Tích cực (No Demotivation):**
   - Điểm Clean Code không bao giờ được chấm quá khắt khe đối với sinh viên năm nhất/người mới học. Dù code dài dòng nhưng giải đúng thuật toán thì điểm sàn tối thiểu là 70/100, tập trung vào lời khuyên mang tính xây dựng.
2. **Chỉ Kích hoạt Sau khi Pass 100%:**
   - Nút Pythonic Review chỉ xuất hiện khi học viên đã đạt 100% test cases để đảm bảo học viên phải tự giải đúng bài toán trước khi học cách tối ưu.

---

## 5. 🧪 KỊCH BẢN KIỂM THỬ XÁC NHẬN

Tạo file kiểm thử `test_phase10_gamification.py`:
- [ ] **TC 10.1:** Sinh viên giải đúng bài tập chỉ với gợi ý Mức 1 được tính đúng 3 Sao.
- [ ] **TC 10.2:** Sinh viên giải đúng sau khi dùng gợi ý Mức 3 được tính đúng 1 Sao.
- [ ] **TC 10.3:** Hàm `generate_pythonic_review` trả về đầy đủ JSON điểm số và mã nguồn tối ưu cho bài toán tính tổng 1 đến n.
- [ ] **TC 10.4:** Bảng xếp hạng lớp học sắp xếp chính xác theo số sao giảm dần.
- [ ] **TC 10.5:** Build Frontend `npm.cmd run build` đạt 0 lỗi.
