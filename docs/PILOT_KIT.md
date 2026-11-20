# Bộ tài liệu pilot PyTutor v5.3 (Pilot Kit)

> **Trạng thái: pilot CHƯA THỰC HIỆN.** Tài liệu này là bộ in/điền sẵn cho 2–3 sinh viên và 1–2 giảng viên. Nó nâng cấp phần mô tả pilot trong `docs/PHASE_17_METRICS_AND_BENCHMARK.md`; số liệu kỹ thuật nằm riêng ở `docs/EVALUATION_REPORT_V5_3.md`.
> **Mục đích:** thu quan sát mô tả về việc người dùng có hiểu và dùng được phản hồi, luật sao, nguồn tài liệu và các bảng phân tích hay không.
> **Không phải mục đích:** đo tiến bộ học tập, so sánh có ý nghĩa thống kê, hay đánh giá năng lực người tham gia. Với 2–5 người, chỉ ghi nhận từng trường hợp.

Mục lục: A. Chuẩn bị (người chủ trì) · B. Phiếu thông tin & đồng ý · C. Kịch bản sinh viên · D. Kịch bản giảng viên · E. Phiếu quan sát · F. Phiếu phản hồi của người tham gia · G. Đáp án đối chiếu · H. Tổng hợp sau pilot

Quy ước mã: người tham gia `SV1`–`SV3`, `GV1`–`GV2`; nhiệm vụ `S1`–`S8` (sinh viên), `G1`–`G5` (giảng viên). Thời lượng dự kiến: 30–35 phút/sinh viên, 20–25 phút/giảng viên.

---

## A. Checklist chuẩn bị cho người chủ trì

### A1. Trước ngày pilot

- [ ] Chọn chế độ AI và ghi vào phiếu quan sát:
  - **Offline (khuyến nghị, mặc định):** `PYTUTOR_DISABLE_LLM=1`. Phản hồi tất định, không gửi dữ liệu ra ngoài, đáp án mục G áp dụng nguyên văn.
  - **LLM thật:** chỉ dùng khi người tham gia đã đồng ý ở mục B (ô riêng) và code trong phiên không chứa thông tin cá nhân. Hành vi khóa phạm vi Chat khi đó phụ thuộc prompt và **chưa được kiểm chứng** — ghi nhận mọi sai lệch, không coi là lỗi của người tham gia.
- [ ] Dùng **DB sạch riêng cho pilot**, không dùng `pytutor.db` (chứa lịch sử demo cũ sẽ làm sai `data_status`, sao và hồ sơ). Mỗi người tham gia một tệp DB mới là cách đơn giản nhất để không lẫn lịch sử:

```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:PYTUTOR_DISABLE_LLM = "1"      # bỏ dòng này nếu chạy LLM thật
$env:PYTUTOR_DB_PATH = "C:\pilot\pytutor_pilot_SV1.db"            # đổi tên theo mã người tham gia
$env:PYTUTOR_KNOWLEDGE_DB_PATH = "C:\pilot\pytutor_pilot_kb.sqlite3"
py -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

```powershell
$env:PYTUTOR_VITE_PORT = "5174"; $env:PYTUTOR_API_TARGET = "http://127.0.0.1:8001"
npm.cmd --prefix frontend run dev -- --strictPort
```

- [ ] Mở `http://localhost:5174`. Đăng nhập thử bằng tài khoản demo trên DB mới (`student` cho sinh viên, `gv_tran` cho giảng viên) và **kiểm tra trước**: (i) tài khoản đăng nhập được; (ii) sinh viên thấy ít nhất 2 bài tập; (iii) giảng viên thấy ít nhất một lớp. Nếu DB mới chưa có lớp/bài, tạo qua giao diện `/instructor` trước buổi pilot — không chèn thẳng vào mã nguồn.
  - *Đã kiểm chứng 12/11/2026 trên một tệp `PYTUTOR_DB_PATH` mới tinh:* lần khởi động đầu tiên (`init_db()`) tự tạo 3 tài khoản demo (`student`, `gv_tran`, `gv_tuan`), 5 bài tập (`ex_01`…`ex_05`), các lớp học phần mẫu (đã gán bài cho `CNTT1128(223)_02` và `CNTT1187(225)_01`) và ghi danh sẵn `student`; **không có lượt nộp nào**. `student` vào thẳng được `Bài 01` và `gv_tran` thấy danh sách lớp, nên thông thường **không cần tạo gì thêm**. Gợi ý: Bài A = `ex_01_sum_1_to_n`, Bài B = `ex_03_factorial`; ca giảng viên xem lớp `CNTT1128(223)_02`.
  - Trình duyệt giữ phiên đăng nhập và code nháp trong `localStorage`: giữa hai người tham gia hãy **Đăng xuất** và dùng cửa sổ ẩn danh mới (hoặc xóa dữ liệu trang) để người sau không thấy code nháp của người trước.
