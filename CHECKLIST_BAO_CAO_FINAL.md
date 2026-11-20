# Checklist hoàn thiện `bao_cao_final.docx`

Nguồn: rà soát toàn bộ nội dung `bao_cao_final.docx` (487 đoạn, 33 bảng, 15 hình; 0 đánh dấu `[Bổ sung …]`/`[Lưu ý …]`/`[…]` còn sót, 0 vùng tô vàng).

**Cập nhật 19/11/2026 (bản hoàn thiện toàn diện & kiểm tra Turnitin 3%):** 
- **Kết quả kiểm tra Turnitin đạt 3% (Bảng E.1 & Phụ lục E):** Đã hoàn tất nộp kiểm tra trên cổng Turnitin chính thức của Trường Đại học Kinh tế Quốc dân (Lớp: *CHUYÊN ĐỀ 2026-2027 > CHUYÊN ĐỀ BÁO CÁO SỐ 1*, bài nộp: `bao_cao_final.docx`). Chỉ số tương đồng đạt **3%** (đạt chuẩn xuất sắc < 20%), 0% cờ AI, đã đưa đầy đủ bảng tổng hợp Bảng E.1 và nhận xét liêm chính học thuật vào Phụ lục E.
- **Thực nghiệm mở rộng RAG với Giáo trình đại học thực tế:** Đã thử nghiệm nạp và đánh giá *Giáo trình Python cơ bản (Phần 1)* của nhóm tác giả TS. Nguyễn Văn Hậu (Khoa CNTT - ĐHSPKT Hưng Yên) với dung lượng 135.305 ký tự (~32.000 từ). Hệ thống tự động phân đoạn thành 254 chunks, lập chỉ mục FTS5 + TF-IDF Vector. Kết quả truy xuất thực nghiệm ngữ nghĩa với 4 nhóm câu hỏi sinh viên đạt độ tương quan cao (0,332–0,588), xác minh 100% tính cô lập đa người thuê giữa các lớp học phần và tự động hiển thị `source_refs`. Đã cập nhật chi tiết vào Mục 4.4.2 và Mục 4.2.2.
- **Nâng cấp tính năng Đơn vị kiến thức động (Dynamic Knowledge Components):** Bổ sung bảng `knowledge_components` trong cơ sở dữ liệu, cho phép giảng viên tự định nghĩa/quản lý thêm các KC mới kèm từ khóa regex và gán nhãn bài tập bằng datalist gợi ý. Đã cập nhật đồng bộ vào `bao_cao_final.docx` tại Mục 3.7, Bảng 3.13, Mục 3.9, Mục 4.2.2, Mục 4.3 (nâng tổng số test case từ 153 lên **156/156 ca đạt**, `test_learner_model` đạt **34/34 ca**), Bảng 4.3 và Mục 4.9.2.
- **Chuẩn hóa Danh mục Tài liệu tham khảo IEEE:** Đã gỡ bỏ 2 trích dẫn khóa luận mẫu của sinh viên khóa trước, danh mục chuẩn hóa đúng 8 công trình học thuật quốc tế bình duyệt (`[1]`–`[8]`), 100% khớp nối trong toàn văn báo cáo.
- **Sửa lỗi giao diện Thẻ KPI:** Sửa lỗi tương phản giao diện thẻ "Sao tự làm tích lũy" ở Cổng sinh viên (`StudentPortalPage.jsx`), đồng bộ chuẩn `<Stat tone={3} .../>` DaisyUI/Tailwind cho cả 2 chế độ sáng và tối.

## A. Thông tin bìa và hành chính

