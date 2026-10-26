# KẾ HOẠCH & BÁO CÁO KỸ THUẬT PHASE 13 & 14 (v4.0 NEU ENTERPRISE LMS-ITS EDITION)
**Dự án:** PyTutor-MCP — Hệ thống Quản lý Học tập & Gia sư Lập trình Thông minh Chuẩn Tín chỉ NEU  
**Đơn vị Triển khai:** Khoa Công nghệ thông tin — Trường Đại học Kinh tế Quốc dân (NEU)  
**Phiên bản:** v4.0 NEU Enterprise LMS-ITS Edition  
**Kiến trúc:** Model Context Protocol (MCP Host & Server), SQLite3 WAL Mode, FastAPI, React + Vite, TailwindCSS, Gemini 3.5 Flash Lite  

---

## I. MỤC TIÊU & BỐI CẢNH TRIỂN KHAI TẠI ĐẠI HỌC KINH TẾ QUỐC DÂN (NEU)
Theo định hướng của Khoa Công nghệ thông tin — NEU, hệ thống học phần lập trình Python cần chuyển dịch từ một công cụ luyện code đơn lẻ thành một **Nền tảng Quản lý Học tập & Gia sư Thích ứng (LMS + ITS)** toàn diện, gắn liền với thực tiễn đào tạo theo hệ thống tín chỉ của Trường Đại học Kinh tế Quốc dân:

1. **Chuẩn hóa Danh tính & Học phần NEU:**
   - Mã học phần, mã lớp học phần, số tín chỉ, khoa phụ trách và thông tin giảng viên/sinh viên được chuẩn hóa theo quy chế đào tạo tín chỉ NEU:
     - `CNTT1116(126)_01` - Lập trình Python cơ bản (Chuyên ngành CNTT & KHMT) • 3 Tín chỉ • TS. Trần Quang Khánh
     - `CNTT1116(126)_02` - Lập trình Python cơ bản (Hệ Chất lượng cao - CLC) • 3 Tín chỉ • TS. Trần Quang Khánh
     - `CNTT1142(126)_01` - Phân tích dữ liệu với Python (Data Science) • 3 Tín chỉ • ThS. Nguyễn Minh Tuấn
     - Tài khoản Sinh viên thực nghiệm: `Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)`
2. **Quản lý Đa Lớp học phần & Bài tập Riêng theo từng Lớp (Multi-Class Enrollment & Per-Class Exercises):**
   - Sinh viên có thể tham gia (enroll) đồng thời nhiều lớp học phần khác nhau bằng **Mã tham gia lớp (Enrollment Code)** hoặc đăng ký trực tiếp.
   - Mỗi lớp học phần có danh sách bài tập, lộ trình kỹ năng và đợt thi riêng biệt.
3. **Cải tổ Cây Kỹ năng thành "Lộ trình Kỹ năng & Ma trận Chuẩn đầu ra Học phần (Curriculum & Skill Matrix)":**
   - Không còn gán cố định cứng nhắc toàn cục. Giảng viên có quyền cấu hình trực tiếp các bài tập trong lớp theo các Module/Chương học phần, thiết lập bài tiên quyết (`prerequisite_id`) và trọng số điểm.
   - Tích hợp **Thang đo Định lượng (Mastery Rubric)**:
     - `min_stars_required` (1-3 ⭐) là điều kiện bắt buộc để được công nhận "Đã làm chủ" (MASTERED).
     - Nếu sinh viên giải đúng 100% test cases nhưng lạm dụng gợi ý AI (chỉ đạt 1 ⭐ trong khi chuẩn lớp yêu cầu 2 ⭐), hệ thống gán trạng thái `NEEDS_MORE_STARS` và yêu cầu làm lại tự lực.
4. **Đại tu Nhật ký Học tập với Động cơ Phân tích Năng lực 4 Chiều (4D Learning Analytics Engine):**
   - Tính toán định lượng:
     - **Điểm Tự lực Sư phạm (Autonomy Score)**: Thang điểm 0 - 100.
     - **Tỷ lệ Vượt qua Ngay Lần đầu (First-try Pass Rate %)**.
     - **Số Lần Nộp Trung bình / Bài giải thành công (Avg Attempts to Solve)**.
     - **Cơ cấu Lỗi Thực nghiệm (Error Breakdown)**: Pass 100% vs Lỗi Logic vs Lỗi Cú pháp / Runtime.
   - Tự động sinh **3 Thẻ Chẩn đoán Dữ liệu Sư phạm**:
     1. 🌟 **Điểm mạnh Nổi bật**
     2. ⚠️ **Điểm nghẽn Cần khắc phục**
     3. 🎯 **Hành động Khuyến nghị Tiếp theo**

