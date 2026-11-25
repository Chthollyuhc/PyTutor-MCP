# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# PyTutor-MCP (điểm vào cho mọi phiên Claude Code)

## 1. Tổng quan
- **PyTutor-MCP**: Khóa luận tốt nghiệp CNTT, ĐH Kinh tế Quốc dân (NEU). Đề tài: *Xây dựng hệ thống hỗ trợ học lập trình Python với phản hồi thích ứng dựa trên mô hình người học*. Sinh viên: Trần Minh Khánh (K65, MSV 11236131).
- Repo: `C:\Users\Admin\Downloads\PyTutor-Thesis` (GitHub `Chthollyuhc/PyTutor-MCP`, nhánh `main`). Giao diện tiếng Việt.
- Trạng thái: Phase 1–15.6 PASSED · **Phase 16** (AI Tutor Upgrade) = MVP implemented · **Phase 17** (Adaptive Feedback & Analytics) = Technical MVP complete, **pilot người dùng chưa chạy** · **Gói nâng cấp sư phạm v5.3** (S1–S5) = hoàn tất kỹ thuật, **chưa commit**, chưa kiểm chứng với LLM thật. Dashboard: `PLAN.md`; nhật ký v5.3: `plans/PLAN_THESIS_PEDAGOGICAL_UPGRADE.md` (mục 5.7 là phiên cuối).
- v5.6 (chưa commit): đề tài nhấn "phản hồi thích ứng dựa trên mô hình người học"; mô hình người học v3 (6 KC, trạng thái thứ bậc, heuristic chưa hiệu chuẩn, không phải BKT/IRT) + chính sách v3; xem `AI_HANDOFF_CONTEXT.md` §17.6.
- v5.4 (chưa commit): giao diện không còn nhắc MCP (backend MCP, `/api/health`, `mcp_trace` giữ nguyên); nhóm quá trình học cho giảng viên (`docs/PROCESS_GROUPS.md`); tài liệu Gia sư AI theo lớp (`docs/KB_UPLOAD_GUIDE.md`). MCP là một chức năng tích hợp công cụ, không phải điểm bán của đề tài.
- Kiến trúc: `frontend/` (React 18 + Vite + Tailwind + Monaco + react-router-dom 7) → `backend/` (FastAPI, MCP Host, JWT RBAC, SQLite WAL) → `mcp_server/` (tiến trình riêng, JSON-RPC 2.0 qua stdio, server `PyTutor-Code-Engine`).
- 8 MCP tools: `run_test_cases`, `analyze_code_ast`, `get_exercise_list`, `get_exercise_details`, `save_learning_event`, `get_attempt_history`, `get_student_model`, `trace_code_execution`.

