# Bản nháp Chương 4 — Kết quả và đánh giá

> **Trạng thái: BẢN NHÁP do trợ lý AI soạn ngày 13/11/2026 để sinh viên chỉnh sửa.** Mọi con số đều lấy từ tệp kết quả trong repo (ghi rõ ở từng mục) và có thể chạy lại bằng lệnh kèm theo. Các chỗ đánh dấu **[SV bổ sung]** là phần chỉ sinh viên làm được (ảnh chụp màn hình, pilot người dùng, điểm chấm tay). Không sao chép nguyên văn vào khóa luận khi chưa đọc lại: văn phong cần thống nhất với các chương khác và mọi trích dẫn học thuật phải do sinh viên tự kiểm tra nguồn.
>
> Cấu trúc bám theo cách các khóa luận đã bảo vệ của Trường Công nghệ – NEU trình bày chương kết quả (môi trường → kết quả chức năng → đánh giá → hạn chế), và bổ sung phần mà các khóa luận đó thường thiếu: tách bạch bằng chứng kỹ thuật với bằng chứng sư phạm.

---

## 4.1. Môi trường và phương pháp đánh giá

### 4.1.1. Môi trường

| Thành phần | Cấu hình |
|---|---|
| Máy thử nghiệm | Một máy cá nhân, Windows 11 **[SV bổ sung CPU/RAM]** |
| Backend | Python 3.14, FastAPI, SQLite (chế độ WAL) |
| Lớp công cụ | Tiến trình `mcp_server` riêng, giao tiếp JSON-RPC 2.0 qua stdio, 8 công cụ |
| Frontend | React 18, Vite, Tailwind, Monaco Editor |
| Mô hình ngôn ngữ | Gemini `gemini-3.5-flash-lite`; dự phòng Qwen; cuối cùng là bộ luật sư phạm tất định (offline) |
| Dữ liệu | Cơ sở dữ liệu và chỉ mục tri thức **tạm, cô lập** cho mọi lần đo; dữ liệu người học đều là giả lập |

### 4.1.2. Ba tầng bằng chứng

Khóa luận không gộp các loại bằng chứng khác bản chất vào một con số. Kết quả được trình bày theo ba tầng, tầng sau không thay được tầng trước:

| Tầng | Câu hỏi trả lời | Dữ liệu | Trạng thái |
|---|---|---|---|
| A. Kiểm thử tự động | Hành vi cài đặt có đúng đặc tả không? | Fixture do dự án viết | Đã chạy (mục 4.3) |
| B. Benchmark tất định và đo với LLM thật | Các thành phần cho tỷ lệ bao nhiêu trên bộ ca cố định? Mô hình thật có tuân thủ ràng buộc sư phạm không? | Corpus tự soạn, 22 ca chuẩn hóa | Đã chạy (mục 4.4–4.6) |
| C. Người dùng thật | Người học và giảng viên có hiểu và dùng được phản hồi không? | Người tham gia thật | **Chưa thực hiện** (mục 4.8) |

Điều chương này **không** khẳng định: không có số liệu nào ở tầng A hoặc B chứng minh người học tiến bộ hơn nhờ hệ thống. Đó là câu hỏi của một nghiên cứu có đối chứng, nằm ngoài phạm vi khóa luận.

---

## 4.2. Kết quả xây dựng chức năng

**[SV bổ sung ảnh chụp màn hình cho từng mục; gợi ý ảnh ghi trong ngoặc.]**

### 4.2.1. Phía người học

1. **Ba hành động tách biệt trong IDE.** `Chạy thử` chỉ chạy kiểm thử, không gọi AI và không tính điểm; `Hỏi Gia sư AI` xin gợi ý theo mức; `Nộp bài` là lượt chấm chính thức. Việc tách này để người học thử–sai thoải mái mà không bị "phạt" vào hồ sơ. *(Ảnh: thanh ba nút và bảng kết quả kiểm thử.)*
2. **Gợi ý ba mức theo nguyên tắc giàn giáo (scaffolding).** Mức 1 đặt câu hỏi gợi mở; Mức 2 chỉ ra kiểm thử chưa đạt và khoanh vùng; Mức 3 cho dàn ý bốn bước và khung mã có chỗ trống. Hệ thống không tự nâng mức vượt mức người học yêu cầu. Ở nhánh offline, gợi ý Mức 3 đối chiếu bài làm với dàn ý (đã có phần đọc dữ liệu, rẽ nhánh/vòng lặp, in kết quả hay chưa) và chỉ nêu **một** bước kế tiếp còn thiếu, kèm lời nói rõ hệ thống chỉ thấy các phần đó có mặt chứ chưa biết chúng đúng hay sai. *(Ảnh: cùng một bài sai ở ba mức.)*
3. **Khung phản hồi hình thành.** Mỗi gợi ý theo cấu trúc "đang ở đâu → bằng chứng từ kiểm thử → một bước kế tiếp vừa sức". *(Ảnh: một gợi ý Mức 2.)*
4. **Chiến lược thích ứng.** Từ kết quả kiểm thử, lịch sử làm bài và hồ sơ, hệ thống chọn một trong bốn chiến lược (`conceptual_start`, `failed_case_diagnosis`, `recurring_difficulty`, `solution_review`). Chiến lược chỉ đổi *cách* gợi ý, không đổi *mức* gợi ý.
5. **Trò chuyện theo phạm vi.** Trước khi nộp đạt, trò chuyện chỉ bàn khái niệm; sau khi đạt mới bàn về bài đã nộp. Câu trả lời có nguồn thì hiện nguồn, không có thì nói rõ "không có tài liệu nội bộ phù hợp". *(Ảnh: hai trạng thái nguồn.)*
6. **Chạy từng bước.** Người học xem giá trị biến thay đổi theo từng dòng lệnh. *(Ảnh: thanh trượt bước chạy.)*
7. **Sao tự làm có giải thích.** Số sao phụ thuộc mức gợi ý cao nhất đã dùng trước lần nộp đạt đầu tiên; số lần nộp không trừ sao; thẻ lý do nêu rõ quy tắc và cách cải thiện. *(Ảnh: thẻ lý do sao.)*
8. **Hồ sơ học tập có trạng thái dữ liệu.** Khi dữ liệu còn ít, hồ sơ ghi "chưa đủ dữ liệu" thay vì đưa ra nhận định. *(Ảnh: hồ sơ ở trạng thái `limited`.)*

