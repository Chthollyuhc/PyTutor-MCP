# KẾ HOẠCH TRIỂN KHAI CHI TIẾT: PHASE 16.0
# NÂNG CẤP TOÀN DIỆN CHATBOT AI PYTUTOR-MCP
## (DYNAMIC PROMPTING, RAG, ROLE-BASED AI, GUARDRAILS & OBSERVABILITY)

> **Mã kế hoạch:** `PLAN_16.0`  
> **Trạng thái:** 🟡 **MVP ĐÃ TRIỂN KHAI; CÒN NGHIỆM THU NGUỒN HỌC LIỆU NEU & EVALUATION MỞ RỘNG**
> **Áp dụng cho:** `backend/`, `frontend/src/`, `scripts/`, `docs/knowledge_base/`  
> **Nền tảng hiện tại:** PyTutor-MCP v5.0 Pro — FastAPI MCP Host, MCP Server 8 tools, SQLite WAL, Gemini, React/Vite/Monaco, LMS NEU đa tầng.

---

## 1. 🔍 BỐI CẢNH KỸ THUẬT & MỤC TIÊU

PyTutor hiện đã có luồng chat đa lượt tại `POST /api/tutor/chat`, dựng prompt trong `backend/llm_service.py`, Student Model với các chỉ số học tập, kiểm tra chế độ EXAM và bộ lọc Anti-Spoil dựa trên Regex. Giao diện `TutorPanel.jsx` lưu lịch sử chat ở phía client. Backend đã có JWT và dependency phân quyền giảng viên, nhưng endpoint chat hiện chưa gắn xác thực role. MCP Trace ghi thời gian gọi công cụ; telemetry dành cho LLM và đánh giá phản hồi chưa có.

Phase 16 nâng cấp chatbot theo năm trụ cột:

1. Dùng template có cấu trúc và persona riêng theo tác vụ; cá nhân hóa theo dữ liệu Student Model.
2. Bổ sung truy xuất tài liệu cục bộ để cung cấp ngữ cảnh khái niệm có nguồn.
3. Phân quyền riêng chatbot sinh viên và chatbot hỏi đáp thống kê cho giảng viên.
4. Kiểm tra đầu vào/đầu ra để tăng khả năng chống injection, ngoài phạm vi và lộ lời giải.
5. Ghi telemetry LLM và thu phản hồi hữu ích/chưa hữu ích từ người học.

### 1.1. Mục tiêu nghiệm thu

- Giữ nguyên ba cấp độ gợi ý, chat đa lượt, sandbox/MCP, EXAM Guard, ba hành động IDE và luồng chấm sao hiện có.
- Student chat chỉ hoạt động cho người dùng đã xác thực trong chế độ được phép; Instructor chat chỉ cho role giảng viên và chỉ dùng thống kê lớp được phép truy cập.
- Câu trả lời khái niệm có thể dựa trên tài liệu truy xuất; không có tài liệu phù hợp thì nói rõ giới hạn, không bịa nguồn.
- Toàn bộ yêu cầu và phản hồi LLM qua guardrails; kết quả bị đánh dấu rủi ro không được gửi thẳng về giao diện.
- Có phép đo Anti-Spoil tự động với tập kiểm thử cố định và báo cáo tỷ lệ chặn rò rỉ.

---

## 2. 🏛️ KIẾN TRÚC AI SAU NÂNG CẤP

```text
[Sinh viên / Giảng viên đã đăng nhập]
                 │
        FastAPI + JWT Role Guard
          ┌──────┴─────────┐
          │                │
   Student tutor       Instructor class Q&A
   + EXAM check        + class authorization
          │                │
          └──────┬─────────┘
                 ▼
       Input Guard / Scope Check
                 │
      ┌──────────┴──────────────┐
      │                         │
  Student Model +          SQLite aggregate query
  exercise / MCP context   (backend-owned, read-only)
      │                         │
      └──────────┬──────────────┘
                 ▼
   Local RAG retrieval (concept questions)
                 │
   Prompt Template + selected persona
   (Socratic Tutor / Pythonic Reviewer /
    Instructor Analytics Assistant)
                 │
      Gemini provider abstraction
                 │
     Output Guard + Anti-Spoil check
          ┌──────┴─────────┐
       safe reply       safe refusal/fallback
          │
          ├── structured LLM telemetry → SQLite
          └── message id → TutorPanel 👍 / 👎 → SQLite
```

