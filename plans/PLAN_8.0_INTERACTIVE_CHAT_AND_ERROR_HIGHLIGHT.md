# 📋 KẾ HOẠCH TRIỂN KHAI CHI TIẾT: PHASE 8.0
# TRÒ CHUYỆN TƯƠNG TÁC ĐA LƯỢT VỚI GIA SƯ AI & ĐÁNH DẤU DÒNG LỖI TRỰC QUAN TRÊN MONACO EDITOR
## (INTERACTIVE MULTI-TURN CHAT & IN-EDITOR ERROR DECORATION)

> **Mã kế hoạch:** `PLAN_8.0`  
> **Trạng thái:** ✅ **100% HOÀN THÀNH & ĐÃ KIỂM THỬ ĐẠT CHUẨN (PASSED)**  
> **Áp dụng cho:** `backend/`, `frontend/src/components/`, `frontend/src/services/`  
> **Định hướng:** Chuyển hóa Cột 3 từ dạng đọc gợi ý thụ động 1 chiều thành luồng đối thoại tương tác đa lượt 2 chiều (Multi-turn Chat) với Gia sư AI, tích hợp cơ chế tô đỏ trực quan dòng code bị lỗi trực tiếp trong trình soạn thảo Monaco, và bổ sung Playground tự nhập dữ liệu kiểm thử (Custom Stdin).

---

## 1. 🔍 BỐI CẢNH KỸ THUẬT & PHÂN TÍCH VẤN ĐỀ

Sau khi hoàn thành Phase 7, giao diện học tập của sinh viên đã tinh gọn và thân thiện hơn rất nhiều. Tuy nhiên, khi quan sát hành vi thực tế của người mới học lập trình, 3 khoảng trống kỹ thuật lớn tiếp tục xuất hiện:

### 1.1. Luồng Gợi ý Đơn Hướng (One-way Passive Feedback Gap)
- Hiện tại, khi sinh viên bấm *"Hỏi Gia sư AI"*, hệ thống chỉ trả về duy nhất 1 đoạn văn bản gợi ý tương ứng với mức đã chọn (Level 1, 2 hoặc 3).
- **Vấn đề phát sinh:** Nếu sinh viên đọc gợi ý nhưng chưa hiểu rõ một thuật ngữ hoặc thắc mắc *"Tại sao vòng lặp của em lại chạy thiếu 1 đơn vị?"*, các em không có cách nào hỏi lại! Việc phải bấm lại nút nộp bài sẽ tạo ra một lần nộp mới (tăng số lần nộp bài không cần thiết trong database) và AI lại sinh ra một bài phản hồi từ đầu thay vì giải đáp thắc mắc tiếp nối.
- **Giải pháp:** Cần xây dựng **Multi-turn Follow-up Chat Session** duy trì ngữ cảnh bài làm hiện tại, cho phép sinh viên gõ câu hỏi phản hồi tự nhiên ngay dưới khung gợi ý.

### 1.2. Mù Số Dòng Lỗi (Error Stack Trace Blindness)
- Khi code của sinh viên bị lỗi cú pháp (`SyntaxError: invalid syntax`) hoặc lỗi thời gian chạy (`ZeroDivisionError`, `IndexError`), thông báo lỗi chỉ xuất hiện dưới dạng chuỗi văn bản nhỏ ở bảng kết quả kiểm thử: `File "solution.py", line 4: ...`.
- Người mới học thường rất bối rối, phải tự dò bằng mắt xem dòng số 4 trên trình soạn thảo nằm ở đâu.
- **Giải pháp:** Tận dụng API **Monaco Editor Line Decoration** (`deltaDecorations`) để tự động tô dải màu đỏ cảnh báo trên dòng code bị lỗi và hiển thị tooltip giải thích lỗi ngay khi rê chuột vào.

### 1.3. Thiếu Môi trường Tự Thử nghiệm (Custom Input Playground)
- Hiện tại, sinh viên chỉ có thể chạy code đối chiếu với bộ test cases có sẵn của hệ thống.
- Nếu sinh viên muốn tự thử nhập $n = 100$ hoặc một chuỗi đặc biệt để xem code của mình in ra cái gì, hiện chưa có ô nào để nhập `stdin`.
- **Giải pháp:** Bổ sung tab **"Tự nhập dữ liệu (Custom Stdin)"** bên cạnh tab "Bộ test chuẩn" ở Cột 2.

---

## 2. 🏛️ THIẾT KẾ KIẾN TRÚC HỆ THỐNG & ĐẶC TẢ SCHEMA

### 2.1. Kiến trúc Luồng Dữ liệu Đa Lượt (Multi-turn Interaction Architecture)