### 4.2.2. Phía giảng viên

1. Quản lý lớp học phần, ngân hàng bài tập và bộ kiểm thử.
2. **Nhóm quá trình học:** mỗi cặp sinh viên–bài được xếp vào một trong sáu nhóm mô tả (đạt độc lập, đạt sau thử–sửa, đạt nhờ gợi ý, đang tiến triển, mắc kẹt, chỉ chạy thử) để giảng viên biết ai cần hỗ trợ. Các ngưỡng là quy ước vận hành, chưa hiệu chuẩn (`docs/PROCESS_GROUPS.md`).
3. **Tài liệu Gia sư AI theo lớp:** giảng viên tải tài liệu lên; lớp nào chỉ thấy tài liệu lớp đó.
4. **Hỏi đáp phân tích lớp:** chỉ số liệu tổng hợp được đưa cho mô hình, không có mã nguồn hay danh tính sinh viên.

---

## 4.3. Tầng A — Kiểm thử tự động

Nguồn: lần chạy lại ngày 13/11/2026 (mục 4.3.1); mô tả chi tiết từng lớp kiểm thử ở `docs/EVALUATION_REPORT_V5_3.md` mục 1. Mỗi module chạy trên một cơ sở dữ liệu tạm riêng, tắt LLM.

| Module | Số ca | Phạm vi |
|---|---:|---|
| `test_thesis_upgrade` | 60 | Phản hồi hình thành, nguồn RAG, luật sao, khóa phạm vi trò chuyện, đồng bộ hai bản mô hình người học, nhóm quá trình học, tài liệu theo lớp |
| `test_phase16_ai_upgrade` | 6 | Kiểm soát đầu vào/đầu ra, prompt, truy xuất cơ bản |
| `test_phase17_adaptive_analytics` | 5 | Chọn chiến lược, định nghĩa chỉ số, `data_status` |
| `test_qa_authorization` | 9 | Phân quyền phía máy chủ, quyền sở hữu lớp |
| `test_level3_scaffold` | 15 | Che logic trong khung mã Mức 3 (mục 4.5.3); gợi ý Mức 3 offline theo tiến độ bài làm |
| `test_passwords` | 7 | Băm mật khẩu, tương thích ngược với dạng văn bản thường, đăng nhập tài khoản mẫu |
| `test_pedagogy_v55` | 19 | Prompt giải thích khái niệm, nêu rõ khi không có tài liệu, đơn vị của nhóm quá trình học (mục 4.5.4) |

### 4.3.1. Kết quả lần chạy lại 13/11/2026

| Hạng mục | Kết quả |
|---|---|
| `test_thesis_upgrade` | 60/60 đạt |
| `test_phase16_ai_upgrade` | 6/6 đạt |
| `test_phase17_adaptive_analytics` | 5/5 đạt |
| `test_qa_authorization` | 9/9 đạt |
| `test_level3_scaffold` (mới) | 15/15 đạt |
| `test_passwords` (mới) | 7/7 đạt |
| `test_pedagogy_v55` (mới) | 19/19 đạt |
| **Tổng unittest** | **121/121 đạt** |
| Kịch bản lớp công cụ (`mcp_server.test_mcp_server`) | 8/8 bước đạt |
| Kịch bản backend đầu-cuối (`backend.test_backend_e2e`) | 6/6 đạt |
| Kịch bản trò chuyện, sao tự làm, lớp học phần (`test_phase8/10/12`) | 7/7, 6/6, 7/7 đạt |
| Benchmark chống lộ lời giải, RAG, chiến lược thích ứng | Kết quả đếm trùng với mục 4.4 |
| Biên dịch `backend`, `mcp_server` | Đạt |
| Cơ sở dữ liệu thật `pytutor.db` | Không đổi (so băm SHA-256 trước và sau) |

Các kịch bản phân hệ cũ (chạy lại cùng ngày): `test_phase5_backend` đạt, `test_phase9_visualizer` 7/7, `test_phase15_3_qa_audit` 6/6, `test_phase15_4_action_buttons` đạt **sau khi sửa kịch bản** (kịch bản không khởi tạo bảng trên cơ sở dữ liệu tạm nên báo lỗi 500; đây là lỗi của kịch bản khi cô lập dữ liệu, không phải của API). `test_phase13_14_neu_lms` 8/8 đạt **sau khi sửa kịch bản**: kịch bản gán một bài tập chưa tồn tại trên cơ sở dữ liệu tạm (nó chỉ có sẵn trong cơ sở dữ liệu demo tích lũy), và API từ chối đúng; kịch bản nay tự tạo bài bằng chính giảng viên đang gán. Đây là lỗi của kịch bản khi cô lập dữ liệu, không phải của API. Giao diện: `test:theme` 3/3, `vite build` thành công.

**Giới hạn:** kiểm thử xác nhận mã làm đúng điều người viết kiểm thử mong đợi; nó không đo tần suất lỗi trên dữ liệu chưa thấy và không kiểm tra giao diện.

---

## 4.4. Tầng B — Benchmark tất định

Nguồn: `docs/EVALUATION_REPORT_V5_3.md` mục 2. Cả ba benchmark không gọi LLM và cho cùng kết quả đếm khi chạy lại.

### 4.4.1. Chống lộ lời giải (Mức 1–2 và trò chuyện)

| Chỉ số | Tập phát triển | Tập giữ riêng |
|---|---|---|
| Tình huống tấn công bị rò rỉ lời giải | 0/30 | **4/14** |
| Chặn đầu vào chèn lệnh hoặc ngoài phạm vi | 22/22 | **1/10** |
| Chặn nhầm câu hỏi hợp lệ | 0/28 | 1/12 |
| Chặn nhầm phản hồi gia sư hợp lệ | 0/31 | 0/12 |

Cách đọc: bộ luật được chỉnh trên chính tập phát triển, nên 0/30 chỉ là kiểm tra hồi quy. Tập giữ riêng, soạn sau khi đóng băng luật và không dùng để chỉnh, cho thấy bộ lọc dựa trên biểu thức chính quy còn lọt lời giải trình bày dạng bảng, dạng a)/b)/c) hoặc lồng trong câu văn. Khóa luận báo cáo cả hai con số; bộ lọc là một lớp phòng vệ bổ sung cho chỉ dẫn trong prompt, không phải bảo đảm.

