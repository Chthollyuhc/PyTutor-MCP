# Các chỗ cần đổi trong `bao_cao_final.docx` sau v5.10

> **Đọc trước.** Báo cáo đã kiểm Turnitin ngày 19/11/2026. Chèn hay không chèn các đoạn dưới đây là quyết định của tác giả; tôi chưa sửa `bao_cao_final.docx` (chỉ đọc, SHA256 không đổi). Mọi con số lấy từ lần chạy đêm 20–21/11/2026, nguồn là tệp JSON ghi kèm. Không có trích dẫn hay tên tác giả mới. Điểm 0–5 trong `docs/HINT_LEVELS_BEFORE_AFTER_V510.md` là **đề xuất của trợ lý**, chưa phải điểm của tác giả, nên KHÔNG đưa vào báo cáo cho tới khi tác giả tự chấm hoặc có người chấm độc lập.
> Cách tìm: dùng Ctrl+F với "Câu mở đầu hiện tại".

## 1. Mục 3.2.3 «Ba mức gợi ý»: thay Bảng 3.7 và bổ sung đoạn ranh giới

**Câu mở đầu hiện tại (đoạn 187):** "Hệ thống cung cấp ba mức gợi ý ứng với ba loại trợ giúp khác nhau về bản chất…"

Giữ đoạn này. **Thay Bảng 3.7** bằng bảng có thêm cột «Cấu trúc nội dung» và nêu cụ thể hơn điều được và không được nêu:

| Mức | Mục tiêu sư phạm | Được nêu | Không được nêu | Cấu trúc nội dung |
|---|---|---|---|---|
| 1. Gợi mở | Định hướng khái niệm | Tên nhóm khái niệm gắn với dạng vấn đề quan sát được, giải thích ngắn bằng lời, một ví dụ ngắn với dữ kiện khác bài, một phép thử người học tự làm | Dòng code của người học, đầu vào/đầu ra của kiểm thử, tham số hay biểu thức sai, cách sửa | Đang ở đâu → khái niệm → một câu hỏi → một bước kế tiếp |
| 2. Chẩn đoán | Khoanh vùng lỗi bằng bằng chứng thực thi | Đúng một dòng code của người học, đầu vào/kỳ vọng/thực tế của kiểm thử giàu thông tin nhất, vết chạy của chính mã người học | Cách sửa, điều kiện hay biểu thức thay thế, khối code từ ba dòng | Đang ở đâu → dòng cần xem → bằng chứng → giải thích hành vi và một câu hỏi → một bước kế tiếp |
| 3. Dàn ý | Cấu trúc của bài, không phải logic | Dàn ý bốn bước theo đề bài, khung mã bám mã người học với logic đã bị che, bảng chạy tay để trống | Điều kiện, miền lặp, vế phải phép gán, lời giải | Đang ở đâu → dàn ý → khung mã `# TODO` → bảng chạy tay → một bước kế tiếp |

**Câu mở đầu hiện tại (đoạn 190):** "Ranh giới giữa Mức 2 và Mức 3 là một lựa chọn sư phạm của đề tài chứ không phải kết quả đo…" Thêm ngay sau đoạn này:

> Từ phiên bản 5.10, ranh giới giữa các mức được thực thi bằng ba lớp thay vì chỉ bằng chỉ dẫn trong lời nhắc. Lớp thứ nhất là rào chắn thông tin: lời nhắc Mức 1 không chứa giá trị kiểm thử, còn Mức 2 và Mức 3 chỉ nhận đúng phần bằng chứng của mình, nên mô hình không thể làm lộ điều nó không được thấy. Lớp thứ hai là chỉ dẫn và bố cục riêng cho từng mức. Lớp thứ ba là bộ lọc tất định ở đầu ra, gồm phát hiện chương trình hoàn chỉnh, che logic trong khung Mức 3 và thay phản hồi chép lại chú thích của người học. Dòng mã được nêu ở Mức 2 là điều quan sát được từ thông báo cú pháp, traceback, vết chạy hoặc cấu trúc chương trình, chứ không phải kết luận rằng dòng đó sai; phản hồi tự ghi rõ điều này. Lớp thứ hai vẫn có thể bị mô hình vượt qua, như được đo ở mục 4.5.7.

