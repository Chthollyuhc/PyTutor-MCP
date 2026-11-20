# Nhóm quá trình học (v5.4)

Giảng viên xem sáu nhóm quá trình thay cho "tỷ lệ lượt nộp đạt". Nhóm được tính **cho từng cặp sinh viên–bài** trong N ngày gần nhất, từ chuỗi sự kiện theo thời gian: lượt Chạy thử (`practice_runs`, không lưu mã nguồn), lượt Hỏi Gia sư AI (`submissions.action_type='ask_ai'`, có `hint_level`) và lượt Nộp bài (`submit`). Hàm: `classify_learning_process` trong `backend/database.py`.

| Nhóm | Điều kiện |
|---|---|
| Đạt độc lập | Đã nộp đạt; mức gợi ý cao nhất trước lần đạt đầu ≤ 1; ≤ 2 lượt nộp và < 5 lượt chạy thử |
| Đạt sau thử–sửa | Đã nộp đạt; gợi ý ≤ 1; > 2 lượt nộp hoặc ≥ 5 lượt chạy thử trước khi đạt |
| Đạt nhờ gợi ý | Đã nộp đạt; mức gợi ý cao nhất trước lần đạt đầu ≥ 2 |
| Đang tiến triển | Chưa đạt; số test đạt tốt nhất còn tăng trong 5 lượt (chạy thử + nộp) gần nhất, hoặc dưới 8 lượt |
| Mắc kẹt | Chưa đạt; ≥ 8 lượt (chạy thử + nộp) và số test đạt tốt nhất không tăng trong 5 lượt gần nhất |
| Chỉ chạy thử | Có chạy thử hoặc hỏi gợi ý nhưng chưa nộp lần nào |

Sinh viên "cần hỗ trợ" là sinh viên có ít nhất một bài thuộc nhóm Mắc kẹt.

## Giới hạn diễn giải
- **Ngưỡng (2 lượt nộp, 5 lượt chạy thử, 8 lượt, cửa sổ 5 lượt) là quy ước vận hành, chưa hiệu chuẩn và chưa kiểm chứng giáo dục.**
- Nhóm quá trình là bằng chứng mô tả cho giảng viên, không phải điểm hay metric chính thức của sinh viên. Sao và student model vẫn chỉ tính lượt `submit`.
- Lượt Chạy thử chỉ được ghi từ v5.4; dữ liệu trước đó không có nên nhóm của giai đoạn cũ có thể thiên thấp.
- Ý tưởng tham khảo là hiện tượng "wheel-spinning" (luyện mãi mà không tiến bộ) và "productive struggle" (vật lộn có ích). Trích dẫn học thuật cụ thể **cần xác minh** trước khi đưa vào khóa luận.

## Luật "cần chú ý" của tóm tắt lớp (v5.7)
Ngoài "Mắc kẹt", tóm tắt lớp nêu: đạt nhờ gợi ý Mức ≥ 2 ở ≥ 2 bài; chỉ chạy thử (chưa nộp) ở ≥ 2 bài. Ngưỡng nằm ở `OVERVIEW_THRESHOLDS` (`backend/class_overview.py`), là quy ước chưa hiệu chuẩn.