### 4.4.2. Truy xuất tri thức (RAG)

Bộ câu hỏi: 38 câu có nội dung trong kho tri thức, 14 câu ngoài kho; 17 đoạn tri thức; ngưỡng liên quan 0,16.

| Chỉ số | Kết quả |
|---|---|
| Đúng mục ở vị trí 1 (hit@1) | 34/38 = 89,47% |
| Đúng mục trong 3 kết quả đầu (hit@3) | 36/38 = 94,74% |
| MRR | 0,9211 |
| Câu ngoài kho được trả lời "không có nguồn" | 13/14 = 92,86% |

Không đặt ngưỡng thì mọi câu ngoài kho đều bị gắn một nguồn không liên quan (0/14). Ngưỡng 0,16 đổi 2 câu trong kho bị trượt lấy 13/14 câu ngoài kho được xử lý trung thực. Ngưỡng được chọn trên chính bộ câu hỏi này nên kết quả lạc quan hơn so với câu hỏi mới; kho tri thức là tài liệu nội bộ, chưa phải giáo trình chính thức của NEU.

### 4.4.3. Chọn chiến lược thích ứng

Bộ phát lại 6 tình huống tổng hợp: chiến lược khớp kỳ vọng 6/6; giữ nguyên mức gợi ý người học yêu cầu 6/6; phương án đối chứng cố định một chiến lược chỉ khớp 2/6. Đây là kiểm tra tính đúng của chính sách trên ca do dự án định nghĩa, không phải bằng chứng về hiệu quả học tập.

### 4.4.4. Chính sách dùng mô hình người học (phát lại tổng hợp)

`evaluate_learner_model_policy.py` dựng 8 hồ sơ tổng hợp bằng cách chèn chuỗi sự kiện vào cơ sở dữ liệu tạm rồi chạy qua `compute_student_model` và chính sách; mỗi hồ sơ xét 5 trạng thái bài × 3 mức gợi ý = 120 ô, tắt mô hình ngôn ngữ (`PYTUTOR_DISABLE_LLM=1`). Đối chứng là cùng chính sách nhưng bỏ qua mô hình người học.

| Chỉ số | Kết quả |
|---|---|
| Chính sách khác đối chứng bỏ qua mô hình | 51/120 (42,5%) |
| Giữ nguyên mức gợi ý yêu cầu | 120/120 |
| Nhất quán bằng chứng (bộ kiểm độc lập) | 120/120 |
| Cổng đúng trên hồ sơ `no_data`/`limited` (không kích hoạt luật mô hình) | 30/30 |
| Văn bản phản hồi offline khác đối chứng | 31,7% |

Bộ phát lại 6 tình huống ở mục 4.4.3 vẫn đạt 6/6. Kiểm thử: `test_learner_model` 31, `test_thesis_upgrade` 61.

**Phạm vi:** đây là phát lại hành vi chính sách trên hồ sơ tổng hợp do dự án định nghĩa. Nó cho thấy mô hình **làm thay đổi** phản hồi một cách đo được và không phá ràng buộc mức gợi ý; nó **không** phải nghiên cứu kết quả học tập, không dùng mô hình ngôn ngữ thật, và pilot người dùng chưa chạy. Tỷ lệ 42,5% phụ thuộc cách dựng hồ sơ và các ngưỡng quy ước, không đọc là "hiệu quả".

---

## 4.5. Đo với mô hình ngôn ngữ thật

Nguồn: `docs/REAL_LLM_EVALUATION.md`, `evaluation/real_llm_results.json` (đo ngày 12/11/2026, 22 ca tự soạn, mô hình `gemini-3.5-flash-lite`, dữ liệu giả lập).

### 4.5.1. Kiểm tra tất định theo nhóm

| Nhóm | Số ca | Kiểm tra tất định đạt |
|---|---:|---|
| 1. Gợi ý thích ứng | 5 | 11/12 |
| 2. Khóa phạm vi trò chuyện | 5 | 12/12 |
| 3. Bám nguồn RAG và tách tài liệu theo lớp | 5 | 12/12 |
| 4. An toàn | 4 | 4/4, một ca cần rà tay |
| 5. Phân tích lớp cho giảng viên | 3 | 8/8 |

Điểm sư phạm 0–5 cho từng phản hồi: **[SV bổ sung — chấm tay theo rubric trong `docs/REAL_LLM_EVALUATION.md`; nên nhờ thêm một người chấm độc lập và báo cáo mức đồng thuận].**

### 4.5.2. Độ trễ và chi phí

| Chỉ số (20 lượt gọi) | Giá trị |
|---|---|
| Độ trễ nhỏ nhất / trung vị / P90 / lớn nhất | 4,5 s / 11,9 s / 28,2 s / 37,0 s |
| Token đầu vào trung bình | 1.202,5 |
| Token đầu ra trung bình | 199,1 |

Trung vị gần 12 giây là dài đối với phản hồi trong lúc đang làm bài. Đây là hạn chế cần nêu thẳng: nhánh offline phản hồi gần như tức thì nhưng kém cụ thể hơn.

### 4.5.3. Hai ca mô hình thật vi phạm ràng buộc sư phạm, và cách hệ thống xử lý

Đây là phần đáng giá nhất của lần đo, vì nó cho thấy chỉ dẫn trong prompt là chưa đủ.

- **Ca H3 (Mức 2).** Mô hình đưa nhiều câu lệnh trong dấu `` ` ``. Bộ lọc đầu ra phát hiện (`solution_inline_code`) và hệ thống thay bằng gợi ý tất định, chỉ nêu điều quan sát được từ kiểm thử. Người học không thấy lời giải.
- **Ca H4 (Mức 3).** Người học mới viết một dòng đọc đầu vào và xin dàn ý. Mô hình trả khung mã có `# TODO` nhưng đã **điền sẵn phép kiểm tra cốt lõi** (`if n % i == 0:`). Tại thời điểm đo, Mức 3 không có lớp kiểm soát nào vì khung mã dài là hợp lệ ở mức này.

Từ ca H4, hệ thống được bổ sung bước **che logic tất định cho khung mã Mức 3** (`enforce_level3_skeleton` trong `backend/guardrails.py`): giữ phần giàn giáo (đọc đầu vào, khởi tạo bằng hằng, `print`, `else:`, chú thích, dòng đã có `...`) và thay điều kiện, miền lặp, vế phải phép gán, lệnh xử lý bằng `...  # TODO`. Khung sau khi che vẫn là Python hợp lệ nên người học chạy thử được ngay. Nguyên tắc: *Mức 3 cho cấu trúc, không cho lập luận.*

