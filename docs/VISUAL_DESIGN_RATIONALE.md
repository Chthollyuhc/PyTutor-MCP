# Lý do thiết kế các màn trực quan v5.8 ("Hành trình học" và "Tình hình lớp")

Phục vụ Chương 3 (thiết kế) và phần phản biện. v5.8 **chỉ đọc và trình bày**: không thu thập dữ liệu mới, không đổi bảng, sao, mô hình người học, luật nhóm quá trình, chiến lược gợi ý hay chỉ số chính thức. API chỉ thêm (`/api/student/journey`, `/api/instructor/classes/{id}/students/{u}/exercises/{e}/journey`, khóa `matrix` và `action_cards` trong `/insights`).

## 1. Năm vấn đề của màn cũ
1. Sắp theo nguồn dữ liệu, không theo câu hỏi người xem (SV: ~10 khối ngang nhau; GV: ~16 khối).
2. Không có thứ bậc thị giác: người xem không biết khối nào hữu dụng.
3. Lặp khối: nhóm quá trình và cơ cấu lỗi mỗi thứ vẽ hai lần.
4. Một số chỉ số đi ngược sư phạm của chính hệ thống: "đạt ngay lần đầu" và "số lần nộp trung bình" ngược luật sao (nộp nhiều lần không trừ sao); "mức gợi ý trung bình" là trung bình của thang thứ bậc và còn hiện mặc định 1.0 kèm nhãn "độc lập tư duy cao" khi chưa có dữ liệu; "mức tự lực /100" là chỉ số gộp chưa hiệu chuẩn nhưng hiện như điểm chính xác.
5. Phần trăm trên mẫu nhỏ.

## 2. Phương pháp → ngành → áp vào PyTutor
Chỉ nêu tên phương pháp. **Danh sách nguồn: ghi "đọc trước khi trích"; chưa đối chiếu bản gốc nên chưa trích dẫn trong khóa luận.**

| Phương pháp | Ngành | Áp vào PyTutor |
|---|---|---|
| Mô hình người học mở (open learner model) | Hệ thống dạy học thông minh | Bản đồ khái niệm cho SV xem: mỗi khái niệm có nút "Vì sao hệ thống nghĩ vậy" |
| Tóm tắt có thể hành động, tiêu đề là kết luận | Trực quan hóa dữ liệu, bảng điều khiển | Thẻ "Việc nên xem": kết luận, bằng chứng k/n, một nút hành động |
| Biểu đồ chấm / icon array cho tỉ lệ nhỏ | Truyền thông rủi ro, thống kê mô tả | Bằng chứng k/n trên thẻ GV; chỉ thêm % khi n ≥ 10 |
| Ma trận nhiệt (small multiples) | Trực quan hóa dữ liệu | Ma trận SV × bài; ô bấm được |
| Chia sẻ đi trước, chi tiết theo yêu cầu (overview first, details on demand) | Thiết kế tương tác | Ba tầng GV; ngăn dấu chân; "Dữ liệu chi tiết" thu gọn |
| So với chính mình, không xếp hạng | Đánh giá quá trình, thiết kế khuyến khích học | SV chỉ thấy hành trình của mình; GV xếp A→Z; bảng xếp hạng ngoài phạm vi (xem §5) |
| Mã hóa dư (màu + hình + chữ) | Khả năng tiếp cận | Mỗi trạng thái có ký hiệu riêng và nhãn chữ; `aria-label` tóm tắt; bàn phím điều khiển được |

## 3. Khối cũ → giữ / chuyển / bỏ
| Khối cũ (màn SV) | Quyết định | Lý do |
|---|---|---|
| 4 ô số (mức tự lực, đạt ngay lần đầu, số lần nộp TB, mức gợi ý TB) | **Bỏ khỏi giao diện** (backend giữ khóa) | Ba ô ngược luật sao hoặc gộp thang thứ bậc; ô còn lại là chỉ số gộp chưa hiệu chuẩn hiện như điểm. Nội dung có ích chuyển vào bản đồ khái niệm và dấu chân |
| Thanh kết quả các lượt chấm | Bỏ | Phần trăm trên mẫu nhỏ; dấu chân thể hiện cùng thông tin theo thời gian |
| "Nhận xét chung" và 2 thẻ điểm mạnh/điểm nghẽn | Bỏ | Nhãn gắn lên người học, không dẫn tới hành động; thay bằng câu tóm tắt kèm nút |
| Danh sách khó khăn lặp lại | Chuyển | Thành khái niệm "đang vướng" cùng bài luyện tương ứng |
| Bước luyện tập tiếp theo | Giữ, nâng lên | Là câu tóm tắt đầu màn kèm nút "Làm bài này" |
| 6 thẻ khái niệm | Giữ, trực quan hóa | Bản đồ khái niệm 4 trạng thái |
| Lịch sử nộp bài | Chuyển | Điểm nộp trên dấu chân, nút "Nạp lại code này" |