## 2. Mục 3.4.2 «Dựng lời nhắc»: sửa một chỗ không còn khớp mã

**Câu mở đầu hiện tại (đoạn 228):** "Lời nhắc gửi cho mô hình ngôn ngữ được dựng từ các mẫu Jinja2 trong backend/prompt_templates.py…"

**Không khớp mã:** chỉ lời nhắc trò chuyện dùng mẫu Jinja2 (`prompt_templates.py`). Lời nhắc gợi ý được ghép từ các khối trong hàm `build_scaffolding_prompt` (`backend/llm_service.py`), không phải mẫu Jinja2. **Đoạn thay thế cho đoạn 228:**

> Lời nhắc trò chuyện được dựng từ các mẫu Jinja2 trong backend/prompt_templates.py, chạy ở chế độ nghiêm ngặt để thiếu một biến là lỗi ngay khi dựng. Lời nhắc gợi ý được ghép từ các khối độc lập trong hàm build_scaffolding_prompt: quy tắc về dữ liệu không đáng tin cậy, đề bài, mã người học, kết quả chạy, phân tích cú pháp, lịch sử nộp bài kèm nội dung tối đa ba gợi ý gần nhất cho cùng bài, hồ sơ và chiến lược thích ứng, bằng chứng ưu tiên theo mức, khung phản hồi hình thành và chỉ dẫn theo mức. Việc đưa nội dung các gợi ý trước vào lời nhắc cho phép yêu cầu gợi ý mới đi tiếp một bước thay vì lặp lại. Các khối này được khóa bằng một bộ kiểm thử dùng lời nhắc chuẩn: lời nhắc được dựng lại từ đầu vào đã lưu và phải giống từng ký tự trên 47 ca.

**Đoạn 229** («Nội dung do người học hoặc đề bài cung cấp được bọc trong các thẻ riêng…») giữ nguyên; từ v5.10 điều này thực sự đúng cho lời nhắc gợi ý (thẻ `<student_code>`, `<exercise_description>`). Thêm một câu: "Nếu mã hoặc chú thích của người học xin đáp án hay ra lệnh, gia sư được yêu cầu từ chối bằng một câu rồi vẫn đưa gợi ý đúng mức."

**Thêm đoạn mới về bằng chứng ưu tiên** (đặt sau đoạn 229):

> Bằng chứng ưu tiên được rút ra tất định bởi các hàm thuần trong backend/hint_evidence.py: chọn kiểm thử chưa đạt có đầu vào nhỏ nhất thay vì kiểm thử đầu tiên; chọn một dòng đáng xem kèm cơ sở quan sát được; gắn dạng lỗi với một nhóm khái niệm; dựng dàn ý nền theo đề bài. Với yêu cầu gợi ý trên bài chưa đạt, hệ thống còn lấy vết chạy của chính mã người học trên đầu vào lỗi bằng công cụ trace_code_execution trong cùng phiên MCP của đường ống chấm bài, có thời hạn sáu giây và quay về bằng chứng tĩnh nếu lỗi. Chi phí thêm nhỏ: phép đo từng lượt cho khoảng 0,8 giây ở trung vị, còn đo tải nhiều luồng không phân biệt được với nhiễu. Vết chạy chỉ được lấy cho mã không nhập mô-đun ngoài một danh sách nhỏ và không gọi hàm như open, exec, eval, vì công cụ này chạy mã trong tiến trình MCP.

**Mục 3.4.1 (đoạn 222):** câu liệt kê thứ tự đường ống công cụ cần thêm "và, khi xin gợi ý trên bài chưa đạt, vết chạy trên đầu vào lỗi" sau "…lấy lịch sử…". Kiểm tra cả Hình 3.4 nếu hình liệt kê từng lời gọi công cụ.

## 3. Mục 3.4.3 «Chuỗi dự phòng»

