# Cơ sở sư phạm của các quyết định thiết kế PyTutor

> **Trạng thái: bản nháp do trợ lý AI soạn ngày 13/11/2026, dùng làm nguyên liệu cho Chương 2 (cơ sở lý thuyết) và Chương 3 (thiết kế).**
>
> **Về trích dẫn:** các công trình dưới đây được nêu theo trí nhớ của trợ lý và **chưa được đối chiếu với bản gốc**. Trước khi đưa vào khóa luận, sinh viên phải tự tìm từng tài liệu, kiểm tra tên tác giả, năm, tên bài, nơi công bố, và đọc phần liên quan để chắc rằng nó thật sự nói điều được gán cho nó. Công trình nào không tìm được bản gốc thì bỏ. Tài liệu này không phải là danh mục tham khảo.
>
> **Về mức khẳng định:** mỗi dòng nói rằng thiết kế *dựa theo* một nguyên tắc, không nói rằng PyTutor đã *chứng minh* nguyên tắc đó có hiệu quả. Hệ thống chưa có dữ liệu người học thật (xem `docs/THESIS_CHAPTER4_DRAFT.md` mục 4.8).

## 1. Lập trường của đề tài

PyTutor là hệ thống **hỗ trợ người muốn học lập trình**, không phải hệ thống kiểm tra người học. Từ lập trường đó có ba hệ quả thiết kế:

1. Thước đo thành công của một phản hồi là *người học tự làm được bước kế tiếp*, không phải bài được chấm đúng nhanh hơn.
2. Thử–sai không bị phạt: `Chạy thử` không ghi vào hồ sơ chính thức; số lần nộp không trừ sao.
3. Giảng viên nhận thông tin để *biết ai cần giúp*, không phải để xếp hạng hay giám sát.

## 2. Bảng ánh xạ nguyên tắc → quyết định thiết kế → nơi cài đặt

| # | Nguyên tắc | Quyết định thiết kế trong PyTutor | Nơi cài đặt / kiểm thử | Công trình cần đối chiếu |
|---|---|---|---|---|
| 1 | **Giàn giáo trong vùng phát triển gần:** hỗ trợ vừa đủ để người học làm được điều chưa tự làm được, rồi rút dần | Ba mức gợi ý tăng dần độ cụ thể; khi bài đạt thì chuyển sang câu hỏi tự kiểm thay vì gợi ý tiếp | `prompt_templates.py`, `build_pass_feedback`; `FormativeFeedbackTests` | Vygotsky (1978), *Mind in Society*; Wood, Bruner & Ross (1976), "The role of tutoring in problem solving" |
| 2 | **Người học kiểm soát mức trợ giúp;** cho quá nhiều trợ giúp làm mất cơ hội học, cho quá ít gây bế tắc (thế lưỡng nan trợ giúp) | Hệ thống không tự nâng mức gợi ý vượt mức người học yêu cầu; chiến lược thích ứng chỉ đổi cách gợi ý | `adaptive_policy.select_hint_strategy`; replay 6/6 giữ nguyên mức | Koedinger & Aleven (2007), "Exploring the assistance dilemma in experiments with cognitive tutors" |
| 3 | **Phản hồi hình thành trả lời ba câu hỏi:** đang hướng tới đâu, đang ở đâu, bước kế tiếp là gì | Khung "đang ở đâu → bằng chứng → một bước kế tiếp" cho cả phản hồi LLM và phản hồi offline | Khối "KHUNG PHẢN HỒI HÌNH THÀNH" trong prompt; `generate_rule_based_fallback` | Hattie & Timperley (2007), "The power of feedback"; Shute (2008), "Focus on formative feedback" |
| 4 | **Phản hồi phải dựa trên bằng chứng quan sát được**, cụ thể và hướng vào nhiệm vụ, không vào con người | Phản hồi offline chỉ nêu điều thấy từ kiểm thử/AST và tự ghi rõ giới hạn; nhãn hồ sơ không vượt bằng chứng | `generate_rule_based_fallback`; `StudentModelSyncTests` | Shute (2008); Nicol & Macfarlane-Dick (2006), "Formative assessment and self-regulated learning" |
| 5 | **Tự giải thích giúp hiểu sâu hơn** so với chỉ đọc lời giải | Sau khi đạt, hệ thống hỏi người học tự giải thích trường hợp biên; Mức 1 là câu hỏi gợi mở | `_self_check_questions`, `build_pass_feedback` | Chi, Bassok, Lewis, Reimann & Glaser (1989), "Self-explanations" |
| 6 | **Lạm dụng gợi ý** (xin đến khi có đáp án) làm giảm việc học; hệ thống nên khuyến khích tìm trợ giúp đúng lúc | Sao tự làm theo mức gợi ý cao nhất trước lần đạt đầu; có thẻ giải thích quy tắc; nộp lại sau khi đạt không tăng sao | `calculate_autonomy_stars`, `explain_autonomy_stars`; `EndpointTests` | Aleven, Stahl, Schworm, Fischer & Wallace (2003), "Help seeking and help design in interactive learning environments" |
| 7 | **Không đưa lời giải trực tiếp** là yêu cầu trung tâm của trợ lý AI cho người học lập trình | Bộ lọc đầu ra ở Mức 1–2 và trò chuyện; khóa phạm vi trò chuyện trước khi nộp đạt; che logic khung mã Mức 3 | `guardrails.py` (`check_student_output`, `enforce_level3_skeleton`); `test_level3_scaffold` | Liffiton, Sheese, Savelka & Denny (2023), "CodeHelp"; Kazemitabaar và cộng sự (2024), "CodeAid" |
| 8 | **Vật lộn có ích khác với mắc kẹt:** thử nhiều mà vẫn tiến là tốt; thử nhiều mà không tiến cần can thiệp | Nhóm quá trình học tách "đang tiến triển" khỏi "mắc kẹt" bằng xu hướng số kiểm thử đạt; chiến lược `recurring_difficulty` đổi hướng sang chạy từng bước | `classify_learning_process`; `docs/PROCESS_GROUPS.md` | Beck & Gong (2013), "Wheel-spinning: Students who fail to master a skill"; Kapur (2008), "Productive failure" |
| 9 | **Nhìn thấy trạng thái chương trình** giúp người mới học hình thành mô hình máy đúng | Chạy từng bước, xem giá trị biến theo dòng lệnh; gợi ý Mức 2 trỏ người học tới công cụ này | `mcp_server/tracer.py`, `ExecutionVisualizerModal.jsx` | Sorva (2013), "Notional machines and introductory programming education"; Guo (2013), "Online Python Tutor" |
| 10 | **Mô hình người học mở:** cho người học thấy hệ thống đang hiểu gì về mình, kèm độ tin cậy | Hồ sơ hiện `data_status` và cỡ mẫu; dữ liệu ít thì nói "chưa đủ dữ liệu" | `compute_student_model` (hai bản đồng bộ) | Bull & Kay (2007), "Student models that invite the learner in: The SMILI open learner modelling framework" |
| 10b | **Đơn vị kiến thức và mô hình mở theo khái niệm:** chia nội dung thành khái niệm nhỏ và cho người học thấy hệ thống nghĩ gì về từng khái niệm, kèm lý do | 6 KC cố định, trạng thái thứ bậc kèm câu "vì sao"; dòng "Vì sao nhận gợi ý này"; chính sách chỉ dùng bằng chứng từ bài khác và khi đủ dữ liệu; mức gợi ý vẫn do người học chọn | `pytutor_shared/learner_model.py`, `adaptive_policy.py`; `test_learner_model`, `evaluate_learner_model_policy.py` | Bull & Kay (2007) (trích dẫn chưa đối chiếu); mô hình là heuristic, không phải BKT/IRT |
| 11 | **Câu trả lời của AI cần truy được nguồn;** nói "không biết" tốt hơn bịa | Trò chuyện trả nguồn hoặc `no_source`; không bao giờ gắn nguồn khi truy xuất rỗng | `rag/retriever.py` (`MIN_RELEVANCE`); `RagSourceTests` | Lewis và cộng sự (2020), "Retrieval-augmented generation for knowledge-intensive NLP tasks" |
| 12 | **Phân tích học tập phải thận trọng về diễn giải** và bảo vệ người học | Chỉ số gắn cỡ mẫu và ghi chú giới hạn; mô hình ngôn ngữ chỉ nhận số liệu tổng hợp của lớp, không nhận mã hay danh tính | `get_class_insights`, `/api/instructor/ai/class-chat`; `test_qa_authorization` | **[SV tự chọn nguồn về đạo đức phân tích học tập]** |

