# MASTER ONBOARDING PROMPT CHO CLAUDE — DỰ ÁN PYTUTOR-MCP

> **Hướng dẫn sử dụng (dành cho chủ dự án):**
> - Tài liệu này đã được đồng bộ với [`docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md`](docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md).
> - Nếu dùng **Claude Code** tại thư mục `C:\Users\Admin\Downloads\PyTutor-Thesis`, bạn chỉ cần gõ:
>   `Đọc kỹ và thực hiện toàn bộ chỉ dẫn trong @CLAUDE_ONBOARDING_PROMPT.md để nắm dự án, kiểm chứng môi trường trên DB cô lập và viết file CLAUDE.md hoàn chỉnh tại thư mục gốc.`
> - Nếu dùng **Claude Desktop / Web / Cursor**, hãy copy toàn bộ nội dung từ mục **`## [BẮT ĐẦU PROMPT GỬI CLAUDE]`** trở xuống.
> - Sau khi Claude tạo xong `CLAUDE.md` và bạn đã hài lòng, có thể xóa file `CLAUDE_ONBOARDING_PROMPT.md` này để repo gọn gàng.

---

## [BẮT ĐẦU PROMPT GỬI CLAUDE]

Bạn đang tiếp quản vai trò kỹ sư phần mềm & trợ lý kỹ thuật cho dự án **PyTutor-MCP** tại thư mục:
`C:\Users\Admin\Downloads\PyTutor-Thesis` *(kho lưu trữ GitHub: `https://github.com/Chthollyuhc/PyTutor-MCP`, nhánh `main`)*.

Đây là **Đồ án / Khóa luận Tốt nghiệp Đại học** ngành Công nghệ Thông tin tại **Trường Đại học Kinh tế Quốc dân (NEU)**:
- **Đề tài:** *Xây dựng hệ thống hỗ trợ học lập trình Python với phản hồi thích ứng và phân tích tiến độ học tập*
- **Sinh viên thực hiện:** Trần Minh Khánh (Khóa K65 CNTT — MSV: `11236131`)

Nhiệm vụ của bạn trong phiên làm việc này gồm **3 việc liên tiếp**:
1. **Đọc đúng tài liệu và mã nguồn trọng yếu** theo lộ trình tiết kiệm token bên dưới để hiểu chính xác kiến trúc, quy trình làm việc Claude Code của dự án, môi trường Windows và các luật bất biến của hệ thống.
2. **Chạy kiểm chứng nhanh trên máy bằng DB tạm cô lập** (tự động thực thi phần kiểm thử/build an toàn, không chạm `pytutor.db` và `pytutor_knowledge.sqlite3` gốc) để xác nhận trạng thái thực tế hiện tại.
3. **Tạo file `CLAUDE.md` hoàn chỉnh** tại `C:\Users\Admin\Downloads\PyTutor-Thesis\CLAUDE.md` làm điểm vào chuẩn mực (< ~200 dòng) cho mọi phiên Claude Code tiếp theo.

---

### 1. BỨC TRANH TỔNG QUAN & TRẠNG THÁI HIỆN TẠI

