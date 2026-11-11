# Python cơ bản và quy tắc viết mã

Nguồn: Tài liệu tham khảo PyTutor (biên soạn nội bộ, không thay thế giáo trình chính thức của NEU).

## List comprehension

List comprehension tạo một danh sách mới từ một iterable bằng biểu thức, có thể kèm điều kiện lọc. Cú pháp tổng quát là `[biểu_thức for phần_tử in iterable if điều_kiện]`. Ví dụ: `[n * n for n in numbers if n > 0]` tạo bình phương của các số dương. Với logic nhiều nhánh hoặc nhiều vòng lặp, vòng lặp `for` thông thường thường dễ đọc hơn.

## Vòng lặp và điều kiện dừng

Vòng lặp `for` duyệt lần lượt các phần tử của iterable. `range(start, stop)` bao gồm `start` nhưng không bao gồm `stop`; vì vậy `range(1, n + 1)` duyệt các số từ 1 đến n. Vòng lặp `while` tiếp tục khi điều kiện còn đúng, nên thân vòng lặp cần cập nhật trạng thái để tránh lặp vô hạn.

## Hàm và giá trị trả về

Hàm được khai báo bằng `def`, có thể nhận tham số và trả kết quả bằng `return`. `print()` chỉ hiển thị dữ liệu; nó không thay thế cho `return` khi phần gọi cần nhận giá trị từ hàm. Tách chương trình thành hàm nhỏ giúp kiểm thử và tái sử dụng dễ hơn.

## Ví dụ đã rà soát

```python
def positive_squares(numbers):
    return [number * number for number in numbers if number > 0]
```

Ví dụ này trả về danh sách mới, giữ nguyên danh sách đầu vào và lọc số không dương trước khi tính bình phương.

## Quy tắc phong cách PEP 8 (tóm lược)

- Dùng tên biến/hàm chữ thường phân tách bằng dấu gạch dưới, ví dụ `total_score`.
- Thụt lề nhất quán bằng 4 dấu cách; không trộn tab và dấu cách.
- Đặt khoảng trắng quanh toán tử nhị phân và sau dấu phẩy.
- Tách nhóm logic bằng dòng trống; ưu tiên mã dễ đọc hơn biểu thức quá cô đọng.
- Dùng tên có ý nghĩa và tránh ghi đè tên built-in như `list`, `sum` hoặc `input`.
