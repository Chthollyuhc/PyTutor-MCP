# Nâng cấp gợi ý Mức 2 và Mức 3 (v5.12)

> Chưa commit. Đo bằng nhánh offline (LLM tắt); **chưa kiểm chứng với Gemini thật** cho thay đổi này.

## 1. Thay đổi

| | Trước | Sau |
|---|---|---|
| **Mức 3** | Dàn ý 4 bước chung, khung mã che logic, bảng chạy tay | Thêm **thuật toán chi tiết bằng lời**: ý tưởng + Bước 1–4 kèm ý con (1.1, 3.2...), mục *Trường hợp cần xử lý* (lấy từ nhóm kiểm thử của giảng viên), `# TODO (Bước 3.k)` trỏ đúng ý con |
| **Nguồn thuật toán** | không có | (1) ô **Ý tưởng thuật toán** do giảng viên viết (`exercises.algorithm_notes`, chỉ Mức 3 nhận, sinh viên không thấy); (2) khuôn theo dạng bài (tổng, tích, số nguyên tố, đảo chuỗi, đếm, lặp/rẽ nhánh/đệ quy chung). Khi dùng khuôn, phản hồi nói rõ đây là thuật toán tổng quát, chưa phải ghi chú của giảng viên |
| **Mức 2** | một dòng + một kiểm thử + giá trị cuối của biến | Thêm: **đối chứng** (test đạt đặt cạnh test chưa đạt), **dãy giá trị** các biến qua các lần chạy (từ vết chạy), **dạng lệch** quan sát được (lệch đúng 1 đơn vị, cùng ký tự khác thứ tự...), trường hợp **biến chỉ được gán một lần** nói như quan sát chứ không coi dòng khởi tạo là sai, xin lại Mức 2 thì **chuyển sang test lỗi kế tiếp** |
| **Bộ chặn** | chỉ che khối code Mức 3 | Thêm `enforce_level3_prose` (`GUARD_RULES_VERSION` 3): che biểu thức/câu lệnh Python nằm trong **phần chữ** của Mức 3 (giữ tên biến và giá trị kiểm thử) |

Ranh giới Mức 3 mới: **cho cấu trúc và thuật toán bằng lời, không cho mã Python của phần logic.** Khung mã vẫn che logic (`enforce_level3_skeleton`) và vẫn không được đạt hết kiểm thử.

## 2. Đo (offline, cùng kịch bản trước và sau)

Đạt mọi kiểm tra theo từng phản hồi (tag `v512_before` / `v512_after` trong `evaluation/`):

| Tập | Mức 1 | Mức 2 | Mức 3 | Số từ TB Mức 2 | Số từ TB Mức 3 |
|---|---|---|---|---|---|
| Phát triển, trước | 15/15 | 14/14 | 15/15 | 193 | 371 |
| Phát triển, sau | 15/15 | 14/14 | 15/15 | 233 | 564 |
| Giữ riêng, trước | 6/7 | 3/7 | 7/7 | 196 | 400 |
| Giữ riêng, sau | 6/7 | 3/7 | 7/7 | 235 | 619 |
| Red-team, trước | 9/9 | 7/9 | 8/9 | 174 | 367 |
| Red-team, sau | 9/9 | 7/9 | 9/9 | 196 | 569 |

- Các ca Mức 2 còn rớt ở tập giữ riêng và red-team **giống hệt trước khi sửa** (chọn dòng chưa đúng chỗ lỗi ở H01/H03/H04/H06, R03/R04); gói này không làm chúng tệ hơn và cũng không sửa chúng.
- Kiểm tra mới (đều đạt trên tập phát triển và tập giữ riêng): `m3_co_thuat_toan_chi_tiet`, `m3_khong_code_trong_loi`, `m3_todo_gan_buoc`, `m2_co_doi_chung`. Biên độ dài được nới (Mức 2: 60–300 từ; Mức 3: 140–760 từ) vì nội dung dài hơn có chủ ý.
- Mức 3 dài hơn khoảng 50% (≈560–620 từ): đây là đánh đổi có chủ ý theo yêu cầu "chi tiết hơn", nhưng chưa biết sinh viên có đọc hết hay không; cần pilot.

## 3. Giới hạn trung thực

