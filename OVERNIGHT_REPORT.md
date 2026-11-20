# Báo cáo chạy đêm v5.10 — nâng chất lượng 3 mức gợi ý

> Nhánh `feat/overnight-deep-upgrade` (tag mốc `pre-overnight-v510`). Chưa push, chưa merge. Nhật ký chi tiết: `plans/PLAN_V510_OVERNIGHT.md`. Số liệu trước/sau và nguyên văn: `docs/HINT_LEVELS_BEFORE_AFTER_V510.md`. Đây là bản đọc trong 5 phút.

## 1. Tóm tắt

**Đã đổi gì.** Ranh giới ba mức giữ nguyên nghĩa; chất lượng nội dung đi sâu hơn về bằng chứng.
- Nhánh rule-based viết lại theo bằng chứng thực thi (`backend/hint_evidence.py`, `backend/hint_rules.py`): Mức 1 gọi tên khái niệm + một phép thử; Mức 2 đúng một dòng mã + đầu vào/kỳ vọng/thực tế (từ thông báo cú pháp, traceback, vết chạy, cấu trúc); Mức 3 dàn ý theo đề + khung mã bám mã người học đã che logic + bảng chạy tay để trống. Hỏi lại cùng mức thì nội dung đổi (không lặp).
- Vết chạy `trace_code_execution` trong cùng phiên MCP (chỉ `ask_ai`, timeout 6 s, fallback tĩnh, chỉ cho mã không import/gọi hàm nguy hiểm).
- Prompt Gemini: tách khối (test vàng khớp từng ký tự trước khi đổi nội dung), Mức 1 không nhận giá trị kiểm thử, bằng chứng ưu tiên theo mức, nội dung ≤ 3 gợi ý cũ, khối "dữ liệu không đáng tin", chỉ dẫn độ dài/bố cục theo mức.
- Đầu ra: phản hồi rỗng/quá ngắn không còn tới người học (lỗi cũ ở Mức 3); phản hồi chép lại chú thích ra lệnh của người học bị thay bằng gợi ý tất định.
- `TutorPanel.jsx`: hiển thị bảng Markdown và chữ nghiêng. Ảnh kiểm ở `docs/ui_audit/v510/` (tối 1280 px, sáng 375 px; console sạch; cặp QA đã tắt).
- Không đổi: luật sao, ba nút IDE, `select_hint_strategy`, S1.4, EXAM, RBAC, `SHOW_EXAM_SESSIONS`, `LeaderboardModal`, schema DB, phụ thuộc pip/npm.

**Đo được gì** (kiểm tra tất định, KHÔNG phải điểm sư phạm; "đạt mọi kiểm tra nội dung", trước → sau):

| Phép đo | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| Gemini thật, tập dev (trước = lần chạy 1; sau = 1 lần) | 9/15 → 9/15 | 8/14 → 14/14 | 5/15 → 12/15 |
| Gemini thật, tập giữ riêng | 5/7 → 4/7 | 3/7 → 4/7 | 2/7 → 5/7 |
| Rule-based, tập dev (số đã tinh chỉnh trên chính tập này) | 9/15 → 15/15 | 0/14 → 14/14 | 0/15 → 15/15 |
| Rule-based, tập giữ riêng (số khách quan) | 6/7 → 6/7 | 0/7 → 3/7 | 0/7 → 7/7 |
| Red-team Gemini thật (27 phản hồi; không có mốc trước) | 7/9 | 6/9 | 7/9 |

Không phản hồi red-team nào lộ biểu thức lời giải hay chương trình hoàn chỉnh. Hồi quy 22 ca Gemini thật sau cải tiến: 20/20 lượt thành công, 48/48 kiểm tra tất định đạt, độ trễ trung vị 2,1 s (`evaluation/real_llm_results_v510.json`, `docs/REAL_LLM_EVALUATION_V510.md`). Chi phí vết chạy: ~+0,8 s trung vị mỗi lượt xin gợi ý (offline).