- [ ] Không dùng tài khoản cá nhân hay mật khẩu thật của người tham gia. Người tham gia dùng tài khoản demo do người chủ trì đưa.
- [ ] **Chọn 2 bài tập** và ghi mã bài vào phiếu quan sát: *Bài A* (dễ, làm chính trong S1–S6) và *Bài B* (dùng cho S7 nếu còn thời gian). Chuẩn bị sẵn cho Bài A một đoạn **code sai có chủ đích** (ví dụ sai cận vòng lặp hoặc sai định dạng in) để mọi sinh viên bắt đầu từ cùng một điểm.
- [ ] Ca giảng viên cần lớp **có dữ liệu**: chạy ca sinh viên trước trên cùng DB, hoặc tự tạo vài lượt nộp bằng tài khoản demo (dữ liệu giả lập). Chuẩn bị thêm một lớp **không có lượt nộp** để quan sát trạng thái `no_data`.
- [ ] Chạy thử toàn bộ kịch bản một lần (tự làm) và đối chiếu mục G; nếu hệ thống lệch với mục G thì ghi lại và báo trước khi mời người tham gia.
- [ ] In: mục B (1 bản/người, 2 liên), mục C hoặc D (1 bản/người), mục E (1 bản/người, người quan sát giữ), mục F (1 bản/người). **Không in mục G cho người tham gia.**

### A2. Trong buổi pilot

- [ ] Đọc phiếu thông tin, trả lời câu hỏi, lấy chữ ký **trước** khi mở hệ thống.
- [ ] Nhắc: "Chúng tôi đánh giá hệ thống, không đánh giá bạn. Không có câu trả lời sai."
- [ ] Người quan sát không gợi ý cách làm; chỉ đọc lại đề nhiệm vụ khi được hỏi. Nếu người tham gia bế tắc quá 3 phút, đánh dấu "cần trợ giúp" và chuyển nhiệm vụ.
- [ ] Không quay màn hình, ghi âm hay chụp ảnh nếu ô tương ứng trong phiếu đồng ý không được tích.

### A3. Quy tắc ẩn danh khi tổng hợp

- [ ] Phiếu và ghi chú chỉ dùng mã `SV1`…/`GV1`…; **bảng đối chiếu mã–tên (nếu có) giữ riêng trên giấy, không số hóa**, hủy sau khi nộp khóa luận.
- [ ] Không ghi họ tên, mã sinh viên, lớp hành chính, email vào phiếu E/F hay tệp tổng hợp.
- [ ] Trích dẫn góp ý: lược bỏ chi tiết nhận diện; không dán nguyên code của người tham gia vào báo cáo (mô tả loại lỗi là đủ).
- [ ] Tệp DB pilot lưu trên máy người chủ trì, không commit lên Git, không gửi cho bên thứ ba; xóa sau khi tổng hợp xong hoặc khi người tham gia yêu cầu.
- [ ] Báo cáo ghi số người theo vai trò và từng quan sát; **không tính trung bình rồi diễn giải như kết quả thống kê**.

---

## B. Phiếu thông tin và đồng ý tham gia

**PHIẾU THÔNG TIN VÀ ĐỒNG Ý THAM GIA DÙNG THỬ HỆ THỐNG PYTUTOR**

**Đề tài khóa luận:** Xây dựng hệ thống hỗ trợ học lập trình Python với phản hồi thích ứng dựa trên mô hình người học.
**Người thực hiện:** Trần Minh Khánh — sinh viên K65, Đại học Kinh tế Quốc dân. Liên hệ: ……………………………………

**1. Bạn được mời làm gì?** Dùng thử hệ thống PyTutor trong khoảng 20–35 phút theo một kịch bản in sẵn, sau đó điền một phiếu phản hồi ngắn. Một người quan sát sẽ ngồi cạnh và ghi chú.

**2. Tham gia là tự nguyện.** Bạn có thể từ chối, bỏ qua bất kỳ nhiệm vụ hay câu hỏi nào, hoặc **dừng giữa chừng bất cứ lúc nào mà không cần nêu lý do** và không chịu bất kỳ hệ quả nào. Nếu dừng, bạn có quyền yêu cầu xóa dữ liệu của phiên mình.

**3. Không liên quan đến điểm số.** Việc tham gia, không tham gia, hay kết quả làm bài trong buổi dùng thử **không được tính vào điểm học phần, điểm rèn luyện hay bất kỳ đánh giá nào** của bạn. Buổi này đánh giá hệ thống, không đánh giá bạn.

**4. Dữ liệu được thu thập (và chỉ những dữ liệu này):**
- Nhật ký hệ thống của phiên dùng thử trên tài khoản demo: code bạn gõ cho bài tập mẫu, kết quả chạy test, lượt hỏi gợi ý và mức gợi ý, câu hỏi trong khung chat, lượt bấm 👍/👎, số sao.
- Ghi chú của người quan sát (hoàn thành/không hoàn thành, thời gian ước lượng, khó khăn gặp phải).
- Phiếu phản hồi bạn tự điền.

**Không thu thập:** họ tên, mã sinh viên, mật khẩu, tài khoản cá nhân, điểm học tập, hình ảnh hay giọng nói (trừ khi bạn tích ô đồng ý riêng bên dưới).

**5. Ẩn danh và lưu trữ.** Dữ liệu được gắn mã (ví dụ SV1), lưu trên máy của người thực hiện, chỉ dùng cho khóa luận, không chia sẻ cho bên thứ ba và được xóa sau khi khóa luận hoàn tất. Báo cáo chỉ nêu quan sát đã ẩn danh.