Áp bước che lên đúng phản hồi H4 đã ghi: dòng `if n % i == 0:` trở thành `if ...:  # TODO: tự viết điều kiện`; dàn ý bốn bước bằng lời giữ nguyên. Sáu ca kiểm thử của lớp `Level3SkeletonTests` trong `test_level3_scaffold.py` khóa hành vi này, trong đó một ca dùng chính phản hồi thật của mô hình.

**Đo bước che bằng cách chạy khung đã che.** Trường hợp xấu nhất ở Mức 3 là mô hình trả nguyên một lời giải đầy đủ. Script `evaluate_level3_skeleton.py` lấy các lời giải đầy đủ của 5 bài mẫu (nhiều phong cách viết), cho qua bước che, rồi **chạy khung đã che trên chính bộ kiểm thử của bài**. Một lời giải bị tính là "lọt" khi khung đã che vẫn đạt mọi kiểm thử.

| Tập | Số lời giải | Lọt nguyên vẹn | Kiểm thử còn đạt sau khi che | Khung còn là Python hợp lệ | Dòng lệnh bị che |
|---|---:|---:|---:|---:|---:|
| Phát triển, luật ban đầu | 24 | **7/24** | 45/125 | 24/24 | 51/129 |
| Phát triển, luật sau khi sửa | 24 | 0/24 | 9/125 | 24/24 | 63/129 |
| **Giữ riêng**, luật sau khi sửa (đo một lần) | 16 | **0/16** | 0/83 | 16/16 | 40/73 |

Lần đo đầu cho thấy bản che đầu tiên bỏ sót hai dạng: logic nằm ngay trong `print(...)` (công thức, cắt chuỗi, lời gọi thư viện) và logic nằm cùng dòng với `input()`. Luật được sửa để chỉ giữ lệnh in hằng hoặc tên biến và lệnh đọc dữ liệu thuần. Chín kiểm thử còn đạt trên tập phát triển là các ca mà khung chỉ còn in hằng `"NO"` trùng với đáp số.

**Giới hạn:** (i) luật được sửa trên chính tập phát triển, nên 0/24 chỉ là kiểm tra hồi quy; tập giữ riêng được soạn sau khi đóng băng luật và không dùng để chỉnh, nhưng do cùng một người soạn và chỉ có 16 ca nên 0/16 không phải là bảo đảm; (ii) phép đo chỉ trả lời "lời giải chạy được có lọt không", **không** trả lời "khung còn lại có đủ giúp người học không" — che nhiều quá cũng là thất bại sư phạm, và điều này chỉ pilot mới cho biết (phiếu F1 câu 13); (iii) phần dàn ý bằng lời vẫn có thể mô tả thuật toán khá sát; (iv) bước che chưa được chạy lại với mô hình thật. **[SV: nếu chạy lại `evaluate_real_llm.py`, cập nhật kết quả ca H4 tại đây.]**

### 4.5.4. Ba kiểu lỗi khác tìm thấy khi đọc nguyên văn 22 phản hồi

Kiểm tra tự động chỉ bắt được việc lộ lời giải. Đọc nguyên văn cho thấy thêm ba kiểu lỗi sư phạm mà phản hồi vẫn "an toàn" (bản chấm đề xuất: `docs/REAL_LLM_SCORING_PROPOSAL.md`; **[SV tự đọc và chốt]**):

| Kiểu lỗi | Ca | Chỉnh sửa | Mức kiểm chứng |
|---|---|---|---|
| Người học hỏi một khái niệm chung, gia sư chỉ hỏi ngược lại, không cho thông tin | C1, R1 | Prompt trò chuyện: giải thích trực tiếp 2–4 câu, tối đa một ví dụ 2 dòng, rồi đúng một câu hỏi kiểm tra; vẫn không bàn mã của bài đang làm | Chỉ khóa nội dung prompt; chưa đo với mô hình thật |
| Người học hỏi "theo tài liệu của lớp" khi lớp không có tài liệu; câu trả lời không nói điều đó | R3 | Thêm chỉ dẫn vào prompt | Như trên |
| Trả lời giảng viên gọi số "cặp sinh viên–bài" là "sinh viên" (12 "sinh viên" trong lớp có 5 người hoạt động) | I1 | Nêu đơn vị trong prompt; gắn ghi chú đơn vị tất định khi phát hiện mẫu câu này | Phản hồi I1 đã ghi được gắn ghi chú |

Với việc nguồn được hiển thị dù câu trả lời không dùng tới (C2, C4, R1), giao diện đổi nhãn từ "Nguồn tham khảo nội bộ" thành "Tài liệu nội bộ liên quan" và nói rõ đó là tài liệu gia sư được cung cấp khi trả lời; hệ thống vẫn chưa kiểm tra được câu trả lời có thật sự dựa vào tài liệu hay không. Kiểu chưa xử lý: gợi ý Mức 1 đã khoanh vùng lỗi (H2).

**Đo lại với mô hình thật sau các chỉnh sửa (13/11/2026, cùng 22 ca; kết quả: `evaluation/real_llm_results_v55b.json`).** Lần đo giữa chừng cho thấy một hồi quy do chính chỉnh sửa gây ra: prompt cho phép ví dụ tới 2 dòng, còn bộ lọc đầu ra chặn khối code từ 3 dòng, nên các câu trả lời khái niệm đúng (R1, R2) bị chặn nhầm. Đã sửa prompt thành "ví dụ ngắn viết inline, không dùng khối code nhiều dòng". Lần đo cuối:

| Chỉ số | Lần đo ban đầu (12/11) | Sau chỉnh sửa (13/11) |
|---|---|---|
| Lượt gọi mô hình thành công | 19/20 | 19/20 |
| Bị bộ lọc đầu ra chặn | 1 (H3) | 1 (H3) |
| Mức 3 được che logic | không áp dụng | 1 (H4: 2 chỗ) |
| Trung vị độ trễ | 11,9 s | 1,9 s |