| Khối cũ (màn GV) | Quyết định | Lý do |
|---|---|---|
| 4 ô số mẫu | Bỏ | Thay bằng một dòng ngữ cảnh |
| Tóm tắt 3 danh sách | Chuyển vào "Dữ liệu chi tiết"; nội dung nâng thành thẻ | Mỗi thẻ có kết luận, bằng chứng và một hành động |
| Nhóm quá trình vẽ lần 2, cơ cấu lỗi lần 2 | Bỏ phần lặp | Ma trận và ngăn bài đã thể hiện |
| Biểu đồ KC, loại lỗi, xu hướng ngày, bảng bài nghẽn, bảng SV, chú giải ngưỡng, giới hạn diễn giải | Chuyển vào "Dữ liệu chi tiết" (thu gọn) | Giữ nguyên để tra cứu, không chiếm màn chính |

## 4. Quy ước trình bày
- **Mẫu nhỏ:** luôn hiện `k/n`; chỉ thêm `%` khi `n ≥ 10` (quy ước trình bày, `frontend/src/utils/share.js`). Độ bất định vẽ bằng hình (ô trống nét đứt), không viết banner.
- **Mẫu số của thẻ:** thẻ mắc kẹt dùng SV đã thử bài; thẻ test sai dùng SV đã thử bài (k = SV bị sai test đó, vì số lượt sai gồm cả chạy thử nên không đặt trên mẫu số lượt nộp); thẻ định dạng dùng lượt chưa đạt (nộp + chạy thử); thẻ bài nghẽn dùng lượt nộp.
- **Bảng mã hóa:**

| Nhóm quá trình | Màu | Ký hiệu |
|---|---|---|
| Đạt độc lập | xanh lá đậm | ✓ |
| Đạt sau thử–sửa | xanh lá nhạt | ↻ |
| Đạt nhờ gợi ý | tím nhạt | G |
| Đang tiến triển | vàng | … |
| Mắc kẹt | đỏ, viền đậm | ! |
| Chỉ chạy thử | xám | ○ |
| Chưa bắt đầu | viền nét đứt | (trống) |

| Trạng thái khái niệm | Hình |
|---|---|
| Khá vững | tô đầy, dấu tích |
| Đang hình thành | nửa tô |
| Đang vướng | viền cam đậm, dấu chấm than |
| Chưa có bằng chứng | nét đứt |

- **Dấu chân:** chạy thử = chấm nhỏ; hỏi Gia sư AI = ô vuông kèm mức; nộp = vòng (đạt thì tô đầy); điểm đạt cao nhất mới = vòng ngoài; chỉ sai định dạng = gạch đứt dưới điểm; quá 20 điểm thì gộp các đoạn chạy thử liên tiếp.
- **Giọng nói với SV:** mô tả kèm bước tiếp theo; không dùng "mắc kẹt", "xếp hạng", "kém", "yếu"; không nêu đầu ra mong đợi hay lời giải; không tự đẩy mức gợi ý. Danh sách từ cấm nằm trong `backend/student_journey.py` và được test.

## 5. Giới hạn
- Nhóm quá trình, trạng thái khái niệm và mọi ngưỡng là quy ước vận hành chưa hiệu chuẩn; câu chữ tất định, không LLM.
- Lượt chạy thử chỉ được ghi từ v5.4 và đặc trưng chi tiết từ v5.7: dấu chân ghi chú ngay trên dải, không suy diễn lượt cũ.
- Giảng viên không nhận mã nguồn qua dấu chân (tối thiểu hóa; đã có màn giám sát bài nộp).
- Trạng thái khái niệm **theo thời gian** (cần lưu ảnh chụp mô hình, tức đổi schema), bảng xếp hạng (`LeaderboardModal`, mâu thuẫn nguyên tắc "so với chính mình"), tóm tắt bằng LLM, nút "Đã xử lý": **ngoài phạm vi v5.8**, ghi vào việc còn mở.
- Chưa kiểm chứng với người dùng thật: các câu hỏi so sánh theo nhiệm vụ nằm ở `docs/PILOT_KIT.md` mục I và chỉ cho quan sát mô tả. Ảnh màn cũ "trước" chưa chụp được vì mã màn cũ đã bị thay trước khi dựng seed; nếu cần so sánh trực quan, khôi phục màn cũ từ bản sao lưu để chụp.

