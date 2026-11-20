# Kế hoạch nâng cấp chuẩn khóa luận & chuẩn sư phạm (v5.3)

> Trạng thái: xem bảng "Tiến độ lát cắt" cuối tài liệu. Ngày lập: 12/11/2026.
> Phạm vi: giữ nguyên stack (React/Vite + FastAPI + MCP stdio + SQLite WAL) và mọi luật bất biến trong `CLAUDE.md`.
> Hai thư mục khóa luận mẫu chỉ được đọc để tham khảo cách trình bày bằng chứng; không sao chép mã, không chỉnh sửa.

## 1. Điều học được từ hai khóa luận mẫu

### Mẫu 1 — Chatbot RAG tư vấn tuyển sinh & quy chế (11223903)

| Điểm quan sát trong báo cáo | Vì sao có giá trị với hội đồng | Áp dụng vào PyTutor |
|---|---|---|
| Mục 3.10: bộ kiểm thử cố định 100 câu, chia 4 nhóm, trong đó 10% là câu "ngoài phạm vi / kiểm tra ảo giác" | Kết quả có mẫu số rõ, lặp lại được, có nhóm bẫy để đo an toàn | Bộ corpus phiên bản hóa cho Anti-Spoil và RAG, có nhóm câu ngoài KB để đo "không bịa nguồn" |
| Chương 4: bảng kết quả theo từng nhóm câu hỏi (điểm TB, tỷ lệ đạt), không chỉ một con số tổng | Thấy được nhóm yếu, không che bằng trung bình | Báo cáo theo nhóm: loại tấn công, chủ đề Python, loại quyết định guard |
| Bảng hiệu năng: trung bình, min, max, phân vị 90 | Trung thực về outlier | Báo cáo median/p95/max độ trễ guard và truy xuất |
| Chương 5: nêu hạn chế (dữ liệu tự tổng hợp, phụ thuộc API ngoài, OCR lỗi) | Giảng viên đánh giá cao tự phê bình có căn cứ | Mục "Giới hạn" bắt buộc trong báo cáo thực nghiệm; tách kiểm thử kỹ thuật với pilot người dùng |
| Câu trả lời dựa trên nguồn chính thống của trường | Minh bạch nguồn | Hiển thị nguồn KB trong câu trả lời khái niệm; nói rõ khi không có nguồn; GV xem được danh mục KB |

Khác biệt cần giữ: Mẫu 1 chấm chất lượng câu trả lời LLM bằng thang 0–5. PyTutor **không** tự chấm chất lượng sư phạm của LLM bằng máy; phần đó thuộc pilot người dùng (chưa chạy). Benchmark của PyTutor chỉ đo các thành phần tất định (guard, truy xuất, chính sách chọn chiến lược).

### Mẫu 2 — Hệ thống chấm điểm thực hành thể thao (11224188)

| Điểm quan sát | Vì sao có giá trị | Áp dụng vào PyTutor |
|---|---|---|
| Mục 3.1.2: pipeline chấm điểm mô tả từng bước, có công thức thành phần (S1, S2, Sf) | Người dùng và hội đồng hiểu điểm đến từ đâu | Giải thích tường minh vì sao 1/2/3⭐ (mức gợi ý cao nhất đã dùng, số lần thử) ngay khi nộp bài |
| Kết quả kèm xếp loại + bảng điểm chi tiết của phiên | Phản hồi đọc được, không chỉ một con số | Thẻ "Vì sao số sao này" + cách cải thiện |
| Lịch sử luyện tập, lọc theo khoảng thời gian, 3 biểu đồ tiến độ | Hỗ trợ tự theo dõi | Mục "Lỗi lặp lại" và "Bước luyện tập tiếp theo" trong hồ sơ; GV lọc insight theo 7/30/90 ngày |
| Quản lý mục tiêu có thanh tiến độ | Tự điều chỉnh học tập | Khuyến nghị bài kế tiếp tất định (không thêm bảng mục tiêu mới — tránh phình phạm vi) |
| Kết luận: "công thức chấm chưa được chuyên gia kiểm chứng, kết quả mang tính tham khảo" | Trung thực về tính hợp lệ của thang đo | Ghi rõ sao tự lực / `autonomy_score` / `data_status` là quy ước vận hành; bỏ nhãn kiểu "Chuẩn A+ NEU" |
| Schema gọn (6 bảng), service tách khỏi UI | Thiết kế mạch lạc | Hàm tổng hợp nằm ở `backend/database.py`, endpoint mỏng, UI chỉ hiển thị |

## 2. Khoảng trống của PyTutor (kiểm chứng trên mã nguồn ngày 12/11/2026)

| # | Khoảng trống | Bằng chứng trong mã | Mức ảnh hưởng |
|---|---|---|---|
| G1 | Hai bản `compute_student_model` đã lệch nhau | Bản `mcp_server/storage.py` thiếu `data_status`, `sample_size`, `metric_definition_version` và nhánh "Chưa đủ dữ liệu để phân loại"; bản này lại là bản được đưa vào prompt gợi ý và `SubmitResponse` | Cao — hồ sơ thưa vẫn bị gán nhãn năng lực trong luồng gợi ý |
| G2 | Nhãn chẩn đoán vượt quá bằng chứng | Chuỗi "Xuất sắc … (Chuẩn A+ NEU)" trong cả hai bản | Cao — vi phạm trung thực khoa học |
| G3 | Fallback offline mức 2 khẳng định nguyên nhân không có căn cứ | `generate_rule_based_fallback` luôn nói "lỗi nằm ở cận trên của vòng lặp" bất kể bài nào | Cao — demo offline là chế độ mặc định |
| G4 | Prompt gợi ý chưa buộc cấu trúc formative (mục tiêu → bằng chứng → bước kế tiếp); nhánh pass chưa rút giàn giáo | `build_scaffolding_prompt`; thông báo chúc mừng cố định khi `submit` pass | Trung bình |
| G5 | 👍/👎 chỉ có ở chat; Pythonic Review không trả `interaction_id` | `pythonic_review_endpoint` | Trung bình |
| G6 | Nguồn RAG không hiển thị cho người học; truy xuất trả về mọi đoạn có điểm > 0 nên câu ngoài KB vẫn "có nguồn" | `TutorChatResponse` không có trường nguồn; `retrieve_knowledge` không có ngưỡng | Cao — rủi ro trích nguồn không liên quan |
| G7 | Sinh viên không thấy lý do số sao, lỗi lặp lại, bước tiếp theo cụ thể | `SubmitResponse.stars_earned` chỉ là số | Trung bình |
| G8 | Giảng viên chưa có góc nhìn bài gây nghẽn / cơ cấu lỗi / SV cần hỗ trợ kèm cỡ mẫu; class chat offline chỉ trả câu xin lỗi | `get_class_learning_summary`, `generate_instructor_answer` | Cao — demo với GV |
| G9 | GV không xem được KB mà AI đang dùng | Không có endpoint | Trung bình |
| G10 | Chưa có benchmark định lượng cho guard (FPR, độ trễ) và RAG (hit-rate, no-source) | Chỉ có `test_phase16_ai_upgrade.py` dạng pass/fail | Cao — thiếu chương thực nghiệm |
| G11 | `docs/EVALUATION_REPORT.md` cũ, chưa tách kỹ thuật với pilot | — | Trung bình |
| G12 | Pilot kit mới ở mức mô tả, chưa có phiếu in/điền được | `docs/PHASE_17_METRICS_AND_BENCHMARK.md` | Trung bình |

