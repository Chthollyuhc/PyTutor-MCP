# Plan v5.8 — "Hành trình học" (sinh viên) và "Tình hình lớp" 3 tầng (giảng viên)

## Context
Giảng viên hướng dẫn nhận xét: nhật ký học tập của sinh viên và biểu đồ của giảng viên chi tiết nhưng **quá nhiều số, máy móc**. Người xem không biết khối nào hữu dụng. Thầy cần một thứ trực quan, khiến cả GV và SV **muốn mở xem** và **có tác dụng**.

Hiện trạng (đã đọc mã ngày 20/11/2026):
- `frontend/src/components/StudentProfileModal.jsx` có khoảng 10 khối ngang nhau: 4 ô số (mức tự làm /100, đạt ngay lần đầu, số lần nộp TB, mức gợi ý TB), thanh kết quả, 2 thẻ nhận xét, khó khăn lặp lại, bước luyện tập, 6 thẻ KC, lịch sử nộp.
- `ClassInsightsPanel` trong `frontend/src/components/InstructorPedagogyPanels.jsx` có khoảng 16 khối: 4 ô số, 3 danh sách tóm tắt, 7 biểu đồ/danh sách, nhóm quá trình vẽ lần 2, cơ cấu lỗi vẽ lần 2, 2 bảng, chú thích.

Vấn đề cần sửa:
1. Sắp theo nguồn dữ liệu, không theo câu hỏi người xem.
2. Không có thứ bậc thị giác.
3. Lặp khối: nhóm quá trình và cơ cấu lỗi mỗi thứ vẽ 2 lần.
4. Một số chỉ số đi ngược sư phạm của chính hệ thống:
   - "Đạt ngay lần đầu" và "số lần nộp TB" ngược với luật sao (nộp nhiều lần không trừ sao).
   - "Mức gợi ý TB" lấy trung bình một thang thứ bậc. Khi chưa có dữ liệu, mã còn hiện mặc định `1.0` kèm nhãn "Độc lập tư duy cao" (`StudentProfileModal.jsx:235`).
   - "Điểm nỗ lực /100" là chỉ số gộp chưa hiệu chuẩn nhưng hiện như điểm chính xác.
5. Phần trăm trên mẫu nhỏ.

Hướng đã chốt (theo bản phác thảo đã trao đổi):
- **Sinh viên:** 3 phần trả lời 3 câu hỏi.
  - Làm gì tiếp: câu tóm tắt và nút.
  - Mình đang ở đâu: bản đồ khái niệm.
  - Mình tiến bộ thế nào: dấu chân từng bài.
- **Giảng viên:** 3 tầng.
  - Việc nên xem: tối đa 5 thẻ, mỗi thẻ có kết luận, bằng chứng k/n và một nút hành động.
  - Ma trận lớp: SV × bài, bấm vào ô để xem dấu chân.
  - Dữ liệu chi tiết: thu gọn, giữ các bảng và biểu đồ cũ.

## Quyết định mặc định (đổi được trước khi bắt đầu Bước 1)
1. **Sinh viên:** bỏ khỏi giao diện 4 ô số, thanh kết quả, nhãn "Nhận xét chung", 2 thẻ điểm mạnh/điểm nghẽn và danh sách khó khăn lặp lại. Nội dung của chúng chuyển vào bản đồ khái niệm và dấu chân. **Backend giữ nguyên các khóa**, vì chương đánh giá và replay vẫn dùng.
2. **Thẻ "Việc nên xem" không có nút "Đã xử lý".** Thẻ tính lại mỗi lần mở, không thêm bảng.
3. **Ma trận giữ đủ 6 nhóm quá trình**, màu theo họ:
   - xanh lá: các kiểu đạt;
   - tím nhạt: đạt nhờ gợi ý;
   - vàng/đỏ: chưa đạt;
   - xám: chỉ chạy thử;
   - viền trống: chưa bắt đầu.
4. **Bảng xếp hạng (`LeaderboardModal`) nằm ngoài phạm vi v5.8.** Ghi vào việc còn mở vì nó mâu thuẫn với nguyên tắc "so với chính mình".
5. **Tên mới "Hành trình học"** thay "Nhật ký học tập"/"Hồ sơ học tập", cho cả nút ở `Header.jsx` và tiêu đề modal.

