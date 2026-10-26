# 📋 KẾ HOẠCH TRIỂN KHAI CHI TIẾT: PHASE 9.0
# TRỰC QUAN HÓA TỪNG BƯỚC THỰC THI (MCP TOOL 8) & CÂY LỘ TRÌNH KỸ NĂNG ĐỒ HỌA
## (PYTHON EXECUTION STEP VISUALIZER & SKILL ROADMAP TREE)

> **Mã kế hoạch:** `PLAN_9.0`  
> **Trạng thái:** ✅ **ĐÃ HOÀN THÀNH 100% (PASSED)**  
> **Áp dụng cho:** `mcp_server/`, `backend/`, `frontend/src/components/`  
> **Định hướng:** Xây dựng Công cụ MCP thứ 8 `trace_code_execution` ghi lại sự biến thiên của bộ nhớ/biến số qua từng dòng lệnh (tương tự PythonTutor.com), tích hợp thanh trượt Step Visualizer trong Monaco Editor và Cây kỹ năng đồ họa phân cấp (Skill Roadmap Tree) để định hướng học tập.

---

## 1. 🔍 BỐI CẢNH KỸ THUẬT & PHÂN TÍCH VẤN ĐỀ

### 1.1. Khó khăn Tư duy Trừu tượng của Người mới học Python
- Khi học lập trình cơ bản, sinh viên gặp khó khăn lớn nhất ở việc hình dung **"Bên trong bộ nhớ máy tính đang diễn ra điều gì?"**.
- Một vòng lặp `for i in range(1, n + 1): tong += i` tuy chỉ có 2 dòng code nhưng làm biến `i` và `tong` biến đổi liên tục qua từng vòng lặp. Hiện tại học viên chỉ thấy kết quả cuối cùng in ra màn hình hoặc lỗi, không thể quan sát giá trị của `tong` và `i` ở bước thứ 3 là bao nhiêu.
- Đây chính là lý do công cụ học tập nổi tiếng thế giới **PythonTutor.com** của GS. Philip Guo (UC San Diego) được sử dụng rộng rãi trong các trường đại học. Việc tích hợp khả năng này trực tiếp vào hệ thống PyTutor thông qua giao thức MCP sẽ nâng tầm giá trị học thuật của đồ án tốt nghiệp lên mức xuất sắc!

### 1.2. Thiếu Lộ trình Định hướng Kỹ năng (Skill Tree Disorientation)
- Danh mục bài tập hiện tại chỉ là một danh sách thả xuống (dropdown) phẳng: Bài 1, 2, 3, 4, 5...
- Sinh viên không nhìn thấy được mối quan hệ logic giữa các bài tập: Bài nào là điều kiện tiên quyết (prerequisite) của bài nào? Khi nào thì sẵn sàng chuyển sang bài đệ quy hay cấu trúc dữ liệu?
- **Giải pháp:** Xây dựng Cây kỹ năng lập trình dạng đồ thị có hướng (Directed Acyclic Graph - DAG) phản ánh trực quan tiến độ của từng học viên.

---

## 2. 🏛️ THIẾT KẾ KIẾN TRÚC MCP TOOL 8: `trace_code_execution`

### 2.1. Cơ chế Hoạt động của Tracing Engine (`mcp_server/tracer.py`)
- Python cung cấp hàm nội tại `sys.settrace(tracer_function)` cho phép theo dõi mọi sự kiện thực thi trong quá trình chạy.
- Một tiến trình con (subprocess) an toàn được khởi tạo với bộ lọc `tracer`:
  - **Sự kiện ghi nhận:** `line` (chuyển dòng), `call` (gọi hàm), `return` (thoát hàm).
  - **Dữ liệu snapshot ở mỗi bước (Step Frame):**
    - `step`: Số thứ tự bước (1, 2, 3...).
    - `line`: Dòng mã nguồn đang chuẩn bị chạy.
    - `event`: Tên sự kiện (`line` / `call` / `return`).
    - `func_name`: Tên hàm đang thực thi (hoặc `<module>`).
    - `locals`: Snapshot từ điển chứa các biến cục bộ tại thời điểm đó (`{var_name: {"type": "int", "value": "15"}}`).
    - `stdout`: Dữ liệu đã in ra màn hình tính đến thời điểm này.
