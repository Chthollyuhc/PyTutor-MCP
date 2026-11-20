# Chủ đề Python nền tảng cho bài thực hành

Nguồn: Tài liệu tham khảo PyTutor (biên soạn nội bộ, không thay thế giáo trình chính thức của NEU).

## Biến và kiểu dữ liệu

Biến là tên gắn với một giá trị; Python xác định kiểu dữ liệu theo giá trị được gán. Các kiểu cơ bản gồm `int` (số nguyên), `float` (số thực), `str` (chuỗi) và `bool` (`True`/`False`). Hàm `type(x)` cho biết kiểu hiện tại của biến. Gán lại biến bằng giá trị khác kiểu là hợp lệ nhưng dễ gây nhầm lẫn, nên giữ một biến cho một ý nghĩa.

## Nhập dữ liệu và ép kiểu

`input()` luôn trả về chuỗi `str`, kể cả khi người dùng gõ số. Muốn tính toán phải ép kiểu: `int(input())` cho số nguyên, `float(input())` cho số thực. Nếu chuỗi không biểu diễn được số, phép ép kiểu sinh `ValueError`. Khi một dòng chứa nhiều giá trị cách nhau bởi dấu cách, dùng `input().split()` để tách thành danh sách chuỗi rồi ép kiểu từng phần tử.

## Xuất dữ liệu với print

`print()` in các đối số cách nhau bởi dấu cách và kết thúc bằng xuống dòng. Tham số `sep` đổi ký tự phân tách, `end` đổi ký tự kết thúc. Bài chấm tự động so khớp chính xác đầu ra, nên thừa dấu cách, thiếu xuống dòng hoặc in thêm lời nhắc trong `input("...")` đều có thể làm kiểm thử không đạt. f-string như `f"{diem:.2f}"` giúp định dạng số chữ số thập phân.

## Câu lệnh điều kiện if elif else

`if` kiểm tra một biểu thức logic; `elif` kiểm tra tiếp khi các nhánh trước sai; `else` xử lý phần còn lại. Chỉ nhánh đầu tiên đúng được thực hiện. Thứ tự điều kiện quan trọng: điều kiện hẹp hoặc trường hợp biên nên được đặt trước điều kiện rộng. Toán tử so sánh gồm `==`, `!=`, `<`, `<=`, `>`, `>=`; kết hợp bằng `and`, `or`, `not`. Nhầm `=` (gán) với `==` (so sánh) là lỗi cú pháp thường gặp.

## Phép chia nguyên và chia lấy dư

`/` luôn cho kết quả `float`. `//` là chia lấy phần nguyên và `%` là chia lấy dư. Một số chẵn khi `n % 2 == 0`. Chữ số cuối của số nguyên dương là `n % 10`, còn `n // 10` bỏ chữ số cuối; hai phép này thường đi cùng nhau trong vòng lặp `while` để xử lý từng chữ số.

## Biến tích lũy

Biến tích lũy giữ kết quả cộng dồn hoặc nhân dồn qua các vòng lặp. Giá trị khởi tạo phải là phần tử trung hòa của phép toán: `0` cho tổng, `1` cho tích, chuỗi rỗng `""` cho ghép chuỗi. Khởi tạo sai hoặc khởi tạo bên trong vòng lặp làm kết quả bị đặt lại ở mỗi lượt. Toán tử `+=` và `*=` là cách viết gọn cho phép cập nhật.

## Chuỗi và cắt chuỗi

Chuỗi là dãy ký tự bất biến, đánh chỉ số từ 0; chỉ số âm đếm từ cuối. Cắt chuỗi `s[start:stop:step]` lấy từ `start` đến trước `stop`; `s[::-1]` tạo chuỗi đảo ngược. `len(s)` trả về độ dài. Các phương thức thường dùng: `lower()`, `upper()`, `strip()`, `split()`, `replace()`, `count()`. Vì chuỗi bất biến, các phương thức trả về chuỗi mới chứ không sửa chuỗi gốc.

## Danh sách

Danh sách `list` lưu nhiều giá trị có thứ tự và thay đổi được. Truy cập phần tử bằng chỉ số từ 0; chỉ số vượt quá `len(lst) - 1` sinh `IndexError`. `append()` thêm vào cuối, `pop()` lấy ra, `sort()` sắp xếp tại chỗ còn `sorted(lst)` trả về danh sách mới. Các hàm dựng sẵn `sum()`, `max()`, `min()`, `len()` làm việc trực tiếp trên danh sách. Gán `b = a` không sao chép danh sách mà tạo thêm một tên trỏ tới cùng đối tượng.

## Từ điển

Từ điển `dict` ánh xạ khóa sang giá trị. Truy cập `d[key]` sinh `KeyError` nếu khóa chưa tồn tại; `d.get(key, mặc_định)` trả giá trị mặc định thay vì báo lỗi. Mẫu đếm tần suất thường dùng là `d[x] = d.get(x, 0) + 1`. Duyệt `for key, value in d.items()` lấy cả khóa và giá trị.

## Các loại lỗi thường gặp

`SyntaxError` xuất hiện khi mã sai cú pháp, ví dụ thiếu dấu hai chấm sau `if`/`for`/`def` hoặc thiếu ngoặc đóng; chương trình không chạy được dòng nào. `IndentationError` là thụt lề không nhất quán. `NameError` là dùng tên chưa được định nghĩa, thường do gõ sai tên biến. `TypeError` là phép toán giữa các kiểu không tương thích, như cộng `str` với `int`. `ValueError` là giá trị không hợp lệ cho phép chuyển đổi, như `int("abc")`. `IndexError` là chỉ số ngoài phạm vi. `ZeroDivisionError` là chia cho 0. Dòng cuối của traceback cho biết loại lỗi, dòng phía trên cho biết vị trí.

## Gỡ lỗi có hệ thống

Khi kết quả sai nhưng chương trình không báo lỗi, đó là lỗi logic. Cách tiếp cận: chọn một đầu vào nhỏ mà bạn tự tính được kết quả, dự đoán giá trị của từng biến sau mỗi dòng, rồi so với thực tế bằng `print()` tạm thời hoặc công cụ chạy từng bước. Điểm đầu tiên mà giá trị thực tế khác dự đoán là nơi cần xem lại. Luôn thử các trường hợp biên: giá trị nhỏ nhất, bằng 0, số âm, chuỗi rỗng, danh sách một phần tử.

## Hàm dựng sẵn hữu ích

`range(n)` sinh các số từ 0 đến n − 1. `enumerate(lst)` trả về cặp chỉ số và phần tử. `zip(a, b)` ghép cặp hai dãy. `abs()`, `round()`, `pow()` phục vụ tính toán số. `sorted()` nhận tham số `key` và `reverse`. Dùng hàm dựng sẵn thường ngắn gọn và ít lỗi hơn tự viết vòng lặp, nhưng người mới học nên hiểu vòng lặp tương đương trước khi dùng.