## Nguyên tắc phải giữ (kiểm lại ở mỗi bước)
**Bất biến kỹ thuật**
- v5.8 **chỉ đọc và trình bày**:
  - không thu thập dữ liệu mới;
  - không `ALTER TABLE`, không bảng mới;
  - không đổi sao, `compute_student_model`, `derive_learner_model`, `classify_learning_process` (luật và ngưỡng), `select_hint_strategy` hay chỉ số chính thức.
  - Replay phải ra số liệu y nguyên.
- API chỉ được **thêm**: endpoint mới hoặc khóa mới. `StudentProfileResponse` và khóa cũ của `/insights` không đổi (PRODUCT.md).
- Luật 1: `backend/` không import `mcp_server/`.
  - Mô hình người học của SV vẫn lấy qua MCP như `/api/student/profile`, có fallback `compute_student_model` như hiện tại.
  - Chuỗi sự kiện là truy vấn phân tích đọc trực tiếp SQLite, giống tiền lệ `get_class_insights`.
  - Mọi kết nối có `timeout=20.0` + WAL.
- RBAC kiểm tra server-side cho mọi endpoint mới (luật 6).
- Không LLM trong luồng mới. Câu chữ sinh tất định từ mẫu câu, giống `class_overview.py`.

**Nguyên tắc hiển thị (mới, áp cho mọi khối)**
- Mỗi khối trên màn chính phải trả lời **một câu hỏi** người xem thật sự hỏi và dẫn tới **một hành động**. Khối không đạt thì chuyển vào "Dữ liệu chi tiết" hoặc bỏ.
- **Tiêu đề là kết luận.** Ví dụ "2 SV mắc kẹt ở Số nguyên tố", không viết "Biểu đồ nhóm quá trình".
- **Mẫu nhỏ thì nói thật:**
  - luôn hiện `k/n`;
  - chỉ thêm `%` khi `n ≥ 10` (quy ước, ghi trong tài liệu);
  - dùng biểu đồ chấm (icon array) cho tỉ lệ;
  - độ bất định vẽ bằng hình (viền nét đứt, ô nhạt), không viết thành banner dài.
- **Sinh viên:**
  - chỉ so với chính mình: không xếp hạng, không so với bạn;
  - không gắn nhãn tiêu cực lên SV (không hiện "Mắc kẹt" cho SV), chỉ mô tả kèm bước tiếp theo;
  - gợi ý không bao giờ tự đẩy mức gợi ý lên (luật 4);
  - Anti-Spoil: không hiện đầu ra mong đợi hay lời giải, chỉ dùng thông tin test mà IDE vốn đã cho SV thấy.
- **Giảng viên:**
  - sinh viên xếp A→Z, không xếp hạng;
  - mỗi kết luận kèm bằng chứng và ngưỡng "quy ước vận hành, chưa hiệu chuẩn" (luật 13, 14, 16).
- Màu đi kèm hình hoặc chữ (người mù màu vẫn đọc được). Có `aria-label` tóm tắt và điều khiển được bằng bàn phím.
- UI theo `DESIGN.md`: NEU green, flat, sáng/tối, 375px, không cuộn ngang trang. Không thêm thư viện biểu đồ, tái dùng `components/charts/ClassCharts.jsx`.

**Quy trình**
- Test và QA trên DB tạm, mỗi module một DB (`.claude/run_isolated.ps1`), đặt `PYTUTOR_DISABLE_LLM=1`, không đụng `pytutor.db`.
- Tắt backend dev `:8000` trước khi sửa `backend/`.
- **Không `git commit`.**
- Không thêm trích dẫn học thuật vào khóa luận khi người dùng chưa đọc nguồn. Tài liệu chỉ nêu tên phương pháp.

## Bước 0 — Mốc "trước" và dữ liệu mẫu
- Viết `seed/seed_demo_class_v58.py`, script dev tạo lớp mẫu tổng hợp: 8–10 SV, 5 bài theo lộ trình, đủ 6 nhóm quá trình, có test sai tập trung, có sai định dạng, có lượt cách đây 8–14 ngày để so sánh tuần.
  - Ghi qua các hàm DB sẵn có (`save_submission`, `save_practice_run`), sau đó lùi mốc thời gian **chỉ trên DB tạm**.
  - **Từ chối chạy** nếu `PYTUTOR_DB_PATH` chưa đặt hoặc trỏ tới `pytutor.db`.
