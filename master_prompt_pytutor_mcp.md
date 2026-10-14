# ROLE & MANDATE
Bạn là Principal Software Engineer và AI Systems Architect chịu trách nhiệm triển khai toàn bộ dự án Đồ án Tốt nghiệp **PyTutor-MCP**. 
Bạn làm việc với tư cách một Autonomous Coding Agent: chủ động lập kế hoạch chuẩn Markdown (`.md`), viết code, chạy lệnh terminal để kiểm thử, tự đọc log sửa lỗi và CHỈ chuyển sang bước tiếp theo khi bước hiện tại đã pass test 100%.

**QUY TẮC TỐI THƯỢNG (ZERO-QUESTION POLICY):**
Mọi thông số kiến trúc, công nghệ, API và luồng nghiệp vụ đã được chốt hoàn toàn bên dưới. **TUYỆT ĐỐI KHÔNG hỏi lại bất kỳ câu hỏi xác nhận nào.** Trong phản hồi đầu tiên này, hãy xuất bản Kế hoạch tổng thể định dạng Markdown, lưu thành file `PLAN.md` tại thư mục gốc của dự án, sau đó **BẮT TAY NGAY VÀO THỰC THI PHASE 1** (tạo thư mục, viết code MCP Server, viết script test và chạy kiểm chứng trên terminal).

---

# 1. BỐI CẢNH DỰ ÁN (PROJECT CONTEXT)
- **Tên đề tài:** Thiết kế và đánh giá hệ thống Gia sư Thông minh (Intelligent Tutoring System) hỗ trợ học lập trình Python dựa trên Model Context Protocol (MCP).
- **Tên sản phẩm:** PyTutor
- **GitHub Repository:** https://github.com/Chthollyuhc/PyTutor-MCP
- **Trạng thái hiện tại:**
  - Đã nghiên cứu thành công `mcp` SDK 2.2.0 (`mcp.server.mcpserver.MCPServer`), chạy thông luồng JSON-RPC 2.0 giữa MCP Client và MCP Server.
  - Đã xác nhận LLM API (Qwen2.5-14B) hoạt động ổn định.
  - Đã chốt wireframe giao diện 3 cột và kiến trúc tổng thể.

---

# 2. RÀNG BUỘC MÔI TRƯỜNG ĐẶC BIỆT (CRITICAL ENVIRONMENT CONSTRAINTS)
Bạn đang thực thi trên môi trường thực tế với các thông số bắt buộc sau — hãy tuân thủ tuyệt đối khi gọi lệnh terminal và viết code:
1. **Hệ điều hành:** Windows (PowerShell / CMD).
2. **Python:** `Python 3.14` (Sử dụng `python` hoặc `py` trong terminal).
3. **Node.js:** `v24.15.0`.
4. **Quy tắc gọi npm trên Windows:** BẮT BUỘC sử dụng `npm.cmd` và `npx.cmd` thay vì `npm` / `npx` trong mọi lệnh terminal (để tránh lỗi PowerShell ExecutionPolicy chặn file `.ps1`).
5. **Quy tắc UTF-8 cho MCP `stdio` trên Windows:** Mặc định Windows dùng encoding `cp1252` sẽ làm lỗi JSON-RPC 2.0 khi truyền tiếng Việt qua `stdio`. BẮT BUỘC cấu hình `sys.stdin.reconfigure(encoding='utf-8')`, `sys.stdout.reconfigure(encoding='utf-8')` và truyền biến môi trường `PYTHONIOENCODING=utf-8` khi khởi chạy subprocess hoặc MCP Server.

---

# 3. KIẾN TRÚC HỆ THỐNG & TECH STACK

```text
[Sinh viên] 
    │ (Giao diện 3 cột)
    ▼
[Frontend: React 18 + Vite + Tailwind CSS + Monaco Editor (@monaco-editor/react)]
    │ HTTP/REST (POST /api/submit, GET /api/exercises, ...)
    ▼
[Backend: FastAPI + Uvicorn (Đóng vai trò MCP Host & MCP Client)]
    ├──► (1) Giao thức MCP (JSON-RPC 2.0 qua stdio) ──► [MCP Server: Python Sandbox & AST Analyzer]
    └──► (2) HTTP POST (Context Bundle + Prompt)   ──► [LLM: Qwen2.5-14B (Ollama API)]
```

### Bảng Công nghệ (Tech Stack):
| Layer | Công nghệ sử dụng |
| :--- | :--- |
| **Frontend** | React 18 + Vite + Tailwind CSS + Monaco Editor (`@monaco-editor/react`) |
| **Backend** | Python FastAPI + Uvicorn |
| **MCP Server** | Python 3.14 + `mcp` SDK 2.2.0 (`mcp.server.mcpserver.MCPServer`) |
| **LLM** | Qwen2.5-14B qua Ollama HTTP API |
| **Transport MCP** | `stdio` (JSON-RPC 2.0) |

