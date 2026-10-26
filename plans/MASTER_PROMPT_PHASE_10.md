# 🚀 PyTutor-MCP — Master Execution Prompt Phase 10: Gamification, 3-Star Autonomy & Pythonic Code Review

> **HƯỚNG DẪN:** Copy toàn bộ nội dung file này và paste vào phiên làm việc của AI Coding Assistant để kích hoạt thực thi Phase 10 tự động với chính sách **Zero-Question Policy**.

---

# MỆNH LỆNH THỰC THI PHASE 10: GAMIFICATION, AUTONOMY STARS & PYTHONIC CODE REVIEW

Bạn là Principal Software Engineer và Lead Product UX Designer phụ trách triển khai **Phase 10** cho hệ thống Gia sư Thông minh **PyTutor-MCP**.
Trước khi bắt đầu, hãy đọc nhanh `PLAN.md`, `AI_HANDOFF_CONTEXT.md` và `plans/PLAN_10.0_GAMIFICATION_AND_CODE_REVIEW.md` ở thư mục gốc để nắm rõ kiến trúc hiện tại v3.3 Pro (8 MCP Tools, SQLite `pytutor.db`, JWT Auth Student/Instructor, Gemini 3.5 Flash Lite, Multi-turn Chat, Monaco Error Decoration, Custom Stdin Playground, Step Visualizer, Skill Roadmap DAG).

**QUY TẮC TỐI THƯỢNG (ZERO-QUESTION POLICY):**
TUYỆT ĐỐI KHÔNG hỏi lại bất kỳ câu hỏi nào. Hãy thực hiện tuần tự, trọn vẹn **5 Nhiệm vụ (Task 1 -> Task 5)** dưới đây, tự chạy kiểm thử trên terminal và chỉ kết thúc khi mọi bài test đều PASS 100% và `npm.cmd run build` đạt 0 errors.

---

## RÀNG BUỘC KỸ THUẬT & MÔI TRƯỜNG
1. **Môi trường:** Windows 11, Python 3.14 (lệnh `py`), Node.js v24.15.0 (`npm.cmd` và `npx.cmd`).
2. **UTF-8:** Giữ nguyên `PYTHONIOENCODING="utf-8"` cho mọi lệnh subprocess và kiểm thử.
3. **Bảo toàn tính năng v3.3:** Tuyệt đối không làm ảnh hưởng đến 8 MCP Tools hiện có, cơ chế Multi-turn Chat, Monaco Error Decoration, Custom Stdin, Step Visualizer, Skill Roadmap và Auth JWT.

---

## NHIỆM VỤ 1: CƠ SỞ DỮ LIỆU & THUẬT TOÁN ĐÁNH GIÁ SAO TỰ LỰC (`backend/`)

1. **Cập nhật `backend/database.py`:**
   - Trong `init_db()`, tự động khởi tạo bảng:
     - `user_exercise_stars`: Lưu số sao (1-3 ⭐) của học viên cho từng bài tập, `highest_clean_score`, `best_submission_id`.
     - `user_achievements`: Lưu các huy hiệu đạt được (`username`, `badge_code`, `badge_title`, `unlocked_at`).
   - Hàm `calculate_autonomy_stars(attempt_count, max_hint_level, all_passed)`:
     - Chưa pass: 0 sao.
     - Pass 100% + hint level $\le 1$ (hoặc không hỏi AI): ⭐⭐⭐ 3 Sao (Tự lực Xuất sắc).
     - Pass 100% + hint level 2: ⭐⭐ 2 Sao (Khá giỏi).
     - Pass 100% + hint level 3: ⭐ 1 Sao (Đã hoàn thành).
   - Hàm `save_exercise_stars(username, exercise_id, stars, clean_score, submission_id)`.
   - Hàm `check_and_unlock_badges(username)`. Các huy hiệu chuẩn:
     - `FIRST_SOLVE`: Hoàn thành bài tập đầu tiên.
     - `INDEPENDENT_HERO`: Đạt 3 sao ở ít nhất 3 bài tập.
     - `BUG_HUNTER`: Sửa thành công sau ít nhất 1 lần nộp lỗi.
     - `PYTHONIC_EXPLORER`: Đạt điểm Clean Code $\ge 90$.
     - `MARATHON_CODER`: Nộp trên 5 lần thử thách và hoàn thành bài.
   - Hàm `get_class_leaderboard(limit=20)`: Trả về danh sách học viên sắp xếp theo tổng sao giảm dần, số bài hoàn thành.
   - Hàm `get_user_achievements(username)`: Trả về danh sách sao và huy hiệu đã mở khóa.
2. **Cập nhật `backend/schemas.py`:**
   - Định nghĩa `LeaderboardItem`, `LeaderboardResponse`.
   - Định nghĩa `AchievementItem`, `UserAchievementsResponse`.
   - Định nghĩa `PythonicReviewRequest`, `PythonicReviewResponse`.

---

## NHIỆM VỤ 2: SENIOR PYTHONISTA CODE REVIEW SERVICE (`backend/llm_service.py`)

