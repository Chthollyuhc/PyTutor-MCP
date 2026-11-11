# CLAUDE.md — PyTutor-MCP (điểm vào cho mọi phiên Claude Code)

## 1. Tổng quan
- **PyTutor-MCP**: Khóa luận tốt nghiệp CNTT, ĐH Kinh tế Quốc dân (NEU). Đề tài: *Xây dựng hệ thống hỗ trợ học lập trình Python với phản hồi thích ứng và phân tích tiến độ học tập*. Sinh viên: Trần Minh Khánh (K65, MSV 11236131).
- Repo: `C:\Users\Admin\Downloads\PyTutor-Thesis` (GitHub `Chthollyuhc/PyTutor-MCP`, nhánh `main`). Giao diện tiếng Việt.
- Trạng thái: Phase 1–15.6 PASSED · **Phase 16** (AI Tutor Upgrade) = MVP implemented · **Phase 17** (Adaptive Feedback & Analytics) = Technical MVP complete, **pilot người dùng chưa chạy**. Dashboard: `PLAN.md`.
- Kiến trúc: `frontend/` (React 18 + Vite + Tailwind + Monaco + react-router-dom 7) → `backend/` (FastAPI, MCP Host, JWT RBAC, SQLite WAL) → `mcp_server/` (tiến trình riêng, JSON-RPC 2.0 qua stdio, server `PyTutor-Code-Engine`).
- 8 MCP tools: `run_test_cases`, `analyze_code_ast`, `get_exercise_list`, `get_exercise_details`, `save_learning_event`, `get_attempt_history`, `get_student_model`, `trace_code_execution`.

## 2. Lệnh chuẩn (Windows 11, PowerShell)
- Dùng `;` thay `&&`. Dùng `py` (không `python3`), `npm.cmd`/`npx.cmd`. Luôn đặt `$env:PYTHONIOENCODING="utf-8"`.
- Chạy app: `.\start_dev.bat` (backend :8000 + Vite :5173). Thủ công: `py -m uvicorn backend.main:app --reload --port 8000` và `cd frontend; npm.cmd run dev`.
- Build/test frontend (trong `frontend/`): `npm.cmd run test:theme`, `npm.cmd run build` (cảnh báo chunk >500 kB là bình thường).
- Biên dịch: `py -m compileall -q backend mcp_server`.
- Test lõi: `py -m unittest test_phase16_ai_upgrade test_phase17_adaptive_analytics test_qa_authorization -v`; replay: `py evaluate_phase17_adaptive.py`.
- Test theo phân hệ (chỉ chạy khi sửa đúng phần đó): `py -m mcp_server.test_mcp_server`, `py -m backend.test_backend_e2e`, `test_phase5_backend.py`, `test_phase8_chat.py`, `test_phase9_visualizer.py`, `test_phase10_gamification.py`, `test_phase12_classroom_exam.py`, `test_phase13_14_neu_lms.py`, `test_phase15_3_qa_audit.py`, `test_phase15_4_action_buttons.py`.
- **BẮT BUỘC cô lập DB khi chạy test** (nhiều test ghi vào DB hiện hành, `pytutor.db` chứa dữ liệu demo tích lũy — không xóa/ghi đè):

```powershell
$env:PYTHONIOENCODING = "utf-8"
$tmpDb = Join-Path $env:TEMP ("pytutor_check_" + [guid]::NewGuid().ToString("N") + ".db")
$tmpKb = Join-Path $env:TEMP ("pytutor_kb_" + [guid]::NewGuid().ToString("N") + ".sqlite3")
$env:PYTUTOR_DB_PATH = $tmpDb; $env:PYTUTOR_KNOWLEDGE_DB_PATH = $tmpKb
try { py -m unittest test_phase17_adaptive_analytics -v }
finally {
  Remove-Item Env:PYTUTOR_DB_PATH, Env:PYTUTOR_KNOWLEDGE_DB_PATH -ErrorAction SilentlyContinue
  Remove-Item $tmpDb, "$tmpDb-wal", "$tmpDb-shm", $tmpKb -Force -ErrorAction SilentlyContinue
}
```
- `PYTUTOR_DB_PATH` đọc ở `backend/database.py` và `mcp_server/storage.py` (mặc định `pytutor.db`); `PYTUTOR_KNOWLEDGE_DB_PATH` đọc ở `backend/rag/retriever.py` (mặc định `pytutor_knowledge.sqlite3`).
- Kết quả kiểm chứng gần nhất (12/11/2026, DB cô lập): compileall OK; 20 unittest (Phase 16 ×6, Phase 17 ×5, QA authorization ×9) OK; replay Phase 17: 6/6 chiến lược khớp, 6/6 giữ nguyên level, baseline 2/6; `test:theme` 3/3; `vite build` OK (1695 modules).