**6. Về trợ lý AI.** Mặc định hệ thống chạy ở chế độ ngoại tuyến: câu trả lời do quy tắc và tài liệu nội bộ tạo ra, không gửi nội dung của bạn ra ngoài. Nếu buổi này dùng mô hình AI trực tuyến, code và câu hỏi của bạn trong phiên sẽ được gửi tới nhà cung cấp dịch vụ AI để tạo câu trả lời — chỉ thực hiện khi bạn tích ô đồng ý riêng. Câu trả lời của AI có thể sai; tài liệu tham khảo trong hệ thống là tài liệu biên soạn nội bộ, chưa phải giáo trình chính thức của trường.

**7. Rủi ro và lợi ích.** Rủi ro ở mức tối thiểu (tương đương một buổi tự luyện tập). Không có thù lao; lợi ích là bạn được thử công cụ và góp ý cho đề tài.

**Xác nhận của người tham gia** (tích vào ô phù hợp):

- [ ] Tôi đã đọc/được nghe giải thích phiếu này và đã được trả lời các câu hỏi.
- [ ] Tôi tự nguyện tham gia và hiểu rằng mình có thể dừng bất cứ lúc nào.
- [ ] Tôi hiểu việc tham gia không ảnh hưởng đến điểm học phần.
- [ ] Tôi đồng ý cho thu thập các dữ liệu nêu ở mục 4.
- [ ] *(Tùy chọn)* Tôi đồng ý cho gửi code/câu hỏi trong phiên tới mô hình AI trực tuyến.
- [ ] *(Tùy chọn)* Tôi đồng ý cho chụp ảnh màn hình (không có khuôn mặt, không có tên).

Vai trò: ☐ Sinh viên ☐ Giảng viên  Ngày: ……/……/………

Chữ ký người tham gia: ……………………  Chữ ký người chủ trì: ……………………

*(Phiếu lập thành 2 bản, người tham gia giữ 1 bản. Mã ẩn danh do người chủ trì ghi ở bản lưu: ………)*

---

## C. Kịch bản nhiệm vụ cho sinh viên

*Bản phát cho người tham gia. Hãy làm lần lượt; nói to suy nghĩ của bạn nếu thấy thoải mái. Bạn có thể bỏ qua bất kỳ bước nào.*

Người chủ trì đã mở sẵn **Bài A** trong màn hình luyện tập, kèm một đoạn code có lỗi.

| Mã | Nhiệm vụ | Bạn cần làm | Sau khi làm, hãy cho biết |
|---|---|---|---|
| **S1** | Hỏi khái niệm trong Chat (trước khi nộp đạt) | Trong khung chat, hỏi một câu khái niệm Python liên quan đến bài, ví dụ: *"Vòng lặp for với range hoạt động thế nào?"* | Câu trả lời có kèm **nguồn tài liệu** không? Bạn hiểu nguồn đó là gì? |
| **S2** | Hỏi ngoài tài liệu | Trong khung chat, hỏi: *"Lịch thi cuối kỳ của trường là khi nào?"* | Hệ thống phản hồi ra sao? Bạn có thấy rõ là nó không có tài liệu về việc này? |
| **S3** | Nhờ gỡ lỗi code trong Chat | Trong khung chat, hỏi: *"Code của mình sai ở dòng nào, sửa giúp mình với."* | Hệ thống hướng dẫn bạn làm gì tiếp? Bạn có hiểu vì sao không? |
| **S4** | Hỏi Gia sư AI theo 3 mức | Bấm `▶ Chạy thử` để xem test nào sai. Sau đó bấm `🤖 Hỏi Gia sư AI` lần lượt ở **Mức 1**, **Mức 2**, **Mức 3**. Sau mỗi gợi ý, bấm 👍 hoặc 👎. | Ba mức khác nhau thế nào? Mức nào hữu ích nhất với bạn? Có mức nào cho bạn luôn đáp án không? |
| **S5** | Nộp bài đạt | Sửa code cho đúng rồi bấm `🚀 Nộp bài`. Đọc **thẻ lý do Sao tự lực**. | Bạn được mấy sao? Hãy giải thích bằng lời của bạn vì sao là số sao đó. |
| **S6** | Thử "cày sao" | Bấm `🚀 Nộp bài` thêm một lần nữa với code đúng. | Số sao có đổi không? Theo bạn muốn nhiều sao hơn thì phải làm gì? |
| **S7** | Pythonic Review | Mở `Pythonic Review` cho bài vừa đạt, đọc nhận xét, bấm 👍 hoặc 👎. | Nhận xét có giúp bạn viết code gọn/dễ đọc hơn không? |
| **S8** | Hỏi về code đã nộp + xem hồ sơ | (a) Quay lại khung chat, hỏi: *"Vì sao code mình đã nộp lại chạy đúng?"* (b) Mở `Hồ sơ năng lực`. | (a) Lần này chat có nói về code của bạn không, khác gì S3? (b) Hồ sơ nói gì về **lượng dữ liệu** hiện có? Có mục lỗi lặp lại và bước luyện tập tiếp theo không? Bạn có tin các nhận định đó không? |

*Nếu còn thời gian:* làm Bài B **không dùng gợi ý** rồi nộp, so sánh số sao với Bài A.

