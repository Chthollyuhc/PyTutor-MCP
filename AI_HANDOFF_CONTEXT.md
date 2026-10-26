# 📘 PYTUTOR-MCP: MASTER AI HANDOFF SPECIFICATION & ARCHITECTURAL BLUEPRINT
## TÀI LIỆU CHUYỂN GIAO TOÀN DIỆN VỀ KIẾN TRÚC, LÝ THUYẾT & TRIỂN KHAI HỆ THỐNG (v5.0 PRO NEU MULTI-STAGE LMS & IDE ARCHITECTURE)

> **MỤC ĐÍCH TỐI THƯỢNG:**  
> File tài liệu này là **"Single Source of Truth" (Kho Tri Thức Toàn Năng Duy Nhất)** của dự án **PyTutor-MCP**. Bất kỳ AI Assistant / Agent mới nào (ChatGPT, Claude, Cursor, Copilot, Antigravity) khi tiếp quản dự án **CHỈ CẦN ĐỌC DUY NHẤT FILE NÀY** là có thể nắm bắt 100% bản chất lý thuyết, kiến trúc dữ liệu, giao thức MCP, logic thuật toán sư phạm, lịch sử bug fix và có thể lập tức phát triển tiếp các Phase tiếp theo mà không cần phải quét lại bất kỳ file mã nguồn nào khác.

---

