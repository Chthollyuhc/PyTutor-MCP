# 📋 PYTUTOR-MCP: MASTER IMPLEMENTATION DASHBOARD

> **Đồ án tốt nghiệp:** Hệ thống Gia sư Thông minh Hỗ trợ Học Lập trình Python Dựa trên Model Context Protocol (MCP)  
> **Sinh viên thực hiện:** Trần Khánh  
> **Repository:** [https://github.com/Chthollyuhc/PyTutor-MCP](https://github.com/Chthollyuhc/PyTutor-MCP)  
> **Phiên bản kiến trúc:** 2.0 (Modular Phased Architecture)

---

## 🏛️ TỔNG QUAN KIẾN TRÚC HỆ THỐNG

```text
[Sinh viên]
    │ Giao diện 3 cột chuẩn IDE (React 18 + Vite + Tailwind + Monaco Editor)
    ▼
[Backend: FastAPI (MCP Host & Orchestrator)]
    ├──► (1) Giao thức MCP (JSON-RPC 2.0 qua stdio) ──► [mcp_server: Sandbox & AST Analyzer]
    └──► (2) HTTP POST (Context Bundle + Prompt)   ──► [LLM: Qwen2.5-14B (Ollama Server)]
```

---

## 🗺️ BẢNG ĐIỀU KHIỂN TIẾN ĐỘ MODULAR (MASTER INDEX)

| Phase | Mã Kế hoạch | Phân hệ | Mục tiêu chính | Trạng thái | Chi tiết kế hoạch |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Phase 1** | `PLAN_1.0` | `mcp_server/` | MCP Server, Execution Sandbox (timeout 5s), AST Analyzer, 5 bài tập mẫu | ✅ **PASSED** | [Xem chi tiết](plans/PLAN_1.0_MCP_SERVER.md) |
| **Phase 2.1** | `PLAN_2.1` | `backend/` | MCP Client & Host Orchestrator, True Discovery (`tools/list`), Schemas | ✅ **PASSED** | [Xem chi tiết](plans/PLAN_2.1_MCP_CLIENT_HOST.md) |
| **Phase 2.2** | `PLAN_2.2` | `backend/` | Tích hợp Qwen2.5-14B API, Prompt Sư phạm 3 cấp độ (Scaffolding), Fallback | ✅ **PASSED** | [Xem chi tiết](plans/PLAN_2.2_QWEN_SCAFFOLDING.md) |
| **Phase 2.3** | `PLAN_2.3` | `backend/` | FastAPI REST API (`/api/submit`, `/api/exercises`, `/api/health`), Test E2E | ✅ **PASSED** | [Xem chi tiết](plans/PLAN_2.3_FASTAPI_E2E.md) |
| **Phase 3.1** | `PLAN_3.1` | `frontend/` | Setup Vite + React 18 + Tailwind, Layout 3 cột, ProblemPanel | ✅ **PASSED** | [Xem chi tiết](plans/PLAN_3.1_FRONTEND_LAYOUT.md) |
| **Phase 3.2** | `PLAN_3.2` | `frontend/` | Monaco Code Editor, Bảng Test Results trực quan, AI Tutor Chat Panel | ✅ **PASSED** | [Xem chi tiết](plans/PLAN_3.2_EDITOR_AND_TUTOR.md) |
| **Phase 4.0** | `PLAN_4.0` | `release/` | Tích hợp toàn hệ thống, script chạy 1-click (`start_dev`), hoàn thiện README | ✅ **PASSED** | [Xem chi tiết](plans/PLAN_4.0_RELEASE_AND_DEMO.md) |

---

## 📊 NHẬT KÝ THỰC THI (EXECUTION LOG)

| Thời gian | Hạng mục | Kết quả | Ghi chú |
| :--- | :--- | :---: | :--- |
| 14/10/2026 | Phase 1.0: MCP Server Core | ✅ 100% PASS | 8/8 test cases đạt chuẩn (AST, Sandbox, Handshake, Discovery) |
| 14/10/2026 | Modularize Planning Docs | ✅ DONE | Tạo 7 file kế hoạch chi tiết trong `plans/` |
| 14/10/2026 | Phase 1.1: Early Break Sandbox Patch | ✅ PASSED | Tối ưu dừng sớm khi gặp `TIMEOUT` (tiết kiệm thời gian) |
| 14/10/2026 | Phase 2.1: MCP Client & Schemas | ✅ PASSED | True Discovery `tools/list`, Pydantic models hoàn chỉnh |
| 14/10/2026 | Phase 2.2: Qwen Integration & Fallback | ✅ PASSED | Scaffolding Prompt 3 cấp độ + Anti-Spoil Guard + Fallback |
| 14/10/2026 | Phase 2.3: FastAPI E2E Integration | ✅ 100% PASS | 6/6 test cases E2E đạt chuẩn (Health, Submit, AST, Hint) |
| 14/10/2026 | Phase 3.1: Frontend Vite & Layout 3 Cột | ✅ PASSED | React 18 + Tailwind CSS + ProblemPanel + Header |
| 14/10/2026 | Phase 3.2: Monaco Editor & Tutor Panel | ✅ PASSED | Editor Python, Sandbox Results, Scaffolding Levels & Confetti |
| 14/10/2026 | Phase 4.0: One-Click Launch & Full Release | ✅ 100% READY | `start_dev.bat`, `start_dev.ps1`, `README.md` hoàn thiện |