## 2. Lệnh chuẩn (Windows 11, PowerShell)
- Dùng `;` thay `&&`. Dùng `py` (không `python3`), `npm.cmd`/`npx.cmd`. Luôn đặt `$env:PYTHONIOENCODING="utf-8"`.
- Chạy app: `.\start_dev.bat` (backend :8000 + Vite :5173). Thủ công: `py -m uvicorn backend.main:app --reload --port 8000` và `cd frontend; npm.cmd run dev`.
- Build/test frontend (trong `frontend/`): `npm.cmd run test:theme`, `npm.cmd run build` (cảnh báo chunk >500 kB là bình thường).
- Biên dịch: `py -m compileall -q backend mcp_server`.
- Test lõi: `py -m unittest test_phase16_ai_upgrade test_phase17_adaptive_analytics test_qa_authorization -v`; replay: `py evaluate_phase17_adaptive.py`.
- Gói nâng cấp v5.3 (hoàn tất kỹ thuật, xem `plans/PLAN_THESIS_PEDAGOGICAL_UPGRADE.md`; số liệu ở `docs/EVALUATION_REPORT_V5_3.md`; pilot ở `docs/PILOT_KIT.md`): `py -m unittest test_thesis_upgrade -v` (tự bỏ qua nếu chưa đặt hai biến DB tạm), `py evaluate_guardrails_benchmark.py [--holdout] [--json]` (thoát mã 1 nếu rò rỉ trên corpus phát triển), `py evaluate_rag_benchmark.py [--min-score 0.16] [--json]`. Corpus nằm ở `evaluation/`; tập `guardrail_holdout.json` **không được dùng để chỉnh luật guard**.
- v5.5 (13/11/2026, chưa commit): `py -m unittest test_level3_scaffold -v` (che logic khung mã Mức 3, không cần DB); `py evaluate_level3_skeleton.py [--holdout]` (đo bước che bằng cách chạy khung đã che; tập `level3_solutions_holdout.json` **không dùng để chỉnh luật**); `py evaluate_load_benchmark.py [--levels 1,5,10,20] [--per-level 20]` (đo tải nhẹ, tự mở uvicorn `:8012` trên DB tạm, khoảng 6 phút). Nháp chương kết quả: `docs/THESIS_CHAPTER4_DRAFT.md`; cơ sở sư phạm: `docs/PEDAGOGICAL_FOUNDATIONS.md` (trích dẫn chưa đối chiếu bản gốc); băm mật khẩu: `py -m unittest test_passwords -v` (`backend/passwords.py`, tương thích ngược với mật khẩu văn bản thường; DB thật chưa được chuyển sang dạng băm); dàn ý và câu hỏi phản biện: `docs/THESIS_OUTLINE_AND_DEFENSE.md`; điểm đề xuất 22 ca: `docs/REAL_LLM_SCORING_PROPOSAL.md`; nháp Chương 1+5 và Chương 3: `docs/THESIS_CHAPTER1_AND_5_DRAFT.md`, `docs/THESIS_CHAPTER3_DRAFT.md`; `py -m unittest test_pedagogy_v55 -v` (prompt khái niệm, đơn vị nhóm quá trình).
- `PYTUTOR_DISABLE_LLM=1` ép chế độ offline (không gọi Gemini/Qwen); dùng khi test, benchmark, pilot mặc định.
- **Chạy mỗi module unittest trong một tiến trình/DB tạm riêng.** Chạy gộp `test_thesis_upgrade` cùng `test_qa_authorization` trên một DB thì `test_qa_authorization` fail 2 test vì dữ liệu `tu_*` do test mới ghi vào (đã xác nhận: từng module chạy riêng đều đạt).
- Chạy **một** test: `py -m unittest test_phase17_adaptive_analytics.Phase17Tests.test_passed_code_uses_review_strategy -v` (vẫn phải cô lập DB như mẫu bên dưới). Không có linter cấu hình; "lint" = `compileall` + `vite build`.
- Kiểm tra giao diện trên DB cô lập: `.claude/launch.json` có `qa-backend` (uvicorn `:8001`, `PYTUTOR_DISABLE_LLM=1`, DB `%TEMP%\pytutor_qa.db`, KB `%TEMP%\pytutor_qa_kb.sqlite3`) và `qa-frontend` (Vite `:5174` qua `PYTUTOR_VITE_PORT`, proxy tới `PYTUTOR_API_TARGET=http://127.0.0.1:8001`). Xóa hai tệp tạm để có DB mới tinh (tự seed 3 tài khoản demo, 5 bài, lớp mẫu, 0 lượt nộp). Đóng cả hai server sau khi xong.
- **Gotcha DB thật:** backend dev `:8000` chạy `--reload` trên `pytutor.db` sẽ tự khởi động lại (`init_db()` + nạp lại chỉ mục KB trên DB thật) mỗi khi sửa tệp trong `backend/`. Test/QA cô lập không ghi vào DB thật, nhưng mốc sửa tệp vẫn đổi; muốn DB thật hoàn toàn đứng yên thì tắt backend dev trước khi sửa mã.
- Test theo phân hệ (chỉ chạy khi sửa đúng phần đó; hai mục đầu là **script**, `py -m unittest ...` sẽ báo "NO TESTS RAN"): `py -m mcp_server.test_mcp_server`, `py -m backend.test_backend_e2e`, `test_phase5_backend.py`, `test_phase8_chat.py`, `test_phase9_visualizer.py`, `test_phase10_gamification.py`, `test_phase12_classroom_exam.py`, `test_phase13_14_neu_lms.py`, `test_phase15_3_qa_audit.py`, `test_phase15_4_action_buttons.py`.
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
- Kết quả kiểm chứng v5.3 bản cuối (12/11/2026, DB cô lập, từng module chạy riêng, LLM tắt): `test_thesis_upgrade` 37, Phase 16 ×6, Phase 17 ×5, QA authorization ×9 đều OK; replay Phase 17 6/6; guard corpus phát triển rò rỉ 0/30 nhưng tập giữ riêng rò rỉ 4/14; RAG hit@3 36/38, no-source 13/14; MCP 8/8, backend E2E 6/6, Phase 8 7/7, Phase 10 6/6, Phase 12 7/7; `test:theme` 3/3; `vite build` OK (1697 modules); đã kiểm tra trình duyệt trên cặp QA (sinh viên S1–S8a của Pilot Kit, giảng viên, dark/light, 375px, lỗi mạng). Đã chạy lại `test_phase5/9/13_14/15_3/15_4` ngày 13/11 (13–14 và 15.4 sau khi sửa kịch bản); chưa thử với LLM thật.
- Kết quả kiểm chứng gần nhất trước v5.3 (12/11/2026, DB cô lập): compileall OK; 20 unittest (Phase 16 ×6, Phase 17 ×5, QA authorization ×9) OK; replay Phase 17: 6/6 chiến lược khớp, 6/6 giữ nguyên level, baseline 2/6; `test:theme` 3/3; `vite build` OK (1695 modules).