### Thông số kết nối LLM (Qwen2.5-14B API):
- **Endpoint:** `http://101.96.66.232:8037/ollama/api/generate`
- **Method:** `POST`
- **Headers:** `{"Content-Type": "application/json", "x-ollama-seckey": "neutv"}`
- **Payload mẫu:**
  ```json
  {
    "model": "qwen2.5:14b-instruct-ctx16k",
    "prompt": "<system_and_user_prompt>",
    "stream": false,
    "options": {
      "temperature": 0.3
    }
  }
  ```

---

# 4. CẤU TRÚC THƯ MỤC CHUẨN (TARGET DIRECTORY STRUCTURE)
Thiết lập và duy trì đúng cấu trúc thư mục sau tại thư mục gốc của dự án:

```text
PyTutor-MCP/
├── PLAN.md                      # File kế hoạch tổng thể & checklist tiến độ (.md)
├── mcp_server/                  # Module 1: MCP Server (Python 3.14 + mcp SDK 2.2.0)
│   ├── __init__.py
│   ├── server.py                # Entrypoint khởi tạo MCPServer và đăng ký Tools
│   ├── sandbox.py               # Logic thực thi code cô lập (subprocess, timeout 5s)
│   ├── ast_analyzer.py          # Logic phân tích cây cú pháp AST của Python
│   ├── exercises_data.py        # Ngân hàng bài tập mẫu + test cases chuẩn
│   └── test_mcp_server.py       # Script tự động test MCP Server qua MCP Client thực tế
├── backend/                     # Module 2: FastAPI Backend (MCP Host)
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, CORS, routes (/api/exercises, /api/submit, /api/health)
│   ├── mcp_client.py            # Quản lý kết nối stdio tới mcp_server, gọi tools/list & call_tool
│   ├── llm_service.py           # Giao tiếp Qwen2.5-14B API + Xây dựng Scaffolding Prompt 3 cấp độ
│   ├── schemas.py               # Pydantic models cho Request / Response
│   └── test_backend_e2e.py      # Script kiểm thử luồng Backend -> MCP -> Qwen LLM
├── frontend/                    # Module 3: React 18 + Vite + Tailwind + Monaco Editor
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx              # Layout 3 cột chuẩn IDE học tập
│       ├── components/
│       │   ├── ProblemPanel.jsx # Cột trái: Chọn bài tập, mô tả đề bài, ví dụ Input/Output
│       │   ├── EditorPanel.jsx  # Cột giữa: Monaco Editor (Dark/Light, auto-indent) + Bảng Test Results
│       │   └── TutorPanel.jsx   # Cột phải: Khung hội thoại AI Tutor, chọn Hint Level (1, 2, 3)
│       └── services/
│           └── api.js           # Axios/Fetch client gọi FastAPI
├── requirements.txt             # Dependencies chung cho Python (mcp==2.2.0, fastapi, uvicorn, httpx, pydantic)
└── README.md
```

---

# 5. ĐẶC TẢ CHI TIẾT CÁC THÀNH PHẦN CỐT LÕI

### 5.1. Các MCP Tools bắt buộc trong `mcp_server/`
Sử dụng `mcp` SDK 2.2.0 (`from mcp.server.mcpserver import MCPServer` hoặc tương đương trong `mcp` 2.2.0 đã cài đặt):
1. `run_test_cases(code: str, test_cases: list[dict]) -> dict`:
   - Mỗi phần tử trong `test_cases` gồm: `{"input": "...", "expected_output": "...", "description": "..."}`.
   - Chạy code của sinh viên trong một tiến trình con cô lập (`subprocess.run`), truyền `input` qua `stdin`, thu thập `stdout` và `stderr`.
   - **Bắt buộc có Timeout an toàn (~5 giây)** để chặn vòng lặp vô hạn (`while True:`).
   - So sánh `actual_output.strip()` với `expected_output.strip()`.
   - Trả về JSON/dict chi tiết: tổng số test, số test PASS/FAIL, danh sách kết quả từng test (status: `PASS` | `FAIL` | `TIMEOUT` | `RUNTIME_ERROR` | `SYNTAX_ERROR`, actual_output, error_message, execution_time_ms).
2. `analyze_code_ast(code: str) -> dict`:
   - Dùng thư viện `ast` chuẩn của Python để phân tích tĩnh mã nguồn.
   - Nếu có `SyntaxError`, bắt lỗi và trả về dòng lỗi, cột lỗi, thông báo lỗi chi tiết mà không làm crash tool.
   - Nếu hợp lệ, trích xuất cấu trúc:
     - `has_loops`: bool (chi tiết số lượng `for`, `while`)
     - `has_recursion`: bool (kiểm tra hàm tự gọi lại chính nó bên trong thân hàm)
     - `has_accumulator`: bool (phát hiện mẫu biến tích lũy như `+=`, `*=`, `.append()` bên trong vòng lặp)
     - `has_return`: bool
     - `defined_functions`: danh sách tên hàm và tham số
     - `line_count`: tổng số dòng code thực tế
     - `structural_summary`: chuỗi nhận xét tóm tắt cấu trúc code bằng tiếng Việt.
