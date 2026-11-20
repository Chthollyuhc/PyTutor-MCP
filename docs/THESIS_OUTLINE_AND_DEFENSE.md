# Dàn ý khóa luận và chuẩn bị bảo vệ

> **Bản nháp do trợ lý AI soạn ngày 13/11/2026.** Dàn ý bám khung chung của bốn khóa luận Trường Công nghệ – NEU đã bảo vệ có trong thư mục dự án (5 chương: giới thiệu → tổng quan/cơ sở lý thuyết → phân tích thiết kế → kết quả → kết luận; 80–140 trang). Sinh viên cần đối chiếu với mẫu trình bày chính thức của Khoa và ý kiến giảng viên hướng dẫn; tài liệu này không thay thế hai nguồn đó.

## Phần 1. Câu chủ đề của khóa luận

Nên viết được một câu mà mọi chương đều phục vụ. Gợi ý:

> *Khóa luận xây dựng một hệ thống thực hành Python trong đó phản hồi của AI được ràng buộc bằng các nguyên tắc sư phạm (giàn giáo ba mức, phản hồi dựa trên bằng chứng, không đưa lời giải), và các ràng buộc đó được **cài đặt thành cơ chế kiểm tra được** thay vì chỉ là lời dặn trong prompt.*

Điểm khác biệt nằm ở vế sau. Rất nhiều hệ thống "nhờ AI gợi ý"; ít hệ thống đo xem AI có thật sự tuân thủ hay không, và báo cáo cả những chỗ nó không tuân thủ.

**Điều không nên lấy làm điểm nhấn:** giao thức MCP (chỉ là lớp tích hợp công cụ), số lượng tính năng, bảng xếp hạng, và phân hệ thi (đang ẩn; đề tài phục vụ người học, không phục vụ kiểm tra).

## Phần 2. Dàn ý đề xuất

| Chương | Nội dung | Số trang gợi ý | Nguyên liệu có sẵn trong repo |
|---|---|---:|---|
| Mở đầu | Bối cảnh, câu chủ đề, cấu trúc khóa luận | 2 | `PRODUCT.md` |
| **1. Giới thiệu đề tài** | 1.1 Lý do chọn đề tài · 1.2 Sự cần thiết · 1.3 Yêu cầu nghiệp vụ (người học, giảng viên) · 1.4 Yêu cầu kỹ thuật · 1.5 Mục tiêu, phạm vi, phương pháp · 1.6 Đóng góp của đề tài | 8–10 | `PLAN.md`, `PRODUCT.md` |
| **2. Cơ sở lý thuyết và tổng quan** | 2.1 Dạy và học lập trình cho người mới: khó khăn điển hình · 2.2 Cơ sở sư phạm: giàn giáo, phản hồi hình thành, tìm kiếm trợ giúp, tự giải thích · 2.3 Hệ thống gia sư thông minh và mô hình người học · 2.4 Mô hình ngôn ngữ lớn trong giáo dục lập trình: cơ hội và rủi ro lộ lời giải · 2.5 Sinh có truy xuất (RAG) · 2.6 Các hệ thống liên quan (chấm bài tự động, trợ lý AI cho lớp lập trình) và khoảng trống · 2.7 Công nghệ sử dụng | 22–28 | `docs/PEDAGOGICAL_FOUNDATIONS.md` (**phải tự kiểm tra trích dẫn**), `docs/PHASE_17_METRICS_AND_BENCHMARK.md` |
| **3. Phân tích và thiết kế** | 3.1 Tác nhân và use case · 3.2 Thiết kế sư phạm: ba hành động IDE, ba mức gợi ý, bốn chiến lược thích ứng, luật sao, khóa phạm vi trò chuyện (bảng nguyên tắc → quyết định thiết kế) · 3.3 Kiến trúc: frontend, backend điều phối, tiến trình công cụ · 3.4 Luồng chấm bài và sinh phản hồi (biểu đồ tuần tự) · 3.5 Các lớp kiểm soát đầu ra: bộ lọc Mức 1–2, che logic Mức 3, phản hồi tất định khi đạt · 3.6 Truy xuất tri thức và tài liệu theo lớp · 3.7 Mô hình người học và chỉ số, kèm `data_status` · 3.8 Phân tích cho giảng viên: nhóm quá trình học · 3.9 Thiết kế cơ sở dữ liệu · 3.10 Phân quyền và bảo vệ dữ liệu người học | 30–38 | `AI_HANDOFF_CONTEXT.md` §3–§9, §18; `CLAUDE.md` §2b; `docs/PROCESS_GROUPS.md`; `docs/KB_UPLOAD_GUIDE.md` |
| **4. Kết quả và đánh giá** | Theo `docs/THESIS_CHAPTER4_DRAFT.md` | 22–28 | Bản nháp đã có số liệu |
| | *Bản nháp Chương 1 và 5: `docs/THESIS_CHAPTER1_AND_5_DRAFT.md`; Chương 3: `docs/THESIS_CHAPTER3_DRAFT.md`* | | |
| **5. Kết luận** | Kết quả đạt được so với mục tiêu ở 1.5 · Hạn chế · Hướng phát triển | 3–4 | Mục 4.9, 4.10 của bản nháp |
| Tài liệu tham khảo | Chỉ ghi tài liệu đã đọc bản gốc | — | — |
| Phụ lục | Rubric chấm phản hồi; bộ tài liệu pilot; ví dụ phản hồi nguyên văn; hướng dẫn cài đặt | — | `docs/PILOT_KIT.md`, `docs/REAL_LLM_EVALUATION.md` |

