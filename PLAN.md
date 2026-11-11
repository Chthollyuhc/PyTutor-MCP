# 📋 PYTUTOR-MCP: MASTER IMPLEMENTATION DASHBOARD

> **Tên đề tài đề xuất:** Xây dựng hệ thống hỗ trợ học lập trình Python với phản hồi thích ứng và phân tích tiến độ học tập
>
> **Sản phẩm:** PyTutor-MCP — nền tảng thực hành Python; MCP đảm nhiệm tích hợp công cụ trong kiến trúc.
> **Sinh viên thực hiện:** Trần Khánh  
> **Repository:** [https://github.com/Chthollyuhc/PyTutor-MCP](https://github.com/Chthollyuhc/PyTutor-MCP)  
> **Định hướng phát triển:** **Continuous Evolution (Phase 1 -> Phase 17)** | **Phiên bản hiện tại:** `v5.2 (Adaptive Feedback & Learning Analytics MVP)`

---

## 🏛️ TỔNG QUAN KIẾN TRÚC HỆ THỐNG

```text
[Sinh viên / Giảng viên]
    │ Giao diện React 18 + Vite + Tailwind + Monaco Editor + React Router v6
    │ ├── /login : Cổng Đăng nhập NEU Split-Screen & 1-Click Demo cho Hội đồng Chấm
    │ ├── /student : Cổng Sinh viên NEU (4 KPIs Tổng quan, Lưới Lớp học phần, Ghi danh bằng Mã, Phòng Luyện tập Tự do)
    │ ├── /student/classes/:classId : Không gian Chi tiết Lớp học phần (4 Tabs: Curriculum & Thang đo Sao, Thực hành & Kỳ thi, Cây kỹ năng DAG, Bảng vàng & Năng lực 4D)
    │ ├── /student/ide/:exerciseId : Môi trường Lập trình IDE Chuyên sâu 3 Cột (ProblemPanel | EditorPanel | TutorPanel)
    │ │            + Nút nổi bật: ⬅️ Quay lại Lớp học phần
    │ │            + Dropdown chuyển nhanh bài tập trong lớp mà không cần rời IDE
    │ │            + Banner đếm ngược thời gian thi nếu là Chế độ EXAM (Khóa Gia sư AI)
    │ │            + Chạy từng bước (Visualizer), Custom Stdin, Auto-save nháp, 3 Sao Tự lực, Thử thách Pythonic
    │ └── /instructor (và /instructor/classes/:classId) : Sidebar Workspace Giảng viên NEU
    │              + 1. Quản lý Lớp học phần NEU: Lưới lớp, Mở lớp mới, Không gian Quản trị Lớp (Lộ trình & Inline Edit Sao, Kỳ thi, Danh sách SV)
    │              + 2. Ngân hàng Bài tập: Quản lý ngân hàng đề, Thêm/Sửa/Xóa, Bộ test cases
    │              + 3. Giám sát Bài nộp & AI: Bảng theo dõi lượt nộp toàn trường, Xem code & gợi ý AI, Xuất CSV UTF-8
    │              + 4. Hạ tầng MCP & Trình biên dịch: Thông số sys.executable, Python 3.14, timeout 5s, 8 MCP Tools
    ▼
[Backend: FastAPI (MCP Host, Auth JWT & Pedagogical Orchestrator)]
    ├──► (1) Giao thức MCP (JSON-RPC 2.0 qua stdio) ──► [mcp_server: 8 Tools]
    │        ├── run_test_cases (Sandbox, timeout 5s)
    │        ├── analyze_code_ast (AST static analysis)
    │        ├── get_exercise_list & get_exercise_details (SQLite Database)
    │        ├── save_learning_event (Ghi nhận lịch sử nộp bài)
    │        ├── get_attempt_history (Lấy tiến trình làm lại của sinh viên)
    │        ├── get_student_model (Mô hình học sinh thích ứng thời gian thực)
    │        └── trace_code_execution (Tracer từng bước biến số, luồng I/O, max 150 bước / 3s)
    ├──► (2) Cơ sở dữ liệu SQLite: `pytutor.db` (WAL Mode: exercises, submissions, users, credit_classes, exam_sessions)
    ├──► (3) Ghi nhận MCP Trace đo đạc độ trễ từng bước Handshake & Call tool
    ├──► (4) Google Gemini 3.5 Flash Lite (Scaffolding Pedagogy 3 Levels + Anti-Spoil Guard + Pythonic Review)
    ├──► (5) Gamification Engine (Đánh giá 1-3 Sao Tự lực, Mở khóa 5 Huy hiệu, Bảng xếp hạng Lớp học)
    └──► (6) Academic Management Engine (Lớp tín chỉ, Đợt thi/Thực hành, EXAM Mode Guard)
```

---

## 🗺️ BẢNG ĐIỀU KHIỂN TIẾN ĐỘ MODULAR (MASTER INDEX)

| Phase | Phân hệ | Mục tiêu chính | Trạng thái | Chi tiết kế hoạch |
| :--- | :--- | :--- | :---: | :--- |
| **Phase 1** | `mcp_server/` | MCP Server, Sandbox (timeout 5s), AST Analyzer, 5 bài tập mẫu | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 2** | `backend/` | MCP Client & Host Orchestrator, True Discovery (`tools/list`), Schemas, Gemini AI | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 3** | `frontend/` | Setup Vite + React 18 + Tailwind, Layout 3 cột, Monaco Editor, Tutor Panel | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 4** | `release/` | Tích hợp toàn hệ thống, script chạy 1-click (`start_dev`), hoàn thiện README | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 5** | `fullstack/` | Phân quyền JWT, Dashboard Giảng viên CRUD bài tập, SQLite, 7 MCP Tools, Adaptive AI | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 6** | `evaluation/`| MCP Protocol Inspector UI, Student Profile Modal, Submission Detail & CSV Export, Báo cáo Thực nghiệm Khoa học | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 7** | `frontend/` | Thu gọn Header MCP Pill, Thân thiện hóa ngôn ngữ giao diện, Auto-save nháp, Phím tắt | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 8** | `fullstack/` | Trò chuyện Tương tác Đa lượt (Multi-turn Chat) & Tô đỏ Dòng Lỗi Monaco (Error Decoration) | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 9** | `mcp & ui/` | MCP Tool thứ 8 `trace_code_execution`, Thanh trượt xem biến từng bước, Cây kỹ năng | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 10**| `gamify/` | Đánh giá 3 Sao Tự lực, Huy hiệu, Thử thách Tối ưu Code Pythonic & Leaderboard | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 11**| `mcp & docs/` | Trình diễn Giá trị Cốt lõi MCP, Multi-Host Configs, Tài liệu Bảo vệ Đồ án | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 12**| `academic` | Quản lý Lớp tín chỉ, Kỳ thi / Thực hành (Exam vs Practice Mode) & Minh bạch Cấu hình Trình biên dịch | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 13 & 14**| `neu_lms & its` | Chuẩn hóa LMS Học phần NEU (Khoa CNTT), Đa lớp học phần, Lộ trình Kỹ năng & Thang đo Định lượng (Mastery Rubric), Động cơ Phân tích 4D & 3 Thẻ Chẩn đoán Sư phạm | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 15**| `multi-stage` | Phân tách Cổng Lớp học phần (`/student`, `/student/classes/:id`) với IDE 3 cột (`/student/ide/:id`), Split-screen Login NEU, Sidebar Workspace Giảng viên (`/instructor`) | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md) |
| **Phase 15.1**| `neu-catalog & fix` | Đại tu 24 môn CNTT chuẩn LMS NEU, đổi tên GV Nguyễn Văn A & Trần Văn B, Fix Black Screen Tab 4 Analytics, Bộ lọc & Grid/List View | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md#156-đại-tu-danh-mục-học-phần-neu-24-môn-cntt-từ-lms-neu-chuẩn-hóa-giảng-viên--cải-tiến-giao-diện) |
| **Phase 15.2**| `submit-flow & sync` | Phân tách nút [▶ Chạy thử] vs [🚀 Nộp bài], Modal chúc mừng & Banner nhắc nộp bài, Đồng bộ định danh sinh viên student (Trần Minh Khánh - 11236131), Sửa key exercise_stars Backend, Curriculum dynamic status theo Mastery Rubric, Khắc phục % tiến độ lớp học phần, Đại tu Cột 3 thành Trung tâm Lịch thi & Thực hành tín chỉ | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md#1566-chuẩn-hóa-luồng-nộp-bài-submit-flow-đồng-bộ-định-danh-sinh-viên-k65--trung-tâm-lịch-thi-tín-chỉ-phase-152) |
| **Phase 15.3**| `qa-audit & integrity` | Sửa NameError get_db_connection tại /api/auth/me (chặn logout khi F5), đảo thứ tự param fetchSkillRoadmap & fetchStudentProfile, chuẩn hóa Mastery Rubric & nhánh NEEDS_MORE_STARS, sửa hiển thị Điểm Tự lực 4D & tổng sao lớp, hỗ trợ POST/DELETE rời lớp | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md#1567-khắc-phục-triệt-để-5-lỗi-nghiêm-trọng-từ-đợt-rà-soát-mã-nguồn-qa-audit-hotfix--data-integrity-phase-153) |
| **Phase 15.4**| `3-buttons & ui-audit` | Tách biệt tường minh 3 nút (Chạy thử / Hỏi Gia sư AI / Nộp bài), truyền action_type ('ask_ai' vs 'submit'), tính sao tự lực theo lịch sử gợi ý, sửa 6 lỗi lệch key giao diện (Instructor roster, submission modal, Python specs, Hero progress, DAG counts & descriptions, Leaderboard names) | ✅ **PASSED** | [Xem chi tiết](AI_HANDOFF_CONTEXT.md#1568-tách-biệt-tường-minh-3-hành-động-chạy-thử--hỏi-gia-sư-ai--nộp-bài--vá-triệt-để-6-lỗi-giao-diện-phase-154) |
| **Phase 16** | `ai-tutor-upgrade` | Prompt persona, RAG cục bộ TF-IDF/SQLite, role chat giảng viên, guardrails, telemetry & feedback | 🟡 **MVP IMPLEMENTED** | [Kế hoạch & trạng thái](plans/PLAN_16_AI_UPGRADE.md) |
| **Phase 17** | `adaptive-feedback & analytics` | Chọn chiến lược gợi ý theo test fail/lịch sử/pass; chỉ số tiến độ có định nghĩa, sample status, kiểm thử replay và pilot so sánh | 🟡 **TECHNICAL MVP COMPLETE; USER PILOT PENDING** | [Chỉ số, benchmark, protocol & nghiên cứu](docs/PHASE_17_METRICS_AND_BENCHMARK.md) |

---

## 📊 NHẬT KÝ THỰC THI (EXECUTION LOG)

| Thời gian | Hạng mục | Kết quả | Ghi chú |
| :--- | :--- | :---: | :--- |
| 14/10/2026 | Phase 1.0: MCP Server Core | ✅ 100% PASS | 8/8 test cases đạt chuẩn (AST, Sandbox, Handshake, Discovery) |
| 14/10/2026 | Phase 2.1 - 2.3: Backend E2E | ✅ 100% PASS | True Discovery, Scaffolding Prompt, Gemini AI, E2E Tests |
| 14/10/2026 | Phase 3.1 - 3.2: Frontend IDE | ✅ PASSED | React 18, Monaco Editor, Tutor Panel, Confetti |
| 14/10/2026 | Phase 4.0: Release & Scripts | ✅ 100% READY | `start_dev.bat`, `start_dev.ps1`, `README.md` |
| 14/10/2026 | Phase 5.1: Quick Fixes UI | ✅ PASSED | Sửa badge Gemini AI, thêm Hint Escalation, render Markdown h1-h3/list |
| 14/10/2026 | Phase 5.2: Auth & Instructor CRUD | ✅ PASSED | JWT Auth, tài khoản sinh viên/giảng viên, Dashboard CRUD ngân hàng đề |
| 14/10/2026 | Phase 5.3: Run vs Submit Separation | ✅ PASSED | Route `/api/run-test` chạy Sandbox không tốn quota AI |
| 14/10/2026 | Phase 5.4: Learning Events via MCP | ✅ PASSED | MCP Tool `save_learning_event`, `get_attempt_history` |
| 14/10/2026 | Phase 5.5: Adaptive Student Model | ✅ PASSED | MCP Tool `get_student_model` tích hợp vào Scaffolding Prompt |
| 14/10/2026 | Phase 6.1: MCP Protocol Inspector | ✅ PASSED | Modal hiển thị 7 Tools và nhật ký thực thi `mcp_trace` thời gian thực |
| 14/10/2026 | Phase 6.2: Student Adaptive Profile| ✅ PASSED | Modal thống kê năng lực ITS và khôi phục code các lần nộp cũ |
| 14/10/2026 | Phase 6.3: Instructor Inspector & CSV | ✅ PASSED | Xem chi tiết code nộp + Tutor hint, Xuất file CSV UTF-8 BOM cho Excel |
| 14/10/2026 | Phase 6.4: Academic Benchmark Report| ✅ PASSED | `evaluate_its_benchmark.py` sinh `docs/EVALUATION_REPORT.md` (4 Benchmarks) |
| 15/10/2026 | Phase 7.1: Header Compact MCP Pill | ✅ PASSED | Thu gọn dòng MCP dài thành 1 nút nhỏ `⚡ Kết nối MCP (7)` click mở modal |
| 15/10/2026 | Phase 7.2: Thân thiện hóa Ngôn ngữ UI | ✅ PASSED | Xóa thuật ngữ nặng nề, 3 mức gợi ý gần gũi, thẻ AST thu gọn/mở rộng |
| 15/10/2026 | Phase 7.3: Auto-save & Phím tắt | ✅ PASSED | `localStorage` nháp per-exercise, phím tắt `Ctrl+Enter` và `Ctrl+Shift+Enter` |
| 15/10/2026 | Phase 8.1: Multi-turn Follow-up Chat | ✅ 100% PASS | Trò chuyện 2 chiều với Gia sư AI qua Gemini 3.5 Flash Lite, Anti-Spoil Guard |
| 15/10/2026 | Phase 8.2: Monaco Error Decoration | ✅ PASSED | Tô đỏ dải màu dòng lỗi cú pháp/runtime trong Monaco, hover tooltip, tự xóa khi gõ |
| 15/10/2026 | Phase 8.3: Custom Input Playground | ✅ 100% PASS | Tab tự nhập Stdin tùy ý chạy qua MCP Sandbox, bảo vệ Timeout 5.0s |
| 15/10/2026 | Phase 9.1: MCP Tool 8 `trace_code_execution` | ✅ 100% PASS | `sys.settrace` sandbox, snapshot biến số, giới hạn an toàn 150 bước / 3s |
| 15/10/2026 | Phase 9.2: Execution Visualizer UI | ✅ PASSED | Modal thanh trượt bước chạy, highlight biến mới đổi, active line, auto-play |
| 15/10/2026 | Phase 9.3: Skill Roadmap DAG Tree | ✅ 100% PASS | Modal bản đồ kỹ năng phân tầng, trạng thái thích ứng Mastered/In-Progress/Locked |
| 15/10/2026 | Phase 10.1: Autonomy Stars Rating | ✅ 100% PASS | Thuật toán chấm 1-3 ⭐ tự lực dựa theo mức gợi ý sư phạm đã dùng |
| 15/10/2026 | Phase 10.2: Achievement Badges System | ✅ 100% PASS | Mở khóa tự động 5 huy hiệu vinh danh học tập trong SQLite `pytutor.db` |
| 15/10/2026 | Phase 10.3: Senior Pythonic Code Review | ✅ 100% PASS | Prompt Gemini Tech Lead đánh giá Clean Code score, diff so sánh code chuẩn |
| 10/10/2026 | Phase 10.4: Classroom Leaderboard | ✅ 100% PASS | Bảng vàng vinh danh top học sinh theo sao, bài giải và điểm code sạch |
| 10/10/2026 | Phase 10.5: Gamification & Review UI | ✅ PASSED | `PythonicReviewModal`, `LeaderboardModal`, Header `🏆 Bảng vàng`, Tutor Stars |
| 16/10/2026 | Post-Audit Fixes (Bugs 1-4) | ✅ 100% PASS | Đồng bộ 8 MCP tools vào Inspector, Header v3.4 Pro, Markdown table flush, SQLite WAL |
| 16/10/2026 | Phase 11: MCP Defense Showcase | ✅ 100% PASS | Modal 3 Tab Showcase (8 Tools, Đối chiếu kiến trúc, Cắm đa nền tảng), WHY_MCP_EXPLAINED |
| 20/10/2026 | Phase 12: Classroom & Exam Mode | ✅ 100% PASS | Lớp tín chỉ, Kỳ thi/Thực hành (EXAM vs PRACTICE), EXAM Mode Guard, Compiler Specs |
| 20/10/2026 | Phase 13 & 14: NEU LMS & 4D Analytics | ✅ 100% PASS | Chuẩn hóa Khoa CNTT - NEU, Cổng Lớp học phần, Curriculum Matrix, Mastery Rubric, Động cơ Phân tích 4D (8/8 tests PASS) |
| 20/10/2026 | Phase 15: Multi-Stage LMS & IDE Architecture | ✅ 100% PASS | Phân tách Cổng Lớp học phần (`/student`, `/student/classes/:id`) với IDE 3 cột (`/student/ide/:id`), Split-screen Login NEU, Sidebar Workspace Giảng viên (`/instructor`) |
| 20/10/2026 | Phase 15.1: NEU LMS Catalog & Ergonomics | ✅ 100% PASS | Nạp 24 môn CNTT chính thức LMS NEU, Đổi GV Nguyễn Văn A & Trần Văn B, Fix Black Screen Tab 4, Bộ lọc tìm kiếm Lớp & Bài tập, Grid/List view toggle, Tinh gọn giao diện IDE |
| 20/10/2026 | Phase 15.2: Submit Flow & Student Data Sync | ✅ 100% PASS | Phân tách tường minh [▶ Chạy thử] vs [🚀 Nộp bài], Gợi ý nộp bài tự động khi pass 100% tests, Đồng bộ định danh sinh viên K65 Trần Minh Khánh (11236131), Sửa key exercise_stars Backend, Khắc phục % tiến độ lớp học phần, Thay Cột 3 bằng Trung tâm Lịch thi & Thực hành tín chỉ |
| 20/10/2026 | Phase 15.3: QA Audit Hotfix & Data Integrity | ✅ 100% PASS | Sửa NameError `get_db_connection` (chống auto-logout khi F5), sửa thứ tự tham số API `fetchSkillRoadmap` & `fetchStudentProfile`, sửa dead code Mastery Rubric (`NEEDS_MORE_STARS` & tiên quyết), sửa hiển thị Chỉ số tự lực & Tổng sao lớp, hỗ trợ POST/DELETE `/api/classes/{id}/leave` |
| 20/10/2026 | Phase 15.4: 3-Button Action Separation & UI Audit Part 2 | ✅ 100% PASS | Tách biệt tường minh 3 nút `▶ Chạy thử`, `🤖 Hỏi Gia sư AI` (action_type='ask_ai') và `🚀 Nộp bài` (action_type='submit'), tính sao tự lực dựa trên lịch sử gợi ý, cập nhật nút nhận gợi ý trực tiếp trong TutorPanel, sửa 6 lỗi lệch key giao diện (Instructor roster, Modal bài nộp, Python version, Hero progress, DAG counts & descriptions, Leaderboard names) |
| 20/10/2026 | Phase 15.5: Exam Mode Toggle & Honor Center | ✅ 100% PASS | Tạm ẩn phân hệ 'Thực hành & Kỳ thi' qua cờ `SHOW_EXAM_SESSIONS = false`, đánh số lại các Tab lớp học, đại tu Cột 3 Cổng sinh viên thành Trung tâm Vinh danh & Năng lực học viên K65 |
| 20/10/2026 | Final Turnkey Release & Handover Checkpoint | ✅ 100% PASS | Chuẩn hóa định danh sinh viên K65 Trần Minh Khánh (11236131), Giảng viên Nguyễn Văn A & Trần Văn B, kịch bản start_dev.bat (tự dò Python) & start_dev.sh, .env.example, benchmark 8 tools evaluate_its_benchmark.py, 100% tests PASS |
| 20/10/2026 | Phase 15.6: Editor Space Key & 3-Tier AI Overhaul | ✅ 100% PASS | Khắc phục triệt để lỗi không gõ được phím Space bar trong Monaco Editor (chặn bubbling, ép chèn type command, cấu hình autocomplete), Đại tu 3 mức gợi ý AI Socratic phân hóa 180 độ (Mức 1: Câu hỏi tư duy; Mức 2: Chỉ chính xác dòng lỗi & phân tích test fail; Mức 3: Dàn ý 4 bước + Khung code mẫu điền chỗ trống `# TODO`) |
| 02/11/2026 | Phase 16: AI Tutor Upgrade MVP | 🟡 CORE IMPLEMENTED | Dynamic Jinja prompts, sparse TF-IDF RAG local SQLite, authenticated student/instructor chat, input/output guards, LLM telemetry/feedback, deterministic Anti-Spoil corpus; awaiting authorized NEU coursebook and broader evaluator/rollout before marking complete |
| 03/11/2026 | Phase 17: Adaptive Feedback & Learning Progress Analytics | 🟡 TECHNICAL MVP COMPLETE; USER PILOT PENDING | Metric contract separates official submit from ask_ai, sparse-data status, deterministic hint strategy, six-case offline replay (6/6 policy expectations; requested level preserved), research-informed 2–3 participant protocol. Automated Phase 17 tests 5/5 PASS; no user learning gain claimed. |

---

## 🧭 PHASE 16–17: TRẠNG THÁI CHI TIẾT & TIÊU CHÍ HOÀN TẤT

### Phase 16 — Nâng cấp động cơ Gia sư AI (MVP)

**Mục tiêu:** chuyển từ prompt ghép chuỗi và câu trả lời phụ thuộc kiến thức nội tại sang đường ống có prompt theo persona, truy xuất tri thức nội bộ, ranh giới role, guardrails và telemetry.

**Phạm vi hiện có:**
- Prompt Jinja2 tách persona Socratic, Pythonic Reviewer và Instructor Analytics; nhận dữ liệu hồ sơ học tập trong đúng luồng quyền.
- RAG cục bộ SQLite + TF-IDF/sparse cosine; nguồn hiện có là tài liệu Python nội bộ trong `docs/knowledge_base/`, chưa được xem là giáo trình chính thức NEU.
- Chat sinh viên xác thực role; EXAM guard được giữ trước khi gọi LLM. Chat giảng viên giới hạn lớp sở hữu và dùng dữ liệu tổng hợp.
- Input/output guard chống injection/off-topic và giảm lộ đáp án; telemetry ghi model, latency, token nếu provider cung cấp, trạng thái guard; phản hồi chat có interaction ID và feedback.
- Pythonic review/hint có telemetry; feedback UI hiện tập trung vào bong bóng chat.

**Tệp chính:** `plans/PLAN_16_AI_UPGRADE.md`, `backend/prompt_templates.py`, `backend/rag/`, `backend/guardrails.py`, `backend/llm_service.py`, `backend/main.py`, `backend/database.py`, `backend/schemas.py`, `frontend/src/components/TutorPanel.jsx`, `test_phase16_ai_upgrade.py`.

**Kiểm thử/trạng thái:** ghi nhận trước đây Phase 16 test 6/6 PASS, backend compile và frontend build PASS. Chỉ đánh dấu hoàn tất sau khi chạy lại suite đầy đủ, hoàn thiện đo false-positive/latency và xác nhận nội dung RAG được phép dùng. Nạp tài liệu NEU là tùy chọn phụ thuộc người dùng cung cấp/cấp quyền; không bịa hoặc tuyên bố đã tích hợp nguồn chưa có.

### Phase 17 — Phản hồi thích ứng & Phân tích tiến độ học tập (Technical MVP)

**Mục tiêu:** làm rõ hai năng lực nổi bật của đề tài: (1) điều chỉnh chiến lược phản hồi theo bằng chứng trong bài hiện tại/lịch sử, (2) tổng hợp tiến độ đủ minh bạch để người học và giảng viên không diễn giải quá mức.

**Luồng phản hồi:** `test result + attempt history + student model → select_hint_strategy → prompt strategy + evidence → tutor response`. Chiến lược gồm `conceptual_start`, `failed_case_diagnosis`, `recurring_difficulty`, `solution_review`. Gợi ý bắt đầu nhỏ; lỗi lặp lại chuyển sang chẩn đoán cụ thể dựa trên test/lịch sử; khi pass thì chuyển sang review/củng cố và giảm scaffolding. Không tự nâng mức tiết lộ vượt `hint_level` người học yêu cầu. `ask_ai` vẫn hữu ích cho lịch sử hướng dẫn nhưng không được tính như bài nộp chính thức.

**Hợp đồng chỉ số:**
- Chỉ `action_type=submit` tính vào số lượt nộp, tỉ lệ pass, tự lực và tổng hợp lớp; `ask_ai` loại khỏi các metric chính thức.
- Báo cáo `total_submissions`, số bài khác nhau, first-try pass rate, submissions/bài, mức hint tối đa trung bình, autonomy score hiện hữu, error breakdown và topic mastery.
- Gắn `data_status`: `no_data` nếu chưa nộp; `limited` nếu dưới 3 bài khác nhau; `sufficient` từ 3 bài. Ngưỡng 3 là heuristic vận hành, không phải cutoff đã kiểm chứng giáo dục.
- Tỷ lệ xin hint không tự nó chứng minh năng lực thấp. Chỉ số tự lực hiện tại kế thừa công thức sản phẩm; cần xác thực ngoài trước mọi diễn giải năng lực mạnh.
- Chat phân tích lớp nêu khoảng thời gian, số lượng mẫu và trường hợp no-data; không gửi mã/định danh sinh viên cá nhân trong phản hồi tổng hợp.

**Tệp chính:** `backend/adaptive_policy.py`, `backend/database.py`, `backend/main.py`, `backend/llm_service.py`, `backend/prompt_templates.py`, `backend/schemas.py`, `test_phase17_adaptive_analytics.py`, `evaluate_phase17_adaptive.py`, `docs/PHASE_17_METRICS_AND_BENCHMARK.md`.

**Bằng chứng kỹ thuật hiện có:** test Phase 17 5/5 PASS; offline replay 6/6 chiến lược khớp expected, 6/6 giữ nguyên mức hint yêu cầu, baseline cố định khớp 2/6. Đây chỉ là bộ replay tổng hợp do dự án định nghĩa, không phải đánh giá chất lượng người dùng hoặc tác động học tập.

**Phương pháp đánh giá đã thống nhất với người dùng:** 2–3 người tình nguyện gồm cả sinh viên và giảng viên; hồ sơ/lỗi lập trình giả lập; cùng kịch bản chạy baseline và adaptive, reset code/history giữa điều kiện và luân phiên thứ tự; rubric đánh giá grounding, specificity, next step, agency, anti-spoil, clarity; khảo sát ngắn sau mỗi ca; giảng viên diễn giải snapshot lớp và nêu giới hạn kết luận. Dùng dữ liệu tối thiểu, xin đồng ý nếu dùng tài khoản người tham gia, ẩn danh ghi chú, không thu mật khẩu.

**Cơ sở thiết kế:** feedback hướng vào goal/current evidence/next step, task/process/self-regulation; khuyến khích người học tự đánh giá và sử dụng feedback; xem accuracy và hint use là hai dạng bằng chứng khác nhau. Xem tài liệu nguồn trong `docs/PHASE_17_METRICS_AND_BENCHMARK.md`. Các nghiên cứu khác môn học chỉ là cơ sở tham khảo, không được ngoại suy thành hiệu quả PyTutor.

**Definition of Done:** kỹ thuật được xem là MVP hoàn tất khi test/replay/build đạt và metric definitions rõ. Đợt pilot chỉ hoàn tất sau khi thực sự tổ chức buổi dùng thử, ghi kết quả ẩn danh, xử lý lỗi answer leakage/unsupported claims/interpretation confusion và cập nhật báo cáo. Với 2–3 người chỉ báo cáo mô tả, không tuyên bố ý nghĩa thống kê hay learning gain/causality.