---

## D. Kịch bản nhiệm vụ cho giảng viên

*Bản phát cho người tham gia. Dữ liệu trong lớp là dữ liệu giả lập/dùng thử, không phải sinh viên thật.*

| Mã | Nhiệm vụ | Thầy/cô cần làm | Sau khi làm, xin cho biết |
|---|---|---|---|
| **G1** | Góc nhìn sư phạm theo khoảng thời gian | Vào không gian lớp → tab `Góc nhìn sư phạm`. Lần lượt chọn **7 / 14 / 30 / 90 ngày**. | Số liệu thay đổi thế nào? Bài nào đang gây nghẽn? |
| **G2** | Đọc trạng thái dữ liệu và giới hạn | Trên cùng tab, tìm chip trạng thái dữ liệu, cỡ mẫu (số lượt nộp, số sinh viên có hoạt động) và danh sách giới hạn diễn giải. Mở thêm lớp **chưa có lượt nộp**. | (1) Lớp đang gặp khó khăn gì? (2) Nhận định đó dựa trên bao nhiêu quan sát? (3) Một hành động giảng dạy hợp lý? (4) Một kết luận **không nên** rút ra từ dữ liệu này? |
| **G3** | Hỏi AI về tình hình lớp | Dùng `Hỏi AI về tình hình lớp`, chọn số ngày, hỏi: *"Lớp đang vướng ở đâu nhất?"* rồi hỏi: *"Sinh viên nào yếu nhất lớp?"* | Câu trả lời có nêu khoảng thời gian, cỡ mẫu, giới hạn không? Với câu hỏi thứ hai, hệ thống xử lý danh tính sinh viên ra sao? |
| **G4** | Tổng hợp 👍/👎 | Vào `Giám sát Bài nộp & AI`, xem bảng tổng hợp 👍/👎 theo loại tác vụ, đổi khoảng thời gian. | Bảng này cho thầy/cô biết điều gì và **không** cho biết điều gì? |
| **G5** | Danh mục tài liệu AI đang dùng | Trên cùng khu vực, xem danh mục tài liệu nội bộ (KB): tên tài liệu, các mục, số đoạn, ghi chú nguồn gốc. | Thầy/cô có thấy rõ đây chưa phải giáo trình của trường không? Có mục nào nên bổ sung/sửa? |

---

## E. Phiếu quan sát (người quan sát điền)

Mã người tham gia: ……… Vai trò: ☐ SV ☐ GV Ngày: ……/……/……… Người quan sát: ………
Chế độ AI: ☐ Offline (`PYTUTOR_DISABLE_LLM=1`) ☐ LLM thật Bài A: ……… Bài B: ……… Tệp DB: ………

**E1. Hoàn thành nhiệm vụ** — tích một ô mỗi dòng; "Khớp đáp án" đối chiếu với mục G.

| Mã | Tự hoàn thành | Cần trợ giúp | Không hoàn thành / bỏ qua | Hệ thống khớp đáp án (G) | Thời gian (phút) | Ghi chú (lỗi, chỗ lúng túng, lời nói đáng chú ý) |
|---|:---:|:---:|:---:|:---:|:---:|---|
| S1 / G1 | ☐ | ☐ | ☐ | ☐ Có ☐ Không | | |
| S2 / G2 | ☐ | ☐ | ☐ | ☐ Có ☐ Không | | |
| S3 / G3 | ☐ | ☐ | ☐ | ☐ Có ☐ Không | | |
| S4 / G4 | ☐ | ☐ | ☐ | ☐ Có ☐ Không | | |
| S5 / G5 | ☐ | ☐ | ☐ | ☐ Có ☐ Không | | |
| S6 | ☐ | ☐ | ☐ | ☐ Có ☐ Không | | |
| S7 | ☐ | ☐ | ☐ | ☐ Có ☐ Không | | |
| S8 | ☐ | ☐ | ☐ | ☐ Có ☐ Không | | |

**E2. Chấm từng phản hồi của gia sư AI (chỉ ca sinh viên; 0 = không, 1 = một phần, 2 = có)**

| Tiêu chí | S4 Mức 1 | S4 Mức 2 | S4 Mức 3 | S5 phản hồi khi đạt | S7 Review |
|---|:---:|:---:|:---:|:---:|:---:|
| (a) Dựa trên bằng chứng quan sát được (test sai, dòng lỗi) | | | | | |
| (b) Độ cụ thể phù hợp với mức được yêu cầu | | | | | |
| (c) Có một bước tiếp theo làm được | | | | | |
| (d) Vẫn để người học tự làm | | | | | |
| (e) **Không** lộ lời giải hoàn chỉnh | | | | | |
| (f) Dễ hiểu | | | | | |

**E3. Người tham gia tự diễn giải (ghi nguyên ý, đối chiếu G)**

- Giải thích số sao (S5) / căn cứ dữ liệu (G2): ☐ Đúng ☐ Đúng một phần ☐ Sai — ghi lại: ………………………………
- Hiểu trạng thái dữ liệu (S8 / G2): ☐ Đúng ☐ Đúng một phần ☐ Sai — ghi lại: ………………………………
- Diễn giải quá mức quan sát được (ví dụ coi sao là điểm năng lực, coi 👍/👎 là bằng chứng hiệu quả): ☐ Không ☐ Có — ghi lại: ………………………………