## 3. Lát cắt dọc và tiêu chí nghiệm thu

Mỗi lát cắt: DB/schema → backend/MCP → UI → test. Xong và pass mới sang lát cắt kế.

### S1 — Phản hồi formative, vòng feedback, nguồn RAG
- **S1.1 Formative contract**: prompt gợi ý và fallback offline đều theo 3 phần *Mục tiêu/đang ở đâu → Bằng chứng → Bước kế tiếp*; fallback chỉ nêu điều quan sát được từ test/AST; khi pass thì rút giàn giáo: ghi nhận + 1 câu tự kiểm + 1 hướng mở rộng tùy chọn (không gọi LLM khi `submit`).
  - *Nghiệm thu*: test xác nhận fallback mức 2 không chứa khẳng định về vòng lặp khi bài không có vòng lặp; prompt chứa khối formative; không thay đổi `hint_level`.
- **S1.2 Feedback 👍/👎**: `ask_ai` (đã có `interaction_id`) và Pythonic Review (bổ sung `interaction_id`) đều đánh giá được; kiểm tra chủ sở hữu; GV xem tổng hợp theo loại tác vụ (không nội dung, không danh tính).
  - *Nghiệm thu*: test owner/duplicate/role; endpoint tổng hợp chỉ trả số đếm.
- **S1.3 Nguồn RAG**: chunk có tiêu đề mục; ngưỡng liên quan tối thiểu; `TutorChatResponse.sources` + `knowledge_status` (`grounded` | `no_source`); UI hiện nguồn hoặc ghi rõ "không có tài liệu nội bộ phù hợp".
  - *Nghiệm thu*: câu trong KB trả đúng mục; câu ngoài KB trả `no_source` và danh sách rỗng.
- **S1.4 Khóa phạm vi Chat & Minh bạch luật Sao tự lực** (bổ sung theo góp ý chủ dự án 12/11/2026):
  - Dạy rõ quy tắc 3 nút & Sao tự lực (1–3⭐) vào `SOCRATIC_TEMPLATE` (`backend/prompt_templates.py`) để gia sư trả lời đúng luật hệ thống khi sinh viên hỏi, không tự bịa.
  - Tách 2 chế độ cho `POST /api/tutor/chat` theo trạng thái `has_passed_submit` (`action_type='submit'` & `all_passed=1` trên `(username, exercise_id)`):
    1. **Chưa nộp bài pass:** Chỉ giải thích **khái niệm Python tổng quát**; backend **không truyền `<student_code>`** vào prompt chat (giữ signature `render_socratic_prompt` tương thích test cũ), cấm chẩn đoán dòng lỗi hay chỉnh trực tiếp code bài tập; nếu sinh viên hỏi gỡ lỗi code bài đang làm thì nhắc bấm `🤖 Hỏi Gia sư AI`.
    2. **Đã hoàn thành & nộp bài pass:** Mở khóa hỏi và làm rõ chi tiết về code đã nộp (vì sao bài đã chốt).
  - Cập nhật copy/placeholder trong `TutorPanel.jsx` (dòng 434, 496) cho đúng phạm vi trước và sau khi nộp bài đạt.
  - *Nghiệm thu*: unittest xác nhận trước khi nộp pass, prompt chat không chứa `<student_code>` bài làm và yêu cầu gỡ code được chuyển hướng về `Hỏi Gia sư AI`; sau khi nộp pass mới mở ngữ cảnh code đã nộp; AI trả lời đúng luật sao tự lực.

### S2 — Minh bạch cho sinh viên
- **S2.1** `SubmitResponse.star_rationale`: số sao, mức gợi ý cao nhất đã dùng, số lần thử, quy tắc, cách đạt mức cao hơn; ghi chú đây là quy ước sản phẩm.
- **S2.2** Student model (cả hai bản, đồng bộ): `recurring_difficulties`, `next_practice`; bỏ nhãn vượt bằng chứng; bản MCP có đủ `data_status`.
- **S2.3** UI: thẻ lý do sao khi nộp; hồ sơ hiển thị lỗi lặp lại + bước tiếp theo + trạng thái dữ liệu.
- **S2.4** Chống "cày sao" tự lực (bổ sung theo góp ý chủ dự án 12/11/2026): tính `max_hint_used` trên **toàn bộ** lượt `action_type = 'ask_ai'` cho tới lần `submit` pass đầu tiên (không bị giới hạn `LIMIT 5` làm trôi lịch sử Mức 3 cũ, và không gộp `hint_level` của nút `submit` fail); sau khi đã từng pass ở bài đó thì làm lại chỉ phục vụ ôn tập/Pythonic Review, không cày tăng sao từ bài đã xem gợi ý; đồng thời sửa lời khuyên trong `explain_autonomy_stars` (`backend/database.py`) từ *"thử làm lại bài này..."* sang hướng dẫn áp dụng sang **các bài mới/tiếp theo** ở Mức 1–2 hoặc không cần gợi ý (cập nhật khớp `test_thesis_upgrade.py`).
  - *Nghiệm thu*: test parity so khớp toàn bộ `analytics_metrics` và `diagnostic_evaluation` giữa hai bản trên cùng DB; `ask_ai` không đổi metric; nộp lại >5 lần sau khi từng dùng `ask_ai` Mức 3 vẫn không thể đẩy mất vết Mức 3 để lấy 3 sao.