1. **Kiến trúc 4 tầng:**
   - **Frontend (`frontend/`):** React 18 + Vite + Tailwind CSS + Monaco Editor + React Router (`frontend/src/App.jsx` định tuyến `/`, `/login`, `/student`, `/student/classes/:classId`, `/student/ide`, `/student/ide/:exerciseId`, `/instructor`, `/instructor/classes/:classId`, `/instructor/exercises/new`, `/instructor/exercises/:id/edit`). Ngôn ngữ giao diện là tiếng Việt.
   - **Backend Host (`backend/`):** FastAPI (`backend/main.py`) đóng vai trò MCP Host & Pedagogical Orchestrator, JWT Auth RBAC (`backend/auth.py`), Pydantic schemas (`backend/schemas.py`), dịch vụ LLM (`backend/llm_service.py`: `gemini-3.5-flash-lite` mặc định + fallback `gemini-3.1-flash-lite` / Qwen / rule-based offline), Jinja2 prompt templates (`backend/prompt_templates.py`), RAG cục bộ SQLite FTS5 + sparse TF-IDF (`backend/rag/retriever.py`), guardrails đầu vào/ra (`backend/guardrails.py`), chính sách chọn chiến lược thích ứng deterministic (`backend/adaptive_policy.py`), SQLite WAL engine (`backend/database.py`).
   - **MCP Server (`mcp_server/`):** Tiến trình độc lập (`mcp>=2.2.0`) giao tiếp 100% qua **JSON-RPC 2.0 `stdio`** (`mcp_server/server.py`, tên server `"PyTutor-Code-Engine"`), cung cấp **8 công cụ**: `run_test_cases`, `analyze_code_ast`, `get_exercise_list`, `get_exercise_details`, `save_learning_event`, `get_attempt_history`, `get_student_model`, `trace_code_execution`.
   - **Database:** SQLite chế độ `PRAGMA journal_mode=WAL;` với `timeout=20.0` (`pytutor.db`), hỗ trợ chuyển hướng cô lập qua **`PYTUTOR_DB_PATH`** (và **`PYTUTOR_KNOWLEDGE_DB_PATH`** cho chỉ mục RAG `pytutor_knowledge.sqlite3`).

2. **Tiến độ các Phase:**
   - **Phase 1 → Phase 15.6:** Đã hoàn thiện (LMS đa tầng NEU với 24 học phần CNTT, tách biệt 3 hành động IDE `▶ Chạy thử` / `🤖 Hỏi Gia sư AI` / `🚀 Nộp bài`, Sư phạm giàn giáo 3 mức tương phản + Anti-Spoil, Sao tự lực 1–3⭐, Visualizer 8th MCP tool, sửa lỗi phím Spacebar Monaco, cờ giao diện `SHOW_EXAM_SESSIONS = false` tạm ẩn tab lịch thi trong UI nhưng giữ nguyên backend).
   - **Phase 16 (`plans/PLAN_16_AI_UPGRADE.md`) — AI Tutor Upgrade:** Đang ở trạng thái **MVP IMPLEMENTED** (đã có Jinja2 persona, RAG TF-IDF cục bộ, role-based chat cho student & instructor có kiểm tra quyền lớp, input/output guardrails, telemetry & feedback UI; còn chờ nghiệm thu mở rộng, đo false-positive/latency và nguồn học liệu NEU chính thức được cấp quyền).
   - **Phase 17 (`docs/PHASE_17_METRICS_AND_BENCHMARK.md`) — Adaptive Feedback & Learning Analytics:** Đang ở trạng thái **TECHNICAL MVP COMPLETE; USER PILOT PENDING** (tách `action_type='submit'` khỏi `'ask_ai'` trong mọi metric chính thức, gắn `data_status`: `no_data`/`limited`/`sufficient`, dùng `select_hint_strategy` deterministic và bảo toàn `hint_level` người học chọn; chưa chạy pilot 2–3 người).

---

### 2. LỘ TRÌNH ĐỌC FILE TIẾT KIỆM TOKEN (ĐỌC THEO THỨ TỰ)

Tuyệt đối **không quét lan man toàn bộ repo** và **không đọc nguyên văn các file quá lớn** (`backend/database.py` 2,273 dòng, `backend/main.py` 1,480 dòng, `InstructorDashboard.jsx` 1,469 dòng) nếu chưa cần sửa trực tiếp vào hàm cụ thể.

**Danh sách file KHÔNG đọc khi onboarding (tránh lãng phí token):**
- `docs/WHY_MCP_EXPLAINED.md`, `docs/EVALUATION_REPORT.md` (báo cáo benchmark v3.0 cũ từ 20/10/2026).
- Các file `test_phase5..15_4*.py` (chỉ đọc/chạy khi sửa đúng phân hệ tương ứng).

Hãy đọc đúng 3 vòng sau:

#### Vòng 1 — Tài liệu định hướng, quy trình & chuẩn dự án
1. `PLAN.md` (166 dòng) — Bảng tổng hợp trạng thái Phase 1–17.
2. `PRODUCT.md` (52 dòng) — Phạm vi sản phẩm, ranh giới nghiệp vụ và ngôn ngữ.
3. `DESIGN.md` (149 dòng) — Design tokens NEU green (`#066e44`/`#13633e`), quy tắc "Flat-By-Default", không tự ý đổi API/luồng nghiệp vụ khi sửa UI.
4. `docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md` (146 dòng) — Quy trình Claude Code chuẩn cho PyTutor (vertical slice, session/model routing, Playwright UI check, permission/privacy boundaries, cấu trúc `CLAUDE.md` + lộ trình mở rộng `.claude/`).
5. `plans/PLAN_16_AI_UPGRADE.md` (210 dòng) — Thiết kế & tiêu chí nghiệm thu Phase 16.
6. `docs/PHASE_17_METRICS_AND_BENCHMARK.md` (89 dòng) — Hợp đồng metric, chính sách thích ứng, cơ sở nghiên cứu & kịch bản pilot Phase 17.
7. `README.md` *(chỉ đọc lướt mục 3–7 khi cần tra cứu cấu trúc thư mục, kịch bản demo hoặc danh mục endpoint)*.

#### Vòng 2 — Single Source of Truth (`AI_HANDOFF_CONTEXT.md`, 1,292 dòng — đọc theo mục)
1. Đọc **Mục lục & Mục 1** (dòng 1–75): Quy tắc vận hành, Windows env, quy tắc dữ liệu.
2. Đọc **Mục 11 & 12** (dòng 658–747): Kho lỗi kỹ thuật đã sửa (Gotchas) và Runbook chạy/test.
3. Đọc **Mục 14–17** (dòng 782–1292): Chuẩn hóa NEU, 4D Analytics, chi tiết các bản vá Phase 15.1–15.6, và bản chốt Phase 16–17.
4. *(Chỉ đọc thêm Mục 3–10 và 13 khi cần tra sâu schema SQLite, 8 MCP tools, hoặc luồng modal/EXAM mode).*

#### Vòng 3 — Xác minh cấu hình & lõi kiến trúc thực tế trong code
1. `requirements.txt`, `.env.example`, `frontend/package.json`, `start_dev.bat`, `mcp_configs/claude_desktop_config.json`.
2. Đọc toàn bộ các file nhỏ cốt lõi:
   - `backend/adaptive_policy.py` (32 dòng)
   - `backend/guardrails.py` (47 dòng)
   - `backend/prompt_templates.py` (50 dòng)
   - `backend/auth.py` (77 dòng)
   - `backend/rag/retriever.py` (101 dòng)
   - `docs/knowledge_base/python_fundamentals.md` (32 dòng)
   - `mcp_server/server.py` (171 dòng)
   - `frontend/src/App.jsx` (146 dòng)
3. Đọc lướt đầu file & cấu trúc import của `backend/mcp_client.py`, `backend/llm_service.py`, `backend/main.py` để xác nhận ranh giới gọi MCP qua stdio và vị trí các endpoint chính.

---

### 3. CÁC NGUYÊN TẮC BẤT BIẾN, QUY TRÌNH CLAUDE CODE & BẪY MÔI TRƯỜNG (BẮT BUỘC CHẮT LỌC VÀO `CLAUDE.md`)

#### A. Môi trường Windows 11 & PowerShell
- **Shell:** PowerShell trên Windows 11 — **KHÔNG dùng `&&`** để nối lệnh, phải dùng `;`.
- **Python 3.14:** Luôn gọi `py` (hoặc `py -3`), **KHÔNG dùng `python3`**. Luôn đặt `$env:PYTHONIOENCODING="utf-8"` trước khi chạy script/test Python để tránh lỗi font tiếng Việt.
- **Node.js / Vite:** Luôn dùng `npm.cmd` và `npx.cmd` thay cho `npm`/`npx`.
- **Không phụ thuộc đường dẫn cứng:** Code lấy root động qua `Path(__file__).resolve().parent.parent`, nhưng các file cấu hình host ngoài trong `mcp_configs/` đã đặt `cwd` là `C:\Users\Admin\Downloads\PyTutor-Thesis`.