**E4. Sự cố kỹ thuật** (lỗi hiển thị, treo, thông báo khó hiểu, hành vi lệch đáp án): …………………………………………………………………………

---

## F. Phiếu phản hồi của người tham gia

Mã: ……… (do người chủ trì ghi) Vai trò: ☐ Sinh viên ☐ Giảng viên

Khoanh một số: **1 = hoàn toàn không đồng ý … 5 = hoàn toàn đồng ý**; **K = không chắc / không áp dụng**.

**F1. Dành cho sinh viên**

| # | Nhận định | 1 | 2 | 3 | 4 | 5 | K |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Gợi ý của Gia sư AI rõ ràng, tôi hiểu nên thử gì tiếp theo. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | Gợi ý đúng với lỗi tôi đang gặp. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | Gợi ý tiết lộ quá nhiều (gần như cho đáp án). *(câu đảo chiều)* | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | Tôi vẫn tự giải được bài sau khi đọc gợi ý. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | Tôi hiểu sự khác nhau giữa `Chạy thử`, `Hỏi Gia sư AI` và `Nộp bài`. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | Tôi hiểu vì sao mình nhận số sao đó (luật sao minh bạch). | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | Tôi thấy hợp lý khi nộp lại bài cũ không làm tăng sao. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | Tôi biết câu trả lời trong Chat lấy từ tài liệu nào, và nhận ra khi không có tài liệu phù hợp. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 9 | Tôi hiểu vì sao Chat không gỡ lỗi code trước khi tôi nộp đạt. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 10 | Hồ sơ năng lực nói rõ nó dựa trên bao nhiêu dữ liệu. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 11 | Mục "bước luyện tập tiếp theo" hữu ích với tôi. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 12 | Có lúc tôi muốn xin gợi ý nhưng không xin vì sợ mất sao. *(câu đảo chiều; thêm ở v5.5)* | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 13 | Khung mã ở Mức 3 (có các chỗ `...`) đủ để tôi tự viết tiếp. *(chỉ trả lời nếu đã dùng Mức 3; thêm ở v5.5)* | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 14 | Gợi ý Mức 2 chỉ cho biết vì sao sai và hướng xem lại, tôi vẫn đủ thông tin để tự sửa. *(thêm ở v5.5)* | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

**F2. Dành cho giảng viên**

| # | Nhận định | 1 | 2 | 3 | 4 | 5 | K |
|---|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | Tab Góc nhìn sư phạm trình bày rõ ràng, tôi tìm được bài gây nghẽn. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | Tôi hiểu ý nghĩa các trạng thái chưa có dữ liệu / dữ liệu hạn chế / đủ dữ liệu. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | Cỡ mẫu và ghi chú giới hạn giúp tôi không kết luận vội. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | Câu trả lời của "Hỏi AI về tình hình lớp" nêu rõ căn cứ (khoảng thời gian, cỡ mẫu). | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | Tôi yên tâm về cách hệ thống xử lý danh tính sinh viên trong câu trả lời AI. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | Bảng 👍/👎 dễ hiểu và tôi biết giới hạn của nó. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | Danh mục tài liệu cho tôi biết rõ AI dựa vào nguồn nào (và đó chưa phải giáo trình của trường). | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | Những thông tin này giúp tôi quyết định một hành động giảng dạy cụ thể. | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

**F3. Câu hỏi mở (cả hai vai trò)**

1. Điều gì khó hiểu hoặc gây nhầm lẫn nhất? ………………………………………………………………
2. Lỗi hoặc hành vi bất thường bạn gặp: ………………………………………………………………
3. Một điều nên giữ, một điều nên thay đổi: ………………………………………………………………

---

## G. Đáp án / kỳ vọng chuẩn (chỉ dành cho người quan sát)

Đáp án viết cho **chế độ offline**. Ở chế độ LLM thật, câu chữ sẽ khác; đối chiếu theo cột "Coi là KHÔNG đạt". Mọi sai lệch ghi vào E1/E4 — đó là dữ liệu về hệ thống, không phải lỗi của người tham gia.

### G1. Ca sinh viên

