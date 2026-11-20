# PLAN v5.10 — Chạy đêm nâng chất lượng 3 mức gợi ý

> Nhật ký tự tiếp quản. Đề bài gốc: `plans/OVERNIGHT_V510_PROMPT.md`. Nhánh: `feat/overnight-deep-upgrade`; tag mốc: `pre-overnight-v510`.
> Lệnh chạy bộ hồi quy đầy đủ: `.\.claude\run_suite_v510.ps1 -OutDir <thư mục>` (mỗi module một DB tạm, LLM tắt).

## Trạng thái nhanh (cập nhật khi xong từng đơn vị việc)
- [x] Pha 0: usage + Cron `9f9c787b`, nhánh + commit snapshot `a3328a3` + tag, mốc test `evaluation/v510_baseline/` (toàn xanh).
- [ ] Pha 1: bộ đo (`evaluate_hint_levels.py`, `hint_quality_checks.py`, kịch bản dev 15 + giữ riêng 7) xong; mốc offline xong; mốc thật đang chạy; còn: phần Điểm yếu bên dưới (đã viết), commit.
- [ ] Pha 2: golden prompt → tách khối → hint_evidence + offline 3 mức → prompt (lịch sử, bằng chứng, từng mức) → vết chạy → enforce_level3 quoted_context.
- [ ] Pha 3 · [ ] Pha 4 · [ ] Pha 5 · [ ] Pha 6

## Số lượt Gemini đã dùng: xem `evaluation/v510_gemini_calls.json` (trần 300; script `evaluate_hint_levels.py --real` tự cộng dồn và từ chối vượt trần)

## Cần người dùng quyết định
1. **Khung Mức 3 có giữ nguyên văn các dòng của người học không?** Đề bài gốc cho phép chỉnh `enforce_level3_skeleton` theo kiểu `quoted_context` (dòng có nguyên văn trong code người học thì không che). Đêm nay KHÔNG làm: bản che toàn bộ dòng logic là bản duy nhất đã đo (lọt 0/24 dev, 0/16 giữ riêng) và còn báo cho người học biết chỗ nào cần tự viết lại; giữ nguyên văn dòng của người học có thể giữ cả dòng sai mà không cảnh báo. Đề xuất: giữ như hiện tại; nếu muốn khung "đọc như bài của mình", làm thành tùy chọn đo riêng.
2. **Bộ lọc ranh giới mức ở đầu ra (đề xuất, chưa làm):** hiện ranh giới Mức 1/2 chủ yếu nhờ prompt và rào chắn thông tin; bộ lọc tất định cho Mức 1 (có trích dòng code / có giá trị kiểm thử không) và Mức 2 (cụm chỉ cách sửa) sẽ chặn cứng hơn nhưng làm thay gợi ý của mô hình bằng bản rule-based thường xuyên hơn; cần quyết định đánh đổi giữa độ phong phú và ranh giới cứng.
3. **Mô tả test trong Mức 1 bị bỏ** (ví dụ "Số lẻ"): Mức 1 chỉ nêu số đạt/tổng và dạng vấn đề. Nếu muốn giữ mô tả test dạng khái niệm cho Mức 1, cần quy ước test nào có mô tả "an toàn" (không chứa giá trị cụ thể).

## Điểm yếu giả định (phản biện) và cách kiểm
Mỗi mục là GIẢ THUYẾT, đã đọc mã nhưng chưa kết luận; cột cuối là chỉ số trong bộ đo.