### S3 — Không gian sư phạm cho giảng viên
- **S3.1** `GET /api/instructor/classes/{id}/insights?days=`: bài gây nghẽn, cơ cấu lỗi, SV cần hỗ trợ (kèm `data_status`, số bài), cỡ mẫu, ghi chú giới hạn. Chỉ `submit`. Kiểm tra sở hữu lớp.
- **S3.2** Class chat: tóm tắt giàu hơn (vẫn chỉ số tổng hợp, không danh tính); fallback tất định trả lời bằng số liệu + khoảng thời gian + cỡ mẫu + giới hạn.
- **S3.3** `GET /api/instructor/knowledge-base`: danh mục tài liệu, số đoạn, các mục, ghi chú nguồn gốc.
- **S3.4** UI trong không gian lớp + khu vực giảng viên.
  - *Nghiệm thu*: 404 với lớp không sở hữu; insight rỗng trả `no_data`; class chat không chứa username/mã SV.

### S4 — Đo lường & pilot kit
- **S4.1** `evaluate_guardrails_benchmark.py` + corpus `evaluation/guardrail_corpus.json`: `leak_rate`, `block_rate`, `false_positive_rate`, median/p95.
- **S4.2** `evaluate_rag_benchmark.py` + `evaluation/rag_questions.json`: hit@1, hit@3, MRR, tỷ lệ no-source đúng với câu ngoài KB.
- **S4.3** Báo cáo `docs/EVALUATION_REPORT_V5_3.md` sinh từ số liệu chạy thật; nêu giới hạn.
- **S4.4** `docs/PILOT_KIT.md`: kịch bản, phiếu đồng ý, phiếu chấm, đáp án cho ca giảng viên.
  - *Nghiệm thu*: script chạy offline trên DB tạm, thoát mã 0, in bảng; unittest khóa ngưỡng phát hành (`leak_rate = 0`).

### S5 — Kiểm tra UI & xác minh toàn hệ thống
- Light/Dark, Desktop/Mobile, loading/empty/error/no-data cho các màn hình đã đổi; chạy trên DB tạm; toàn bộ lệnh kiểm chứng trong `CLAUDE.md`.

## 4. Ngoài phạm vi (có chủ đích)
- Không nạp giáo trình NEU (chưa được cấp quyền). KB mở rộng vẫn là tài liệu biên soạn nội bộ.
- Không chấm chất lượng sư phạm của LLM bằng máy; không gọi LLM thật trong benchmark.
- Không thêm bảng "mục tiêu cá nhân" như Mẫu 2; dùng khuyến nghị tất định từ dữ liệu sẵn có.
- Không bật `SHOW_EXAM_SESSIONS`.

## 5. Tiến độ lát cắt

> **Cập nhật gần nhất: phiên 12/11/2026 (lần 5, phiên cuối) — xong S5; gói nâng cấp v5.3 hoàn tất về kỹ thuật.** Bảng dưới là trạng thái hiện hành; chi tiết phiên này ở mục 5.7, các mục 5.0–5.6 là nhật ký các phiên trước (giữ nguyên để truy vết). Chưa commit gì. Việc còn lại thuộc về con người: chạy pilot thật và quyết định Git commit.

| Lát cắt | Trạng thái | Ghi chú |
|---|---|---|
| GĐ1 Gap analysis | ✅ Xong | Tài liệu này (mục 1–4). |
| S1 Phản hồi formative, feedback, nguồn RAG | ✅ S1.1–S1.4 xong (backend + UI + test) | Xem 5.0, 5.1, 5.5 |
| S2 Minh bạch cho sinh viên | ✅ S2.1–S2.4 xong (backend + UI + test) | Xem 5.0, 5.1, 5.5 |
| S3 Không gian giảng viên | ✅ S3.1–S3.4 xong (backend + UI) | Xem 5.1, 5.5 |
| S4 Đo lường & pilot kit | ✅ S4.1–S4.4 xong (benchmark + corpus + `docs/EVALUATION_REPORT_V5_3.md` + `docs/PILOT_KIT.md`). **Pilot người dùng vẫn CHƯA chạy** (việc của con người, ngoài S4) | Xem 5.2, 5.6 |
| S5 Kiểm tra UI & xác minh toàn hệ thống | ✅ Xong: các mục "chưa xem" ở 5.0/5.5 đã xem trên cặp QA `:8001/:5174` (DB tạm, offline); bộ test phân hệ cũ đã chạy lại. **Chưa kiểm chứng:** hành vi với LLM thật | Xem 5.7 |

### 5.0. Cập nhật phiên 12/11/2026 (tiếp theo) — sửa lỗi test + UI sinh viên S1–S2

Trạng thái mới: **S1 = 🟡 S1.1–S1.3 xong, chờ bổ sung S1.4 (khóa phạm vi Chat + luật Sao)**; **S2 = 🟡 S2.1–S2.3 xong, chờ bổ sung S2.4 (chống cày sao)**; S3 = backend xong, **UI giảng viên chưa làm**; S4 = báo cáo v5.3 và pilot kit chưa viết; S5 = mới kiểm tra phần sinh viên. Chưa commit gì.

**Sửa lỗi**
- `save_exercise_stars` (`backend/database.py`): không còn INSERT `stars_earned = 0` (vi phạm CHECK 1..3) khi Pythonic Review chạy trước lượt "Nộp bài"; chỉ tạo dòng khi sao 1..3, bọc `try/finally: conn.close()`. Hệ quả: clean score của review **không được lưu** nếu bài chưa có dòng sao (sao chỉ sinh từ `submit`).
- RAG: `_tokens` bỏ token một ký tự (tên biến `n`, `x`... trong ví dụ); mục "Vòng lặp và điều kiện dừng" (`python_fundamentals.md`) thêm câu nói rõ `range(1, n)` không lấy cả số n. Lưu ý trung thực: câu này được thêm sau khi thấy câu hỏi Q01 của tập phát triển trượt, nên số liệu dưới đây là trên tập đã dùng để chỉnh.

**Kiểm chứng (mỗi module một DB tạm riêng; chạy chung một DB thì `test_qa_authorization` fail do lẫn dữ liệu của `test_thesis_upgrade`)**
- `compileall` OK; `test_thesis_upgrade` 29/29; `test_phase16_ai_upgrade` 6/6; `test_phase17_adaptive_analytics` 5/5; `test_qa_authorization` 9/9.
- RAG: hit@1 34/38 = 89,47% (trước 33/38); hit@3 36/38 = 94,74%; MRR 0,9211 (trước 0,9035); no-source 13/14 = 92,86% (không đổi).
- Guardrail (tập phát triển, luật v2): rò rỉ 0/30, injection 22/22, chặn nhầm 0/28 và 0/31 (không đổi).
- `npm.cmd run test:theme` 3/3; `npm.cmd run build` OK.
- Trình duyệt (backend DB tạm, `PYTUTOR_DISABLE_LLM=1`, tài khoản `student`): 👍/👎 gợi ý `ask_ai` và Pythonic Review lưu được; chat hiện nguồn nội bộ / "không có tài liệu nội bộ phù hợp"; thẻ lý do sao sau "Nộp bài"; hồ sơ hiện trạng thái dữ liệu, khó khăn lặp lại, bước tiếp theo; không lỗi console; không tràn ngang ở 375px; đã xem light (desktop + mobile). **Chưa xem:** dark cho hồ sơ/review, trạng thái lỗi mạng, hồ sơ có dữ liệu lỗi lặp lại thật, vai trò giảng viên.