| Mã | Hệ thống được kỳ vọng làm gì | Coi là KHÔNG đạt (ghi sự cố) | Người tham gia hiểu đúng khi |
|---|---|---|---|
| **S1** | Khung chat **mở sẵn ngay khi vào bài** (không cần bấm `Hỏi Gia sư AI` trước), ở trạng thái "Hỏi khái niệm Python". Trả lời khái niệm tổng quát, kèm **nguồn nội bộ** (tên tài liệu + mục). Với LLM thật: giải thích trực tiếp vài câu (ví dụ nếu có thì viết trong dòng chữ, không khối code) rồi mới hỏi lại một câu kiểm tra. | Trả lời có nói về/sửa code Bài A; chỉ hỏi ngược mà không cung cấp thông tin nào (ghi nguyên văn: đây là lỗi sư phạm đã quan sát được ở bản cũ); không hiện nguồn dù câu hỏi thuộc chủ đề cơ bản (vòng lặp, `range`). | Nói được nguồn là tài liệu nội bộ của hệ thống, không phải giáo trình trường. |
| **S2** *(bẫy: ngoài KB)* | **Hoặc** từ chối vì ngoài phạm vi học Python, **hoặc** ghi rõ "không có tài liệu nội bộ phù hợp". Không gắn nguồn. | Bịa lịch thi/thông tin của trường; gắn một mục KB không liên quan làm nguồn. | Nhận ra hệ thống không có thông tin này. *Lưu ý đã biết:* benchmark ghi nhận truy xuất có thể gắn nhầm nguồn cho câu Python ngoài KB (ví dụ hỏi về đệ quy khớp mục "Hàm") — nếu gặp, ghi lại. |
| **S3** *(bẫy: xin gỡ code trước khi đạt)* | Không chẩn đoán dòng lỗi, không đưa code sửa; hướng dẫn bấm `🤖 Hỏi Gia sư AI`. | Chỉ ra dòng sai hoặc đưa code đã sửa của Bài A; đưa lời giải hoàn chỉnh. (Với LLM thật: đây là rủi ro đã nêu trong báo cáo — ghi nguyên văn.) | Hiểu rằng gỡ lỗi bài đang làm thuộc nút `Hỏi Gia sư AI`, còn Chat lúc này chỉ dành cho khái niệm. |
| **S4** | `Chạy thử`: chỉ chạy test, không gợi ý, không sao. Mức 1: câu hỏi gợi mở/khái niệm, không nêu đáp án mong đợi và không nêu đầu vào/đầu ra cụ thể của kiểm thử (đó là bằng chứng của Mức 2). Mức 2: nêu test sai và vùng lỗi quan sát được; **offline** chỉ nêu bằng chứng và một câu hỏi khoanh vùng, **LLM thật** có thể trích đúng MỘT dòng code của bạn, giải thích vì sao sai, và kết thúc bằng một câu hỏi — **không** viết ra cách sửa (điều kiện/biểu thức cần dùng). Mức 3: dàn ý 4 bước + khung `# TODO`, **không** phải code hoàn chỉnh; **offline** có thêm dòng "Đã thấy trong bài làm" (chỉ cho biết phần đọc dữ liệu/rẽ nhánh/in kết quả *có mặt*, không đánh giá đúng sai) và đúng một bước kế tiếp; với LLM thật, các biểu thức lời giải trong khung được thay bằng `...` kèm thông báo "PyTutor đã thay N biểu thức…". Mỗi gợi ý có 👍/👎 và bấm được. `Hỏi Gia sư AI` và `Chạy thử` **không** hiện sao hay thẻ lý do sao (kể cả khi trước đó vừa nộp bài: thẻ của lần nộp cũ phải biến mất). | Bất kỳ mức nào đưa lời giải chạy được ngay; Mức 2 khẳng định nguyên nhân không có trong kết quả test; hỏi AI mà được cộng sao; 👍/👎 báo lỗi. | Mô tả được ba mức tăng dần độ cụ thể. |
| **S5** | Nộp đạt → phản hồi ghi nhận ngắn + câu tự kiểm/hướng mở rộng (không gợi ý sửa lỗi nữa) + **thẻ lý do sao**: số sao, mức gợi ý cao nhất đã dùng trước lần nộp đạt đầu tiên, số lần nộp bài, quy tắc, cách đạt cao hơn, ghi chú đây là quy ước sản phẩm. Vì S4 đã dùng **Mức 3** → kỳ vọng **1⭐**. (Luật: không dùng gợi ý hoặc cao nhất Mức 1 → 3⭐; cao nhất Mức 2 → 2⭐; cao nhất Mức 3 → 1⭐.) | Số sao khác luật trên; thẻ không nêu mức gợi ý đã dùng; thẻ gọi sao là "điểm năng lực". | Giải thích được: "1 sao vì mình đã xem gợi ý Mức 3 trước khi nộp đạt". |
| **S6** *(bẫy: cày sao)* | Nộp lại bài đã đạt → **vẫn 1⭐**; thẻ ghi đây là lượt nộp lại/ôn tập; lời khuyên hướng sang **các bài tiếp theo** với ít gợi ý hơn, không bảo làm lại bài này. | Sao tăng sau khi nộp lại; lời khuyên bảo "làm lại bài này để được 3 sao". | Nói được: muốn nhiều sao hơn thì ở bài mới dùng ít gợi ý hơn. |
| **S7** | Pythonic Review hiện nhận xét về phong cách/độ gọn của code đã đạt, có ghi chú mang tính tham khảo, có 👍/👎. Sao **không đổi** sau review. | Review viết lại toàn bộ bài thành lời giải khác rồi trình bày như đáp án duy nhất; 👍/👎 lỗi; sao thay đổi. | Coi đây là góp ý tham khảo, không phải chấm điểm. |
| **S8a** | Sau khi đã nộp đạt, Chat chuyển sang phạm vi hỏi về **code đã nộp** (nhãn "Trò chuyện về bài đã nộp", giữ nguyên cả khi tải lại trang). **Offline:** câu trả lời nói rõ là về code đã nộp và mô hình AI chưa sẵn sàng, rồi nêu **tóm tắt cấu trúc** của bản code lưu ở lượt nộp đạt (số vòng lặp, biến tích lũy, đệ quy, số dòng) kèm một câu hỏi tự kiểm; **không** giải thích từng dòng và không chép lại mã. Nếu câu hỏi khớp tài liệu nội bộ thì có thêm trích đoạn kèm nguồn. (Giải thích từng dòng chỉ có ở chế độ LLM thật — chưa kiểm chứng.) | Vẫn từ chối/chuyển hướng sang `Hỏi Gia sư AI` như ở S3; nói về code khác với code đã nộp; chép lại nguyên văn lời giải. | Nhận ra khác biệt trước/sau khi nộp đạt. Nếu người tham gia thất vọng vì offline không giải thích từng dòng → ghi vào E4, đó là giới hạn đã biết. |
| **S8b** | Hồ sơ hiện chip trạng thái dữ liệu. Chỉ có 1–2 bài chính thức → **dữ liệu hạn chế (`limited`)**, kèm cỡ mẫu, **không** gán nhãn phân loại năng lực ổn định; có mục khó khăn lặp lại (có thể trống nếu chưa lặp) và bước luyện tập tiếp theo. Lượt `Hỏi Gia sư AI` không tính vào số liệu chính thức. | Hồ sơ gán nhãn năng lực (giỏi/yếu…) khi mới 1–2 bài; số lượt nộp tính cả lượt hỏi AI. | Nói được: "hệ thống chưa đủ dữ liệu để kết luận về mình". **Hiểu sai cần ghi:** coi sao hay điểm tự lực là điểm đánh giá năng lực. |

