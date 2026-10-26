# 🚀 PyTutor-MCP — Master Execution Prompt Phase 9: Trực quan hóa Từng bước Thực thi & Cây Lộ trình Kỹ năng Đồ họa

> **HƯỚNG DẪN:** Copy toàn bộ nội dung file này và paste vào phiên làm việc mới của AI Coding Assistant để kích hoạt thực thi Phase 9 tự động với chính sách **Zero-Question Policy**.

---

# MỆNH LỆNH THỰC THI PHASE 9: EXECUTION STEP VISUALIZER (MCP TOOL 8) & INTERACTIVE SKILL ROADMAP

Bạn là Principal Software Engineer đang phụ trách triển khai **Phase 9** cho hệ thống Gia sư Thông minh **PyTutor-MCP**.
Trước khi bắt đầu, hãy đọc nhanh `PLAN.md`, `AI_HANDOFF_CONTEXT.md` và `plans/PLAN_9.0_EXECUTION_VISUALIZER_AND_ROADMAP.md` ở thư mục gốc để nắm rõ kiến trúc hiện tại v3.2 Pro (7 MCP Tools, SQLite `pytutor.db`, JWT Auth Student/Instructor, Gemini 3.5 Flash Lite, Multi-turn Chat, Monaco Error Decoration, Custom Stdin Playground).

**QUY TẮC TỐI THƯỢNG (ZERO-QUESTION POLICY):**
TUYỆT ĐỐI KHÔNG hỏi lại bất kỳ câu hỏi nào. Hãy thực hiện tuần tự, trọn vẹn **5 Nhiệm vụ (Task 1 -> Task 5)** dưới đây, tự chạy kiểm thử trên terminal và chỉ kết thúc khi mọi bài test đều PASS 100% và `npm.cmd run build` đạt 0 errors.

---

## RÀNG BUỘC KỸ THUẬT & MÔI TRƯỜNG
1. **Môi trường:** Windows 11, Python 3.14 (lệnh `py`), Node.js v24.15.0 (`npm.cmd` và `npx.cmd`).
2. **UTF-8:** Giữ nguyên `PYTHONIOENCODING="utf-8"` cho mọi lệnh subprocess.
3. **Bảo toàn tính năng v3.2:** Tuyệt đối không làm ảnh hưởng đến 7 MCP Tools hiện có, cơ chế Multi-turn Chat, Monaco Error Decoration, Auto-save draft, và Auth JWT.

---

## NHIỆM VỤ 1: XÂY DỰNG MCP TOOL THỨ 8 `trace_code_execution` (`mcp_server/`)

1. **Tạo module `mcp_server/tracer.py`:**
   - Sử dụng cơ chế tracing tiêu chuẩn (`sys.settrace`) chạy trong sandbox cô lập.
   - Ghi nhận từng frame `ExecutionStep`: `{ step: int, line: int, event: str, func_name: str, locals: dict[str, str], stdout: str }`.
   - Giới hạn an toàn: Tối đa 150 bước, chuỗi giá trị biến tối đa 80 ký tự, timeout 3.0 giây để chống treo và chống vòng lặp vô hạn.
2. **Đăng ký Tool 8 vào `mcp_server/server.py`:**
   - Thêm `@mcp.tool() def trace_code_execution(code: str, stdin_input: str = "", max_steps: int = 100) -> dict`.
   - Xác nhận `tools/list` phát hiện đủ **8 MCP Tools**.

---

## NHIỆM VỤ 2: BACKEND SCHEMAS & ENDPOINTS CHO TRACING VÀ ROADMAP (`backend/`)

1. **Cập nhật `backend/schemas.py`:**
   - Định nghĩa `TraceStepItem(step: int, line: int, event: str, func_name: str, locals: dict[str, str], stdout: str)`.
   - Định nghĩa `TraceExecutionRequest(code: str, stdin_input: str = "", max_steps: int = 100)`.
   - Định nghĩa `TraceExecutionResponse(success: bool, total_steps: int, code_lines: list[str], steps: list[TraceStepItem], error: Optional[str])`.
   - Định nghĩa `SkillNode(id: str, title: str, category: str, difficulty: str, prerequisites: list[str], status: str)`.
   - Định nghĩa `SkillRoadmapResponse(nodes: list[SkillNode], total_mastered: int, total_exercises: int)`.
2. **Cập nhật `backend/mcp_client.py`:**
   - Thêm hàm `execute_trace_pipeline(code: str, stdin_input: str = "")` gọi MCP tool `trace_code_execution` qua JSON-RPC stdio.