## 2b. Kiến trúc xuyên file (cần đọc nhiều file mới thấy)
- **Luồng chấm bài** (`backend/main.py` `POST /api/submit`, `require_student`): kiểm tra exam session/`ensure_class_access` → `backend/mcp_client.execute_submission_pipeline` (chạy test + AST + lịch sử + student model, thu `mcp_trace`) → `select_hint_strategy` → nhánh: EXAM guard (khóa AI) / chúc mừng cố định khi `submit` + pass hết (không gọi LLM) / `llm_service.generate_tutor_hint` → `save_llm_interaction` → `save_learning_event_via_mcp` (lỗi chỉ log warning) → nếu `submit` + pass: `calculate_autonomy_stars` + `save_exercise_stars`. `/api/run-test` dùng `run_test_only_pipeline` riêng.
- **Mỗi hàm trong `mcp_client.py` mở một tiến trình MCP stdio mới** (`async with stdio_client(get_server_params())`), không có kết nối dùng chung; chi phí handshake được ghi vào `mcp_trace`.
- **Mô hình người học nằm ở module hàm thuần dùng chung** `pytutor_shared/learner_model.py` (KC, trạng thái, hồ sơ lỗi/hỗ trợ, `classify_learning_process`). Hai bản `compute_student_model` (`mcp_server/storage.py` cho tool `get_student_model`, `backend/database.py`) giống hệt về mã nguồn, chỉ khác dòng mở kết nối (`get_conn()`); `test_thesis_upgrade` so khớp mã nguồn và kết quả. Sửa bản backend rồi sao chép sang MCP; logic mô hình sửa ở module chung. Lệnh: `py -m unittest test_learner_model -v`, `py evaluate_learner_model_policy.py (replay chính sách theo hồ sơ tổng hợp, LLM tắt); `py evaluate_real_llm_learner_model.py` (kiểm tra thật với Gemini trên hồ sơ tổng hợp, 48 lượt, cần `GEMINI_API_KEY`, DB tạm; chỉ chạy khi người dùng đồng ý gửi dữ liệu giả lập lên nhà cung cấp)` (120 ô, mức gợi ý phải giữ 120/120).
- **Guard & RAG đo được**: `backend/guardrails.py` (`GUARD_RULES_VERSION`) và `backend/rag/retriever.py` (`MIN_RELEVANCE`) có benchmark riêng; đổi luật/ngưỡng phải chạy lại hai script `evaluate_*_benchmark.py`. Truy xuất trả `[]` khi không đủ liên quan và chat báo `knowledge_status=no_source`; không bao giờ gắn nguồn khi danh sách rỗng.
- **Phản hồi gợi ý**: prompt có khung formative (mục tiêu → bằng chứng → bước kế tiếp); `submit` + pass dùng `build_pass_feedback` tất định (không LLM); `generate_rule_based_fallback` chỉ được nêu điều quan sát từ test/AST.
- **Luật sao v5.3 (S2.1/S2.4)**: sao chỉ sinh ở `submit` + pass; số sao theo mức gợi ý **cao nhất đã dùng ở `ask_ai` cho tới lần nộp đạt đầu tiên** (không gợi ý/Mức 1 → 3⭐, Mức 2 → 2⭐, Mức 3 → 1⭐); số lần nộp không trừ sao; nộp lại sau khi đạt là ôn tập, **không tăng sao**; `hint_level` gửi kèm lượt `submit` không tính. `star_rationale` (từ `explain_autonomy_stars`) phải khớp `calculate_autonomy_stars`; giao diện chỉ hiện thẻ sao sau `Nộp bài`.
- **Khóa phạm vi chat (S1.4)**: `/api/tutor/chat` quyết định `chat_scope` từ DB (`get_latest_passed_submission_code`), không tin code client gửi: chưa nộp đạt → `concept_only` (prompt không có code bài làm); đã đạt → `code_review` với code đã nộp + tóm tắt AST qua `mcp_client.get_code_structure_summary`. Offline: `build_system_rule_reply` → `build_offline_code_review_reply` / `build_offline_chat_reply`. `GET /api/exercises/{id}` trả `has_passed` chỉ để giao diện hiển thị.
- **Bài tập/Student model sống trong SQLite**, truy cập từ hai tiến trình (backend + MCP server) cùng file `PYTUTOR_DB_PATH` → cần WAL + `timeout=20.0`. `exercises_data.py` chỉ là seed/fallback.
- **LLM** (`llm_service.py`): prompt dựng từ `prompt_templates.py` (StrictUndefined) + chiến lược thích ứng + RAG; chuỗi fallback Gemini → Qwen → rule-based offline; đầu ra qua `check_student_output`.
- **RAG**: `lifespan` của FastAPI gọi `ingest_knowledge_base` mỗi lần khởi động (rebuild toàn bộ chỉ mục từ `docs/knowledge_base/*.md|txt`).
- Frontend gọi backend bằng axios; trạng thái role/lớp quyết định tuyến ở `App.jsx`, nhưng quyền thật nằm ở dependency `verify_token`/`require_student`/`ensure_class_access` phía backend.