| # | Giả thuyết | Bằng chứng ban đầu trong mã | Cách kiểm |
|---|---|---|---|
| W1 | Dàn ý Mức 3 là khuôn chung cho mọi bài | `llm_service.py` Mức 3: 4 bước "nhập → khởi tạo → lặp → in" cố định; nhánh offline cũng cố định | `m3_dan_y_4_buoc_khop_bai` |
| W2 | Prompt không có nội dung gợi ý trước nên chỉ dẫn "không lặp" vô nghĩa | `history_section` chỉ ghi mức gợi ý + kết quả, bỏ `tutor_hint` (dữ liệu có sẵn ở `get_attempt_history`) | `khong_lap_voi_luot_truoc` (Jaccard 3-gram), D03 (hỏi Mức 1 hai lần), D09 |
| W3 | Khi guard chặn (H3) bản thay thế kém hơn bản bị chặn | `generate_tutor_hint` trả `generate_rule_based_fallback` nguyên khối | so sánh `m2_*` của nhánh offline với nhánh thật |
| W4 | Mức 1 trôi về hai phía: hỏi suông hoặc khoanh vùng lỗi | prompt Mức 1 yêu cầu "câu hỏi"; offline Mức 1 liệt kê câu hỏi chung | `m1_khong_chi_la_cau_hoi_suong`, `m1_neu_khai_niem`, `m1_khong_trich_dong_code`, `m1_khong_bang_chung_test_cu_the` |
| W5 | Bằng chứng luôn lấy test fail đầu tiên; lỗi cú pháp và TIMEOUT không có cách nói riêng ở nhánh thật | `build_scaffolding_prompt` lấy tối đa 3 test lỗi theo thứ tự; offline `_first_failed_test` | `m2_co_bang_chung_thuc_thi`, D02, D06 |
| W6 | Cùng giới hạn 100–200 từ cho cả 3 mức | quy tắc bắt buộc số 3 trong prompt | `do_dai` theo ngưỡng riêng từng mức |
| W7 | Offline Mức 2 không trích dòng code nào; lỗi cú pháp/TIMEOUT trả CÙNG một nội dung ở mọi mức | `generate_rule_based_fallback` các nhánh cú pháp/TIMEOUT bỏ qua `hint_level` | `m2_dung_mot_dong_that`, `tang_tien_so_voi_luot_truoc` |
| W8 | Mã/ comment người học đưa vào prompt không được phân định là dữ liệu không tin cậy | prompt chèn `{code}` trực tiếp trong khối ``` | D11, D12 (chèn lệnh trong comment) |
| W9 | Mô tả trong báo cáo/bản nháp chương có thể lệch mã (tên mức, số ca test, mô tả guard) | chưa so sánh | Pha 5: đọc `bao_cao_final.docx` chỉ-đọc, lập `docs/REPORT_UPDATES_V510.md` |
| W10 | Trích tên/biến có thể bịa (mô hình nêu tên không có trong code/đề) | không có kiểm tra | `ten_co_that` |

## Tiêu chí ĐÃ CHỐT (khóa trước khi đo mốc thật; muốn đổi phải ghi lý do ở Nhật ký và tính lại CẢ trước lẫn sau bằng `--rescore`)
Nguồn mã: `hint_quality_checks.py` (kiểm thử riêng: `test_hint_quality_v510.py`). Kiểm tra = so khớp quy tắc tất định, KHÔNG phải điểm sư phạm.
- **Chung (mọi mức, chưa đạt):** `do_dai` Mức 1 [45,190] từ, Mức 2 [60,230], Mức 3 [110,430]; `khong_nhan_xet_nang_luc`; `khung_muc_tieu_bang_chung_buoc` (từ khóa, heuristic); `dung_mot_buoc_ke_tiep` (đúng một nhãn "Bước kế tiếp"; là yêu cầu ĐỊNH DẠNG, bản trước không được hướng dẫn nhãn này nên số trước có thể thấp vì định dạng); `ten_co_that` (mọi tên trong `backtick` có trong code/đề/test/built-in); `khong_lo_bieu_thuc_loi_giai` (biểu thức lời giải theo `exercise_profiles.core`, bỏ qua nếu đã có sẵn trong code người học); `khong_chuong_trinh_hoan_chinh` (Mức 1–2, qua `check_student_output`); `khong_cum_chi_cach_sua` ("đổi … thành", "thay … bằng", "nên dùng điều kiện"…).
- **Mức 1:** không bằng chứng test cụ thể (nhãn Input/Kỳ vọng/Thực tế hoặc giá trị test trong `backtick`); không trích dòng code của người học (dòng ≥ 8 ký tự, không phải khung mẫu); không khối code; nêu khái niệm mục tiêu (từ trong `concept_terms`); không chỉ là câu hỏi suông (có câu khẳng định nêu khái niệm hoặc phép thử cụ thể).
- **Mức 2:** trích ĐÚNG MỘT dòng có thật của người học; dòng đó thuộc `expected_lines` của kịch bản; có bằng chứng thực thi (FAIL: đầu vào + kỳ vọng + thực tế trong `backtick`; RUNTIME_ERROR: đầu vào + tên lỗi; TIMEOUT: nêu không dừng/quá thời gian; SYNTAX_ERROR: số dòng hoặc thông báo của trình phân tích); không khối code ≥ 3 dòng.
- **Mức 3:** đủ Bước 1–4, ≤ 1 cụm khuôn chung và ≥ 2 thuật ngữ riêng của bài (`terms`); có khung `# TODO`/`...`; khung đem chạy với bộ test KHÔNG đạt hết; khung là Python hợp lệ.
- **Tăng tiến:** `khong_lap_voi_luot_truoc`: Jaccard 3-gram từ giữa hai gợi ý liên tiếp trong cùng kịch bản < 0.30; `tang_tien_so_voi_luot_truoc`: Mức 2 có bằng chứng Mức 1 không có; Mức 3 có khung mã mà Mức 2 không có.
- **Thông tin (không tính đạt/trượt):** có bảng chạy tay (v5.10), có giữ dòng của người học trong khung, số từ.
- Rubric định tính 0–5 cho từng mức (người chấm = trợ lý, ghi "đề xuất", cột "SV chốt" để trống): xem `docs/HINT_LEVELS_BEFORE_AFTER_V510.md` (tạo ở Pha 3).