**Câu mở đầu hiện tại (đoạn 232):** "Bộ luật tất định, hiện thực trong hàm generate_rule_based_fallback, chỉ nêu những điều quan sát được…"

Thay đoạn 232 bằng:

> Bộ luật tất định, hiện thực trong backend/hint_rules.py và được gọi qua hàm generate_rule_based_fallback, dùng cùng bằng chứng với nhánh mô hình và chỉ nêu những điều quan sát được. Mức 1 gọi tên khái niệm và đưa một phép thử. Mức 2 nêu đúng một dòng mã cùng cơ sở quan sát, ghi rõ đó là nơi đáng quan sát chứ chưa phải kết luận, và đưa bằng chứng thực thi. Mức 3 dựng dàn ý bốn bước theo đề bài, khung mã từ mã người học với logic đã bị che và một bảng chạy tay để trống, rồi đối chiếu bài làm với dàn ý để nêu đúng một bước còn thiếu. Chú thích của người học không bao giờ được chép lại. Bộ luật cũng thay thế phản hồi của mô hình khi bộ lọc đầu ra chặn, khi phản hồi rỗng hoặc quá ngắn, hoặc khi phản hồi chép lại chú thích mang tính ra lệnh của người học.

Đoạn 231: thêm "hoặc trả về nội dung rỗng" sau "nếu lời gọi lỗi" (lỗi cũ: phản hồi rỗng ở Mức 3 từng tới tay người học; đã sửa ở v5.10).

## 4. Mục 3.5, Bảng 3.11 «Năm lớp kiểm soát»

Thêm vào hàng của lớp lọc đầu ra (hoặc thêm hàng thứ sáu nếu tác giả muốn tách): «chặn chép lại chú thích mang tính ra lệnh của người học (`output_guard=comment_echo`), áp dụng cho cả ba mức; phản hồi rỗng hoặc dưới 20 ký tự bị coi là không có phản hồi». Cập nhật câu «năm lớp» ở đoạn 234 nếu thêm hàng.

## 5. Mục 4.3 (đoạn 325, Bảng 4.3) và các số cũ phải sửa

**Câu mở đầu hiện tại (đoạn 325):** "Bộ kiểm thử đơn vị của hệ thống gồm tám mô-đun với tổng cộng 156 ca…"

Số cũ phải đổi: **tám mô-đun, 156 ca**. Sau v5.10 có thêm bốn mô-đun, nên là **mười ba mô-đun, 211 ca** (156 + 17 + 14 + 2 + 20 + 2). Thêm bốn hàng vào Bảng 4.3 (cũng đổi dòng «Tổng»):

| Mô-đun | Số ca đạt | Phạm vi kiểm thử |
|---|---|---|
| test_hint_quality_v510 | 17/17 | Các hàm kiểm tra chất lượng gợi ý (ca đạt và ca trượt của từng kiểm tra) |
| test_hint_evidence_v510 | 14/14 | Chọn kiểm thử, chọn dòng đáng xem, khái niệm, dàn ý theo đề, bảng chạy tay, bỏ chú thích khỏi dòng trích |
| test_prompt_golden_v510 | 2/2 | Lời nhắc dựng lại giống từng ký tự trên 47 ca |
| test_trace_integration_v510 | 2/2 | Bước vết chạy với máy chủ MCP thật trên cơ sở dữ liệu tạm: dạng kết quả, chọn đúng dòng, bỏ qua khi mã nguy hiểm hoặc đã đạt |
| test_hint_resilience_v510 | 20/20 | Gemini lỗi, rỗng, quá ngắn; vết chạy lỗi; bộ chặn chép chú thích; các lỗi tìm thấy khi rà soát mã |