## 3. Bản đồ file (đọc có chọn lọc)
- Docs chuẩn: `PLAN.md` (trạng thái phase), `PRODUCT.md`, `DESIGN.md`, `AI_HANDOFF_CONTEXT.md` (nguồn chi tiết), `plans/PLAN_16_AI_UPGRADE.md`, `docs/PHASE_17_METRICS_AND_BENCHMARK.md`, `docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md`.
- Backend: `main.py` (endpoint, ~1,480 dòng), `database.py` (~2,270 dòng), `auth.py` (JWT), `schemas.py`, `llm_service.py` (Gemini `gemini-3.5-flash-lite` + fallback Qwen/rule-based offline), `prompt_templates.py` (Jinja2: Socratic/Instructor/Reviewer), `guardrails.py`, `adaptive_policy.py`, `rag/retriever.py`, `mcp_client.py`.
- MCP: `mcp_server/server.py`, `sandbox.py`, `ast_analyzer.py`, `tracer.py`, `storage.py`, `exercises_data.py`. Cấu hình host ngoài: `mcp_configs/*.json` (cwd cố định `C:\Users\Admin\Downloads\PyTutor-Thesis`).
- Frontend: `frontend/src/App.jsx` (route `/login`, `/student`, `/student/classes/:classId`, `/student/ide[/:exerciseId]`, `/instructor`, `/instructor/classes/:classId`, `/instructor/exercises/new`, `/instructor/exercises/:id/edit`).
- **Không đọc nguyên văn** khi không cần sửa: `database.py`, `main.py`, `InstructorDashboard.jsx` (~1,470 dòng) — dùng Grep rồi đọc đúng hàm. Bỏ qua mặc định: `docs/WHY_MCP_EXPLAINED.md`, `docs/EVALUATION_REPORT.md` (cũ), `test_phase5..15_4*.py` (chỉ khi sửa phân hệ tương ứng).
- Tra `AI_HANDOFF_CONTEXT.md` theo việc: v5.3 (luật sao, khóa chat, lệnh benchmark, QA) §18; Gotchas §11; runbook/tài khoản §12; lớp tín chỉ/EXAM §13; NEU, Mastery Rubric, 4D analytics §14; Phase 15.x §15; AI/RAG §16.0; adaptive/metric/pilot §17.

