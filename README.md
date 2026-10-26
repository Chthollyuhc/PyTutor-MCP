<div align="center">

# 🎓 PyTutor-MCP: Intelligent Tutoring System
### Hệ thống Gia sư Thông minh Hỗ trợ Học Lập trình Python Dựa trên Giao thức Model Context Protocol (MCP)

[![Python Version](https://img.shields.io/badge/Python-3.14%20%7C%203.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Model Context Protocol](https://img.shields.io/badge/Protocol-Anthropic%20MCP%202.2.0-orange?logo=anthropic&logoColor=white)](https://modelcontextprotocol.io/)
[![Google Gemini](https://img.shields.io/badge/AI%20Model-Gemini%203.5%20Flash%20Lite-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![University](https://img.shields.io/badge/NEU-Khoa%20CNTT-red?logo=bookstack&logoColor=white)](https://lms.neu.edu.vn/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Release-v5.0%20Pro%20(Defense--Ready)-success)](https://github.com/Chthollyuhc/PyTutor-MCP)

<br/>

> **Đồ án Tốt nghiệp Đại học Ngành Công nghệ Thông tin**  
> **Trường Đại học Kinh tế Quốc dân (NEU) — Khoa Công nghệ thông tin**  
> **Sinh viên thực hiện:** **Trần Minh Khánh** (Sinh viên Khóa K65 CNTT — MSV: `11236131`)  
> **Giảng viên hướng dẫn:** Thầy **Nguyễn Văn A** & Thầy **Trần Văn B**  
> **Kho lưu trữ chính thức:** [https://github.com/Chthollyuhc/PyTutor-MCP](https://github.com/Chthollyuhc/PyTutor-MCP)  
> **Báo cáo Thực nghiệm Khoa học:** [`docs/EVALUATION_REPORT.md`](docs/EVALUATION_REPORT.md)

</div>

---

## 📑 Mục lục (Table of Contents)

- [1. Giới thiệu Tổng quan & Vấn đề Cốt lõi](#-1-giới-thiệu-tổng-quan--vấn-đề-cốt-lõi)
- [2. Kiến trúc Tổng thể Hệ thống (Architecture)](#-2-kiến-trúc-tổng-thể-hệ-thống-architecture)
- [3. Tính Năng Nổi Bật (Key Features)](#-3-tính-năng-nổi-bật-key-features)
  - [3.1. Kiến trúc Đa tầng LMS & IDE](#31-kiến-trúc-điều-hướng-đa-tầng-multi-stage-lms--ide)
  - [3.2. Danh mục 8 Công cụ Chuẩn MCP](#32-danh-mục-8-công-cụ-chuẩn-model-context-protocol-mcp)
  - [3.3. Quy trình 3 Nút Độc Lập](#33-quy-trình-3-hành-động-độc-lập-trên-ide)
  - [3.4. Sư phạm Giàn giáo 3 Cấp độ & Anti-Spoil Guard](#34-phương-pháp-sư-phạm-giàn-giáo-3-cấp-độ--anti-spoil-guard)
  - [3.5. Gamification, Chuẩn sao & Hồ sơ Năng lực 4D](#35-gamification-chuẩn-sao-mastery-rubric--hồ-sơ-năng-lực-4d)
  - [3.6. Công cụ Trực quan hóa Visualizer & Review Pythonic](#36-công-cụ-trực-quan-hóa-visualizer--review-chuẩn-pythonic)
- [4. Tài khoản Đăng nhập Demo](#-4-tài-khoản-đăng-nhập-demo-hội-đồng-chấm-đồ-án)
- [5. Hướng dẫn Cài đặt & Khởi chạy Nhanh](#-5-hướng-dẫn-cài-đặt--khởi-chạy-nhanh-quickstart)
  - [5.1. Yêu cầu Hệ thống](#51-yêu-cầu-hệ-thống)
  - [5.2. Cài đặt Môi trường](#52-cài-đặt-môi-trường-thủ-công)
  - [5.3. Khởi chạy 1-Click](#53-khởi-chạy-1-click-tự-động)
- [6. Cấu trúc Thư mục Dự án](#-6-cấu-trúc-thư-mục-dự-án-project-structure)
- [7. Danh mục API Chính (REST Endpoints)](#-7-danh-mục-api-chính-rest-endpoints)
- [8. Kịch bản 5 Bước Trình Diễn Trước Hội Đồng](#-8-kịch-bản-5-bước-trình-diễn-trước-hội-đồng-defense-demo-script)
- [9. Đánh Giá Thực Nghiệm Khoa Học](#-9-đánh-giá-thực-nghiệm-khoa-học-academic-benchmark)
- [10. Bản quyền & Đóng góp](#-10-bản-quyền--đóng-góp-license--credits)

---

## 📖 1. Giới thiệu Tổng quan & Vấn đề Cốt lõi

### 1.1. Bối cảnh & Vấn đề Cốt tử của AI truyền thống trong Giáo dục Lập trình
Trong kỷ nguyên Generative AI, phần lớn sinh viên sử dụng ChatGPT hoặc GitHub Copilot để hỏi bài tập lập trình. Tuy nhiên, các mô hình ngôn ngữ lớn (LLM) thông thường khi hoạt động độc lập mắc phải **4 vấn đề nghiêm trọng**:
1. **Ảo giác Kết quả (Hallucination - Thiếu Ground Truth):** LLM sinh từ theo xác suất thống kê chứ không phải trình thông dịch (Interpreter). Khi phân tích một đoạn mã phức tạp có vòng lặp lồng nhau hoặc xử lý mảng biên, AI đoán sai kết quả từ 35% - 45%, dẫn đến giải thích sai lệch cho sinh viên.
2. **Hiểm họa Sập Máy Chủ (Process Crashing):** Nếu máy chủ web chạy mã nguồn sinh viên trực tiếp bằng `exec()` hay `eval()`, một vòng lặp vô hạn `while True:` hoặc đệ quy tràn bộ nhớ sẽ làm treo cứng toàn bộ dịch vụ.
3. **Mất Trí Nhớ Sư Phạm (Stateless Amnesia):** AI thông thường quên tiến trình làm bài của sinh viên ngay sau lượt hỏi, lặp lại những câu hỏi chung chung làm người học mất kiên nhẫn.
4. **Hành vi Giải Hộ Code (Spoiling):** Thay vì dẫn dắt người học tư duy giải thuật, AI thường viết luôn mã giải hoàn chỉnh, triệt tiêu động lực và năng lực tư duy lập trình độc lập của sinh viên.

### 1.2. Giải pháp Đột phá: PyTutor-MCP
**PyTutor-MCP** là Hệ thống Gia sư Thông minh Thích ứng (Adaptive Intelligent Tutoring System — ITS) giải quyết triệt để các vấn đề trên nhờ ứng dụng tiêu chuẩn công nghiệp mở **Model Context Protocol (MCP)** do Anthropic khởi xướng:
- **Cầu nối Ground Truth:** Kết nối trực tiếp LLM (**Google Gemini 3.5 Flash Lite** / **Qwen2.5-14B**) với Hộp cát thực thi cô lập (**Python Execution Sandbox**) và Bộ phân tích cú pháp tĩnh (**AST Inspector**) qua giao thức chuẩn JSON-RPC 2.0 `stdio`.
- **Sư phạm Giàn giáo (Scaffolding Pedagogy):** Triển khai 3 cấp độ trợ giúp từ gợi mở tư duy Socratic đến dàn ý thuật toán và khung mã nguồn điền khuyết.
- **Anti-Spoil Guard:** Bộ lọc bảo vệ nghiêm ngặt tuyệt đối không giải hộ toàn bộ bài toán, buộc sinh viên phải tự tay viết mã để đạt chuẩn năng lực.

---

## 🏛️ 2. Kiến trúc Tổng thể Hệ thống (Architecture)

```text
┌────────────────────────────────────────────────────────────────────────┐
│               TẦNG TRÌNH DUYỆT (CLIENT: REACT 18 + VITE)               │
│                                                                        │
│  [Cổng Đăng Nhập /login] ──► 1-Click Quick Login (Sinh viên K65 / GV)   │
│                                                                        │
│  [Cổng Sinh Viên /student]                                             │
│  ├── Thống kê KPIs Tín chỉ: Số môn, Sao tự lực, Điểm Tự lực 4D        │
│  ├── Danh mục Lớp học phần NEU: Tìm kiếm thời gian thực, Lưới/Cột      │
│  └── Trung tâm Vinh danh: Huy hiệu đạt được, Bảng Vàng K65, Hồ sơ 4D   │
│                                                                        │
│  [Không Gian Lớp Học Phần /student/classes/:classId]                   │
│  ├── Tab 1: Chương Trình & Bài Tập (Gom nhóm Module, Thang đo Mastery) │
│  ├── Tab 2: Cây Kỹ Năng & Chuẩn Sao (Đồ thị DAG có hướng tương tác)   │
│  └── Tab 3: Bảng Vàng & Đánh Giá Năng Lực (Leaderboard, Hồ sơ 4 Chiều) │
│                                                                        │
│  [Môi Trường Lập Trình IDE /student/ide/:exerciseId]                   │
│  ├── Cột 1: Đề bài Markdown, Thông tin Lớp học phần duy nhất          │
│  ├── Cột 2: Monaco Editor, Custom Stdin, Visualizer, 3 NÚT ĐỘC LẬP:    │
│  │     ▶ [Chạy thử]       ── Chấm Sandbox siêu tốc (0.07s)             │
│  │     🤖 [Hỏi Gia sư AI]  ── Gợi ý Socratic 3 Mức (Không cấp sao)      │
│  │     🚀 [Nộp bài]       ── Chấm điểm sao tự lực & Mở khóa bài mới   │
│  └── Cột 3: Gia sư AI Socratic, Nhận diện AST, Review chuẩn Pythonic   │
│                                                                        │
│  [Bảng Điều Khiển Giảng Viên /instructor]                              │
│  ├── Sidebar Workspace: Quản lý Lớp, Ngân hàng Bài tập, Giám sát nộp   │
│  └── Xuất Báo cáo CSV Mã hóa chuẩn UTF-8 BOM cho Microsoft Excel       │
└────────────────────────────────────┬───────────────────────────────────┘
                                     │ HTTP REST + Bearer JWT Token (24h)
                                     ▼
┌────────────────────────────────────────────────────────────────────────┐
│             BACKEND FASTAPI (MCP HOST & ITS ORCHESTRATOR)              │
│                                                                        │
│  • True MCP Discovery (tools/list) qua giao thức JSON-RPC 2.0 stdio    │
│  • Context Bundle Orchestration: [Code + Tests + AST + Model + History]│
│  • Phân quyền RBAC (Role-Based Access Control): student & instructor   │
│  • Bộ lọc Hậu kiểm Chống Tiết lộ Lời giải (Anti-Spoil Guard)           │
│  • Cơ sở Dữ liệu SQLite: pytutor.db (WAL Mode, Timeout 20.0s)          │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
    JSON-RPC 2.0   │                                 │ Google GenAI SDK
    (stdio pipe)   │                                 │ (Gemini 3.5 Flash Lite)
                   ▼                                 ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│        MCP SERVER PYTHON 3.14        │  │  PEDAGOGICAL LLM ENGINE      │
│  (PyTutor Code Execution Engine)     │  │  (Google Gemini / Qwen / ITS)│
│                                      │  │                              │
│  🛠️ run_test_cases (Timeout 5.0s)    │  │  🧠 Gợi mở Socratic (Lv 1)   │
│  🛠️ analyze_code_ast (AST Inspector) │  │  🔍 Chẩn đoán lỗi (Lv 2)     │
│  🛠️ get_exercise_list (SQLite)       │  │  📘 Mã giả & Khung code(Lv3) │
│  🛠️ get_exercise_details (SQLite)    │  │                              │
│  🛠️ save_learning_event (Log trace)  │  │  🛡️ Anti-Spoil Guard:       │
│  🛠️ get_attempt_history (Lịch sử)    │  │     Tuyệt đối không giải hộ │
│  🛠️ get_student_model (Mô hình ITS)  │  │     code ở Mức 1 & 2        │
│  🛠️ trace_code_execution (Visualizer)│  │                              │
└──────────────────────────────────────┘  └──────────────────────────────┘
```

---

## 🚀 3. Tính Năng Nổi Bật (Key Features)

### 3.1. Kiến Trúc Điều Hướng Đa Tầng (Multi-Stage LMS & IDE)
- **Tách biệt Không gian Học vụ với Môi trường Viết mã:** Sinh viên không bị đẩy ngay vào màn hình IDE chật chội mà đi tuần tự theo luồng chuẩn mực:
  `Đăng nhập (/login)` ──► `Cổng Sinh viên (/student)` ──► `Lớp Học phần (/student/classes/:id)` ──► `Không gian Code IDE (/student/ide/:id)`.
- **Catalogue 24 Lớp Học Phần Chuẩn NEU LMS:** Nạp sẵn các môn học tín chỉ thực tế của Khoa CNTT - NEU (`Hệ quản trị CSDL`, `Lập trình phân tích dữ liệu`, `Phân tích thiết kế hệ thống`, `Quản trị mạng`, `Mạng kết nối vạn vật`, `Đề án CNTT`...) với tính năng tìm kiếm tức thì và bộ chuyển đổi hiển thị Dạng Lưới (Grid) / Dạng Cột (List).

### 3.2. Danh Mục 8 Công Cụ Chuẩn Model Context Protocol (MCP)
Tất cả 8 công cụ được Host tự động khám phá động (*Dynamic Discovery*) qua giao thức JSON-RPC 2.0 stdio khi khởi động:

| # | Tên MCP Tool | Đầu vào (Arguments) | Chức năng chi tiết |
|:---:|:---|:---|:---|
| 1 | `run_test_cases` | `code: str`, `test_cases: list` | Thực thi mã nguồn trong Hộp cát cô lập với Timeout 5.0s, bắt lỗi vô hạn |
| 2 | `analyze_code_ast` | `code: str` | Phân tích cú pháp tĩnh AST: phát hiện For/While, đệ quy, biến accumulator |
| 3 | `get_exercise_list` | *(none)* | Truy xuất danh mục bài tập lập trình Python từ SQLite |
| 4 | `get_exercise_details` | `exercise_id: str` | Cung cấp đề bài Markdown, mã khởi tạo và bộ test cases chuẩn |
| 5 | `save_learning_event` | `session_id`, `exercise_id`, `code`... | Ghi nhận sự kiện học tập và lượt nộp bài phục vụ phân tích dữ liệu |
| 6 | `get_attempt_history` | `session_id: str`, `exercise_id: str` | Cung cấp lịch sử nộp bài trước đó để AI nhận thức tiến trình làm lại |
| 7 | `get_student_model` | `session_id: str`, `class_id: str` | Tính toán mô hình người học: bài đã thành thạo, bài gặp khó khăn, mức gợi ý TB |
| 8 | `trace_code_execution` | `code: str`, `stdin_input: str` | Ghi nhận vết từng bước thực thi (dòng lệnh, hàm, biến số, stdout) cho Visualizer |

### 3.3. Quy Trình 3 Hành Động Độc Lập Trên IDE
Thanh công cụ Monaco Editor cung cấp 3 nút bấm với màu sắc và phím tắt chuyên biệt:
- **`▶ Chạy thử` (Ctrl + Enter | Màu Cyan):** Chạy kiểm tra nhanh trong Sandbox chỉ tốn **0.07 giây**, hoàn toàn không tiêu tốn quota AI, không ghi nhận điểm nộp.
- **`🤖 Hỏi Gia sư AI` (Màu Vàng Amber):** Gửi yêu cầu với `action_type = 'ask_ai'`. AI phân tích AST + Sandbox để trả lời theo mức gợi ý (1, 2, 3), **không cấp sao và không mở modal chúc mừng** để sinh viên tiếp tục hoàn thiện mã nguồn.
- **`🚀 Nộp bài` (Ctrl + Shift + Enter | Màu Xanh Emerald):** Gửi yêu cầu với `action_type = 'submit'`. Hệ thống chấm điểm chính thức: nếu vượt qua 100% test cases, hệ thống kiểm tra lịch sử các lần hỏi AI để cấp đúng số **Sao Tự Lực (1 - 3 ⭐)**, mở khóa huy hiệu, kích hoạt pháo hoa confetti và cập nhật Cây lộ trình.

### 3.4. Phương Pháp Sư Phạm Giàn Giáo 3 Cấp Độ & Anti-Spoil Guard
Hệ thống phân hóa 3 cấp độ gợi ý với độ tương phản rõ rệt:
- **💡 Mức 1 — Gợi Mở Tư Duy (Bảo toàn 3 ⭐):** Đánh giá hướng đi tổng quan, đặt 2 câu hỏi Socratic sắc bén về điều kiện biên/cận vòng lặp, chỉ ra từ khóa/khái niệm Python cần ôn lại. Tuyệt đối không trích dòng code cụ thể, không viết code sửa.
- **🔍 Mức 2 — Chẩn Đoán Dòng Lỗi (Bảo toàn 2 ⭐):** Khoanh vùng chính xác dòng code hoặc biểu thức của học viên bị sai. Mổ xẻ chi tiết Test Case bị FAIL (`Input`, `Actual Output` từ code của bạn, `Expected Output` đề bài yêu cầu, giải thích lý do sai số). Chỉ dẫn logic sửa bằng lời giải thích kỹ thuật.
- **📘 Mức 3 — Dàn Ý & Khung Code Mẫu (Bảo toàn 1 ⭐):** Cung cấp dàn ý giải thuật 4 bước rõ ràng VÀ một **Khung mã nguồn gợi ý (Scaffolded Code Skeleton)** chuẩn chỉnh có chừa các chỗ trống `...` hoặc `# TODO:` để sinh viên nhìn vào hiểu ngay cấu trúc giải thuật và tự hoàn thành phần cốt lõi.
- **🛡️ Anti-Spoil Guard:** Bộ lọc regex tự động hậu kiểm phản hồi của LLM, lập tức thay thế các khối mã nguồn dài $\ge 3$ dòng bằng thông báo sư phạm nếu học viên ở Mức 1 và 2.

### 3.5. Gamification, Chuẩn Sao Mastery Rubric & Hồ Sơ Năng Lực 4D
- **Quy tắc Thang đo Năng lực (Mastery Rubric):**
  - Bài tập yêu cầu đạt chuẩn tối thiểu (ví dụ `min_stars_required = 2`).
  - Nếu giải đúng 100% test cases nhưng dùng quá nhiều gợi ý (chỉ đạt 1 ⭐) $\rightarrow$ Trạng thái `NEEDS_MORE_STARS` (Yêu cầu làm lại tự lực hơn để mở khóa bài tiếp theo).
  - Bài phụ thuộc trong Đồ thị có hướng (DAG) chỉ mở khóa khi bài tiên quyết đã đạt chuẩn (`MASTERED`).
- **5 Huy hiệu Vinh danh:** `first_blood` (Bước Chân Đầu Tiên), `clean_coder` (Bậc Thầy Clean Code), `independent_thinker` (Nhà Tư Duy Độc Lập), `speed_demon` (Chiến Binh Tốc Độ), `bug_hunter` (Dũng Sĩ Diệt Bug).
- **Động cơ Phân tích 4D (Student 4D Analytics):** Đo lường Định lượng:
  1. *Điểm Tự lực Sư phạm (Autonomy Score / 100)*.
  2. *Tỷ lệ Vượt qua Lần đầu (First-try Pass Rate %)*.
  3. *Số lần Nộp bài Trung bình / Bài*.
  4. *Cơ cấu Lỗi (Error Breakdown %)*: Tỷ lệ lỗi logic vs lỗi cú pháp/runtime.
  5. *3 Thẻ Chẩn đoán Sư phạm Thông minh*: Điểm mạnh nổi bật, Điểm nghẽn cần khắc phục, Hành động khuyến nghị tiếp theo.

### 3.6. Công Cụ Trực Quan Hóa (Visualizer) & Review Chuẩn Pythonic
- **👁️ Execution Step Visualizer (MCP Tool 8):** Bắt vết từng dòng lệnh thực thi, cho phép bước tới/bước lui (Next/Prev Step), hiển thị bảng biến số cục bộ thay đổi theo thời gian thực và luồng xuất màn hình (stdout), kèm hỗ trợ Custom Stdin.
- **🐍 Senior Pythonic Code Review:** Gọi Gemini Tech Lead chấm điểm Clean Code (thang 100), phân tích độ phức tạp thời gian $O(n)$, kiểm tra chuẩn PEP 8 và hiển thị Diff so sánh mã nguồn đối chứng.

---

## 🔑 4. Tài khoản Đăng nhập Demo (Hội đồng Chấm Đồ án)

Trang `/login` tích hợp sẵn nút bấm **1-Click Quick Login** để Hội đồng kiểm tra ngay lập tức:

| Tài khoản | Mật khẩu | Vai trò | Họ tên & Đơn vị đào tạo | Chức năng trải nghiệm |
|:---|:---|:---|:---|:---|
| `student` | `student123` | **Sinh viên** | **Trần Minh Khánh**<br>*(SV K65 CNTT — MSV: 11236131)* | Truy cập Cổng sinh viên, vào Lớp học phần, làm bài trên IDE 3 cột, nhận gợi ý AI, nộp bài tính sao tự lực, xem Bảng Vàng và Hồ sơ 4D. |
| `gv_tran` | `gv123` | **Giảng viên** | **Nguyễn Văn A**<br>*(Khoa CNTT — ĐH Kinh tế Quốc dân)* | Toàn quyền Dashboard Giảng viên: CRUD bài tập, xem lịch sử nộp bài của sinh viên, xem cấu hình sandbox, xuất báo cáo CSV UTF-8 BOM. |
| `gv_tuan` | `gv123` | **Giảng viên** | **Trần Văn B**<br>*(Khoa CNTT — ĐH Kinh tế Quốc dân)* | Giảng viên phụ trách các lớp học phần được phân công trong học kỳ. |

---

## ⚡ 5. Hướng dẫn Cài đặt & Khởi chạy Nhanh (Quickstart)

### 5.1. Yêu cầu Hệ thống
- **Hệ điều hành:** Windows 10/11, Ubuntu 20.04+ hoặc macOS 12+
- **Python:** 3.10+ (Khuyến nghị **Python 3.14**)
- **Node.js:** v18+ (Khuyến nghị **Node.js v24+**)

### 5.2. Cài đặt Môi trường Thủ công

```bash
# 1. Clone kho lưu trữ mã nguồn
git clone https://github.com/Chthollyuhc/PyTutor-MCP.git
cd PyTutor-MCP

# 2. Khởi tạo môi trường ảo Python & Cài đặt thư viện Backend
python -m venv venv

# Kích hoạt trên Windows (PowerShell/CMD):
.\venv\Scripts\activate
# Hoặc trên Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt

# 3. Cài đặt thư viện Frontend
cd frontend
npm install
cd ..

# 4. Thiết lập biến môi trường
cp .env.example .env
# Mở file .env và điền GEMINI_API_KEY của bạn (nhận miễn phí tại Google AI Studio)
```

### 5.3. Khởi chạy 1-Click Tự động

#### Trên Windows:
Nhấp đúp chuột vào file:
👉 **`start_dev.bat`**  
*(Script được tích hợp cơ chế tự động dò tìm môi trường Python trong `venv`, `.venv` hoặc Python hệ thống, sau đó bật song song cả Backend và Frontend).*

#### Trên Linux / macOS:
```bash
chmod +x start_dev.sh
./start_dev.sh
```

Hệ thống sẽ khởi chạy tại các địa chỉ:
* 🌐 **Cổng Web Ứng dụng:** [http://localhost:5173](http://localhost:5173)
* 📑 **Tài liệu API Tương tác (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* 🔍 **Kiểm tra Sức khỏe MCP & Sandbox:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 📁 6. Cấu trúc Thư mục Dự án (Project Structure)

```text
PyTutor-MCP/
├── backend/                        # Máy chủ Backend FastAPI (MCP Host & Orchestrator)
│   ├── auth.py                     # Quản lý xác thực JWT & Phân quyền RBAC
│   ├── database.py                 # SQLite engine (WAL mode), Schemas 9 bảng & Seeding dữ liệu NEU
│   ├── llm_service.py              # Đóng gói Context Bundle, Sư phạm Giàn giáo 3 cấp & Anti-Spoil
│   ├── main.py                     # 30+ REST API Routes & Lifespan handler
│   ├── mcp_client.py               # Kết nối JSON-RPC 2.0 Client qua stdio pipe tới MCP Server
│   └── schemas.py                  # Pydantic DTO models kiểm định dữ liệu
│
├── frontend/                       # Giao diện người dùng Web (React 18 + Vite + TailwindCSS)
│   ├── src/
│   │   ├── components/             # Các thành phần giao diện & Modals chuyên sâu
│   │   │   ├── EditorPanel.jsx     # Monaco Editor, Hotkeys, Error Decoration & Tab Test cases
│   │   │   ├── ExecutionVisualizerModal.jsx # Trực quan hóa từng bước thực thi (Tracer steps)
│   │   │   ├── Header.jsx          # Thanh điều hướng trên, MCP Status Pill & User identity
│   │   │   ├── LeaderboardModal.jsx# Bảng Vàng vinh danh học viên K65
│   │   │   ├── MCPInspectorModal.jsx # Trực quan hóa 8 MCP Tools & Nhật ký JSON-RPC Trace
│   │   │   ├── ProblemPanel.jsx    # Đề bài Markdown, Metadata & Ngữ cảnh Lớp học phần
│   │   │   ├── PythonicReviewModal.jsx # Đánh giá Clean Code PEP 8 từ Tech Lead
│   │   │   ├── SkillRoadmapModal.jsx   # Đồ thị DAG kỹ năng học phần
│   │   │   ├── StudentProfileModal.jsx # Hồ sơ năng lực 4 chiều & Lịch sử nạp lại code
│   │   │   └── TutorPanel.jsx      # Phản hồi Sư phạm 3 cấp độ, AST & Multi-turn Chat
│   │   ├── context/
│   │   │   └── AuthContext.jsx     # Quản lý phiên đăng nhập JWT & Tự động gia hạn
│   │   ├── pages/                  # Các trang màn hình điều hướng đa tầng
│   │   │   ├── ExerciseFormPage.jsx    # Form thêm/sửa bài tập cho Giảng viên
│   │   │   ├── InstructorDashboard.jsx # Bảng điều khiển Quản trị Giảng viên
│   │   │   ├── LoginPage.jsx           # Cổng Đăng nhập NEU Split-screen & 1-Click Demo
│   │   │   ├── StudentClassDetailPage.jsx # Không gian Lớp học phần tín chỉ (3 Tabs)
│   │   │   ├── StudentIDE.jsx          # Môi trường Lập trình Code IDE 3 Cột
│   │   │   └── StudentPortalPage.jsx   # Cổng Lớp học phần Sinh viên & Trung tâm Vinh danh
│   │   ├── services/
│   │   │   └── api.js              # Axios Client kết nối Backend API
│   │   └── App.jsx                 # Routing phân cấp & Bộ bảo vệ Route
│   ├── package.json                # Cấu hình dependencies frontend
│   └── vite.config.js              # Cấu hình Vite build tool
│
├── mcp_server/                     # Máy chủ Model Context Protocol độc lập (mcp SDK 2.2.0)
│   ├── ast_analyzer.py             # Bộ phân tích tĩnh cây cú pháp trừu tượng AST
│   ├── exercises_data.py           # Dữ liệu 5 bài tập nền tảng cơ sở
│   ├── sandbox.py                  # Hộp cát thực thi mã Python Subprocess (Timeout 5.0s)
│   ├── server.py                   # Điểm vào MCP Server, đăng ký 8 MCP Tools qua stdio
│   ├── storage.py                  # Tầng truy xuất dữ liệu độc lập cho MCP Server
│   └── tracer.py                   # Tracing từng bước thực thi biến số qua sys.settrace
│
├── docs/                           # Tài liệu khoa học & Báo cáo đồ án
│   ├── EVALUATION_REPORT.md        # Báo cáo thực nghiệm khoa học độc lập tự động xuất
│   ├── MCP_QUICK_SUMMARY_MOBILE.md # Tóm tắt nhanh kiến trúc MCP đọc trên điện thoại
│   └── WHY_MCP_EXPLAINED.md        # Luận cứ khoa học: Vì sao đồ án cần sử dụng MCP
│
├── plans/                          # Kế hoạch & Kiến trúc chi tiết qua 15 Phases
├── scripts/                        # Các scripts hỗ trợ di trú và đồng bộ dữ liệu
├── test_phase*.py                  # Hệ thống kiểm thử tự động toàn diện qua từng Phase
├── evaluate_its_benchmark.py       # Script đo đạc thực nghiệm khoa học 4 Benchmarks
├── requirements.txt                # Thư viện Python phụ thuộc
├── start_dev.bat                   # Script khởi chạy 1-Click tự động cho Windows
├── start_dev.sh                    # Script khởi chạy tự động cho Linux/macOS
├── AI_HANDOFF_CONTEXT.md           # Single Source of Truth phục vụ bàn giao & tiếp quản
├── PLAN.md                         # Bảng theo dõi tiến độ tổng thể 15 Phases
└── README.md                       # Tài liệu giới thiệu chính thức của dự án
```

---

## 📡 7. Danh mục API Chính (REST Endpoints)

Hệ thống cung cấp hơn 30+ endpoints RESTful chuẩn mực được bảo vệ bằng JWT Bearer Token:

### Xác thực & Người dùng (Authentication)
- `POST /api/auth/login`: Xác thực đăng nhập, cấp phát JWT Bearer Token (24h).
- `GET /api/auth/me`: Kiểm tra phiên làm việc hiện tại và định danh người dùng.

### Không gian Sinh viên & Lớp Học Phần (Student & Classroom)
- `GET /api/classes`: Lấy danh mục 24 lớp học phần tín chỉ kèm trạng thái ghi danh.
- `GET /api/student/my-classes`: Lấy danh sách các lớp học phần sinh viên đang theo học.
- `POST /api/classes/enroll-by-code`: Ghi danh vào lớp học phần bằng mã tham gia.
- `DELETE /api/classes/{class_id}/leave`: Hủy ghi danh (rút khỏi lớp học phần).
- `GET /api/classes/{class_id}/curriculum`: Lấy danh mục bài tập theo module của lớp kèm chuẩn sao.
- `GET /api/skill-roadmap`: Lấy đồ thị kỹ năng DAG theo chuẩn Mastery Rubric.
- `GET /api/student/profile`: Lấy Hồ sơ Năng lực 4D Metrics và 3 Thẻ chẩn đoán sư phạm.
- `GET /api/leaderboard`: Lấy Bảng Vàng vinh danh top học viên K65 theo lớp.

### Thực thi Mã Nguồn & Gia Sư AI (Coding & ITS Engine)
- `POST /api/run-test`: Chạy thử nhanh mã nguồn trong Sandbox (0.07s, không tốn quota AI).
- `POST /api/submit`: Xử lý 2 hành động:
  - `action_type = "ask_ai"`: Sinh phản hồi Socratic theo 3 mức độ gợi ý, không cấp sao.
  - `action_type = "submit"`: Chấm điểm chính thức, cấp sao tự lực (1-3 ⭐) và mở khóa bài tiếp theo.
- `POST /api/run-custom`: Chạy thử mã nguồn với dữ liệu đầu vào tự do (Custom Stdin).
- `POST /api/tutor/chat`: Trò chuyện đàm thoại nhiều lượt (Multi-turn Follow-up Chat) với Gia sư AI.
- `POST /api/code-review`: Chấm điểm Clean Code PEP 8 và phân tích độ phức tạp thuật toán.
- `POST /api/trace`: Truy xuất chuỗi vết thực thi từng dòng lệnh cho Visualizer.

### Quản trị Giảng viên (Instructor Dashboard)
- `GET /api/instructor/stats`: Lấy 4 chỉ số KPIs giảng dạy tổng hợp toàn trường.
- `POST /api/instructor/exercises`: Thêm bài tập mới vào ngân hàng đề kèm test cases.
- `PUT /api/instructor/exercises/{id}`: Chỉnh sửa bài tập và cấu hình test cases.
- `DELETE /api/instructor/exercises/{id}`: Xóa bài tập khỏi hệ thống.
- `GET /api/instructor/submissions`: Xem toàn bộ lịch sử nộp bài của sinh viên kèm code và lời khuyên AI.
- `GET /api/instructor/export-csv`: Xuất báo cáo dữ liệu nộp bài chuẩn UTF-8 BOM cho Excel.
- `GET /api/health`: Kiểm tra thông số trình thông dịch Python 3.14, sandbox flags và 8 MCP tools.

---

## 🎬 8. Kịch Bản 5 Bước Trình Diễn Trước Hội Đồng (Defense Demo Script)

Khi đứng trước Hội đồng chấm Đồ án Tốt nghiệp, sinh viên thực hiện theo kịch bản mẫu 5 bước chuẩn mực:

### Bước 1: Trình diễn Khám phá Động MCP (Dynamic MCP Discovery)
- Đăng nhập với tài khoản **Sinh viên** (`student`).
- Bấm vào biểu tượng **⚡ MCP (8)** trên thanh điều hướng.
- **Thuyết minh với Hội đồng:** Hệ thống không hardcode danh sách công cụ mà tự động khám phá 8 công cụ thông qua giao thức chuẩn JSON-RPC 2.0 `stdio` khi khởi động. Hiển thị trực quan từng lệnh `initialize` và `tools/list` trong nhật ký.

### Bước 2: Trình diễn Không gian Lớp học phần & Điều hướng Đa tầng
- Tại Cổng sinh viên, chọn lớp **"Cơ sở lập trình"** (`CNTT1128(223)_02`).
- Trình diễn **Cây kỹ năng & Chuẩn sao (Mastery Rubric)**: Chứng minh tính phân cấp kiến thức theo đồ thị có hướng (DAG), các bài tập mở khóa tuần tự dựa trên chuẩn sao tự lực tích lũy.

### Bước 3: Trình diễn 3 Nút Độc lập & Sư phạm Giàn giáo (Scaffolding Pedagogy)
- Mở bài tập *"Bài 01: Tính tổng từ 1 đến n"*.
- **Thao tác 1 (Chạy thử):** Bấm **"▶ Chạy thử"**: Mã được kiểm thử trong Sandbox độc lập chỉ tốn **0.07 giây**, hoàn toàn không tốn quota AI.
- **Thao tác 2 (Hỏi Gia sư AI):** Cố ý sửa code sai logic (`tong = n * 2`), chọn **Level 1** và bấm **"🤖 Hỏi Gia sư AI"**:
  - AI đóng vai trò nhà sư phạm Socratic, đặt câu hỏi gợi mở, **tuyệt đối không đưa ra lời giải** (tuân thủ Anti-Spoil Guard).
  - Bấm nâng cấp lên **Level 2** (Chẩn đoán nguyên nhân) và **Level 3** (Dàn ý thuật toán & Khung code mẫu `# TODO`).
- **Thao tác 3 (Nộp bài):** Viết code đúng và bấm **"🚀 Nộp bài"**: Modal chúc mừng xuất hiện, cấp sao tự lực (1-3 ⭐) dựa trên mức độ sử dụng gợi ý AI và trao huy hiệu vinh danh.

### Bước 4: Trình diễn Công cụ Trực quan hóa (Visualizer) & Đánh giá Mã nguồn (Review)
- Bấm nút **"👁️ Trực quan hóa"**: Trình diễn từng bước nhảy của biến số $i$ và biến tổng qua từng vòng lặp.
- Bấm nút **"🐍 Đánh giá Pythonic"**: Hệ thống phân tích chuẩn PEP 8 và tư duy tối ưu giải thuật bằng AI.

### Bước 5: Trình diễn Bảng điều khiển Quản trị Giảng viên (Instructor Dashboard)
- Đăng xuất và đăng nhập tài khoản Giảng viên (`gv_tran` - Thầy **Nguyễn Văn A**).
- Trình diễn 4 thẻ KPIs tổng hợp, quản lý ngân hàng bài tập (thêm/sửa test case trực tiếp).
- Mở danh sách sinh viên: Kiểm tra định danh sinh viên **Trần Minh Khánh - MSV: 11236131**, số bài đã làm chủ và tổng sao tích lũy.
- Bấm **"📥 Xuất Báo Cáo CSV"**: Tải file về và mở trực tiếp bằng Microsoft Excel, chứng minh tiếng Việt hiển thị sắc nét nhờ mã hóa UTF-8 BOM.

---

## 🧪 9. Đánh Giá Thực Nghiệm Khoa Học (Academic Benchmark)

Hệ thống tích hợp sẵn kịch bản kiểm thử đo đạc thực nghiệm độc lập theo 4 câu hỏi nghiên cứu (Research Questions):
- **RQ1 (Hiệu năng MCP):** Khám phá 8 MCP Tools qua JSON-RPC 2.0 stdio đạt độ trễ trung bình **~739 ms** (dưới 1 giây).
- **RQ2 (An toàn Sandbox):** Kiểm thử 5 kịch bản (Code đúng, Code sai, Lỗi cú pháp, Lỗi chia cho 0, Vòng lặp vô hạn `while True:` bị cưỡng chế ngắt sau đúng **~5.0s** mà không làm treo máy chủ).
- **RQ3 (Trí tuệ AST):** Phân tích tĩnh cấu trúc mã nguồn hoàn tất dưới **3 ms**.
- **RQ4 (Sư phạm & Chống lộ đáp án):** 100% phản hồi ở Mức 1 và 2 tuân thủ nghiêm ngặt Anti-Spoil Guard.

Chạy kịch bản tự động:
```powershell
py -3 evaluate_its_benchmark.py
```
Toàn bộ số liệu thực nghiệm được tổng hợp tự động và xuất ra file: 👉 **[`docs/EVALUATION_REPORT.md`](docs/EVALUATION_REPORT.md)**.

---

## 📄 10. Bản quyền & Đóng góp (License & Credits)

- **Mã nguồn:** Bản quyền thuộc về **Trần Minh Khánh** (Sinh viên Khóa K65 CNTT — Khoa Công nghệ thông tin, Trường Đại học Kinh tế Quốc dân).
- **Giấy phép phần mềm:** Phát hành theo giấy phép mã nguồn mở [MIT License](LICENSE).
- **Tri ân học thuật:** Xin trân trọng cảm ơn các Thầy Cô Khoa Công nghệ thông tin — Trường Đại học Kinh tế Quốc dân (NEU) đã tận tình định hướng và hướng dẫn đồ án tốt nghiệp này.