## Hạn chế đã biết của bộ đo
- 15 kịch bản phát triển + 7 giữ riêng, tự soạn, 5 bài seed, một mô hình; không thay pilot người dùng.
- `m2_dong_dung_cho_loi` phụ thuộc nhãn `expected_lines` do tác giả bộ đo gán; với lỗi có nhiều dòng liên quan, nhãn có thể chưa bao hết.
- Kiểm tra từ khóa (`khung_*`, `m1_neu_khai_niem`) có thể trượt nhầm khi dùng từ đồng nghĩa; báo cáo ghi theo số ca.

## Checklist Pha 2 (ưu tiên; đánh dấu khi xong + commit)
1. [ ] Test vàng prompt (`evaluation/prompt_golden_v510.json`, `test_prompt_golden_v510.py`) trên mã CŨ.
2. [ ] Tách `build_scaffolding_prompt` thành khối (giữ nguyên từng ký tự) → test vàng xanh → commit.
3. [ ] `backend/hint_evidence.py` (chọn test thông tin nhất, dòng cần trích, loại lỗi, bảng chạy tay, dàn ý theo đề).
4. [ ] Offline Mức 1/2/3 viết lại dựa trên hint_evidence; cập nhật test chỉ khi đổi hành vi có chủ đích.
5. [ ] Prompt: lịch sử gợi ý (rút gọn), phân định dữ liệu không tin cậy, chỉ dẫn từng mức, độ dài từng mức.
6. [ ] Vết chạy (`trace_code_execution`) trong cùng phiên MCP, timeout + fallback; đo độ trễ.
7. [ ] `enforce_level3_skeleton` quoted_context + đo lại `evaluate_level3_skeleton.py` hai tập.