## 4. Quy trình làm việc
- Vòng lặp: hiểu yêu cầu (mục tiêu, phạm vi không đổi, nghiệm thu, rủi ro dữ liệu) → plan **vertical slice** nhỏ (schema/DB → API/quyền → UI → test) → triển khai có test → review (bắt buộc với auth/RBAC/migration/dữ liệu cá nhân/Anti-Spoil) → xác minh → cập nhật `PLAN.md`/`AI_HANDOFF_CONTEXT.md` nếu đổi trạng thái phase.
- Còn quyết định nghiệp vụ/schema/kiến trúc chưa chốt → **hỏi trước**; yêu cầu kỹ thuật rõ ràng → tự làm, tự test, báo cáo.
- Giữ xác nhận cho xóa/ghi đè, DB thật, secrets, dịch vụ ngoài; không bật chế độ bỏ qua quyền.
- Bảo toàn thay đổi chưa commit (`docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md` và các thay đổi v5.3/v5.4 chưa commit); **không** `git reset`/`git checkout` để dọn.
- Mặc định mock LLM + dữ liệu sinh viên giả lập; không gửi nội dung người học thật lên provider ngoài; không nối Claude/MCP vào DB thật.
- Sửa UI: build không thay thế kiểm tra giao diện — nếu có browser/Playwright, chạy trên DB cô lập, kiểm tra student/instructor, console, light/dark, desktop/mobile.
- Session/model: chọn theo độ khó (mạnh cho kiến trúc/RBAC/Phase 17; cân bằng cho lát cắt đã chốt; nhanh cho tìm file/log). Mỗi mục tiêu lớn một session; tối đa 1–2 worker, không cùng sửa migration/`PLAN.md`/handoff/cấu hình chung/cùng component.

## 5. Luật bất biến
**Kiến trúc & sư phạm**
1. `backend/` **không** import hàm từ `mcp_server/`; mọi chấm test/AST/trace/đề/student model qua `backend/mcp_client.py` (stdio JSON-RPC).
2. Ba hành động IDE tách biệt: `▶ Chạy thử` = `POST /api/run-test` (không LLM, không sao); `🤖 Hỏi Gia sư AI` = `POST /api/submit` với `action_type='ask_ai'` (lưu lịch sử, **không** sao/modal/metric chính thức); `🚀 Nộp bài` = `action_type='submit'` (chấm chính thức, sao 1–3, Mastery Rubric, analytics).
3. Giữ 3 mức gợi ý (1 Socratic; 2 dòng lỗi + test fail; 3 dàn ý 4 bước + khung `# TODO`) và Anti-Spoil (`guardrails.py`).
3b. Mức 3 cho cấu trúc và thuật toán bằng lời, không cho mã Python của logic (v5.12): đầu ra LLM ở Mức 3 (khi chưa đạt) phải qua `enforce_level3_skeleton` (khung mã) và `enforce_level3_prose` (phần chữ). Thuật toán chi tiết lấy từ `exercises.algorithm_notes` (giảng viên viết, **chỉ Mức 3 nhận, sinh viên không bao giờ thấy**) hoặc khuôn theo dạng bài (`backend/hint_algorithm.py`, heuristic). Hệ thống dành cho người muốn học, không phải để kiểm tra: **không thêm** chức năng chống gian lận hay kỳ thi.
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
14. Chỉ số quá trình của giảng viên (nhóm quá trình, lượt chạy thử) là bằng chứng mô tả với ngưỡng quy ước chưa hiệu chuẩn, không phải metric chính thức; chỉ `submit` tính vào sao/student model.
15. Tài liệu giảng viên tải lên gắn theo lớp (`kb_documents`, `scope`=class_id); `retrieve_knowledge(class_id=None)` chỉ lấy tài liệu chung; lớp này không bao giờ thấy tài liệu lớp khác; nguồn hiển thị kèm "do giảng viên lớp cung cấp"; đổi retriever phải chạy lại `evaluate_rag_benchmark.py` (hit@3 36/38).
16. Replay Phase 17 là fixture tổng hợp, không LLM thật; pilot 2–3 người **chưa chạy** — không tuyên bố learning gain/nhân quả, chỉ ghi quan sát mô tả.

