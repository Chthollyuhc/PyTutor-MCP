# Hướng dẫn tải tài liệu cho Gia sư AI (v5.4)

Giảng viên tải tài liệu ở **trang chi tiết lớp → tab "Tài liệu cho Gia sư AI"**. Tài liệu gắn theo **lớp học phần**: chỉ sinh viên đã ghi danh lớp đó nhận được trích dẫn từ tài liệu này; lớp khác không thấy. Tài liệu chung của hệ thống (`docs/knowledge_base/`) áp dụng cho mọi lớp và xem ở mục Giám sát bài nộp & AI.

## 1. Tiêu chuẩn tài liệu (kiểm tra phía máy chủ)
| Hạng mục | Quy định |
|---|---|
| Định dạng | `.md`, `.txt`, `.pdf`, `.docx` |
| PDF | Phải có lớp chữ. Bản scan (không trích được chữ) bị từ chối; PDF đặt mật khẩu bị từ chối; tối đa 200 trang |
| Kích thước | ≤ 5 MB mỗi tệp |
| Văn bản sau khi trích | ≤ 150.000 ký tự |
| Số lượng | ≤ 20 tài liệu mỗi lớp |
| Lưu trữ | Chỉ lưu **văn bản đã trích** (`kb_documents`); không lưu tệp gốc |

### Khai báo bắt buộc (thiếu một mục là bị từ chối)
1. **Quyền sử dụng:** tự biên soạn / được tác giả hoặc đơn vị cấp phép / tài liệu mở có giấy phép (phải ghi rõ giấy phép, ví dụ CC BY 4.0).
2. **Nguồn gốc:** tác giả, năm, đường dẫn nếu có.
3. **Cam kết** tài liệu không chứa dữ liệu cá nhân sinh viên, đề thi hay đáp án bài tập của lớp.

### Cảnh báo (vẫn lưu)
- Tài liệu chứa nhiều khối code dài (> 40% ký tự nằm trong khối code). Gia sư AI bỏ khối code khi trích đoạn ở chế độ offline, và luật Anti-Spoil vẫn áp dụng cho câu trả lời.
- PDF/DOCX dài không có tiêu đề mục: tài liệu bị chia theo đoạn nên truy xuất kém chính xác hơn.

## 2. Tài liệu nên tải
- Giải thích **khái niệm** (biến, vòng lặp, hàm, kiểu dữ liệu...) bằng ví dụ ngắn.
- **Quy tắc viết mã** của lớp (đặt tên, định dạng, quy ước nộp bài).
- **Lỗi thường gặp** và cách đọc thông báo lỗi.
- Chia mục bằng tiêu đề (`#`/`##` trong Markdown; Heading trong Word) để mỗi mục là một đoạn truy xuất.

## 3. Không nên tải
- Lời giải hoặc đáp án của bài trong lộ trình lớp, đề thi, danh sách sinh viên, điểm số.
- Giáo trình có bản quyền khi chưa được cấp phép (luật dự án: giáo trình NEU chỉ nạp khi được cấp quyền). Dự án không bịa nguồn: nguồn hiển thị chính là tên tài liệu bạn đặt.

## 4. Cách hệ thống dùng tài liệu
- Mỗi lần thêm, xóa hoặc bật/tắt tài liệu, chỉ mục RAG được dựng lại toàn bộ (chỉ mục nhỏ nên rẻ).
- Truy xuất theo phạm vi: `retrieve_knowledge(query, class_id=None)` chỉ lấy tài liệu chung; có `class_id` thì lấy thêm tài liệu của đúng lớp đó. Mặc định `None` nên benchmark RAG không đổi (hit@3 36/38).
- Chat của sinh viên truyền `class_id` của lớp đang học; backend kiểm tra ghi danh trước khi truy xuất.
- Nguồn hiển thị: tên tài liệu + mục, kèm nhãn **"do giảng viên lớp cung cấp"**. Khi không có đoạn đủ liên quan, Gia sư AI trả lời **không kèm nguồn**.
- Tài liệu giảng viên tải lên chưa qua kiểm chứng của dự án; chất lượng và bản quyền là trách nhiệm của người tải.

## 5. API
`POST|GET /api/instructor/classes/{class_id}/knowledge`, `PATCH|DELETE /api/instructor/classes/{class_id}/knowledge/{doc_id}` — đều yêu cầu vai trò giảng viên sở hữu lớp (giảng viên khác nhận 404, sinh viên nhận 403).