#### B. Luật bất biến về Kiến trúc & Nghiệp vụ
1. **Ranh giới MCP tuyệt đối:** `backend/` **TUYỆT ĐỐI KHÔNG** import trực tiếp hàm từ `mcp_server/`. Mọi thao tác chấm test, AST, tracer, lấy đề/student model trong luồng MCP phải đi qua `backend/mcp_client.py` (JSON-RPC 2.0 `stdio`).
2. **Tách biệt 3 hành động IDE:**
   - `▶ Chạy thử` (`POST /api/run-test`): chạy sandbox nhanh, không gọi LLM, không ghi sao.
   - `🤖 Hỏi Gia sư AI` (`POST /api/submit` với `action_type='ask_ai'`): lưu lịch sử hướng dẫn để tránh lặp gợi ý, **KHÔNG cấp sao, KHÔNG mở modal chúc mừng, KHÔNG tính vào metric nộp chính thức**.
   - `🚀 Nộp bài` (`POST /api/submit` với `action_type='submit'`): chấm điểm chính thức, cấp 1–3 sao tự lực dựa trên lịch sử hỏi AI, cập nhật Mastery Rubric & analytics.
3. **Bảo toàn cơ chế sư phạm & an toàn:**
   - Giữ nguyên phân hóa 3 mức gợi ý (Mức 1 Socratic câu hỏi; Mức 2 chỉ dòng lỗi & mổ xẻ test fail; Mức 3 dàn ý 4 bước + khung code `# TODO`) và `Anti-Spoil Guard` (input/output guardrails).
   - `select_hint_strategy()` chỉ chọn chiến lược (`conceptual_start`, `failed_case_diagnosis`, `recurring_difficulty`, `solution_review`), **KHÔNG tự động tăng `hint_level`** vượt quá mức sinh viên yêu cầu.
   - `EXAM Mode Guard` luôn chạy trước RAG và trước mọi lệnh gọi LLM; giữ nguyên backend EXAM dù tab thi/thực hành đang ẩn ở UI.
   - Mọi quyền giảng viên/sinh viên phải được kiểm tra **server-side**; chat giảng viên (`/api/instructor/ai/class-chat`) bắt buộc kiểm tra quyền sở hữu lớp và chỉ đưa số liệu tổng hợp cho LLM (không đưa SQL tự sinh, không lộ code/danh tính sinh viên).
4. **Dữ liệu & Giao diện:**
   - **Không chèn chay bài tập** vào file code Python; mọi bài tập phải quản lý qua `/instructor` hoặc API hợp lệ lưu SQLite.
   - Mọi kết nối SQLite dùng `timeout=20.0` và `PRAGMA journal_mode=WAL;`.
   - Cờ `SHOW_EXAM_SESSIONS = false` đang tạm ẩn tab lịch thi ở `StudentPortalPage.jsx` và `StudentClassDetailPage.jsx` — giữ nguyên cho đến khi người dùng yêu cầu bật lại; không xóa backend exam sessions.
   - Khi sửa UI, tuân thủ `DESIGN.md` (Light/Dark theme, NEU green, flat-by-default) và `PRODUCT.md` (không tự đổi API contract hay business rules).

