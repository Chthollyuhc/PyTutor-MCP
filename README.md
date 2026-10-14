# 🎓 PyTutor: Intelligent Tutoring System with Model Context Protocol (MCP)

> **Đồ án Tốt nghiệp:** Hệ thống Gia sư Thông minh Hỗ trợ Học Lập trình Python Dựa trên Giao thức Model Context Protocol (MCP)  
> **Sinh viên thực hiện:** Trần Khánh  
> **GitHub Repository:** [https://github.com/Chthollyuhc/PyTutor-MCP](https://github.com/Chthollyuhc/PyTutor-MCP)  
> **Phiên bản:** 2.0 (Full-Stack 3-Column IDE với True MCP Discovery)

---

## 📖 Giới thiệu (Overview)

**PyTutor** là hệ thống gia sư AI thông minh chuyên sâu hỗ trợ học sinh, sinh viên rèn luyện tư duy lập trình Python. Khác biệt cốt lõi của PyTutor so với các chatbot AI thông thường (chỉ suy đoán văn bản và dễ bị ảo giác) là **việc tích hợp Model Context Protocol (MCP)** – tiêu chuẩn công nghiệp mở do Anthropic và Linux Foundation bảo trợ.

Hệ thống kết nối trực tiếp mô hình ngôn ngữ lớn (**Qwen2.5-14B**) với môi trường thực thi hộp cát (**Python Execution Sandbox**) và bộ phân tích cú pháp tĩnh (**AST Inspector**) qua giao thức JSON-RPC 2.0 `stdio`. AI luôn nhận được **Bằng chứng Thực tế (Ground Truth)** trước khi đưa ra phản hồi, kết hợp phương pháp sư phạm giàn giáo (**Scaffolding Pedagogy**) 3 cấp độ gợi ý, hoàn toàn không tiết lộ lời giải sẵn.

---

## 🏗️ Kiến trúc Tổng thể Hệ thống (Architecture)

```text
┌────────────────────────────────────────────────────────────────────────┐
│               GIAO DIỆN HỌC VIÊN (REACT 18 + VITE + TAILWIND)          │
│                                                                        │
│  ┌──────────────────┬─────────────────────────────┬─────────────────┐  │
│  │   CỘT 1 (ĐỀ BÀI)  │     CỘT 2 (MONACO EDITOR)   │ CỘT 3 (AI TUTOR)│  │
│  │ • 5 Bài tập mẫu  │ • Python syntax highlighting│ • Hint Level 1-3│  │
│  │ • Input/Output   │ • Chạy & Nộp bài            │ • Thẻ AST MCP   │  │
│  │ • Mục tiêu học   │ • Bảng Test Cases PASS/FAIL │ • Lời khuyên AI │  │
│  └──────────────────┴──────────────┬──────────────┴─────────────────┘  │
└────────────────────────────────────┼───────────────────────────────────┘
                                     │ HTTP REST (/api/submit, /api/health)
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│             BACKEND FASTAPI (MCP HOST & ORCHESTRATOR)                  │
│                                                                        │
│  • Quản lý True MCP Discovery (tools/list) qua stdio_client            │
│  • Đóng gói Context Bundle: [Đề bài + Code + Sandbox Test + AST]       │
│  • Bộ lọc hậu kiểm chống lộ lời giải (Anti-Spoil Guard)                │
│  • Bộ tạo gợi ý sư phạm dự phòng (Rule-based Fallback)                │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
    JSON-RPC 2.0   │                                 │ HTTP POST
    (stdio pipe)   │                                 │ (Context Bundle)
                   ▼                                 ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│         MCP SERVER PYTHON 3.14       │  │   LLM: QWEN2.5-14B (OLLAMA)  │
│  (PyTutor Code Execution Engine)     │  │   Endpoint: 101.96.66.232    │
│                                      │  │   Header: x-ollama-seckey    │
│  🛠️ run_test_cases (Timeout 5.0s)    │  │                              │
│  🛠️ analyze_code_ast (AST Inspector) │  │  🧠 Gợi mở Socratic (Lv 1)   │
│  🛠️ get_exercise_list                │  │  🔍 Chẩn đoán lỗi (Lv 2)     │
│  🛠️ get_exercise_details             │  │  📘 Mã giả từng bước (Lv 3) │
└──────────────────────────────────────┘  └──────────────────────────────┘
```

---

## 💡 Phương Pháp Sư Phạm Giàn Giáo 3 Cấp Độ (Scaffolding Pedagogy)

1. **Level 1 — Gợi mở Socratic (Conceptual Hint):**
   - Đặt câu hỏi định hướng tư duy và nhắc lại khái niệm lập trình liên quan.
   - *Ràng buộc:* Tuyệt đối không chỉ ra vị trí lỗi và không viết bất kỳ code nào.
2. **Level 2 — Chẩn đoán & Khoanh vùng lỗi (Diagnostic Hint):**
   - Đối chiếu giữa Actual Output và Expected Output của Test Case bị `FAIL`.
   - Khoanh vùng khối lệnh đang có vấn đề logic và giải thích nguyên nhân.
3. **Level 3 — Hướng dẫn từng bước & Mã giả (Step-by-Step & Pseudocode):**
   - Chia nhỏ thuật toán thành các bước (Bước 1, Bước 2...).
   - Cung cấp mã giả (pseudocode), tuyệt đối không đưa code giải Python hoàn chỉnh.
4. **Khi đạt 100% Test Cases:**
   - Bắn pháo giấy chúc mừng (`canvas-confetti`).
   - AI nhận xét cấu trúc code dựa trên AST và hướng dẫn cách tối ưu theo phong cách Pythonic.

---

## ⚡ Khởi Chạy Nhanh Dự Án (Quickstart)

### Yêu cầu hệ thống:
* **Hệ điều hành:** Windows 10/11
* **Python:** 3.10+ (Đã kiểm thử trên Python 3.14)
* **Node.js:** v18+ (Đã kiểm thử trên Node.js v24.15.0)

### 1. Cài đặt Dependencies (Chỉ chạy 1 lần đầu)
```powershell
# Cài đặt Python packages cho Backend & MCP Server
py -m pip install -r requirements.txt

# Cài đặt Node modules cho Frontend
cd frontend
npm.cmd install
cd ..
```

### 2. Khởi chạy 1-Click (Khuyên dùng)
Bạn chỉ cần nhấp đúp vào file:
👉 **`start_dev.bat`** (hoặc chạy `./start_dev.ps1` trong PowerShell)

Hệ thống sẽ tự động bật đồng thời cả Backend và Frontend:
* 🌐 **Giao diện Học viên:** [http://localhost:5173](http://localhost:5173)
* 📑 **Tài liệu Backend API (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* 🔍 **Kiểm tra True MCP Discovery:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 🎬 Kịch Bản Demo Cho Buổi Bảo Vệ Đồ Án (Presentation Scenarios)

### Kịch bản 1: Code Đúng 100% (Tính tổng 1..n)
- **Code nhập vào:**
  ```python
  n = int(input())
  tong = 0
  for i in range(1, n + 1):
      tong += i
  print(tong)
  ```
- **Hiện tượng:** Cả 5/5 test cases xanh lá `PASS`. Màn hình bắn pháo giấy chúc mừng. AI Tutor chúc mừng và nhận xét phong cách sử dụng biến tích lũy và vòng lặp.

### Kịch bản 2: Code Sai Logic (Thử nghiệm 3 mức gợi ý)
- **Code nhập vào:**
  ```python
  n = int(input())
  print(n * 2)  # Sai logic
  ```
- **Hiện tượng:**
  - Chọn **Level 1**: AI Tutor đặt câu hỏi gợi mở về công thức tính tổng và biến tích lũy.
  - Chọn **Level 2**: AI Tutor chỉ rõ với Input=3, kết quả in ra là 6 nhưng với Input=5 kết quả in ra là 10 (kỳ vọng 15).
  - Chọn **Level 3**: AI Tutor cung cấp mã giả 4 bước để sinh viên tự hoàn thiện.

### Kịch bản 3: Chống Vòng Lặp Vô Hạn (An Toàn Sandbox)
- **Code nhập vào:**
  ```python
  n = int(input())
  while True:
      pass
  ```
- **Hiện tượng:** Sau đúng 5.0 giây, hệ thống ngắt tiến trình an toàn, hiển thị trạng thái `TIMEOUT (Time Limit Exceeded > 5.0s)`, các test sau tự động `SKIPPED`, server không hề bị đơ hay crash.

### Kịch bản 4: Bắt Lỗi Cú Pháp Tĩnh Bằng AST
- **Code nhập vào:**
  ```python
  n = int(input())
  for i in range(1, n + 1)   # Thiếu dấu hai chấm :
      print(i)
  ```
- **Hiện tượng:** Thẻ MCP AST Inspector lập tức báo `Lỗi cú pháp: expected ':' tại dòng 3`. AI Tutor hướng dẫn sinh viên bổ sung dấu hai chấm trước khi chạy kiểm thử logic.

---

## 🧪 Kiểm Thử Tự Động Toàn Diện (Automated Test Suites)

Hệ thống được xây dựng theo phương pháp **Test-First Approach** với 100% test cases pass:

```powershell
# 1. Kiểm thử Phân hệ 1: MCP Server Core, Sandbox & AST
$env:PYTHONIOENCODING="utf-8"; py -m mcp_server.test_mcp_server

# 2. Kiểm thử Phân hệ 2: FastAPI Backend E2E & True Discovery
$env:PYTHONIOENCODING="utf-8"; py -m backend.test_backend_e2e

# 3. Kiểm thử Phân hệ 3: Đóng gói Production Frontend
cd frontend; npm.cmd run build
```

---

## 📂 Cấu trúc Thư mục Dự Án (Repository Structure)

```text
PyTutor-MCP/
├── start_dev.bat               # Script khởi chạy 1-click Windows Batch
├── start_dev.ps1               # Script khởi chạy PowerShell
├── PLAN.md                     # Master Implementation Dashboard
├── requirements.txt            # Python dependencies (mcp, fastapi, uvicorn, httpx)
├── README.md                   # Tài liệu hướng dẫn đồ án
│
├── plans/                      # 7 File kế hoạch chi tiết từng phân hệ
│   ├── PLAN_1.0_MCP_SERVER.md
│   ├── PLAN_2.1_MCP_CLIENT_HOST.md
│   ├── PLAN_2.2_QWEN_SCAFFOLDING.md
│   ├── PLAN_2.3_FASTAPI_E2E.md
│   ├── PLAN_3.1_FRONTEND_LAYOUT.md
│   ├── PLAN_3.2_EDITOR_AND_TUTOR.md
│   └── PLAN_4.0_RELEASE_AND_DEMO.md
│
├── mcp_server/                 # MODULE 1: MCP Server (JSON-RPC 2.0 stdio)
│   ├── server.py               # MCPServer entrypoint đăng ký 4 tools
│   ├── sandbox.py              # Sandbox thực thi cô lập (timeout 5s + early break)
│   ├── ast_analyzer.py         # Bộ phân tích tĩnh cây cú pháp AST
│   ├── exercises_data.py       # Ngân hàng 5 bài tập Python mẫu
│   └── test_mcp_server.py      # Bộ test tự động Phase 1
│
├── backend/                    # MODULE 2: FastAPI Backend (MCP Host & Orchestrator)
│   ├── main.py                 # REST API endpoints (/api/submit, /api/health)
│   ├── mcp_client.py           # True MCP Discovery qua stdio_client
│   ├── llm_service.py          # Kết nối Qwen2.5-14B + Scaffolding Pedagogy + Fallback
│   ├── schemas.py              # Pydantic v2 Models
│   └── test_backend_e2e.py     # Bộ test tự động Phase 2
│
├── frontend/                   # MODULE 3: React 18 + Vite + Tailwind + Monaco Editor
│   ├── package.json
│   ├── vite.config.js          # Config server & proxy /api
│   ├── tailwind.config.js
│   └── src/
│       ├── App.jsx             # Layout 3 cột hoàn chỉnh + Confetti
│       ├── components/
│       │   ├── Header.jsx      # Top bar & MCP Tools Discovery Badges
│       │   ├── ProblemPanel.jsx# Cột 1: Đề bài, ví dụ I/O, Test cases
│       │   ├── EditorPanel.jsx # Cột 2: Monaco Editor & Bảng Test Results
│       │   └── TutorPanel.jsx  # Cột 3: Hint Level 1-3, AST card, AI chat
│       └── services/
│           └── api.js          # Axios API Client
│
└── docs/                       # Tài liệu nghiên cứu, báo cáo Word và Wireframe
    ├── reports/                # Báo cáo học thuật chi tiết
    └── wireframe/              # Bản vẽ kiến trúc wireframe chuẩn
```

---

*Đồ án tốt nghiệp chuyên ngành Công nghệ Thông tin.*