1. Xây dựng hàm `generate_pythonic_review(exercise: dict, student_code: str) -> dict`:
   - Đóng vai một **Senior Python Architect** tận tâm, giàu kinh nghiệm.
   - Trả về JSON chuẩn mực:
     - `clean_score`: Điểm Clean Code từ 0 đến 100 (đối với code sinh viên đã pass, điểm tối thiểu 70 để khích lệ).
     - `strengths`: Điểm mạnh trong code của sinh viên (đặt tên, tư duy giải quyết).
     - `improvements`: Điểm cần tối ưu (PEP 8, loại bỏ code thừa, dùng hàm built-in `sum()`, `min()`, `max()`, list comprehension, slicing `[::-1]`).
     - `pythonic_code`: Đoạn mã viết lại theo phong cách Pythonic chuẩn mực nhất.
     - `explanation`: Giải thích tại sao đoạn mã Pythonic này lại ưu việt hơn (tốc độ thực thi C-level, tính dễ bảo trì).

---

## NHIỆM VỤ 3: TÍCH HỢP FASTAPI ENDPOINTS & AUTO-CALCULATE TRONG SUBMIT (`backend/main.py`)

1. Tích hợp tính sao tự động trong `POST /api/submit`:
   - Khi `test_results.all_passed` là `True`, tự động tính số sao theo `calculate_autonomy_stars` và lưu vào `user_exercise_stars`.
   - Tự động gọi `check_and_unlock_badges(username)`.
   - Trả về trường `stars_earned` và `new_badges` trong response của `/api/submit`.
2. Thêm endpoint `POST /api/tutor/pythonic-review`:
   - Kiểm tra mã nguồn, gọi `generate_pythonic_review`, cập nhật `highest_clean_score` và mở khóa badge `PYTHONIC_EXPLORER` nếu điểm $\ge 90$.
3. Thêm endpoint `GET /api/leaderboard`:
   - Trả về bảng xếp hạng lớp học (Top 1, 2, 3 kèm tổng sao, số bài hoàn thành).
4. Thêm endpoint `GET /api/student/achievements`:
   - Trả về danh sách bài tập kèm số sao đạt được và bộ sưu tập huy hiệu của người dùng hiện tại.

---

## NHIỆM VỤ 4: GIAO DIỆN GAMIFICATION & REVIEW MÃ NGUỒN TRÊN FRONTEND (`frontend/`)

1. **Cập nhật `frontend/src/services/api.js`:**
   - Thêm `fetchLeaderboard()`, `fetchUserAchievements(username)`, `requestPythonicReview({ exercise_id, code })`.
2. **Tạo component `frontend/src/components/PythonicReviewModal.jsx`:**
   - Vòng tròn hiển thị Điểm Clean Code (Circular Gauge) với màu sắc chuyển động.
   - Khung so sánh: Mã nguồn của bạn vs Mã nguồn Chuẩn Pythonic.
   - Thẻ giải thích chi tiết vì sao đoạn code mẫu ưu việt hơn.
3. **Tạo component `frontend/src/components/LeaderboardModal.jsx`:**
   - Bảng vinh danh Top 1 (🥇 Vàng), Top 2 (🥈 Bạc), Top 3 (🥉 Đồng).
   - Hiển thị Tổng số sao ⭐, Số bài tập đã giải, Bộ sưu tập huy hiệu rực rỡ.
4. **Tích hợp các nút mở trên giao diện:**
   - Trên `Header.jsx`: Thêm nút **`🏆 Bảng vàng`** (kế bên `🗺️ Cây kỹ năng`).
   - Trên `TutorPanel.jsx`: Khi giải đúng 100%, hiển thị badge số sao đạt được (⭐⭐⭐) và nút **`🚀 Thử thách Tối ưu Code Pythonic`** mở `PythonicReviewModal`.
   - Trên `ProblemPanel.jsx`: Hiển thị số sao nhỏ (ví dụ ⭐⭐⭐) cạnh tên bài tập đã giải.

---

## NHIỆM VỤ 5: KIỂM THỬ TỰ ĐỘNG & XÁC NHẬN BUILD

1. Tạo file kiểm thử tự động `test_phase10_gamification.py`:
   - Kiểm tra tính sao: 3 sao cho hint level 1, 1 sao cho hint level 3.
   - Kiểm tra mở khóa huy hiệu: `FIRST_SOLVE` khi hoàn thành bài đầu tiên.
   - Kiểm tra endpoint `POST /api/tutor/pythonic-review` trả về điểm Clean Code $\ge 70$, code tối ưu và giải thích.
   - Kiểm tra endpoint `GET /api/leaderboard` sắp xếp chính xác theo số sao.
   - Kiểm tra endpoint `GET /api/student/achievements`.
2. Chạy:
   - `py test_phase10_gamification.py`
   - `py test_phase9_visualizer.py`
   - `py test_phase8_chat.py`
   - `py -m backend.test_backend_e2e`
   - `cd frontend && npm.cmd run build` (0 errors).
3. Cập nhật `PLAN.md`, `plans/PLAN_10.0_GAMIFICATION_AND_CODE_REVIEW.md`, và `AI_HANDOFF_CONTEXT.md` chuyển trạng thái Phase 10 thành **✅ PASSED**.

**BẮT ĐẦU THỰC HIỆN NGAY NHIỆM VỤ 1 ĐẾN NHIỆM VỤ 5!**