**Chưa đo được / điều xấu phải nói thẳng**
- Mức 1 với mô hình thật KHÔNG cải thiện trên số đo (vẫn hơi dài; 1 ca nêu giá trị test).
- Mô hình **neo vào "dòng đáng xem" của luật tất định**: ca giữ riêng H01, H06 bản sau chọn SAI dòng (bản trước đúng); "dòng trích đúng chỗ lỗi" vẫn 4/7. Chưa sửa (tập giữ riêng chỉ để đo); đề xuất nhãn độ tin cậy cho dòng đề xuất.
- Kiểm tra từ khóa không bắt được câu hỏi/bước kế tiếp vẫn gợi cách sửa (D03 Mức 1, D12 Mức 2, D03 Mức 3): chỉ đọc tay mới thấy. Cần người chấm.
- Chỉ **một** lần chạy dev thật "sau" (hết ngân sách), trong khi Gemini dao động giữa các lần (hai lần dev trước: Mức 1 9/15 và 8/15, Mức 2 8/14 và 9/14, Mức 3 5/15 và 7/15).
- Bộ đo do chính trợ lý viết và đã tinh chỉnh trong đêm để bỏ dương tính giả (áp dụng đồng nhất cho trước và sau bằng `--rescore`, lý do ở nhật ký). Điểm 0–5 ở `docs/HINT_LEVELS_BEFORE_AFTER_V510.md` là **đề xuất của trợ lý** (cột "SV chốt" trống), không phải điểm của tác giả.
- Đo tải sau khi nối vết chạy (`evaluation/load_benchmark_results_v510.json`, 1/5/10/20 luồng, 20 yêu cầu mỗi mức, 0 lỗi, DB thật không đổi): `ask_ai` (có vết chạy) p50 1,83 s ở 1 luồng, 3,52 s ở 10, 5,88 s ở 20 (p95 7,0 s); `submit` (không vết chạy) cùng mức: 1,85 / 3,62 / 5,94 s. Tức chi phí vết chạy không phân biệt được với nhiễu đo; con số +0,8 s ở trên đến từ phép đo TestClient từng lượt, nên hai số không khớp nhau và nên coi chi phí là "nhỏ, chưa xác định chính xác". So với mốc 13/11 (`load_benchmark_results.json`) chênh trong khoảng ±10%, cả ở `run-test` không đổi gì, nên phần lớn là khác điều kiện máy. Đã có test tích hợp chạy MCP thật cho bước vết chạy (`test_trace_integration_v510`, 2/2). Chưa pilot; không có bằng chứng về hiệu quả học tập.
- Tinh chỉnh sau review (bộ chặn chép chú thích hẹp hơn, bỏ bằng chứng lỗi khi chưa viết code, an toàn vết chạy) chưa được đo lại bằng Gemini thật (hết lượt); chỉ chạy lại offline và test.

## 2. Commit (`git log --oneline pre-overnight-v510..HEAD`)
```
eda05d8 docs(v5.10): REPORT_UPDATES_V510
16bdc91 fix(v5.10): sửa lỗi review
1f9cf9a test(v5.10): hồi quy cuối (toàn xanh)
bdc4749 test(v5.10): hồi quy 22 ca với Gemini thật
6363a45 chore(v5.10): script sinh tệp vàng và kịch bản vào evaluation/
731a81c docs(v5.10): PLAN, handoff §22, CLAUDE §11, nháp chương 3/4, dàn ý và phản biện
cb2d566 docs(v5.10): so sánh trước/sau 3 mức gợi ý
66bb220 docs(v5.10): ảnh kiểm giao diện
8376f81 fix(v5.10): bộ chống chép chú thích chạy cả khi bộ lọc khác gắn cờ ở Mức 3
3da19ac feat(v5.10): chống chép chú thích; đo thật Mức 1 vòng 1c và red-team
0c73861 feat(v5.10): TutorPanel bảng chạy tay; siết trần độ dài Mức 1
c5e62c5 feat(v5.10): vòng 1 đo thật, siết prompt Mức 1/2, tinh chỉnh bộ đo
528bc92 feat(v5.10): độ tin cậy luồng gợi ý, luật 'không đọc input', red-team, test resilience
7aa28d9 feat(v5.10): prompt có bằng chứng theo mức, nội dung gợi ý cũ, dữ liệu không đáng tin
7a179aa feat(v5.10): nhánh rule-based 3 mức dựa trên bằng chứng, vết chạy trong phiên MCP
ff7a550 feat(v5.10): bộ đo 3 mức, mốc trước, test vàng prompt, tách khối prompt
4c15c32 test(v5.10): mốc kiểm thử trước cải tiến
```
`git diff --stat pre-overnight-v510 HEAD`: 151 tệp, +98 543 / −413 (phần lớn là JSON/Markdown kết quả đo); mã sản phẩm (`backend`, `frontend/src`): 8 tệp, +1 332 / −396. `mcp_server/` không đổi.

## 3. Hồi quy cuối so với mốc (`evaluation/v510_baseline/` → `evaluation/v510_final/`)
Mốc và cuối đều xanh toàn bộ: compileall OK; `test_thesis_upgrade` 61, learner_model 34, phase16 ×6, phase17 ×5, qa_authorization ×9, level3 ×15, pedagogy_v55 ×19, passwords ×7, no_code_hint ×5, data_capture ×8, class_overview ×9, visual_views ×19, plain_language ×23; 8 script phase5–15.4 + MCP 8/8 + backend E2E 6/6 đạt; bốn module mới: hint_quality 17, hint_evidence 14, prompt_golden 2, hint_resilience 20 (tổng test đơn vị 156 → 211 với năm module mới trong bảng của báo cáo, gồm `test_trace_integration_v510` 2 ca chạy MCP thật). Đo: guard dev rò rỉ 0/30, giữ riêng 4/14 (không đổi); RAG hit@3 36/38 (không đổi); che Mức 3 lọt 0/24 và 0/16 (không đổi); replay Phase 17 và chính sách mô hình người học không đổi. Frontend: `test:theme` 3/3, `test:ui-utils` 12 → 17, build OK. `/code-review high`: 7 phát hiện, 6 đã sửa (vết chạy chạy trong tiến trình MCP → chỉ cho mã an toàn; bộ chặn chép chú thích quá rộng; bằng chứng lỗi cho mã trống; chọn sai vòng while; regex chữ nghiêng; chuỗi nhiều dòng), 1 để mở (test tích hợp vết chạy).
SHA256 đầu/cuối đêm trùng: `bao_cao_final.docx` = `3E611B83…771C27`, `pytutor.db` = `ACC3701F…2A4CF`. Cổng 8000/5173/8001/5174 không có tiến trình nào còn nghe; DB tạm đã xóa.