- Chụp màn cũ (modal SV và Góc nhìn sư phạm GV) trên cặp `qa-backend`/`qa-frontend` với dữ liệu mẫu. Lưu vào `docs/ui_audit/v58_before/` để làm mốc so sánh trong pilot.

## Bước 1 — Backend: chuỗi sự kiện (dấu chân) và câu tóm tắt cho SV
**1a. Hàm thuần trong `pytutor_shared/learner_model.py`:**
- `build_journey_points(events)`
  - Đầu vào: sự kiện đã sắp xếp, cùng dạng `classify_learning_process`, có thêm `timestamp`, `total_tests`, `error_class`, `failed_tests`, `format_only`, `submission_id`.
  - Đầu ra mỗi điểm: `kind`, `passed`, `total`, `hint_level`, `all_passed`, `is_new_best` (số test đạt vượt mức tốt nhất trước đó), `format_only`.
  - Đầu ra tóm tắt: `group` (gọi chính `classify_learning_process`, không viết luật mới), số lượt từng loại, `best`, `first_pass_index`.
- Hằng `PROCESS_EVENT_ORDER = {"run": 0, "ask": 1, "submit": 2}`. Tiêu chí sắp xếp giống hệt `get_class_insights`: (timestamp, loại, id).

**1b. Đọc DB trong `backend/database.py`:**
- `get_exercise_journey(username, exercise_id, days=None, limit=60, include_code=False)`
  - Đọc `submissions` (`submit` + `ask_ai`), LEFT JOIN `attempt_features` và `practice_runs`.
  - `include_code=True` chỉ dùng cho chính SV, để nạp lại code ở các điểm nộp. Phía GV không trả code (tối thiểu hóa; GV đã có màn giám sát bài nộp).
  - Lượt trước v5.4 không có chạy thử: trả cờ `runs_recorded_from` để giao diện chú thích.
- `get_student_journey_overview(username, class_id=None)`
  - Tối đa 5 bài hoạt động gần nhất, mỗi bài kèm điểm rút gọn.
  - `week = {"this": n, "prev": n}`: số bài **nộp đạt lần đầu** trong 7 ngày gần nhất và 7 ngày trước đó.

**1c. Module thuần mới `backend/student_journey.py`** (tất định, không DB, không LLM):
- `build_student_headline(learner_model, next_practice, week, recent)` trả `headline_vi`, `detail_vi`, `cta {exercise_id, title}`, `tone`. Ưu tiên theo thứ tự:
  1. Chưa có dữ liệu: mời làm bài đầu tiên.
  2. Có KC "đang vướng": nêu khái niệm và bài luyện tương ứng.
  3. Có bài đang tiến gần: "đạt a/b test".
  4. Tuần này có bài đạt mới: ghi nhận, rồi nêu bước tiếp.
  5. Còn lại: dùng `next_practice.reason`.
- `describe_exercise_journey(points, summary)`: một câu mô tả dấu chân bằng giọng nói với SV.
  - Đã đạt: "thử–sửa N lượt rồi đạt; số test đạt tăng từ a lên b".
  - Không tiến trong 5 lượt gần nhất: gợi ý chạy từng bước, xem lại khái niệm, hoặc hỏi Gia sư AI ở mức SV tự chọn.
  - Không dùng chữ "mắc kẹt".

**1d. API (chỉ thêm):**
- `GET /api/student/journey?class_id=&exercise_id=`
  - Quyền: `require_student`; người dùng lấy từ token; có `class_id` thì gọi `ensure_class_access`.
  - Trả `headline`, `week`, `concepts` (từ `learner_model`, gồm `exercise_details` sẵn có), `recent_exercises[]`, `current` (dấu chân đầy đủ của `exercise_id`, kèm code các lượt nộp của chính SV) và `disclaimer`.
- `GET /api/instructor/classes/{class_id}/students/{username}/exercises/{exercise_id}/journey?days=`
  - Quyền: GV sở hữu lớp, SV đã ghi danh, bài thuộc lớp. Sai quyền trả 404 như các endpoint lớp hiện có; SV gọi trả 403.
  - Dùng cùng cửa sổ `days` với ma trận để nhóm khớp nhau. Không trả code.