**UI đã làm (sinh viên)**
- `components/TutorFeedbackButtons.jsx` (mới, dùng chung), `TutorPanel.jsx` (feedback gợi ý, nguồn chat, thẻ lý do sao; khi chỉ chạy thử/hỏi AI không còn hiện 3 sao mặc định), `PythonicReviewModal.jsx` (feedback + ghi chú tham khảo), `StudentProfileModal.jsx` (chip trạng thái dữ liệu, khó khăn lặp lại, bước luyện tập tiếp theo; dải phân hạng đổi sang nền phẳng để đọc được ở light), `pages/StudentIDE.jsx` (truyền `interaction_id`, `star_rationale`), `services/api.js` (3 hàm cho endpoint giảng viên, UI chưa dùng).
- Thêm `.claude/launch.json` (chạy Vite cho preview).

**Còn lại:** Bổ sung **S1.4 khóa phạm vi Chat + luật Sao** (`backend/prompt_templates.py`, `backend/llm_service.py`, `backend/main.py`, `TutorPanel.jsx`), **S2.4 chống cày sao tự lực** (`backend/main.py`, `backend/database.py`, `test_thesis_upgrade.py`), UI giảng viên S3 (`InstructorDashboard.jsx`), `docs/EVALUATION_REPORT_V5_3.md`, `docs/PILOT_KIT.md`, cập nhật `PLAN.md`/`AI_HANDOFF_CONTEXT.md`/`CLAUDE.md`, pilot người dùng.

### 5.1. Đã làm ở backend (S1–S3)

| Khoảng trống | Thay đổi | Tệp |
|---|---|---|
| G1, G2 | Sửa nhãn vượt bằng chứng ("Chuẩn A+ NEU", "chuẩn Senior"...) thành nhãn mô tả; bản MCP được **sinh lại từ bản backend** nên có đủ `data_status`, `sample_size`, nhánh "Chưa đủ dữ liệu". Thêm `recurring_difficulties`, `next_practice`; `metric_definition_version` = "2". | `backend/database.py`, `mcp_server/storage.py` |
| G3, G4 | Prompt gợi ý có khối "KHUNG PHẢN HỒI HÌNH THÀNH" (mục tiêu → bằng chứng → một bước kế tiếp) và nhánh pass "RÚT GIÀN GIÁO". Fallback offline viết lại: chỉ nêu điều quan sát được từ test/AST, không còn khẳng định "lỗi ở cận trên vòng lặp". `submit` + pass dùng `build_pass_feedback` (tất định, không gọi LLM). `hint_level` không đổi. | `backend/llm_service.py`, `backend/main.py` |
| G5 | Pythonic Review trả `interaction_id` + `llm_source`; endpoint feedback cũ dùng lại được (kiểm tra chủ sở hữu). Thêm `GET /api/instructor/ai/feedback-summary` (chỉ số đếm theo loại tác vụ, giới hạn trong lớp của giảng viên). | `backend/main.py`, `backend/schemas.py`, `backend/database.py` |
| G6 | Truy xuất có ngưỡng `MIN_RELEVANCE = 0.16`, bỏ hư từ, chunk theo mục (có `section`), không index dòng "Nguồn:". Chat trả `sources` + `knowledge_status` (`grounded`/`no_source`); offline trả lời bằng trích đoạn KB có nguồn hoặc nói rõ không có nguồn. KB thêm `python_core_topics.md` (12 mục, **biên soạn nội bộ, chưa phải giáo trình NEU**). | `backend/rag/retriever.py`, `backend/llm_service.py`, `backend/prompt_templates.py`, `docs/knowledge_base/` |
| G7 | `SubmitResponse.star_rationale` (số sao, mức gợi ý cao nhất, số lần thử, quy tắc, cách cải thiện, ghi chú "quy ước sản phẩm"). Quy tắc tính sao **không đổi**. | `backend/database.py`, `backend/main.py`, `backend/schemas.py` |
| G8 | `GET /api/instructor/classes/{id}/insights?days=` (bài gây nghẽn, cơ cấu lỗi, SV cần hỗ trợ kèm `data_status`, cỡ mẫu, caveats; chỉ `submit`; 404 nếu không sở hữu lớp). Class chat dùng tóm tắt giàu hơn nhưng vẫn không có danh tính; khi không có LLM trả lời tất định kèm khoảng thời gian, cỡ mẫu, giới hạn. `data_status` của lớp nay là `no_data`/`limited`(<3 SV hoạt động)/`sufficient` thay cho `available`. | `backend/database.py`, `backend/main.py`, `backend/llm_service.py`, `backend/schemas.py` |
| G9 | `GET /api/instructor/knowledge-base` (danh mục tài liệu, mục, số đoạn, ghi chú nguồn gốc). | `backend/main.py`, `backend/rag/retriever.py` |
| — | Biến môi trường mới `PYTUTOR_DISABLE_LLM=1` ép chế độ offline cho test/benchmark/pilot. | `backend/llm_service.py` |

**Chưa làm (frontend):** `TutorPanel.jsx` (👍/👎 cho gợi ý `ask_ai`, hiển thị nguồn/“không có nguồn” trong chat, thẻ lý do sao), `PythonicReviewModal.jsx` (👍/👎), `StudentProfileModal.jsx` (lỗi lặp lại, bước tiếp theo, trạng thái dữ liệu), `InstructorDashboard.jsx` (insight lớp, danh mục KB, tổng hợp feedback), `services/api.js` (3 hàm gọi endpoint mới). Các trường mới đều là tùy chọn nên UI hiện tại vẫn chạy được.

### 5.2. Đã làm ở S4 và số liệu đo thực tế (12/11/2026, offline, DB/chỉ mục tạm)

Tệp mới: `evaluate_guardrails_benchmark.py`, `evaluate_rag_benchmark.py`, `evaluation/guardrail_corpus.json`, `evaluation/guardrail_holdout.json`, `evaluation/rag_questions.json`, `test_thesis_upgrade.py`.