## 6. Môi trường & tài khoản demo
- `.env.example`: `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.5-flash-lite`, `QWEN_API_URL/QWEN_SECKEY/QWEN_MODEL`, `JWT_SECRET_KEY`. Thiếu key → rule-based offline fallback (không lỗi 500). Không commit key thật.
- Demo: `student` / `student123` (Trần Minh Khánh), `gv_tran` / `gv123` (Nguyễn Văn A), `gv_tuan` (Trần Văn B). Python 3.14, Node v24.
- Gotcha Windows: console cần UTF-8; `frontend/dist` sinh ra khi build — kiểm tra `git status` trước khi commit.

## 7. Lộ trình mở rộng `.claude/`
Chưa tách. Khi lặp lại nhiều: `.claude/rules/{backend,frontend,evaluation}.md`; skill `pytutor-phase-workflow` và `pytutor-qa` (QA trên DB cô lập) — chỉ tạo sau khi đã dùng workflow thật và có gotchas. Việc còn mở (của con người): chạy pilot thật theo `docs/PILOT_KIT.md` (2–3 người, chỉ ghi quan sát mô tả) và xem diff rồi quyết định Git commit cho toàn bộ v5.3 — **agent không tự `git commit`**. Tùy chọn: thử kịch bản S1–S8 với LLM thật trên dữ liệu giả lập; nguồn RAG NEU chỉ nạp khi được cấp quyền.

## 8. v5.7 (chưa commit)
- Test mới: `test_data_capture_v57`, `test_class_overview_v57` (mỗi module một DB tạm; `.claude/run_isolated.ps1 <module>...`). Luật 6: chat AI của giảng viên **ẩn ở UI** từ v5.7, endpoint backend giữ. Từ điển dữ liệu: `docs/LEARNER_DATA_DICTIONARY.md`.
- Hai bản `compute_student_model` đã đồng bộ lại (nạp KC nội tuyến); `test_thesis_upgrade` 61/61 OK.

## 9. v5.8 (chưa commit)
- "Hành trình học" (SV) và "Tình hình lớp" 3 tầng (GV): chỉ đọc và trình bày, API chỉ thêm. Test: `.claude/run_isolated.ps1 test_visual_views_v58` (tự dựng lớp mẫu bằng `seed/seed_demo_class_v58.py`, từ chối chạy nếu không phải DB tạm); `npm.cmd run test:ui-utils`. Lý do thiết kế: `docs/VISUAL_DESIGN_RATIONALE.md`; nhật ký: `AI_HANDOFF_CONTEXT.md` §20.
- Bảng xếp hạng (`LeaderboardModal`) mâu thuẫn nguyên tắc "so với chính mình", **ngoài phạm vi v5.8**, ghi là việc còn mở.

## 10. v5.9 (chưa commit) — Lời thường
- Câu nhận xét cho SV/GV chỉ sinh ở `backend/plain_language.py` (hàm thuần, có `BANNED_WORDS`); giao diện hiển thị nguyên văn các trường `*_vi`. Màn chính: SV `TodayCard` (trang chủ + Hành trình học); GV "Bản tin lớp" + 3 nhóm bạn + bài tập của lớp; số liệu v5.8 nằm trong "Xem số liệu đầy đủ".
- Test: `.\.claude\run_isolated.ps1 test_plain_language_v59`; frontend `npm.cmd run test:ui-utils` (gồm quét từ cấm ở `components/plain/` và `StudentProfileModal.jsx`).

