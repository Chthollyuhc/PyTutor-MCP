# KẾ HOẠCH THỰC THI PHASE 15 (v5.0 PRO): ĐẠI TU KIẾN TRÚC ĐIỀU HƯỚNG ĐA TẦNG & TÁCH BIỆT KHÔNG GIAN LỚP HỌC PHẦN VỚI IDE (NEU MULTI-STAGE LMS & IDE ARCHITECTURE)

## 1. Bối Cảnh & Mục Tiêu Cải Cách
Hệ thống **PyTutor-MCP** trước Phase 15 gom toàn bộ tính năng vào một màn hình IDE 3 cột duy nhất, khiến giao diện bị chật chội và thiếu đi tính phân cấp của một Hệ thống Quản lý Học tập Đại học (LMS).
Phase 15 thực hiện cuộc đại cách mạng trải nghiệm người dùng theo mô hình kết hợp giữa **Coursera/Canvas LMS** (Quản lý lớp học phần tín chỉ) và **LeetCode/HackerRank** (Môi trường lập trình chuyên sâu):
* **Không đẩy người dùng thẳng vào màn hình code:** Sinh viên và Giảng viên trải nghiệm luồng đi tuần tự, mạch lạc, sang trọng.
* **Luồng Người dùng Sinh viên (3 Tầng):**
  1. `Cổng Đăng Nhập NEU (/login)`: Split-screen Enterprise EdTech Portal với thương hiệu Khoa CNTT - NEU, 3 thẻ giới thiệu giá trị cốt lõi, form đăng nhập chuẩn và 3 nút 1-Click Demo cho Hội đồng chấm đồ án.
  2. `Tầng 1 - Cổng Sinh Viên (/student)`: Thống kê 4 KPIs tổng quan (Lớp đang học, Bài đã giải, Sao tự lực, Autonomy Score), lưới thẻ các lớp tín chỉ đã ghi danh (`CNTT1116`, `CNTT1142`), thanh tiến độ %, form ghi danh bằng mã (`NEU-PY02`), và phòng luyện tập tự do.
  3. `Tầng 2 - Không Gian Chi Tiết Lớp (/student/classes/:classId)`: Breadcrumb điều hướng, thông tin giảng viên, số tín chỉ; 4 Tabs nội dung trực tiếp trên trang: (1) Chương trình học & Bài tập theo Module kèm chuẩn sao Mastery Rubric, (2) Đợt thực hành & Kỳ thi (Practice vs Exam mode), (3) Cây kỹ năng DAG có tương tác, (4) Bảng vàng lớp & Đánh giá năng lực 4D.
  4. `Tầng 3 - Môi Trường Lập Trình Chuyên Sâu (/student/ide/:exerciseId?classId=...&sessionId=...)`: 3 cột tập trung 100% cho viết code, nút nổi bật "Quay lại Lớp học phần", dropdown đổi nhanh bài tập trong lớp, đồng hồ đếm ngược phòng thi (nếu là Exam mode).
* **Luồng Người dùng Giảng Viên (Sidebar Workspace Layout):**
  1. `Sidebar Bên Trái`: Cố định 260px với thương hiệu Giảng viên NEU, 4 mục điều hướng:
     - `🏫 Quản lý Lớp học phần NEU`: Danh sách lớp, mở lớp mới, quản trị chi tiết từng lớp (Curriculum inline edit sao, Exam sessions, Student Roster).
     - `📚 Ngân hàng Bài tập`: Quản lý ngân hàng đề, thêm mới, sửa đề, test cases.
     - `📊 Giám sát Bài nộp & AI`: Lịch sử nộp bài toàn trường, xem chi tiết code & lời khuyên AI, xuất CSV UTF-8 Excel.
     - `🔌 Hạ tầng MCP & Trình biên dịch`: Thông số `sys.executable`, Python 3.14, timeout 5s, 8 MCP tools.
  2. `Nút chuyển nhanh sang Cổng Sinh viên (/student)` và nút Đăng xuất.

---

## 2. Chi Tiết Thực Hiện Các Nhiệm Vụ

### Nhiệm Vụ 1: Tái Cấu Trúc Routing & Cơ Chế Xác Thực
* **`frontend/src/context/AuthContext.jsx`**:
  - Gỡ bỏ cơ chế tự động silent auto-login `student`.
  - Nếu không có token hợp lệ trong `localStorage`, giữ `user = null` và điều hướng về `/login`.
  - Cập nhật hàm `logout()` xóa sạch token và chuyển về `/login`.