### Gợi ý cho mục 1.6 "Đóng góp của đề tài"

Viết ở mức đã có bằng chứng, không hơn:

1. Một thiết kế phản hồi ba mức có khung "đang ở đâu → bằng chứng → bước kế tiếp", cài đặt cho cả nhánh có mô hình ngôn ngữ và nhánh tất định.
2. Các cơ chế kiểm tra được cho ràng buộc "không đưa lời giải": bộ lọc đầu ra, khóa phạm vi trò chuyện, che logic khung mã Mức 3 — kèm phép đo, **bao gồm cả kết quả chưa tốt** trên tập giữ riêng.
3. Mô hình người học và phân tích cho giảng viên luôn gắn cỡ mẫu và trạng thái dữ liệu, tránh kết luận vượt bằng chứng.
4. Bộ công cụ đánh giá chạy lại được (kiểm thử, benchmark, đo tải, 22 ca với mô hình thật).

Không viết: "nâng cao kết quả học tập", "hiệu quả hơn ChatGPT", "đã được sinh viên đánh giá cao" khi chưa có dữ liệu.

## Phần 3. Câu hỏi phản biện có thể gặp

Mỗi câu kèm hướng trả lời và nơi lấy bằng chứng. Hãy tập trả lời bằng lời của mình.

**Nhóm A — Giá trị của đề tài**

1. *"Hệ thống này khác gì việc sinh viên hỏi thẳng ChatGPT?"*
   Trợ lý đa dụng tối ưu cho việc trả lời; hệ thống này tối ưu cho việc người học tự làm được. Ba khác biệt cụ thể: người học chọn mức trợ giúp và hệ thống không vượt mức đó; có lớp kiểm soát chặn lời giải ngay cả khi mô hình "lỡ" đưa ra (ca H3, H4 ở mục 4.5.3); phản hồi dựa trên kết quả kiểm thử thật của bài làm chứ không dựa trên mô tả của người hỏi.

2. *"Sinh viên vẫn có thể mở ChatGPT ở tab khác. Vậy chặn lời giải để làm gì?"*
   Đúng, và đề tài không cố ngăn việc đó: đây là công cụ cho người **muốn học**, không phải công cụ giám sát. Mục tiêu của việc không đưa lời giải là để công cụ không tự làm hỏng việc học của người đang dùng nó đúng mục đích.

3. *"Vì sao không có chức năng thi và chống gian lận như các hệ thống chấm bài khác?"*
   Vì đó là bài toán khác. Hệ thống chấm bài trả lời "bài này đúng chưa"; đề tài trả lời "người học cần gì để tự sửa". Thêm giám sát sẽ làm người học ngại thử–sai, ngược với mục tiêu.

4. *"MCP đóng vai trò gì? Có cần thiết không?"*
   Là lớp tích hợp công cụ (chạy kiểm thử, phân tích cú pháp, truy vết) tách khỏi backend. Nó không phải phương pháp dạy học và không được coi là đóng góp sư phạm. Cái giá là mỗi lời gọi mở một tiến trình mới, đo được ở mục 4.6.

**Nhóm B — Bằng chứng**

5. *"Em có bằng chứng gì là hệ thống giúp sinh viên học tốt hơn?"*
   Chưa có, và khóa luận nói rõ điều đó. Bằng chứng hiện có thuộc hai loại: hệ thống làm đúng thiết kế (kiểm thử, benchmark) và mô hình thật phần lớn tuân thủ ràng buộc (22 ca). Chứng minh hiệu quả học tập cần nghiên cứu có đối chứng, nằm ngoài phạm vi. **[Nếu đã chạy pilot: nêu quan sát mô tả, không khái quát.]**