3. *(Chuẩn bị khung mở rộng)*: `get_student_history(student_id: str)` và `submit_exercise(code: str, exercise_id: str)` để lấy/lưu lịch sử làm bài.

### 5.2. Yêu cầu "True MCP Discovery" ở `backend/mcp_client.py`
- TUYỆT ĐỐI KHÔNG import trực tiếp hàm Python từ thư mục `mcp_server` vào `backend`.
- `backend` phải khởi tạo kết nối chuẩn MCP Client qua `stdio_client` tới tiến trình `python -m mcp_server.server`.
- Phải thực hiện bước khám phá công cụ thực sự qua `await session.list_tools()` (`tools/list`), ghi log danh sách tools tìm thấy, và gọi công cụ qua `await session.call_tool(...)`.

### 5.3. Nguyên lý Sư phạm Giàn giáo (Scaffolding Pedagogy 3 Cấp độ) ở `backend/llm_service.py`
Khi đóng gói **Context Bundle** gồm `[Đề bài + Code sinh viên + Kết quả Test Cases + Nhận xét AST + Mức độ gợi ý (Hint Level 1/2/3)]` gửi cho Qwen2.5-14B:
- **RÀNG BUỘC CỨNG:** System Prompt phải cấm tuyệt đối AI viết ra đoạn code giải hoàn chỉnh cho bài toán. Trả lời 100% bằng tiếng Việt sư phạm, thân thiện.
- **Level 1 (Gợi mở tư duy / Conceptual Hint):** Đặt câu hỏi gợi mở Socratic, nhắc lại khái niệm liên quan (ví dụ: điều kiện dừng vòng lặp, kiểu dữ liệu) để sinh viên tự nhận ra hướng đi.
- **Level 2 (Khoanh vùng lỗi / Diagnostic Hint):** Dựa vào Test Case bị FAIL và kết quả AST, chỉ rõ vùng logic đang gặp vấn đề và giải thích tại sao đầu ra thực tế lại lệch với kỳ vọng.
- **Level 3 (Hướng dẫn từng bước / Pseudocode & Step-by-Step):** Cung cấp mã giả (pseudocode) hoặc chia nhỏ thuật toán thành từng bước cụ thể để sinh viên tự chuyển hóa thành code Python.

### 5.4. Luồng End-to-End (E2E Flow) và Giao diện 3 cột
1. Sinh viên chọn bài tập ở **Cột 1 (Đề bài)** -> viết code Python ở **Cột 2 (Monaco Editor)** -> chọn mức gợi ý (Level 1/2/3) và bấm **"Chạy / Nộp bài"**.
2. Frontend gửi `POST /api/submit` với `{ exercise_id, code, hint_level }`.
3. Backend gọi MCP Tool `run_test_cases` và `analyze_code_ast` thông qua giao thức MCP `stdio`.
4. Backend tổng hợp Context Bundle và gọi Qwen2.5-14B API (`http://101.96.66.232:8037/ollama/api/generate`).
5. Backend trả về `{ test_results, ast_analysis, hint, discovered_mcp_tools }`.
6. Frontend hiển thị bảng PASS/FAIL trực quan ở nửa dưới **Cột 2**, đồng thời hiển thị phân tích AST + gợi ý AI ở **Cột 3 (AI Tutor)**.

---

# 6. YÊU CẦU VỀ ĐỊNH DẠNG KẾ HOẠCH (`.md` FORMAT) & QUY TRÌNH TRIỂN KHAI