* **`frontend/src/App.jsx`**:
  - Cấu hình các Route phân cấp: `/login`, `/student`, `/student/classes/:classId`, `/student/ide/:exerciseId`, `/student/ide`, `/instructor`, `/instructor/classes/:classId`, `/instructor/exercises/new`, `/instructor/exercises/:id/edit`.
  - Thêm component `IndexRedirect` tại `/`: chưa đăng nhập $\rightarrow$ `/login`, sinh viên $\rightarrow$ `/student`, giảng viên $\rightarrow$ `/instructor`.
  - Thêm `StudentRoute` và `InstructorRoute` bảo vệ phân quyền.

### Nhiệm Vụ 2: Nâng Cấp Trang Đăng Nhập NEU (`LoginPage.jsx`)
* Thiết kế Split-Screen:
  - Cột trái: Giới thiệu Khoa Công nghệ thông tin - NEU, thương hiệu PyTutor-MCP v5.0 Enterprise LMS, 3 thẻ trụ cột: Đào tạo tín chỉ NEU, Gia sư AI 3 cấp độ (Anti-Spoil), Động cơ 8 MCP Tools JSON-RPC 2.0.
  - Cột phải: Form đăng nhập chuẩn + Khối **1-Click Demo cho Hội đồng Chấm Đồ án** (Sinh viên Trần Minh Khánh, Giảng viên TS. Trần Quang Khánh, Giảng viên ThS. Nguyễn Văn Tuấn).

### Nhiệm Vụ 3: Tầng 1 Sinh Viên — Cổng Học Tập (`StudentPortalPage.jsx`)
* Top Navigation Bar chuẩn LMS với thông tin sinh viên, nút mở Hồ sơ 4D, nút xem 8 MCP Tools, nút Đăng xuất.
* 4 KPI cards: Lớp đang học, Bài đã hoàn thành, Sao tự lực, Điểm Tự lực Autonomy Score / 100.
* Danh sách Lớp học phần đang theo học (Class Cards with progress bars, lecturer, enrollment code).
* Khối Đăng ký / Ghi danh lớp mới bằng mã và Khối Phòng Tự Luyện Tập Tự Do.

### Nhiệm Vụ 4: Tầng 2 Sinh Viên — Không Gian Lớp Học Phần (`StudentClassDetailPage.jsx`)
* Breadcrumb điều hướng: `Cổng Sinh viên / Mã Lớp - Tên Lớp`.
* Nút `⬅️ Quay về Danh sách Lớp học phần`.
* Banner thông tin học phần, giảng viên, mã tham gia, tiến độ %.
* 4 Tabs trực quan trên trang:
  - Tab 1: Chương trình & Bài tập theo Module, hiển thị trạng thái chuẩn sao Mastery Rubrics (`MASTERED`, `NEEDS_MORE_STARS`, `AVAILABLE`, `LOCKED`), nút "Làm bài trên IDE ▶".
  - Tab 2: Thực hành & Kỳ thi (Practice vs Exam mode với thời lượng phút).
  - Tab 3: Cây kỹ năng DAG có tương tác, click node vào IDE làm bài.
  - Tab 4: Bảng vàng lớp học & 3 thẻ chẩn đoán sư phạm 4D.

### Nhiệm Vụ 5: Tầng 3 Sinh Viên — Môi Trường Lập Trình IDE 3 Cột (`StudentIDE.jsx`, `Header.jsx`)
* Hỗ trợ Route `/student/ide/:exerciseId?classId=...&sessionId=...`.
* Nút `⬅️ Quay lại Lớp học phần` trên Header.
* Dropdown chuyển đổi bài tập trong cùng lớp/kỳ thi mà không cần thoát IDE.
* Đếm ngược thời gian phòng thi nếu `EXAM` mode.
* Bảo toàn 100% 3 cột Monaco Editor, Test cases, Custom Stdin, Visualizer, và Gia sư AI Socratic.

### Nhiệm Vụ 6: Giao Diện Giảng Viên Sidebar Workspace (`InstructorDashboard.jsx`)
* Fixed Sidebar bên trái (260px) với 4 mục: Quản lý Lớp học phần NEU, Ngân hàng Bài tập, Giám sát Bài nộp & AI, Hạ tầng MCP & Trình biên dịch.
* Không gian Quản trị Lớp học phần có 3 sub-tabs: Lộ trình & Inline edit sao tối thiểu, Kỳ thi & Đợt thực hành, Danh sách sinh viên & Tiến độ.
* Xem chi tiết code bài nộp, xuất CSV UTF-8.

---

## 3. Kết Quả Kiểm Thử
* `cd frontend && npm.cmd run build`: **0 errors (built in 2.57s)**.
* `py test_phase13_14_neu_lms.py`: **8/8 test categories PASS 100%**.
* `py test_phase12_classroom_exam.py`: **7/7 tests PASS 100%**.
* Backend E2E & MCP Server tests: **100% PASS**.