## Nhật ký
- 04:13 Bắt đầu. Hạn mức 5 giờ 66% (reset ~05:30 giờ địa phương), tuần 33% (reset ~12:59 giờ địa phương). Job Cron `9f9c787b` (7,27,47 * * * *), tự hết hạn sau 7 ngày.
- 04:13 Cổng 8000/5173/8001/5174: không có tiến trình nào đang nghe (không phải tắt gì).
- 04:13 SHA256 `bao_cao_final.docx` = 3E611B83623D64ABD14633F6DB00397F80D55178DBCAD882C2AA51B30B771C27
- 04:13 SHA256 `pytutor.db` = ACC3701FD1034708D6215D387D709982C2997DC6BF8BB6917EE58B282C85A4CF
- 04:13 `.env` có GEMINI_API_KEY (chỉ kiểm có/không).
- 04:20 Git: nhánh `feat/overnight-deep-upgrade`, commit snapshot `a3328a3` (268 tệp, không khóa/DB; tệp lớn nhất 446 kB), tag `pre-overnight-v510`. Untracked có chủ đích: `scratch`, `.codex`, `.gemini`, `.claude/skills`, `.claude/agents`, `frontend/.impeccable`, `pytutor.db.backup_before_seed`.
- 04:25 Mốc test (`evaluation/v510_baseline/`): compileall OK; mọi module unittest và script đều xanh (test_thesis_upgrade 61, phase16 ×6, phase17 ×5, qa_authorization ×9, level3 ×15, pedagogy_v55 ×19, learner_model ×34, passwords ×7, no_code_hint ×5, data_capture ×8, class_overview ×9, visual_views ×19, plain_language ×23; 8 script phase5–15.4 + MCP 8/8 + backend E2E 6/6 đạt; frontend test:theme 3/3, test:ui-utils 12/12, build 1710 modules). Số đo: guard dev rò rỉ 0/30 (FPR 0), giữ riêng rò rỉ 4/14 (FPR 1/12); RAG hit@3 36/38; che Mức 3 lọt 0/24 (dev), 0/16 (giữ riêng). Không có gì đỏ từ trước.
- 04:30 Bộ đo: 15 kịch bản dev + 7 giữ riêng, mọi kịch bản đã xác minh đúng loại lỗi bằng sandbox (`--verify-scenarios`). Sửa dương tính giả của `khong_cum_chi_cach_sua` ("thay đổi … trở thành") trước khi đo mốc thật; thêm ca kiểm thử; đã `--rescore` mốc offline.
- 04:31 Mốc offline TRƯỚC (`evaluation/hint_levels_v510_before_offline_{dev,holdout}.json`): đạt mọi kiểm tra — dev: Mức 1 8/15, Mức 2 0/14, Mức 3 0/15; giữ riêng (chưa đọc nguyên văn): Mức 1 6/7, Mức 2 0/7, Mức 3 0/7. Trượt chính: Mức 2 không trích dòng code (m2_dung_mot_dong_that 0/13); Mức 3 dàn ý khuôn chung (m3_dan_y_4_buoc_khop_bai 0/14).
- 04:32 Mốc thật TRƯỚC (`evaluation/hint_levels_v510_before_real_{dev_1,dev_2,holdout}.json`): 109 lượt Gemini (mô hình `gemini-3.5-flash-lite`); phản hồi từ Gemini 43/44, 42/44, 20/21 (còn lại là fallback guard/offline). Mức 1 trượt nhiều nhất ở lộ chi tiết test (3/13) và trích dòng code (2/14); Mức 3 dàn ý khuôn chung (7/14 khớp bài) và khung không hợp lệ Python (3/14). Kiểm tra `dung_mot_buoc_ke_tiep` (nhãn) 0/15 ở Mức 1 vì prompt cũ không yêu cầu nhãn: tách thành tổng hợp "nội dung" riêng.
- 04:40 Sửa bộ đo theo lý do ghi rõ (áp dụng cho CẢ trước lẫn sau bằng `--rescore`): (1) bỏ dòng thông báo hệ thống 🔒 khỏi kiểm tra cụm chỉ cách sửa (dương tính giả: "đã thay N biểu thức … bằng `...`"); (2) cụm "thay đổi … trở thành" không còn bị coi là chỉ cách sửa; (3) tên trong `backtick` được phép lấy từ thông báo lỗi của trình thông dịch; (4) dòng "đáng kể" tối thiểu 5 ký tự (trước 8, làm `dem = 1` không được tính), loại `break/pass/else:`…; (5) bằng chứng TIMEOUT của Mức 2 phải có đầu vào cụ thể (trước chỉ cần cụm "quá thời gian", nên Mức 1 cũng "đạt"); (6) độ dài của ca đã đạt dùng khoảng riêng [30,230]; (7) khung mục tiêu chấp nhận "vượt qua"/"x/y kiểm thử". Thêm tổng hợp `all_pass_content_by_level` (bỏ kiểm tra định dạng nhãn).
- 04:52 Pha 2 đã làm: (a) tách khối `build_scaffolding_prompt`, test vàng khớp từng ký tự TRƯỚC khi đổi nội dung (commit ff7a550); (b) `backend/hint_evidence.py` + `backend/hint_rules.py`: nhánh rule-based 3 mức theo bằng chứng (test thông tin nhất, dòng đáng xem từ cú pháp/traceback/vết chạy/AST, khái niệm + phép thử, dàn ý theo đề, khung mã bám mã người học đã che logic, bảng chạy tay, xoay vòng khi hỏi lại, chú thích người học KHÔNG bao giờ được chép lại); (c) `trace_code_execution` trong cùng phiên MCP (`execute_submission_pipeline(with_trace=True)` chỉ cho `ask_ai` và khi không bị khóa EXAM; timeout 6s; lỗi → SKIPPED trong `mcp_trace`, dùng bằng chứng tĩnh); (d) prompt: rào chắn thông tin Mức 1 (không đưa giá trị kiểm thử cho mô hình), bằng chứng ưu tiên theo mức, nội dung ≤ 3 gợi ý cũ, khối "dữ liệu không đáng tin", bố cục và độ dài theo mức; (e) test chuỗi prompt cũ đổi CÓ CHỦ ĐÍCH: `test_pedagogy_v55` (Ranh giới Mức 1/2, nhãn bằng chứng), `test_learner_model` (KHUNG MÃ), `test_thesis_upgrade` (Mức 1 không còn nêu mô tả test lỗi). Tệp vàng sinh lại.
- 04:53 Offline dev SAU (`hint_levels_v510_r1d_offline_dev.json`): đạt mọi kiểm tra Mức 1 15/15, Mức 2 14/14, Mức 3 15/15 (trước: 8/15, 0/14, 0/15). LƯU Ý trung thực: nhánh offline được viết khi nhìn tập dev nên số trên tập dev là số ĐÃ TINH CHỈNH; tập giữ riêng mới là số đo khách quan (chưa chạy, chưa đọc).
- 04:54 Chưa quyết: không chỉnh `enforce_level3_skeleton` theo `quoted_context` (xem "Cần người dùng quyết định").