---

## II. CHI TIẾT NÂNG CẤP KIẾN TRÚC & CƠ SỞ DỮ LIỆU

### 1. Cơ sở dữ liệu SQLite WAL (`backend/database.py` & `pytutor.db`)
- Bổ sung các cột vào bảng `credit_classes`:
  - `course_code TEXT DEFAULT 'CNTT1116'`
  - `credits INTEGER DEFAULT 3`
  - `faculty TEXT DEFAULT 'Khoa Công nghệ thông tin - NEU'`
  - `enrollment_code TEXT UNIQUE`
  - `instructor_name TEXT`
- Tạo mới bảng `class_exercises` (Ma trận Chương trình & Chuẩn đầu ra Lớp):
  ```sql
  CREATE TABLE IF NOT EXISTS class_exercises (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      class_id TEXT NOT NULL,
      exercise_id TEXT NOT NULL,
      module_name TEXT NOT NULL DEFAULT 'Chương 1: Cốt lõi Python',
      order_idx INTEGER NOT NULL DEFAULT 1,
      prerequisite_id TEXT,
      min_stars_required INTEGER NOT NULL DEFAULT 2,
      skill_tag TEXT NOT NULL DEFAULT 'Tư duy thuật toán',
      weight_point INTEGER NOT NULL DEFAULT 10,
      added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      UNIQUE(class_id, exercise_id),
      FOREIGN KEY (class_id) REFERENCES credit_classes(id) ON DELETE CASCADE,
      FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
  );
  ```

### 2. Thuật toán Động cơ Phân tích Năng lực 4 Chiều (`compute_student_model`)
- Được đồng bộ tại cả `mcp_server/storage.py` và `backend/database.py`:
  - **Autonomy Score (0-100)**: Tổng hợp từ mức độ gợi ý (`hint_level`), số sao trung bình trên các bài đã nộp và tỷ lệ tự giải không trợ giúp.
  - **First-try Pass Rate**: Tỷ lệ phần trăm các bài tập được giải đúng ngay từ lần submit đầu tiên.
  - **Avg Attempts**: Số lần chạy trung bình để một bài tập đạt pass 100%.
  - **Error Breakdown**: Thống kê số lần lỗi logic (AssertionError, Wrong output) và lỗi cú pháp/runtime (SyntaxError, ZeroDivisionError...).
  - **3 Diagnostic Cards**: Phân tích logic sư phạm tự động từ các chỉ số thực tế của sinh viên, chỉ ra chính xác sinh viên đang mạnh ở chủ đề nào, bị nghẽn ở cấu trúc cú pháp hay logic rẽ nhánh, và đưa ra khuyến nghị bài tập tiếp theo.

### 3. Nâng cấp Giao thức MCP (`mcp_server/server.py` & `backend/mcp_client.py`)
- Tool `get_student_model` tiếp nhận thêm tham số tùy chọn `class_id: str = ""`.
- Khi có `class_id`, mô hình học viên sẽ lọc và tính toán độc lập dựa trên các bài tập thuộc riêng lớp học phần đó.

---

## III. NÂNG CẤP GIAO DIỆN NGƯỜI DÙNG (FRONTEND REACT)

1. **`ClassPortalModal.jsx` (Mới):**
   - Tab 1: **Lớp Học Phần Của Tôi**: Thẻ lớp học hiển thị tiến độ học tập (%), số sao, nút "Vào học lớp này" và "Rời lớp".
   - Tab 2: **Đăng ký & Ghi danh Lớp Mới**: Ô nhập Mã lớp (e.g. `NEU-PY01`, `NEU-PY02`, `NEU-DA01`) và danh sách các lớp mở với nút 1-click Ghi danh.
2. **`Header.jsx`:**
   - Hiển thị pill lớp học phần NEU hiện tại: `🏫 CNTT1116(126)_01 • Lập trình Python cơ bản [Đổi lớp]` - bấm vào mở ngay `ClassPortalModal`.
   - Cập nhật phiên bản hệ thống lên `v4.0 NEU LMS`.