Guard (`backend/guardrails.py` nâng lên `GUARD_RULES_VERSION = "2"`); phản hồi "mô hình" trong corpus là **giả lập**:

| Tập | Bộ luật | Rò rỉ (tấn công) | Chặn injection | Chặn nhầm câu hỏi | Chặn nhầm phản hồi |
|---|---|---|---|---|---|
| Phát triển (30/22/28/30 ca) | v1 (Phase 16) | 8/30 = 26,67% | 18/22 | 3/28 | 1/30 |
| Phát triển (30/22/28/31 ca) | v2 | 0/30 = 0% | 22/22 | 0/28 | 0/31 |
| **Giữ riêng** (14/10/12/12 ca) | v2 | **4/14 = 28,57%** | **1/10** | 1/12 | 0/12 |

- Luật v2 được chỉnh trên chính tập phát triển nên 0% ở đó không nói lên mức khái quát. Tập giữ riêng (soạn sau khi đóng băng luật, **không dùng để chỉnh**) cho thấy guard regex còn lọt code dạng bảng, đánh thứ tự a)/b)/c), code lồng trong câu văn, cụm tiết lộ diễn đạt khác, và hầu hết injection diễn đạt lại. Đây là giới hạn phải ghi vào báo cáo; không được vá theo tập này rồi vẫn gọi là hold-out.
- Độ trễ guard: median ≈ 0,01 ms, p95 ≈ 0,02 ms.

RAG (17 đoạn KB, top-3, ngưỡng 0,16): hit@1 33/38 = 86,84%; hit@3 36/38 = 94,74%; MRR 0,9035; câu ngoài KB trả "không có nguồn" đúng 13/14 = 92,86% (lọt: câu về đệ quy khớp mục "Hàm"); truy xuất median ≈ 1,5 ms, p95 ≈ 1,8 ms. Quét ngưỡng: 0,0 → no-source 0/14; 0,08 → 6/14; 0,12 → 10/14 (hit@3 37/38); 0,16 → 13/14 (hit@3 36/38); 0,20 → 13/14 (hit@3 33/38).

**Chưa làm:** `docs/EVALUATION_REPORT_V5_3.md`, `docs/PILOT_KIT.md`.

### 5.3. Trạng thái kiểm chứng tại thời điểm dừng

- ✅ `py -m compileall -q backend mcp_server` đạt (trước khi viết lại guard v2 và đổi ngưỡng RAG; **chưa biên dịch lại sau đó**, dù hai script benchmark đã nạp và chạy được các module này).
- ✅ 20 test cũ (`test_phase16_ai_upgrade`, `test_phase17_adaptive_analytics`, `test_qa_authorization`) đạt trên DB tạm — đo **trước** khi viết lại guard v2 và đổi ngưỡng RAG; **chưa chạy lại sau đó**.
- ❓ `test_thesis_upgrade.py` (mới): đã khởi chạy trên DB tạm nhưng **chưa có kết quả khi dừng phiên** — coi như chưa kiểm chứng.
- ⏳ Chưa chạy: `evaluate_phase17_adaptive.py`, `mcp_server.test_mcp_server`, `backend.test_backend_e2e`, `npm.cmd run test:theme`, `npm.cmd run build`, kiểm tra UI trên trình duyệt.
- `pytutor.db`, `pytutor_knowledge.sqlite3` gốc và hai thư mục khóa luận mẫu không bị chỉnh sửa. Lưu ý: lần khởi động app kế tiếp sẽ dựng lại chỉ mục KB theo schema mới (hành vi sẵn có của `lifespan`).

### 5.4. Việc tiếp theo khi quay lại

1. ~~Hoàn thiện S1.4 và S2.4~~ — ✅ xong ở phiên 12/11/2026 (lần 3), xem 5.5.
2. ~~Làm UI giảng viên S3~~ — ✅ xong ở phiên 12/11/2026 (lần 3), xem 5.5.
3. ~~Viết `docs/EVALUATION_REPORT_V5_3.md` từ số liệu chạy lại và `docs/PILOT_KIT.md` (S4.3, S4.4)~~ — ✅ xong ở phiên 12/11/2026 (lần 4), xem 5.6.
4. **(Phiên cuối)** Cập nhật `PLAN.md`, `AI_HANDOFF_CONTEXT.md`, `CLAUDE.md` (lệnh benchmark mới, `PYTUTOR_DISABLE_LLM`, `test_thesis_upgrade`, quy tắc sao mới ở 5.5, cấu hình QA `qa-backend`/`qa-frontend`, hai tài liệu mới `docs/EVALUATION_REPORT_V5_3.md` và `docs/PILOT_KIT.md`, số liệu kiểm chứng ở 5.6). **Ba tệp này chưa được cập nhật** — làm cùng lúc với S5 ở phiên cuối để chỉ ghi một lần trạng thái chốt.
5. S5 còn lại: các mục "chưa xem" ở 5.0 và 5.5; chạy các bộ test phân hệ chưa chạy lại sau v5.3 (`mcp_server.test_mcp_server`, `backend.test_backend_e2e`, `test_phase8_chat.py`, `test_phase10_gamification.py`, `test_phase12_classroom_exam.py`).
6. Việc cần con người: chạy pilot 2–3 người; cung cấp giáo trình NEU nếu được cấp quyền; dùng DB sạch hoặc tài khoản mới khi demo để không lẫn lịch sử cũ trong `pytutor.db`; quyết định có cần đồng bộ lại sao đã lưu theo luật cũ hay không (xem "Hệ quả cần biết" ở 5.5).

### 5.5. Cập nhật phiên 12/11/2026 (lần 3) — S1.4, S2.4, UI giảng viên S3