Đối chiếu từng ca: I1 gọi đúng đơn vị "cặp sinh viên–bài"; R3 nói rõ không có tài liệu rồi mới giải thích chung; C1 giải thích trực tiếp; R1 và R2 không còn bị chặn; H4 khung mã đã che điều kiện. **Ba lưu ý:** (i) độ trễ thấp hơn nhiều giữa hai lần đo là do điều kiện dịch vụ tại thời điểm đo, không phải do chỉnh sửa của dự án; không nên đưa vào khóa luận như một cải thiện; (ii) R1 cho thấy một bất nhất: câu trả lời nói "không tìm thấy tài liệu nội bộ" trong khi giao diện vẫn hiển thị "Tài liệu nội bộ liên quan" vì truy xuất đã trả một mục có điểm trên ngưỡng. Đã xử lý ở máy chủ (`reply_says_no_source`): khi phần đầu câu trả lời chứa cụm "không tìm thấy tài liệu nội bộ/nào", trạng thái đặt thành `no_source` và bỏ danh sách nguồn. Cách này chỉ bắt được đúng cụm mà prompt yêu cầu mô hình dùng; nếu mô hình diễn đạt khác thì bất nhất vẫn có thể xảy ra, và việc này mới được kiểm tra trên phản hồi đã ghi (R1, R2), chưa chạy lại với mô hình thật; (iii) đây vẫn là 22 ca tự soạn, một lần đo, điểm sư phạm chưa được chấm tay.

**Lần đo thứ ba và tính dao động của mô hình (`evaluation/real_llm_results_v55c.json`).** Sau khi thêm vào Mức 1 ràng buộc "không nêu đầu vào/đầu ra cụ thể của kiểm thử" (ca H2), chạy lại cho thấy H2 không còn trích số liệu kiểm thử, nhưng R1 lại bị bộ lọc chặn (`solution_inline_code`) vì mô hình đưa nhiều đoạn code inline dạng phép gán. Qua ba lần chạy cùng một prompt gốc hoặc gần như gốc, R1 bị chặn ở lần 1 và lần 3, không bị chặn ở lần 2. Điều này cho thấy: (i) mỗi ca chỉ có một mẫu cho mỗi lần chạy, nên một lần chạy "sạch" không chứng minh được hành vi ổn định; (ii) kết quả với mô hình thật dao động giữa các lần chạy, nên khóa luận chỉ nên báo cáo tỷ lệ trên nhiều lần chạy, không nêu từng ca như bằng chứng; (iii) bộ lọc đầu ra chặn nhầm câu trả lời khái niệm đúng khi mô hình dùng nhiều đoạn code inline, và đây là cái giá của việc bộ lọc thiên về an toàn. Prompt được chỉnh thêm (tối đa hai đoạn code inline, không đoạn nào là phép gán) nhưng **bản chỉnh này chưa được chạy lại với mô hình thật**. **[SV: nếu có thể, chạy `evaluate_real_llm.py` nhiều lần (ví dụ 5 lần) rồi báo cáo số lần bị chặn trên tổng số lần cho từng ca.]**

**Đo nhiều lần để thay cho đo một mẫu** (`summarize_real_llm_runs.py`; 5 lần chạy `evaluate_real_llm.py` cho mỗi cấu hình prompt, cùng 22 ca; tổng hợp: `docs/REAL_LLM_RUNS_SUMMARY_BEFORE_L2.md` và `docs/REAL_LLM_RUNS_SUMMARY.md`, thô: `evaluation/runs_before_l2/`, `evaluation/runs/`). Con số là số lần xảy ra trên 5 lần chạy, **không phải ước lượng tỷ lệ** (5 mẫu là rất nhỏ).

| Ca | Hiện tượng | Cấu hình A (ví dụ inline, tối đa hai đoạn) | Cấu hình B (A + Mức 2 chỉ trích một dòng) |
|---|---|---:|---:|
| R1 | bị bộ lọc chặn | 0/5 | 0/5 |
| H4 | khung Mức 3 được che | 5/5 (che 1–2 chỗ) | 5/5 (che 1–2 chỗ) |
| H3 | Mức 2 bị bộ lọc chặn, rơi về phản hồi tất định | **5/5** | **4/5** |
| Các ca còn lại | bị chặn | 0/5 | 0/5 |

Hai điều rút ra. Thứ nhất, các chỉnh sửa cho R1 và H4 ổn định qua 5 lần chạy, khác với kết quả một mẫu trước đó (R1 từng bị chặn 2/3 lần). Thứ hai, **H3 vẫn chưa được giải quyết**: ở ca "lặp lại lỗi" Mức 2, phản hồi của mô hình gần như luôn bị bộ lọc chặn (`solution_inline_code`) và người học nhận phản hồi tất định kém cụ thể; giới hạn "một dòng" trong prompt chỉ giảm từ 5/5 xuống 4/5. Hệ thống không lưu bản phản hồi gốc bị chặn nên chưa rõ mô hình chèn gì; việc lưu bản gốc phục vụ phân tích (không hiển thị cho người học) là bước nên làm tiếp. Lưu ý thêm: kiểm tra tự động `knowledge_status=grounded` của R1 báo "không đạt" 1/5 ở cấu hình B vì sau bản sửa nhất quán nguồn, câu trả lời nói không có tài liệu thì trạng thái là `no_source`; đây là kiểm tra cũ lệch với hành vi mới, không phải lỗi của hệ thống.

**H3 là chặn nhầm, không phải lộ lời giải; sửa bộ lọc và đo lại** (cấu hình C; 5 lần chạy, `docs/REAL_LLM_RUNS_SUMMARY.md`, thô ở `evaluation/runs/`). Gọi trực tiếp mô hình với đúng đầu vào của ca H3 và in phản hồi gốc trước bộ lọc cho thấy phản hồi là chẩn đoán Mức 2 tốt: trích đúng một dòng của người học, nêu kiểm thử thất bại, hướng sửa bằng lời. Bộ lọc chặn vì đếm các đoạn inline `if n % i != 0:`, `if n > 1:` (đều là dòng của chính người học) và `Input = '2'` (nhãn bằng chứng kiểm thử) như thể đó là lời giải. Sửa: khi lọc gợi ý, **không đếm** đoạn inline trích lại đúng dòng code của người học hoặc nhãn bằng chứng kiểm thử (`quoted_context` trong `check_student_output`); dòng lệnh mới không có trong code của người học vẫn bị đếm và bị chặn (kiểm thử riêng). Tham số là tùy chọn nên benchmark không đổi: tập phát triển rò rỉ 0/30, tập giữ riêng vẫn lọt 4/14 ca như cũ.