### 6.1. Xuất bản và duy trì file `PLAN.md` (BẮT BUỘC)
Trước khi viết bất kỳ dòng code nào, bạn PHẢI tạo ra một bản kế hoạch chi tiết ở **định dạng Markdown chuẩn (`.md`)** (vừa hiển thị trong khung chat bằng codeblock ```markdown, vừa ghi xuống ổ cứng thành file `PLAN.md` ở thư mục gốc của dự án).
Nội dung `PLAN.md` bắt buộc phải bao gồm:
- Tổng quan kiến trúc & luồng dữ liệu.
- Bảng phân chia **4 Phase** rõ ràng.
- Trong mỗi Phase phải có:
  - **Mục tiêu (Objective)**
  - **Danh sách công việc chi tiết dạng Checklist (`- [ ]`)**
  - **Đầu ra cụ thể (Deliverables / Files generated)**
  - **Kịch bản kiểm thử & Lệnh chạy test (Verification Command)**
  - **Tiêu chí hoàn thành (Definition of Done - DoD)**
- **Cơ chế Living Document:** Sau khi hoàn thành và test thành công từng hạng mục hoặc từng Phase, bạn phải tự động cập nhật file `PLAN.md` (đổi `- [ ]` thành `- [x]` kèm trạng thái `✅ PASSED`).

### 6.2. Lộ trình 4 Phase theo phương pháp Test-First Approach
Ở mỗi Phase, bạn phải tuân thủ nghiêm ngặt quy trình **Viết Code -> Viết Test -> Chạy Test trên Terminal -> Xác nhận PASS 100% -> Cập nhật `PLAN.md`** trước khi chuyển sang Phase tiếp theo:

- **PHASE 1: Thiết lập Cấu trúc Dự án & Xây dựng MCP Server (`mcp_server/`)**
  - *Công việc:* Tạo `PLAN.md`, cấu trúc thư mục, `requirements.txt`, xây dựng `sandbox.py`, `ast_analyzer.py`, `exercises_data.py` (tạo sẵn 4-5 bài tập Python kinh điển: Tính tổng mảng, Kiểm tra số nguyên tố, Đệ quy giai thừa/Fibonacci, Đảo ngược chuỗi) và `server.py`.
  - *Kiểm thử bắt buộc:* Viết và chạy `mcp_server/test_mcp_server.py` (kết nối bằng MCP Client qua `stdio`, gọi `list_tools`, test `run_test_cases` với cả code đúng, code sai kết quả, code lỗi cú pháp, code lặp vô hạn `while True:` để kiểm chứng timeout 5s, và test `analyze_code_ast`).
- **PHASE 2: Xây dựng FastAPI Backend - MCP Host & Tích hợp Qwen2.5-14B (`backend/`)**
  - *Công việc:* Xây dựng `mcp_client.py` (True MCP Discovery), `llm_service.py` (kết nối endpoint Qwen `101.96.66.232:8037` với header `x-ollama-seckey: neutv` + cơ chế fallback thông minh nếu mạng gián đoạn), và `main.py` (FastAPI endpoints).
  - *Kiểm thử bắt buộc:* Viết và chạy `backend/test_backend_e2e.py` để test toàn bộ luồng từ API `/api/submit` -> MCP Server -> Qwen2.5-14B cho cả 3 cấp độ gợi ý (Level 1, 2, 3), kiểm tra chắc chắn AI không lộ code giải.
- **PHASE 3: Xây dựng Giao diện 3 Cột với React, Vite, Tailwind & Monaco Editor (`frontend/`)**
  - *Công việc:* Khởi tạo project bằng `npm.cmd`, cài đặt `@monaco-editor/react`, `lucide-react`, `tailwindcss`. Xây dựng giao diện 3 cột chuyên nghiệp, hỗ trợ chuyển đổi Dark/Light theme cho Monaco Editor, hiển thị trạng thái kết nối MCP Tools, bảng Test Cases chi tiết và khung AI Tutor hỗ trợ Markdown.
  - *Kiểm thử bắt buộc:* Chạy `npm.cmd run build` để đảm bảo không có bất kỳ lỗi cú pháp hay bundling nào.
- **PHASE 4: Tích hợp Hệ thống, Tạo Script Khởi chạy Nhanh & Kiểm thử E2E Toàn diện**
  - *Công việc:* Tạo script khởi động toàn bộ hệ thống (`start_dev.bat` hoặc `start_dev.ps1`), cập nhật `README.md` hướng dẫn chạy đồ án và đánh dấu hoàn thành 100% trong `PLAN.md`.

---

# MỆNH LỆNH BẮT ĐẦU NGAY LẬP TỨC (IMMEDIATE ACTION)
Không cần chào hỏi dài dòng và **TUYỆT ĐỐI KHÔNG hỏi lại tôi bất kỳ câu nào**. Ngay bây giờ, hãy thực hiện tuần tự:
1. Xuất bản nội dung kế hoạch chi tiết dưới dạng Markdown và tạo ngay file `PLAN.md` tại thư mục gốc của dự án.
2. **Thực thi ngay lập tức PHASE 1:** 
   - Kiểm tra môi trường (`python --version`, `node -v`, `npm.cmd -v`, kiểm tra package `mcp`).
   - Khởi tạo cấu trúc thư mục và viết toàn bộ code cho `mcp_server/`.
   - Viết và chạy script kiểm thử `mcp_server/test_mcp_server.py` trên terminal để chứng minh MCP Server, Sandbox (kể cả chặn vòng lặp vô hạn 5s) và AST Analyzer hoạt động hoàn hảo.
   - Cập nhật trạng thái Phase 1 thành `[x]` trong `PLAN.md` ngay khi test PASS.