**Luồng dữ liệu:** MCP tiếp tục là nguồn Ground Truth cho chạy code, AST và Student Model. RAG bổ sung tài liệu khái niệm, không thay thế kết quả chạy sandbox/test. Chat thống kê giảng viên lấy số liệu bằng hàm truy vấn backend có phân quyền; LLM không được tự sinh hoặc thực thi SQL.

---

## 3. 📋 CHI TIẾT NHIỆM VỤ TRIỂN KHAI

### Task 16.1 — Prompt Templates & Persona Sư phạm

**Files dự kiến:** `backend/llm_service.py`, `backend/schemas.py`, `backend/prompts/`.

- [ ] Thêm Jinja2 và xây dựng template riêng cho Socratic Tutor, Pythonic Reviewer và Instructor Analytics Assistant.
- [ ] Chọn persona theo tác vụ hiện hữu: chat/gợi ý mức 1–2 dùng Socratic Tutor; Pythonic Review chỉ sau khi pass 100%; thống kê lớp dùng Instructor Analytics Assistant.
- [ ] Truyền `autonomy_score`, `first_try_pass_rate`, `average_hint_level` từ Student Model đã tính ở backend; hướng dẫn giọng văn hỗ trợ phù hợp, không dán nhãn hoặc làm nản học viên.
- [ ] Đóng gói code, câu hỏi, lịch sử, kết quả test và tài liệu RAG như dữ liệu không tin cậy; không cho nội dung này ghi đè system instruction.
- [ ] Giữ lịch sử chat có giới hạn và nội dung prompt không chứa bí mật cấu hình/API key.

### Task 16.2 — RAG Knowledge Base

**Files dự kiến:** `backend/rag/`, `scripts/ingest_knowledge_base.py`, `docs/knowledge_base/`, `requirements.txt`.

- [ ] Dùng ChromaDB persistent local làm vector store MVP; tạo adapter retrieval để có thể thay backend vector về sau.
- [ ] Chuẩn hóa tài liệu thành các đoạn có metadata: nguồn, tiêu đề, chủ đề, phiên bản và vị trí/trang nếu có.
- [ ] Nạp giáo trình Python NEU do người dùng cung cấp hoặc có quyền sử dụng, tài liệu PEP 8 phù hợp và ví dụ mã đúng đã rà soát.
- [ ] Tạo pipeline chia đoạn, embedding, nạp/cập nhật chỉ mục và lệnh kiểm tra tài liệu trùng hoặc thiếu metadata.
- [ ] Truy xuất top-k đoạn phù hợp cho câu hỏi khái niệm; giới hạn ngữ cảnh đưa vào prompt và kèm trích dẫn ngắn có nguồn.
- [ ] Khi vector store lỗi hoặc không có kết quả đủ liên quan, tiếp tục theo fallback không RAG có thông báo nội bộ/log; không tạo citation giả.
- [ ] Không đưa test case ẩn, đáp án mẫu riêng của bài hoặc dữ liệu sinh viên vào kho RAG dùng chung.

### Task 16.3 — Chat Riêng Theo Role & Thống Kê Lớp

**Files dự kiến:** `backend/main.py`, `backend/auth.py`, `backend/database.py`, `backend/schemas.py`, `frontend/src/services/api.js`, `frontend/src/pages/InstructorDashboard.jsx`.

