# 🚀 PyTutor-MCP — Master Execution Prompt Phase 8: Trò chuyện Đa lượt & Đánh dấu Dòng Lỗi Trực quan

> **HƯỚNG DẪN:** Copy toàn bộ nội dung file này và paste vào phiên làm việc mới của AI Coding Assistant để kích hoạt thực thi Phase 8 tự động với chính sách **Zero-Question Policy**.

---

# MỆNH LỆNH THỰC THI PHASE 8: INTERACTIVE MULTI-TURN CHAT & MONACO ERROR LINE DECORATION

Bạn là Principal Software Engineer đang phụ trách triển khai **Phase 8** cho hệ thống Gia sư Thông minh **PyTutor-MCP**.
Trước khi bắt đầu, hãy đọc nhanh `PLAN.md`, `AI_HANDOFF_CONTEXT.md` và `plans/PLAN_8.0_INTERACTIVE_CHAT_AND_ERROR_HIGHLIGHT.md` ở thư mục gốc để nắm rõ kiến trúc hiện tại v3.1 Pro (7 MCP Tools, SQLite `pytutor.db`, JWT Auth Student/Instructor, Gemini 3.5 Flash Lite).

**QUY TẮC TỐI THƯỢNG (ZERO-QUESTION POLICY):**
TUYỆT ĐỐI KHÔNG hỏi lại bất kỳ câu hỏi nào. Hãy thực hiện tuần tự, trọn vẹn **5 Nhiệm vụ (Task 1 -> Task 5)** dưới đây, tự chạy kiểm thử trên terminal và chỉ kết thúc khi mọi bài test đều PASS 100% và `npm.cmd run build` đạt 0 errors.

---

## RÀNG BUỘC KỸ THUẬT & MÔI TRƯỜNG
1. **Môi trường:** Windows 11, Python 3.14 (lệnh `py`), Node.js v24.15.0 (`npm.cmd` và `npx.cmd`).
2. **UTF-8:** Giữ nguyên `PYTHONIOENCODING="utf-8"` cho mọi lệnh subprocess.
3. **Bảo toàn tính năng v3.1:** Không làm phá vỡ 7 MCP Tools hiện có, cơ chế lưu nháp `localStorage`, phím tắt `Ctrl+Enter` / `Ctrl+Shift+Enter` và hệ thống Auth JWT.

---

## NHIỆM VỤ 1: BACKEND SCHEMAS & LLM MULTI-TURN CHAT ENGINE (`backend/`)

1. **Cập nhật `backend/schemas.py`:**
   - Định nghĩa `ChatMessage(role: str, content: str, timestamp: Optional[str])`.
   - Định nghĩa `TutorChatRequest(exercise_id: str, code: str, session_id: str, user_message: str, history: List[ChatMessage] = [])`.
   - Định nghĩa `TutorChatResponse(reply: str, llm_source: str, updated_history: List[ChatMessage])`.
   - Định nghĩa `CustomRunRequest(exercise_id: Optional[str], code: str, custom_input: str)`.
   - Định nghĩa `CustomRunResponse(stdout: str, stderr: str, execution_time_ms: float, status: str, error_message: Optional[str])`.
2. **Cập nhật `backend/llm_service.py`:**
   - Xây dựng hàm `generate_chat_followup(exercise_details: dict, code: str, user_message: str, history: list, ast_summary: str = "") -> str`:
     - Sử dụng Google Gemini 3.5 Flash Lite qua `google-genai` SDK.
     - Ghép System Instruction: Nhập vai PyTutor AI, biết rõ đề bài, mã nguồn sinh viên đang làm, và nội dung câu hỏi làm rõ của sinh viên.
     - **ANTI-SPOIL GUARD TỐI THƯỢNG:** Tuyệt đối không bao giờ cung cấp mã nguồn giải hoàn chỉnh. Chỉ giải thích thắc mắc, phân tích bản chất logic và hướng dẫn sinh viên tự gõ từng dòng lệnh.
     - Tự động cắt ngắn lịch sử chat nếu dài hơn 6 lượt để tiết kiệm quota.

---

## NHIỆM VỤ 2: FASTAPI ENDPOINTS CHO CHAT VÀ CHẠY THỬ CUSTOM INPUT (`backend/main.py`)