6. *"Benchmark do chính em soạn thì có ý nghĩa gì?"*
   Ý nghĩa hạn chế, và được báo cáo như vậy: tập phát triển chỉ là kiểm tra hồi quy. Vì thế mới có tập giữ riêng, soạn sau khi đóng băng luật và không dùng để chỉnh. Tập đó cho kết quả xấu hơn hẳn với bộ lọc Mức 1–2 (lọt 4/14) và khóa luận giữ nguyên con số đó.

7. *"Bộ lọc lọt 4/14, chặn chèn lệnh chỉ 1/10. Vậy có dùng được không?"*
   Bộ lọc là lớp thứ hai sau chỉ dẫn trong prompt, không phải lớp duy nhất. Trong 22 ca với mô hình thật, các kiểm tra tự động (dạng heuristic, chưa chấm tay) không ghi nhận ca nào lời giải tới được người học ở Mức 1–2 hay trong trò chuyện; một ca bị bộ lọc chặn (H3). Hướng khắc phục: phân tích cú pháp thay cho biểu thức chính quy, hoặc dùng mô hình thứ hai để thẩm định.

8. *"Ngưỡng 3 bài, công thức sao, sáu nhóm quá trình học lấy từ đâu?"*
   Là quy ước vận hành, chưa hiệu chuẩn; giao diện và tài liệu đều ghi rõ. Chúng được thiết kế để dễ thay khi có dữ liệu thật.

9. *"22 ca là quá ít, và mô hình trả lời mỗi lần một khác."*
   Đồng ý, và còn một điểm nữa: ca R1 bị bộ lọc chặn ở 2 trong 3 lần chạy với gần như cùng prompt, nên một lần chạy không đại diện cho hành vi ổn định. 22 ca chỉ để phát hiện kiểu lỗi (đã phát hiện ba kiểu); muốn ước lượng tỷ lệ cần chạy nhiều lần và báo cáo số lần xảy ra trên tổng số lần.

**Nhóm C — Sư phạm**

10. *"Trừ sao khi xin gợi ý có khiến sinh viên không dám xin gợi ý?"*
    Đây là rủi ro có thật của thiết kế. Giảm nhẹ: Mức 1 không trừ sao; số lần nộp không trừ sao; sao không phải điểm học phần và giao diện nói rõ. Phiếu pilot có câu hỏi riêng về việc này (F1 câu 12).

11. *"Vì sao ba mức mà không phải hai hay năm?"*
    Ba mức ứng với ba loại trợ giúp khác bản chất: định hướng khái niệm, khoanh vùng lỗi, cấu trúc lời giải. Số mức chưa được kiểm chứng thực nghiệm.

12. *"Khi không có mô hình AI thì hệ thống còn giá trị không?"*
    Còn: phản hồi tất định vẫn theo khung hình thành và chỉ nêu điều quan sát được. Nó kém cụ thể hơn và tự nói rõ giới hạn của mình.

13. *"Che logic ở Mức 3 có làm khung trở nên vô dụng không?"*
    Có thể. Phép đo hiện có chỉ cho biết lời giải không lọt (0/24, 0/16), chưa cho biết khung còn đủ dùng. Đây là câu hỏi cho pilot (F1 câu 13).

**Nhóm D — Kỹ thuật và dữ liệu**

14. *"Lớp 50–100 sinh viên dùng cùng lúc thì sao?"*
    Đã đo đến 20 yêu cầu đồng thời trên một máy: không lỗi, P95 khoảng 6,3 giây cho nộp bài. Điểm nghẽn là mở tiến trình công cụ cho mỗi lời gọi; hướng khắc phục là giữ kết nối dùng chung. Chưa đo trên máy chủ.

15. *"Độ trễ của mô hình thật trung vị 12 giây có chấp nhận được không?"*
    Là hạn chế. Giảm nhẹ: `Chạy thử` không gọi mô hình; nộp đạt dùng phản hồi tất định. Hướng khắc phục: phản hồi dạng luồng, mô hình nhanh hơn.

16. *"Dữ liệu sinh viên có bị gửi cho bên thứ ba không?"*
    Mã nguồn bài làm được gửi cho nhà cung cấp mô hình khi xin gợi ý; phân tích lớp cho giảng viên chỉ gửi số liệu tổng hợp, không có mã hay danh tính. Mọi thử nghiệm trong khóa luận dùng dữ liệu giả lập. Triển khai thật cần thỏa thuận về dữ liệu.

17. *"Kho tri thức lấy từ đâu?"*
    Tài liệu nội bộ do dự án soạn, chưa phải giáo trình NEU; giảng viên có thể tải tài liệu riêng cho lớp mình.