#### C. Quy trình làm việc Claude Code cho PyTutor (theo `docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md`)
1. **Vòng lặp chuẩn & Vertical Slice:** **Hiểu yêu cầu** (nêu mục tiêu, phạm vi không đổi, điều kiện nghiệm thu, test, rủi ro dữ liệu) → **Plan theo lát cắt dọc nhỏ** (schema/DB → API/quyền → UI → kiểm thử, thay vì làm xong hết một tầng mới kiểm tra) → **Triển khai có kiểm thử** → **Review** (bắt buộc rà kỹ/cross-review với auth, RBAC, migration, dữ liệu cá nhân, Anti-Spoil hoặc thay đổi lớn) → **Xác minh** → **Cập nhật `PLAN.md` / `AI_HANDOFF_CONTEXT.md`** khi trạng thái phase thay đổi.
2. **Ranh giới hỏi vs tự thực thi:** Với yêu cầu kỹ thuật đã rõ, chủ động phân tích, triển khai, chạy kiểm thử và báo cáo; **khi còn quyết định ảnh hưởng nghiệp vụ, phạm vi sản phẩm, schema hoặc đánh đổi kiến trúc chưa chốt, phải hỏi trước khi tự mở rộng**.
3. **An toàn quyền & Git Worktree:**
   - Giữ xác nhận cho thao tác xóa/ghi đè file, thao tác DB thật, secrets và external services — **không bật chế độ bỏ qua mọi quyền**; chỉ allowlist lệnh kiểm thử/build an toàn đã hiểu.
   - **Bảo toàn mọi thay đổi chưa commit** (ví dụ `CLAUDE_ONBOARDING_PROMPT.md`, `docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md`); **tuyệt đối không** dùng `git reset` hay `git checkout` để "dọn" worktree.
4. **Quyền riêng tư & Mock mặc định:** Mặc định mock LLM và dùng dữ liệu sinh viên giả lập khi chạy test/pilot. Không gửi nội dung người học thật lên provider ngoài khi chưa đồng ý; không kết nối Claude hoặc MCP vào DB/tài khoản sinh viên thật để hỗ trợ code.
5. **Kiểm tra UI bằng trình duyệt:** Build thành công (`npm.cmd run build`) **không thay thế** kiểm tra giao diện. Khi thay UI, nếu môi trường có browser/Playwright, hãy chạy app trên dữ liệu test/demo cô lập và kiểm tra luồng student/instructor, console errors, light/dark và desktop/mobile.
6. **Quản lý Session & Chọn Model theo năng lực:**
   - Chọn năng lực model theo độ khó/rủi ro (không khóa cứng tên model vì tên/giá thay đổi): mạnh cho kiến trúc/RBAC/Phase 17, cân bằng cho lát cắt đã chốt & regression test, nhanh cho tìm file/log/bản đồ repo.
   - Mỗi mục tiêu lớn dùng một session riêng (hoặc `/compact` có chỉ dẫn); tối đa **1–2 worker** khi hai lát cắt thực sự độc lập và không đụng cùng file (cấm để 2 worker cùng sửa migration, `PLAN.md`, handoff, cấu hình chung hoặc cùng component); truyền brief rõ file sở hữu, file cấm chạm và lệnh test.

#### D. Ranh giới Trung thực Khoa học (Bắt buộc cho Khóa luận NEU)
- **Vai trò của MCP:** Chỉ là thành phần kiến trúc tích hợp công cụ (chạy code, AST, trace, lưu sự kiện); **không** mô tả MCP là phương pháp dạy học hay bằng chứng tự chứng minh hiệu quả học tập cao hơn.
- **Nguồn RAG (`docs/knowledge_base/python_fundamentals.md`):** Là tài liệu Python/PEP 8 biên soạn nội bộ, **CHƯA phải giáo trình chính thức của NEU**. Chỉ nạp giáo trình NEU khi người dùng cung cấp/xác nhận quyền sử dụng. Không bịa citation.
- **Chỉ số & Ngưỡng Heuristic:** Ngưỡng `data_status` (`no_data` = 0, `limited` < 3 bài khác nhau, `sufficient` >= 3 bài) và `autonomy_score` là quy ước vận hành sản phẩm, **không phải thang đo tâm trắc hay cutoff đã kiểm chứng giáo dục**.
- **Phase 17 Pilot:** Kết quả `evaluate_phase17_adaptive.py` là offline replay trên 6 fixture tổng hợp (không dùng LLM thật). Pilot 2–3 người **chưa chạy**, tuyệt đối không tuyên bố cải thiện learning gain hay hiệu quả thống kê; khi chạy pilot chỉ ghi quan sát mô tả.

