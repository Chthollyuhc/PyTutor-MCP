# AI Handoff Context

File này dùng để chuyển ngữ cảnh làm việc từ Codex/ChatGPT sang Antigravity hoặc một AI coding assistant khác.

## Mục tiêu hiện tại

Người dùng đang chuẩn bị đồ án tốt nghiệp với hướng đề tài:

**Thiết kế và đánh giá hệ thống gia sư thông minh dựa trên Model Context Protocol (MCP) hỗ trợ học lập trình Python**

Tên tiếng Anh đề xuất:

**Design and Evaluation of an MCP-Based Intelligent Tutoring System for Python Programming Education**

## Ý tưởng sản phẩm

Xây dựng một hệ thống gia sư lập trình Python trực tuyến. Sinh viên vào website, chọn bài tập, viết mã Python, chạy thử, nộp bài, xem kết quả kiểm thử và nhận gợi ý thích ứng từ AI Tutor.

MCP không chỉ là thư viện phụ. MCP được định vị là lớp tích hợp trung tâm giữa hệ thống gia sư và các nguồn ngữ cảnh/công cụ:

- mã nguồn hiện tại của sinh viên
- đề bài và bộ test
- lịch sử nộp bài
- kết quả chạy/test
- lỗi cú pháp/lỗi logic
- lịch sử gợi ý
- mô hình học tập của sinh viên

Use case quan trọng nhất:

```text
Request Hint
  -> lấy code hiện tại
  -> lấy đề bài
  -> lấy test result
  -> lấy submission history
  -> lấy previous hints
  -> cập nhật/đọc student model
  -> pedagogical model chọn mức gợi ý
  -> LLM sinh adaptive hint
  -> lưu hint và learning event
```

## Chức năng chính đang làm

Chức năng chính được chọn để vẽ Balsamiq mockup và báo cáo là:

**Màn hình làm bài Python với AI Tutor gợi ý thích ứng**

Màn hình gồm 3 vùng chính:

- Cột trái: đề bài, yêu cầu, ví dụ, khái niệm, mục tiêu học tập
- Cột giữa: code editor Python, nút chạy thử, nút nộp bài, kết quả kiểm thử
- Cột phải: AI Tutor, mức gợi ý, nội dung gợi ý, nút yêu cầu gợi ý rõ hơn

Luồng tương tác:

```text
Đọc đề -> Viết mã -> Chạy/Nộp bài -> Xem kiểm thử -> Nhận gợi ý -> Sửa mã
```

## File đã tạo

Trong folder dự án:

- `Bao_cao_wireframe_PyTutor_Tran_Khanh.docx`: báo cáo Word đơn giản 2 trang, làm theo phong cách file mẫu của người dùng.
- `pytutor-main-wireframe.png`: ảnh wireframe chức năng chính.
- `build_template_report.py`: script tạo lại báo cáo Word nếu cần sửa nội dung.

Ngoài folder dự án, wireframe HTML nằm ở:

```text
C:\Users\Admin\.codex\visualizations\2026\08\13\019ffa8f-76f5-70e0-aba2-1ca3cdcd06e7\pytutor-main-function-wireframe.html
```

## Hướng công nghệ đề xuất cho dự án mới

Có thể xây hệ thống với độ phức tạp tương đương một dự án web hiện đại:

- Frontend: Next.js hoặc React
- Backend: NestJS hoặc Express/FastAPI
- Database: PostgreSQL
- Code execution: Python sandbox hoặc container
- AI Tutor: LLM orchestration
- MCP layer:
  - MCP server chạy code/test
  - MCP server phân tích mã
  - MCP server cung cấp learning context

Các tool MCP có thể có:

- `run_python`
- `run_tests`
- `analyze_syntax`
- `analyze_ast`
- `detect_error_patterns`
- `get_exercise`
- `get_attempt_history`
- `get_student_model`
- `get_previous_hints`
- `save_learning_event`

## Nguyên tắc sản phẩm

- Không mở rộng quá sớm sang nhiều ngôn ngữ lập trình.
- Tập trung vào Python.
- Không hứa MCP tự làm hệ thống thông minh hơn.
- Lập luận đúng: MCP giúp hệ thống dễ tích hợp, mở rộng, tái sử dụng công cụ và cung cấp ngữ cảnh theo chuẩn thống nhất.
- Điểm demo quan trọng nhất là trải nghiệm sinh viên xin gợi ý sau khi chạy/nộp bài.

## Prompt gợi ý để bắt đầu với Antigravity

Khi mở dự án trong Antigravity, có thể gửi prompt sau:

```text
Hãy đọc file AI_HANDOFF_CONTEXT.md trước. Đây là ngữ cảnh chuyển giao từ phiên làm việc trước.

Tôi đang làm đồ án tốt nghiệp về hệ thống gia sư thông minh dựa trên MCP hỗ trợ học lập trình Python. Trước mắt, hãy giúp tôi tiếp tục từ wireframe và báo cáo đã có trong dự án. Hãy giữ phạm vi tập trung vào chức năng chính: màn hình làm bài Python với AI Tutor gợi ý thích ứng.
```