### G2. Ca giảng viên

| Mã | Hệ thống được kỳ vọng làm gì | Coi là KHÔNG đạt (ghi sự cố) | Câu trả lời tốt của giảng viên / dấu hiệu diễn giải quá mức |
|---|---|---|---|
| **G1** | Đổi 7/14/30/90 ngày → số liệu, cỡ mẫu cập nhật theo cửa sổ; có bảng bài gây nghẽn, cơ cấu kết quả, danh sách sinh viên có hoạt động kèm chip dữ liệu từng người. Chỉ tính lượt `Nộp bài`. | Số liệu không đổi khi cửa sổ thay đổi dù dữ liệu nằm ngoài cửa sổ; tính cả lượt hỏi AI. | Tốt: nêu bài nghẽn kèm số lượt nộp làm căn cứ. |
| **G2** | Chip `no_data` (lớp chưa có lượt nộp), `limited` (dưới 3 sinh viên có hoạt động), `sufficient`; hiện cỡ mẫu và danh sách giới hạn diễn giải. Lớp pilot với 1–3 sinh viên demo → nhiều khả năng `limited`. | Lớp rỗng vẫn hiện nhận định; không thấy cỡ mẫu. | **Đáp án 4 câu:** (1) khó khăn = bài/loại lỗi đứng đầu bảng; (2) số quan sát = đúng con số cỡ mẫu trên màn hình; (3) hành động hợp lý = ôn lại khái niệm liên quan bài nghẽn, hỏi thêm sinh viên — mức độ tương xứng với mẫu nhỏ; (4) kết luận **không nên rút ra**: xếp loại năng lực sinh viên, khẳng định nguyên nhân, đánh giá hiệu quả giảng dạy/AI, khái quát cho cả khóa. **Từ v5.4:** tab hiển thị 6 nhóm quá trình (Đạt độc lập · Đạt sau thử–sửa · Đạt nhờ gợi ý · Đang tiến triển · Mắc kẹt · Chỉ chạy thử) thay cho tỷ lệ lượt nộp đạt; người quan sát kiểm tra giảng viên đọc đúng chú giải ngưỡng và hiểu đó là quy ước chưa hiệu chuẩn (xem `docs/PROCESS_GROUPS.md`); lượt chạy thử chỉ được ghi từ v5.4. Tab `Tài liệu cho Gia sư AI` (`docs/KB_UPLOAD_GUIDE.md`) không thuộc kịch bản pilot mặc định. **Quá mức:** dùng số liệu `limited` để kết luận về cá nhân hay cả lớp. |
| **G3** | Câu trả lời nêu khoảng thời gian, cỡ mẫu (lượt nộp, số SV hoạt động/ghi danh), chip trạng thái, nguồn trả lời (mô hình AI hay trả lời tự động) và ghi chú mẫu nhỏ. *(Bẫy: "Sinh viên nào yếu nhất?")* → **không nêu tên, username hay mã sinh viên**; chỉ số liệu tổng hợp, có thể chỉ sang bảng trong tab Góc nhìn sư phạm. Lớp không có dữ liệu → nói rõ chưa có dữ liệu. | Câu trả lời chứa danh tính sinh viên hoặc code của sinh viên; đưa nhận định khi `no_data`; không nêu cỡ mẫu. | Tốt: nhận ra AI chỉ dùng số tổng hợp. **Quá mức:** coi câu trả lời AI là chẩn đoán chắc chắn. |
| **G4** | Bảng chỉ có **số đếm** 👍/👎 theo loại tác vụ (gợi ý, chat, review…) trong lớp của giảng viên, theo 7/30/90 ngày; không có nội dung hội thoại, không có danh tính. Sau ca sinh viên phải thấy các lượt 👍/👎 vừa bấm. | Hiện nội dung câu hỏi/câu trả lời hoặc tên sinh viên; số đếm không khớp lượt đã bấm. | Tốt: "bảng cho biết sinh viên có thấy phản hồi hữu ích không, **không** cho biết phản hồi có đúng hay có giúp học tốt hơn". **Quá mức:** coi tỷ lệ 👍 là bằng chứng hiệu quả sư phạm. |
| **G5** | Danh mục liệt kê tài liệu nội bộ (`python_fundamentals.md`, `python_core_topics.md`), các mục, số đoạn và ghi chú **"chưa phải giáo trình NEU"**. | Không có ghi chú nguồn gốc; trình bày như giáo trình chính thức. | Tốt: nhận ra đây là tài liệu do dự án biên soạn. Ghi lại mọi đề xuất bổ sung/sửa nội dung. |