- **Ràng buộc An toàn & Chống quá tải Bộ nhớ (Safety Bounds):**
  - Giới hạn tối đa **150 bước thực thi** (sau 150 bước tự động ngắt và trả về cờ `truncated: true`).
  - Giới hạn độ dài chuỗi giá trị biến tối đa **80 ký tự** (tránh string quá dài làm tràn JSON).
  - Bỏ qua các frame của thư viện nội bộ Python (`importlib`, `encodings`...).
  - Áp dụng Sandbox Timeout **3.0 giây** để chống lặp vô hạn.

### 2.2. Đặc tả JSON-RPC 2.0 Tool Schema: `trace_code_execution`

```json
{
  "name": "trace_code_execution",
  "description": "Thực thi mã nguồn Python và ghi lại từng bước thay đổi của biến số và con trỏ dòng lệnh phục vụ trực quan hóa (Execution Visualizer).",
  "inputSchema": {
    "type": "object",
    "properties": {
      "code": {
        "type": "string",
        "description": "Mã nguồn Python cần chạy từng bước"
      },
      "stdin_input": {
        "type": "string",
        "description": "Dữ liệu đầu vào giả lập (input)",
        "default": ""
      },
      "max_steps": {
        "type": "integer",
        "description": "Giới hạn số bước thực thi tối đa (mặc định 100)",
        "default": 100
      }
    },
    "required": ["code"]
  }
}
```

### 2.3. Cấu trúc Dữ liệu Phản hồi (Step Trace Output Model)

```json
{
  "success": true,
  "total_steps": 12,
  "code_lines": ["n = int(input())", "tong = 0", "for i in range(1, n + 1):", "    tong += i", "print(tong)"],
  "steps": [
    { "step": 1, "line": 1, "event": "line", "locals": {}, "stdout": "" },
    { "step": 2, "line": 2, "event": "line", "locals": {"n": "3"}, "stdout": "" },
    { "step": 3, "line": 3, "event": "line", "locals": {"n": "3", "tong": "0"}, "stdout": "" },
    { "step": 4, "line": 4, "event": "line", "locals": {"n": "3", "tong": "0", "i": "1"}, "stdout": "" },
    { "step": 5, "line": 3, "event": "line", "locals": {"n": "3", "tong": "1", "i": "1"}, "stdout": "" },
    { "step": 6, "line": 4, "event": "line", "locals": {"n": "3", "tong": "1", "i": "2"}, "stdout": "" },
    { "step": 7, "line": 3, "event": "line", "locals": {"n": "3", "tong": "3", "i": "2"}, "stdout": "" },
    { "step": 8, "line": 4, "event": "line", "locals": {"n": "3", "tong": "3", "i": "3"}, "stdout": "" },
    { "step": 9, "line": 5, "event": "line", "locals": {"n": "3", "tong": "6", "i": "3"}, "stdout": "" },
    { "step": 10, "line": 5, "event": "return", "locals": {"n": "3", "tong": "6", "i": "3"}, "stdout": "6\n" }
  ]
}
```

---

## 3. 📋 CHI TIẾT TỪNG NHIỆM VỤ TRIỂN KHAI (TASKS)

### Task 9.1 — Xây dựng Bộ ghi vết Thực thi `mcp_server/tracer.py`
- Tạo module `mcp_server/tracer.py`:
  - Lớp `CodeTracer`: Quản lý frame trace, ghi đè `sys.stdout` và `sys.stdin`.
  - Hàm `trace_code_execution(code, stdin_input, max_steps)`: Chạy code qua `exec()` trong namespace cô lập có bảo vệ timeout.
  - Xử lý ngoại lệ an toàn nếu code bị lỗi cú pháp hoặc runtime error giữa chừng.

### Task 9.2 — Đăng ký MCP Tool thứ 8 vào `mcp_server/server.py`
- Khai báo tool thứ 8: `trace_code_execution` trong danh mục `tools/list`.
- Xử lý request trong `handle_call_tool`:
  - Nhận tham số: `code`, `stdin_input`, `max_steps`.
  - Gọi `tracer.trace_code_execution()`.
  - Trả về JSON serialized payload qua giao thức stdio.

### Task 9.3 — Backend Integration & Endpoint `/api/trace`
- Bổ sung vào [`backend/mcp_client.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/mcp_client.py): Hàm `execute_trace_pipeline(code, stdin_input)`.
- Bổ sung vào [`backend/main.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/main.py): Endpoint `POST /api/trace`:
  - Request: `{ code: str, stdin_input: str }`.
  - Response: Cấu trúc mảng `steps` kèm thông tin biến và stdout.

