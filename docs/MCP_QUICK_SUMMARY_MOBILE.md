# 📱 TÓM TẮT NHANH: TẠI SAO DÙNG MCP? (MOBILE DEFENSE CHEATSHEET)
> **Đồ án:** Hệ thống Gia sư Thông minh PyTutor-MCP (v3.5 Showcase)  
> **Sinh viên:** Trần Khánh | **Mục đích:** Đọc lướt 2 phút trên điện thoại trước giờ bảo vệ

---

## 1. 💡 MCP LÀ GÌ? (ẨN DỤ 30 GIÂY)

* **LLM (Trí tuệ Nhân tạo - Gemini / Claude / Qwen):**
  * Giống như **"Bộ não thiên tài bị giam trong phòng kính"**.
  * Rất giỏi đọc hiểu và hành văn, nhưng **KHÔNG CÓ TAY CHÂN** để chạy code thật và **KHÔNG CÓ SỔ TAY** để nhớ lịch sử học viên.
  * Nếu để AI tự chấm code $\rightarrow$ AI buộc phải **"đoán mò"** kết quả theo xác suất từ ngữ $\rightarrow$ Dễ bị **Ảo giác (Hallucination)**, hướng dẫn sai lệch.

* **MCP (Model Context Protocol):**
  * Là **"Cổng USB-C mở quốc tế"** do Anthropic khởi xướng.
  * Gắn "tay chân" và "giác quan" vào bộ não AI qua đường ống `stdio` (JSON-RPC 2.0):
    1. 🦾 **Tay chân:** Chạy code thật trong hộp cát an toàn (`run_test_cases`, `trace_code_execution`).
    2. 🔬 **Kính hiển vi:** Soi cây cú pháp AST phát hiện vòng lặp, đệ quy, biến dồn (`analyze_code_ast`).
    3. 📒 **Sổ tay sư phạm:** Ghi nhớ tiến trình và năng lực từng sinh viên (`get_student_model`).

---

## 2. ⚡ 5 ĐIỂM "ĂN ĐỨT" AI TRUYỀN THỐNG

| Khía cạnh | ❌ AI Truyền Thống (Không MCP) | ✅ PyTutor-MCP |
| :--- | :--- | :--- |
| **1. Độ chính xác (Ground Truth)** | Đọc code và **đoán mò xác suất token** (dễ ảo giác). | Gọi MCP chạy code trên máy tính thật $\rightarrow$ **kết quả thật 100%**. |
| **2. An toàn máy chủ (Isolation)** | Chạy code trực tiếp trong web server $\rightarrow$ `while True` làm **sập server**. | MCP Server chạy tiến trình con độc lập $\rightarrow$ **tự ngắt sau 5s/3s**. |
| **3. Trí nhớ sư phạm (Memory)** | Stateless API: Gọi xong là **quên sạch sành sanh**. | Lưu vết học tập vào SQLite $\rightarrow$ biết học viên sai ở đâu để **leo thang gợi ý**. |
| **4. Khả năng mở rộng (Discovery)** | Muốn thêm tool phải **sửa lại code web backend**. | Thêm decorator `@mcp.tool()` $\rightarrow$ Host **tự khám phá qua `tools/list`**. |
| **5. Cắm đa nền tảng (Universal)** | Code dính chặt vào web, **không tái sử dụng được**. | Chuẩn mở USB-C $\rightarrow$ **cắm thẳng vào Cursor, Claude, VS Code**. |

---

## 3. 🛠️ 8 CÔNG CỤ MCP CHIA THEO 3 KHỐI CHỨC NĂNG

### 🔹 Khối 1: Thực thi & Phân tích Code (Ground Truth)
1. `run_test_cases`: Chạy Sandbox cô lập (timeout 5s), chấm PASS/FAIL từng test case.
2. `analyze_code_ast`: Mổ xẻ cây cú pháp tĩnh (vòng lặp for/while, đệ quy, biến tích lũy accumulator).
3. `trace_code_execution`: Truy vết từng dòng lệnh và giá trị biến số (max 150 bước / 3s).

### 🔹 Khối 2: Quản lý Ngân hàng Học liệu (SQLite)
4. `get_exercise_list`: Lấy danh mục bài tập theo độ khó từ SQLite.
5. `get_exercise_details`: Lấy đề bài Markdown, starter code và bộ test cases chuẩn.

### 🔹 Khối 3: Trí nhớ Sư phạm & Cá nhân hóa
6. `save_learning_event`: Lưu mã nguồn nộp, số test đạt và phản hồi AI vào SQLite.
7. `get_attempt_history`: Lấy 5 lần nộp gần nhất để AI không đưa ra gợi ý trùng lặp.
8. `get_student_model`: Tổng hợp bài đã làm chủ, bài đang vướng để cá nhân hóa độ khó.

---

## 4. 🎯 BỘ 3 CÂU HỎI "TỦ" CỦA HỘI ĐỒNG & CÁCH TRẢ LỜI CHỐT HẠ

### ❓ Q1: Sao không import hàm Python thẳng vào FastAPI mà phải dựng MCP Server?
> **Trả lời:**
> *"Thưa Thầy/Cô, lý do sống còn là **Cô lập Tiến trình (Process Isolation)**. Nếu import thẳng, sinh viên viết vòng lặp vô hạn `while True` hoặc ngốn RAM sẽ làm treo cứng toàn bộ Web Server. Với MCP, server chạy tiến trình độc lập qua pipe `stdio`, tự cưỡng chế ngắt an toàn sau 5 giây mà FastAPI không hề bị ảnh hưởng. Ngoài ra, chuẩn MCP giúp bộ công cụ này có thể cắm vào Claude Desktop hay Cursor IDE ngay lập tức."*

### ❓ Q2: Ném toàn bộ code vào Gemini có giải quyết được không?
> **Trả lời:**
> *"Thưa Thầy/Cô, **không thể**. LLM sinh từ theo xác suất từ ngữ chứ không phải trình biên dịch (Interpreter). Các bài báo khoa học đã chứng minh AI tự đoán kết quả code sai từ 35–45% ở các ca kiểm thử biên. MCP cung cấp dữ liệu thực tế (Ground Truth) từ máy tính để AI đưa ra lời giảng chính xác 100%."*

### ❓ Q3: Sinh viên nộp mã độc (`os.system('shutdown')`) thì hệ thống xử lý sao?
> **Trả lời:**
> *"Hệ thống phòng vệ theo 3 lớp:  
> 1. Cây cú pháp AST duyệt trước cấu trúc mã.  
> 2. Subprocess thực thi không có quyền quản trị và bị giới hạn timeout 5s.  
> 3. MCP Server chỉ giao tiếp dạng chuỗi văn bản JSON qua luồng `stdio`, hoàn toàn không mở cổng mạng ra ngoài."*
