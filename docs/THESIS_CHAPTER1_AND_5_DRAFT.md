# Bản nháp Chương 1 (Giới thiệu) và Chương 5 (Kết luận)

> **Trạng thái: BẢN NHÁP do trợ lý AI soạn ngày 13/11/2026 để sinh viên viết lại bằng giọng của mình.** Phần lập luận về bối cảnh ở Chương 1 cần số liệu và trích dẫn do sinh viên tự tìm; trợ lý **không đưa số liệu thống kê hay trích dẫn nào** ở đây để tránh bịa. Các chỗ **[SV bổ sung]** là bắt buộc.

---

# Chương 1. Giới thiệu đề tài

## 1.1. Lý do lựa chọn đề tài

Học lập trình là học một kỹ năng: người học chỉ tiến bộ khi tự viết, tự chạy và tự sửa chương trình của mình. Với người mới bắt đầu, khó khăn lớn nhất thường không nằm ở cú pháp mà ở chỗ không biết vì sao chương trình sai và nên thử gì tiếp theo. Trong lớp học đông, giảng viên không thể đứng cạnh từng người vào đúng lúc họ bế tắc. **[SV bổ sung: quy mô lớp thực hành ở Khoa, tỷ lệ giảng viên/sinh viên, hoặc quan sát của chính mình khi học môn lập trình.]**

Hai loại công cụ hiện có trả lời một phần nhu cầu này. Các hệ thống chấm bài tự động cho biết ngay chương trình đúng hay sai trên bộ kiểm thử, nhưng dừng ở đó. Các trợ lý dựa trên mô hình ngôn ngữ lớn thì giải thích được, nhưng thường đưa luôn lời giải hoàn chỉnh; người học có được chương trình chạy đúng mà không trải qua quá trình làm ra nó. **[SV bổ sung: 2–3 tài liệu về việc sinh viên dùng trợ lý AI khi học lập trình và các lo ngại đi kèm.]**

Khoảng trống giữa hai loại công cụ đó là đối tượng của khóa luận: một hệ thống thực hành mà phản hồi của AI **giúp người học tự sửa được**, và việc "không làm hộ" được bảo đảm bằng cơ chế kiểm tra được chứ không chỉ bằng lời dặn mô hình.

## 1.2. Sự cần thiết

- **Với người học:** cần phản hồi tức thời, đúng với lỗi đang gặp, ở mức trợ giúp do chính mình chọn, và không lấy mất cơ hội tự nghĩ.
- **Với giảng viên:** cần biết bài nào đang gây nghẽn và ai đang thử mãi mà không tiến, thay vì chỉ một bảng điểm.
- **Với việc ứng dụng AI trong giảng dạy:** cần những thiết kế cho thấy có thể dùng mô hình ngôn ngữ một cách có kiểm soát, đo được nó tuân thủ tới đâu, và nói rõ chỗ nó chưa tuân thủ.

## 1.3. Yêu cầu nghiệp vụ

**Người học**

1. Viết và chạy thử chương trình Python trên trình duyệt, xem kết quả từng kiểm thử.
2. Xin gợi ý theo ba mức tăng dần độ cụ thể; hệ thống không tự nâng mức.
3. Nộp bài chính thức và hiểu vì sao nhận số sao đó.
4. Hỏi gia sư về khái niệm; biết câu trả lời dựa trên tài liệu nào hoặc không có tài liệu.
5. Xem chương trình chạy từng bước.
6. Xem tiến độ của mình kèm mức độ tin cậy của nhận định.

**Giảng viên**

1. Quản lý lớp, bài tập, bộ kiểm thử.
2. Xem phân tích quá trình học của lớp, luôn kèm cỡ mẫu và giới hạn diễn giải.
3. Cung cấp tài liệu riêng của lớp cho gia sư AI.

## 1.4. Yêu cầu kỹ thuật

1. Ứng dụng web; không cần cài đặt phía người học.
2. Chạy mã của người học tách khỏi tiến trình máy chủ, có giới hạn thời gian.
3. Vẫn hoạt động khi không có dịch vụ mô hình ngôn ngữ.
4. Phân quyền kiểm tra ở máy chủ.
5. Các ràng buộc sư phạm có kiểm thử và phép đo chạy lại được.

## 1.5. Mục tiêu, phạm vi và phương pháp thực hiện

### 1.5.1. Mục tiêu

