# KẾ HOẠCH & BÁO CÁO TRIỂN KHAI PHASE 12: MÔ HÌNH LỚP TÍN CHỈ, KỲ THI / ĐỢT THỰC HÀNH (EXAM VS PRACTICE MODE) & CẤU HÌNH TRÌNH BIÊN DỊCH

- **Phiên bản hệ thống:** PyTutor-MCP v3.6 Pro (Academic Classroom & Exam Edition)
- **Trạng thái:** Hoàn tất 100% (All Passed)
- **Ngày hoàn thành:** 20/10/2026
- **Mục tiêu:** Giải quyết triệt để phản biện từ Giảng viên hướng dẫn về ngữ cảnh triển khai thực tế trong trường Đại học (Lớp tín chỉ, Chế độ Thi khóa AI vs Chế độ Thực hành mở AI) và minh bạch hóa cấu hình trình biên dịch Python Sandbox.

---

## 1. BỐI CẢNH & VẤN ĐỀ CẦN GIẢI QUYẾT
1. **Làm rõ ngữ cảnh triển khai học phần Lập trình Python tại Trường Đại học:**
   - Cần mô hình hóa Lớp tín chỉ (`credit_classes`) gắn liền với Giảng viên phụ trách và Sinh viên ghi danh.
   - Cần mô hình hóa các Kỳ thi & Đợt thực hành (`exam_sessions`): Giảng viên được chọn lọc bài tập cụ thể từ Ngân hàng đề (`exercises`), cấu hình thời lượng (phút), và thiết lập chế độ:
     - **Chế độ Luyện tập (`PRACTICE`)**: Sinh viên được sử dụng đầy đủ Gia sư AI 3 mức Scaffolding và trò chuyện Socratic.
     - **Chế độ Thi / Kiểm tra (`EXAM`)**: Khóa 100% Trợ lý AI (không sinh gợi ý, khóa chat) để đảm bảo tính công bằng học thuật. Hệ thống vẫn chấm điểm test cases qua MCP Sandbox cô lập.
2. **Minh bạch hóa cấu hình Trình biên dịch & Sandbox:**
   - Cung cấp minh bạch qua API `/api/health` và Modal `MCPInspectorModal.jsx`: đường dẫn trình thông dịch (`sys.executable`), phiên bản Python (`sys.version`), cờ thực thi (`-u -c`), bảng mã I/O (`UTF-8`), cơ chế cô lập (`subprocess.Popen` stdio), và các giới hạn tài nguyên (Sandbox 5s, Tracer 150 bước / 3s, SQLite WAL 20s).

---

## 2. KIẾN TRÚC & CÁC THAY ĐỔI KỸ THUẬT

### 2.1. Cơ sở dữ liệu SQLite (`backend/database.py`)
Bổ sung 3 bảng mới trong `init_db()` (chế độ WAL, timeout 20s):
1. **`credit_classes`:**
   - `id` (TEXT PK), `class_code` (TEXT UNIQUE), `class_name` (TEXT), `semester` (TEXT), `instructor_username` (TEXT), `description` (TEXT), `created_at` (TEXT).
   - Seed sẵn 2 lớp: `cls_it1110_01` (`IT1110-K66-01` - Nhập môn Lập trình Python) và `cls_it1110_02` (`IT1110-K66-02` - Python Phân tích Dữ liệu).
2. **`class_enrollments`:**
   - `id` (INTEGER PK AUTOINCREMENT), `class_id` (TEXT), `student_username` (TEXT), `enrolled_at` (TEXT), `UNIQUE(class_id, student_username)`.
   - Seed sẵn ghi danh `student` vào `cls_it1110_01`.