| Ca | Hiện tượng | Cấu hình B | Cấu hình C (B + bỏ đếm trích dẫn của người học) |
|---|---|---:|---:|
| H3 | Mức 2 bị chặn, rơi về phản hồi tất định | 4/5 | **0/5** |
| H3 | kiểm tra tất định báo lộ lời giải (heuristic) | 0/5 | **2/5** |
| C3 | bị chặn (`solution_disclosure`) | 0/5 | 1/5 |
| R1, H4, các ca còn lại | như B | 0/5 / che 5/5 | 0/5 / che 5/5 |

Hai điều không có lợi cần nêu thẳng. **(i)** Heuristic của kịch bản báo H3 "lộ lời giải" 2/5 lần ở cấu hình C. Đọc nguyên văn hai phản hồi đó: mô hình mô tả bằng lời gần như toàn bộ cách sửa ("nếu n có ước số trong khoảng 2 đến n-1, tức `n % i == 0`, thì in `NO` rồi dừng; nếu vòng lặp chạy hết thì là số nguyên tố"). Đó không phải mã hoàn chỉnh nhưng sát với lời giải thuật toán; prompt Mức 2 hiện cho phép "chỉ dẫn kỹ thuật để sửa" nên hành vi này nằm trong thiết kế, nhưng có thể quá sát cho một phản hồi Mức 2. Đây là câu hỏi sư phạm chưa có đáp án: ranh giới giữa Mức 2 (giải thích hướng sửa) và Mức 3 (dàn ý) cần được chính sinh viên quyết định và kiểm tra trong pilot. **(ii)** Bỏ chặn nhầm đồng nghĩa phản hồi chi tiết hơn tới được người học, nên số liệu "bị chặn ít hơn" không tự nó là cải thiện: một nửa của cải thiện đó là đánh đổi với nguy cơ lộ hướng giải. C3 bị chặn 1/5 do cụm từ chối chứa "lời giải hoàn chỉnh" (bộ lọc dựa trên mẫu chữ, một giới hạn đã biết).

**Siết ranh giới Mức 2/Mức 3 (cấu hình D; 5 lần chạy; tổng hợp `docs/REAL_LLM_RUNS_SUMMARY.md`, thô ở `evaluation/runs/`; cấu hình C lưu ở `evaluation/runs_config_c/`).** Ở cấu hình C, phản hồi Mức 2 của H3 đôi khi mô tả gần hết cách sửa bằng lời. Đây là lựa chọn sư phạm của dự án, **không phải kết quả đo**: Mức 2 chỉ chẩn đoán *vì sao sai* và *nên xem lại hướng nào*, kết thúc bằng đúng một câu hỏi để người học tự đưa ra cách sửa; mọi chỉ dẫn mang tính cách sửa thuộc về Mức 3. Prompt Mức 2 được viết lại theo hướng đó (ví dụ cũ "bạn cần cho vòng lặp chạy đến `n + 1`" bị thay bằng câu hỏi).

| Chỉ số (5 lần chạy) | Cấu hình C | Cấu hình D |
|---|---:|---:|
| H3 bị bộ lọc chặn | 0/5 | 0/5 |
| H3 kiểm tra heuristic báo "lộ lời giải" | 2/5 | 1/5 |
| C3 bị chặn | 1/5 | 0/5 |
| H2, R1, các ca còn lại bị chặn | 0/5 | 0/5 |
| H4 khung Mức 3 được che | 5/5 | 5/5 |

Đọc nguyên văn phản hồi H3 ở cấu hình D: không còn câu nêu điều kiện cần viết hay hành động cần làm ("kiểm tra nếu n có ước số … thì in `NO` rồi dừng" ở cấu hình C đã biến mất); các phản hồi chỉ ra trường hợp biên `n <= 1` hoặc việc kiểm tra chưa duyệt hết ước số rồi hỏi lại người học. Lần báo 1/5 của heuristic ở D là mô hình trích lại `range(2, n)` của chính người học, tức heuristic dương tính giả. **Giới hạn:** 5 mẫu mỗi cấu hình, chênh lệch 2/5 so với 1/5 và 1/5 so với 0/5 không có ý nghĩa thống kê; một số phản hồi (ví dụ chỉ ra "cần xử lý `n <= 1` để in `NO`") vẫn gần với cách sửa; chưa có điểm sư phạm do người chấm; và Mức 2 chặt hơn có thể khiến người học thấy chưa đủ giúp, điều này chỉ pilot mới trả lời (phiếu F1: hỏi riêng về việc "gợi ý có đủ để tự sửa không").

Bài học rút ra cho khóa luận: "không lộ lời giải" là điều kiện cần, chưa phải là "phản hồi tốt"; và phép đo tự động không thay được việc đọc phản hồi.

---

### 4.5.7. Đo riêng chất lượng ba mức gợi ý trước và sau cải tiến (v5.10)

**Mục đích.** Các mục trên chỉ cho thấy chất lượng gợi ý ở mức tổng quát (5 ca nhóm H). Mục này đo riêng từng mức, trước và sau khi đổi cách dựng bằng chứng và lời nhắc, để trả lời: gợi ý có bám sát mã và kết quả chấm hơn không, các mức có tăng tiến, và ranh giới giữa các mức có được giữ không.

**Phương pháp.** Bộ 15 kịch bản phát triển, 7 kịch bản giữ riêng (viết trước khi sửa, không dùng để chỉnh luật hay lời nhắc) và 9 kịch bản tấn công trên năm bài mẫu; mỗi kịch bản được hỏi lần lượt Mức 1, 2, 3 qua đúng đường `POST /api/submit` (`action_type='ask_ai'`) trên cơ sở dữ liệu tạm. Kiểm tra tất định (`hint_quality_checks.py`, có test riêng) gồm: độ dài theo mức, không lộ biểu thức lời giải, Mức 1 không trích dòng code và không nêu bằng chứng test, Mức 2 trích đúng một dòng có thật và nêu đầu vào/kỳ vọng/thực tế, Mức 3 có dàn ý bốn bước khớp bài và khung không đạt hết test khi đem chạy, độ trùng Jaccard 3-gram giữa hai lượt liên tiếp dưới 0,30. Đây là so khớp quy tắc, không phải điểm sư phạm.