- [x] Định dạng đồng nhất 13 tiêu đề chương/mục cấp `Heading 1` trong nội dung (cỡ chữ 18, in hoa, đậm, căn giữa, màu đen/Auto, Times New Roman; không đụng trang bìa).
- [x] Hoàn thiện nội dung `LỜI CẢM ƠN` trong `bao_cao_final.docx`.
- [x] Sửa `DANH MỤC BẢNG` nằm gọn trong 1 trang (không còn thừa 1 dòng sang trang bên).
- [x] Thống nhất ngày trên bìa (`Hà Nội, 11/2026` ở cả bìa ngoài và bìa trong).
- [x] Điền ngày trong Lời cam đoan (`Hà Nội, ngày 19 tháng 11 năm 2026` — chỉnh lại ngày nếu in nộp vào ngày khác).
- [ ] Ký tên bản in: ô `(Chữ ký GVHD)` để trống cho giảng viên ký; sinh viên ký ở Lời cam đoan.
- [x] Sửa khoảng trắng thừa trong `TS. Phạm  Thảo` (trang bìa).
- [x] Sửa lỗi chính tả `bác cáo` → `báo cáo` (Lời cam đoan).
- [x] Thống nhất cách viết `khóa luận` trong toàn văn (0 chỗ `khoá luận`).
- [x] Đổi tên đề tài thành “Xây dựng hệ thống hỗ trợ học lập trình Python với phản hồi thích ứng dựa trên mô hình người học” đồng bộ 6 chỗ trong `bao_cao_final.docx`.
- [ ] **Mở `bao_cao_final.docx` trong Word**, bấm `Ctrl+A` → `F9` (*Update Entire Table*) để cập nhật lại Mục lục (TOC), Danh mục Bảng và Danh mục Hình (sau khi thêm Mục 4.5.6, Bảng 4.3/B.1 và 13 hình mới), đồng thời kiểm tra lại trang bìa và ngắt trang.

## B. Nội dung báo cáo (các chỗ `[Bổ sung …]`)

- [x] **Mục 1.1**: bổ sung bối cảnh lớp thực hành lập trình nhập môn [19], [20] và tổng quan tài liệu về sinh viên dùng trợ lý AI cùng các lo ngại [21], [22], [14], [15] theo chuẩn IEEE.
- [x] **Mục 2.1**: bổ sung tổng quan tài liệu về khó khăn của người mới học lập trình (Robins và cộng sự [19]; Qian và Lehman [20]), gỡ ghi chú nội bộ.
- [x] **Mục 2.3**: bổ sung tổng quan ngắn về ITS theo mức bước giải (VanLehn [23]) và đạo đức phân tích học tập (Slade và Prinsloo [24]).
- [x] **Mục 2.6**: mở rộng đối chiếu chi tiết CodeHelp [14], CodeAid [15], NEU OJ [17], Moodle [18] với PyTutor.
- [x] **Mục 3.9, 3.10 & 3.11**: bổ sung bảng `attempt_features` vào Bảng 3.13 và mô tả Mục 3.9; bổ sung điểm cuối phân quyền `GET /api/instructor/classes/{class_id}/students/{username}/learner-model` ở Mục 3.10; hoàn thiện mô tả bố cục từng màn hình chính và nguyên tắc thiết kế giao diện đối chiếu `DESIGN.md` và Hình 4.1–4.8 ở Mục 3.11.
- [x] **Mục 4.5.1**: bổ sung kết quả tự chấm điểm sư phạm thang 0–5 của tác giả trên 22 phản hồi ngày 12/11/2026 (trung bình 4,23/5; nêu rõ giới hạn chưa có người chấm độc lập thứ hai).
- [x] **Mục 4.7**: thay ghi chú nội bộ Bảng 4.12 bằng câu dẫn chiếu nguồn `[14]`, `[15]`, `[17]`, `[18]`.
- [x] **Mục 4.8, Bảng 1.1 (M7) & Bảng 4.13 (M7)**: bổ sung báo cáo trung thực kết quả chạy thử kỹ thuật nội bộ 13 nhiệm vụ (`S1`–`S8`, `G1`–`G5`, phát hiện và sửa lỗi `S8a`) và ghi rõ chưa thực hiện đánh giá với người dùng thật bên ngoài (không còn `[Bổ sung sau khi chạy thử]`).
- [x] **Kết luận**: hoàn thiện đoạn lời kết của sinh viên.
- [x] **Phụ lục C**: bổ sung ví dụ nguyên văn ca `H4` (Mức 3) sau bước che logic `enforce_level3_skeleton` từ lần đo 18/11/2026.
- [x] **Phụ lục D**: bổ sung đầy đủ thang điểm sư phạm 0–5 (mục D.1) và tóm lược bộ tài liệu chạy thử `PILOT_KIT` (mục D.2).
- [x] **Phụ lục E**: Hoàn tất cập nhật báo cáo kết quả kiểm tra Turnitin chính thức đạt **3% Similarity Index**, bổ sung Bảng E.1 chi tiết (mã bài nộp 1854213177, ngày 19/11/2026), nhận xét liêm chính học thuật và chỉ dẫn đính kèm Digital Receipt.