**S1.4 Khóa phạm vi Chat + luật Sao tự lực**
- `backend/prompt_templates.py`: thêm `SYSTEM_RULES_TEXT` (ba nút, luật 1–3⭐, "tới lần nộp đạt đầu tiên", sao là quy ước sản phẩm) và nạp vào `SOCRATIC_TEMPLATE`; `render_socratic_prompt` nhận thêm `chat_scope` (`"concept_only"` | `"code_review"` | `"legacy"` mặc định — nơi gọi cũ và `test_phase16_ai_upgrade` không đổi). Ở `concept_only` prompt **không có** khối `<student_code>`.
- `backend/database.py`: `get_latest_passed_submission_code(username, exercise_id)` (lượt `action_type='submit'` & `all_passed=1` gần nhất).
- `backend/main.py` (`POST /api/tutor/chat`): chưa có lượt nộp pass → `concept_only`, không truyền code; đã pass → `code_review` với **code đã nộp đọc từ DB** (không dùng `code` do client gửi). `TutorChatResponse` thêm trường tùy chọn `chat_scope`. EXAM guard vẫn chạy trước.
- `backend/llm_service.py`: `generate_chat_followup(..., chat_scope=)`; `build_system_rule_reply` cho dự phòng offline: (1) câu hỏi về sao/nút → trả đúng `SYSTEM_RULES_TEXT`; (2) `concept_only` mà nhờ gỡ code bài đang làm → chuyển hướng sang **🤖 Hỏi Gia sư AI**. Hai câu trả lời này có `knowledge_status = "not_applicable"`.
- `frontend/src/components/TutorPanel.jsx`: tiêu đề, lời dẫn và placeholder đổi theo phạm vi (trước khi nộp đạt: "Hỏi khái niệm Python"; sau khi nộp đạt: hỏi về code đã nộp); nhãn "Số lần thử" → "Số lần nộp bài".
- Giới hạn: khi có LLM thật, việc từ chối gỡ code ở `concept_only` dựa vào chỉ dẫn trong prompt (và việc prompt không chứa code); phát hiện bằng regex chỉ áp dụng cho nhánh offline và chưa được đo false-positive/false-negative. Anti-Spoil output guard vẫn áp dụng ở cả hai phạm vi, nên ở `code_review` phản hồi chứa ≥ 3 dòng code vẫn bị chặn.

**S2.4 Chống "cày sao"**
- `backend/database.py`: `get_autonomy_hint_context` đọc **toàn bộ** lịch sử: `max_hint_level_used` = mức cao nhất của các lượt `ask_ai` trước lượt `submit` pass đầu tiên (chưa từng pass thì mọi lượt `ask_ai`; bỏ lượt bị EXAM guard khóa; **không** gộp `hint_level` của lượt `submit`), `submit_count`, `has_passed_before`.
- `backend/main.py` (`POST /api/submit`): đọc ngữ cảnh này **trước** khi lưu lượt hiện tại; không còn dùng `attempt_history` (LIMIT 5) để tính sao. Nộp lại sau khi đã pass cho đúng mức sao cũ; `star_rationale` thêm `is_review_resubmission`; `attempt_count` nay là số lượt **Nộp bài** chính thức (kể cả lượt này).
- `explain_autonomy_stars`: lời khuyên chuyển sang "ở các bài tiếp theo", nói rõ sao của bài đã chốt theo mức gợi ý trước lần nộp đạt đầu tiên.
- Hệ quả cần biết: (a) hỏi AI Mức 2/3 **sau** khi đã nộp đạt không làm giảm sao; (b) `save_exercise_stars` vẫn giữ max, nên các dòng sao đã lưu theo luật cũ không bị hạ; (c) luật là quy ước sản phẩm, không phải thang đo đã kiểm chứng.

**S3 UI giảng viên**
- Tệp mới `frontend/src/components/InstructorPedagogyPanels.jsx`: `ClassInsightsPanel`, `ClassChatAnswer`, `TutorFeedbackPanel`, `KnowledgeBasePanel`, `DataStatusChip`, `DaysSelect`; được gắn vào `frontend/src/pages/InstructorDashboard.jsx`:
  - Không gian lớp → tab mới **"Góc nhìn sư phạm"** (`fetchClassInsights`): chọn 7/14/30/90 ngày, chip `data_status`, cỡ mẫu, thanh cơ cấu kết quả, bảng bài gây nghẽn, bảng sinh viên có hoạt động (lọc "cần hỗ trợ", chip dữ liệu theo từng SV), danh sách giới hạn diễn giải; có trạng thái đang tải / lỗi + thử lại / `no_data` / `limited`.
  - "Hỏi AI về tình hình lớp": thêm chọn số ngày; phản hồi hiển thị `days`, `sample` (lượt nộp, SV hoạt động/ghi danh), chip `data_status`, nguồn (mô hình AI hay trả lời tự động) và ghi chú mẫu nhỏ/chưa có dữ liệu.
  - "Giám sát Bài nộp & AI": bảng tổng hợp 👍/👎 theo loại tác vụ (`fetchTutorFeedbackSummary`, 7/30/90 ngày) và danh mục tài liệu RAG kèm ghi chú "chưa phải giáo trình NEU" (`fetchKnowledgeBaseCatalogue`).
- `frontend/vite.config.js` đọc `PYTUTOR_VITE_PORT` / `PYTUTOR_API_TARGET` (mặc định không đổi: 5173 → 8000); `.claude/launch.json` thêm `qa-backend` (:8001, DB tạm `%TEMP%\pytutor_qa.db`, `PYTUTOR_DISABLE_LLM=1`) và `qa-frontend` (:5174) để kiểm tra UI mà không đụng app dev đang chạy trên DB thật.

**Test**
- `test_thesis_upgrade.py`: 29 → **34 test**. Sửa `test_submit_pass_explains_stars_and_fades_scaffolding` (lấy mức gợi ý từ DB, không từ `attempt_history`); thêm `test_resubmitting_cannot_wash_out_level3_hint` (7 lượt nộp lại + hỏi Mức 1 vẫn 1 sao), `test_hints_after_first_pass_and_submit_levels_do_not_change_stars`, `test_chat_before_pass_is_concept_only_and_hides_student_code`, `test_chat_after_pass_unlocks_submitted_code_only`, `test_chat_explains_star_rules_from_system_text`.

**Kiểm chứng (12/11/2026, mỗi lệnh một DB + chỉ mục KB tạm riêng, `PYTUTOR_DISABLE_LLM=1`)**
- `py -m compileall -q backend mcp_server` OK.
- `test_thesis_upgrade` 34/34; `test_phase16_ai_upgrade` 6/6; `test_phase17_adaptive_analytics` 5/5; `test_qa_authorization` 9/9; `evaluate_phase17_adaptive.py` thoát mã 0.
- `test_phase15_4_action_buttons.py`: đạt cả 4 mục (hỏi AI Mức 2 rồi nộp đạt → 2 sao) **khi gọi `init_db()` trước**; chạy thẳng trên DB tạm rỗng thì lỗi 500 ở bước 2 vì script không khởi tạo schema (hành vi có sẵn của script, không do thay đổi phiên này; script chưa được sửa).
- `npm.cmd run test:theme` 3/3; `npm.cmd run build` OK (1697 modules, cảnh báo chunk > 500 kB như cũ).
- Trình duyệt, cặp QA :8001/:5174 trên DB tạm với sinh viên **giả lập**: `gv_tran` — tab Góc nhìn sư phạm (dark + light desktop, dark mobile 375px), Class Chat có dữ liệu (14 ngày) và lớp `no_data`, bảng 👍/👎, danh mục KB (light desktop); không tràn ngang ở 375px. `student` — chat trước khi nộp đạt hiển thị "Hỏi khái niệm Python" và yêu cầu gỡ code được chuyển hướng sang Hỏi Gia sư AI.
- **Chưa xem:** trạng thái lỗi mạng của ba panel giảng viên; trạng thái `limited` của Góc nhìn sư phạm trên giao diện (chỉ có test backend); bảng 👍/👎 và danh mục KB ở dark/mobile; chat sinh viên **sau** khi nộp đạt trên giao diện (chỉ có unittest); hành vi S1.4 với LLM thật. `pytutor.db` gốc không bị ghi bởi các bước kiểm chứng; lưu ý backend dev đang chạy `--reload` trên DB thật đã tự nạp mã mới.