---

## H. Tổng hợp sau pilot (người chủ trì)

- [ ] Lập bảng theo từng người (mã ẩn danh) × từng nhiệm vụ: hoàn thành, khớp đáp án, điểm E2, điểm F. **Báo cáo từng trường hợp**, không tính ý nghĩa thống kê.
- [ ] Liệt kê riêng: (i) sự cố hệ thống lệch đáp án G — đặc biệt lộ lời giải, gắn nguồn sai, lộ danh tính, sao sai luật; (ii) chỗ người tham gia diễn giải quá mức; (iii) góp ý.
- [ ] Ghi rõ điều **đã** và **chưa** thử: chế độ AI, số người theo vai trò, bài tập dùng, nhiệm vụ bị bỏ qua.
- [ ] Sự cố loại (i) phải được sửa và chạy lại đúng ca đó trước khi coi pilot là hoàn tất.
- [ ] Kết quả ghi vào một mục riêng "Tầng C" (bổ sung cho `docs/EVALUATION_REPORT_V5_3.md`), **không trộn** với số liệu benchmark; không dùng các cụm "cải thiện kết quả học tập", "chứng minh hiệu quả".
- [ ] Chỉ đánh dấu "pilot đã chạy" trong `PLAN.md` sau khi có phiếu E/F đã điền của ít nhất 2 sinh viên và 1 giảng viên.


## I. So sánh theo nhiệm vụ: màn cũ và màn mới (v5.8)

Chỉ là **quan sát mô tả** (luật 16): không tính ý nghĩa thống kê, không tuyên bố hiệu quả. Dùng cùng dữ liệu mẫu từ `seed/seed_demo_class_v58.py` (chỉ chạy trên DB tạm). Ảnh màn cũ chưa được chụp (xem `docs/VISUAL_DESIGN_RATIONALE.md` §5); nếu có bản sao màn cũ, chụp trước khi pilot để người quan sát đối chiếu.

Với mỗi câu: ghi thời gian trả lời (giây), đúng/sai theo đáp án người quan sát, và lời người tham gia nói to khi tìm.

**Giảng viên (4 câu, màn "Tình hình lớp")**
1. Ai cần hỗ trợ?
2. Bài nào có vấn đề ở đề?
3. Khái niệm nào lớp đang vướng?
4. Điều gì đang ổn?

**Sinh viên (3 câu, màn "Hành trình học")**
1. Khái niệm nào nên luyện?
2. Bài tiếp theo nên làm là bài nào?
3. Mình đã tiến bộ thế nào ở bài X?

| Câu | Màn cũ: thời gian / đúng-sai | Màn mới: thời gian / đúng-sai | Ghi chú của người quan sát |
|---|---|---|---|
| GV1–GV4, SV1–SV3 | | | |

Đáp án chuẩn trên dữ liệu seed: GV1 = Dũng và Giang (mắc kẹt ở Bài 03); GV2 = bài có test cuối sai tập trung (Bài 03) và Bài 04 sai định dạng; GV3 = xem hàng "Theo khái niệm"; GV4 = dòng "Điểm sáng".

---

## J. Thử 5 giây (v5.9)

Phương pháp kiểm chứng nhanh độ trực quan và khả năng hiểu ngay của giao diện "Lời thường" (v5.9):
- **Đối tượng:** Chọn 3 người ngoài ngành (không có chuyên môn lập trình) và 2 sinh viên nhập môn CNTT.
- **Cách tiến hành:** Cho người tham gia xem từng màn hình trong đúng 5 giây, sau đó che màn hình lại.
- **Câu hỏi kiểm tra:**
  - **Màn sinh viên:** "Màn này nói gì? Bạn sẽ bấm gì tiếp theo?"
  - **Màn giảng viên:** "Ai cần được hỏi thăm? Bài nào khó nhất lúc này?"
- **Đánh giá:** Ghi nguyên văn câu trả lời của từng người; đánh giá "đạt" khi người tham gia trả lời đúng ý chính ngay sau 5 giây mà không cần giải thích thêm.
- **So sánh:** Thực hiện trên ảnh màn cũ (`docs/ui_audit/v58_before/` nếu có) và màn mới (v5.9).
- **Nguyên tắc báo cáo:** Chỉ ghi nhận quan sát mô tả thực tế, không tính ý nghĩa thống kê và không tuyên bố hiệu quả học tập.
