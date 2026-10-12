# 🎓 PyTutor: Intelligent Tutoring System with Model Context Protocol (MCP)

> **Đồ án tốt nghiệp:** Hệ thống Gia sư Thông minh Hỗ trợ Học Lập trình Python Dựa trên Giao thức Model Context Protocol (MCP)  
> **Sinh viên thực hiện:** Trần Khánh  
> **Repository:** [https://github.com/Chthollyuhc/PyTutor-MCP](https://github.com/Chthollyuhc/PyTutor-MCP)

---

## 📖 Giới thiệu (Overview)

**PyTutor** là hệ thống gia sư AI thông minh thế hệ mới hỗ trợ sinh viên học lập trình Python. Khác với các hệ thống Chatbot truyền thống (chỉ suy luận văn bản tĩnh và dễ gặp ảo giác - *hallucination*), PyTutor tích hợp **Model Context Protocol (MCP)** – chuẩn giao tiếp công nghiệp do Anthropic khởi xướng (hiện thuộc quản lý của *Agentic AI Foundation / Linux Foundation*).

Hệ thống kết nối trực tiếp mô hình ngôn ngữ lớn (LLM - *Qwen2.5-14B*) với môi trường thực thi hộp cát an toàn (Python Execution Sandbox), cho phép AI đọc **bằng chứng thực tế (Ground Truth)** từ kết quả chạy test cases và phân tích cú pháp tĩnh (AST) trước khi đưa ra gợi ý sư phạm từng bước (*Scaffolding hints*), hoàn toàn không tiết lộ lời giải sẵn cho sinh viên.

---

## 💡 Tại sao sử dụng MCP thay vì REST API thông thường?

| Tiêu chí | REST API truyền thống | Model Context Protocol (MCP) |
|---|---|---|
| **Người sử dụng chính** | Lập trình viên viết code cố định | AI Model / Agent tự khám phá tại Runtime |
| **Cơ chế tích hợp** | Hardcoded endpoints (ví dụ: `/run_code`) | Dynamic Tool Discovery qua JSON-RPC 2.0 |
| **Độ phức tạp tích hợp** | **Bài toán $M \times N$:** Mỗi AI phải viết lại keo dán (glue code) cho mỗi Tool | **Bài toán $M + N$:** Cắm và chạy (*Plug-and-play*), chuẩn hóa toàn cầu |
| **Bảo mật & Sandbox** | Dễ rủi ro nếu chạy chung process server | Cô lập hoàn toàn qua Stdio / HTTP SSE Subprocess |
| **Tính giải thích (Explainability)** | Khó audit xem AI suy luận từ đâu | Lưu vết toàn bộ Tool Calls & kết quả trả về trong Log |

---

## 🏗️ Kiến trúc Hệ thống (Architecture)

PyTutor được xây dựng theo mô hình **Client-Server** của giao thức MCP:

```
┌────────────────────────────────────────────────────────┐
│                        MCP HOST                        │
│   (Giao diện Web Streamlit / React + Monaco Editor)    │
│                                                        │
│        ┌──────────────────────────────────────┐        │
│        │   AI TUTOR ENGINE (Qwen2.5-14B)      │        │
│        └──────────────────┬───────────────────┘        │
│                           │                            │
│        ┌──────────────────▼───────────────────┐        │
│        │              MCP CLIENT              │        │
│        └──────────────────┬───────────────────┘        │
└───────────────────────────┼────────────────────────────┘
                            │  JSON-RPC 2.0 (Stdio Transport)
                            │
┌───────────────────────────▼────────────────────────────┐
│                       MCP SERVER                       │
│             (PyTutor Code Execution Engine)            │
│                                                        │
│   🛠️ run_student_code(code, n_value)                  │
│       └── Chạy code sinh viên trong Sandbox cô lập     │
│                                                        │
│   🛠️ analyze_syntax(code) / analyze_ast(code)         │
│       └── Phân tích cây cú pháp trừu tượng (AST)       │
└────────────────────────────────────────────────────────┘
```

---

## ⚡ Quy trình 9 Bước Hoạt động (9-Step Protocol Flow)

1. **Sinh viên nộp bài / xin gợi ý:** Nhập mã nguồn vào editor và chọn mức gợi ý (*Level 1, 2, hoặc 3*).
2. **Khởi tạo kết nối:** MCP Client gửi yêu cầu `initialize` (Handshake) tới MCP Server.
3. **Tự động khám phá (Discovery):** Client gửi `tools/list` để nhận danh sách công cụ và schema tham số.
4. **Gọi thực thi mã:** Client gửi `tools/call: run_student_code` kèm code sinh viên.
5. **Thực thi trong Sandbox:** Server chạy code trong môi trường an toàn, bắt toàn bộ stdout, stderr, exception.
6. **Phân tích cú pháp AST:** Server kiểm tra cấu trúc lặp `for`/`while`, biến tích lũy `+=`, lệnh `return`.
7. **Đóng gói Context Bundle:** Ghép `[Đề bài + Code sinh viên + Kết quả Sandbox + Nhận xét AST]`.
8. **Suy luận Sư phạm:** Gửi Context Bundle tới LLM (Qwen2.5-14B) với prompt phân cấp gợi ý sư phạm.
9. **Hiển thị trực quan:** Render kết quả kiểm thử và câu trả lời gợi ý của AI Tutor lên giao diện.

---

## 🚀 Cài đặt & Chạy Thử (Quickstart)

### Yêu cầu hệ thống
* Python 3.10 trở lên
* Trình duyệt web (Chrome, Edge, Firefox)

### 1. Cài đặt thư viện cần thiết
```bash
pip install mcp streamlit streamlit-ace requests docx python-docx
```

### 2. Chạy Demo Giao diện Trực quan MCP (Khuyên dùng)
Bản demo có giao diện chia màn hình, hiển thị log các tin nhắn JSON-RPC 2.0 thời gian thực giữa Client và Server:
```bash
python -m streamlit run mcp_visual_demo.py --server.port 8503
```
👉 Mở trình duyệt tại: **[http://localhost:8503](http://localhost:8503)**

### 3. Chạy Demo Terminal (Kiểm tra giao thức Stdio thuần túy)
```bash
python mcp_real_client.py
```

---

## 📂 Cấu trúc Thư mục (Repository Structure)

```
.
├── mcp_visual_demo.py                  # Giao diện chính hiển thị tương tác MCP Live
├── mcp_server_pytutor.py               # MCP Server chính thức (dùng mcp 2.x SDK)
├── mcp_real_server.py                  # MCP Server mở rộng (AST & Test runner)
├── mcp_real_client.py                  # MCP Client chạy qua terminal (stdio transport)
├── pytutor_mcp_demo.py                 # Bản demo tích hợp API Qwen2.5-14B
├── pytutor_demo.py                     # Bản demo đơn giản hóa ban đầu
├── test_mcp_connection.py              # Script kiểm thử kết nối JSON-RPC
│
├── Bao_cao_MCP_PyTutor_Tran_Khanh_v2.docx # Báo cáo nghiên cứu học thuật đầy đủ (Phần I & II)
├── Bao-cao-wireframe-chuc-nang-chinh-PyTutor.pdf # Báo cáo phân tích thiết kế giao diện
├── pytutor-main-wireframe.png          # Bản vẽ wireframe màn hình chính của hệ thống
├── AI_HANDOFF_CONTEXT.md               # Tài liệu ngữ cảnh kỹ thuật của dự án
└── .gitignore                          # Cấu hình loại trừ file rác / secrets
```

---

## 📚 Tài liệu Nghiên cứu Tham khảo (References)

1. **Anthropic.** (2024). *Model Context Protocol Specification*. [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
2. **Stefan Szeider.** (2025). *MCP-Solver: Integrating Language Models with Constraint Programming Systems*. SAT 2025 Conference. [GitHub: szeider/mcp-solver](https://github.com/szeider/mcp-solver)
3. **James Zou et al.** (2026). *Paper2Agent: Transforming Research Papers into Executable AI Agents*. **Nature**.
4. **Linux Foundation.** (2025). *Agentic AI Foundation & Protocol Standards*.

---

*Dự án thuộc Đồ án Tốt nghiệp chuyên ngành Công nghệ Thông tin.*