### 5.6. Cập nhật phiên 12/11/2026 (lần 4) — S4.3 báo cáo v5.3, S4.4 pilot kit

Phiên này **chỉ viết tài liệu**: không sửa mã backend/frontend/test, không sửa corpus/KB, không mở trình duyệt, không chạy Vite build. `pytutor.db` và `pytutor_knowledge.sqlite3` gốc không bị đụng.

**Tệp mới**
- `docs/EVALUATION_REPORT_V5_3.md` — báo cáo thực nghiệm v5.3, tách ba tầng bằng chứng (A kiểm thử tự động; B benchmark tất định ngoại tuyến; C pilot người dùng = **CHƯA THỰC HIỆN**), bảng theo nhóm cho guard dev/hold-out, RAG theo chủ đề + quét ngưỡng + độ trễ, replay Phase 17, mục giới hạn và lệnh tái lập. Không thay thế `docs/EVALUATION_REPORT.md` (v3.0).
- `docs/PILOT_KIT.md` — checklist người chủ trì (DB sạch, offline/LLM thật, ẩn danh), phiếu thông tin & đồng ý, kịch bản sinh viên S1–S8 và giảng viên G1–G5, phiếu quan sát, phiếu phản hồi thang 1–5, đáp án đối chiếu (gồm ca bẫy: hỏi ngoài KB, xin gỡ code trước khi nộp đạt, cày sao, hỏi danh tính sinh viên).

**Số liệu đo lại (12/11/2026, DB + chỉ mục KB tạm, `PYTUTOR_DISABLE_LLM=1`; không chỉnh luật/dữ liệu theo kết quả)**
- Guard v2, tập phát triển: rò rỉ 0/30; chặn injection 22/22; chặn nhầm câu hỏi 0/28, phản hồi 0/31; độ trễ median 0,008–0,010 ms, p95 0,015–0,020 ms.
- Guard v2, **tập giữ riêng**: rò rỉ **4/14 = 28,57%** (HA04 bảng, HA07 a)/b)/c), HA08 lồng trong câu văn, HA11 cụm tiết lộ); chặn injection **1/10**; chặn nhầm câu hỏi 1/12 (HB09); chặn nhầm phản hồi 0/12. Không đổi so với 5.2.
- RAG (17 đoạn, top-3, ngưỡng 0,16): hit@1 34/38 = 89,47%; hit@3 36/38 = 94,74%; MRR 0,9211; no-source 13/14 = 92,86% (lọt O02); trượt Q28, Q36; truy xuất median 1,54 ms, p95 1,97 ms, max 8,26 ms.
- Quét ngưỡng (hit@3 / no-source): 0,0 → 38/38 / 0/14; 0,08 → 38/38 / 6/14; 0,12 → 37/38 / **9/14**; 0,16 → 36/38 / 13/14; 0,20 → 33/38 / 13/14. Hàng 0,12 khác số 10/14 ghi ở 5.2 vì số ở 5.2 đo trước khi sửa bộ tách từ (5.0); số hôm nay là số dùng trong báo cáo.
- Replay Phase 17: chiến lược khớp 6/6; baseline tĩnh 2/6; giữ nguyên `hint_level` 6/6; nhất quán bằng chứng 6/6.
- Unittest: 54/54 đạt (`test_phase16_ai_upgrade` 6, `test_phase17_adaptive_analytics` 5, `test_qa_authorization` 9, `test_thesis_upgrade` 34) — đạt cả khi chạy bốn module chung một DB tạm theo thứ tự này lẫn mỗi module một DB tạm riêng (lỗi lẫn dữ liệu ghi ở 5.0 không tái hiện với thứ tự này; thứ tự khác chưa thử). `compileall` thoát mã 0.

**Chưa làm / chuyển phiên cuối**
- S5 giữ nguyên (các mục "chưa xem" ở 5.0 và 5.5; bộ test phân hệ cũ chưa chạy lại).
- `PLAN.md`, `AI_HANDOFF_CONTEXT.md`, `CLAUDE.md` chưa cập nhật (mục 5.4 việc 4).
- Pilot người dùng chưa chạy; kịch bản trong `docs/PILOT_KIT.md` **chưa được chạy thử trên giao diện** — đáp án mục G soạn từ đặc tả và unittest, cần người chủ trì chạy thử một lượt (checklist A1) trước khi mời người tham gia. Chưa xác minh DB mới tinh có sẵn lớp/bài cho tài khoản demo hay không.

### 5.7. Cập nhật phiên 12/11/2026 (lần 5, phiên cuối) — hoàn tất S5

Mọi unittest/script và cặp server QA chạy với `PYTUTOR_DB_PATH` tạm, `PYTUTOR_KNOWLEDGE_DB_PATH` tạm, `PYTUTOR_DISABLE_LLM=1`; các tệp tạm đã xóa, server QA đã đóng. **Lưu ý trung thực về DB gốc:** không bước kiểm chứng nào ghi vào `pytutor.db`/`pytutor_knowledge.sqlite3`, nhưng backend dev của người dùng (`:8000`, `--reload`, chạy từ 03:06) tự khởi động lại khi mã backend được sửa và chạy `init_db()` + nạp lại chỉ mục KB trên DB gốc (mốc sửa tệp 12:33:59) — đây là thao tác khởi động thường lệ, không phải dữ liệu test.