- [ ] Bảo vệ `POST /api/tutor/chat` bằng JWT và giới hạn quyền sử dụng cho sinh viên; xác định danh tính từ token, không tin `session_id` do client tự khai.
- [ ] Giữ EXAM Guard chạy trước mọi truy xuất RAG hoặc gọi LLM; không gọi model khi ca thi khóa AI.
- [ ] Thêm endpoint riêng `POST /api/instructor/ai/class-chat`, dùng `require_instructor` và xác thực giảng viên được quyền xem lớp yêu cầu.
- [ ] Tạo một tập truy vấn thống kê backend cho câu hỏi lớp: số lượt nộp, tỷ lệ pass, nhóm lỗi/chủ đề, xu hướng theo khoảng thời gian; chỉ trả dữ liệu tổng hợp cần thiết.
- [ ] Giới hạn câu hỏi giảng viên vào thống kê học tập lớp; không cho LLM truy cập SQL trực tiếp hay đọc thông tin cá nhân không cần thiết.
- [ ] Thêm giao diện hỏi đáp lớp ở khu vực giảng viên, hiển thị lớp và khoảng thời gian của số liệu được phân tích.

### Task 16.4 — Input/Output Guardrails & Anti-Spoil

**Files dự kiến:** `backend/guardrails/`, `backend/llm_service.py`, `backend/main.py`.

- [ ] Tạo lớp kiểm tra đầu vào theo phạm vi hỗ trợ Python/khóa học, jailbreak/prompt injection, nội dung độc hại và giới hạn độ dài.
- [ ] Kiểm tra đầu ra bằng quy tắc xác định và bộ đánh giá ngữ nghĩa; phát hiện yêu cầu bị làm theo, mã lời giải hoàn chỉnh, lộ test/đáp án hoặc nội dung ngoài phạm vi.
- [ ] Tái sử dụng `sanitize_spoil_code()` như lớp tương thích trong giai đoạn chuyển tiếp; không xem Regex hiện tại là guard duy nhất.
- [ ] Nếu output không đạt, thử sửa/kiểm tra lại tối đa một lần; nếu vẫn rủi ro hoặc guard service lỗi, trả lời từ chối/fallback an toàn.
- [ ] Guardrails phải áp dụng cả chat đa lượt và các phản hồi gia sư khác; Pythonic Review vẫn chỉ chạy sau khi bài pass 100% và được đánh dấu rõ là review hậu nghiệm.
- [ ] Ghi lại loại quyết định guard và phiên bản luật, không lưu chain-of-thought hay bí mật nội bộ của model.

### Task 16.5 — LLM Telemetry & Feedback Loop

**Files dự kiến:** `backend/database.py`, `backend/llm_service.py`, `backend/schemas.py`, `backend/main.py`, `frontend/src/components/TutorPanel.jsx`.

- [ ] Tạo migration SQLite idempotent cho bảng log lần gọi LLM và bảng feedback; không xóa hoặc đổi dữ liệu hiện có.
- [ ] Lưu correlation ID, loại tác vụ, role, model/provider, latency, token prompt/completion nếu SDK trả về, trạng thái guard, trạng thái thành công/lỗi và thời gian.
- [ ] Không log API key; giới hạn nội dung nhận dạng cá nhân. Nội dung prompt/code đầy đủ chỉ lưu nếu có lý do sản phẩm rõ ràng và theo chính sách lưu trữ được phê duyệt.
- [ ] Trả `message_id`/`feedback_id` cùng phản hồi chat; thêm nút 👍 và 👎 trên từng bong bóng AI, tránh gửi lặp feedback cho cùng message.
- [ ] Thêm endpoint feedback yêu cầu đăng nhập; chỉ chủ sở hữu message hoặc role quản trị được đánh giá; lưu rating, thời gian và loại tác vụ.
- [ ] Cung cấp truy vấn/tổng hợp cho giảng viên đánh giá chất lượng theo lớp/thời gian mà không làm lộ nội dung riêng tư của người học.

---

## 4. 📦 THƯ VIỆN & PHỤ THUỘC DỰ KIẾN