**Kết quả (số ca đạt mọi kiểm tra nội dung, trước → sau).**

| Phép đo | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| Gemini thật, tập phát triển (lần chạy dev 1 trước; 1 lần sau) | 9/15 → 9/15 | 8/14 → 14/14 | 5/15 → 12/15 |
| Gemini thật, tập giữ riêng | 5/7 → 4/7 | 3/7 → 4/7 | 2/7 → 5/7 |
| Offline (rule-based), tập phát triển* | 9/15 → 15/15 | 0/14 → 14/14 | 0/15 → 15/15 |
| Offline (rule-based), tập giữ riêng | 6/7 → 6/7 | 0/7 → 3/7 | 0/7 → 7/7 |

*Số đã tinh chỉnh trên chính tập này; số khách quan là tập giữ riêng. Nguồn: `evaluation/hint_levels_v510_*.json`, báo cáo chi tiết kèm nguyên văn ở `docs/HINT_LEVELS_BEFORE_AFTER_V510.md`. Hai lần chạy dev trước cho kết quả khác nhau (Mức 1: 9/15 và 8/15; Mức 2: 8/14 và 9/14; Mức 3: 5/15 và 7/15), cho thấy dao động của mô hình; mốc sau chỉ có một lần chạy dev vì hết ngân sách lượt gọi.

**Điều đo được.** Mức 2 và Mức 3 cải thiện rõ ở cả hai tập: bằng chứng thực thi đầy đủ (giữ riêng 5/7 → 7/7), tăng tiến so với lượt trước (Mức 2 5/7 → 7/7; Mức 3 4/7 → 7/7), dàn ý theo bài thay vì khuôn chung. Trên tập tấn công (27 phản hồi Gemini), không phản hồi nào lộ biểu thức lời giải hay chương trình hoàn chỉnh.

**Điều không cải thiện hoặc xấu đi.** Mức 1 không tăng ở Gemini thật trên cả hai tập: mô hình vẫn viết dài hơn khoảng đặt ra ở 2/7 ca giữ riêng và 1 ca nêu giá trị test. Độ chính xác của "dòng trích đúng chỗ lỗi" trên tập giữ riêng vẫn 4/7: ở hai ca giai thừa (H01, H06) bản trước chọn đúng dòng còn bản sau chọn sai vì mô hình tin theo "dòng đáng xem" do luật tất định đề xuất. Kiểm tra từ khóa không bắt được việc câu hỏi hay bước kế tiếp vẫn gợi cách sửa; việc này chỉ thấy khi đọc tay (D03 Mức 1, D12 Mức 2). Chi phí thêm của bước vết chạy nhỏ: khoảng 0,8 giây ở trung vị theo phép đo từng lượt, còn phép đo tải 1–20 luồng không phân biệt được với nhiễu.

**Giới hạn.** Cỡ mẫu nhỏ và tự soạn, một mô hình, một thời điểm, bộ đo được tinh chỉnh trong quá trình làm (đã áp dụng đồng nhất cho trước và sau), điểm sư phạm đề xuất do bên có xung đột lợi ích chấm và chưa được tác giả chốt. Kết quả không cho phép kết luận về hiệu quả học tập; điều đó cần pilot người học.

## 4.6. Hiệu năng của đường ống chấm bài

Nguồn: `evaluation/load_benchmark_results.json`, sinh bởi `py evaluate_load_benchmark.py --levels 1,5,10,20 --per-level 20` ngày 13/11/2026. Backend chạy riêng trên cơ sở dữ liệu tạm, tắt LLM; client và server cùng một máy (16 luồng CPU); một tài khoản mẫu dùng cho mọi luồng.

Ba kịch bản ứng với ba hành động trong IDE: `run-test` (Chạy thử), `ask_ai` (Hỏi Gia sư AI, phản hồi bằng bộ luật offline), `submit` (Nộp bài đạt).

| Kịch bản | Số yêu cầu đồng thời | Số yêu cầu | Trung vị (ms) | P95 (ms) | Lớn nhất (ms) | Thông lượng (yêu cầu/giây) | Lỗi |
|---|---:|---:|---:|---:|---:|---:|---:|
| run-test | 1 | 20 | 1.119 | 1.146 | 1.181 | 0,89 | 0 |
| run-test | 5 | 20 | 1.374 | 1.398 | 1.399 | 3,64 | 0 |
| run-test | 10 | 20 | 1.791 | 1.859 | 1.860 | 5,49 | 0 |
| run-test | 20 | 40 | 3.043 | 3.486 | 3.603 | 6,23 | 0 |
| ask_ai | 1 | 20 | 2.029 | 2.072 | 2.154 | 0,49 | 0 |
| ask_ai | 5 | 20 | 2.479 | 2.540 | 2.552 | 2,01 | 0 |
| ask_ai | 10 | 20 | 3.307 | 3.385 | 3.386 | 3,0 | 0 |
| ask_ai | 20 | 40 | 5.262 | 6.393 | 6.460 | 3,54 | 0 |
| submit | 1 | 20 | 2.070 | 2.120 | 2.131 | 0,48 | 0 |
| submit | 5 | 20 | 2.404 | 2.479 | 2.480 | 2,06 | 0 |
| submit | 10 | 20 | 3.308 | 3.369 | 3.369 | 3,0 | 0 |
| submit | 20 | 40 | 5.356 | 6.212 | 6.398 | 3,49 | 0 |

Nhận xét:

- **Không có yêu cầu lỗi** ở mọi mức đã đo (0/300).
- **Chi phí nền khi không tải** là khoảng 1,1 giây cho `Chạy thử` và khoảng 2,1 giây cho `Hỏi Gia sư AI`/`Nộp bài`. Phần lớn thời gian này đến từ thiết kế: mỗi lời gọi công cụ mở một tiến trình `mcp_server` mới và bắt tay lại giao thức; `Nộp bài` gọi nhiều công cụ hơn `Chạy thử`.
- **Thông lượng bão hòa** quanh 6 yêu cầu/giây với `Chạy thử` và 3,5 yêu cầu/giây với `Nộp bài`. Ở 20 yêu cầu đồng thời, P95 là khoảng 3,5 giây và 6,2–6,4 giây.
- **Ý nghĩa thực tế:** với một lớp thực hành vài chục sinh viên, hiếm khi có 20 người bấm nộp trong cùng một giây; khi điều đó xảy ra, người chờ lâu nhất mất khoảng 6,5 giây cho phần chấm. Khi dùng mô hình thật, thời gian chờ còn cộng thêm độ trễ của mô hình (mục 4.5.2), và đó mới là phần chi phối.