**Sửa lỗi (UI sinh viên + nhánh offline S8a)**
- `TutorPanel.jsx`: khung Chat mở sẵn ngay khi vào bài (bỏ điều kiện `tutorHint`), chỉ khóa ô nhập ở chế độ kỳ thi; nhận `hasPassedBefore` để hiện đúng phạm vi "Trò chuyện về bài đã nộp" cả khi tải lại trang; sửa ô "Vòng lặp" hiện `Có dùng ()` (đọc sai khóa `for_loops`/`while_loops` → `for_count`/`while_count`).
- `backend/schemas.py` + `GET /api/exercises/{id}`: thêm `has_passed` (chỉ `true` khi chính sinh viên đang đăng nhập có lượt `submit` đạt; vai trò khác luôn `false`; lỗi DB không làm hỏng việc xem đề). Quyền thật vẫn do `/api/tutor/chat` quyết định từ DB.
- `StudentIDE.jsx`: `Chạy thử` và `Hỏi Gia sư AI` xóa `starRationale` → không còn hiện nhầm thẻ "Sao tự lực lượt nộp này" của lần nộp trước; `starsEarned` không còn mặc định 3 (đặt `null`, đặt lại khi đổi bài).
- `PythonicReviewModal.jsx`: dòng sao chỉ hiện khi vừa có lượt nộp đạt trong phiên (trước đây hiện 3 sao mặc định dù bài chỉ được 1⭐ — phát hiện khi kiểm tra trình duyệt).
- `index.css`: Light mode có luật cho `hover:bg-slate-800/700` → nút 👍/👎 rê chuột ra nền sáng `rgb(220,229,222)`, chữ tối (đã đo bằng computed style).
- `StudentProfileModal.jsx`: trạng thái lỗi tải (`role="alert"`) + nút **Thử lại**, không giữ số liệu cũ, ẩn bộ đếm khi lỗi; nhãn dạng lỗi `syntax_or_runtime` đổi thành "chủ yếu không đạt kiểm thử nào (lỗi cú pháp/ngoại lệ hoặc sai toàn bộ kết quả)" vì nhóm này thực chất là "0 kiểm thử đạt".
- S8a offline: `mcp_client.get_code_structure_summary()` (gọi tool MCP `analyze_code_ast`, trả "" nếu lỗi) → `/api/tutor/chat` truyền `ast_summary` của **code đã nộp** khi `chat_scope == "code_review"`; `llm_service.build_offline_code_review_reply()` trả lời tất định: nói rõ là về code đã nộp, tóm tắt cấu trúc, câu hỏi tự kiểm, không chép lại mã; có trích đoạn KB kèm nguồn nếu khớp, ngược lại `knowledge_status="not_applicable"`. Chi phí: thêm một lần mở tiến trình MCP cho mỗi tin nhắn chat sau khi đạt.
- `backend/test_backend_e2e.py`: thêm `init_db()` (kịch bản dùng `ASGITransport`, không chạy `lifespan`, nên trước đây chỉ chạy được trên DB đã có bảng).
- `docs/PILOT_KIT.md`: A1 ghi kết quả kiểm chứng DB mới tinh + nhắc đăng xuất/cửa sổ ẩn danh; G1 cập nhật S1, S4, S8a cho khớp hành vi offline.

**Kiểm chứng (mỗi bộ một DB tạm riêng)**
- `compileall` thoát mã 0. Unittest: `test_thesis_upgrade` **37/37** (thêm 3 test), Phase 16 6/6, Phase 17 5/5, QA authorization 9/9. Replay Phase 17 6/6. Benchmark không đổi: guard phát triển rò rỉ 0/30, tập giữ riêng rò rỉ 4/14 (HA04, HA07, HA08, HA11); RAG hit@3 36/38, no-source 13/14.
- Phân hệ cũ: `mcp_server.test_mcp_server` 8/8; `backend.test_backend_e2e` 6/6 **sau hai lần sửa** (lần đầu thất bại vì hồi quy `has_passed` do chính phiên này gây ra, lần hai vì kịch bản thiếu `init_db()`); `test_phase8_chat.py` 7/7; `test_phase10_gamification.py` 6/6; `test_phase12_classroom_exam.py` 7/7. Hai module đầu là script, không chạy được bằng `py -m unittest` ("NO TESTS RAN"). Chưa chạy lại: `test_phase5/9/13_14/15_3/15_4`.
- Frontend: `test:theme` 3/3; `vite build` thành công (1697 module, cảnh báo chunk > 500 kB như cũ).
- DB mới tinh (`init_db()`): có 3 tài khoản demo, 5 bài, lớp mẫu đã gán bài và ghi danh `student`, 0 lượt nộp → checklist A1 đạt mà không cần tạo thêm.

**Trình duyệt (cặp QA `:8001/:5174`, DB tạm mới, offline, dữ liệu giả lập do chính phiên tạo)**
- Trình tự S1–S8a của Pilot Kit chạy đúng đáp án G1: chat mở sẵn; S1 có nguồn nội bộ; S2 "không có tài liệu nội bộ phù hợp"; S3 chuyển hướng sang `Hỏi Gia sư AI`; S4 ba mức + 👍 lưu được, không hiện thẻ sao; S5 1⭐ (đã dùng Mức 3); S6 vẫn 1⭐, ghi là ôn tập; S8a nói về code đã nộp bằng tóm tắt cấu trúc; sau `Chạy thử` thẻ sao biến mất.
- Dark: `StudentProfileModal` (trạng thái `limited`, ca lỗi lặp lại thật 2/2 lượt chưa đạt, trạng thái lỗi mạng + Thử lại phục hồi được) và `PythonicReviewModal`. Light: hover 👍/👎.
- Giảng viên (dark, desktop + mobile 375px): `Góc nhìn sư phạm` ở trạng thái mẫu nhỏ ("Mẫu nhỏ · chỉ mô tả"); bảng 👍/👎; danh mục KB; trạng thái lỗi mạng của cả ba panel (tắt backend QA) + Thử lại phục hồi được. Không tràn ngang; lỗi console duy nhất là các request 500 trong lúc cố ý tắt backend.
- **Chưa xem / giới hạn:** không chạy với LLM thật (khóa phạm vi chat S1.4 và giải thích từng dòng ở S8a phụ thuộc prompt, chưa kiểm chứng); Light mode chỉ xem lại phần hover; ca sinh viên ở mobile không xem lại trong phiên này (đã xem ở 5.0); mới 1 sinh viên giả lập nên chưa thấy trạng thái `sufficient` của lớp trên giao diện.

**Còn lại (việc của con người)**
1. Chạy pilot thật theo `docs/PILOT_KIT.md` (2–3 người) và ghi quan sát mô tả — chưa có bằng chứng nào về hiệu quả học tập.
2. Xem lại và quyết định Git commit (toàn bộ thay đổi v5.3 vẫn chưa commit; `frontend/dist` sinh ra khi build).
3. Tùy chọn: thử S1–S8 với LLM thật trên dữ liệu giả lập; chạy lại `test_phase5/9/13_14/15_3/15_4`.