1. **Endpoint `POST /api/tutor/chat`:**
   - Nhận payload `TutorChatRequest`.
   - Lấy thông tin bài tập qua `mcp_client.get_exercise_details_via_mcp`.
   - Gọi `llm_service.generate_chat_followup`.
   - Cập nhật và trả về `TutorChatResponse` kèm danh sách lịch sử hội thoại mới nhất.
2. **Endpoint `POST /api/custom-run`:**
   - Nhận payload `CustomRunRequest`.
   - Sử dụng MCP tool `run_test_cases` với một test case duy nhất chứa `input: custom_input` và `expected_output: None`.
   - Đo đạc thời gian thực thi (ms) và bắt các trường hợp `TIMEOUT` (nếu chạy quá 5s) hoặc `RUNTIME_ERROR`.
   - Trả về `CustomRunResponse`.

---

## NHIỆM VỤ 3: MONACO EDITOR ERROR LINE DECORATION TRỰC QUAN (`frontend/src/components/EditorPanel.jsx`)

1. **Trích xuất số dòng lỗi từ thông báo lỗi:**
   - Viết hàm `parseErrorLine(errorMessage)` nhận vào chuỗi lỗi của Python (ví dụ `SyntaxError ... line 3` hoặc `File "solution.py", line 4`) và trả về số dòng `int`.
2. **Tô màu đỏ cảnh báo trên dòng lỗi:**
   - Khi chạy thử hoặc nộp bài mà gặp lỗi (`SYNTAX_ERROR`, `RUNTIME_ERROR` hoặc `FAIL`), tự động gọi `editor.deltaDecorations` để:
     - Thêm vệt màu đỏ nhẹ làm nổi bật toàn bộ dòng code bị lỗi (`bg-rose-500/20 border-l-4 border-rose-500`).
     - Hiển thị tooltip giải thích lỗi khi rê chuột vào dòng code đó (`hoverMessage`).
3. **Tự động xóa cảnh báo khi sửa code:**
   - Lắng nghe sự kiện `editor.onDidChangeModelContent`: Ngay khi sinh viên gõ phím sửa code, lập tức xóa các vệt highlight đỏ để không làm phiền học viên.

---

## NHIỆM VỤ 4: GIAO DIỆN MULTI-TURN CHAT & CUSTOM INPUT PLAYGROUND (`frontend/`)

1. **Nâng cấp Cột 3 (`TutorPanel.jsx`):**
   - Bên dưới phần gợi ý sư phạm hiện tại, bổ sung khu vực **"Trò chuyện làm rõ với Gia sư"**:
     - Hiển thị danh sách các tin nhắn trao đổi tiếp nối dạng bong bóng chat đẹp mắt.
     - Ô nhập tin nhắn: `<input type="text" placeholder="Hỏi thêm Gia sư về bài làm..." />` kèm nút Gửi (`Send`).
     - Hỗ trợ phím tắt `Enter` để gửi tin nhắn.
     - Hiển thị hiệu ứng chờ khi AI đang suy nghĩ.
2. **Nâng cấp Cột 2 (`EditorPanel.jsx`):**
   - Phía trên bảng kết quả kiểm thử, bổ sung 2 Tab chuyển đổi:
     - Tab 1: **`🧪 Bộ test chuẩn`** (hiển thị danh sách test cases như hiện tại).
     - Tab 2: **`💻 Tự nhập dữ liệu (Custom Stdin)`** (cho phép sinh viên gõ dữ liệu bất kỳ vào `textarea`, bấm nút **`▶ Chạy với dữ liệu này`** và xem kết quả in ra màn hình `stdout`).

---

## NHIỆM VỤ 5: KIỂM THỬ TỰ ĐỘNG & XÁC NHẬN BUILD

1. Tạo file kiểm thử tự động `test_phase8_chat.py` kiểm chứng:
   - Endpoint `POST /api/tutor/chat` phản hồi thông minh và tuân thủ Anti-Spoil Guard.
   - Endpoint `POST /api/custom-run` chạy chuẩn xác dữ liệu mẫu và ngắt đúng timeout với vòng lặp vô hạn.
2. Chạy các lệnh kiểm tra:
   - `py test_phase8_chat.py`
   - `py -m backend.test_backend_e2e`
   - `cd frontend && npm.cmd run build` (xác nhận 0 errors).
3. Cập nhật `PLAN.md` và `AI_HANDOFF_CONTEXT.md` chuyển trạng thái Phase 8 thành **✅ PASSED**.

**BẮT ĐẦU THỰC HIỆN NGAY NHIỆM VỤ 1 ĐẾN NHIỆM VỤ 5!**