**Giới hạn của phép đo:** một máy cá nhân, client chung máy với server nên tranh CPU với chính hệ thống đang đo; không đo trên 20 yêu cầu đồng thời; một tài khoản cho mọi luồng nên chưa phản ánh tranh chấp ghi giữa nhiều người học; không có độ trễ mạng và không có LLM thật. Số liệu mô tả chi phí của đường ống chấm trên máy này, không phải năng lực phục vụ khi triển khai.

---

## 4.7. So sánh với các hệ thống liên quan

So sánh theo tính năng công bố, không phải so sánh chất lượng. **[SV kiểm tra lại từng ô với tài liệu gốc trước khi đưa vào khóa luận.]**

| Tiêu chí | Hệ thống chấm bài tự động (kiểu Online Judge) | Trợ lý AI đa dụng | PyTutor |
|---|---|---|---|
| Mục đích | Chấm đúng/sai, tổ chức thi | Trả lời mọi câu hỏi | Hỗ trợ người học tự làm được bài |
| Phản hồi khi sai | Kết quả kiểm thử | Thường đưa luôn lời giải | Gợi ý ba mức, có bằng chứng từ kiểm thử |
| Kiểm soát lộ lời giải | Không áp dụng | Phụ thuộc người hỏi | Bộ lọc đầu ra, khóa phạm vi trò chuyện, che logic Mức 3 |
| Thích ứng theo lịch sử | Không | Trong phạm vi một hội thoại | Chiến lược theo kiểm thử, lịch sử và hồ sơ |
| Nguồn tri thức | Không áp dụng | Không nêu nguồn | Nêu nguồn hoặc nói rõ không có nguồn |
| Thông tin cho giảng viên | Bảng điểm | Không | Nhóm quá trình học, số liệu tổng hợp |
| Quy mô đã kiểm chứng | Lớn (hàng nghìn người dùng) | Rất lớn | Nhỏ, một máy (mục 4.6) |

PyTutor không cạnh tranh với hệ thống chấm bài về quy mô hay tổ chức thi; đề tài tập trung vào phần các hệ thống đó để ngỏ: phản hồi giúp người học tự sửa.

---

## 4.8. Đánh giá với người dùng

**Chưa thực hiện.** Bộ tài liệu chạy thử đã chuẩn bị ở `docs/PILOT_KIT.md` (phiếu đồng ý, kịch bản S1–S8 cho sinh viên, G1–G5 cho giảng viên, phiếu quan sát, phiếu phản hồi).

**[SV bổ sung sau khi chạy thử:]**

- Số người tham gia, vai trò, cách tuyển.
- Bảng quan sát theo nhiệm vụ: hoàn thành / cần trợ giúp / không hoàn thành.
- Phản hồi định tính tiêu biểu (trích nguyên văn, ẩn danh).
- Các vấn đề phát hiện và cách đã xử lý.

Với cỡ mẫu vài người đến vài chục người và không có nhóm đối chứng, phần này chỉ nên trình bày **quan sát mô tả về tính dùng được**, không kết luận về tiến bộ học tập.

---

## 4.9. Hạn chế

1. **Chưa có bằng chứng từ người học thật.** Mọi số liệu hiện có đến từ kiểm thử, corpus tự soạn và dữ liệu giả lập.
2. **Bộ lọc chống lộ lời giải còn lọt** trên tập giữ riêng (4/14), và gần như không chặn được câu chèn lệnh diễn đạt mới (1/10).
3. **Độ trễ của mô hình thật cao** (trung vị khoảng 12 giây).
4. **Hiệu năng mới đo ở quy mô nhỏ** trên một máy; mỗi lời gọi công cụ mở một tiến trình mới.
5. **Kho tri thức là tài liệu nội bộ**, chưa phải giáo trình chính thức.
6. **Các ngưỡng** (`data_status`, điểm tự làm, nhóm quá trình học) là quy ước vận hành, chưa hiệu chuẩn.
7. **Nhánh offline** chỉ nêu điều quan sát được, chưa chỉ ra dòng lệnh cụ thể; khung mã Mức 3 offline là khung chung cho mọi bài (chỉ phần "bước kế tiếp" thay đổi theo bài làm).
8. **Chưa triển khai** trên máy chủ dùng chung.
9. **Chưa đạt mức an toàn để triển khai:** mã của người học chạy trong tiến trình con chỉ có giới hạn thời gian, chưa cô lập bộ nhớ, tệp và mạng. Mật khẩu của cơ sở dữ liệu mới được băm (PBKDF2), nhưng cơ sở dữ liệu có từ trước vẫn có thể lưu dạng văn bản thường; khóa ký JWT mặc định chỉ bị cảnh báo. Chấp nhận được cho bản mẫu với dữ liệu giả lập, không chấp nhận được khi vận hành.

10. **Mô hình người học là heuristic thứ bậc** (6 KC, 4 trạng thái, ngưỡng quy ước), không phải BKT/IRT; chưa hiệu chuẩn vì chưa có dữ liệu người học thật và chỉ có khoảng 5 bài mẫu; chưa kiểm chứng việc "thích ứng" có giúp học tốt hơn.

## 4.10. Hướng phát triển

1. Chạy thử với người học thật theo `docs/PILOT_KIT.md`, sau đó thiết kế nghiên cứu có đối chứng nếu có điều kiện.
2. Soạn tập giữ riêng mới cho bộ lọc; với bước che Mức 3, đo thêm trên phản hồi thật của mô hình và cân nhắc dùng phân tích cú pháp thay cho biểu thức chính quy.
3. Giữ kết nối công cụ dùng chung thay vì mở tiến trình mới cho mỗi lời gọi.
4. Phản hồi dạng luồng (streaming) để giảm thời gian chờ cảm nhận.
5. Nạp giáo trình chính thức khi được cấp quyền.
6. Khi có đủ dữ liệu người học thật, hiệu chuẩn ngưỡng và thử mô hình truy vết kiến thức (BKT hoặc tương đương) để so với mô hình heuristic hiện tại.