## 3. Những điều thiết kế này chưa trả lời được

1. Ba mức gợi ý có phải là số mức phù hợp không, và ranh giới giữa các mức có đúng với người học thật không.
2. Luật sao có khiến người học *né* xin gợi ý khi thật sự cần hay không. Đây là rủi ro đã biết của mọi cơ chế "trừ điểm khi xin trợ giúp"; cần quan sát trong pilot (câu hỏi gợi ý: "Bạn có lúc nào muốn xin gợi ý nhưng không xin vì sợ mất sao không?").
3. Bước che logic Mức 3 có để lại khung đủ dùng hay làm người học bế tắc hơn.
4. Các ngưỡng của nhóm quá trình học có tách đúng "vật lộn có ích" với "mắc kẹt" hay không.
5. Phản hồi offline (không chỉ ra dòng lệnh) có đủ giúp người học đi tiếp hay không.
6. Các KC gán bằng từ khóa và ngưỡng trạng thái (2 bài, tự làm 70) có phản ánh đúng mức vững của người học thật không; việc "thích ứng" theo mô hình có giúp học tốt hơn hay không (chưa đo, mới có phát lại tổng hợp).

Mỗi câu trên là một câu hỏi quan sát cụ thể cho pilot, và là hướng phát triển trung thực để nêu ở chương kết luận.

## 4. Gợi ý dùng trong khóa luận

- **Chương 2:** trình bày các nguyên tắc 1–8 như cơ sở lý thuyết, sau khi đã đọc bản gốc.
- **Chương 3:** dùng bảng ở mục 2 (bỏ cột cuối, thay bằng số trích dẫn) làm bảng "nguyên tắc → quyết định thiết kế".
- **Chương 4/5:** dùng mục 3 làm phần hạn chế và hướng nghiên cứu tiếp.
- **Khi bảo vệ:** câu "hệ thống của em khác gì hỏi thẳng ChatGPT?" có câu trả lời ở các dòng 2, 6, 7 và 11.