3. **Cập nhật `backend/main.py`:**
   - Thêm endpoint `POST /api/trace-execution`: nhận request, gọi MCP tool 8, trả về danh sách bước.
   - Thêm endpoint `GET /api/skill-roadmap`: tổng hợp cây kỹ năng theo độ phụ thuộc giữa các bài tập (biến/nhập xuất -> rẽ nhánh -> vòng lặp -> chuỗi -> hàm/đệ quy) kết hợp dữ liệu `mastered_exercises` của session học viên.

---

## NHIỆM VỤ 3: GIAO DIỆN THANH TRƯỢT VISUALIZER TRÊN FRONTEND (`frontend/`)

1. **Tạo component `frontend/src/components/ExecutionVisualizerModal.jsx`:**
   - Hiển thị thanh điều hướng:
     - Nút `[⏮️ Bắt đầu] [◀ Lùi 1 bước] [▶ Tiếp 1 bước] [⏭️ Cuối]`.
     - Nút `[⏯️ Tự chạy (Auto-play 1.2s/bước)]`.
     - Thanh trượt Slider: Kéo trực tiếp để nhảy đến bước `X / Y`.
   - Khung theo dõi biến số (Variables Table): Hiển thị `Tên biến | Kiểu dữ liệu | Giá trị`, biến vừa thay đổi giá trị được làm nổi bật (highlight xanh ngọc).
   - Khung xem mã nguồn kèm con trỏ mũi tên `▶` và viền sáng chỉ vào dòng lệnh đang thực thi ở bước hiện tại.
   - Khung `stdout` hiển thị dữ liệu in ra màn hình tính đến bước đó.
2. **Tích hợp nút kích hoạt trên `EditorPanel.jsx`:**
   - Thêm nút **`👁️ Chạy từng bước (Visualizer)`** trên toolbar của Editor, bấm vào mở modal Visualizer.

---

## NHIỆM VỤ 4: GIAO DIỆN CÂY LỘ TRÌNH KỸ NĂNG ĐỒ HỌA (`frontend/`)

1. **Tạo component `frontend/src/components/SkillRoadmapModal.jsx`:**
   - Hiển thị cây lộ trình học tập trực quan dạng các thẻ kỹ năng phân tầng:
     - Tầng 1: Nhập xuất & Biến cơ bản (`ex_01_sum_1_to_n`)
     - Tầng 2: Cấu trúc Rẽ nhánh & Điều kiện (`ex_02_prime_check`)
     - Tầng 3: Vòng lặp & Đệ quy (`ex_03_factorial`)
     - Tầng 4: Xử lý Chuỗi & Chỉ mục (`ex_04_reverse_string`, `ex_05_count_vowels`)
   - Trạng thái trực quan:
     - 🟢 **Đã làm chủ (Mastered):** Đạt 100% test cases.
     - 🟡 **Đang thử sức (In Progress):** Đã nộp thử.
     - 🔒 **Khóa (Locked):** Cần hoàn thành bài trước.
   - Bấm vào nút chuyển thẳng đến bài tập tương ứng trong IDE và đóng modal.
2. **Tích hợp nút mở Lộ trình trên `Header.jsx`:**
   - Thêm nút **`🗺️ Cây kỹ năng`** cạnh nút `📒 Nhật ký học tập`.

---

## NHIỆM VỤ 5: KIỂM THỬ TỰ ĐỘNG & XÁC NHẬN BUILD

1. Tạo file kiểm thử tự động `test_phase9_visualizer.py`:
   - Xác nhận MCP Server phát hiện đủ **8 MCP Tools**.
   - Kiểm thử tracing thuật toán tính tổng 1 đến 3 (ghi lại đúng các bước và giá trị biến).
   - Kiểm thử tracing đệ quy `giaithua(3)` bắt đúng frame `call` và `return`.
   - Kiểm thử tracing vòng lặp vô hạn `while True:` tự dừng an toàn ở bước 150.
   - Kiểm thử endpoint `GET /api/skill-roadmap` trả về đúng các nodes.
2. Chạy:
   - `py test_phase9_visualizer.py`
   - `py -m backend.test_backend_e2e`
   - `cd frontend && npm.cmd run build` (0 errors).
3. Cập nhật `PLAN.md` và `AI_HANDOFF_CONTEXT.md` chuyển trạng thái Phase 9 thành **✅ PASSED**.

**BẮT ĐẦU THỰC HIỆN NGAY NHIỆM VỤ 1 ĐẾN NHIỆM VỤ 5!**