**Mục tiêu tổng quát:** xây dựng hệ thống hỗ trợ học lập trình Python với phản hồi thích ứng dựa trên mô hình người học, trong đó các nguyên tắc sư phạm được cài đặt thành cơ chế kiểm tra được.

**Mục tiêu cụ thể**

| # | Mục tiêu | Cách kiểm chứng trong khóa luận |
|---|---|---|
| M1 | Phản hồi ba mức theo khung "đang ở đâu → bằng chứng → bước kế tiếp" | Kiểm thử tự động; 22 ca với mô hình thật |
| M2 | Cơ chế hạn chế lộ lời giải ở cả ba mức và trong trò chuyện | Benchmark có tập giữ riêng; phép đo chạy khung mã đã che |
| M3 | Chọn chiến lược gợi ý theo bằng chứng mà không tự nâng mức | Kiểm thử; bộ phát lại 6 tình huống |
| M4 | Trả lời có nguồn, và nói rõ khi không có nguồn | Benchmark truy xuất |
| M5 | Hồ sơ người học và phân tích lớp gắn cỡ mẫu, trạng thái dữ liệu | Kiểm thử; rà soát giao diện |
| M6 | Bộ công cụ đánh giá chạy lại được | Các script trong repo |
| M7 | Quan sát mô tả về tính dùng được với người học và giảng viên thật | **Pilot — [SV bổ sung khi đã chạy]** |

### 1.5.2. Phạm vi

- **Trong phạm vi:** bài tập Python nhập môn (vào/ra chuẩn, rẽ nhánh, vòng lặp, chuỗi); hai vai trò người học và giảng viên; thử nghiệm trên một máy với dữ liệu giả lập; một đợt chạy thử quy mô nhỏ.
- **Ngoài phạm vi:** chứng minh hiệu quả học tập bằng nghiên cứu có đối chứng; tổ chức thi và chống gian lận; hỗ trợ ngôn ngữ lập trình khác; triển khai vận hành ở quy mô trường; nạp giáo trình chính thức.

### 1.5.3. Phương pháp thực hiện

1. **Nghiên cứu tài liệu** về dạy học lập trình, phản hồi hình thành, hệ thống gia sư thông minh và ứng dụng mô hình ngôn ngữ trong giáo dục.
2. **Thiết kế từ nguyên tắc sư phạm:** mỗi quyết định thiết kế gắn với một nguyên tắc (bảng ở Chương 3).
3. **Phát triển lặp theo lát cắt dọc:** dữ liệu → API và quyền → giao diện → kiểm thử.
4. **Đánh giá ba tầng:** kiểm thử tự động; benchmark tất định và đo với mô hình thật; chạy thử với người dùng. Mỗi tầng chỉ được dùng để trả lời câu hỏi của tầng đó.
5. **Báo cáo trung thực:** kết quả trên tập giữ riêng và các ca mô hình vi phạm được báo cáo cùng với kết quả tốt.

## 1.6. Đóng góp của đề tài

1. Một thiết kế phản hồi ba mức có khung thống nhất, cài đặt cho cả nhánh có mô hình ngôn ngữ và nhánh tất định.
2. Bộ cơ chế kiểm tra được cho ràng buộc "không làm hộ" (bộ lọc đầu ra, khóa phạm vi trò chuyện, che logic khung mã), kèm phép đo và các kết quả chưa tốt.
3. Mô hình người học và phân tích cho giảng viên luôn mang theo cỡ mẫu và trạng thái dữ liệu.
4. Bộ công cụ đánh giá chạy lại được, gồm 22 ca chuẩn hóa với mô hình thật và phân tích các kiểu lỗi sư phạm tìm thấy.

## 1.7. Cấu trúc khóa luận

Chương 2 trình bày cơ sở lý thuyết và các hệ thống liên quan. Chương 3 phân tích yêu cầu và thiết kế hệ thống. Chương 4 trình bày kết quả và đánh giá. Chương 5 kết luận, nêu hạn chế và hướng phát triển.

---

# Chương 5. Kết luận

## 5.1. Kết quả đạt được

Khóa luận đã xây dựng PyTutor, một hệ thống thực hành Python trên nền web với gia sư AI có ràng buộc sư phạm. Đối chiếu với các mục tiêu ở mục 1.5.1:

| Mục tiêu | Kết quả | Bằng chứng |
|---|---|---|
| M1 | Đạt về cài đặt | Kiểm thử tự động đạt toàn bộ; phần lớn phản hồi của mô hình thật theo đúng khung |
| M2 | Đạt một phần | Ở Mức 3, lời giải đầy đủ không lọt qua bước che trên cả hai tập đã đo. Ở Mức 1–2, bộ lọc còn lọt 4/14 tình huống trên tập giữ riêng |
| M3 | Đạt | 6/6 tình huống phát lại; mức gợi ý luôn được giữ nguyên |
| M4 | Đạt trên bộ câu hỏi tự soạn | Đúng mục trong 3 kết quả đầu 36/38; nói "không có nguồn" đúng 13/14 |
| M5 | Đạt về cài đặt | Kiểm thử; rà soát giao diện |
| M6 | Đạt | Các script kiểm thử, benchmark, đo tải, đo với mô hình thật |
| M7 | **[SV bổ sung]** | **Pilot** |

Ngoài các mục tiêu ban đầu, quá trình đánh giá mang lại hai nhận thức đáng ghi lại. Thứ nhất, chỉ dẫn trong prompt là chưa đủ: mô hình thật đã điền sẵn lời giải vào khung mã Mức 3, và chỉ một cơ chế tất định đặt sau mô hình mới chặn được. Thứ hai, "không lộ lời giải" chưa phải là "phản hồi tốt": có những phản hồi hoàn toàn an toàn nhưng không giúp gì cho người học, và chỉ đọc nguyên văn mới thấy.

## 5.2. Hạn chế

1. **Chưa có bằng chứng về hiệu quả học tập.** **[SV chỉnh theo kết quả pilot: nếu đã chạy, chỉ có quan sát mô tả ở quy mô nhỏ.]**
2. **Bộ lọc dựa trên biểu thức chính quy còn lọt** với các cách trình bày lời giải chưa lường trước, và gần như không chặn được câu chèn lệnh diễn đạt mới.
3. **Các chỉnh sửa prompt gần nhất chưa được đo lại với mô hình thật.**
4. **Độ trễ của mô hình thật cao** (trung vị khoảng 12 giây trong lần đo).
5. **Hiệu năng mới đo ở quy mô nhỏ trên một máy;** mỗi lời gọi công cụ mở một tiến trình mới.
6. **Chạy mã của người học chưa được cô lập về bảo mật** (tiến trình con chỉ có giới hạn thời gian, không giới hạn bộ nhớ, tệp, mạng). Mật khẩu của cơ sở dữ liệu mới đã được băm, nhưng cơ sở dữ liệu có từ trước vẫn có thể lưu dạng văn bản thường, và khóa ký JWT mặc định chỉ được cảnh báo chứ không bị chặn. Hệ thống ở mức bản mẫu nghiên cứu, chưa sẵn sàng triển khai.
7. **Các ngưỡng** của trạng thái dữ liệu, điểm tự lực và nhóm quá trình học là quy ước, chưa hiệu chuẩn.
8. **Kho tri thức** là tài liệu nội bộ, chưa phải giáo trình chính thức; hệ thống chưa kiểm tra được câu trả lời có thật sự dựa vào tài liệu đã truy xuất hay không.
9. **Phạm vi bài tập** giới hạn ở Python nhập môn với vào/ra chuẩn.

## 5.3. Hướng phát triển

1. **Nghiên cứu với người học thật:** mở rộng pilot, sau đó thiết kế so sánh có đối chứng giữa phản hồi ba mức và phản hồi không ràng buộc.
2. **Thay biểu thức chính quy bằng phân tích cú pháp** cho bộ lọc và bước che; cân nhắc dùng một mô hình thứ hai để thẩm định phản hồi trước khi gửi.
3. **Hiệu chuẩn các ngưỡng** bằng dữ liệu thật, đặc biệt là ranh giới giữa "đang tiến triển" và "mắc kẹt".
4. **Giảm thời gian chờ:** phản hồi dạng luồng; giữ kết nối công cụ dùng chung.
5. **Sẵn sàng triển khai:** cô lập việc chạy mã trong vùng chứa, chuyển mật khẩu cũ sang dạng băm, bắt buộc đặt khóa ký, quản lý khóa bí mật, thỏa thuận về dữ liệu với nhà cung cấp mô hình.
6. **Khung mã Mức 3 theo từng bài** ở nhánh không có mô hình, và nghiên cứu xem che tới mức nào thì khung vẫn hữu ích.
7. **Nạp giáo trình chính thức** khi được cấp quyền.

## 5.4. Lời kết

**[SV tự viết: điều mình học được, lời cảm ơn giảng viên hướng dẫn.]**