---

## 6. v5.9 — Lời thường

### 6.1. Vì sao v5.8 vẫn học thuật (5 nguyên nhân)
1. **Chữ là từ của người nghiên cứu:** dùng các thuật ngữ như "khái niệm", "đang hình thành", "chưa có bằng chứng", "trung vị", "k/n", "quy ước vận hành chưa hiệu chuẩn".
2. **Biểu đồ phải học mới đọc được:** trục "số test đạt", ký hiệu M1 và ×8, ma trận 7 màu kèm chú giải phức tạp.
3. **Màn hình nói về "hệ thống nghĩ gì về bạn"**, trong khi người dùng chỉ hỏi "xong chưa, còn bao nhiêu, làm gì bây giờ".
4. **Lần nào mở ra cũng giống nhau**, không có tin mới, không có gì để vui hay khích lệ.
5. **Phải bấm nút mới thấy**, không hiện ngay ở trang chính.

### 6.2. Quy tắc chữ và hình v5.9

**Quy tắc chữ:**
- Viết như đang nói chuyện: câu ngắn, xưng "bạn" với sinh viên; màn giảng viên cũng gọi sinh viên là "bạn" ("2 bạn nên hỏi thăm").
- Không dùng ký hiệu: `≥`, `≤`, `%`, `#`, `n=`, `k/n`. Viết "4 trên 5 trường hợp", "8 trong 10 bạn".
- Nói việc cụ thể, không đánh giá chung.
- Nói điều tốt trước, rồi đúng **một** việc nên làm.
- Dùng "lần", không dùng "lượt". Dùng "trường hợp" (hoặc "trường hợp kiểm tra"), không dùng "test".
- Danh sách từ cấm nằm ở `BANNED_WORDS` trong `backend/plain_language.py`; frontend có test quét từ cấm tự động (`plainCopy.test.js`).

**Quy tắc hình:**
- Chặng đường (giống màn theo dõi đơn hàng), ngôi sao ★, thanh tiến độ có ghi chữ ngay bên cạnh.
- Nhóm tên theo 3 màu: đỏ = nên hỏi thăm, vàng = đang cố gắng, xanh = đang ổn. Xám = chưa bắt đầu.
- Một con số lớn kèm một câu.
- **Không** dùng ở màn chính: biểu đồ có trục, thanh chồng nhiều màu, ma trận màu, biểu đồ đường, hay bất kỳ hình nào cần bảng chú giải.
- Mỗi hình đi kèm một câu nói đúng điều hình muốn nói. Che hình đi, câu vẫn phải đủ ý.

### 6.3. Bảng Trước → Sau