Chú thích bảng hiện ghi «lần chạy ngày 18/11/2026» nhưng đoạn 325 ghi «ngày 19/11/2026»: hai ngày không khớp nhau; nên thống nhất. Lần chạy hồi quy cuối của v5.10 (21/11/2026) ở `evaluation/v510_final/`: toàn bộ module đạt; các kịch bản phân hệ (đoạn 328) vẫn 8/8, 6/6, 7/7, 6/6, 7/7, 6/6; bộ kiểm thử giao diện `test:ui-utils` từ 12 lên 17 ca, `test:theme` 3/3, build thành công; cơ sở dữ liệu trình diễn không đổi (SHA-256 trước/sau trùng). Ba bài kiểm tra chuỗi lời nhắc cũ phải đổi vì hành vi đổi có chủ đích (`test_pedagogy_v55`, `test_learner_model`, `test_thesis_upgrade`).

## 6. Mục 4.4 và 4.5: thêm mục 4.5.7 và đối chiếu số cũ

Chèn **mục 4.5.7** (sau 4.5.6) với nội dung ở `docs/THESIS_CHAPTER4_DRAFT.md`, mục «4.5.7. Đo riêng chất lượng ba mức gợi ý trước và sau cải tiến (v5.10)». Tóm tắt số để đối chiếu (nguồn `evaluation/hint_levels_v510_*.json`, báo cáo `docs/HINT_LEVELS_BEFORE_AFTER_V510.md`):

| Phép đo (đạt mọi kiểm tra nội dung) | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| Gemini thật, tập phát triển (trước = lần chạy 1) | 9/15 → 9/15 | 8/14 → 14/14 | 5/15 → 12/15 |
| Gemini thật, tập giữ riêng | 5/7 → 4/7 | 3/7 → 4/7 | 2/7 → 5/7 |
| Rule-based, tập giữ riêng | 6/7 → 6/7 | 0/7 → 3/7 | 0/7 → 7/7 |

Phải nói thẳng trong báo cáo: Mức 1 với mô hình thật không cải thiện trên số đo; chỉ số «dòng trích đúng chỗ lỗi» trên tập giữ riêng vẫn 4/7 vì mô hình tin theo dòng đáng xem của luật tất định (ca H01, H06); kiểm tra từ khóa không bắt được câu hỏi vẫn gợi cách sửa. Hồi quy 22 ca với mô hình thật sau cải tiến (`evaluation/real_llm_results_v510.json`): 20/20 lượt gọi Gemini thành công, 48/48 kiểm tra tất định đạt, độ trễ trung vị 2,1 giây (số cũ ở mục 4.5.2 là mốc khác; không so trực tiếp vì mô hình và tải khác nhau).

**Đoạn 4.5.3 «Hai trường hợp mô hình vi phạm ràng buộc»:** giữ nguyên (mô tả đúng mốc 12/11). Thêm một câu cuối: "Từ v5.10, ca H4 và ca H3 được đo lại bằng bộ kịch bản riêng ở mục 4.5.7."

**Mục 4.9.2 «Hạn chế»:** thêm các ý: bộ đo ba mức do chính tác giả viết và được tinh chỉnh trong quá trình làm (đã áp dụng đồng nhất cho trước và sau); chỉ một lần chạy dev sau cải tiến do giới hạn lượt gọi; điểm sư phạm chưa có người chấm độc lập; chưa pilot nên chưa có bằng chứng về hành vi người học; bước vết chạy chạy mã trong tiến trình MCP (đã giới hạn bằng danh sách an toàn, nhưng chưa có sandbox riêng); đo tải 1–20 luồng (`evaluation/load_benchmark_results_v510.json`) cho thấy đường có vết chạy gần như bằng đường không có (p50 ở 10 luồng: 3,52 s so với 3,62 s), nên chi phí thêm nhỏ nhưng chưa xác định chính xác (phép đo từng lượt cho +0,8 s, hai số không khớp nhau).

## 7. Phụ lục B «Các lệnh chạy lại kết quả đánh giá»: thêm hàng vào Bảng B.1