## 4. Lượt Gemini
Bộ đếm `evaluation/v510_gemini_calls.json`: 275 lượt do `evaluate_hint_levels.py` + 22 lượt hồi quy `evaluate_real_llm.py` (đếm tay; thực tế 20 lượt gọi LLM) = **297/300**. Chỉ dữ liệu giả lập; Qwen bị tắt trong lúc đo; không đọc `pytutor.db`; không in khóa.

## 5. Tài liệu đã cập nhật, chỗ cần mắt người
- Đã cập nhật: `PLAN.md` (dòng v5.10), `AI_HANDOFF_CONTEXT.md` §22, `CLAUDE.md` §11, `docs/THESIS_CHAPTER3_DRAFT.md` (3.2.2, 3.4.2, 3.4.3), `docs/THESIS_CHAPTER4_DRAFT.md` (mục 4.5.7), `docs/THESIS_OUTLINE_AND_DEFENSE.md` (Phần 6: kịch bản demo 3 mức và 8 câu phản biện, có câu "Gợi ý sâu hơn có làm sinh viên ỷ lại không?").
- **`docs/REPORT_UPDATES_V510.md`**: từng chỗ cần đổi trong `bao_cao_final.docx` (số mục, câu để Ctrl+F, đoạn thay thế). Chèn hay không là quyết định của anh (báo cáo đã qua Turnitin 19/11). Phát hiện không khớp mã: báo cáo ghi lời nhắc gợi ý dùng mẫu Jinja2 (chỉ chat dùng); "156 ca / tám mô-đun" thành 209 / mười hai; hai ngày chạy khác nhau (18/11 và 19/11) ở Bảng 4.3.
- Cần mắt người: các điểm 0–5 đề xuất (cần anh hoặc người chấm độc lập chấm), nguyên văn ca xấu (H01, H06, D03 Mức 1/3) và đoạn "Điều không cải thiện" trong 4.5.7.

## 6. Cần anh quyết định
1. Khung Mức 3 có giữ nguyên văn các dòng của người học (`quoted_context`)? Đề xuất: KHÔNG (bản che toàn bộ là bản duy nhất đã đo, lọt 0/24 và 0/16).
2. Bộ lọc ranh giới Mức 1/2 ở đầu ra (Mức 1: dòng code/giá trị test; Mức 2: cụm chỉ cách sửa): chặn cứng hơn nhưng thay nhiều gợi ý của mô hình bằng bản rule-based.
3. Gắn nhãn độ tin cậy cho dòng đáng xem để mô hình tự chọn dòng khi độ tin cậy thấp (sửa lỗi H01/H06). Chưa làm vì tập giữ riêng chỉ để đo; làm xong cần tập giữ riêng mới.
4. Mức 1 không còn nêu mô tả test lỗi: có muốn quy ước mô tả "an toàn"?
5. `LeaderboardModal` (mâu thuẫn nguyên tắc "so với chính mình"): vẫn là việc còn mở, chưa chạm.

## 7. Việc chưa làm
Chạy lại Gemini thật cho bản sau review; sandbox riêng cho vết chạy (hiện dùng danh sách an toàn); bản `.docx` có tracked changes (tùy chọn, không làm); pilot người học.

## 8. Lệnh git buổi sáng (PowerShell)
Xem: 
```powershell
git log --oneline main..feat/overnight-deep-upgrade
```
Giữ tất cả lên main:
```powershell
git switch main; git merge --ff-only feat/overnight-deep-upgrade
```
Chỉ giữ v5.3–v5.9, bỏ phần đêm nay:
```powershell
git switch main; git merge --ff-only pre-overnight-v510
```
**Cảnh báo:** `main` chưa có v5.3–v5.9 (chúng nằm ở commit snapshot `a3328a3` trên nhánh này). Đừng chỉ chạy `git switch main` rồi tưởng đã mất việc. Tệp untracked có chủ đích: `scratch/`, `.codex/`, `.gemini/`, `.claude/skills`, `.claude/agents`, `frontend/.impeccable`, `pytutor.db.backup_before_seed`.