**Test 1** (`test_visual_views_v58.py`, lớp thuần không cần DB):
- `build_journey_points`: thứ tự sự kiện, `is_new_best`, nhóm trùng `classify_learning_process`.
- Câu tóm tắt: mỗi nhánh ưu tiên bật đúng; không chứa "mắc kẹt"/"xếp hạng"; không chứa đầu ra mong đợi.
- Mẫu rỗng không lỗi.

## Bước 2 — Backend: ma trận và thẻ "Việc nên xem"
**2a. Ma trận.** Thêm khóa `matrix` vào kết quả `get_class_insights`, dựng từ `process_by_pair` và danh sách bài sẵn có, không tính lại nhóm.
- `exercises`: các bài theo `order_idx`, kèm số SV đạt, đã thử và đã ghi danh.
- `rows`: **mọi** SV ghi danh xếp A→Z (SV chưa hoạt động có ô rỗng), mỗi hàng có `cells {exercise_id: group|null}`.

**2b. Thẻ hành động trong `backend/class_overview.py`.**
- Thêm `exercise_ids` vào `evidence` của các mục `attention`. Chỉ thêm khóa, câu chữ cũ giữ nguyên.
- Hàm thuần `build_action_cards(overview, insights, limit=5)`:
  - Gộp "mắc kẹt" theo bài thành một thẻ, ví dụ "k SV mắc kẹt ở X", kèm danh sách SV.
  - Thứ tự ưu tiên là hằng `ACTION_PRIORITY`: `stuck` → `failing_test` → `format_mismatch` → `bottleneck` → `kc_struggling` → `hint_dependence` → `practice_only`.
  - Mỗi thẻ có: `code`, `title_vi` (kết luận), `evidence {k, n, unit_vi}`, `students[]`, `exercise_id`/`kc`, `action {target, label_vi}`.
  - Kèm `positives` (tối đa 2) và `more_count`.
  - Mẫu số được định nghĩa rõ: thẻ mắc kẹt dùng n = số SV đã thử bài; thẻ test sai dùng n = số lượt chưa đạt của bài.
- Endpoint `/insights` thêm khóa `action_cards` cạnh `overview`.

**Test 2** (cùng module):
- Thuần: giới hạn 5 thẻ, thứ tự ưu tiên, gộp theo bài, k/n khớp `evidence`; `limited`/`no_data` không sinh thẻ cấp lớp.
- Tích hợp trên DB tạm:
  - ma trận có đủ SV ghi danh, A→Z, đúng thứ tự bài;
  - **nhóm ở ô ma trận = nhóm trong `journey` = `process_by_exercise`** với cùng cặp và cùng cửa sổ;
  - RBAC cả hai endpoint mới: GV khác → 404, SV khác lớp/không ghi danh → 404, SV gọi endpoint GV → 403, SV chỉ thấy dữ liệu của mình (theo mẫu `test_qa_authorization.py`).

## Bước 3 — Giao diện sinh viên "Hành trình học"
Trước khi viết: đọc `DESIGN.md`, tải skill `dataviz`. Component mới đặt ở `frontend/src/components/journey/`.
- `JourneyHeadline`: một câu lớn, một dòng lý do và **một** nút chính ("Làm bài này" → `/student/ide/:id`). Có dòng "Tuần này / tuần trước", chỉ hiện số đếm, không phần trăm.
- `ConceptMap`
  - 6 nút KC thành lộ trình. Trạng thái mã hóa bằng cả tô màu lẫn hình: tô đầy = khá vững, nửa = đang hình thành, viền cam = đang vướng, nét đứt = chưa có bằng chứng. Mỗi nút có nhãn chữ.
  - Bấm vào nút mở popover "Vì sao hệ thống nghĩ vậy": `explanation` cộng `exercise_details`, kèm nút tới bài để luyện.
  - Ở 375px chuyển thành danh sách dọc.
- `AttemptStrip`
  - SVG, trục dọc là số test đạt trên tổng. Ký hiệu: chạy thử = chấm nhỏ, hỏi AI = ô vuông kèm mức, nộp = vòng (đạt thì tô đầy).
  - Điểm `is_new_best` được nhấn. Có câu mô tả từ `describe_exercise_journey`.
  - Điểm nộp có nút "Nạp lại code này".
  - Quá 20 điểm thì gộp các đoạn chạy thử liên tiếp. Có `aria-label` tóm tắt và bảng thay thế ẩn cho trình đọc màn hình.