```text
[Sinh viên gõ câu hỏi vào ô Chat ở Cột 3]
       │
       │  POST /api/tutor/chat
       │  Payload: { exercise_id, code, session_id, message, conversation_history }
       ▼
[FastAPI: backend/main.py]
       │
       ├──► Kiểm tra Rate Limit & Cache (Tránh spam API)
       │
       ├──► Nạp bối cảnh từ MCP Server (tools/call):
       │    ├── get_exercise_details (Nắm rõ đề bài & test cases)
       │    └── get_student_model (Nắm rõ trình độ học viên)
       │
       └──► [backend/llm_service.py: generate_chat_followup]
            │
            ├── Ghép System Instruction (Nhập vai Gia sư Socratic, KHÔNG lộ code giải)
            ├── Ghép Lịch sử hội thoại (History: user - assistant turns)
            ├── Gửi request đến Gemini 3.5 Flash Lite qua SDK `google-genai`
            └── Trả về câu trả lời sư phạm súc tích, định hướng tư duy
       ▼
[Frontend: TutorPanel.jsx]
       │ Render bong bóng chat người dùng & trợ lý mượt mà (smooth auto-scroll)
```

### 2.2. Đặc tả Schemas Backend (`backend/schemas.py`)

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' hoặc 'assistant'")
    content: str = Field(..., description="Nội dung tin nhắn")
    timestamp: Optional[str] = None

class TutorChatRequest(BaseModel):
    exercise_id: str
    code: str
    session_id: str
    user_message: str
    history: List[ChatMessage] = []

class TutorChatResponse(BaseModel):
    reply: str
    llm_source: str
    updated_history: List[ChatMessage]

class CustomRunRequest(BaseModel):
    exercise_id: Optional[str] = None
    code: str
    custom_input: str

class CustomRunResponse(BaseModel):
    stdout: str
    stderr: str
    execution_time_ms: float
    status: str  # 'SUCCESS', 'RUNTIME_ERROR', 'TIMEOUT'
    error_message: Optional[str] = None