## 3. Bản đồ file (đọc có chọn lọc)
- Docs chuẩn: `PLAN.md` (trạng thái phase), `PRODUCT.md`, `DESIGN.md`, `AI_HANDOFF_CONTEXT.md` (nguồn chi tiết), `plans/PLAN_16_AI_UPGRADE.md`, `docs/PHASE_17_METRICS_AND_BENCHMARK.md`, `docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md`.
- Backend: `main.py` (endpoint, ~1,480 dòng), `database.py` (~2,270 dòng), `auth.py` (JWT), `schemas.py`, `llm_service.py` (Gemini `gemini-3.5-flash-lite` + fallback Qwen/rule-based offline), `prompt_templates.py` (Jinja2: Socratic/Instructor/Reviewer), `guardrails.py`, `adaptive_policy.py`, `rag/retriever.py`, `mcp_client.py`.
- MCP: `mcp_server/server.py`, `sandbox.py`, `ast_analyzer.py`, `tracer.py`, `storage.py`, `exercises_data.py`. Cấu hình host ngoài: `mcp_configs/*.json` (cwd cố định `C:\Users\Admin\Downloads\PyTutor-Thesis`).
- Frontend: `frontend/src/App.jsx` (route `/login`, `/student`, `/student/classes/:classId`, `/student/ide[/:exerciseId]`, `/instructor`, `/instructor/classes/:classId`, `/instructor/exercises/new`, `/instructor/exercises/:id/edit`).
- **Không đọc nguyên văn** khi không cần sửa: `database.py`, `main.py`, `InstructorDashboard.jsx` (~1,470 dòng) — dùng Grep rồi đọc đúng hàm. Bỏ qua mặc định: `docs/WHY_MCP_EXPLAINED.md`, `docs/EVALUATION_REPORT.md` (cũ), `test_phase5..15_4*.py` (chỉ khi sửa phân hệ tương ứng).
- Tra `AI_HANDOFF_CONTEXT.md` theo việc: Gotchas §11; runbook/tài khoản §12; lớp tín chỉ/EXAM §13; NEU, Mastery Rubric, 4D analytics §14; Phase 15.x §15; AI/RAG §16.0; adaptive/metric/pilot §17.

## 4. Quy trình làm việc
- Vòng lặp: hiểu yêu cầu (mục tiêu, phạm vi không đổi, nghiệm thu, rủi ro dữ liệu) → plan **vertical slice** nhỏ (schema/DB → API/quyền → UI → test) → triển khai có test → review (bắt buộc với auth/RBAC/migration/dữ liệu cá nhân/Anti-Spoil) → xác minh → cập nhật `PLAN.md`/`AI_HANDOFF_CONTEXT.md` nếu đổi trạng thái phase.
- Còn quyết định nghiệp vụ/schema/kiến trúc chưa chốt → **hỏi trước**; yêu cầu kỹ thuật rõ ràng → tự làm, tự test, báo cáo.
- Giữ xác nhận cho xóa/ghi đè, DB thật, secrets, dịch vụ ngoài; không bật chế độ bỏ qua quyền.
- Bảo toàn thay đổi chưa commit (hiện có `CLAUDE_ONBOARDING_PROMPT.md`, `docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md` và các file xóa/sửa trong `docs/`, `README.md`); **không** `git reset`/`git checkout` để dọn.
- Mặc định mock LLM + dữ liệu sinh viên giả lập; không gửi nội dung người học thật lên provider ngoài; không nối Claude/MCP vào DB thật.
- Sửa UI: build không thay thế kiểm tra giao diện — nếu có browser/Playwright, chạy trên DB cô lập, kiểm tra student/instructor, console, light/dark, desktop/mobile.
- Session/model: chọn theo độ khó (mạnh cho kiến trúc/RBAC/Phase 17; cân bằng cho lát cắt đã chốt; nhanh cho tìm file/log). Mỗi mục tiêu lớn một session; tối đa 1–2 worker, không cùng sửa migration/`PLAN.md`/handoff/cấu hình chung/cùng component.