3. **`exam_sessions`:**
   - `id` (TEXT PK), `title` (TEXT), `class_id` (TEXT), `session_type` (TEXT: `'PRACTICE'` | `'EXAM'`), `exercise_ids` (TEXT JSON array), `duration_minutes` (INTEGER), `allow_ai_hints` (INTEGER), `is_active` (INTEGER), `created_by` (TEXT), `created_at` (TEXT).
   - Seed sẵn:
     - `sess_practice_01`: "Đợt Thực hành số 1: Làm quen Vòng lặp & Số học" (`PRACTICE`, `allow_ai_hints=1`, 90 phút, 3 bài tập).
     - `sess_exam_midterm`: "Kỳ thi Giữa kỳ Học phần Python (Chế độ Thi)" (`EXAM`, `allow_ai_hints=0`, 45 phút, 2 bài tập).
4. **CRUD Functions:**
   - `get_credit_classes`, `get_credit_class_by_id`, `create_credit_class`, `enroll_student_in_class`, `get_student_classes`, `get_class_students`.
   - `get_exam_sessions`, `get_exam_session_by_id`, `create_exam_session`, `delete_exam_session`.

### 2.2. Backend API & Cấu hình Trình biên dịch (`backend/main.py` & `schemas.py`)
1. **Endpoint `GET /api/health`:**
   - Bổ sung đối tượng `compiler_config` (`CompilerConfig`):
     - `executable_path`: `sys.executable` (Python 3.14.0).
     - `execution_flags`: `["-u (Unbuffered I/O)", "-c (In-memory bytecode compile)"]`.
     - `encoding`: `"utf-8 (PYTHONIOENCODING=utf-8)"`.
     - `isolation_mechanism`: `"OS Subprocess Popen via MCP JSON-RPC 2.0 stdio"`.
     - `sandbox_timeout_seconds`: `5.0`.
     - `tracer_limits`: `"Max 150 steps / 3.0s timeout (sys.settrace)"`.
     - `database_engine`: `"SQLite3 WAL Mode (timeout=20.0s)"`.
2. **Các Endpoint Quản trị Lớp học & Kỳ thi:**
   - `GET /api/classes`: Lấy danh sách lớp kèm sĩ số sinh viên và số đợt thi.
   - `POST /api/instructor/classes`: Giảng viên tạo lớp tín chỉ mới.
   - `POST /api/classes/{class_id}/enroll`: Ghi danh sinh viên vào lớp tín chỉ.
   - `GET /api/exam-sessions`: Lấy danh sách đợt thực hành và kỳ thi.
   - `POST /api/instructor/exam-sessions`: Giảng viên tạo đợt thi/thực hành, chọn lọc danh sách bài tập từ ngân hàng đề.
   - `DELETE /api/instructor/exam-sessions/{session_id}`: Giảng viên xóa kỳ thi/đợt thực hành.
3. **Chốt chặn Bảo mật Chế độ Thi (`EXAM Mode Guard`):**
   - Trong `POST /api/submit`: Nếu `exam_session_id` có `session_type == 'EXAM'` hoặc `allow_ai_hints == 0`, Sandbox và AST vẫn chấm điểm 100% test cases và ghi vết học tập, nhưng khóa Gemini và gán `llm_source = "Exam-Mode-Guard"` kèm thông báo khóa sư phạm.
   - Trong `POST /api/tutor/chat`: Nếu gửi kèm `exam_session_id` chế độ thi, từ chối trả lời và nhắc sinh viên tuân thủ quy chế thi cử.

