# 📋 PYTUTOR-MCP: MASTER IMPLEMENTATION PLAN

> **Dự án:** Hệ thống Gia sư Thông minh Hỗ trợ Học Lập trình Python Dựa trên Model Context Protocol (MCP)  
> **Sinh viên thực hiện:** Trần Khánh  
> **Repository:** https://github.com/Chthollyuhc/PyTutor-MCP  
> **Ngày khởi tạo:** 14/10/2026  
> **Trạng thái:** ĐANG TRIỂN KHAI (Phase 1 In Progress)

---

## 🏛️ 1. TỔNG QUAN KIẾN TRÚC & LUỒNG DỮ LIỆU

```text
[Sinh viên]
    │ (Tương tác trên giao diện 3 cột)
    ▼
[Frontend: React 18 + Vite + Tailwind CSS + Monaco Editor]
    │ HTTP REST (POST /api/submit, GET /api/exercises)
    ▼
[Backend: FastAPI + Uvicorn (MCP Host & Client)]
    ├──► (1) JSON-RPC 2.0 (stdio) ──► [MCP Server: Python Sandbox & AST Analyzer]
    └──► (2) HTTP POST           ──► [LLM: Qwen2.5-14B (Ollama Server 101.96.66.232)]
```

### Nguyên tắc thực thi:
1. **Zero-Hardcoding**: Backend kết nối MCP Server thông qua MCP Client tiêu chuẩn với cơ chế True Discovery (`tools/list`).
2. **Pedagogy-First**: AI không cung cấp trực tiếp code hoàn chỉnh, phân cấp gợi ý 3 mức độ (Level 1: Gợi mở Socratic, Level 2: Chẩn đoán lỗi, Level 3: Mã giả / Hướng dẫn từng bước).
3. **Fail-Safe & Sandbox**: Code sinh viên được thực thi độc lập với timeout 5 giây, bảo vệ tài nguyên hệ thống.
4. **Test-First Progression**: Mỗi phase chỉ hoàn tất khi test case tương ứng đạt 100% PASS.

---

## 📅 2. LỘ TRÌNH 4 GIAI ĐOẠN (PHASED ROADMAP)

```
[Phase 1: MCP Server Core] ──► [Phase 2: FastAPI Backend] ──► [Phase 3: Frontend UI] ──► [Phase 4: E2E Integration]
```

---

### 🚀 PHASE 1: THIẾT LẬP CẤU TRÚC DỰ ÁN & XÂY DỰNG MCP SERVER (`mcp_server/`)

- **Mục tiêu:** Xây dựng Execution Sandbox an toàn (timeout 5s), bộ phân tích tĩnh AST Python và đóng gói thành MCP Server chuẩn giao thức JSON-RPC 2.0 `stdio`.
- **Trạng thái:** ✅ ĐÃ HOÀN THÀNH (100% Tests Passed)

#### Danh sách công việc (Checklist):
- [x] Khởi tạo cấu trúc thư mục chuẩn (`mcp_server/`, `backend/`, `frontend/`) và `requirements.txt`.
- [x] Xây dựng `mcp_server/exercises_data.py`: Ngân hàng 5 bài tập Python mẫu kèm bộ test cases chuẩn.
- [x] Xây dựng `mcp_server/sandbox.py`: Bộ thực thi code an toàn qua subprocess độc lập, bắt timeout 5s, bắt runtime & syntax errors.
- [x] Xây dựng `mcp_server/ast_analyzer.py`: Bộ phân tích AST tĩnh (vòng lặp, đệ quy, biến accumulator, return, danh sách hàm).
- [x] Xây dựng `mcp_server/server.py`: MCP Server đăng ký các tools `run_test_cases` và `analyze_code_ast` bằng `mcp` SDK 2.2.0.
- [x] Viết script `mcp_server/test_mcp_server.py`: Kiểm thử tự động qua MCP Client thực sự (Code đúng, Code sai logic, Code lỗi cú pháp, Code lặp vô hạn `while True:`).
- [x] Chạy test, xác nhận PASS 100% và cập nhật tài liệu.

#### Đầu ra cụ thể (Deliverables):
- `requirements.txt`
- `mcp_server/__init__.py`
- `mcp_server/exercises_data.py`
- `mcp_server/sandbox.py`
- `mcp_server/ast_analyzer.py`
- `mcp_server/server.py`
- `mcp_server/test_mcp_server.py`

#### Kịch bản kiểm thử & Lệnh chạy:
```powershell
$env:PYTHONIOENCODING="utf-8"; py -m mcp_server.test_mcp_server
```
- **Tiêu chí hoàn thành (DoD):** Tất cả 4 kịch bản kiểm thử (Pass, Fail, Syntax Error, Timeout 5s) đều chạy thông suốt qua giao thức MCP stdio mà không xảy ra crash.

---

### ⚙️ PHASE 2: XÂY DỰNG FASTAPI BACKEND - MCP HOST & TÍCH HỢP QWEN2.5-14B (`backend/`)

- **Mục tiêu:** Xây dựng MCP Host đóng vai trò Orchestrator, kết nối MCP Server qua stdio và gọi Qwen2.5-14B API theo prompt sư phạm Scaffolding 3 cấp độ.
- **Trạng thái:** ⏸️ Chưa bắt đầu