| Gói | Mục đích | Ghi chú triển khai |
| :--- | :--- | :--- |
| `jinja2` | Render prompt template có cấu trúc | Thêm vào `requirements.txt`; template bật autoescape phù hợp với dạng text và tách dữ liệu khỏi chỉ dẫn |
| SQLite FTS5 + sparse TF-IDF | Chỉ mục RAG cục bộ và xếp hạng cosine vector thưa | Đã chọn để tránh phụ thuộc embedding model/runtime chưa xác nhận trên Python 3.14/Windows; adapter có thể thay bằng Chroma sau benchmark |
| `chromadb` / `sentence-transformers` | Vector store/embedding dense tùy chọn | Chưa cài; chỉ chuyển sang khi xác nhận tương thích, tài nguyên và quyền xử lý dữ liệu |
| `pytest` (nếu chưa có) | Unit/API/E2E tests | Ưu tiên thư viện test đã dùng trong repository |

Embedding provider mặc định cho MVP là sparse TF-IDF local. Knowledge base đi kèm hiện là tài liệu Python/PEP 8 biên soạn nội bộ; giáo trình NEU phải được người dùng cung cấp hoặc xác nhận quyền sử dụng trước khi nạp. Không âm thầm gửi tài liệu/câu hỏi tới dịch vụ ngoài. Không cài NeMo Guardrails hoặc Llama Guard trong MVP cho đến khi đánh giá được phụ thuộc runtime, mô hình và độ trễ; guard đầu tiên dùng module Python nội bộ.

---

## 5. 🛡️ QUY TẮC AN TOÀN, TƯƠNG THÍCH & XỬ LÝ NGOẠI LỆ

1. **Bảo toàn hệ thống:** Không thay đổi ý nghĩa ba hành động Chạy thử / Hỏi AI / Nộp bài, cơ chế sao tự lực, EXAM Guard, MCP True Discovery hoặc các MCP tools hiện có.
2. **Phân quyền server-side:** Không dựa vào role, tên lớp, session ID hay quyền do frontend gửi nếu không được đối chiếu với JWT và dữ liệu lớp.
3. **Dữ liệu riêng tư:** Student Model chỉ được dùng cho chính người học; dữ liệu lớp cho giảng viên phải thuộc lớp được phân quyền và chỉ tổng hợp theo nhu cầu câu hỏi.
4. **RAG có nguồn:** Chỉ dùng nguồn đã đăng ký; giữ metadata nguồn; không xem văn bản truy xuất là chỉ dẫn hệ thống; không khẳng định tài liệu NEU đã có trước khi được cung cấp.
5. **Fail-safe:** EXAM luôn khóa AI. Lỗi retrieval có thể fallback sang prompt không RAG; lỗi input/output guard không được trả nguyên văn phản hồi chưa kiểm tra.
6. **Telemetry tối thiểu:** Ghi số liệu vận hành cần thiết; token thiếu thì lưu `NULL`; không ước lượng rồi gắn nhãn như số đo thật.
7. **Migration:** Khởi tạo schema có thể chạy lặp an toàn, tương thích DB cũ và SQLite WAL; không xóa lịch sử submissions hoặc dữ liệu lớp.
8. **Môi trường:** Windows, Python 3.14; dùng `PYTHONIOENCODING=utf-8`; gọi frontend bằng `npm.cmd`.

---

## 6. 🧪 KỊCH BẢN KIỂM THỬ & TIÊU CHÍ XÁC NHẬN

Tạo bộ test mới `test_phase16_ai_upgrade.py` cùng fixture dữ liệu RAG không chứa thông tin cá nhân. E2E dùng LLM giả lập để chạy ổn định; thêm một smoke suite tích hợp Gemini có bật bằng cấu hình riêng.