18. *"Chạy mã của sinh viên trên máy chủ có an toàn không? Mật khẩu lưu thế nào?"*
    Chưa an toàn để triển khai, và khóa luận nói rõ: mã chạy trong tiến trình con chỉ có giới hạn thời gian 5 giây, chưa cô lập tệp, bộ nhớ, mạng. Mật khẩu của cơ sở dữ liệu mới được băm bằng PBKDF2 (có muối, 200.000 vòng) nhưng cơ sở dữ liệu cũ vẫn chấp nhận và có thể đang lưu dạng văn bản thường; khóa ký JWT mặc định chỉ bị cảnh báo. Hệ thống là bản mẫu nghiên cứu chạy với tài khoản mẫu. Hướng khắc phục: chạy mã trong vùng chứa hoặc công cụ cô lập chuyên dụng, chuyển mật khẩu cũ sang dạng băm, bắt buộc đặt khóa ký. **[Nếu đã sửa trước khi bảo vệ thì cập nhật câu trả lời.]**

19. *"Em dùng AI để viết mã ở mức nào?"*
    **[SV tự trả lời trung thực.]** Nên chuẩn bị để giải thích được mọi quyết định thiết kế và đọc–sửa được bất kỳ đoạn mã nào hội đồng chỉ vào.

**Nhóm E — Mô hình người học**

20. *"Vì sao không dùng BKT hay IRT cho mô hình người học?"*
    Cả hai cần dữ liệu để ước lượng tham số; đề tài chưa có dữ liệu người học thật, chỉ khoảng 5 bài mẫu và pilot chưa chạy, nên tham số ước lượng sẽ không có nghĩa. Mô hình thứ bậc (4 trạng thái cho 6 đơn vị kiến thức) kèm câu giải thích giúp người học và giảng viên kiểm tra được "vì sao", điều mà xác suất ẩn khó làm. BKT là hướng phát triển khi có đủ dữ liệu (mục 4.10). Đề tài không tự nhận là Knowledge Tracing.

21. *"'Thích ứng' trong tên đề tài nghĩa là gì? Có chứng minh học tốt hơn không?"*
    Nghĩa là phản hồi thay đổi theo hồ sơ người học theo luật tường minh, đo được: trên 120 ô phát lại tổng hợp, chính sách khác đối chứng bỏ qua mô hình ở 51 ô (42,5%), mức gợi ý yêu cầu giữ 120/120, cổng dữ liệu đúng 30/30 (mục 4.4.4). Đây là hành vi chính sách, **không** phải kết quả học tập: chưa có pilot, chưa dùng mô hình ngôn ngữ thật, và không tuyên bố học tốt hơn.

22. *"Các ngưỡng (2 bài, tự lực 70, 45, 80...) lấy từ đâu?"*
    Là quy ước vận hành do dự án chọn, chưa hiệu chuẩn bằng dữ liệu thực; được ghi rõ trong `THRESHOLDS`, trong câu miễn trừ của mô hình hiển thị cho người học và ở mục hạn chế. Cổng dữ liệu (chỉ dùng khi đủ bằng chứng từ bài khác) giảm rủi ro kích hoạt sai khi dữ liệu thưa. Hiệu chuẩn là việc cần làm sau pilot.

## Phần 4. Kịch bản demo 7 phút

1. (1') Đăng nhập sinh viên, mở Bài 02, viết sai có chủ ý, bấm `Chạy thử` → bảng kiểm thử.
2. (2') `Hỏi Gia sư AI` Mức 1 → Mức 2 trên cùng bài: chỉ ra khung "đang ở đâu → bằng chứng → bước kế tiếp".
3. (1') Mức 3: khung mã có `...`; nói về ca H4 và bước che.
4. (1') Sửa đúng, `Nộp bài` → thẻ lý do sao.
5. (1') Trò chuyện: một câu có nguồn, một câu "không có tài liệu phù hợp".
6. (1') Đăng nhập giảng viên → nhóm quá trình học, ghi chú cỡ mẫu.

Chuẩn bị sẵn bản quay màn hình phòng khi mạng hoặc mô hình chậm; có thể demo ở chế độ offline (`PYTUTOR_DISABLE_LLM=1`) để phản hồi tức thì và ổn định.

## Phần 5. Thứ tự việc nên làm trước khi nộp

1. Chạy pilot (`docs/PILOT_KIT.md`), kể cả chỉ 5–10 người.
2. Chấm tay 22 ca; nếu được, nhờ một người chấm độc lập.
3. Đọc bản gốc các tài liệu trong `docs/PEDAGOGICAL_FOUNDATIONS.md`, loại cái không kiểm chứng được.
4. Viết Chương 2 và 3 theo dàn ý; Chương 4 từ bản nháp.
5. Chụp ảnh màn hình trên cơ sở dữ liệu sạch.
6. Tập trả lời Phần 3 thành tiếng.
