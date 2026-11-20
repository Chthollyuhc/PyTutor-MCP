# Từ điển dữ liệu người học → chỉ báo → hành động (v5.7)

Mục đích: trả lời giảng viên "hệ thống thu thập gì, dùng để làm gì, giảng viên làm được gì". Mọi chỉ báo là **mô tả**, ngưỡng là quy ước vận hành **chưa hiệu chuẩn**; không phải thang năng lực hay bằng chứng hiệu quả học tập.

| Dữ liệu | Khi nào thu | Chỉ báo sinh ra | Ai dùng | Hành động có thể làm | Giới hạn |
|---|---|---|---|---|---|
| Lượt nộp (`submissions`): số test đạt, mức gợi ý | Bấm Nộp bài / Hỏi Gia sư | Sao, mô hình người học (6 KC), bài gây nghẽn | Sinh viên (sao), Gia sư AI (chiến lược), GV | Xem lại bài nghẽn; hỗ trợ SV vướng | Chỉ `submit` tính chính thức |
| Lượt chạy thử (`practice_runs`): số test đạt, loại lỗi, test sai, nhãn sai định dạng (từ v5.7) | Bấm Chạy thử (không lưu mã) | Nhóm quá trình (Mắc kẹt, Chỉ chạy thử...), loại lỗi theo bài | GV | Nhắn SV mắc kẹt; làm rõ đề nếu nhiều SV sai cùng test | Lượt trước v5.7 chưa có đặc trưng (hiện tỉ lệ phủ) |
| Đặc trưng lượt nộp (`attempt_features`): `error_class`, `failed_tests`, `format_mismatch_tests` | Cùng lượt nộp | Test hay sai nhất, tỉ lệ "chỉ sai định dạng" | GV | Sửa/làm rõ đề, thêm ví dụ đầu ra | Nhãn sai định dạng chỉ để chẩn đoán; bài vẫn chưa đạt, không đổi `error_class`, sao |
| Mốc thời gian đã có | Sẵn có | Khoảng thời gian tới lần đạt đầu (trung vị), xu hướng theo ngày | GV | Nhận ra bài quá dài/khó | Không phải thời gian ngồi làm |

## Nguyên tắc tối thiểu hóa
Chỉ lưu thứ dẫn tới một chỉ báo có hành động. **Không thu thập:** thao tác gõ phím (không dẫn tới hành động sư phạm, xâm phạm riêng tư), mã nguồn của lượt chạy thử, nội dung chat, bất kỳ dữ liệu chống gian lận (hệ thống dành cho người muốn học, không phải để kiểm tra).

## Vì sao ẩn ô "Hỏi AI về tình hình lớp" của GV (từ v5.7)
Số liệu bằng biểu đồ và tóm tắt tất định đáng tin hơn câu trả lời sinh bởi LLM, phù hợp giảng viên bận (nhìn là thấy, không phải chat), và không gửi số liệu lớp ra nhà cung cấp ngoài. Endpoint `/api/instructor/ai/class-chat` và test của nó vẫn giữ ở backend.

## Tóm tắt "Tình hình lớp"
`backend/class_overview.py` sinh ba danh sách tất định (cần chú ý / vấn đề chung / tiến triển tốt) với ngưỡng `OVERVIEW_THRESHOLDS`; mẫu nhỏ (`limited`/`no_data`) không sinh kết luận cấp lớp. Danh sách "cần chú ý" nêu lý do, không xếp hạng sinh viên.


## Hiển thị ở đâu (v5.8)
| Dữ liệu | Màn sinh viên ("Hành trình học") | Màn giảng viên ("Tình hình lớp") |
|---|---|---|
| Lượt chạy thử, hỏi Gia sư AI, nộp (theo bài) | Dấu chân từng bài (`AttemptStrip`), nạp lại code của chính SV | Ngăn dấu chân của một SV ở một bài, **không có mã nguồn** |
| Trạng thái 6 khái niệm (mô hình người học) | Bản đồ khái niệm + "Vì sao hệ thống nghĩ vậy" | Hàng "Theo khái niệm" (mỗi chấm một SV) |
| Nhóm quá trình theo cặp SV–bài | Không hiện nhãn nhóm tiêu cực; chỉ câu mô tả kèm bước tiếp | Ô ma trận SV × bài; thẻ "Việc nên xem" |
| Test sai, sai định dạng, loại lỗi | Không hiện (Anti-Spoil) | Ngăn bài; thẻ test sai và định dạng |
| Bài đạt lần đầu theo tuần | Dòng "tuần này / tuần trước" (số đếm) | Không dùng |
| Chỉ số gộp cũ (mức tự làm /100, đạt ngay lần đầu, số lần nộp TB, mức gợi ý TB) | **Bỏ khỏi giao diện** (backend giữ khóa) | "Dữ liệu chi tiết" giữ bảng bài nghẽn và bảng sinh viên |

Chi tiết lý do ở `docs/VISUAL_DESIGN_RATIONALE.md`.