#### Danh sách công việc (Checklist):
- [ ] Xây dựng `backend/schemas.py`: Định nghĩa Pydantic models cho Request/Response.
- [ ] Xây dựng `backend/mcp_client.py`: Quản lý subprocess `mcp_server`, thực hiện True Discovery (`tools/list`) và gọi Tool execution.
- [ ] Xây dựng `backend/llm_service.py`: Giao tiếp Qwen2.5-14B (`101.96.66.232:8037`), đóng gói Context Bundle, xây dựng System Prompt 3 mức độ và cơ chế fallback an toàn.
- [ ] Xây dựng `backend/main.py`: Khởi tạo FastAPI app, CORS, routes `/api/health`, `/api/exercises`, `/api/submit`.
- [ ] Xây dựng `backend/test_backend_e2e.py`: Kiểm thử tích hợp toàn bộ luồng Backend -> MCP -> Qwen LLM.
- [ ] Chạy kiểm thử E2E Backend và cập nhật `PLAN.md`.

#### Đầu ra cụ thể (Deliverables):
- `backend/__init__.py`
- `backend/schemas.py`
- `backend/mcp_client.py`
- `backend/llm_service.py`
- `backend/main.py`
- `backend/test_backend_e2e.py`

#### Kịch bản kiểm thử & Lệnh chạy:
```powershell
$env:PYTHONIOENCODING="utf-8"; py -m backend.test_backend_e2e
```
- **Tiêu chí hoàn thành (DoD):** Backend gọi thành công MCP tools, Qwen trả về gợi ý sư phạm hợp lệ không làm lộ lời giải cho cả 3 Level gợi ý.

---

### 🖥️ PHASE 3: XÂY DỰNG GIAO DIỆN 3 CỘT (REACT + VITE + TAILWIND + MONACO) (`frontend/`)

- **Mục tiêu:** Hiện thực hóa chính xác wireframe 3 cột của hệ thống: Đề bài (Trái), Monaco Editor & Test Results (Giữa), AI Tutor (Phải).
- **Trạng thái:** ⏸️ Chưa bắt đầu

#### Danh sách công việc (Checklist):
- [ ] Khởi tạo dự án Vite React bằng `npm.cmd`, cài đặt Tailwind CSS, `@monaco-editor/react`, `lucide-react`, `axios`.
- [ ] Xây dựng `frontend/src/services/api.js`: Module giao tiếp API với FastAPI Backend.
- [ ] Xây dựng `ProblemPanel.jsx`: Cột 1 - Danh sách bài tập, mô tả đề, ràng buộc, ví dụ I/O.
- [ ] Xây dựng `EditorPanel.jsx`: Cột 2 - Monaco Editor (Python syntax highlighting, đổi theme Dark/Light) + Bảng kết quả Test Cases (PASS/FAIL/TIMEOUT trực quan).
- [ ] Xây dựng `TutorPanel.jsx`: Cột 3 - Khung tương tác AI Tutor, chọn Hint Level (1, 2, 3), hiển thị nhận xét AST và câu trả lời sư phạm.
- [ ] Tích hợp `App.jsx` layout 3 cột responsive, thanh trạng thái kết nối MCP & Backend.
- [ ] Chạy `npm.cmd run build` kiểm tra bundling sạch sẽ, không lỗi cú pháp.

#### Đầu ra cụ thể (Deliverables):
- Toàn bộ source code `frontend/` hoàn chỉnh
- Bản build production kiểm thử thành công

#### Kịch bản kiểm thử & Lệnh chạy:
```powershell
cd frontend; npm.cmd run build
```
- **Tiêu chí hoàn thành (DoD):** Build thành công không có lỗi, giao diện 3 cột hiển thị mượt mà.

---

### 🎯 PHASE 4: TÍCH HỢP HỆ THỐNG, SCRIPT KHỞI CHẠY & HOÀN THIỆN ĐỒ ÁN

- **Mục tiêu:** Đóng gói toàn bộ hệ thống, viết script chạy một lệnh (`start_dev.bat` / `.ps1`), kiểm thử vòng lặp học tập E2E hoàn chỉnh.
- **Trạng thái:** ⏸️ Chưa bắt đầu

#### Danh sách công việc (Checklist):
- [ ] Tạo file cấu hình `start_dev.bat` và `start_dev.ps1` để khởi chạy đồng thời Backend và Frontend bằng 1 click.
- [ ] Cập nhật `README.md` với hướng dẫn cài đặt, kiến trúc, và các kịch bản demo cho Giảng viên hướng dẫn.
- [ ] Thực hiện bài test kiểm thử người dùng thực nghiệm trên 5 bài toán mẫu.
- [ ] Commit toàn bộ source code sạch lên GitHub repository.
- [ ] Cập nhật toàn bộ checklist `PLAN.md` thành `[x] ✅ PASSED`.

---

## 📊 NHẬT KÝ TIẾN ĐỘ THỰC TẾ (PROGRESS LOG)

| Thời gian | Module / Tác vụ | Trạng thái | Ghi chú |
| :--- | :--- | :--- | :--- |
| 14/10/2026 | Khởi tạo file PLAN.md | ✅ DONE | Bắt đầu thực thi Phase 1 |
| 14/10/2026 | Phase 1: MCP Server & Sandbox Core | ✅ PASSED (100%) | 8/8 test cases pass, chặn timeout 5s hoàn hảo |
| 14/10/2026 | Phase 2: FastAPI Backend & Qwen LLM | ⏳ READY | Chuẩn bị triển khai Phase 2 |