- Khuôn thuật toán theo dạng bài là heuristic nhận diện qua tiêu đề/chủ đề; bài ngoài 5 bài mẫu thường rơi vào khuôn chung (lặp, rẽ nhánh, đệ quy). Nguồn đáng tin nhất là ô ghi chú của giảng viên.
- Mức 3 giờ nói cách giải bằng lời nên **gần lời giải hơn trước**. Sao tự lực vẫn chỉ 1⭐ cho Mức 3, và người học còn phải tự viết mã; chưa có bằng chứng về tác động học tập.
- Bộ chặn phần chữ là luật tất định (regex); chưa đo trên Gemini thật nên chưa biết tần suất Gemini viết biểu thức trong phần chữ.
- Tập giữ riêng chỉ để đo, không dùng chỉnh luật.

## 4. Dữ liệu và quyền

- Cột mới `exercises.algorithm_notes TEXT NOT NULL DEFAULT ''` (thêm khi `init_db()` chạy, không xóa gì). Bài đã có trong DB thật **không tự có ghi chú** (seed chỉ chạy khi bảng trống): giảng viên điền qua form, hoặc dùng khuôn theo dạng bài.
- `GET /api/exercises/{id}` chỉ trả trường này cho giảng viên; test `AlgorithmNotesApiTests` kiểm tra sinh viên không thấy, và phản hồi `/api/submit` không chứa trường này. Mức 1–2 và chat không nhận ghi chú.

## 5. Kiểm chứng với Gemini thật (38 lượt, dữ liệu giả lập; trần nâng 335 → 375, tổng 367/375)

Chạy `--real --levels 2,3` (tag `v512_real_dev`, `v512_real_holdout`). Chỉ Mức 2–3; Mức 1 không đổi nên không đo lại.

| Tập | Mức 2 | Mức 3 | Nguồn phản hồi |
|---|---|---|---|
| Phát triển (12 kịch bản, **trước** khi sửa theo kết quả này) | 9/12 | 7/12 | Gemini 20, offline 4 (nhà cung cấp không trả lời) |
| Giữ riêng (7 kịch bản, **sau** khi sửa) | 3/7 | 6/7 | Gemini 8, chặn đầu ra → offline 4, offline 2 |
| Mốc cũ v5.10/5.11 (cùng tập, tất cả do Gemini) | 14/14 dev, 4/7 giữ riêng | 11/15 dev, 5/7 giữ riêng | |

Phát hiện và xử lý (không cần gọi thêm):
- Khung mã do Gemini viết đôi khi **sai thụt lề** (không phải Python hợp lệ) và có dòng `TODO` do bộ che sinh ra chưa gắn số bước. Đã sửa: `_finish_level3` gắn số bước vào mọi TODO; khung không parse được thì rơi về khung offline hợp lệ (nhãn `level3_skeleton_invalid`).
- Gemini không phải lúc nào cũng nêu test đạt ở Mức 2 (đối chứng: 5/8). Đã đổi prompt thành bắt buộc khi có dòng "Đối chứng".

Giới hạn trung thực:
- Hai sửa trên **chưa được đo lại với Gemini** (còn 8 lượt). Ở tập giữ riêng, 4/7 phản hồi Mức 3 đã rơi về offline (chặn đầu ra), nên số 6/7 phản ánh khá nhiều nhánh luật chứ không riêng chất lượng Gemini.
- Mức 2 giữ riêng vẫn 3/7 như mốc offline; không tốt hơn mốc thật cũ (4/7), cỡ mẫu 7 quá nhỏ để kết luận khác biệt.
- Dev có 4/24 lượt nhà cung cấp không trả lời (không rõ lý do; không phải lỗi mã đã biết).

### Đo lại sau hai sửa (8 lượt cuối, tổng 375/375; tag `v512_real_recheck`; D07, D09, D11, D12 × Mức 2–3)
- Khung mã Mức 3: không còn ca khung sai Python hay TODO thiếu nhãn (D07, D09 rơi về khung offline hợp lệ, D12 đạt). Mức 3: 3/4 đạt mọi kiểm tra; ca rớt D11 do chép chú thích của người học, tên không có thật và cụm chỉ cách sửa.
- Mức 2: 1/4. Đối chứng vẫn thiếu ở D12 (Gemini bỏ qua dù prompt bắt buộc); D09 có cụm chỉ cách sửa; D11 chép chú thích của người học. Đây là giới hạn của Gemini với prompt hiện tại, chưa có thêm lượt để thử cách khác.
- Hết trần lượt Gemini; cỡ mẫu 4 chỉ cho thấy xu hướng, không đủ kết luận.