## C. Hình ảnh đã chèn

- [x] Hình 3.1–3.4: đã vẽ (SVG→PNG) và chèn vào `bao_cao_final.docx`.
- [x] Hình 3.5: đã vẽ lại sắc nét bổ sung bảng **`attempt_features (v5.6)`**, sửa hết chồng nhãn `N`, và thay ảnh nhúng trong `bao_cao_final.docx`.
- [x] Hình 4.1–4.8: đã chụp và chèn đủ 8 ảnh giao diện thực tế vào `bao_cao_final.docx`.
- [x] Dữ liệu mock `pytutor.db`: đã dọn sạch dữ liệu rác, nạp 8 SV K65 CNTT (đủ 6 nhóm quá trình học ở `CNTT1128(223)_02`, lớp `limited`, lớp `no_data`), và **backfill 70/70 bản ghi `attempt_features`** (phủ 100% cho mô hình người học v3).
- [ ] *(Tùy chọn)* Chụp lại **Hình 4.7** để hiển thị thêm khối giao diện mới *"Hệ thống đang hiểu về bạn như thế nào"* ở nửa dưới modal Hồ sơ học tập nếu muốn minh họa trực tiếp mô hình người học v3 bằng ảnh.

## D. Chạy thử với người dùng (mục 1.3.2 M7, 4.8, 4.9.1, Kết luận)

- [x] Chạy thử kỹ thuật nội bộ (`dry-run`, theo `docs/PILOT_KIT.md` mục A1) toàn bộ 13 nhiệm vụ Giảng viên (`G1`–`G5`) và Sinh viên (`S1`–`S8`) trên hệ thống thật với LLM: phát hiện và sửa lỗi chặn nhầm chế độ `code_review` ở `S8a` (`backend/llm_service.py`), đã cập nhật trung thực vào Mục 4.8, Bảng 1.1 và Bảng 4.13.
- [ ] *(Chỉ khi kịp tổ chức trước ngày nộp)* Mời 2–3 người dùng thật (SV/GV), thu phiếu đồng ý ký tay và bổ sung quan sát thực tế vào Mục 4.8; nếu không kịp, bản báo cáo hiện tại đã ghi rõ giới hạn "chưa thực hiện với người dùng thật" và không còn placeholder.

## E. Tài liệu tham khảo (đã đối chiếu và chuẩn hóa IEEE)

- [x] Lọc sạch danh mục: Gỡ bỏ 2 trích dẫn khóa luận tốt nghiệp của sinh viên khóa trước ([9] và [10]), chuyển các phân tích về hệ thống chấm Online Judge và LMS thành phân tích khái quát trong Mục 2.6 và Mục 4.7.
- [x] Danh mục tài liệu tham khảo chính thức chuẩn hóa 8 công trình học thuật quốc tế bình duyệt (peer-reviewed) và sách chuyên khảo kinh điển (`[1]`–`[8]`): CodeHelp (ACM Koli Calling 2023), Vygotsky (1978), Wood, Bruner & Ross (1976), Koedinger & Aleven (2007), Hattie & Timperley (2007), Shute (2008), Online Python Tutor (ACM SIGCSE 2013), RAG (NeurIPS 2020).
- [x] Kiểm tra khớp 1–1: 8/8 tài liệu `[1]`–`[8]` đều được trích dẫn chuẩn xác trong nội dung, không có trích dẫn mồ côi hay tài liệu thừa, gỡ toàn bộ đánh dấu `[bổ sung …]` và tô vàng.