- `StudentProfileModal.jsx` viết lại thành "Hành trình học", gọi `/api/student/journey`.
  - Thứ tự hiển thị: câu tóm tắt → bản đồ khái niệm → dấu chân (bài hiện tại mở sẵn; các bài gần đây hiện dải thu nhỏ, bấm để mở).
  - Giữ trạng thái đang tải, lỗi và thử lại. Giữ `onLoadCode`.
  - 3 nơi mở modal giữ nguyên: `StudentIDE`, `StudentPortalPage`, `StudentClassDetailPage`.
- `frontend/src/utils/share.js` có `formatShare(k, n)` (`k/n`, thêm `%` khi `n ≥ 10`) và `formatCount`. Test bằng `node --test`, thêm script `test:ui-utils` vào `package.json`.

## Bước 4 — Giao diện giảng viên "Tình hình lớp"
`ClassInsightsPanel` được sắp lại; mọi phần tái dùng hàm và biểu đồ có sẵn.
- **Dòng ngữ cảnh:** một câu ("7 ngày qua · 8/10 SV có hoạt động · 3 việc nên xem") cùng `DataStatusChip`, `DaysSelect` và nút tải lại. Thay cho 4 `SampleCell`.
- **Tầng 1 — `ActionCards`:**
  - Tối đa 5 thẻ; mỗi thẻ có tiêu đề kết luận, biểu đồ chấm hoặc `k/n`, và một nút hành động theo `target`:
    - Xem quá trình: mở ngăn dấu chân hoặc hồ sơ SV;
    - Sửa đề: `/instructor/exercises/:id/edit`;
    - Mở tài liệu lớp;
    - Mở lộ trình.
  - Thêm một dòng "Điểm sáng" và nút "Xem thêm k".
  - Khi không có thẻ: hiện câu "Không có việc cần xử lý ngay theo quy ước hiện tại".
- **Tầng 2 — `ClassMatrix`:**
  - Lưới HTML: cột đầu (tên SV) và hàng tiêu đề cố định. Nếu nhiều bài, cuộn ngang **bên trong khung**, trang không cuộn ngang.
  - Mỗi ô là một `button` có `aria-label` ("An · Bài 3: Đang tiến triển"). Ô mắc kẹt có thêm viền đậm để không chỉ dựa vào màu.
  - Có chú giải 7 trạng thái.
  - Bấm vào ô mở `JourneyDrawer`: `AttemptStrip` gọi endpoint GV, kèm nút sang `StudentLearnerModelDetail`.
  - Bấm vào tiêu đề cột mở `ExerciseDrawer`: test hay sai, loại lỗi (gồm "chỉ sai định dạng"), thời gian tới khi đạt (trung vị, n), tái dùng `StackedBarRows`/`HBar`.
- **Theo khái niệm** (dưới ma trận): 6 dòng, mỗi dòng một dãy chấm theo số SV ở từng trạng thái. Đây là chỗ nối mô hình người học với màn GV.
- **Tầng 3 — "Dữ liệu chi tiết"** (`<details>`, mặc định đóng): chuyển vào đây các biểu đồ KC, loại lỗi, xu hướng ngày, bảng bài gây nghẽn, bảng SV, chú giải ngưỡng và "Giới hạn khi diễn giải". **Bỏ phần vẽ lặp**: `ProcessBar` tổng và theo bài, và `ErrorMixBar` đã có trong ngăn bài.
- `ClassesAttentionList` ở danh sách lớp giữ nguyên.

## Bước 5 — Kiểm chứng
- `py -m compileall -q backend mcp_server pytutor_shared`.
- Chạy mỗi module một DB tạm:
  - `test_visual_views_v58` (mới), `test_class_overview_v57`, `test_data_capture_v57`, `test_learner_model`;
  - `test_thesis_upgrade` (61/61), `test_phase16_ai_upgrade`, `test_phase17_adaptive_analytics`, `test_qa_authorization`, `test_pedagogy_v55`;
  - script `py -m mcp_server.test_mcp_server`, `py -m backend.test_backend_e2e`.