| Chỗ | Trước (v5.8) | Sau (v5.9) |
|---|---|---|
| Trang chủ sinh viên | 4 ô số: Lớp học phần, Bài hoàn thành, Sao tự lực tích lũy, Chỉ số tự lập (mã còn hiện 85% mặc định khi chưa có dữ liệu) | Thẻ **"Hôm nay của bạn"** |
| Câu chính | "Khái niệm “Vòng lặp” đáng luyện thêm" | "Tuần này bạn làm đúng 2 bài mới, nhiều hơn tuần trước 1 bài." |
| Tin vui | không có | "Bạn không bỏ cuộc: bài Số nguyên tố đúng hết sau 7 lần thử." |
| Chặng đường | không có ở trang chủ | 5 trạm theo lộ trình lớp: bài xong có ★★★, "Bạn ở đây", bài khóa có ổ khóa; "Còn 2 bài nữa là xong học phần." |
| Kỹ năng | 6 ô "Khá vững / Đang hình thành / Đang vướng / Chưa có bằng chứng" + "Vì sao hệ thống nghĩ vậy" | Một dòng: "Bạn làm tốt: Vòng lặp · Đang luyện: Câu lệnh if · Nên luyện thêm: Đệ quy" |
| Dấu chân một bài | Biểu đồ có trục "số test đạt", ký hiệu M1, ×8, chú giải 4 mục | Các bước bằng lời: "Chạy thử: đúng 3 trên 5 · Đúng thêm", "Nộp bài: đúng hết" |
| Sau khi nộp đạt | "Hệ thống đã ghi nhận 3 sao tự lực vào hồ sơ năng lực và cập nhật lộ trình kỹ năng của bạn." | "**Đúng hết rồi!** Bạn làm đúng hết bài này và có 3 sao. Bạn tự làm, không cần gợi ý lớn." + một tin vui nếu có |
| Đầu màn giảng viên | "7 ngày qua · 8/10 SV có hoạt động · 3 việc nên xem" + nhãn "Mẫu nhỏ · chỉ mô tả" | **Bản tin lớp** 3–5 câu: "Tuần này có 8 trong 10 bạn vào làm bài, làm đúng thêm 23 bài. Phần lớn các bạn đang ổn. 2 bạn nên được hỏi thăm: An, Hà. Bài khó nhất lúc này: Số nguyên tố. Nhiều bạn sai ở trường hợp “n = 1” (ví dụ đầu vào: 1)." |
| Nhóm sinh viên | Ma trận 7 màu + chú giải | Ba cột tên: **Nên hỏi thăm / Đang cố gắng / Đang ổn**, mỗi tên có một câu lý do; dòng "Chưa bắt đầu (2): …" |
| Theo bài | Thanh chồng 6 loại lỗi, "trung vị (n=6)" | "6 trong 10 bạn đã làm xong, 3 bạn đang làm." + lỗi hay gặp nói bằng ví dụ + "Các bạn làm xong thường mất khoảng 20 phút." |
| Thẻ lớp ở danh sách lớp | "2 SV cần chú ý · 1 vấn đề chung" | "2 bạn nên hỏi thăm · bài khó: Số nguyên tố" |
| Giới hạn | "quy ước vận hành chưa hiệu chuẩn" lặp ở nhiều chỗ | Một mục thu gọn "Hệ thống nhận xét thế nào?" + một dòng nhỏ "Nhận xét tự động…, có thể chưa chính xác." |

### 6.4. Yếu tố game hóa có / không

| Yếu tố | Có / Không | Lý do |
|---|---|---|
| Chặng đường học phần có sao | Có | Trực quan hóa tiến độ cụ thể, mỗi bài là một trạm rõ ràng |
| Tin vui về tiến bộ của bản thân | Có | Khích lệ nỗ lực vượt khó (ví dụ: làm đúng sau nhiều lần thử) |
| Lời khen cụ thể theo kỹ năng | Có | Ghi nhận tích cực dựa trên sự kiện thực tế |
| "Còn N bài nữa là xong học phần" | Có | Mục tiêu ngắn hạn, dễ hình dung |
| Chuỗi ngày học (streak) | Không | Tránh áp lực duy trì chuỗi ảo không gắn với học tập thực chất |
| Điểm kinh nghiệm / cấp độ ảo (XP/Level) | Không | Dễ gây lạm phát điểm số và xao lãng mục tiêu hiểu bản chất |
| Huy hiệu sưu tầm | Không | Không phản ánh trực tiếp năng lực lập trình |
| So sánh hay xếp hạng với bạn khác | Không | Đi ngược nguyên tắc "so với chính mình", tránh gây nản lòng |
| Hiệu ứng và thông báo dồn dập | Không | Giảm tải nhận thức, giữ tập trung vào bài tập và code |

### 6.5. Nguyên tắc "Chỉ đổi cách nói, không đổi cách tính"
- Toàn bộ backend logic lõi giữ nguyên 100%: cách tính sao, `compute_student_model`, `derive_learner_model`, `classify_learning_process`, các hằng số phân nhóm, chiến lược gợi ý và RAG.
- Dữ liệu đầu vào cho ngôn ngữ tự nhiên được lấy từ các hàm đã có (`get_class_insights`, `get_student_journey_overview`, `get_exercise_journey`).
- Module `backend/plain_language.py` là hàm thuần, tất định, không gọi LLM, không truy vấn database trực tiếp.

### 6.6. Chỗ giữ trung thực khoa học
- **"Hệ thống nhận xét thế nào?"**: Phần thu gọn công khai minh bạch toàn bộ quy tắc phân nhóm quá trình và tiêu chí nhận xét đang vận hành.
- **"Xem số liệu đầy đủ"**: Toàn bộ ma trận SV × bài, thẻ việc nên xem v5.8, biểu đồ phân bố và bảng chi tiết đều được giữ nguyên vẹn trong thẻ thu gọn để phục vụ phân tích sư phạm chuyên sâu và đối sánh đánh giá khóa luận.
- **Ngôn ngữ rào đón**: Thêm chú thích rõ ràng "Nhận xét tự động từ các lần bạn chạy thử và nộp bài, có thể chưa chính xác." để tránh khẳng định tuyệt đối.