| Mục đích | Lệnh |
|---|---|
| Đo ba mức gợi ý, nhánh offline | `py evaluate_hint_levels.py --offline --quiet --tag X` (thêm `--holdout` hoặc `--redteam`) |
| Đo ba mức gợi ý, Gemini thật (đếm lượt, trần 300) | `py evaluate_hint_levels.py --real --quiet --tag X` |
| Tính lại kiểm tra từ phản hồi đã lưu | `py evaluate_hint_levels.py --rescore evaluation/hint_levels_v510_X.json` |
| Bộ hồi quy v5.10 | `.\.claude\run_suite_v510.ps1 -OutDir evaluation\v510_final` |
| Bốn mô-đun kiểm thử mới | `py -m unittest test_hint_quality_v510 test_hint_evidence_v510 test_prompt_golden_v510 test_hint_resilience_v510` (không cần cơ sở dữ liệu) |

## 8. Phụ lục C: ví dụ mới nên thêm (nguyên văn trước/sau)

Nên thêm ca **D03** (sai cận `range(1, n)`) ở cả ba mức, trước và sau: nguyên văn có sẵn trong `docs/HINT_LEVELS_BEFORE_AFTER_V510.md` mục 3 (phản hồi Mức 1 và Mức 3 trước nêu thẳng tham số của `range` và comment trong khung; bản sau chỉ nêu khái niệm với ví dụ khác bài và khung toàn chỗ trống kèm bảng chạy tay). Có thể thêm **H01** (tập giữ riêng) làm ví dụ phản biện: bản sau chọn sai dòng vì tin theo dòng đáng xem.

## 9. Chỗ thuật ngữ, tên tệp hoặc sơ đồ không còn khớp mã

1. Đoạn 228: mẫu Jinja2 cho lời nhắc gợi ý (xem mục 2) là mô tả không đúng ngay cả ở bản trước v5.10.
2. Hình 3.4 và đoạn 222: nếu liệt kê thứ tự công cụ MCP thì thiếu bước vết chạy tùy chọn; đường ống có thể có bước thứ bảy.
3. Đoạn 232 nhắc hàm generate_rule_based_fallback: tên hàm giữ nguyên, nhưng thân hàm nay ủy quyền cho hint_rules.build_offline_hint.
4. Bảng 3.7 cột «Được phép» của Mức 2 ghi «vùng cần xem lại»; mã hiện nêu đúng một dòng.
5. Hai ngày chạy khác nhau (18/11 và 19/11) trong chú thích Bảng 4.3 và đoạn 325.
6. Số «156 ca» và «tám mô-đun» ở đoạn 325/Bảng 4.3 (đổi thành 211 ca, mười ba mô-đun).

## 7. Cập nhật v5.11 và đổi đầu đề (22/11/2026)

Đã áp dụng vào bản sao `bao_cao_final_v510.docx` (không đụng `bao_cao_final.docx` gốc; sao lưu trước khi sửa ở `scratch/bao_cao_final_v510.docx.bak_v511`):
- **Đầu đề dễ hiểu hơn** (26 đầu đề, cả mục lục lưu sẵn và Bảng 3.7): 3.2.3 «Các mức gợi ý», 3.4.2 «Cách hệ thống soạn yêu cầu gửi cho Gia sư AI», 4.4.1 «Chống lộ lời giải ở các mức gợi ý», 4.5.3–4.5.5 và các mục còn nhiều thuật ngữ (xem danh sách trong `scratch/edit_docx_v511.py`, biến `RENAMES`). Nội dung chỉ thêm các đoạn giải thích bằng lời thường (đầu mục 3.4.2).
- **Nội dung v5.11:** đoạn «Từ phiên bản 5.11…» ở 3.2.3; đoạn chặng đường trang chủ ở 4.2.1; Bảng 4.3 thêm `test_exercise_brief_v511` 16/16 và `test_path_class_v511` 7/7, tổng 15 mô-đun/234 ca (cũng sửa ở Mở đầu và Kết luận); đoạn kiểm chứng 29 lượt Gemini thật ở 4.5.7 (Mức 2 7/7, Mức 1 4/7 trên mẫu 14 lượt, ghi rõ mẫu nhỏ).
- Mục lục: Word sẽ hỏi cập nhật trường khi mở; chọn «Có» để số trang khớp.