## 5. Luật bất biến
**Kiến trúc & sư phạm**
1. `backend/` **không** import hàm từ `mcp_server/`; mọi chấm test/AST/trace/đề/student model qua `backend/mcp_client.py` (stdio JSON-RPC).
2. Ba hành động IDE tách biệt: `▶ Chạy thử` = `POST /api/run-test` (không LLM, không sao); `🤖 Hỏi Gia sư AI` = `POST /api/submit` với `action_type='ask_ai'` (lưu lịch sử, **không** sao/modal/metric chính thức); `🚀 Nộp bài` = `action_type='submit'` (chấm chính thức, sao 1–3, Mastery Rubric, analytics).
3. Giữ 3 mức gợi ý (1 Socratic; 2 dòng lỗi + test fail; 3 dàn ý 4 bước + khung `# TODO`) và Anti-Spoil (`guardrails.py`).
4. `select_hint_strategy()` chỉ chọn chiến lược (`conceptual_start`, `failed_case_diagnosis`, `recurring_difficulty`, `solution_review`), **không** tự tăng `hint_level` vượt mức người học yêu cầu.
5. EXAM Mode Guard chạy trước RAG/LLM; giữ backend exam dù UI ẩn.
6. RBAC kiểm tra **server-side**; `/api/instructor/ai/class-chat` kiểm tra sở hữu lớp, chỉ đưa số liệu tổng hợp cho LLM (không SQL tự sinh, không code/danh tính SV).
**Dữ liệu & UI**
7. Không chèn chay bài tập vào code; thêm qua `/instructor` hoặc API vào SQLite.
8. Mọi kết nối SQLite: `timeout=20.0` + `PRAGMA journal_mode=WAL;`.
9. `SHOW_EXAM_SESSIONS = false` (`StudentPortalPage.jsx`, `StudentClassDetailPage.jsx`) giữ nguyên tới khi người dùng yêu cầu bật.
10. UI theo `DESIGN.md` (NEU green `#066e44`/`#13633e`, flat-by-default, light/dark) và `PRODUCT.md` (không đổi API contract/business rule khi chỉnh giao diện).
**Trung thực khoa học**
11. MCP chỉ là lớp tích hợp công cụ, không phải phương pháp dạy học hay bằng chứng hiệu quả.
12. `docs/knowledge_base/python_fundamentals.md` là tài liệu nội bộ, **chưa phải giáo trình NEU**; không bịa citation; chỉ nạp giáo trình NEU khi được cấp quyền.
13. Ngưỡng `data_status` (`no_data`=0, `limited`<3 bài khác nhau, `sufficient`≥3) và `autonomy_score` là heuristic vận hành, không phải cutoff/thang đo đã kiểm chứng. Chỉ `action_type='submit'` tính vào metric chính thức.
14. Replay Phase 17 là fixture tổng hợp, không LLM thật; pilot 2–3 người **chưa chạy** — không tuyên bố learning gain/nhân quả, chỉ ghi quan sát mô tả.

## 6. Môi trường & tài khoản demo
- `.env.example`: `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.5-flash-lite`, `QWEN_API_URL/QWEN_SECKEY/QWEN_MODEL`, `JWT_SECRET_KEY`. Thiếu key → rule-based offline fallback (không lỗi 500). Không commit key thật.
- Demo: `student` / `student123` (Trần Minh Khánh), `gv_tran` / `gv123` (Nguyễn Văn A), `gv_tuan` (Trần Văn B). Python 3.14, Node v24.
- Gotcha Windows: console cần UTF-8; `frontend/dist` sinh ra khi build — kiểm tra `git status` trước khi commit.

## 7. Lộ trình mở rộng `.claude/`
Chưa tách. Khi lặp lại nhiều: `.claude/rules/{backend,frontend,evaluation}.md`; skill `pytutor-phase-workflow` và `pytutor-qa` (QA trên DB cô lập) — chỉ tạo sau khi đã dùng workflow thật và có gotchas. Việc còn mở: nghiệm thu Phase 16 (false-positive/latency, nguồn RAG NEU được phép) và chạy pilot Phase 17.