#### E. Bẫy dữ liệu kiểm thử (`PYTUTOR_DB_PATH` & `PYTUTOR_KNOWLEDGE_DB_PATH`) — RẤT QUAN TRỌNG
- File `pytutor.db` ở thư mục gốc có chứa dữ liệu tích lũy từ các lần chạy demo/kiểm thử trước. **Tuyệt đối không xóa hay ghi đè phá dữ liệu `pytutor.db` gốc của người dùng nếu không được yêu cầu.**
- `backend/database.py` và `mcp_server/storage.py` đọc `PYTUTOR_DB_PATH` (mặc định `pytutor.db`), còn `backend/rag/retriever.py` đọc `PYTUTOR_KNOWLEDGE_DB_PATH` (mặc định `pytutor_knowledge.sqlite3`).
- Các test như `test_phase16_ai_upgrade.py` (chạy `init_db()` và `TestClient(app)` kích hoạt lifespan RAG ingestion), `test_phase17_adaptive_analytics.py` (ghi `phase17_synthetic_limited` vào `submissions`), `test_qa_authorization.py`, `test_phase15_3_qa_audit.py`, `test_phase15_4_action_buttons.py` đều đọc/ghi vào DB hiện hành nếu chưa đặt biến môi trường cô lập.
- **Luôn đặt cả `$env:PYTUTOR_DB_PATH` và `$env:PYTUTOR_KNOWLEDGE_DB_PATH`** trỏ tới file tạm trong `$env:TEMP` trước khi chạy test (và xóa file tạm + dọn biến môi trường sau khi xong).

---

### 4. KIỂM CHỨNG THỰC TẾ TRƯỚC KHI VIẾT `CLAUDE.md`

Hãy thực thi các lệnh kiểm chứng sau trong PowerShell (tại `C:\Users\Admin\Downloads\PyTutor-Thesis`) để xác nhận trạng thái thực tế của repo trên **DB tạm cô lập** mà không chạm vào `pytutor.db` hay `pytutor_knowledge.sqlite3` gốc:

```powershell
$env:PYTHONIOENCODING = "utf-8"
git status -s
py -m compileall -q backend mcp_server

$tmpDb = Join-Path $env:TEMP ("pytutor_check_" + [guid]::NewGuid().ToString("N") + ".db")
$tmpKb = Join-Path $env:TEMP ("pytutor_kb_" + [guid]::NewGuid().ToString("N") + ".sqlite3")
$env:PYTUTOR_DB_PATH = $tmpDb
$env:PYTUTOR_KNOWLEDGE_DB_PATH = $tmpKb
try {
    py -m unittest test_phase16_ai_upgrade test_phase17_adaptive_analytics test_qa_authorization -v
    py evaluate_phase17_adaptive.py
} finally {
    Remove-Item Env:PYTUTOR_DB_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:PYTUTOR_KNOWLEDGE_DB_PATH -ErrorAction SilentlyContinue
    Remove-Item $tmpDb, "$tmpDb-wal", "$tmpDb-shm", $tmpKb -Force -ErrorAction SilentlyContinue
}

Set-Location frontend; npm.cmd run test:theme; npm.cmd run build; Set-Location ..
```

---

### 5. YÊU CẦU ĐẦU RA: FILE `CLAUDE.md` HOÀN CHỈNH

Sau khi đọc xong các tài liệu/code ở Mục 2 và có kết quả kiểm chứng thực tế ở Mục 4, hãy tạo duy nhất file **`C:\Users\Admin\Downloads\PyTutor-Thesis\CLAUDE.md`** *(chưa cần tạo sẵn `.claude/rules/` hay `.claude/skills/` trong phiên onboarding này; tuân thủ nguyên tắc bắt đầu tối thiểu từ `docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md`)* đạt các tiêu chí sau:

1. **Ngắn gọn, mật độ thông tin cao, thực dụng (dưới ~200 dòng):** Viết bằng tiếng Việt chuẩn xác (giữ nguyên tên file, tên hàm, biến môi trường và lệnh shell). **Không** chép lại toàn bộ `AI_HANDOFF_CONTEXT.md` hay `docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md`; hãy tổng hợp thành điểm vào ngắn (bất biến + lệnh + quy trình + bản đồ chỉ đường) để tiết kiệm token cho mọi phiên sau.
2. **Cấu trúc tối thiểu cần có trong `CLAUDE.md`:**
   - **Tổng quan dự án & định danh đề tài NEU** (PyTutor-MCP, đường dẫn `PyTutor-Thesis`, trạng thái Phase 1–15.6 PASS, Phase 16 MVP, Phase 17 Technical MVP / Pilot pending).
   - **Lệnh phát triển & kiểm thử chuẩn Windows 11** (`py`, `npm.cmd`, `PYTHONIOENCODING=utf-8`, PowerShell `;`, `start_dev.bat`, compile/build/unittest/replay commands, và mẫu cô lập DB bằng `$env:PYTUTOR_DB_PATH` + `$env:PYTUTOR_KNOWLEDGE_DB_PATH`).
   - **Bản đồ kiến trúc, file trọng yếu & danh sách file không đọc mặc định** (`frontend/` – `backend/` – `mcp_server/` – `docs/` – `plans/`, 8 MCP tools, và hướng dẫn đọc có chọn lọc để tránh tốn token).
   - **Quy trình làm việc Claude Code** (Vertical slice, review bước nhạy cảm, UI check với Playwright khi sửa giao diện, bảo toàn worktree chưa commit, không bypass permissions, mock LLM mặc định, quy tắc session/model ngắn gọn).
   - **Các luật bất biến kỹ thuật, sư phạm & trung thực khoa học** (MCP stdio boundary, 3-button separation, 3-tier scaffolding + Anti-Spoil, non-escalating `select_hint_strategy`, EXAM Mode Guard, RBAC server-side / aggregate-only class chat, no hardcoded exercises, SQLite WAL `20.0s`, `SHOW_EXAM_SESSIONS = false`, `DESIGN.md`/`PRODUCT.md`, MCP là tool integration, RAG chưa có giáo trình NEU, heuristic cutoffs & pilot pending).
   - **Thông tin môi trường & tài khoản demo** (`.env.example`, `GEMINI_MODEL=gemini-3.5-flash-lite`, `PYTUTOR_DB_PATH`, `PYTUTOR_KNOWLEDGE_DB_PATH`, `student`, `gv_tran`, `gv_tuan`).
   - **Tra cứu nhanh theo loại tác vụ & lộ trình mở rộng `.claude/`** (bảng chỉ rõ sửa AI/RAG, analytics/adaptive, UI, hoặc tra lịch sử sâu ở mục nào của `AI_HANDOFF_CONTEXT.md`; ghi chú ngắn khi nào nên tách `.claude/rules/` và tạo skill `pytutor-phase-workflow` / `pytutor-qa`).
3. **Tính xác thực tuyệt đối:** Mọi đường dẫn file, tên symbol, lệnh test và kết quả kiểm chứng ghi trong `CLAUDE.md` và trong báo cáo trả lời đều phải khớp 100% với những gì bạn vừa trực tiếp đọc/chạy được trong repo.

Sau khi tạo xong `CLAUDE.md`, hãy báo cáo ngắn gọn cho tôi:
1. Kết quả kiểm chứng thực tế bạn vừa chạy (chỉ nêu đúng các lệnh đã chạy trên DB cô lập và số liệu thực tế).
2. Tóm tắt cấu trúc & số dòng của file `CLAUDE.md` đã tạo.
3. Các hạng mục còn mở (Phase 16/17, gợi ý plugin/skill tiếp theo theo `docs/CLAUDE_CODE_PYTUTOR_ADOPTION_GUIDE.md`) để tôi quyết định bước làm việc tiếp theo với bạn.

## [KẾT THÚC PROMPT GỬI CLAUDE]