## 11. v5.10 (nhánh `feat/overnight-deep-upgrade`) — 3 mức gợi ý
- Lệnh đo: `py evaluate_hint_levels.py --offline --quiet --tag X` (thêm `--holdout` hoặc `--redteam`); `--real` gọi Gemini thật (trần 300 lượt cả đêm, `evaluation/v510_gemini_calls.json`; chỉ dữ liệu giả lập); `--rescore <json>` tính lại kiểm tra; `--levels 1` tiết kiệm lượt. Hồi quy đầy đủ: `.\.claude
un_suite_v510.ps1 -OutDir <thư mục>`.
- Test: `test_hint_quality_v510`, `test_hint_evidence_v510`, `test_prompt_golden_v510`, `test_hint_resilience_v510` (không cần DB). Đổi prompt gợi ý thì sinh lại tệp vàng (`py evaluation/gen_prompt_golden_v510.py (đặt PYTHONPATH=. và PYTUTOR_DISABLE_LLM=1)`) và ghi lý do.
- Luật mới: Mức 1 **không nhận** giá trị kiểm thử trong prompt; dòng Mức 2 trích chỉ là điều quan sát được, không phải kết luận dòng sai; chú thích của người học không bao giờ được chép vào gợi ý; vết chạy chỉ cho `ask_ai`, có timeout và fallback. Tập giữ riêng gợi ý `evaluation/hint_scenarios_holdout.json` chỉ để đo. Điểm 0–5 trong `docs/HINT_LEVELS_BEFORE_AFTER_V510.md` là đề xuất của trợ lý, không ghi thành điểm tác giả.

## 12. v5.11
- Tên hiển thị: **Điểm nỗ lực** (trước là "Sao tự lực"); tên nội bộ `autonomy_*`/`stars_earned` giữ nguyên. Chặng đường trang chủ chọn lớp qua `student_journey.pick_path_class` (test `test_path_class_v511`). Gợi ý đọc đề và bộ kiểm thử qua `backend/exercise_brief.py` (test `test_exercise_brief_v511`); Mức 1 vẫn KHÔNG nêu giá trị kiểm thử hay ví dụ của đề.

## 13. v5.12 (chưa commit) — Mức 2 và Mức 3 mạnh hơn
- Mức 3: thuật toán chi tiết bằng lời (ý tưởng, Bước 1–4 kèm ý con, trường hợp cần xử lý, `# TODO (Bước 3.k)`); Mức 2: đối chứng test đạt/chưa đạt, dãy giá trị theo vết, dạng lệch, "biến chỉ gán một lần" (quan sát, không kết luận sai), xin lại thì đổi test lỗi. Chi tiết và số đo: `docs/HINT_L2_L3_V512.md`; kế hoạch: `plans/PLAN_V512_HINT_L2_L3.md`.
- Test: `.\.claudeun_isolated.ps1 test_hint_l23_v512` (17 test không cần DB + 3 test API cần DB tạm). Đổi prompt/khuôn thì sinh lại tệp vàng (`py evaluation/gen_prompt_golden_v510.py`, đặt `PYTHONPATH=.` và `PYTUTOR_DISABLE_LLM=1`) và đo lại `evaluate_hint_levels.py --offline` ở cả ba tập.
- Cột `algorithm_notes` được thêm khi `init_db()` chạy (backend dev `--reload` sẽ thêm cột vào `pytutor.db` thật khi khởi động lại); 5 bài đã có trong DB thật chưa có ghi chú (seed chỉ chạy khi bảng trống).
- Đã đo Gemini thật 38 lượt cho gói này (tổng 367/375); đã đo lại 8 lượt sau hai sửa (Mức 3 tốt hơn, Mức 2 vẫn yếu). Xem `docs/HINT_L2_L3_V512.md` §5.

## 14. v5.15 (chưa commit) — năng lực do giảng viên chọn, quản lý năng lực/tài liệu chung
- Bài có `exercises.kc_tags` (giảng viên chọn); rỗng thì dò từ khóa như cũ. 6 năng lực hệ thống khóa; năng lực/tài liệu chung tự thêm chỉ người tạo sửa/tắt/xóa; hai tệp tài liệu trên đĩa chỉ tắt/bật. Pythonic Review đã ẩn khỏi giao diện (endpoint giữ). Test: `.\.claude\run_isolated.ps1 test_kc_and_kb_management`. Chi tiết: `AI_HANDOFF_CONTEXT.md` §25.