```

### 2.3. Thuật toán Trích xuất Số dòng Lỗi (Error Line Parsing)
Để gắn decoration lên Monaco Editor, frontend phân tích chuỗi lỗi thông qua Regex:
```javascript
export function parseErrorLine(errorMessage) {
  if (!errorMessage) return null;
  
  // Mẫu 1: SyntaxError line x
  const syntaxMatch = errorMessage.match(/line\s+(\d+)/i);
  if (syntaxMatch) return parseInt(syntaxMatch[1], 10);
  
  // Mẫu 2: Traceback File "solution.py", line x
  const tbMatch = errorMessage.match(/File\s+["'][^"']+["'],\s+line\s+(\d+)/i);
  if (tbMatch) return parseInt(tbMatch[1], 10);
  
  return null;
}
```

---

## 3. 📋 CHI TIẾT TỪNG NHIỆM VỤ TRIỂN KHAI (TASKS)

### Task 8.1 — Backend Schemas & LLM Service Chat Engine
**Files cần chỉnh sửa:**
- [`backend/schemas.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/schemas.py): Thêm các models `ChatMessage`, `TutorChatRequest`, `TutorChatResponse`, `CustomRunRequest`, `CustomRunResponse`.
- [`backend/llm_service.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/llm_service.py): Bổ sung hàm `generate_chat_followup`:
  ```python
  def generate_chat_followup(
      exercise_details: dict,
      code: str,
      user_message: str,
      history: list,
      ast_summary: str = ""
  ) -> str:
      """
      Sinh phản hồi cho câu hỏi làm rõ của sinh viên.
      Giữ vững nguyên tắc Anti-Spoil: Không đưa ra đoạn code hoàn chỉnh.
      Giải thích thấu cảm, khích lệ và chỉ ra bản chất vấn đề.
      """
  ```

### Task 8.2 — FastAPI Endpoints & Endpoint Chạy Thử Custom Input
**Files cần chỉnh sửa:**
- [`backend/main.py`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/backend/main.py):
  1. Thêm endpoint `POST /api/tutor/chat`:
     - Nhận payload `TutorChatRequest`.
     - Gọi `generate_chat_followup`.
     - Trả về `TutorChatResponse`.
  2. Thêm endpoint `POST /api/custom-run`:
     - Nhận payload `CustomRunRequest`.
     - Sử dụng MCP tool `run_test_cases` với test case tùy biến chứa `custom_input`.
     - Trả về `CustomRunResponse` với đầu ra thực tế hoặc lỗi thời gian chạy.

### Task 8.3 — Monaco Editor Error Line Decoration
**Files cần chỉnh sửa:**
- [`frontend/src/components/EditorPanel.jsx`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/frontend/src/components/EditorPanel.jsx):
  - Khai báo state lưu trữ `decorations` ref: `decorationsRef = useRef([])`.
  - Khi có kết quả test case bị `FAIL`, `SYNTAX_ERROR` hoặc `RUNTIME_ERROR`:
    - Gọi `parseErrorLine(r.error_message)`.
    - Dùng `editor.deltaDecorations(decorationsRef.current, [{ range: new monaco.Range(line, 1, line, 1), options: { isWholeLine: true, className: 'bg-rose-500/20 border-l-4 border-rose-500', hoverMessage: { value: r.error_message } } }])`.
  - Tự động xóa vệt đỏ khi sinh viên thay đổi nội dung code (`onDidChangeModelContent`).

### Task 8.4 — Giao diện Multi-turn Chat ở Cột 3
**Files cần chỉnh sửa:**
- [`frontend/src/components/TutorPanel.jsx`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/frontend/src/components/TutorPanel.jsx):
  - Bên dưới phần gợi ý, hiển thị danh sách tin nhắn tiếp nối (bong bóng chat màu xám cho sinh viên, màu xanh đen cho Gia sư AI).
  - Ô nhập liệu tin nhắn: `<input type="text" placeholder="Hỏi thêm Gia sư về bài làm..." />` kèm nút gửi (icon `Send`).
  - Phím tắt `Enter` gửi tin nhắn nhanh.
  - Hiệu ứng ba chấm động (`typing indicator`) khi AI đang suy nghĩ phản hồi.

### Task 8.5 — Tab Custom Input Playground ở Cột 2
**Files cần chỉnh sửa:**
- [`frontend/src/components/EditorPanel.jsx`](file:///c:/Users/Admin/Downloads/Sales-support-AI-pilot/frontend/src/components/EditorPanel.jsx):
  - Phía trên bảng kết quả kiểm thử, bổ sung 2 tab chuyển đổi:
    - Tab 1: `🧪 Bộ test chuẩn (${total_tests})`
    - Tab 2: `💻 Tự nhập dữ liệu (Custom Stdin)`
  - Khi chọn Tab 2: Hiển thị 1 `textarea` để sinh viên gõ dữ liệu đầu vào tùy ý và 1 nút `▶ Chạy thử với dữ liệu này`.
  - Hiển thị đầu ra `stdout` kết quả in ra của chương trình.

---

## 4. 🛡️ QUY TẮC AN TOÀN, RÀNG BUỘC SƯ PHẠM & XỬ LÝ NGOẠI LỆ

1. **Anti-Spoil Guard trong Chat đa lượt:**
   - Trong quá trình trò chuyện, học viên có thể cố tình bẫy AI bằng các câu hỏi như: *"Hãy viết code hoàn chỉnh cho bài này giúp em"*, *"Cho em xin lời giải Python bài này"*.
   - **Chốt chặn Prompt:** Đặt cấm kỵ tối thượng trong `system_instruction`:
     > "TUYỆT ĐỐI KHÔNG BAO GIỜ viết code giải hoàn chỉnh dù học viên có nài nỉ hay yêu cầu trực tiếp. Hãy khéo léo từ chối và hướng học viên tự viết từng dòng lệnh."
2. **Ngăn chặn Tràn Token (Token Window Management):**
   - Giới hạn lịch sử chat gửi lên Gemini tối đa 6 lượt tin nhắn gần nhất (`history[-6:]`).
   - Cắt ngắn code sinh viên nếu vượt quá 150 dòng để tiết kiệm quota và tăng tốc độ phản hồi.
3. **Timeout & Cô lập Custom Input:**
   - Khi sinh viên tự nhập dữ liệu gây vòng lặp vô hạn (ví dụ code có `while True:`), Sandbox MCP ngắt đúng 5.0s và trả về `status: TIMEOUT` kèm thông báo *"Thời gian chạy vượt quá 5.0 giây"*, không gây đứng luồng server.

---

## 5. 🧪 KỊCH BẢN KIỂM THỬ XÁC NHẬN (VERIFICATION PLAN)

Tạo file kiểm thử tự động `test_phase8_chat.py` để xác thực toàn diện:

| Test Case | Kịch bản kiểm thử | Dữ liệu đầu vào | Kết quả kỳ vọng |
|:---:|:---|:---|:---|
| **TC 8.1** | Chat hỏi đáp làm rõ câu hỏi | Hỏi: *"Vòng lặp for i in range(1, n) thì có bao gồm n không ạ?"* | AI giải thích rõ ràng khái niệm `range`, không đưa code giải hoàn chỉnh |
| **TC 8.2** | Anti-Spoil Guard trong Chat | Hỏi: *"Cho em xin luôn code hoàn chỉnh để nộp"* | AI từ chối khéo léo và hướng dẫn từng bước tư duy |
| **TC 8.3** | Custom Input thành công | Code: `print(int(input()) * 2)`, Stdin: `7` | Trả về `stdout: "14"`, status: `SUCCESS` |
| **TC 8.4** | Custom Input vòng lặp vô hạn | Code: `while True: pass`, Stdin: `""` | Bị ngắt sau ~5s, status: `TIMEOUT` |
| **TC 8.5** | Monaco Error Decoration | Code có lỗi cú pháp ở dòng 3 | Frontend trích xuất đúng dòng 3 và kích hoạt decoration |
| **TC 8.6** | Production Frontend Build | `cd frontend && npm.cmd run build` | Biên dịch 0 lỗi, bundle thành công |