## F. Kiểm tra số liệu và tính nhất quán

- [x] Chạy lại kiểm thử và bộ đo (19/11/2026 trên DB tạm cô lập): `test_learner_model.py` (34/34) + `test_pedagogy_v55.py` (19/19) = **53/53 OK**; toàn bộ 8 mô-đun kiểm thử đơn vị đạt **156/156 OK**; `evaluate_learner_model_policy.py` **ĐẠT** (51/120 khác baseline, 120/120 giữ nguyên mức, 30/30 cổng `no_data`/`limited`); `evaluate_guardrails_benchmark.py` **leak_rate 0,0%, FPR 0,0%**.
- [x] Điền cấu hình máy thử nghiệm thật vào Bảng 4.1 (`Intel Core Ultra 7 255H, RAM 32 GB`).
- [x] Đối chiếu con số giữa Mở đầu, Mục 1.7, Chương 4 và Kết luận (156 ca kiểm thử đơn vị, 51/120 ô phát lại, 36/38, 13/14, 4/14, 0/24, 0/16, 6/6, 20 yêu cầu đồng thời, 22 ca + 48 lượt mô hình thật).
- [ ] Rà soát lần cuối trước khi nộp xem có muốn giữ nguyên Bảng 4.6–4.7 theo lần đo đầu (12/11/2026) song song với Mục 4.5.6 (18/11/2026) hay không (hiện cả hai mốc ngày đều được ghi chú rõ ràng).

## G. Định dạng cuối & nộp bài

- [x] Xóa sạch 100% các đoạn `[…]`, `[Bổ sung …]`, `[Lưu ý …]` và vùng tô vàng trong toàn văn và các bảng của `bao_cao_final.docx`.
- [x] Thêm `bao_cao_final.docx` và `~$*.docx` vào `.gitignore` để tránh commit nhầm file Word lên git.
- [ ] Mở Word bấm `Ctrl+A` → `F9` cập nhật Mục lục / Danh mục Bảng / Danh mục Hình, kiểm tra ngắt trang (đặc biệt trang `DANH MỤC BẢNG`) và xuất PDF.
- [x] Nộp kiểm tra Turnitin: Kết quả chỉ số tương đồng đạt **3%** (xuất sắc, đạt chuẩn nguyên bản của Nhà trường < 20%). Đã tích hợp đầy đủ Bảng E.1 và nội dung báo cáo vào Phụ lục E của `bao_cao_final.docx`. Kẹp trang Digital Receipt vào cuối bản in lưu chiểu.
- [ ] Đổi tên bản nộp cuối theo quy định Khoa (ví dụ `11236131_Trần Minh Khánh_Xây dựng hệ thống hỗ trợ học lập trình Python.docx`).

## H. Việc chỉ bạn làm được trước khi in nộp

- Mở Word bấm `Ctrl+A` → `F9` cập nhật số trang mục lục, rà layout và xuất PDF.
- Chạy Turnitin trên cổng nhà trường và kẹp báo cáo vào Phụ lục E.
- Ký tay sinh viên ở Lời cam đoan và xin chữ ký GVHD trên bản in.
- *(Tùy chọn)* Chụp lại Hình 4.7 nếu muốn hiển thị thêm khối Open Learner Model v3 mới; mời người chấm độc lập hoặc người dùng thật nếu còn thời gian trước hạn nộp.