### Task 9.4 — Giao diện Thanh trượt Visualizer (`ExecutionVisualizer.jsx`)
- Tạo component `frontend/src/components/ExecutionVisualizer.jsx`:
  - **Thanh điều hướng:**
    - Nút `[⏮️ Bắt đầu] [◀ Lùi 1 bước] [▶ Tiếp 1 bước] [⏭️ Cuối]`.
    - Nút `[⏯️ Tự động chạy (Auto-play)]`: Tự động nhảy 1 bước mỗi 1.2 giây.
    - Thanh trượt Slider: Kéo trực tiếp để nhảy đến bước bất kỳ: `Bước ${currentStep} / ${totalSteps}`.
  - **Bảng Theo dõi Biến số (Variables Watch Window):**
    - Danh sách các biến: `Tên biến | Kiểu dữ liệu | Giá trị`.
    - Biến có giá trị vừa thay đổi ở bước này được bôi viền vàng hoặc xanh lá nổi bật.
  - **Tương tác với Monaco Editor:**
    - Sử dụng `editor.deltaDecorations` để tạo một dải sáng màu xanh dương mềm (`bg-cyan-500/20`) trên dòng code đang thực thi ở bước hiện tại, kèm con trỏ mũi tên `▶` ở lề trái (glyph margin).

### Task 9.5 — Cây Kỹ năng Lập trình Đồ họa (`SkillRoadmapModal.jsx`)
- Xây dựng component `frontend/src/components/SkillRoadmapModal.jsx`:
  - Sơ đồ trực quan dạng cây phân nhánh:
    - Nhánh 1: *Cơ bản & Nhập xuất* (`ex_01_sum_1_to_n`)
    - Nhánh 2: *Cấu trúc Rẽ nhánh & Logic* (`ex_02_prime_check`)
    - Nhánh 3: *Vòng lặp & Đệ quy* (`ex_03_factorial`)
    - Nhánh 4: *Thao tác Chuỗi & Chỉ mục* (`ex_04_reverse_string`, `ex_05_count_vowels`)
  - Trạng thái nút:
    - 🟢 **Đã làm chủ (Mastered):** Vượt qua 100% test cases.
    - 🟡 **Đang thử sức (In Progress):** Đã có lần nộp nhưng chưa pass.
    - 🔒 **Khóa (Locked):** Cần hoàn thành bài trước để mở khóa.
  - Khi bấm vào nút: Tự động chuyển bài tập trong IDE và đóng modal.

---

## 4. 🛡️ QUY TẮC AN TOÀN & XỬ LÝ NGOẠI LỆ

1. **Chống Treo Trình duyệt do Dữ liệu Tracing Quá Lớn:**
   - Nếu chương trình lặp 1000 lần, việc gửi 1000 bước về frontend sẽ làm đơ trình duyệt. Cố định trần `max_steps = 150`.
   - Các biến dạng danh sách (`list`) dài hơn 10 phần tử được rút gọn thành `[1, 2, 3, ... (100 phần tử)]`.
2. **Ngăn chặn Lệnh Nguy hiểm trong Tracing:**
   - Vô hiệu hóa các module hệ thống `os`, `shutil`, `subprocess` trong namespace thực thi của `tracer`.

---

## 5. 🧪 KỊCH BẢN KIỂM THỬ XÁC NHẬN

Tạo file kiểm thử `test_phase9_visualizer.py`:
- [ ] **TC 9.1:** Tracing thuật toán tính tổng 1 đến 3 cho ra đúng 10 bước lặp, biến `tong` tăng dần: `0 -> 1 -> 3 -> 6`.
- [ ] **TC 9.2:** Tracing hàm đệ quy `giaithua(3)` ghi nhận đúng các frame sự kiện `call` và `return`.
- [ ] **TC 9.3:** Tracing vòng lặp vô hạn `while True:` tự động dừng ở bước thứ 150 mà không làm crash server.
- [ ] **TC 9.4:** MCP Server Discovery tự động phát hiện đủ **8 MCP Tools**.
- [ ] **TC 9.5:** Frontend `npm.cmd run build` biên dịch 0 lỗi.
