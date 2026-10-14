# 🚀 PLAN 2.3: FASTAPI REST API & END-TO-END VERIFICATION

> **Phân hệ:** `backend/`  
> **Trạng thái:** ✅ ĐÃ HOÀN THÀNH (100% Tests Passed)

---

## 🎯 1. Mục tiêu (Objective)
Xây dựng ứng dụng FastAPI hoàn chỉnh phục vụ làm cầu nối giữa Frontend với MCP Server và LLM Service. Viết script kiểm thử E2E tự động (`test_backend_e2e.py`) kiểm tra thông suốt luồng từ API endpoint qua MCP Server tới Qwen2.5-14B cho tất cả các tình huống.

---

## 🏗️ 2. Danh sách Endpoints API

| Phương thức | Endpoint | Mô tả | Nguồn dữ liệu |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Kiểm tra trạng thái hệ thống & danh sách MCP Tools khám phá được | `discover_tools()` |
| `GET` | `/api/exercises` | Danh sách bài tập tóm tắt | MCP Tool `get_exercise_list` |
| `GET` | `/api/exercises/{exercise_id}` | Chi tiết bài tập, mô tả đề bài và starter code | MCP Tool `get_exercise_details` |
| `POST` | `/api/submit` | Nộp bài/Xin gợi ý -> Chạy sandbox -> Phân tích AST -> Gọi AI Tutor | MCP Sandbox + AST + Qwen LLM |

---

## ✅ 3. Danh sách Công việc (Checklist)

- [x] Xây dựng `backend/main.py`:
  - [x] Cấu hình FastAPI app với metadata tiêu chuẩn.
  - [x] Bật `CORSMiddleware` (cho phép `http://localhost:5173`, `http://localhost:3000`...).
  - [x] Định nghĩa route `GET /api/health`.
  - [x] Định nghĩa route `GET /api/exercises`.
  - [x] Định nghĩa route `GET /api/exercises/{exercise_id}`.
  - [x] Định nghĩa route `POST /api/submit`:
    - [x] Nhận `SubmitRequest`: `exercise_id`, `code`, `hint_level`.
    - [x] Lấy test cases từ MCP Tool `get_exercise_details`.
    - [x] Gọi MCP Tool `run_test_cases` qua stdio.
    - [x] Gọi MCP Tool `analyze_code_ast` qua stdio.
    - [x] Gọi `llm_service.generate_tutor_hint(...)` truyền Context Bundle.
    - [x] Trả về `SubmitResponse` hoàn chỉnh.
- [x] Xây dựng `backend/test_backend_e2e.py`:
  - [x] Test 1: `GET /api/health` -> HTTP 200, phát hiện đủ 4 tools.
  - [x] Test 2: `GET /api/exercises` -> HTTP 200, trả về >= 5 bài tập.
  - [x] Test 3: `GET /api/exercises/ex_01_sum_1_to_n` -> HTTP 200, có starter_code và đề bài.
  - [x] Test 4: `POST /api/submit` với code sai logic ở cả 3 mức `hint_level = 1, 2, 3`.
  - [x] Test 5: `POST /api/submit` với code đúng 100% -> Kiểm tra AI chúc mừng và nhận xét tối ưu.
- [x] Chạy kiểm thử trên terminal và xác nhận 100% PASS.

---

## 📁 4. Danh sách File Đầu ra (Deliverables)
- `backend/main.py`
- `backend/test_backend_e2e.py`

---

## 🧪 5. Kịch bản Kiểm thử & Lệnh chạy (Verification)
```powershell
$env:PYTHONIOENCODING="utf-8"; py -m backend.test_backend_e2e
```
- **Tiêu chuẩn đạt (DoD):** Tất cả các bài test tích hợp E2E đều trả về mã HTTP 200, phản hồi đầy đủ trường dữ liệu, không có lỗi runtime.