3. **`SkillRoadmapModal.jsx`:**
   - Hiển thị tiêu đề lớp học phần NEU và thanh giải thích Thang đo Định lượng (⭐⭐⭐ Tự lực, ⭐⭐ Gợi ý nhẹ, ⭐ Gợi ý sâu).
   - Phân nhóm bài tập động theo từng **Module / Chương học phần**.
   - Thể hiện trạng thái định lượng: `MASTERED`, `NEEDS_MORE_STARS`, `IN_PROGRESS`, `AVAILABLE`, `LOCKED`.
4. **`StudentProfileModal.jsx`:**
   - Huy hiệu Phân hạng Năng lực (e.g. `🎓 Chuẩn A+ NEU (Senior Autonomy)`).
   - Grid 4 chiều: Autonomy Score (0-100), First-try Pass Rate (%), Avg Attempts, Mức gợi ý TB.
   - Biểu đồ phân bổ cơ cấu lỗi (Passed vs Logic vs Syntax/Runtime).
   - 3 Thẻ Chẩn đoán Dữ liệu Sư phạm (Điểm mạnh, Điểm nghẽn, Khuyến nghị).
5. **`InstructorDashboard.jsx`:**
   - Tab 2 (Lớp tín chỉ): Hiển thị thông tin chuẩn NEU (Mã học phần, tín chỉ, khoa, giảng viên, mã ghi danh, sĩ số, số bài lộ trình).
   - Modal **Quản lý Lộ trình & Ma trận Kỹ năng của Lớp**: Bảng bài tập lớp, sửa nhanh `min_stars_required` (1-3 ⭐), gán bài mới từ ngân hàng đề, gỡ bài.
   - Modal **Danh sách Sinh viên & Bảng Đo lường Tiến độ**: Hiển thị danh sách sinh viên, tiến độ hoàn thành (%) và tổng số sao tự lực.

---

## IV. KẾT QUẢ KIỂM THỬ TỰ ĐỘNG TOÀN DIỆN (100% PASS)

| Hạng mục kiểm thử | Script thực thi | Kết quả | Ghi chú |
| :--- | :--- | :---: | :--- |
| **Phase 13 & 14 (NEU LMS & 4D Analytics)** | `test_phase13_14_neu_lms.py` | **8/8 PASS (100%)** | Xác thực tài khoản NEU, Đa lớp học phần, Ghi danh bằng mã, Curriculum Matrix CRUD, Student Roster, Mastery Rubric, 4D Metrics |
| **Phase 12 (Classroom & Exam Mode)** | `test_phase12_classroom_exam.py` | **7/7 PASS (100%)** | Bảo toàn tuyệt đối chế độ thi khóa AI & compiler config |
| **Backend Integration E2E** | `backend.test_backend_e2e` | **6/6 PASS (100%)** | Discovery, Exercises, Gemini 3.5 Flash Lite 3 levels hint |
| **MCP Server Unit Tests** | `mcp_server.test_mcp_server` | **8/8 PASS (100%)** | 8 MCP Tools, AST, Sandbox Isolation, Timeout 5s |
| **Frontend Production Build** | `cd frontend && npm.cmd run build` | **0 ERRORS** | Vite build thành công trong 2.43s |

---

## V. KẾT LUẬN & SẴN SÀNG BẢO VỆ ĐỒ ÁN
Hệ thống **PyTutor-MCP v4.0 NEU Enterprise LMS-ITS Edition** đã giải quyết triệt để và toàn diện toàn bộ các yêu cầu từ Giảng viên hướng dẫn:
- Phù hợp 100% với môi trường đào tạo tín chỉ tại Trường Đại học Kinh tế Quốc dân (Khoa Công nghệ thông tin).
- Tách bạch rõ ràng quyền hạn giữa Giảng viên (tùy biến chương trình, phân bổ lớp, quản lý kỳ thi) và Sinh viên (học tập có định hướng, xem tiến độ trực quan, nhận chẩn đoán thích ứng).
- Nền tảng MCP chứng minh được giá trị vượt trội: vừa là công cụ thực thi sandbox cô lập an toàn, vừa là kho lưu trữ năng lực học sinh thích ứng thông minh.