| Test Case | Kịch bản | Kết quả kỳ vọng |
| :---: | :--- | :--- |
| **TC 16.1** | Render persona Socratic, Reviewer, Instructor | Đúng template theo tác vụ; có metrics được phép; dữ liệu người dùng không thể ghi đè system instruction |
| **TC 16.2** | Hỏi khái niệm có trong knowledge base | Context chứa đoạn truy xuất đúng cùng metadata nguồn; câu trả lời không bịa nguồn |
| **TC 16.3** | Hỏi ngoài knowledge base / vector store unavailable | Trả lời với fallback an toàn, không tạo trích dẫn giả và chat không crash |
| **TC 16.4** | Sinh viên gọi chat không token / token giảng viên | 401 / từ chối role theo hợp đồng API |
| **TC 16.5** | Sinh viên đang trong EXAM gọi chat | EXAM Guard từ chối trước retrieval và LLM; không phát sinh telemetry gọi model |
| **TC 16.6** | Giảng viên hỏi lớp được phân quyền / lớp ngoài quyền | Trả thống kê tổng hợp đúng / 403 hoặc 404 theo quy ước bảo mật |
| **TC 16.7** | Injection, jailbreak, off-topic, nội dung độc hại | Input Guard chặn hoặc chuyển hướng; model không được gọi khi bị chặn |
| **TC 16.8** | Model trả code giải đầy đủ hoặc rò đáp án ở nhiều dạng | Output Guard ngăn gửi câu trả lời; fallback an toàn được trả về và quyết định được telemetry ghi lại |
| **TC 16.9** | Anti-Spoil regression corpus | Tỷ lệ câu trả lời rò rỉ lời giải = **0%** trên corpus phát hành cố định; báo cáo riêng false-positive trên câu hỏi hợp lệ |
| **TC 16.10** | Token usage có/không có từ provider, timeout và lỗi model | Latency/model/trạng thái luôn được ghi; token lưu đúng hoặc `NULL`; API có fallback phù hợp |
| **TC 16.11** | Feedback thumbs up/down, gửi lặp, người dùng khác | Chủ sở hữu feedback được ghi đúng; duplicate bị từ chối/idempotent; không thể đánh giá message người khác |
| **TC 16.12** | Regression toàn hệ thống | MCP 8 tools, test Phase 8–15 và `npm.cmd run build` đều đạt; luồng hỏi AI không cấp sao, nộp bài vẫn chấm đúng |

### 6.1. Đo lường tỷ lệ Anti-Spoil E2E

- Xây corpus cố định gồm yêu cầu trực tiếp xin lời giải, prompt injection tiếng Việt/Anh, yêu cầu mã theo từng phần, biến thể Markdown/inline code, yêu cầu in test/đáp án, câu hỏi khái niệm hợp lệ và phản hồi model giả lập bị cài sẵn đáp án.
- Chấm bằng bộ kiểm tra xác định trước: phát hiện code hoàn chỉnh/trùng đáp án, xem xét quyết định của output guard và yêu cầu người rà soát kiểm tra các trường hợp mơ hồ.
- Báo cáo `leak_rate = số phản hồi rò lời giải / tổng tình huống tấn công`, `block_rate`, `false_positive_rate` trên câu hỏi học hợp lệ và độ trễ trung vị/p95 của guard.
- Điều kiện phát hành trên corpus phiên bản hóa: `leak_rate = 0%`; false-positive phải được báo cáo và không được che bởi chỉ số tổng hợp. LLM thật chỉ là smoke test, không thay thế bộ test deterministic.

### 6.2. Lệnh kiểm chứng dự kiến

```powershell
$env:PYTHONIOENCODING = "utf-8"
py test_phase16_ai_upgrade.py
py test_phase15_4_action_buttons.py
py test_phase15_3_qa_audit.py
py -m backend.test_backend_e2e
py -m mcp_server.test_mcp_server
cd frontend
npm.cmd run build
```

---

## 7. ✅ DEFINITION OF DONE

- [ ] Năm trụ cột được tích hợp và có tài liệu cấu hình/chạy thử; Phase 16 chỉ đánh dấu PASSED sau khi kiểm tra đạt.
- [ ] Student và instructor endpoints được xác thực role; EXAM và quyền truy cập lớp đã có regression tests.
- [ ] RAG ingest/retrieve chạy trên fixture; nguồn và metadata được trả đúng; fallback hoạt động khi kho rỗng/lỗi.
- [ ] Input/output guard và corpus Anti-Spoil đạt `0%` rò lời giải trên tập kiểm thử phát hành; false-positive được báo cáo.
- [ ] Telemetry và feedback được lưu đúng, migration chạy lặp an toàn, không chứa API key.
- [ ] Các test regression liên quan và frontend production build đạt; `PLAN.md` và `AI_HANDOFF_CONTEXT.md` được cập nhật sau triển khai.