- Hồi quy phải **giữ nguyên** số liệu: `py evaluate_learner_model_policy.py` (120/120 mức gợi ý) và `py evaluate_phase17_adaptive.py` (6/6). Guard và RAG không đổi nên không bắt buộc chạy lại.
- Frontend: `npm.cmd run test:theme`, `npm.cmd run test:ui-utils`, `npm.cmd run build`.
- Kiểm tra trình duyệt trên cặp `qa-backend`/`qa-frontend` với dữ liệu từ seed Bước 0:
  - SV: mở từ IDE, cổng SV và trang lớp; bấm nút khái niệm; nạp lại code; trường hợp DB mới tinh không có dữ liệu.
  - GV `gv_tran`: thẻ, ma trận, hai ngăn, chi tiết thu gọn.
  - Chung: sáng/tối, 375px, bàn phím, console sạch, lỗi mạng.
  - Đo thời gian trả `/insights` và `/journey`. Đóng cả hai server sau khi xong.
- Tự chạy thử bộ câu hỏi pilot (Bước 6) trên màn mới và ảnh mốc "trước", để kiểm tra mỗi câu trả lời được trong vài giây. Đây là **tự kiểm**, không phải kết quả pilot.
- Review bắt buộc: RBAC của 2 endpoint mới, Anti-Spoil trong câu chữ cho SV, quyền riêng tư (GV không nhận code qua dấu chân).

## Bước 6 — Tài liệu
- Mới `docs/VISUAL_DESIGN_RATIONALE.md` (phục vụ Chương 3 và phản biện):
  - 5 vấn đề của màn cũ;
  - bảng "phương pháp → ngành → áp vào PyTutor";
  - bảng "khối cũ → giữ / chuyển / bỏ và lý do", gồm lý do bỏ 4 ô số;
  - quy ước mẫu nhỏ, bảng mã hóa màu và hình, giới hạn.
  - Chỉ nêu tên phương pháp. Danh sách nguồn ghi "đọc trước khi trích".
- `docs/PILOT_KIT.md`: thêm phần so sánh theo nhiệm vụ.
  - GV có 4 câu: ai cần hỗ trợ, bài nào có vấn đề ở đề, khái niệm nào lớp vướng, điều gì đang ổn.
  - SV có 3 câu: khái niệm nào nên luyện, bài tiếp theo, mình đã tiến bộ ra sao ở bài X.
  - Ghi thời gian và đúng/sai trên ảnh màn cũ so với màn mới. Chỉ là quan sát mô tả (luật 16).
- `docs/LEARNER_DATA_DICTIONARY.md`: thêm cột "hiển thị ở đâu (v5.8)".
- `AI_HANDOFF_CONTEXT.md` §20, `PLAN.md` và `CLAUDE.md` §9: lệnh test mới, seed v5.8, ghi chú bảng xếp hạng là việc còn mở.

## Ngoài phạm vi
Bảng xếp hạng; thay đổi trạng thái KC theo thời gian (cần lưu ảnh chụp mô hình, tức là đổi schema); chủ đề câu hỏi chat; tóm tắt bằng LLM; nút "Đã xử lý"; thay đổi màn giám sát bài nộp.

## Rủi ro và cách xử lý
- **Nhóm ở ô ma trận lệch với dấu chân:** dùng chung cửa sổ `days` và tiêu chí sắp xếp; có test khớp ba nguồn (Bước 2).
- **Lớp đông (60+ SV):** lưới cuộn dọc trong khung, giữ tiêu đề cố định; đo hiệu năng ở Bước 5.
- **Câu tóm tắt bị hiểu như điểm số:** dùng mẫu câu mô tả, có danh sách từ cấm trong test; review câu chữ ở Bước 5.
- **Dữ liệu cũ thiếu chạy thử (trước v5.4) hoặc thiếu đặc trưng (trước v5.7):** chú thích ngay trên dải dấu chân; không suy diễn.

## File chính
- `pytutor_shared/learner_model.py`, `backend/database.py`, `backend/student_journey.py` (mới), `backend/class_overview.py`, `backend/main.py`.
- `frontend/src/components/StudentProfileModal.jsx`, `frontend/src/components/journey/*` (mới), `frontend/src/components/InstructorPedagogyPanels.jsx`, `frontend/src/components/Header.jsx`, `frontend/src/utils/share.js` (mới), `frontend/src/services/api.js`, `frontend/package.json`.
- `seed/seed_demo_class_v58.py` (mới), `test_visual_views_v58.py` (mới), các tài liệu ở Bước 6.
