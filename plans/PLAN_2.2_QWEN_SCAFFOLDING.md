# 🧠 PLAN 2.2: QWEN2.5-14B INTEGRATION & SCAFFOLDING PEDAGOGY

> **Phân hệ:** `backend/`  
> **Trạng thái:** ✅ ĐÃ HOÀN THÀNH (100% Tests Passed)

---

## 🎯 1. Mục tiêu (Objective)
Tích hợp mô hình ngôn ngữ lớn Qwen2.5-14B qua Ollama API của giảng viên (`101.96.66.232:8037`), đóng gói Context Bundle dựa trên dữ liệu Ground Truth thực tế từ MCP Server và hiện thực hóa phương pháp sư phạm giàn giáo (Scaffolding Pedagogy) 3 cấp độ gợi ý, kèm bộ lọc cấm spoil code và cơ chế Fallback thông minh.

---

## 🏗️ 2. Kiến trúc Context Bundle & Phân cấp Sư phạm

```text
[Dữ liệu từ MCP Server]
  ├── Đề bài & Mục tiêu học tập
  ├── Code sinh viên nhập vào
  ├── Kết quả chạy Sandbox (PASS / FAIL / TIMEOUT / SYNTAX_ERROR)
  └── Phân tích cấu trúc cú pháp AST
           │
           ▼
[backend/llm_service.py: Context Bundle Builder]
           │
           ├──► Level 1: Gợi mở Socratic (Nhắc khái niệm, câu hỏi định hướng, KHÔNG nói lỗi cụ thể)
           ├──► Level 2: Chẩn đoán & Khoanh vùng (Chỉ rõ khối lệnh lỗi, giải thích sai lệch Actual vs Expected)
           └──► Level 3: Hướng dẫn từng bước & Mã giả (Chia nhỏ thuật toán, Pseudocode, KHÔNG viết code Python hoàn chỉnh)
           │
           ▼
[Qwen2.5-14B API: 101.96.66.232:8037/ollama/api/generate]
           │
           ├──► Thành công ──► AI Scaffolding Response (Kiểm tra Guard filter)
           └──► Lỗi kết nối ──► Rule-based Pedagogical Fallback Engine (Dựa trên AST + Test Results)
```

---

## ✅ 3. Danh sách Công việc (Checklist)

- [x] Xây dựng `backend/llm_service.py`:
  - [x] Cấu hình kết nối Ollama API (`endpoint`, `x-ollama-seckey: neutv`, `model: qwen2.5:14b-instruct-ctx16k`, `temperature: 0.3`).
  - [x] Xây dựng hàm `build_scaffolding_prompt(exercise, code, test_results, ast_analysis, hint_level)`:
    - [x] Áp dụng quy tắc cấm spoil code Python hoàn chỉnh cho sinh viên.
    - [x] System Prompt chuyên biệt cho từng Level (1, 2, 3).
    - [x] Trường hợp đặc biệt: Nếu code sinh viên đã `all_passed == True`, chuyển sang chế độ chúc mừng, nhận xét độ tối ưu code dựa trên AST và gợi ý viết Pythonic hơn.
  - [x] Triển khai hàm async `call_qwen_api(prompt)` với timeout 45s qua `httpx.AsyncClient`.
  - [x] Triển khai hàm `generate_rule_based_fallback(exercise, code, test_results, ast_analysis, hint_level)` tự động sinh gợi ý sư phạm chuẩn mực dựa trên dữ liệu AST và Sandbox nếu không gọi được LLM.
  - [x] Triển khai hàm chính `generate_tutor_hint(...)` điều phối gọi LLM kèm fallback an toàn.

---

## 📁 4. Danh sách File Đầu ra (Deliverables)
- `backend/llm_service.py`

---

## 🧪 5. Tiêu chuẩn Đạt (DoD)
- Gọi thành công tới Qwen2.5-14B API và nhận về câu trả lời bằng tiếng Việt thân thiện.
- Gợi ý của cả 3 Level tuân thủ đúng nguyên tắc sư phạm, không đưa ra code giải trọn vẹn.
- Khi ngắt mạng giả lập hoặc server LLM bận, hệ thống tự kích hoạt Fallback sinh ra gợi ý có nghĩa, không bao giờ ném lỗi HTTP 500 ra ngoài.