### 2.3. Frontend Giảng viên (`frontend/src/pages/InstructorDashboard.jsx`)
Thiết kế hệ thống **3 Tabs quản trị chuyên nghiệp**:
- **Tab 1 - 📚 Ngân hàng Bài tập & Lịch sử nộp bài:** Giữ nguyên CRUD bài tập, bảng thống kê 4 chỉ số, xem chi tiết bài nộp và xuất báo cáo CSV UTF-8 BOM cho Excel.
- **Tab 2 - 🏫 Quản lý Lớp tín chỉ (`Credit Classes`):** Danh sách lớp tín chỉ kèm sĩ số sinh viên, học kỳ, và form tạo nhanh lớp mới.
- **Tab 3 - 📝 Quản lý Kỳ thi & Đợt thực hành (`Exams & Practice Sessions`):**
  - Form tạo Kỳ thi / Đợt thực hành:
    - Tiêu đề, chọn Lớp tín chỉ áp dụng.
    - Chọn chế độ: **Đợt Thực hành (Mở AI 3 mức)** vs **Kỳ thi (Khóa AI - Chỉ chấm điểm)**.
    - Thời gian làm bài (phút).
    - **Danh sách Checkbox chọn bài tập từ Ngân hàng đề (`exercises`)**: Cho phép tích chọn hoặc bỏ chọn bài tập cho đề thi.
  - Danh sách các kỳ thi/đợt thực hành đang mở kèm nhãn chế độ, danh sách bài tập con và nút Xóa.

### 2.4. Frontend Sinh viên (`StudentIDE.jsx`, `ProblemPanel.jsx`, `TutorPanel.jsx`, `MCPInspectorModal.jsx`)
1. **`ProblemPanel.jsx` & `StudentIDE.jsx`:**
   - Huy hiệu Lớp tín chỉ hiện tại của sinh viên (`🏫 Lớp: IT1110-K66-01`).
   - Bộ chọn Chế độ / Đợt làm bài: Tự luyện tập tự do, Đợt thực hành của lớp, hoặc Kỳ thi của lớp.
   - Tự động lọc danh sách bài tập theo Kỳ thi / Đợt thực hành đã chọn.
   - **Thanh trạng thái Kỳ thi (EXAM Mode Banner)**: Khi ở chế độ thi, hiển thị banner hổ phách/đỏ nổi bật kèm **đồng hồ đếm ngược thời gian thực (MM:SS)**.
2. **`TutorPanel.jsx`:**
   - Trong chế độ thi: Khóa các nút chọn Mức gợi ý 1-3, hiển thị thẻ cảnh báo: *"🔒 Đang trong chế độ Kiểm tra / Thi: Trợ lý AI tạm khóa để đảm bảo đánh giá công bằng. Bạn hãy sử dụng nút 'Chạy thử code' và 'Nộp bài chấm điểm' ở cột giữa."*
   - Khóa ô nhập câu hỏi chat và nút gửi tin nhắn.
3. **`MCPInspectorModal.jsx`:**
   - Thêm thẻ thông số kỹ thuật **"⚙️ Cấu hình Trình biên dịch & Hạ tầng Thực thi (Python Compiler & Sandbox Specs)"** lấy trực tiếp từ `/api/health`.

---

## 3. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG
- **File kiểm thử:** `test_phase12_classroom_exam.py`
  - [1] Xác thực tài khoản Giảng viên và Sinh viên: **PASS**
  - [2] Kiểm tra Cấu hình Trình biên dịch & Sandbox qua GET /api/health: **PASS**
  - [3] Quản lý Lớp tín chỉ (GET /api/classes, POST /api/instructor/classes, enroll): **PASS**
  - [4] Tạo Kỳ thi chọn lọc bài tập (POST /api/instructor/exam-sessions): **PASS**
  - [5] Chốt chặn Bảo mật Chế độ Thi khi Nộp bài (POST /api/submit -> Exam-Mode-Guard): **PASS**
  - [6] Chốt chặn Bảo mật trong Chat làm rõ (POST /api/tutor/chat -> Exam-Mode-Guard): **PASS**
  - [7] Xóa Kỳ thi kiểm thử (DELETE /api/instructor/exam-sessions): **PASS**
- **Toàn bộ kiểm thử hệ thống:**
  - `mcp_server/test_mcp_server.py`: **8/8 PASS 100%**
  - `test_phase10_gamification.py`: **6/6 PASS 100%**
  - `test_phase12_classroom_exam.py`: **7/7 PASS 100%**
  - `npm.cmd run build`: **0 errors, Vite production bundle 1.93s**