## 📑 MỤC LỤC TỔNG QUAN
1. [Cam Kết & Quy Tắc Vận Hành Cho Agent Mới](#1-cam-kết--quy-tắc-vận-hành-cho-agent-mới)
2. [Bản Chất Lý Thuyết & Triết Lý Thiết Kế Hệ Thống](#2-bản-chất-lý-thuyết--triết-lý-thiết-kế-hệ-thống)
3. [Kiến Trúc Tổng Thể Đa Tầng (End-to-End Architecture)](#3-kiến-trúc-tổng-thể-đa-tầng-end-to-end-architecture)
4. [Cơ Sở Dữ Liệu SQLite `pytutor.db` (Schema 9 Bảng & Concurrency WAL)](#4-cơ-sở-dữ-liệu-sqlite-pytutordb-schema--concurrency-wal)
5. [Đặc Tả Chi Tiết 8 MCP Tools (Engine Lõi Giao Thức stdio)](#5-đặc-tả-chi-tiết-8-mcp-tools-engine-lõi-giao-thức-stdio)
6. [Chiến Lược Sư Phạm Giàn Giáo (Scaffolding Pedagogy & Prompt Engineering)](#6-chiến-lược-sư-phạm-giàn-giáo-scaffolding-pedagogy--prompt-engineering)
7. [Hệ Thống Gamification, Sao Tự Lực & Code Review Tech Lead](#7-hệ-thống-gamification-sao-tự-lực--code-review-tech-lead)
8. [Đặc Tả Toàn Bộ Danh Mục 30+ API Endpoints (FastAPI Backend)](#8-đặc-tả-toàn-bộ-danh-mục-30-api-endpoints-fastapi-backend)
9. [Cấu Trúc Giao Diện React 18, Monaco Editor & 7 Modals](#9-cấu-trúc-giao-diện-react-18-monaco-editor--7-modals)
10. [Khả Năng Cắm Đa Nền Tảng (Multi-Host: Claude Desktop, Cursor, VS Code)](#10-khả-năng-cắm-đa-nền-tảng-multi-host-claude-desktop-cursor-vs-code)
11. [Kho Tri Thức Sửa Lỗi Kỹ Thuật (Known Gotchas & Bug Fixes History)](#11-kho-tri-thức-sửa-lỗi-kỹ-thuật-known-gotchas--bug-fixes-history)
12. [Cẩm Nang Khởi Chạy & Bộ Lệnh Kiểm Thử Toàn Diện (Run & Test Runbook)](#12-cẩm-nang-khởi-chạy--bộ-lệnh-kiểm-thử-toàn-diện-run--test-runbook)
13. [Mô Hình Triển Khai Học Viện: Lớp Tín Chỉ & Chế Độ Thi vs Thực Hành](#13-mô-hình-triển-khai-học-viện-lớp-tín-chỉ--chế-độ-thi-vs-thực-hành)
14. [Chuẩn Hóa Học Phần NEU, Quản Lý Đa Lớp Học Phần & Động Cơ Phân Tích Năng Lực 4 Chiều (Phase 13 & 14)](#14-chuẩn-hóa-học-phần-neu-quản-lý-đa-lớp-học-phần--động-cơ-phân-tích-năng-lực-4-chiều-phase-13--14)
15. [Kiến Trúc Điều Hướng Đa Tầng, Không Gian Lớp Học Phần Tách Biệt & Đại Tu 24 Môn NEU LMS (Phase 15 & 15.1)](#15-kiến-trúc-điều-hướng-đa-tầng--không-gian-lớp-học-phần-tách-biệt-phase-15)

---

## 1. CAM KẾT & QUY TẮC VẬN HÀNH CHO AGENT MỚI

Khi bạn (AI Agent mới) tiếp quản dự án này, bạn **BẮT BUỘC TUÂN THỦ 4 NGUYÊN TẮC CỐT LÕI**:

1. **Chính sách Không Hỏi Lại (Zero-Question Policy):**
   * Tuyệt đối không hỏi người dùng những câu hỏi xác nhận hiển nhiên (như *"Bạn có muốn tôi chạy test không?"*, *"Tôi có nên sửa file này không?"*).
   * Hãy chủ động phân tích, tự thực thi từ A đến Z, tự chạy test trên terminal và báo cáo kết quả hoàn tất.
2. **Bảo toàn Tính Năng & Ổn Định Tuyệt Đối:**
   * Hệ thống hiện tại đã hoàn thiện trọn vẹn từ **Phase 1 đến Phase 15 (v5.0 Pro NEU Multi-Stage LMS & IDE Architecture)** với **100% bài test PASS**.
   * Bất kỳ sửa đổi nào cũng phải đảm bảo: `npm.cmd run build` đạt 0 lỗi, các file test `test_phase*.py` đều pass 100%.
3. **Môi Trường Máy Tính Của Người Dùng:**
   * **Hệ điều hành:** Windows 11.
   * **Python:** Python 3.14 (Bắt buộc dùng lệnh `py`, KHÔNG dùng `python3`).
   * **Node.js / NPM:** Node v24.15.0 (Bắt buộc dùng `npm.cmd` và `npx.cmd`).
   * **Mã hóa Tiếng Việt UTF-8:** Mọi lệnh subprocess hoặc terminal đều phải thiết lập `$env:PYTHONIOENCODING="utf-8"` để tránh lỗi hiển thị tiếng Việt trên Windows console.
4. **Nguyên Tắc Thêm Dữ Liệu:**
   * Tuyệt đối **không tự ý chèn chay bài tập** vào file code Python. Mọi bài tập phải được thêm thông qua Dashboard Giảng viên trên giao diện web (`/instructor`) hoặc qua API hợp lệ để lưu vào SQLite `pytutor.db`.

---

## 2. BẢN CHẤT LÝ THUYẾT & TRIẾT LÝ THIẾT KẾ HỆ THỐNG

### 2.1. Đề tài & Tác giả
* **Tên đề tài:** Hệ thống Gia sư Thông minh Hỗ trợ Học Lập trình Python Dựa trên Model Context Protocol (MCP) (Đồ án Tốt nghiệp Đại học).
* **Sinh viên thực hiện:** Trần Minh Khánh (Sinh viên Khóa K65 CNTT — MSV: `11236131`).
* **Đơn vị đào tạo:** Khoa Công nghệ thông tin — Trường Đại học Kinh tế Quốc dân (NEU).
* **Giảng viên hướng dẫn:** Nguyễn Văn A & Trần Văn B.
* **Mục tiêu giáo dục:** Xây dựng một Hệ thống Gia sư Thông minh Thích ứng (Adaptive Intelligent Tutoring System - ITS) giúp sinh viên nhập môn lập trình Python tự rèn luyện tư duy giải quyết vấn đề mà không bị ỷ lại vào việc AI giải hộ (Anti-Spoil / Không lộ đáp án).

### 2.2. Vấn đề cốt tử của AI truyền thống trong Giáo dục Lập trình
Trước khi có MCP, các ứng dụng AI dạy lập trình (như ChatGPT, Copilot chat thông thường) mắc phải **5 căn bệnh nan y**:
1. **Ảo giác Kết quả (Hallucination - Thiếu Ground Truth):** Mô hình Ngôn ngữ Lớn (LLM) sinh từ theo xác suất thống kê (Token probability), nó **không phải trình thông dịch (Interpreter)**. Khi đọc một đoạn code có vòng lặp lồng nhau hoặc xử lý mảng biên, AI đoán sai kết quả từ 35% - 45%, dẫn đến giảng giải sai cho học sinh.
2. **Hiểm họa Sập Máy Chủ (Process Crashing):** Nếu web server chạy code sinh viên trực tiếp bằng `exec()` hoặc `eval()`, chỉ cần sinh viên viết `while True: pass` hoặc đệ quy vô hạn là **toàn bộ Web Server bị treo cứng hoặc cạn kiệt CPU**.
3. **Mất Trí Nhớ Sư Phạm (Stateless Amnesia):** API LLM thông thường là stateless (gọi xong quên ngay). AI không biết học viên đã thử bài này 5 lần trước đó và đều sai ở vòng lặp, dẫn đến việc lặp đi lặp lại những câu hỏi gợi mở ban đầu làm học sinh ức chế.
4. **Phân Mảnh & Khó Mở Rộng (Hardcoded Integration):** Muốn thêm một chức năng phân tích cú pháp mới, lập trình viên phải sửa lại code Backend, sửa Router, sửa DTO và hardcode vào prompt.
5. **Bị Khóa Chặt Vào Nhà Cung Cấp (Vendor Lock-in):** Dùng Function Calling độc quyền của OpenAI thì không chạy được với Gemini hoặc các mô hình mã nguồn mở cục bộ như Qwen/Ollama.

### 2.3. Giải pháp Đột Phá: Model Context Protocol (MCP)
**Model Context Protocol (MCP)** là một chuẩn giao thức mở do **Anthropic** công bố vào cuối năm 2024, được coi là **"Cổng USB-C của thời đại Trí tuệ Nhân tạo"**.
* **Ẩn dụ chuẩn mực:** LLM là "bộ não thiên tài trong phòng kính". MCP là sợi cáp kết nối mang lại cho bộ não đó:
  * **Tay chân:** Tự bấm máy chạy code thật trong hộp cát cô lập (`run_test_cases`, `trace_code_execution`).
  * **Kính hiển vi:** Soi từng node trên cây cú pháp trừu tượng (`analyze_code_ast`).
  * **Sổ tay sư phạm:** Ghi nhớ tiến trình và năng lực cá nhân hóa (`save_learning_event`, `get_student_model`).
* **Giao thức chuẩn:** Giao tiếp 100% qua chuẩn **JSON-RPC 2.0 trên luồng `stdio` (Standard Input / Output)**, cho phép kết nối an toàn, phân tách hoàn toàn giữa Host (FastAPI) và Server (`mcp_server`).

---

## 3. KIẾN TRÚC TỔNG THỂ ĐA TẦNG (END-TO-END ARCHITECTURE)

```
+---------------------------------------------------------------------------------------------------------+
|                                          TẦNG TRÌNH DUYỆT (CLIENT)                                      |
|  React 18 + Vite (Port 5173)                                                                            |
|  ├── /login : Đăng nhập & 1-Click Demo (Sinh viên: student/student123 | Giảng viên: gv_tran/gv123)     |
|  ├── /      : Student IDE 3 Cột Tinh Gọn (ProblemPanel | Monaco EditorPanel | TutorPanel)               |
|  │            ├── Nút Compact Pill: ⚡ Kết nối MCP (8)  ──► MCPInspectorModal.jsx (Showcase 3 Tabs)    |
|  │            ├── Nút 🗺️ Cây kỹ năng                   ──► SkillRoadmapModal.jsx (Đồ thị DAG)          |
|  │            ├── Nút 🏆 Bảng vàng                     ──► LeaderboardModal.jsx (Top 3 & 5 Badges)     |
|  │            ├── Nút 📒 Nhật ký học tập               ──► StudentProfileModal.jsx (Nạp lại code cũ)   |
|  │            ├── Nút 👁️ Chạy từng bước (Visualizer)   ──► ExecutionVisualizerModal.jsx (Trace Steps)  |
|  │            └── Nút 🚀 Thử thách Tối ưu Code Pythonic ──► PythonicReviewModal.jsx (Tech Lead Review)  |
|  └── /instructor : Instructor Dashboard (CRUD bài tập, Giám sát bài nộp, Chi tiết & Xuất CSV UTF-8)     |
+---------------------------------------------------------------------------------------------------------+
                                                     │ ▲
                                     REST API (JSON) │ │ Bearer JWT Token (24h)
                                                     ▼ │
+---------------------------------------------------------------------------------------------------------+
|                                  TẦNG ĐIỀU PHỐI BACKEND (FASTAPI MCP HOST)                              |
|  FastAPI (Port 8000)                                                                                    |
|  ├── Lifespan Event: Khởi tạo SQLite pytutor.db (WAL Mode, Seed 5 bài mẫu, Seed 2 tài khoản)            |
|  ├── Bảo mật & Phân quyền: backend/auth.py (JWT encode/decode, verify_token, require_instructor)         |
|  ├── Điều phối Sư phạm: backend/llm_service.py                                                          |
|  │     ├── Gemini 3.5 Flash Lite (Scaffolding 3 Levels: Gợi mở -> Chỉ chỗ sai -> Từng bước)             |
|  │     ├── Anti-Spoil Guard (Bộ lọc Regex tự động ẩn code giải dài >= 3 dòng ở Level 1-2)                |
|  │     ├── Multi-turn Follow-up Chat (Gia sư đàm thoại làm rõ, không lộ code giải)                      |
|  │     └── Senior Pythonic Code Review (Đánh giá Clean Code score 70-98, Strengths, Improvements)        |
|  ├── Gamification Engine: backend/database.py (Sao tự lực 1-3⭐, 5 Huy hiệu, Bảng xếp hạng)             |
|  └── MCP Host Client: backend/mcp_client.py (True Discovery qua tools/list, stdio JSON-RPC 2.0)         |
+---------------------------------------------------------------------------------------------------------+
                                                     │ ▲
                                     JSON-RPC 2.0    │ │ Pipe stdio (stdin/stdout)
                                  Subprocess cô lập  │ │ Đóng gói mcp_trace (ms)
                                                     ▼ │
+---------------------------------------------------------------------------------------------------------+
|                                  TẦNG ĐỘNG CƠ MCP SERVER (MCP SERVER ENGINE)                            |
|  mcp_server/server.py (MCPServer: "PyTutor-Code-Engine" - 8 Tools)                                      |
|                                                                                                         |
|  [Khối 1: Thực thi & Phân tích Code]                                                                    |
|    1. run_test_cases       : Sandbox Subprocess cô lập, Timeout cứng 5.0s, so sánh Output chuẩn        |
|    2. analyze_code_ast     : AST Static Parser, đếm For/While, phát hiện Đệ quy, Accumulator            |
|    3. trace_code_execution : Tracer sys.settrace ghi nhận line, event, snapshot biến số, max 150 bước / 3s|
|                                                                                                         |
|  [Khối 2: Quản lý Ngân hàng Học liệu]                                                                   |
|    4. get_exercise_list    : Danh mục bài tập từ SQLite (hoặc fallback exercises_data.py)               |
|    5. get_exercise_details : Đề bài Markdown, Starter code, Test cases chuẩn                             |
|                                                                                                         |
|  [Khối 3: Trí nhớ Sư phạm & Thích ứng]                                                                  |
|    6. save_learning_event  : Ghi nhận sự kiện nộp bài & phản hồi AI vào SQLite                            |
|    7. get_attempt_history  : Lấy 5 lần nộp bài gần nhất để AI nắm bắt tiến trình cải thiện              |
|    8. get_student_model    : Tính toán mô hình học sinh thích ứng (Mastered, Struggling, Hint Level)     |
+---------------------------------------------------------------------------------------------------------+
                                                     │ ▲
                                       Đọc / Ghi SQL │ │ sqlite3 Connection (timeout=20.0s)
                                       PRAGMA WAL    │ │ Row Factory Dict
                                                     ▼ │
+---------------------------------------------------------------------------------------------------------+
|                                     TẦNG DỮ LIỆU CỤC BỘ (SQLITE DATABASE)                               |
|  pytutor.db (Write-Ahead Logging Mode - Chống Lock 100%)                                                |
|  ├── exercises           : id, title, difficulty, category, description, starter_code, test_cases       |
|  ├── submissions         : id, session_id, exercise_id, code, hint_level, passed_tests, total_tests... |
|  ├── users               : username, password, role ('student'|'instructor'), full_name                |
|  ├── user_exercise_stars : username, exercise_id, stars_earned (1-3), highest_clean_score, timestamps  |
|  └── user_achievements   : username, badge_code, badge_title, badge_icon, description, unlocked_at     |
+---------------------------------------------------------------------------------------------------------+
```

---

## 4. CƠ SỞ DỮ LIỆU SQLITE `pytutor.db` (SCHEMA & CONCURRENCY WAL)

Cơ sở dữ liệu được định vị tại thư mục gốc: `c:\Users\Admin\Downloads\Sales-support-AI-pilot\pytutor.db`.

### 4.1. Giải pháp Chống Khóa Ghi Đồng Thời (Concurrency WAL Mode)
Trước Phase 10, SQLite sử dụng chế độ mặc định (`journal_mode=DELETE`), khi vừa nộp bài (ghi `submissions`), vừa chấm sao (ghi `user_exercise_stars`), vừa mở khóa huy hiệu (ghi `user_achievements`), hệ thống có nguy cơ phát sinh lỗi `sqlite3.OperationalError: database is locked`.  
**Giải pháp đã xử lý triệt để:**  
Cả 2 file kết nối database (`backend/database.py` và `mcp_server/storage.py`) đều được cấu hình:
```python
def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn
```
* `timeout=20.0`: Cho phép luồng chờ tối đa 20 giây thay vì fail ngay.
* `PRAGMA journal_mode=WAL;`: Kích hoạt **Write-Ahead Logging**, cho phép nhiều luồng ĐỌC đồng thời trong khi một luồng đang GHI mà không hề bị block.

### 4.2. Cấu trúc 8 Bảng Chi Tiết

#### Bảng 1: `exercises` (Ngân hàng bài tập lập trình)
```sql
CREATE TABLE IF NOT EXISTS exercises (
    id TEXT PRIMARY KEY,                       -- vd: 'ex_01_sum_1_to_n', 'ex_06_palindrome'
    title TEXT NOT NULL,                      -- Tiêu đề hiển thị
    difficulty TEXT NOT NULL,                 -- 'Dễ', 'Trung bình', 'Khó'
    category TEXT NOT NULL,                   -- Chủ đề thuật toán (Vòng lặp, Chuỗi, Đệ quy...)
    description TEXT NOT NULL,                -- Đề bài dạng Markdown hoàn chỉnh
    starter_code TEXT NOT NULL,               -- Mã nguồn mẫu khởi tạo trong Monaco Editor
    test_cases TEXT NOT NULL,                 -- JSON array chứa các test cases [{input, expected_output, description}]
    created_by TEXT DEFAULT 'system',         -- 'system' hoặc username của giảng viên tạo đề
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    is_active INTEGER DEFAULT 1               -- 1: Hiển thị, 0: Ẩn (xóa mềm)
);
```

#### Bảng 2: `submissions` (Nhật ký nộp bài & Vết học tập - Learning Trace)
```sql
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,                 -- Username sinh viên hoặc session định danh
    exercise_id TEXT NOT NULL,                -- Tham chiếu tới exercises.id
    code TEXT NOT NULL,                       -- Mã nguồn sinh viên nộp tại thời điểm đó
    hint_level INTEGER DEFAULT 1,             -- Cấp độ gợi ý đã chọn (1, 2, 3)
    passed_tests INTEGER DEFAULT 0,           -- Số test case vượt qua
    total_tests INTEGER DEFAULT 0,            -- Tổng số test cases
    all_passed INTEGER DEFAULT 0,             -- 1 nếu đúng 100%, 0 nếu có test fail
    llm_source TEXT DEFAULT '',               -- Tên mô hình AI sinh gợi ý ('gemini-3.5-flash-lite', 'Exam-Mode-Guard')
    tutor_hint TEXT DEFAULT '',               -- Toàn văn phản hồi sư phạm mà AI đã đưa ra
    timestamp TEXT DEFAULT (datetime('now', 'localtime'))
);
```

#### Bảng 3: `users` (Tài khoản người dùng & Phân quyền)
```sql
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,                -- 'student', 'gv_tran'
    password TEXT NOT NULL,                   -- Mật khẩu xác thực (demo: student123, gv123)
    role TEXT NOT NULL,                       -- 'student' hoặc 'instructor'
    full_name TEXT NOT NULL,                  -- Tên hiển thị đầy đủ
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);
```

#### Bảng 4: `user_exercise_stars` (Đánh giá Sao tự lực & Điểm Clean Code cao nhất)
```sql
CREATE TABLE IF NOT EXISTS user_exercise_stars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    exercise_id TEXT NOT NULL,
    stars_earned INTEGER NOT NULL CHECK (stars_earned BETWEEN 1 AND 3),
    best_submission_id INTEGER,
    highest_clean_score INTEGER DEFAULT 0,    -- Điểm Clean Code cao nhất từ Pythonic Review (0-100)
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(username, exercise_id)
);
```

#### Bảng 5: `user_achievements` (Bộ sưu tập Huy hiệu Thành tích của Học viên)
```sql
CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    badge_code TEXT NOT NULL,                 -- 'FIRST_SOLVE', 'INDEPENDENT_HERO',...
    badge_title TEXT NOT NULL,
    badge_icon TEXT DEFAULT '🏆',
    description TEXT DEFAULT '',
    unlocked_at TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(username, badge_code)
);
```

#### Bảng 6: `credit_classes` (Lớp Tín chỉ / Lớp Học phần Chuẩn NEU - Phase 12 & 13)
```sql
CREATE TABLE IF NOT EXISTS credit_classes (
    id TEXT PRIMARY KEY,                      -- vd: 'cls_neu_cntt1128_02'
    class_code TEXT NOT NULL UNIQUE,          -- Mã học phần/lớp NEU: 'CNTT1128(223)_02'
    class_name TEXT NOT NULL,                 -- Tên lớp: 'Cơ sở lập trình'
    course_code TEXT DEFAULT 'CNTT1116',      -- Mã môn học: 'CNTT1128'
    credits INTEGER DEFAULT 3,                -- Số tín chỉ
    faculty TEXT DEFAULT 'Khoa Công nghệ thông tin - NEU',
    semester TEXT DEFAULT 'Học kỳ 1 (2026-2027)',
    enrollment_code TEXT DEFAULT 'NEU-CSLP',   -- Mã ghi danh nhanh cho sinh viên
    instructor_username TEXT NOT NULL DEFAULT 'gv_tran',
    instructor_name TEXT DEFAULT 'Nguyễn Văn A',
    description TEXT DEFAULT '',              -- Mô tả mục tiêu học phần
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);
```

#### Bảng 7: `class_enrollments` (Danh sách Ghi danh Sinh viên vào Lớp Tín chỉ - Phase 12)
```sql
CREATE TABLE IF NOT EXISTS class_enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id TEXT NOT NULL,                   -- Khóa ngoại logic tới credit_classes.id
    student_username TEXT NOT NULL,           -- Khóa ngoại logic tới users.username
    enrolled_at TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(class_id, student_username)
);
```

#### Bảng 8: `exam_sessions` (Kỳ thi & Đợt Thực hành của Lớp Tín chỉ - Phase 12)
```sql
CREATE TABLE IF NOT EXISTS exam_sessions (
    id TEXT PRIMARY KEY,                      -- vd: 'sess_neu_practice_01', 'sess_neu_exam_midterm'
    title TEXT NOT NULL,                      -- vd: 'Kỳ thi Giữa kỳ Python (45 phút)'
    class_id TEXT NOT NULL,                   -- Thuộc lớp tín chỉ nào (credit_classes.id)
    session_type TEXT NOT NULL,               -- 'PRACTICE' (Luyện tập) hoặc 'EXAM' (Kỳ thi chính thức)
    exercise_ids TEXT NOT NULL,               -- JSON array chứa các ID bài tập chọn lọc: '["ex_01_sum_1_to_n", "ex_02_prime_check"]'
    duration_minutes INTEGER DEFAULT 60,      -- Thời lượng làm bài (phút), dùng cho Live Countdown Timer
    allow_ai_hints INTEGER DEFAULT 1,         -- 1: Bật Gia sư AI (Practice), 0: KHÓA AI hoàn toàn (Exam)
    is_active INTEGER DEFAULT 1,              -- 1: Đang mở cho sinh viên, 0: Đóng đợt thi
    created_by TEXT DEFAULT 'gv_tran',
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);
```

#### Bảng 9: `class_exercises` (Ma trận Kỹ năng & Lộ trình Học phần Tín chỉ - Phase 13 & 14)
```sql
CREATE TABLE IF NOT EXISTS class_exercises (
    id TEXT PRIMARY KEY,                      -- 'cls_xxx_ex_yyy'
    class_id TEXT NOT NULL,                   -- Khóa ngoại tới credit_classes.id
    exercise_id TEXT NOT NULL,                -- Khóa ngoại tới exercises.id
    module_name TEXT NOT NULL,                -- Tên chương (vd: 'Chương 1: Biến & I/O')
    order_idx INTEGER DEFAULT 0,              -- Thứ tự trong module
    prerequisite_id TEXT DEFAULT NULL,        -- Bài tập tiên quyết cần MASTERED
    min_stars_required INTEGER DEFAULT 1,     -- Số sao tự lực tối thiểu để đạt chuẩn (1-3 ⭐)
    skill_tag TEXT DEFAULT 'General',         -- Nhãn kỹ năng: Variables, Loops, Conditionals,...
    weight_point REAL DEFAULT 1.0,            -- Trọng số điểm
    added_at TEXT DEFAULT (datetime('now', 'localtime')),
    UNIQUE(class_id, exercise_id)
);
```

---

## 5. ĐẶC TẢ CHI TIẾT 8 MCP TOOLS (ENGINE LÕI GIAO THỨC STDIO)

File triển khai: [`mcp_server/server.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/mcp_server/server.py).  
Khởi tạo: `mcp = MCPServer("PyTutor-Code-Engine")`.  
Tất cả 8 công cụ đều được trang trí bằng `@mcp.tool()` và tự động công bố schema JSON qua lệnh `tools/list` của giao thức MCP.

### 5.1. Khối 1: Thực thi & Phân tích Code (Ground Truth Engine)

#### Tool 1: `run_test_cases(code: str, test_cases: list[dict]) -> dict`
* **File logic:** `mcp_server/sandbox.py` $\rightarrow$ `run_test_cases()`.
* **Cơ chế hoạt động:**
  * Khởi tạo subprocess độc lập bằng `subprocess.Popen([sys.executable, "-u", "-c", code])` với biến môi trường `PYTHONIOENCODING="utf-8"`.
  * Bơm `input` của từng test case qua `proc.communicate(input=stdin_data, timeout=5.0)`.
  * So sánh kết quả `actual_output.strip()` với `expected_output.strip()`.
  * Đo đạc chính xác thời gian thực thi `elapsed_ms`.
* **Phân loại lỗi:** Nếu exit code $\ne 0$, tự động trích xuất dòng cuối của stderr để phân loại: `SYNTAX_ERROR`, `RUNTIME_ERROR` (ZeroDivisionError, IndexError, NameError, ValueError,...).
* **Bảo vệ an toàn (Timeout 5.0s):** Nếu chạy quá 5 giây (do vòng lặp `while True`), subprocess bị cưỡng chế `proc.kill()`, trả về trạng thái `TIMEOUT` mà không làm treo Web Server. Nếu gặp `SYNTAX_ERROR` hoặc `TIMEOUT` ở test case nào, hệ thống tự động skip các test case phía sau để tối ưu hiệu năng.

#### Tool 2: `analyze_code_ast(code: str) -> dict`
* **File logic:** `mcp_server/ast_analyzer.py` $\rightarrow$ `analyze_code_ast()`.
* **Cơ chế hoạt động:**
  * Parse mã nguồn thành cây cú pháp trừu tượng bằng `ast.parse(code)`.
  * Nếu có lỗi cú pháp, bắt `SyntaxError`, lấy chính xác số dòng `line_number`, vị trí ký tự `offset` và thông báo lỗi.
  * Sử dụng `ast.NodeVisitor` duyệt cây để nhận diện:
    * **Vòng lặp:** Đếm số lượng `ast.For` và `ast.While`.
    * **Đệ quy (Recursion):** Bắt các `ast.FunctionDef`, kiểm tra xem bên trong thân hàm có lời gọi `ast.Call` nào trùng tên với chính hàm đó không.
    * **Biến tích lũy (Accumulator):** Phát hiện các phép toán gán dồn `ast.AugAssign` (`+=`, `-=`, `*=`, `/=`) hoặc gọi hàm dồn mảng (`.append()`, `.extend()`).
    * **Hàm tự định nghĩa:** Đếm số lượng `def` và danh sách tên hàm.

#### Tool 3: `trace_code_execution(code: str, stdin_input: str = "", max_steps: int = 150) -> dict`
* **File logic:** `mcp_server/tracer.py` $\rightarrow$ `trace_code_execution()`.
* **Cơ chế hoạt động:**
  * Cài đặt hàm trace tùy biến qua `sys.settrace()`.
  * Ghi nhận từng frame thực thi khi có sự kiện `line`, `call`, `return`.
  * Tại mỗi bước, chụp ảnh (snapshot) trạng thái các biến số cục bộ `frame.f_locals` (chỉ lọc các biến của học viên, loại trừ biến nội bộ `__name__`, `__doc__`,...).
  * Chuyển đổi an toàn giá trị biến sang chuỗi JSON-safe bằng hàm `_safe_serialize()`.
  * Bắt toàn bộ luồng xuất chuẩn `stdout` tại từng bước bằng `io.StringIO`.
* **Giới hạn an toàn:** Tự ngắt khi vượt quá `max_steps=150` bước hoặc quá thời gian `timeout_seconds=3.0s`.
* **Thân thiện hóa lỗi EOFError:** Nếu code có gọi `input()` nhưng học viên chưa cung cấp đủ dữ liệu stdin trong Visualizer, hệ thống tự động bắt `EOFError` và trả về thông báo hướng dẫn tiếng Việt rõ ràng, kích hoạt nút 1-click điền stdin mẫu trên giao diện.

---

### 5.2. Khối 2: Quản lý Ngân hàng Học liệu (SQLite Data Engine)

#### Tool 4: `get_exercise_list() -> dict`
* **File logic:** `mcp_server/storage.py` $\rightarrow$ `get_all_exercises_summary()`.
* **Cơ chế:** Truy vấn các bài tập có `is_active = 1` từ bảng `exercises` trong SQLite, đếm số lượng test cases từ JSON field và trả về danh sách tóm tắt (id, title, difficulty, category, test_cases_count). Nếu bảng rỗng, tự động fallback lấy từ `mcp_server/exercises_data.py`.

#### Tool 5: `get_exercise_details(exercise_id: str) -> dict`
* **File logic:** `mcp_server/storage.py` $\rightarrow$ `get_exercise_by_id(exercise_id)`.
* **Cơ chế:** Truy vấn chi tiết một bài tập từ SQLite, tự động `json.loads(test_cases)` thành mảng đối tượng chuẩn, trả về đầy đủ đề bài Markdown, starter code và danh sách test cases làm **Ground Truth** cho hệ thống.

---

### 5.3. Khối 3: Trí nhớ Sư phạm & Cá nhân hóa (Stateful Memory)

#### Tool 6: `save_learning_event(...) -> dict`
* **File logic:** `mcp_server/storage.py` $\rightarrow$ `save_submission()`.
* **Cơ chế:** Lưu toàn bộ thông tin lần nộp bài (session_id, exercise_id, code, hint_level, passed_tests, total_tests, all_passed, llm_source, tutor_hint) vào bảng `submissions` trong SQLite. Trả về `submission_id`.

#### Tool 7: `get_attempt_history(session_id: str, exercise_id: str) -> dict`
* **File logic:** `mcp_server/storage.py` $\rightarrow$ `get_attempts(session_id, exercise_id, limit=5)`.
* **Cơ chế:** Lấy tối đa 5 lần nộp bài gần nhất của học viên đối với bài tập đó. Giúp LLM nhận biết: *"Học viên đã nộp 3 lần, lần 1 đạt 1/5 test, lần 2 đạt 3/5 test, lần này đang vướng ở test số 4"*. Từ đó, AI không bao giờ đặt lại câu hỏi mở ban đầu mà tập trung tháo gỡ điểm nghẽn hiện tại.

#### Tool 8: `get_student_model(session_id: str) -> dict`
* **File logic:** `mcp_server/storage.py` $\rightarrow$ `compute_student_model(session_id)`.
* **Cơ chế tính toán Adaptive ITS:**
  * Gom nhóm lịch sử nộp bài của `session_id` theo từng `exercise_id`.
  * **Mastered Exercises (Đã làm chủ):** Các bài có ít nhất một lần nộp `all_passed == 1`.
  * **Struggling Exercises (Đang gặp khó khăn):** Các bài đã nộp từ 3 lần trở lên nhưng chưa lần nào pass 100%.
  * **Average Hint Level:** Cấp độ gợi ý trung bình mà học viên thường phải yêu cầu.
  * **Summary:** Chuỗi văn bản tự động tóm tắt năng lực học tập để bơm trực tiếp vào System Prompt của AI.

---

## 6. CHIẾN LƯỢC SƯ PHẠM GIÀN GIÁO & AI PROMPT ENGINEERING

File điều phối chính: [`backend/llm_service.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/llm_service.py).  
Mô hình AI sử dụng: **Google Gemini 3.5 Flash Lite** (`gemini-3.5-flash-lite`) thông qua SDK chính thức `google-genai`.

### 6.1. Phương Pháp Sư Phạm Giàn Giáo (Scaffolding Pedagogy)
Khi học viên gặp lỗi, hệ thống không bao giờ giải hộ ngay lập tức mà áp dụng kỹ thuật giàn giáo 3 cấp độ:
* **Mức 1: 💡 Gợi ý nhẹ (Conceptual / Socratic Hint):**
  * *Mục tiêu:* Đặt câu hỏi gợi mở để học viên tự nhận ra vấn đề logic.
  * *Ràng buộc:* Tuyệt đối không chỉ ra dòng lỗi cụ thể, không viết bất kỳ dòng code Python nào, không nói đáp án.
* **Mức 2: 🔍 Chỉ chỗ sai (Diagnostic Hint):**
  * *Mục tiêu:* Dựa vào Test Case bị FAIL và cấu trúc AST, chỉ rõ khối lệnh hoặc điều kiện đang bị lỗi logic.
  * *Ràng buộc:* Giải thích vì sao với dữ liệu đầu vào đó thì chương trình lại in ra kết quả sai lệch. Không cung cấp code sửa hoàn chỉnh.
* **Mức 3: 🧭 Hướng dẫn từng bước (Step-by-Step & Pseudocode):**
  * *Mục tiêu:* Cung cấp dàn ý thuật toán chi tiết từng bước (Bước 1 làm gì, Bước 2 làm gì).
  * *Được phép:* Cung cấp mã giả (Pseudocode) hoặc giải thích hàm thư viện.
  * *Ràng buộc cứng:* Tuyệt đối không đưa code Python hoàn chỉnh để copy-paste.

### 6.2. Bộ Lọc Hậu Kiểm Chống Lộ Lời Giải (Anti-Spoil Guard)
* **Hàm:** `sanitize_spoil_code(response_text, hint_level, all_passed)`.
* **Cơ chế:** Sử dụng biểu thức chính quy (Regex) quét qua toàn bộ phản hồi của LLM:
  * Nếu bài tập **chưa pass 100%** và đang ở **Mức 1 hoặc Mức 2**:
  * Bất kỳ khối code Markdown nào (` ```python ... ``` ` hoặc ` ``` ... ``` `) có độ dài từ **3 dòng lệnh trở lên** đều bị tự động cắt bỏ và thay thế bằng thông báo sư phạm:
    > *"🔒 [Đoạn mã minh họa đã được PyTutor ẩn tự động ở Level 1-2 để bạn tự rèn luyện tư duy lập trình]"*

### 6.3. Trò Chuyện Đa Lượt Làm Rõ (Multi-turn Follow-up Chat - Phase 8)
* **Endpoint:** `POST /api/tutor/chat` $\rightarrow$ `generate_chat_followup()`.
* Học viên có thể gõ câu hỏi thắc mắc trực tiếp tại khung chat ở Cột 3.
* Hệ thống đóng gói: Đề bài + Code hiện tại + Tóm tắt AST + 6 lượt chat gần nhất + Câu hỏi mới.
* Prompt bắt buộc Gemini đóng vai gia sư Socratic, kiên quyết từ chối nếu sinh viên nài nỉ xin code hoàn chỉnh, chỉ giải thích bản chất cú pháp bằng ví dụ trừu tượng ngắn không liên quan trực tiếp đến đề bài.

### 6.4. Đánh Giá Code Chuẩn Tech Lead (Pythonic Review - Phase 10)
* **Endpoint:** `POST /api/tutor/pythonic-review` $\rightarrow$ `generate_pythonic_review()`.
* Kích hoạt tự động khi học viên **đã giải đúng 100% test cases**.
* Gemini đóng vai **Senior Python Architect**, chấm điểm Clean Code theo chuẩn PEP 8 và tính Pythonic (thang điểm 70 - 98, sàn 70 để khích lệ).
* Bắt buộc trả về JSON hợp lệ với 5 trường:
  1. `clean_score`: Điểm số (int).
  2. `strengths`: Lời khen cụ thể về thuật toán hoặc cấu trúc logic.
  3. `improvements`: Cơ hội tối ưu bằng đặc trưng tinh hoa của Python (dùng `sum()`, list comprehension, slicing, built-in functions...).
  4. `pythonic_code`: Đoạn mã viết lại hoàn chỉnh nhất theo phong cách Pythonic.
  5. `explanation`: Lời giải thích chuyên sâu vì sao cách viết này tối ưu hơn ở tầng C / bộ nhớ.

---

## 7. HỆ THỐNG GAMIFICATION, SAO TỰ LỰC & CODE REVIEW TECH LEAD

File logic: [`backend/database.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/database.py).

### 7.1. Thuật Toán Chấm Sao Tự Lực (Autonomy Stars Rating)
* **Hàm:** `calculate_autonomy_stars(attempt_count, max_hint_level_used, all_passed)`.
* **Quy tắc sư phạm:**
  * **0 Sao:** Chưa vượt qua 100% test cases.
  * **3 Sao ⭐⭐⭐ (Tự lực Xuất sắc):** Pass 100% mà chỉ dùng gợi ý $\le$ Mức 1 (hoặc tự giải không hỏi AI).
  * **2 Sao ⭐⭐ (Khá giỏi):** Pass 100% nhưng cần sự hỗ trợ của Mức 2 (Chỉ chỗ sai).
  * **1 Sao ⭐ (Hoàn thành):** Pass 100% nhưng cần hướng dẫn từng bước của Mức 3.
* Điểm sao được lưu vào bảng `user_exercise_stars`. Mỗi bài tập lưu lại số sao cao nhất mà học viên từng đạt được.

### 7.2. Hệ Thống 5 Huy Hiệu Vinh Danh (Achievement Badges)
Định nghĩa trong `BADGE_DEFINITIONS`:
1. `FIRST_SOLVE` (**Bước Chân Đầu Tiên** 🌟): Mở khóa ngay khi hoàn thành bài tập đầu tiên trong đời.
2. `INDEPENDENT_HERO` (**Bậc Thầy Tự Lực** 🦸‍♂️): Đạt điểm tối đa **3 Sao trên ít nhất 3 bài tập khác nhau**.
3. `BUG_HUNTER` (**Thợ Săn Lỗi Tự Thân** ⚡): Hoàn thành bài tập đúng 100% sau ít nhất một lần nộp bài trước đó bị fail (biểu dương tinh thần tự sửa lỗi).
4. `PYTHONIC_EXPLORER` (**Nhà Khai Phá Pythonic** 🐍): Đạt điểm Clean Code $\ge 90$ điểm trong phần review code chuyên sâu.
5. `MARATHON_CODER` (**Kiên Trì Bền Bỉ** 🧗): Hoàn thành một bài tập sau hơn 5 lần kiên trì thử sức.

### 7.3. Bảng Vàng Lớp Học (Classroom Leaderboard)
* **Hàm:** `get_class_leaderboard(limit=20)`.
* Xếp hạng toàn bộ học viên theo thứ tự ưu tiên:
  $$\text{total\_stars} \downarrow \quad \longrightarrow \quad \text{completed\_exercises} \downarrow \quad \longrightarrow \quad \text{highest\_clean\_score} \downarrow$$
* Hiển thị danh sách huy hiệu thực tế đã mở khóa của từng học sinh.

---

## 8. ĐẶC TẢ TOÀN BỘ DANH MỤC 30+ API ENDPOINTS (FASTAPI BACKEND)

File triển khai: [`backend/main.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/main.py).  
Port: `http://127.0.0.1:8000`.

| Method | Endpoint | Yêu cầu Auth | Mô tả chức năng & Luồng xử lý |
| :---: | :--- | :---: | :--- |
| `POST` | `/api/auth/login` | Public | Đăng nhập (`student`/`student123`, `gv_tran`/`gv123`), sinh Bearer JWT Token 24h. |
| `GET` | `/api/auth/me` | Bearer Token | Xác thực token và lấy thông tin người dùng hiện tại (username, role, full_name). |
| `GET` | `/api/health` | Public | **True MCP Discovery & Trình biên dịch**: Kết nối MCP Server qua stdio, gọi `session.list_tools()`, trả về danh sách 8 tools và đối tượng `compiler_config` minh bạch đường dẫn Python, cờ chạy, encoding và sandbox timeout. |
| `GET` | `/api/exercises` | Public | Lấy danh mục bài tập tóm tắt qua MCP tool `get_exercise_list`. |
| `GET` | `/api/exercises/{id}` | Public | Lấy chi tiết đề bài, starter code, test cases qua MCP tool `get_exercise_details`. |
| `POST` | `/api/run-test` | Public | **Chạy thử siêu tốc (Không tốn AI quota):** Gọi MCP pipeline lấy test cases, chạy Sandbox và phân tích AST. Trả về kết quả kèm `mcp_trace`. |
| `POST` | `/api/submit` | Public | **Điểm chạm nộp bài chính (Main E2E Route):** Gọi MCP Sandbox + AST + Lịch sử + Student Model $\rightarrow$ Nếu `EXAM mode`: khóa AI, ghi nhận kết quả chấm khách quan $\rightarrow$ Nếu `PRACTICE mode`: gọi Gemini sinh gợi ý sư phạm $\rightarrow$ Lưu `save_learning_event` $\rightarrow$ Tính sao tự lực & mở khóa badge. |
| `POST` | `/api/tutor/chat` | Public | **Trò chuyện đa lượt Socratic (Phase 8):** Gửi câu hỏi làm rõ kèm ngữ cảnh bài làm và lịch sử chat, gọi Gemini với Anti-Spoil Guard. Bị chặn tuyệt đối nếu đang trong chế độ `EXAM`. |
| `POST` | `/api/custom-run` | Public | **Chạy thử Custom Stdin (Phase 8):** Nhận code và stdin tùy ý, thực thi qua Sandbox an toàn có timeout 5.0s. |
| `POST` | `/api/trace-execution`| Public | **Tracing bước chạy (Phase 9):** Gọi MCP tool `trace_code_execution`, trả về frame-by-frame snapshot biến số cho Visualizer. |
| `GET` | `/api/student/profile` | Public | Gọi MCP tools `get_student_model` và `get_attempt_history`, trả về hồ sơ năng lực và các lần nộp gần nhất để nạp lại code. |
| `GET` | `/api/skill-roadmap` | Public | Xây dựng đồ thị DAG phụ thuộc bài tập 4 tầng, gán trạng thái `MASTERED`, `IN_PROGRESS`, `AVAILABLE`, `LOCKED`. |
| `POST` | `/api/tutor/pythonic-review`| Public | Đánh giá Clean Code chuẩn Senior Tech Lead cho bài đã pass 100%, tự động mở khóa badge `PYTHONIC_EXPLORER` nếu điểm $\ge 90$. |
| `GET` | `/api/leaderboard` | Public | Lấy bảng vàng xếp hạng học viên theo tổng sao tự lực và số bài giải. |
| `GET` | `/api/student/achievements`| Public | Lấy tổng số sao, chi tiết sao từng bài và danh sách huy hiệu đã mở khóa của học viên. |
| `GET` | `/api/classes` | Public | Lấy danh sách toàn bộ Lớp tín chỉ kèm thông tin giảng viên phụ trách, sĩ số sinh viên và số kỳ thi. |
| `POST` | `/api/instructor/classes`| Giảng viên | Giảng viên tạo mới một lớp tín chỉ (`class_code`, `class_name`, `semester`, `description`). |
| `POST` | `/api/classes/{class_id}/enroll`| Public | Ghi danh một sinh viên vào lớp tín chỉ (`student_username`). |
| `GET` | `/api/exam-sessions` | Public | Lấy danh sách kỳ thi & đợt thực hành (hỗ trợ lọc theo `class_id`). |
| `POST` | `/api/instructor/exam-sessions`| Giảng viên | Giảng viên tạo kỳ thi hoặc đợt thực hành: chọn lớp, đặt thời gian (phút), chế độ (`PRACTICE` vs `EXAM`), và danh sách bài tập chọn lọc (`exercise_ids`). |
| `DELETE`| `/api/instructor/exam-sessions/{session_id}`| Giảng viên | Giảng viên xóa bỏ một đợt thi hoặc đợt thực hành. |
| `GET` | `/api/instructor/dashboard`| Giảng viên | Thống kê số lượng bài tập, tổng lượt nộp bài, số học viên active và tỷ lệ pass cả lớp. |
| `GET` | `/api/instructor/submissions`| Giảng viên | Xem toàn bộ 100 lần nộp bài gần nhất của sinh viên (kèm mã nguồn, kết quả test và tutor hint). |
| `GET` | `/api/instructor/submissions/{id}`| Giảng viên | Xem chi tiết toàn diện một bài nộp cụ thể. |
| `GET` | `/api/instructor/exercises`| Giảng viên | Lấy toàn bộ bài tập (bao gồm cả bài ẩn `is_active=0`). |
| `POST` | `/api/instructor/exercises`| Giảng viên | Giảng viên tạo mới một bài tập lập trình vào SQLite. |
| `PUT` | `/api/instructor/exercises/{id}`| Giảng viên | Giảng viên chỉnh sửa nội dung bài tập đã có. |
| `DELETE`| `/api/instructor/exercises/{id}`| Giảng viên | Giảng viên xóa bài tập khỏi ngân hàng đề. |

### 8.1. Cơ chế Chốt chặn Bảo mật Kỳ thi (EXAM Mode Guard)
Trong môi trường giáo dục đại học, khi sinh viên làm bài kiểm tra hoặc thi giữa kỳ/cuối kỳ, hệ thống cần đảm bảo tính trung thực học thuật:
* Khi sinh viên tham gia một session có `session_type == "EXAM"` hoặc `allow_ai_hints == 0`:
  * `POST /api/submit`: Hệ thống vẫn kích hoạt MCP Sandbox để chấm điểm test cases và ghi vết học tập vào `submissions`, nhưng **bỏ qua hoàn toàn cuộc gọi tới Gemini LLM**. Trường `llm_source` được gán cố định là `"Exam-Mode-Guard"` và phản hồi sư phạm nhắc nhở sinh viên tập trung làm bài độc lập.
  * `POST /api/tutor/chat`: Trả về ngay cảnh báo từ chối cung cấp gợi ý trong giờ thi.

### 8.2. Cấu hình Trình biên dịch Minh bạch (`compiler_config` trong `/api/health`)
Endpoint `/api/health` trả về cấu hình chi tiết của môi trường thực thi:
* `executable_path`: Đường dẫn tuyệt đối tới file thực thi Python trên máy chủ (`sys.executable`).
* `version`: Phiên bản Python thực tế (vd: `3.14.0`).
* `platform`: Hệ điều hành lưu trữ (vd: `win32` / Windows 11).
* `execution_flags`: Các cờ chạy dòng lệnh chuẩn (`-u` unbuffered I/O, `-c` in-memory bytecode compilation).
* `encoding`: Chuẩn mã hóa dữ liệu I/O (`utf-8` / `PYTHONIOENCODING=utf-8`).
* `isolation_mechanism`: Cơ chế cô lập tiến trình qua `subprocess.Popen` kết hợp giao thức MCP JSON-RPC 2.0 stdio.
* `sandbox_timeout_seconds`: Ngưỡng ngắt an toàn của hộp cát (`5.0s`).
* `tracer_limits`: Giới hạn của bộ trực quan hóa dữ liệu (`150 steps / 3.0s timeout`).
* `database_engine`: Cơ sở dữ liệu SQLite3 chế độ WAL (`timeout=20.0s`).

---

## 9. CẤU TRÚC GIAO DIỆN REACT 18, MONACO EDITOR & 7 MODALS

Frontend chạy bằng **Vite + React 18 + Tailwind CSS** tại cổng `http://localhost:5173`.  
Được thiết kế theo tiêu chuẩn công thái học (Ergonomics) giúp sinh viên học code tập trung cao độ.

### 9.1. Bố Cục 3 Cột Màn Hình Chính (`StudentIDE.jsx`)
* **Thanh Header & Banner Đếm Ngược Kỳ Thi:**
  * Hiển thị trạng thái lớp học, thông tin tài khoản đăng nhập, và các nút truy cập modal.
  * Khi chọn một kỳ thi (`EXAM`), phía trên màn hình xuất hiện **Banner Đỏ Cảnh Báo kèm Đồng Hồ Đếm Ngược Trực Tiếp (Live Countdown Timer)** hiển thị phút:giây còn lại.
* **Cột 1 (Bên trái - `ProblemPanel.jsx`):**
  * **Bộ chọn Lớp tín chỉ (`credit_classes`):** Cho phép sinh viên chuyển đổi giữa các lớp học phần ghi danh.
  * **Bộ chọn Kỳ thi / Đợt thực hành (`exam_sessions`):** Khi chọn một đợt thi cụ thể, danh sách bài tập bên dưới tự động lọc đúng theo danh sách bài tập được giảng viên giao.
  * Hiển thị huy hiệu độ khó, chủ đề, số test cases.
  * Nội dung đề bài Markdown được format bảng biểu và danh sách đẹp mắt.
  * Xem trước các test cases mẫu (Input / Output mong đợi).
* **Cột 2 (Ở giữa - `EditorPanel.jsx`):**
  * Trình soạn thảo chuyên nghiệp **Monaco Editor** (nhân của VS Code) hỗ trợ syntax highlight Python, tự động thụt lề.
  * **Auto-save nháp:** Tự động lưu mã nguồn đang gõ vào `localStorage` theo key `pytutor_draft_${exerciseId}`. Khi F5 hoặc đổi bài rồi quay lại, code cũ được phục hồi nguyên vẹn.
  * **Tô đỏ dòng lỗi (Error Decoration):** Khi test case bị lỗi cú pháp hoặc runtime error, Monaco tự động đánh dấu dải màu đỏ cảnh báo trên chính xác dòng lệnh gây lỗi kèm hover tooltip. Khi học viên gõ sửa code, dải màu tự động biến mất.
  * **2 Phím tắt toàn cục:**
    * `Ctrl + Enter`: Chạy thử nhanh qua Sandbox (không tốn AI quota).
    * `Ctrl + Shift + Enter`: Nộp bài chính thức & Gọi Gia sư AI (hoặc nộp bài thi trong chế độ EXAM).
  * **Tab Custom Stdin:** Cho phép học viên tự gõ dữ liệu đầu vào tùy ý để chạy thử nghiệm.
* **Cột 3 (Bên phải - `TutorPanel.jsx`):**
  * Tiêu đề: **`🤖 Trợ lý Học tập PyTutor`**.
  * **Chế độ Thi (`EXAM`):** Khóa hoàn toàn 3 mức gợi ý và ô chat với bảng cảnh báo vi phạm quy chế thi.
  * **Chế độ Luyện tập (`PRACTICE`):**
    * Bộ chọn 3 mức độ gợi ý sư phạm: `💡 Gợi ý nhẹ`, `🔍 Chỉ chỗ sai`, `🧭 Hướng dẫn từng bước`.
    * **Thẻ AST Nhận diện nhanh code:** Thu gọn/mở rộng hiển thị số dòng lệnh, có vòng lặp for/while không, có biến tích lũy không, có đệ quy không.
    * Nút leo thang gợi ý: *"Vẫn thấy khó? Xem gợi ý chi tiết hơn (Mức X) ▶"*.
    * **Khung Chat Đa lượt:** Học viên gõ câu hỏi thắc mắc trực tiếp với Gia sư AI.
    * **Huy hiệu Sao & Nút Kích hoạt Pythonic Review:** Khi pass 100%, hiển thị số sao tự lực đạt được (⭐⭐⭐) và nút bấm `🚀 Thử thách Tối ưu Code Pythonic`.

### 9.2. Trung Tâm 6 Modals Chuyên Dụng & Dashboard Giảng Viên

#### Dashboard Giảng Viên (`InstructorDashboard.jsx` - 3 Tabs Quản trị)
* **Tab 1 - 📚 Quản lý Ngân hàng Bài tập & Lịch sử Nộp bài:** Thống kê tổng quan lớp học, CRUD đề bài vào SQLite, xem chi tiết bài làm sinh viên và xuất báo cáo CSV UTF-8 BOM cho Excel.
* **Tab 2 - 🏛️ Quản lý Lớp tín chỉ:** Tạo mới lớp tín chỉ (`IT1110-K66-01`), quản lý học kỳ, hiển thị sĩ số sinh viên đã ghi danh.
* **Tab 3 - 📝 Quản lý Kỳ thi & Đợt thực hành:** Giảng viên tạo kỳ thi/đợt thực hành mới: chọn lớp phụ trách, đặt tên đợt thi, chọn chế độ (`PRACTICE` mở AI vs `EXAM` khóa AI), cấu hình thời gian làm bài (phút), và **tích chọn (checkbox) danh sách các bài tập từ ngân hàng đề** đưa vào đề thi.

#### Modal 1: `MCPInspectorModal.jsx` (Trung Tâm Trình Diễn MCP Showcase 3 Tabs)
* **Tab 1 - 🔌 8 Công cụ MCP, Live Trace & Cấu hình Trình biên dịch:**
  * **Thẻ Cấu hình Trình biên dịch & Sandbox Execution Infrastructure:** Hiển thị trực quan đường dẫn tuyệt đối của Python thực thi (`sys.executable`), phiên bản, cờ chạy (`-u -c`), bảng mã I/O (`UTF-8`), cơ chế cô lập tiến trình `subprocess.Popen` qua stdio, và các thông số an toàn (Timeout 5s, Tracer 150 bước, WAL 20s).
  * Phân nhóm 8 công cụ thành 3 khối chức năng, hiển thị nhật ký `mcp_trace` từng bước (Handshake, call_tool, ms), và nút bấm **"🔄 Khám phá lại Tools (Live Discovery)"** gọi `/api/health`.
* **Tab 2 - ⚖️ Tại sao dùng MCP?:** Ma trận đối chiếu 5 chiều giữa AI truyền thống (đoán mò, dễ crash server) vs PyTutor-MCP (chạy thật 100%, cô lập an toàn, trí nhớ sư phạm).
* **Tab 3 - 🌐 Cắm Đa Nền Tảng (Chuẩn USB-C):** Hướng dẫn cắm nóng `mcp_server` vào Claude Desktop, Cursor IDE, VS Code kèm nút copy JSON một chạm.

#### Modal 2: `ExecutionVisualizerModal.jsx` (Thanh Trượt Xem Từng Bước Biến Số)
* Hoạt động tương tự công cụ nổi tiếng *Python Tutor (pythontutor.com)* nhưng chạy hoàn toàn cục bộ qua MCP Tool `trace_code_execution`.
* Bộ điều khiển: `[⏮️ Bắt đầu] [◀ Lùi] [▶ Tiếp] [⏭️ Cuối] [⏯️ Tự chạy (1.2s)]`.
* Dòng code đang chạy được highlight sáng kèm mũi tên chỉ báo.
* Bảng biến số hiển thị giá trị thời gian thực; **biến nào vừa thay đổi giá trị sẽ được làm nổi bật màu xanh ngọc**.
* Tự động phát hiện hàm `input()` trong code và nạp sẵn dữ liệu mẫu từ test case 1; tích hợp nút 1-click sửa lỗi `EOFError`.

#### Modal 3: `SkillRoadmapModal.jsx` (Cây Lộ Trình Kỹ Năng Đồ Họa DAG)
* Xây dựng đồ thị có hướng (Directed Acyclic Graph) phân tầng 4 cấp độ kỹ năng:
  * Tầng 1: Biến & Nhập xuất (`ex_01_sum_1_to_n`)
  * Tầng 2: Cấu trúc Rẽ nhánh & Điều kiện (`ex_02_prime_check`)
  * Tầng 3: Vòng lặp & Đệ quy (`ex_03_factorial`)
  * Tầng 4: Xử lý Chuỗi & Slicing (`ex_04_reverse_string`, `ex_05_count_vowels`)
* Trạng thái thích ứng theo người học: 🟢 Đã làm chủ (Mastered), 🟡 Đang làm (In Progress), 🔵 Có thể học ngay (Available), 🔒 Đang khóa (Locked - do chưa hoàn thành bài tiên quyết).

#### Modal 4: `LeaderboardModal.jsx` (Bảng Vàng Lớp Học & Bộ Sưu Tập Huy Hiệu)
* Vinh danh Top 3 Podium: 🥇 Quán quân (Vàng), 🥈 Á quân (Bạc), 🥉 Quý quân (Đồng).
* Bảng xếp hạng chi tiết toàn lớp theo tổng số sao tự lực, số bài đã giải và điểm Clean Code cao nhất.
* Showcase bộ sưu tập 5 huy hiệu danh giá kèm điều kiện mở khóa.

#### Modal 5: `PythonicReviewModal.jsx` (Thử Thách Tối Ưu Code Chuẩn Tech Lead)
* Hiển thị đồng hồ đo điểm tròn (Circular Gauge) trực quan cho điểm Clean Code (0-100).
* Thẻ khen ngợi điểm mạnh (Strengths) và Thẻ gợi ý cải tiến chuẩn PEP 8 (Improvements).
* **Khung so sánh Diff Code:** Đặt mã nguồn của sinh viên song song với mã nguồn Pythonic tối ưu mẫu của Senior Architect.

#### Modal 6: `StudentProfileModal.jsx` (Nhật Ký Học Tập & Nạp Lại Code Cũ)
* Tóm tắt năng lực cá nhân từ Student Model.
* Danh sách lịch sử các lần nộp bài gần nhất: hiển thị số test đạt, cấp độ gợi ý và thời gian nộp.
* Tích hợp nút **"📥 Nạp lại code lần nộp này"** giúp học viên dễ dàng đưa phiên bản code cũ trở lại Monaco Editor để tiếp tục phát triển.

---

## 10. KHẢ NĂNG CẮM ĐA NỀN TẢNG (MULTI-HOST: CLAUDE DESKTOP, CURSOR, VS CODE)

Một trong những giá trị học thuật và thực tiễn cao nhất của đồ án là chứng minh **tính độc lập của MCP Server**: Engine không bị "giam cầm" trong trang web PyTutor mà có thể cắm trực tiếp vào các môi trường phát triển chuyên nghiệp.

Thư mục lưu trữ: [`mcp_configs/`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/mcp_configs/).

### 10.1. Cấu hình Claude Desktop App (`mcp_configs/claude_desktop_config.json`)
Đường dẫn trên Windows: `%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "pytutor-engine": {
      "command": "py",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\Users\\Admin\\Downloads\\Sales-support-AI-pilot",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```
*Sau khi lưu, khởi động Claude Desktop $\rightarrow$ Biểu tượng chiếc búa 🔨 xuất hiện, Claude có thể gọi trực tiếp 8 tools của PyTutor để chấm bài và lấy đề.*

### 10.2. Cấu hình Cursor IDE (`mcp_configs/cursor_mcp.json`)
Đường dẫn: `.cursor/mcp.json` tại thư mục dự án hoặc cấu hình toàn cục của Cursor:
```json
{
  "mcpServers": {
    "pytutor-engine": {
      "command": "py",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\Users\\Admin\\Downloads\\Sales-support-AI-pilot",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### 10.3. Cấu hình VS Code GitHub Copilot / Cline (`mcp_configs/vscode_mcp.json`)
```json
{
  "cline.mcpServers": {
    "pytutor-engine": {
      "command": "py",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\Users\\Admin\\Downloads\\Sales-support-AI-pilot",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      },
      "disabled": false,
      "autoApprove": [
        "run_test_cases",
        "analyze_code_ast",
        "get_exercise_list",
        "get_exercise_details",
        "trace_code_execution"
      ]
    }
  }
}
```

---

## 11. KHO TRI THỨC SỬA LỖI KỸ THUẬT (KNOWN GOTCHAS & BUG FIXES HISTORY)

Agent mới cần đọc kỹ mục này để **không bao giờ lặp lại các lỗi đã được giải quyết**:

1. **Lỗi `EOFError: EOF when reading a line` trong Visualizer (Hotfix Phase 10):**
   * *Nguyên nhân:* Khi sinh viên viết code có lệnh `input()` nhưng mở Visualizer mà không nhập dữ liệu vào ô `stdin`. Trình thông dịch Python gọi `sys.stdin.readline()` gặp kết thúc luồng rỗng và quăng lỗi `EOFError`.
   * *Giải pháp:* Trong `mcp_server/tracer.py`, thêm khối `except EOFError` trả về thông báo tiếng Việt giải thích lý do cần nhập stdin. Trên `ExecutionVisualizerModal.jsx`, tự động phát hiện `input(` trong code, tự động mở thanh nhập dữ liệu và nạp sẵn stdin mẫu từ test case 1; bổ sung nút 1-click điền lại dữ liệu.
2. **Lỗi `database is locked` trong SQLite (Hotfix Post-Audit):**
   * *Nguyên nhân:* Nhiều tiến trình cùng mở SQLite với chế độ journal mặc định DELETE và timeout 5s.
   * *Giải pháp:* Luôn mở kết nối bằng `sqlite3.connect(..., timeout=20.0)` và thực thi `PRAGMA journal_mode=WAL;` ở cả `backend/database.py` và `mcp_server/storage.py`.
3. **Lỗi Tràn Trang / Không Cuộn Được Form Thêm Bài Tập (Hotfix Phase 11):**
   * *Nguyên nhân:* File `frontend/index.html` có thẻ `<body class="... overflow-hidden">` làm khóa cứng thanh cuộn của cửa sổ trình duyệt; đồng thời `ExerciseFormPage.jsx` dùng `min-h-screen` khiến chiều cao không bị chặn lại, làm `<main>` không tự kích hoạt thanh cuộn dọc.
   * *Giải pháp:* Đổi thẻ `body` thành `overflow-x-hidden`. Trong `ExerciseFormPage.jsx` và `InstructorDashboard.jsx`, đặt container gốc thành `h-screen overflow-hidden` và `<main>` thành `flex-1 overflow-y-auto pb-20`. Nâng cấp thanh lưu bài thành dạng Sticky bám đáy có hiệu ứng kính mờ `backdrop-blur-md`.
4. **Lỗi Nuốt Bảng Markdown Ở Cuối Đề Bài (Hotfix Post-Audit):**
   * *Nguyên nhân:* Trong `ProblemPanel.jsx`, hàm `renderFormattedContent` duyệt từng dòng và chỉ đẩy bảng vào danh sách khi gặp dòng không phải bảng. Nếu bảng nằm ở cuối cùng của đề bài, biến `inTable` không bao giờ được flush.
   * *Giải pháp:* Thêm khối kiểm tra `if (inTable && tableRows.length > 0)` ngay sau vòng lặp để bảo đảm bảng luôn được render 100%.

---

## 12. CẨM NANG KHỞI CHẠY & BỘ LỆNH KIỂM THỬ TOÀN DIỆN (RUN & TEST RUNBOOK)

### 12.1. Lệnh Khởi Chạy Hệ Thống
* **Cách 1 (Khuyên dùng - 1 Click):**  
  Click đúp chuột vào file `start_dev.bat` ở thư mục gốc (hoặc chạy lệnh PowerShell: `.\start_dev.ps1`).  
  File script sẽ tự động mở 2 cửa sổ console: một cửa sổ chạy Backend FastAPI (port 8000), một cửa sổ chạy Frontend Vite React (port 5173).
* **Cách 2 (Khởi chạy thủ công từng dịch vụ):**
  * **Cửa sổ 1 (Backend):**
    ```powershell
    $env:PYTHONIOENCODING="utf-8"
    py -m uvicorn backend.main:app --reload --port 8000
    ```
  * **Cửa sổ 2 (Frontend):**
    ```powershell
    cd frontend
    npm.cmd run dev
    ```
* **Mở ứng dụng trên trình duyệt:** `http://localhost:5173`

### 12.2. Tài Khoản Đăng Nhập Mẫu (Demo Credentials)
* **Tài khoản Sinh viên:**  
  * Username: `student` | Password: `student123`  
  * Quyền hạn: Làm bài tập, chạy thử, hỏi gia sư AI, xem lộ trình kỹ năng, xem bảng vàng, xem visualizer.
* **Tài khoản Giảng viên:**  
  * Username: `gv_tran` | Password: `gv123`  
  * Quyền hạn: Toàn quyền truy cập Dashboard Giảng viên (`/instructor`), thêm/sửa/xóa bài tập trong SQLite, xem lịch sử nộp bài của cả lớp, xuất báo cáo CSV UTF-8 BOM.

### 12.3. Bộ Lệnh Kiểm Thử Tự Động (Tất Cả Phải PASS 100% Trước Khi Bàn Giao)
Agent mới trước khi hoàn tất bất kỳ task nào phải chạy các lệnh sau trong terminal PowerShell:

```powershell
# 1. Đặt biến môi trường UTF-8 bắt buộc trên Windows
$env:PYTHONIOENCODING="utf-8"

# 2. Kiểm thử toàn diện 8 công cụ MCP Server (Handshake, Timeout 5s, AST, Sandbox)
py -m mcp_server.test_mcp_server

# 3. Kiểm thử Backend Phase 5 (Auth JWT, Phân quyền Giảng viên, CRUD Bài tập, Learning Events)
py test_phase5_backend.py

# 4. Kiểm thử Backend Phase 8 (Custom Input Stdin, Multi-turn Chat, Anti-Spoil Guard)
py test_phase8_chat.py

# 5. Kiểm thử Backend Phase 9 (MCP Tool 8 trace_code_execution, Visualizer, Skill Roadmap DAG)
py test_phase9_visualizer.py

# 6. Kiểm thử Backend Phase 10 (Sao tự lực 1-3⭐, 5 Huy hiệu, Review Pythonic, Leaderboard)
py test_phase10_gamification.py

# 7. Kiểm thử tích hợp E2E Backend tổng thể
py -m backend.test_backend_e2e

# 8. Kiểm thử Backend Phase 12 (Lớp tín chỉ, Kỳ thi/Thực hành, EXAM Mode Guard, Compiler Specs)
py test_phase12_classroom_exam.py

# 9. Kiểm thử Backend Phase 13 & 14 (NEU LMS, Đa Lớp Học Phần, Ma Trận Kỹ Năng & Phân Tích Năng Lực 4 Chiều)
py test_phase13_14_neu_lms.py

# 10. Kiểm thử Backend & Frontend Integration Phase 15.3 (QA Audit Hotfix & Data Integrity)
py test_phase15_3_qa_audit.py

# 11. Kiểm thử Tách Biệt 3 Nút & Đồng Bộ Dữ Liệu Giao Diện Phase 15.4
py test_phase15_4_action_buttons.py

# 12. Biên dịch Frontend Vite React (Bắt buộc phải đạt 0 errors)
cd frontend
npm.cmd run build
cd ..
```

---

## 13. MÔ HÌNH TRIỂN KHAI HỌC VIỆN: LỚP TÍN CHỈ & CHẾ ĐỘ THI VS THỰC HÀNH

### 13.1. Ngữ Cảnh Triển Khai Thực Tế Tại Trường Đại Học
Hệ thống PyTutor-MCP được thiết kế đặc thù phục vụ giảng dạy học phần **Lập trình Python** tại các trường Đại học kỹ thuật:
* **Lớp tín chỉ / Lớp học phần (`credit_classes`):** Đại diện cho một lớp sinh viên cụ thể trong học kỳ (ví dụ: `IT1110-K66-01`). Mỗi lớp do một Giảng viên phụ trách và có danh sách sinh viên ghi danh (`class_enrollments`).
* **Đợt thực hành & Kỳ thi (`exam_sessions`):** Thay vì để sinh viên tự do làm toàn bộ ngân hàng đề mọi lúc mọi nơi, Giảng viên có thể thiết lập các buổi thực hành định kỳ hoặc bài kiểm tra giữa kỳ/cuối kỳ với bộ đề được chọn lọc (`exercise_ids`) và giới hạn thời gian làm bài (`duration_minutes`).

### 13.2. Bảng Đối Chiếu: Chế Độ Luyện Tập (PRACTICE) vs Chế Độ Thi (EXAM)

| Tiêu chí | Chế độ Luyện tập (`PRACTICE`) | Chế độ Thi / Kiểm tra (`EXAM`) |
| :--- | :--- | :--- |
| **Mục đích sư phạm** | Học tập tương tác, xây dựng tư duy thuật toán từng bước | Đánh giá năng lực tự lập, trung thực và công bằng học thuật |
| **Gia sư AI (Gemini 3.5 Flash Lite)** | **BẬT 100%**: 3 mức gợi ý Scaffolding, Anti-Spoil Guard, trò chuyện Socratic đa lượt | **KHÓA TUYỆT ĐỐI**: Chặn xin gợi ý, chặn chat AI |
| **Cơ chế Chốt chặn Backend** | `POST /api/submit` kích hoạt Scaffolding Prompt | `EXAM Mode Guard` phát hiện session thi, **bỏ qua gọi LLM**, gán `llm_source="Exam-Mode-Guard"` |
| **Cơ chế Chấm điểm** | MCP Sandbox thực thi test cases độc lập (timeout 5s) | MCP Sandbox thực thi test cases độc lập (timeout 5s) |
| **Giao diện IDE** | IDE 3 cột bình thường, đầy đủ tính năng trợ giúp | Banner đỏ cảnh báo thi cử, **Live Countdown Timer** (đếm ngược thời gian) |
| **Đánh giá & Thưởng** | Đánh giá 1-3 ⭐ tự lực, mở khóa huy hiệu, Pythonic Review | Chấm điểm PASS/FAIL test cases khách quan, lưu vết bài làm vào SQLite |

### 13.3. Minh Bạch Hóa Trình Biên Dịch & Hạ Tầng Thực Thi Sandbox
Để trả lời các câu hỏi kỹ thuật từ Hội đồng Chấm đồ án về môi trường thực thi mã nguồn:
* **Trình biên dịch:** `sys.executable` (vd: `C:\Users\Admin\AppData\Local\Programs\Python\Python314\python.exe`), phiên bản `Python 3.14.0`.
* **Cờ thực thi (Execution Flags):**
  * `-u`: Unbuffered I/O giúp luồng dữ liệu chuẩn `stdin/stdout` không bị đệm, truyền tức thời qua giao thức MCP stdio.
  * `-c`: Biên dịch bytecode và thực thi mã nguồn trực tiếp trong bộ nhớ RAM, không sinh file rác `.py` tạm thời trên ổ cứng.
* **Bảng mã I/O:** `UTF-8` thông qua biến môi trường `PYTHONIOENCODING="utf-8"` bảo đảm tiếng Việt không bị lỗi font trên hệ điều hành Windows.
* **Cơ chế cô lập (Process Isolation):** Sử dụng `subprocess.Popen` độc lập của hệ điều hành, giao tiếp hai chiều với Backend qua đường ống `stdin`/`stdout` chuẩn JSON-RPC 2.0 của MCP.
* **Thông số giới hạn an toàn (Safe Resource Quotas):**
  * Hộp cát chấm bài: Cưỡng chế ngắt (kill) sau **5.0 giây** nếu gặp vòng lặp vô hạn hoặc nghẽn mạng.
  * Hộp cát truy vết trực quan: Tự động dừng sau tối đa **150 bước lệnh** hoặc **3.0 giây**.
  * Cơ sở dữ liệu: SQLite3 chế độ WAL với thời gian chờ ghi **20.0 giây**.

---

## 14. CHUẨN HÓA HỌC PHẦN NEU, QUẢN LÝ ĐA LỚP HỌC PHẦN & ĐỘNG CƠ PHÂN TÍCH NĂNG LỰC 4 CHIỀU (PHASE 13 & 14)

### 14.1. Chuẩn Hóa Học Phần & Mã Lớp Theo Quy Chuẩn Đại Học Kinh Tế Quốc Dân (NEU)
Hệ thống v4.0 được chuẩn hóa hoàn toàn theo cấu trúc quản lý đào tạo tín chỉ thực tế của **Trường Đại học Kinh tế Quốc dân (NEU) - Khoa Công nghệ thông tin**:
* **Bảng Lớp tín chỉ (`credit_classes`):**
  * `id TEXT PRIMARY KEY`: Mã định danh hệ thống (vd: `cls_neu_cntt1116_01`).
  * `class_code TEXT UNIQUE`: Mã lớp học phần theo định dạng NEU (vd: `CNTT1116(126)_01`).
  * `course_code TEXT`: Mã học phần NEU (vd: `CNTT1116`, `CNTT1142`).
  * `class_name TEXT`: Tên học phần (vd: *Lập trình Python cơ bản*, *Phân tích dữ liệu với Python*).
  * `credits INTEGER`: Số tín chỉ học phần (3 tín chỉ).
  * `faculty TEXT`: Khoa phụ trách chuyên môn (*Khoa Công nghệ thông tin - NEU*).
  * `semester TEXT`: Học kỳ áp dụng (vd: *Học kỳ 1 - 2026-2027*).
  * `enrollment_code TEXT UNIQUE`: Mã đăng ký ghi danh nhanh cho sinh viên (vd: `NEU-PY01`, `NEU-PY02`, `NEU-DA01`).
  * `instructor_username TEXT`: Tài khoản Giảng viên phụ trách lớp.
  * `instructor_name TEXT`: Họ tên học hàm/học vị Giảng viên (vd: *Nguyễn Văn A*, *Trần Văn B*).
* **Tài khoản người dùng chuẩn NEU:**
  * `gv_tran`: Nguyễn Văn A (Giảng viên Khoa Công nghệ thông tin - NEU).
  * `gv_tuan`: Trần Văn B (Giảng viên Khoa Công nghệ thông tin - NEU).
  * `student`: Trần Minh Khánh (Sinh viên Khóa K65 CNTT - MSV: `11236131`).

---

### 14.2. Quản Lý Đa Lớp Học Phần & Ghi Danh Hai Chiều (Multi-Class Enrollment Architecture)
1. **Đối với Sinh viên (Multi-Class Enrollment):**
   * Sinh viên có thể đồng thời ghi danh vào nhiều lớp học phần khác nhau trong cùng một học kỳ.
   * Giao diện **Cổng Lớp học phần (`ClassPortalModal.jsx`)** cung cấp 2 chế độ:
     * **Tab 1 - Lớp của tôi:** Hiển thị thẻ từng lớp học phần đã ghi danh, tỷ lệ % tiến độ hoàn thành, Giảng viên phụ trách, số tín chỉ, nút "Chọn lớp đang học" và nút "Rút khỏi lớp".
     * **Tab 2 - Đăng ký ghi danh:** Cho phép nhập Mã ghi danh nhanh (`NEU-PY01`, ...) hoặc duyệt danh mục các lớp học phần đang mở tại NEU và bấm nút "Ghi danh ngay".
   * Trên thanh **Header (`Header.jsx`)**, hiển thị pill trạng thái trực quan: `🏫 [Mã Lớp] • [Tên Lớp] [Đổi lớp]` giúp sinh viên chuyển đổi tức thời ngữ cảnh lớp học mà không cần reload trang.
2. **Đối với Giảng viên (Class Management & Progress Roster):**
   * Giảng viên xem danh sách các lớp học phần do mình phụ trách tại Tab 2 của **Instructor Dashboard (`InstructorDashboard.jsx`)**.
   * Mỗi thẻ lớp cung cấp 2 công cụ quản trị nâng cao:
     * **⚙️ Lộ trình Kỹ năng (`Curriculum & Skill Matrix`):** Quản lý ma trận bài tập, module và điều kiện mở khóa riêng cho từng lớp.
     * **👥 Danh sách SV (`Class Student Roster`):** Tra cứu toàn bộ sinh viên đã ghi danh, xem số bài đã giải, tổng điểm kinh nghiệm (XP), số sao tự lực tích lũy và tỷ lệ hoàn thành học phần (%) của từng em.

---

### 14.3. Ma Trận Kỹ Năng & Lộ Trình Học Phần (Curriculum & Skill Matrix) với Thang Đo Định Lượng
Khắc phục nhược điểm của Cây Kỹ Năng tĩnh cứng nhắc trước đây, v4.0 giới thiệu bảng cấu trúc liên kết bài tập theo từng lớp:

#### 14.3.1. Cấu trúc Bảng `class_exercises`
```sql
CREATE TABLE IF NOT EXISTS class_exercises (
    id TEXT PRIMARY KEY,
    class_id TEXT NOT NULL,
    exercise_id TEXT NOT NULL,
    module_name TEXT NOT NULL,          -- Tên chương/module (vd: Chương 1: Cú pháp & I/O)
    order_idx INTEGER DEFAULT 0,        -- Thứ tự hiển thị trong module
    prerequisite_id TEXT DEFAULT NULL,  -- Bài tập tiên quyết cần vượt qua
    min_stars_required INTEGER DEFAULT 1, -- Số sao tự lực tối thiểu để đạt chuẩn (1-3 ⭐)
    skill_tag TEXT DEFAULT 'General',   -- Nhãn kỹ năng (Variables, Conditionals, Loops, ...)
    weight_point REAL DEFAULT 1.0,      -- Hệ số điểm đánh giá
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES credit_classes(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE,
    UNIQUE(class_id, exercise_id)
);
```

#### 14.3.2. Thang Đo Định Lượng (Mastery Rubric & State Machine)
Mỗi node kỹ năng trong đồ thị định hướng có chu trình (DAG) của lớp học phần được tính toán động dựa trên trạng thái học tập của sinh viên:
* **`MASTERED` (Đã làm chủ):** Sinh viên đã vượt qua 100% test case (`all_passed == 1`) **VÀ** số sao tự lực đạt được lớn hơn hoặc bằng chuẩn tối thiểu (`stars_earned >= min_stars_required`). Node hiển thị màu xanh lá rực rỡ kèm số sao đạt được.
* **`NEEDS_MORE_STARS` (Cần cải thiện sao tự lực):** Sinh viên đã giải được bài (`all_passed == 1`) nhưng do lạm dụng gợi ý hoặc chat AI nên số sao tự lực thấp hơn chuẩn của Giảng viên (`stars_earned < min_stars_required`). Hệ thống thông báo học viên cần làm lại bài tập độc lập hơn để mở khóa node tiên quyết tiếp theo.
* **`IN_PROGRESS` (Đang giải):** Sinh viên đã nộp bài ít nhất 1 lần nhưng chưa vượt qua toàn bộ test cases. Node hiển thị màu hổ phách.
* **`AVAILABLE` (Sẵn sàng mở khóa):** Toàn bộ bài tập tiên quyết (`prerequisite_id`) đã đạt trạng thái `MASTERED`. Sinh viên có thể bấm vào làm ngay.
* **`LOCKED` (Bị khóa):** Bài tập tiên quyết chưa đạt chuẩn năng lực tối thiểu. Node bị làm mờ kèm biểu tượng ổ khóa 🔒.

#### 14.3.3. Quyền Chỉnh Sửa Trực Tiếp Cho Giảng Viên (Instructor Direct Configuration)
Tại giao diện Giảng viên, Giảng viên có toàn quyền:
* **Gán bài tập từ Ngân hàng đề vào Lớp:** Thiết lập Module, Thứ tự, Bài tiên quyết và Chuẩn sao yêu cầu (1-3 ⭐).
* **Chỉnh sửa trực tiếp (Inline Edit):** Điều chỉnh nhanh `min_stars_required` (1 ⭐ Cơ bản, 2 ⭐ Khá, 3 ⭐ Tự lực tuyệt đối) ngay trên bảng danh sách.
* **Gỡ bài tập khỏi Lớp:** Loại bỏ bài tập khỏi lộ trình học phần mà không làm mất dữ liệu gốc trong ngân hàng đề.

---

### 14.4. Động Cơ Phân Tích Năng Lực 4 Chiều (4D Learning Analytics Engine) & Chẩn Đoán Sư Phạm Tự Động
Hàm `compute_student_model(session_id, class_id=None)` được tái cấu trúc toàn diện tại cả 2 tầng:
* `mcp_server/storage.py` (Lõi phân tích phía MCP Tool `get_student_model`)
* `backend/database.py` (Lõi phân tích phía Backend Service)

#### 14.4.1. 4 Chiều Chỉ Số Định Lượng (4D Quantitative Metrics)
1. **Chỉ số Tự lực / Độc lập Tư duy (`autonomy_score` - Thang điểm 0 - 100):**
   $$\text{Autonomy Score} = 0.7 \times \left(\frac{\sum \text{stars\_earned}}{3 \times N_{\text{solved}}} \times 100\right) + 0.3 \times \left(\frac{N_{\text{passed without hint lvl 2/3}}}{N_{\text{passed}}} \times 100\right)$$
   Đo lường mức độ tự mình giải quyết vấn đề của sinh viên mà không bị phụ thuộc vào gợi ý chi tiết của gia sư AI.
2. **Tỷ lệ Vượt qua Ngay Lần Đầu (`first_try_pass_rate` - %):**
   $$\text{First Try Pass Rate} = \frac{\text{Số bài giải đúng ngay ở lần nộp thứ nhất}}{\text{Tổng số bài đã giải thành công}} \times 100\%$$
   Phản ánh sự chắc chắn về cú pháp và khả năng lường trước các trường hợp biên (edge cases) trước khi bấm nộp bài.
3. **Số Lần Thử Trung Bình Để Giải Quyết Một Bài (`avg_attempts_to_solve`):**
   $$\text{Avg Attempts to Solve} = \frac{\text{Tổng số lần nộp bài của các bài đã giải}}{\text{Tổng số bài đã giải thành công}}$$
   Chỉ số đo lường tốc độ gỡ lỗi (debugging cycle time). Trung bình lý tưởng từ 1.2 - 2.5 lần/bài.
4. **Cơ Cấu Lỗi & Tỷ Lệ Nộp Bài (`error_breakdown`):**
   Phân loại tất cả các lần nộp thành 3 nhóm tỷ lệ %:
   * `passed_pct`: Tỷ lệ nộp bài thành công (All tests passed).
   * `logic_fail_pct`: Tỷ lệ sai logic thuật toán (Output không khớp kỳ vọng test case).
   * `syntax_runtime_pct`: Tỷ lệ lỗi cú pháp hoặc ngoại lệ thực thi (IndexError, TypeError, SyntaxError, ...).
5. **Ma Trận Làm Chủ Chủ Đề (`topic_mastery`):**
   Thống kê chi tiết tỷ lệ bài hoàn thành trên tổng số bài cho từng kỹ năng (`Variables`, `Conditionals`, `Loops`, `Strings`, `Functions`, `Lists`, `Dictionaries`).

#### 14.4.2. Chẩn Đoán Sư Phạm & Đề Xuất Học Tập Tự Động (AI Diagnostic Evaluation Cards)
Hệ thống tự động sinh 3 thẻ chẩn đoán năng lực dựa trên dữ liệu phân tích:
* **Phân loại Trình độ (`level_classification`):**
  * `Xuất sắc (Advanced)`: Autonomy score $\ge 80$ và số bài giải $\ge 3$.
  * `Khá (Competent)`: Autonomy score $\ge 60$ và số bài giải $\ge 2$.
  * `Đang phát triển (Developing)`: Đang trong quá trình tích lũy kiến thức cơ bản.
* **Thẻ 1 - Điểm mạnh Kỹ thuật (`strengths_analysis`):** Xác định khả năng tư duy tự lập, tỷ lệ giải đúng lần đầu và các chủ đề đã làm chủ hoàn toàn.
* **Thẻ 2 - Điểm nghẽn & Khó khăn Thường gặp (`weaknesses_and_bottlenecks`):** Nhận diện chính xác tỷ lệ lỗi logic so với lỗi cú pháp, phát hiện dấu hiệu lạm dụng gợi ý hoặc các chủ đề còn bị mắc kẹt.
* **Thẻ 3 - Khuyến nghị Hành động Kế tiếp (`recommended_next_action`):** Đưa ra chỉ dẫn học tập cụ thể (vd: *Cần giải lại bài XYZ với 0 gợi ý để nâng cao sao tự lực*, hoặc *Tiến hành mở khóa Chương tiếp theo*).

---

### 14.5. Đặc Tả Danh Mục API Endpoints Mới Thêm Ở Phase 13 & 14

| Phương thức | Đường dẫn API | Vai trò & Mục đích | Tham số & Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/student/my-classes` | Lấy danh sách lớp sinh viên đã ghi danh kèm tiến độ | Header Bearer Token |
| `POST` | `/api/classes/enroll-by-code` | Sinh viên ghi danh vào lớp bằng mã tham gia | `{ "enrollment_code": "NEU-PY01" }` |
| `POST` | `/api/classes/{class_id}/leave` | Sinh viên rút khỏi lớp học phần | URL param `class_id` |
| `GET` | `/api/classes/{class_id}/curriculum` | Lấy lộ trình môn học & danh sách bài tập của lớp | URL param `class_id` |
| `POST` | `/api/instructor/classes/{class_id}/exercises` | Giảng viên gán bài tập vào lớp học phần | Body: `ClassExerciseAssignRequest` |
| `PUT` | `/api/instructor/classes/{class_id}/exercises/{exercise_id}` | Giảng viên chỉnh sửa min_stars, order_idx của bài trong lớp | Body: `ClassExerciseUpdateRequest` |
| `DELETE` | `/api/instructor/classes/{class_id}/exercises/{exercise_id}` | Giảng viên gỡ bài tập khỏi lộ trình lớp | URL param `class_id`, `exercise_id` |
| `GET` | `/api/instructor/classes/{class_id}/students` | Giảng viên xem danh sách sinh viên & tiến độ chi tiết | URL param `class_id` |
| `GET` | `/api/skill-roadmap?class_id=...` | Lấy đồ thị kỹ năng DAG theo lớp kèm chuẩn sao | Query param `class_id` |
| `GET` | `/api/student/profile?class_id=...` | Lấy hồ sơ học tập 4D metrics & thẻ chẩn đoán sư phạm | Query param `class_id` |

---

### 14.6. Trải Nghiệm Giao Diện Người Dùng & Các Modals Nâng Cấp (Frontend Architecture)

1. **`ClassPortalModal.jsx` (Cổng Đa Lớp Học Phần NEU):**
   * Cho phép sinh viên quản lý đa lớp, đổi lớp đang học, xem % tiến độ từng môn, ghi danh lớp mới qua mã code hoặc catalogue.
2. **`SkillRoadmapModal.jsx` (Lộ Trình Kỹ Năng & Chuẩn Sao):**
   * Hiển thị tên lớp học phần NEU đang kích hoạt, giải thích bảng quy chuẩn Mastery Rubric, nhóm bài tập trực quan theo từng Module/Chương, hiển thị số sao yêu cầu `min_stars_required` so với số sao đạt được `stars_earned`, gắn nhãn cảnh báo `NEEDS_MORE_STARS` khi cần cải thiện tính tự lập.
3. **`StudentProfileModal.jsx` (Hồ Sơ Năng Lực 4 Chiều):**
   * Thẻ định danh sinh viên chuẩn NEU (Họ tên, MSV, Khoa CNTT - NEU), Badge phân loại năng lực (Xuất sắc / Khá / Đang phát triển), 4 thẻ chỉ số định lượng, thanh xếp chồng phân bổ cơ cấu lỗi, 3 thẻ chẩn đoán sư phạm thông minh và lịch sử nộp bài gần nhất.
4. **`InstructorDashboard.jsx` (Quản Lý Lộ Trình & Danh Sách Lớp):**
   * Tích hợp Modal quản lý Ma trận Kỹ năng (Curriculum Manager) cho phép Giảng viên thêm/sửa/xóa bài tập trong lớp, sửa đổi trực tiếp số sao yêu cầu, cùng Modal xem Roster sinh viên và tiến độ học tập thực tế.

---

## 15. KIẾN TRÚC ĐIỀU HƯỚNG ĐA TẦNG & KHÔNG GIAN LỚP HỌC PHẦN TÁCH BIỆT (PHASE 15)

### 15.1. Triết Lý Thiết Kế Tách Biệt Không Gian (Separation of Concerns: LMS vs IDE)
Phiên bản **v5.0 Pro** thực hiện bước chuyển mình kiến trúc quan trọng: **chấm dứt việc gom tất cả tính năng vào một màn hình IDE 3 cột duy nhất**.
Hệ thống kết hợp hài hòa giữa 2 chuẩn mực EdTech hàng đầu:
* **Mô hình LMS Đào tạo Tín chỉ Đại học (Chuẩn Coursera / Canvas):** Quản lý lớp học phần, đề cương học phần (Curriculum), đợt thực hành, kỳ thi, cây kỹ năng và bảng xếp hạng thành tích lớp học được tổ chức trên các trang chuyên biệt, rộng rãi, trực quan và không bị che khuất bởi các cửa sổ Modal chồng chéo.
* **Môi trường Lập trình Chuyên sâu (Chuẩn LeetCode / HackerRank):** Khi sinh viên bắt đầu viết mã nguồn cho một bài tập cụ thể, hệ thống mở ra một **Focused Coding Workspace** tập trung 100% tài nguyên màn hình cho việc đọc đề bài, soạn thảo code Monaco Editor, gỡ lỗi từng bước qua Visualizer và nhận phản hồi sư phạm Socratic từ Gia sư AI.

---

### 15.2. Luồng Người Dùng Sinh Viên Đa Tầng (3-Stage Student Journey)

```text
[Màn hình Đăng nhập Cổng NEU (/login)]
                 │
                 ▼
[Tầng 1: Cổng Học tập Sinh viên NEU (/student)]
  ├── 4 Thẻ KPI Tổng quan: Số lớp đang học, Bài đã giải, Sao tự lực, Autonomy Score / 100
  ├── Lưới Thẻ Lớp học phần đang theo học (Thanh tiến độ %, Giảng viên, Mã tham gia)
  ├── Form Đăng ký Ghi danh Lớp học phần mới bằng Mã tham gia (vd: NEU-PY02)
  └── Phòng Tự Luyện tập Tự do (Ngân hàng đề mở rộng)
                 │
                 ▼ (Bấm "👉 Vào Lớp Học Phần")
[Tầng 2: Không gian Chi tiết Lớp học phần (/student/classes/:classId)]
  ├── Header Lớp: Tên môn học, Mã lớp, Giảng viên phụ trách, Số tín chỉ, Tiến độ lớp
  ├── Nút "⬅️ Quay về Danh sách Lớp học phần"
  └── 4 Tabs Nội dung Trực tiếp trên trang:
        ├── Tab 1: 📚 Chương trình & Bài tập theo Module (Kèm chuẩn sao Mastery Rubrics)
        ├── Tab 2: 📝 Đợt thực hành & Kỳ thi của Lớp (Practice vs Exam mode)
        ├── Tab 3: 🗺️ Cây Kỹ năng Học phần DAG có tương tác (Click node vào IDE)
        └── Tab 4: 🏆 Bảng vàng Lớp học & Đánh giá Năng lực 4D Cá nhân
                 │
                 ▼ (Bấm "💻 Làm bài trên IDE ▶")
[Tầng 3: Môi trường Lập trình IDE 3 Cột (/student/ide/:exerciseId?classId=...&sessionId=...)]
  ├── Top Header: Nút nổi bật "⬅️ Quay lại Lớp học phần" + Dropdown chuyển nhanh bài tập
  ├── Banner đếm ngược thời gian làm bài nếu đang trong Kỳ thi (EXAM mode)
  ├── Cột 1: Đề bài Markdown, Bảng test cases mẫu, Chuẩn đầu ra số sao yêu cầu
  ├── Cột 2: Monaco Editor (Auto-save, tô đỏ lỗi, phím tắt), Visualizer, Custom Stdin, Kết quả Sandbox
  └── Cột 3: Gia sư AI Socratic 3 cấp độ, Nhận diện AST, Đánh giá 3 sao tự lực, Review Pythonic
```

---

### 15.3. Cổng Đăng Nhập Split-Screen NEU (`/login` - `LoginPage.jsx`)
* **Cột trái (Hero & Architecture Showcase):**
  - Thương hiệu **PyTutor-MCP • Hệ thống Quản lý Học tập & Gia sư Lập trình Thông minh (v5.0 Enterprise LMS)**.
  - Nhãn nhận diện: **Khoa Công nghệ thông tin • Đại học Kinh tế Quốc dân (NEU)**.
  - 3 Thẻ nổi bật: Đào tạo theo Lớp học phần Tín chỉ (`CNTT1116`, `CNTT1142`), Gia sư AI Thích ứng 3 cấp độ (Anti-Spoil Guard), và Động cơ 8 MCP Tools JSON-RPC 2.0 (Sandbox 5s, AST, Tracer).
* **Cột phải (Form Đăng nhập & 1-Click Demo):**
  - Form đăng nhập tài khoản / mật khẩu tiêu chuẩn.
  - Khối **⚡ Đăng nhập Nhanh 1-Click dành cho Hội đồng Chấm Đồ án**:
    1. *Sinh viên NEU:* Trần Minh Khánh (`student` / `student123`) $\rightarrow$ chuyển thẳng vào `/student`.
    2. *Giảng viên NEU:* Nguyễn Văn A (`gv_tran` / `gv123`) $\rightarrow$ chuyển thẳng vào `/instructor`.
    3. *Giảng viên 2:* Trần Văn B (`gv_tuan` / `gv123`) $\rightarrow$ chuyển thẳng vào `/instructor`.

---

### 15.4. Hệ Thống Quản Trị Giảng Viên Sidebar Workspace (`/instructor` - `InstructorDashboard.jsx`)
Thiết kế theo chuẩn **Modern Admin Sidebar Layout** (Thanh menu dọc cố định 260px bên trái + Không gian làm việc rộng mở bên phải):
1. **Sidebar Bên Trái:**
   - Logo PyTutor Lecturer Portal & Thẻ định danh Giảng viên (`Nguyễn Văn A - Khoa CNTT - NEU`).
   - 4 Nút điều hướng chính:
     1. `🏫 1. Quản lý Lớp học phần`: Lưới các lớp phụ trách + Mở lớp mới. Khi bấm vào 1 lớp cụ thể, mở **Không gian Quản trị Lớp** với 3 sub-tabs: (1) Lộ trình & Inline edit số sao yêu cầu, (2) Kỳ thi & Đợt thực hành, (3) Danh sách sinh viên & Tiến độ.
     2. `📚 2. Ngân hàng Bài tập`: Quản lý kho bài tập Python, thêm/sửa/xóa, kiểm thử test cases.
     3. `📊 3. Giám sát Bài nộp & AI`: Bảng lịch sử nộp bài toàn trường, xem chi tiết code & lời khuyên AI, xuất CSV UTF-8 Excel.
     4. `🔌 4. Hạ tầng MCP & Trình biên dịch`: Thông số `sys.executable`, Python 3.14, cờ `-u -c`, UTF-8, Sandbox 5s, 8 MCP Tools.
   - Nút chuyển nhanh sang Cổng Sinh viên (`/student`) và Nút Đăng xuất.

---

### 15.5. Cấu Hình Routing & Bảo Vệ Route Thông Minh (`frontend/src/App.jsx`)
* **Điều hướng Route gốc (`/`):**
  - Nếu chưa đăng nhập $\rightarrow$ Chuyển hướng sang `/login`.
  - Nếu đã đăng nhập với role `instructor` $\rightarrow$ Chuyển hướng sang `/instructor`.
  - Nếu đã đăng nhập với role `student` $\rightarrow$ Chuyển hướng sang `/student`.
* **Cơ chế Bảo vệ Route (`StudentRoute` & `InstructorRoute`):**
  - Tự động kiểm tra phiên đăng nhập và phân quyền (RBAC), ngăn chặn sinh viên truy cập trái phép vào Dashboard giảng viên hoặc người dùng chưa xác thực truy cập vào IDE.

---

### 15.6. Đại Tu Danh Mục Học Phần NEU (24 Môn CNTT từ LMS NEU), Chuẩn Hóa Giảng Viên & Cải Tiến Giao Diện (Phase 15.1)

#### 15.6.1. Khắc Phục Triệt Để Lỗi Màn Hình Đen (Black Screen Bug) ở Tab 4 Lớp Học Phần
* **Bối cảnh & Nguyên nhân:**
  Khi người dùng click vào Tab 4 (*🏆 Bảng vàng & Đánh giá Năng lực*) trên trang Không gian Chi tiết Lớp học phần (`/student/classes/:classId`), ứng dụng bị sập toàn bộ giao diện thành màn hình đen.
  *Nguyên nhân cốt lõi*: Endpoint Backend `/api/leaderboard` trả về một payload JSON dạng Object:
  `{ "leaderboard": [ ... ], "total_students": N }`
  Tuy nhiên, trong `StudentClassDetailPage.jsx`, hàm `loadClassData` thực hiện: `setLeaderboard(lb || [])`. Khi đó biến state `leaderboard` nhận giá trị là một Object `{ leaderboard: [...] }` thay vì Array thuần túy. Đến khi giao diện render Tab 4, câu lệnh `leaderboard.slice(0, 10)` ném ra ngoại lệ JavaScript: `TypeError: leaderboard.slice is not a function`, làm sập toàn bộ cây React Virtual DOM.
* **Giải pháp Khắc phục Toàn diện:**
  1. Chuẩn hóa ngay tại tầng nhận dữ liệu (`loadClassData`):
     ```javascript
     setLeaderboard(Array.isArray(lb) ? lb : (lb?.leaderboard || []));
     ```
  2. Bổ sung phòng thủ kép tại khối JSX render:
     ```javascript
     const safeLb = Array.isArray(leaderboard) ? leaderboard : [];
     safeLb.slice(0, 10).map(...)
     ```
  3. Bổ sung Optional Chaining và giá trị fallback an toàn cho các đối tượng KPI năng lực: `classProfile?.analytics_metrics` và `classProfile?.diagnostic_evaluation`, triệt tiêu hoàn toàn nguy cơ Null Reference Error khi học viên mới tham gia chưa có dữ liệu nộp bài.

#### 15.6.2. Đại Tu Danh Mục 24 Học Phần Chuẩn LMS Khoa CNTT - Đại Học Kinh Tế Quốc Dân (NEU)
Hệ thống đã dọn sạch toàn bộ các dữ liệu mẫu cũ (`cls_it1110%`, `cls_neu_cntt1116%`) và nạp lại **24 Lớp học phần thực tế** từ dữ liệu LMS NEU chính thức (đã lọc bỏ các môn đại cương ngoài ngành như GDTC, Triết học Mác-Lênin, Vật lý đại cương, Thư viện,...):
1. `cls_neu_cntt1128_02`: `CNTT1128(223)_02 - Cơ sở lập trình` (3 tín chỉ, Mã ghi danh: `NEU-CSLP`, GV: Nguyễn Văn A).
2. `cls_neu_cntt1187_01`: `CNTT1187(225)_01 - Lập trình phân tích dữ liệu` (3 tín chỉ, Mã ghi danh: `NEU-LTPTDL`, GV: Nguyễn Văn A).
3. `cls_neu_cntt1131_04`: `CNTT1131(124)_04 - Lập trình hướng đối tượng` (3 tín chỉ, Mã ghi danh: `NEU-OOP`, GV: Nguyễn Văn A).
4. `cls_neu_cntt1152_01`: `CNTT1152(125)_01 - Hệ quản trị cơ sở dữ liệu` (3 tín chỉ, Mã ghi danh: `NEU-HQTCSDL`, GV: Nguyễn Văn A).
5. `cls_neu_cntt1167_01`: `CNTT1167(225)_01 - Phát triển ứng dụng Web` (3 tín chỉ, Mã ghi danh: `NEU-WEB`, GV: Nguyễn Văn A).
6. `cls_neu_cntt1117_02`: `CNTT1117(125)_02 - Phân tích và thiết kế hệ thống` (3 tín chỉ, Mã: `NEU-PTTKHT`, GV: Trần Văn B).
7. `cls_neu_cntt1121_01`: `CNTT1121(225)_01 - Quản trị mạng Thứ 6` (3 tín chỉ, Mã: `NEU-QTM`, GV: Trần Văn B).
8. `cls_neu_cntt1154_01`: `CNTT1154(225)_01 - Mạng kết nối vạn vật` (3 tín chỉ, Mã: `NEU-IOT`, GV: Trần Văn B).
9. `cls_neu_tikt1130_04`: `TIKT1130(124)_04 - Cơ sở dữ liệu` (3 tín chỉ, Mã: `NEU-CSDL`, GV: Nguyễn Văn A).
10. `cls_neu_tikt1135_01`: `TIKT1135(124)_01 - Hệ điều hành` (3 tín chỉ, Mã: `NEU-HDH`, GV: Trần Văn B).
11. `cls_neu_cntt1164_01`: `CNTT1164(124)_01 - Cấu trúc dữ liệu và giải thuật` (3 tín chỉ, Mã: `NEU-CTDL`, GV: Nguyễn Văn A).
12. `cls_neu_cntt1172_01`: `CNTT1172(325)_01 - Đề án - Công nghệ thông tin` (3 tín chỉ, Mã: `NEU-DEAN`, GV: Nguyễn Văn A).
... và 12 lớp học phần CNTT chuyên ngành khác.

#### 15.6.3. Chuẩn Hóa Định Danh Giảng Viên & Sinh Viên
* **Giảng viên 1:** `Nguyễn Văn A` (Tài khoản: `gv_tran` / Mật khẩu: `gv123`).
* **Giảng viên 2:** `Trần Văn B` (Tài khoản: `gv_tuan` / Mật khẩu: `gv123`).
* **Sinh viên K65:** `Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)` (Tài khoản: `student` / Mật khẩu: `student123`).
* **Màn hình Đăng nhập (`LoginPage.jsx`):** Đã xóa bỏ tiêu đề đồ án rườm rà, thay thế bằng định danh chuẩn mực: `Khoa Công nghệ thông tin • Đại học Kinh tế Quốc dân (NEU)`.

#### 15.6.4. Nâng Cấp Trải Nghiệm Tìm Kiếm & Chế Độ Xem Đa Dạng
1. **Tìm kiếm Lớp học phần & Chế độ xem Lưới vs Danh sách (`StudentPortalPage.jsx`):**
   - Bổ sung ô tìm kiếm thời gian thực (`searchQuery`) lọc theo Tên môn học, Mã lớp và Tên giảng viên ở cả 2 khu vực: *Lớp của tôi* và *Lớp học phần mở*.
   - Bổ sung cụm nút chuyển chế độ hiển thị:
     - **Chế độ Lưới (Grid View):** 3 cột thẻ trực quan, phù hợp cho màn hình lớn.
     - **Chế độ Cột / Danh sách (List View):** Các dòng thẻ trải ngang thanh thoát, hiển thị rõ ràng số tín chỉ, tiến độ % thanh bar và các nút thao tác nhanh.
2. **Thanh Tìm Kiếm Bài Tập Trong Lớp (`StudentClassDetailPage.jsx`):**
   - Ô tìm kiếm bài tập tại Tab 1 (Chương trình & Bài tập) hỗ trợ lọc tức thì theo tên bài, module, độ khó và nhãn kỹ năng.
3. **Khóa Đổi Lớp & Tinh Gọn Môi Trường IDE (`ProblemPanel.jsx`):**
   - Tuyệt đối không cho phép sinh viên tự ý đổi lớp ngay trong giao diện code IDE nhằm đảm bảo tính toàn vẹn của ngữ cảnh bài nộp và phiên học.
   - Loại bỏ thẻ dropdown `<select>` chọn phiên thi thừa thãi, thay bằng Huy hiệu Trạng thái (Status Badge) thông báo minh bạch: `🟢 Đang trong chế độ: Luyện tập tự do` hoặc `🔒 Đang trong đợt thi: [Tên kỳ thi]`.

#### 15.6.5. Tinh Gọn Giao Diện Code IDE & Tối Ưu Công Thái Học (IDE Decluttering)
Nhằm tạo ra một **Focused Coding Workspace** thực sự thanh thoát, không gây xao nhãng và loại bỏ các thành phần trùng lặp giữa các tầng giao diện:
1. **Loại bỏ Nút "Cây kỹ năng" và Modal `SkillRoadmapModal` trong IDE:** Sinh viên đã xem sơ đồ trực quan và chọn bài tập tại Tab 3 của trang Lớp học phần (`/student/classes/:classId`), nên việc mở modal cây kỹ năng trong IDE là dư thừa.
2. **Loại bỏ Nút "Bảng vàng" và Modal `LeaderboardModal` trên Header IDE:** Thành tích xếp hạng lớp học và năng lực 4D đã được hiển thị đầy đủ, rộng rãi tại Tab 4 của trang Lớp học phần.
3. **Loại bỏ Ô Dropdown Chọn Bài Tập bên Cột Trái (`ProblemPanel.jsx`):** Sinh viên đã chọn bài từ ngoài và vào IDE để tập trung giải quyết trọn vẹn bài tập đó. Loại bỏ dropdown giúp phần đầu cột trái ngắn gọn, làm nổi bật ngay nhãn độ khó, chủ đề, số lượng test cases và toàn văn đề bài.
4. **Loại bỏ Subtitle Rườm Rà Trên Header:** Gỡ bỏ dòng chữ *"Khoa CNTT - neu gia sư thông minh..."* bên cạnh logo PyTutor, giúp thanh Header giữ được khoảng trống mắt (breathing space) sang trọng.
5. **Loại bỏ Nút Đăng Xuất Trên Header Khi Làm Bài:** Ngăn ngừa hoàn toàn nguy cơ sinh viên bấm nhầm nút đăng xuất làm gián đoạn bài làm dở dang hoặc mất phiên thi. Thao tác đăng xuất được gom gọn ra ngoài Cổng Sinh viên.
6. **Quy Về 1 Vị Trí Duy Nhất Hiển Thị Mã Lớp & Tên Học Phần:** Trước đây mã lớp xuất hiện trùng lặp ở 3 nơi (Nút Back, Huy hiệu giữa Header, Thẻ cột trái). Hệ thống đã tinh gọn: nút Back hiển thị nhãn sạch `⬅️ Quay lại Lớp học phần`, xóa bỏ huy hiệu giữa Header, và chỉ giữ lại một vị trí duy nhất tại Thẻ Lớp học phần ở đầu Cột 1 (`ProblemPanel.jsx`) hiển thị đầy đủ `Lớp: [class_code] • [class_name]`.

#### 15.6.6. Chuẩn Hóa Luồng Nộp Bài (Submit Flow), Đồng Bộ Định Danh Sinh Viên K65 & Trung Tâm Lịch Thi Tín Chỉ (Phase 15.2)
Nhằm giải quyết triệt để vấn đề sinh viên đã làm bài pass 100% test cases nhưng hệ thống chưa ghi nhận số sao và mở khóa bài tiếp theo:
1. **Phân Tách Rõ Ràng Giữa "Chạy Thử" và "Nộp Bài" (`EditorPanel.jsx`):**
   - Trước đây giao diện có 2 nút: `▶ Chạy thử code` (chỉ chạy test sandbox, không lưu kết quả) và `🤖 Hỏi Gia sư AI` (gọi submit nhưng nhãn gây hiểu nhầm là chỉ để xin gợi ý). Sinh viên chỉ bấm chạy thử mà không nộp bài chính thức.
   - Đã chuẩn hóa lại thành 2 nút với công năng trực quan:
     - **Nút 1 (Cyan): `▶ Chạy thử` (Ctrl + Enter):** Chạy thử code siêu tốc trong sandbox với các test cases mẫu, không chấm điểm chính thức.
     - **Nút 2 (Emerald Green): `🚀 Nộp bài` (Ctrl + Shift + Enter):** Chính thức nộp bài, tính điểm, ghi nhận số sao năng lực (1-3 ⭐), mở khóa bài tiên quyết tiếp theo và cập nhật Bảng Vàng.
   - **Banner Tự Động Gợi Ý Nộp Bài:** Khi sinh viên chạy thử và vượt qua toàn bộ test cases (`testResults.all_passed = true`), một banner chúc mừng nổi bật lập tức hiện ra kèm nút bấm trực tiếp `🚀 Nộp bài ngay`.
   - **Modal Chúc Mừng Sau Khi Nộp Thành Công (`StudentIDE.jsx`):** Sau khi nộp bài thành công, hệ thống bắn pháo hoa confetti, hiển thị modal chúc mừng với số sao đạt được và nút điều hướng 1-click `👉 Về Lớp Học Phần` hoặc tiếp tục ở lại IDE.

2. **Đồng Bộ Tuyệt Đối Định Danh Sinh Viên (`sessionId` Unification):**
   - Trước đây `StudentIDE.jsx` khởi tạo `sessionId` ngẫu nhiên từ `localStorage` (`stu_timestamp_random`), dẫn đến việc kết quả chấm bài bị lưu phân mảnh vào session ẩn danh, trong khi Cổng sinh viên và Lớp học phần tra cứu theo tài khoản `student` (`Trần Minh Khánh - SV K65 CNTT, MSV: 11236131`).
   - Đã thống nhất toàn diện: `sessionId` luôn ưu tiên `user?.username || 'student'` trong toàn bộ hệ thống (`StudentIDE.jsx`, `StudentClassDetailPage.jsx`, `StudentPortalPage.jsx`).
   - Đã chạy script di trú toàn bộ 6 sao, 14 lượt nộp bài và 4 huy hiệu về đúng định danh `student`. Sinh viên Trần Minh Khánh lập tức vươn lên vị trí chính thức trên Bảng Vàng.

3. **Khắc Phục Lỗi Logic Tra Cứu Sao Backend (`backend/main.py`):**
   - Sửa lỗi lệch key tại dòng 596: hàm `get_user_achievements` trong `database.py` trả về dictionary có key `"exercise_stars"`, nhưng `get_skill_roadmap_endpoint` lại tra cứu key `"stars_by_exercise"`.
   - Cập nhật chuẩn hóa: `achievements.get("exercise_stars", achievements.get("stars_by_exercise", {}))`. Ngay lập tức các bài tập đạt chuẩn hiển thị đúng 3 ⭐ và trạng thái `MASTERED`.

4. **Nâng Cấp API Lộ Trình Học Phần (`GET /api/classes/{class_id}/curriculum`):**
   - Bổ sung tham số `student_username: Optional[str] = None`. Khi truyền mã sinh viên, backend tự động tính toán động các trường: `status` (`MASTERED`, `AVAILABLE`, `IN_PROGRESS`, `LOCKED`), `stars_earned`, `status_description` và `is_unlocked` cho từng bài tập theo đúng thang đo định lượng Mastery Rubric.
   - Nhờ đó, tại Tab 1 của Lớp học phần, bài đã hoàn thành sẽ hiện huy hiệu `Đã đạt chuẩn (3 ⭐)`, bài tiếp theo mở khóa `Sẵn sàng làm bài`, và các bài nâng cao bị khóa `Khóa do chưa hoàn thành bài tiên quyết`.

5. **Sửa Lỗi Hiển Thị Tiến Độ Học Phần 0% (`StudentPortalPage.jsx`):**
   - Tại `StudentPortalPage.jsx` (cả Grid View và List View), mã nguồn trước đây tra cứu `cls.progress.progress_percent` (thuộc tính không tồn tại trong `CreditClassSummary`), dẫn đến tiến độ luôn bị gán 0%.
   - Đã cập nhật đọc trực tiếp các trường chuẩn: `cls.progress_percent` và `cls.completed_in_class`. Lớp Cơ sở lập trình hiển thị chính xác `1/5 bài (20%)`.

6. **Đại Tu Cột 3 Cổng Sinh Viên Thành "Trung Tâm Lịch Thi & Đợt Thực Hành":**
   - Theo phản ánh của người dùng về việc "Phòng tự luyện tập tự do" ở Cột 3 chỉ mở được bài 01 và gây dư thừa, hệ thống đã thay thế hoàn toàn khối này bằng **"Trung Tâm Lịch Thi & Đợt Thực Hành Tín Chỉ"** (Exam & Assignment Hub).
   - Tự động hiển thị các ca thi / đợt thực hành đang mở kèm thời lượng, mã lớp và nút bấm truy cập nhanh.
   - Tích hợp khu vực tóm tắt Huy hiệu năng lực đạt được và 2 nút tắt tiện ích: `🏆 Bảng Vàng K65` (mở `LeaderboardModal`) và `📊 Hồ Sơ 4D` (mở `StudentProfileModal`).

#### 15.6.7. Khắc Phục Triệt Để 5 Lỗi Nghiêm Trọng Từ Đợt Rà Soát Mã Nguồn (QA Audit Hotfix & Data Integrity - Phase 15.3)
Qua quá trình kiểm thử mã nguồn tĩnh (Static QA Audit) và rà soát đồng bộ dữ liệu giữa Backend và Frontend, hệ thống đã xử lý dứt điểm 5 vấn đề cốt lõi:

1. **Sửa lỗi `NameError: name 'get_db_connection' is not defined` tại `@app.get("/api/auth/me")` (`backend/main.py`):**
   - *Hiện trạng cũ:* Thiếu import `get_db_connection` ở đầu file `backend/main.py`. Mỗi lần người dùng nhấn F5 trên trình duyệt hoặc tải lại trang, route `/api/auth/me` trả về lỗi HTTP 500, kích hoạt `AuthContext.jsx` tự động đăng xuất người dùng (bị đẩy ra `/login`).
   - *Khắc phục:* Bổ sung `get_db_connection` vào danh sách import từ `backend.database`. Xác thực F5 / khôi phục phiên hoạt động trơn tru 100%.

2. **Khắc phục Đảo Ngược Thứ Tự Tham Số API tại `StudentClassDetailPage.jsx`:**
   - *Hiện trạng cũ:* Tại dòng 55-56, gọi `fetchSkillRoadmap(classId, sessionId)` và `fetchStudentProfile(sessionId, classId)` làm đảo lộn vị trí các tham số so với định nghĩa trong `frontend/src/services/api.js`:
     - `fetchSkillRoadmap(sessionId, classId)`: Gọi sai khiến backend nhận `sessionId = 'cls_...'` và `classId = 'student'`, dẫn đến truy vấn lộ trình kỹ năng của lớp bị trả về cây mặc định rỗng.
     - `fetchStudentProfile(sessionId, exerciseId, classId)`: Gọi sai làm `classId` bị truyền vào vị trí `exerciseId`, lọc sai dữ liệu hồ sơ.
   - *Khắc phục:* Đã chuẩn hóa chính xác thứ tự: `fetchSkillRoadmap(sessionId, classId)` và `fetchStudentProfile(sessionId, '', classId)`. Đồng thời rà soát toàn bộ các components (`SkillRoadmapModal`, `StudentProfileModal`, `StudentPortalPage`), đảm bảo 100% lời gọi API khớp đúng signature.

3. **Khắc phục Dead Code & Thắt Chặt Tiêu Chuẩn Mastery Rubric (`backend/database.py` & `backend/main.py`):**
   - *Hiện trạng cũ:* Trong `get_class_exercises` và `get_skill_roadmap_endpoint`, điều kiện phân loại trạng thái bài tập dùng `if ex_id in mastered_set or stars_earned >= min_stars`. Do `compute_student_model` đưa tất cả các bài có `all_passed == 1` vào `mastered_exercises`, các bài chỉ đạt 1 sao đã bị coi là `MASTERED` (dù yêu cầu 2 ⭐), khiến nhánh `NEEDS_MORE_STARS` biến thành Dead Code không bao giờ được chạm tới; đồng thời bài tiên quyết tiếp theo bị mở khóa sớm khi chưa đủ chuẩn sao.
   - *Khắc phục:* 
     - Xây dựng tập `mastered_set` nghiêm ngặt: yêu cầu học viên vừa phải `has_passed == True` VỪA PHẢI đạt `stars_earned >= min_stars`.
     - Nhánh `NEEDS_MORE_STARS` được kích hoạt chính xác: khi bài tập đã giải đúng toàn bộ test cases nhưng `stars_earned < min_stars` (thông báo: *"Đã giải đúng nhưng mới đạt X/Y ⭐. Hãy tự giải lại với ít gợi ý hơn để đạt chuẩn!"*).
     - Kiểm tra bài tiên quyết: bài phụ thuộc chỉ được chuyển sang `AVAILABLE` hoặc `IN_PROGRESS` khi bài tiên quyết đã nằm trong `mastered_set` (đạt đủ số sao tối thiểu).

4. **Sửa Lỗi Hiển Thị Điểm Tự Lực & Thống Nhất Chỉ Số Năng Lực 4D (`StudentPortalPage.jsx` & `StudentClassDetailPage.jsx`):**
   - *Hiện trạng cũ:* Thẻ KPI "Chỉ số Tự lực" trên Cổng Sinh viên hiển thị fallback cứng `profile?.analytics_metrics?.pedagogical_autonomy_score ?? 95` (sai key backend trả về `autonomy_score`). Tại thẻ tổng quan lớp, trường tổng sao đọc nhầm `currentClass?.total_stars` (thay vì `total_stars_in_class`).
   - *Khắc phục:* Cập nhật đọc chính xác `profile?.analytics_metrics?.autonomy_score ?? 0` và `currentClass?.total_stars_in_class`. Xác minh toàn bộ 4D metrics (`autonomy_score`, `first_try_pass_rate`, `avg_attempts_to_solve`, `error_breakdown`, `diagnostic_evaluation`) đồng bộ hoàn hảo giữa Backend và UI.

5. **Hoàn Thiện Tương Thích HTTP Methods & Luồng Điều Hướng (`backend/main.py`, `StudentIDE.jsx`, `InstructorDashboard.jsx`):**
   - *Hỗ trợ kép HTTP Route:* Route hủy ghi danh `/api/classes/{class_id}/leave` được hỗ trợ đồng thời cả `DELETE` và `POST` (`@app.delete` & `@app.post`), triệt tiêu rủi ro lỗi HTTP 405 Method Not Allowed khi client hoặc proxy gửi POST.
   - *Điều hướng Nút Back IDE:* Nút `⬅️ Quay lại Lớp học phần` trong `StudentIDE.jsx` trỏ chuẩn xác về `/student/classes/{classId}` dựa trên `classIdParam` hoặc `currentClass?.id`, tránh bị văng ra cổng ngoài `/student`.
   - *Đồng bộ tức thì Workspace Giảng viên:* Tại `InstructorDashboard.jsx`, khi giảng viên gán bài tập, cập nhật số sao hoặc gỡ bài khỏi lớp, hệ thống gọi đồng thời cả `fetchCurriculum` và `fetchCreditClasses` để cập nhật lập tức số lượng bài tập và ma trận kỹ năng trên giao diện mà không cần F5.

6. **Bộ Kiểm Thử Tự Động Toàn Diện Phase 15.3 (`test_phase15_3_qa_audit.py`):**
   - Xây dựng bộ test suite chuyên sâu 6 kịch bản kiểm tra: `/api/auth/me` F5 persistence, DELETE/POST leave class, Mastery Rubric với `NEEDS_MORE_STARS`, DAG tree consistency, và Autonomy Score 4D. Kết quả kiểm thử: **6/6 tests PASS 100%**.

#### 15.6.8. Tách Biệt Tường Minh 3 Hành Động (Chạy Thử / Hỏi Gia Sư AI / Nộp Bài) & Vá Triệt Để 6 Lỗi Giao Diện (Phase 15.4)
Nhằm giải quyết triệt để nhu cầu phân tách rõ ràng giữa việc *thử nghiệm*, *xin trợ giúp sư phạm* và *nộp bài chấm điểm*, hệ thống đã đại tu toàn diện luồng người dùng và đồng bộ hóa các trường dữ liệu:

1. **Tách biệt 3 Nút Hành Động Độc Lập Trên Toolbar IDE & API (`EditorPanel.jsx`, `StudentIDE.jsx`, `backend/schemas.py`, `backend/main.py`):**
   - **`▶ Chạy thử` (Ctrl + Enter - Màu Cyan):** Chạy kiểm tra nhanh trong MCP Sandbox, không tốn quota AI, không tính điểm nộp bài.
   - **`🤖 Hỏi Gia sư AI` (Màu Vàng Amber):** Gửi yêu cầu với `action_type = 'ask_ai'`. Backend thực thi MCP Sandbox + AST + Gemini Scaffolding sinh `tutor_hint` đúng theo mức gợi ý (1, 2, 3), ghi vết vào `submissions` nhưng **KHÔNG** tính hay lưu sao hoàn thành vào `user_exercise_stars` (`stars_earned = 0`, `new_badges = []`). Không mở modal chúc mừng để sinh viên yên tâm xem gợi ý tại Cột 3 và tiếp tục code.
   - **`🚀 Nộp bài` (Ctrl + Shift + Enter - Màu Xanh Emerald):** Gửi yêu cầu với `action_type = 'submit'`. Backend chấm điểm chính thức: nếu pass 100% test cases, hệ thống kiểm tra lịch sử các lần hỏi AI trước đó của sinh viên ở bài tập này để chấm đúng 1, 2 hoặc 3 Sao Tự Lực, lưu vào `user_exercise_stars`, mở khóa huy hiệu, bắn pháo hoa confetti và hiển thị Modal Chúc Mừng.
   - **Tích hợp Nút Nhận Gợi Ý Trực Tiếp tại Cột 3 (`TutorPanel.jsx`):** Bổ sung nút `🤖 Nhận gợi ý Mức ${hintLevel} từ Gia sư AI` ngay dưới 3 thẻ chọn mức gợi ý và gắn trực tiếp vào nút leo thang gợi ý (`Vẫn thấy khó? Xem gợi ý chi tiết hơn`).

2. **Vá 3 Lỗi Dữ Liệu Trên Dashboard Giảng Viên (`InstructorDashboard.jsx`):**
   - *Modal Chi tiết bài nộp:* Sửa lỗi trống code và sai thời gian bằng cách đọc fallback kép `sub.timestamp || sub.submitted_at` và `selectedSubmission.code || selectedSubmission.submitted_code`.
   - *Bảng Danh sách Sinh viên (Sub-tab 3):* Sửa lỗi `@undefined` và `0 bài, 0 ⭐` bằng cách đọc chuẩn xác `st.student_username || st.username`, `st.completed_exercises ?? st.solved_count ?? 0`, và `st.total_stars ?? st.stars_earned ?? 0`.
   - *Thông số Python (Sidebar Tab 4):* Đọc chính xác `health?.compiler_config?.python_version || health?.compiler_config?.version || '3.14.0'`.

3. **Vá 4 Lỗi Hiển Thị Trên Không Gian Chi Tiết Lớp Học Phần (`StudentClassDetailPage.jsx`):**
   - *Tiến độ Hero Banner & Tab 4:* Đọc các trường phẳng `currentClass.completed_in_class`, `currentClass.exercise_count`, và `currentClass.progress_percent`. Tổng sao lớp được tính trực tiếp từ ma trận bài tập: `curriculum.reduce((sum, item) => sum + (item.stars_earned || 0), 0)`.
   - *Cây Kỹ Năng DAG (Tab 3):* Sửa số lượng làm chủ thành `{skillRoadmap?.total_mastered ?? skillRoadmap?.mastered_count ?? 0}/{skillRoadmap?.total_exercises ?? skillRoadmap?.total_nodes ?? 0}` và mô tả trạng thái `{node.status_description || node.unlock_message}`.
   - *Bảng Vàng (Tab 4):* Sửa lỗi định danh bằng cách đọc `{row.full_name || row.username || row.session_id}` và `@{row.username || row.session_id}`.

4. **Sửa Đồng Bộ Phím Tắt, Banner Test & Custom Stdin (`EditorPanel.jsx`, `StudentIDE.jsx`, `StudentPortalPage.jsx`):**
   - Sửa key đếm test trong banner chúc mừng `EditorPanel.jsx`: `{testResults.passed_tests}/{testResults.total_tests}`.
   - Sửa prop `defaultStdin` truyền vào `ExecutionVisualizerModal`: `exerciseDetail?.test_cases?.[0]?.input || ''`.
   - Chuẩn hóa fallback `autonomyScore` trên Cổng Sinh viên: `profile?.analytics_metrics?.autonomy_score ?? 85`.

5. **Bộ Kiểm Thử Tự Động Toàn Diện (`test_phase15_4_action_buttons.py`):**
   - Xác nhận 100% các kịch bản: `action_type = 'ask_ai'` không cấp sao; `action_type = 'submit'` tính đúng số sao tự lực dựa trên lịch sử gợi ý trước đó; thông số trình thông dịch Python và danh sách sinh viên lớp học phần hoạt động chuẩn xác. Kết quả: **4/4 tests PASS 100%**.

#### 15.6.9. Tạm Ẩn Phân Hệ "Thực Hành & Kỳ Thi" & Cải Tiến Giao Diện Vinh Danh Sinh Viên K65 (Phase 15.5)
Nhằm đáp ứng yêu cầu người dùng về việc tinh giản giao diện, tập trung cao độ vào việc tự học và làm bài tập học phần, hệ thống đã tạm ẩn phân hệ kỳ thi theo cơ chế cờ đảo chiều tức thì:

1. **Kiến Trúc Cờ Điều Khiển (One-Click Reversible Flag):**
   - Trong [`StudentClassDetailPage.jsx`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/frontend/src/pages/StudentClassDetailPage.jsx):
     - Khai báo flag: `const SHOW_EXAM_SESSIONS = false; // Đặt true khi cần hiển thị lại`.
     - Ẩn Tab 2 ("Thực Hành & Kỳ Thi") và khối nội dung danh sách ca thi tương ứng (`activeTab === 'sessions'`).
     - Tự động đánh số lại các Tab còn lại:
       - **Tab 1:** `1. Chương Trình & Bài Tập`
       - **Tab 2:** `2. Cây Kỹ Năng & Chuẩn Sao`
       - **Tab 3:** `3. Bảng Vàng & Đánh Giá Năng Lực`
   - Trong [`StudentPortalPage.jsx`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/frontend/src/pages/StudentPortalPage.jsx):
     - Khai báo flag: `const SHOW_EXAM_SESSIONS = false;`.
     - Chuyển đổi Cột 3 thành **"Vinh Danh & Năng Lực"** (Icon Trophy, Badge `SV K65 CNTT`).
     - Khi `!SHOW_EXAM_SESSIONS`: Ẩn danh sách ca thi, hiển thị thẻ **"Thành Tích Học Phần"** (Tổng sao tự lực `totalStars`, Số bài hoàn thành `totalSolved`, Chỉ số tự lực `autonomyScore`), đi kèm danh sách huy hiệu và 2 nút mở nhanh **Bảng Vàng K65** và **Hồ Sơ 4D**. Bố cục 3 cột giữ nguyên độ cân xứng, không có khoảng trống thừa.
2. **Bảo Toàn Tuyệt Đối Backend & Khôi Phục Dễ Dàng:**
   - Toàn bộ bảng `exam_sessions`, các route `/api/exam-sessions`, logic EXAM Mode Guard trong Backend vẫn được giữ nguyên vẹn 100%.
   - Khi cần khôi phục lại tính năng, chỉ cần sửa `SHOW_EXAM_SESSIONS = true` trong 2 file trên là giao diện kỳ thi sẽ lập tức hiển thị trở lại.

#### 15.6.10. Đợt Rà Soát Cuối Cùng Trước Khi Chuyển Giao (Final Turnkey Release Checkpoint)
Trước khi người dùng hoàn tất nghiệm thu và chuyển giao đồ án, toàn bộ hệ sinh thái dự án đã được rà soát và kiểm chứng đạt chuẩn cao nhất:

1. **Chuẩn Hóa Thông Tin Định Danh Học Thuật:**
   - **Sinh viên:** `Trần Minh Khánh - SV K65 CNTT (MSV: 11236131)` (Tài khoản: `student` / Mật khẩu: `student123`).
   - **Đơn vị:** Khoa Công nghệ thông tin — Trường Đại học Kinh tế Quốc dân (NEU).
   - **Giảng viên hướng dẫn:** Thầy **Nguyễn Văn A** (`gv_tran`) và Thầy **Trần Văn B** (`gv_tuan`).
   - **Danh mục Môn học Tín chỉ:** 24 lớp học phần định dạng chuẩn LMS NEU được lưu trong SQLite `pytutor.db`.
2. **Kịch Bản Khởi Chạy Tự Động & Hỗ Trợ Đa Nền Tảng:**
   - `start_dev.bat`: Đã nâng cấp thuật toán tự dò tìm Python trong `venv`, `.venv` hoặc Python toàn cục. Khởi chạy song song Backend + Frontend chỉ với 1 cú click đúp chuột trên Windows.
   - `start_dev.sh`: Tạo kịch bản khởi chạy đồng bộ cho Linux và macOS.
   - `.env.example`: Cung cấp file mẫu biến môi trường với chú thích chi tiết cho Google Gemini API, Qwen và cơ chế Offline Fallback.
3. **Báo Cáo Thực Nghiệm Khoa Học Tự Động:**
   - `evaluate_its_benchmark.py`: Cập nhật tự động kiểm thử đủ **8 Công cụ MCP**, 5 kịch bản Sandbox và 3 cấp độ Scaffolding.
   - `docs/EVALUATION_REPORT.md`: Tự động xuất báo cáo thực nghiệm độc lập đầy đủ số liệu phục vụ in phụ lục đồ án tốt nghiệp.
4. **Kết Quả Kiểm Thử Toàn Diện (Regression Test Results):**
   - `npm.cmd run build`: **0 errors** (1,686 modules, build trong 1.98s).
   - `test_phase15_4_action_buttons.py`: **4/4 PASS**.
   - `test_phase15_3_qa_audit.py`: **6/6 PASS**.
   - `test_phase13_14_neu_lms.py`: **8/8 PASS**.
   - `test_phase12_classroom_exam.py`: **7/7 PASS**.
   - `evaluate_its_benchmark.py`: **4/4 Benchmarks PASS 100%**.

#### 15.6.11. Vá Lỗi Phím Space Bar Trong Editor & Đại Tu Phân Hóa 3 Cấp Độ Gợi Ý Sư Phạm (Phase 15.6 Hotfix)
1. **Khắc Phục Triệt Để Lỗi Không Gõ Được Phím Space Bar (Dấu Cách) Trong Monaco Editor (`EditorPanel.jsx`):**
   - *Hiện trạng:* Do cơ chế bắt phím của trình duyệt, các listener của container hoặc các bộ gõ tiếng Việt (UniKey, EVKey, Windows IME), sự kiện phím Space đôi khi bị nuốt hoặc bubbling ra ngoài khiến Monaco Editor không nhận diện được dấu cách.
   - *Khắc phục:*
     - Chặn sự kiện bubbling ra ngoài: `editor.onKeyDown((e) => { if (e.keyCode === monaco.KeyCode.Space || e.browserEvent?.key === ' ' || e.browserEvent?.code === 'Space') e.stopPropagation(); })`.
     - Đăng ký lệnh cưỡng chế chèn ký tự khoảng trắng: `editor.addCommand(monaco.KeyCode.Space, () => editor.trigger('keyboard', 'type', { text: ' ' }))` và `editor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.Space, ...)`.
     - Cấu hình Monaco Options: `acceptSuggestionOnCommitCharacter: false` và `quickSuggestions: { other: true, comments: false, strings: false }` ngăn chặn popup autocomplete nuốt phím cách.
2. **Đại Tu Độ Phân Hóa & Tính Tương Phản 3 Cấp Độ Gợi Ý Sư Phạm (`backend/llm_service.py` & `TutorPanel.jsx`):**
   - *Hiện trạng:* 3 mức gợi ý trước đây bị phản hồi là quá giống nhau do prompt chung chung và bộ sinh fallback chưa phân tầng rõ rệt.
   - *Khắc phục:* Thiết kế lại cấu trúc 3 Mức với sự khác biệt 180 độ:
     - **Mức 1 (💡 Gợi Mở Tư Duy - 3⭐):** Pure Socratic Concept. Đánh giá hướng đi tổng quan, đặt 2 câu hỏi gợi mở tư duy sâu sắc, chỉ ra từ khóa/khái niệm Python cần ôn lại. Tuyệt đối không trích dẫn dòng code hay đưa cách sửa.
     - **Mức 2 (🔍 Chẩn Đoán Dòng Lỗi - 2⭐):** Root Cause Localization. Trích dẫn chính xác dòng code hoặc biểu thức của học viên bị sai. Mổ xẻ chi tiết Test Case bị FAIL (`Input`, `Actual Output` từ code của bạn, `Expected Output` đề bài yêu cầu, giải thích tại sao máy tính ra kết quả đó). Chỉ rõ cách sửa logic bằng lời.
     - **Mức 3 (📘 Dàn Ý & Khung Code Mẫu - 1⭐):** Algorithm & Scaffolded Code Skeleton. Cung cấp quy trình giải thuật 4 bước rõ ràng VÀ một khung mã nguồn Python (Code Skeleton) chuẩn chỉnh có chừa các chỗ trống `...` hoặc `# TODO` để sinh viên nhìn vào hiểu ngay cách tổ chức code và tự hoàn thành phần cốt lõi!

---

## 🎯 KẾT LUẬN & LỜI DẶN DÒ DÀNH CHO AGENT TIẾP QUẢN
Hệ thống **PyTutor-MCP** là một công trình đồ án tốt nghiệp được thiết kế với chất lượng mã nguồn cao cấp (Production-grade), tuân thủ nghiêm ngặt các nguyên tắc kiến trúc phần mềm, bảo mật cô lập tiến trình và phương pháp sư phạm hiện đại.  
Khi tiếp quản dự án từ phiên bản **v5.0 Pro (NEU Multi-Stage LMS & IDE Architecture - Final Turnkey Release)**, bạn hãy tự tin phát triển tiếp các tính năng mới theo yêu cầu của người dùng, luôn giữ vững tính ổn định, quy tắc zero-question và sự chuẩn mực của giao thức Model Context Protocol!


