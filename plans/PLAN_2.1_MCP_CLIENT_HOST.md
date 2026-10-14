# 🔌 PLAN 2.1: MCP CLIENT & HOST ORCHESTRATION LAYER

> **Phân hệ:** `backend/`  
> **Trạng thái:** ✅ ĐÃ HOÀN THÀNH (100% Tests Passed)

---

## 🎯 1. Mục tiêu (Objective)
Xây dựng MCP Client tiêu chuẩn cho FastAPI Backend đóng vai trò MCP Host. Module này kết nối tới `mcp_server.server` qua giao thức `stdio`, thực hiện cơ chế **True MCP Discovery** (`tools/list`) động tại runtime và cung cấp giao diện async để gọi các Tools phục vụ các route API mà KHÔNG import trực tiếp bất kỳ hàm logic nào từ `mcp_server`.

---

## 🏗️ 2. Kiến trúc Kỹ thuật (Technical Architecture)

```text
FastAPI Endpoints (main.py)
       │
       ▼
[backend/mcp_client.py: PyTutorMCPClient]
       │
       ├──► StdioServerParameters (python -m mcp_server.server)
       ├──► stdio_client() & ClientSession
       │
       ├──► discover_tools() ──► session.list_tools() [True MCP Discovery]
       ├──► get_exercise_list() ──► session.call_tool("get_exercise_list")
       ├──► get_exercise_details() ──► session.call_tool("get_exercise_details")
       ├──► run_test_cases() ──► session.call_tool("run_test_cases")
       └──► analyze_code_ast() ──► session.call_tool("analyze_code_ast")
```

---

## ✅ 3. Danh sách Công việc (Checklist)

- [x] Tạo `backend/__init__.py`.
- [x] Xây dựng `backend/schemas.py`:
  - [x] `TestCase`: `input`, `expected_output`, `description`.
  - [x] `TestResultItem`: `test_idx`, `description`, `input`, `expected_output`, `actual_output`, `status`, `error_message`, `execution_time_ms`.
  - [x] `TestResults`: `total_tests`, `passed_tests`, `failed_tests`, `all_passed`, `summary`, `results`.
  - [x] `ASTAnalysis`: `valid`, `line_count`, `has_loops`, `has_recursion`, `has_accumulator`, `defined_functions`, `observations`, `structural_summary`.
  - [x] `SubmitRequest`: `exercise_id`, `code`, `hint_level` (1..3).
  - [x] `SubmitResponse`: `exercise_id`, `test_results`, `ast_analysis`, `tutor_hint`, `hint_level`, `discovered_mcp_tools`, `llm_source`.
  - [x] `ExerciseSummary` & `ExerciseDetail`.
- [x] Xây dựng `backend/mcp_client.py`:
  - [x] Thiết lập kết nối subprocess `stdio_client` với biến môi trường UTF-8.
  - [x] Triển khai `discover_tools()` đọc danh sách tools thực tế từ MCP Server.
  - [x] Triển khai các hàm wrapper bất đồng bộ gọi từng MCP Tool an toàn (`get_exercise_list`, `get_exercise_details`, `run_test_cases`, `analyze_code_ast`, `execute_submission_pipeline`).

---

## 📁 4. Danh sách File Đầu ra (Deliverables)
- `backend/__init__.py`
- `backend/schemas.py`
- `backend/mcp_client.py`

---

## 🧪 5. Kịch bản Kiểm thử & Tiêu chuẩn Đạt (DoD)
- Gọi được `discover_tools()` và nhận về đủ 4 tools: `run_test_cases`, `analyze_code_ast`, `get_exercise_list`, `get_exercise_details`.
- Không có bất kỳ dòng `import mcp_server...` nào trong `backend/mcp_client.py`.
- Toàn bộ tham số và kết quả trả về khớp hoàn toàn với Pydantic Schemas.
