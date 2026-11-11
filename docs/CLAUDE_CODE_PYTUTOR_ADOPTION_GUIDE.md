# Claude Code cho PyTutor-MCP — hướng dẫn áp dụng

> Mục đích: chắt lọc các ý có ích từ nguồn người dùng gửi và biến chúng thành quy trình làm việc phù hợp repo PyTutor-Thesis/PyTutor-MCP. Đây không phải bản dịch toàn bộ repo tham khảo hay lệnh cài mọi plugin.
>
> **Giới hạn nguồn:** Nội dung bài Facebook về chia session và định tuyến model được người dùng dán trực tiếp trong hội thoại; nội dung đó được tóm tắt như nguồn do người dùng cung cấp, không phải nội dung tôi truy xuất độc lập từ Facebook. Năm Reels và bài đăng Facebook còn lại vẫn không truy cập/xác minh được. Archify và Claude Code được đối chiếu với trang GitHub/tài liệu chính thức tại thời điểm cập nhật; khả năng, phiên bản, tên model và giá có thể đổi.

## 1. Kết luận ngắn

PyTutor phù hợp với quy trình Claude Code theo vòng lặp **Hiểu yêu cầu → Plan theo lát cắt dọc → Triển khai có kiểm thử → Review → Xác minh → Cập nhật handoff**. Dùng repo GitHub làm danh mục ý tưởng, không phải bộ quy tắc bắt buộc: nó tập hợp kiến thức về `CLAUDE.md`, skills, commands, hooks, MCP, context và workflows, đồng thời liên kết tới nhiều hướng dẫn chính thức lẫn cộng đồng. Repo cũng tự liệt kê các workflow khác nhau; điều đó không đồng nghĩa phải cài hết hoặc mọi lời khuyên đều phù hợp đồ án này.

## 2. Điều rút ra từ repo tham khảo

| Ý trong repo tham khảo | Áp dụng vào PyTutor |
|---|---|
| Chốt yêu cầu/plan trước, triển khai theo phase có cổng kiểm thử | Giữ cách làm phase hiện có trong `PLAN.md`; từng phase cần tiêu chí nghiệm thu và test cụ thể trước khi sửa. |
| Làm theo vertical slice thay vì hoàn tất DB rồi mới tới API/UI | Với thay đổi nghiệp vụ, triển khai một luồng xuyên suốt nhỏ: dữ liệu/schema → API/quyền → giao diện → kiểm thử; tiếp tục các lát cắt sau khi lát đầu chạy được. |
| Dùng `CLAUDE.md` và rules theo phạm vi để giữ project context | Tạo `CLAUDE.md` ngắn làm trang vào; kiến trúc và lịch sử dài vẫn ở `AI_HANDOFF_CONTEXT.md`, phase status ở `PLAN.md`, quy tắc chuyên biệt đặt trong `.claude/rules/`. |
| Skill/command nên đóng gói quy trình lặp lại | Chỉ tạo skill/command riêng cho tác vụ lặp, ví dụ triển khai phase, QA cô lập DB, chuẩn bị báo cáo pilot; không tạo skill cho một việc đơn lẻ. |
| Quản lý context/session có chủ đích | Mỗi mục tiêu lớn hoặc không liên quan nên có phiên riêng. Khi tiếp tục phiên dài, ghi tóm tắt file đã đổi, test đã chạy và việc còn lại; dùng `/compact` có chỉ dẫn hoặc bắt đầu session mới khi chuyển mục tiêu. |
| Dùng screenshot và browser automation để debug UI | Khi thay giao diện, chạy app trên dữ liệu demo/kiểm thử, dùng Playwright kiểm tra luồng student/instructor, lỗi console và ảnh desktop/mobile. Build thành công không thay thế kiểm tra giao diện. |
| Quyền có thể cấu hình tường minh; tránh bỏ qua toàn bộ permission | Giữ xác nhận cho xóa/ghi đè, thao tác DB thật, secrets và external services; chỉ allowlist lệnh kiểm thử/build an toàn đã hiểu. Không dùng chế độ bỏ qua mọi quyền. |
| Review độc lập/cross-model có thể phát hiện lỗi | Chỉ dùng review bổ sung cho auth, phân quyền lớp, migration, dữ liệu cá nhân, Anti-Spoil hoặc thay đổi lớn; review là bước phụ, test và bằng chứng vẫn là tiêu chí chính. |

Repo tham khảo còn đưa ra nhiều plugin, skill collections, agent collections, loop và workflow orchestration. Đó là danh mục để khám phá, không phải danh sách cài mặc định. Các ngưỡng context dạng phần trăm/số token, số lượng prototype cao, subagent/agent-team cho mọi việc, hoặc vòng lặp tự chạy không cần review nên được xem là kinh nghiệm cá nhân; không áp thành luật cho PyTutor nếu chưa chứng minh lợi ích.

## 3. Archify: dùng để giải thích kiến trúc, không điều phối phiên

Archify là skill/tiện ích tạo sơ đồ tương tác và trang giải thích một trang từ yêu cầu hoặc bằng chứng trong repository; repo mô tả các dạng architecture, workflow, sequence, data-flow, lifecycle/state, ERD và class diagram, cùng đầu ra HTML độc lập. Vì vậy, nó có thể giúp PyTutor tạo sơ đồ dễ trình bày cho handoff, báo cáo và bảo vệ đồ án — ví dụ luồng nộp bài, phân quyền lớp, pipeline phản hồi thích ứng và mô hình dữ liệu analytics. Nó **không phải** công cụ chia session hay định tuyến model.

Khuyến nghị áp dụng có chọn lọc:

1. Trước tiên thử tạo một sơ đồ kiến trúc PyTutor nhỏ từ code/tài liệu hiện có, yêu cầu gắn các thành phần với file/API làm bằng chứng; đối chiếu thủ công với code trước khi đưa vào báo cáo.
2. Dùng sơ đồ HTML như artifact giải thích, không làm nguồn chuẩn thay cho `PLAN.md`, `AI_HANDOFF_CONTEXT.md` hay source code.
3. Chỉ cài từ repo chính thức sau khi rà `SKILL.md`, lệnh/script được chạy, phạm vi file đọc/ghi, dependency và license. Không cấp quyền database thật, secrets hoặc dữ liệu sinh viên cho skill; tạo artifact trong thư mục riêng.
4. Giữ lại nếu đầu ra tiết kiệm thời gian đọc/giải thích thực tế; nếu chỉ tạo thêm bước bảo trì, dùng Mermaid/Markdown hiện có là đủ.

Nguồn dự án: [tt-a1i/archify](https://github.com/tt-a1i/archify), [mô tả skill và loại sơ đồ](https://github.com/tt-a1i/archify/blob/main/archify/SKILL.md), [hướng dẫn tạo sơ đồ](https://github.com/tt-a1i/archify/blob/main/docs/authoring-cookbook.md). README/release hiện mô tả Archify là agent-facing skill, không phải workflow manager; tích hợp host và hướng dẫn cài có thể khác nhau, vì vậy cần kiểm tra bản mới nhất trước khi cài.

## 4. Chia session và chọn model theo độ khó/rủi ro

Bài Facebook bạn cung cấp đề xuất ba tầng: model mạnh cho kiến trúc/điều phối/review, model cân bằng cho triển khai, model nhẹ cho tìm kiếm/log/test phụ trợ; đồng thời dùng một session điều phối và các session chuyên trách, tránh chạy quá nhiều phiên cùng lúc. Đây là kinh nghiệm thực hành của tác giả bài viết, không phải benchmark độc lập. Những số liệu so sánh Opus/Sonnet cho sản xuất video và chi phí trong bài không liên quan trực tiếp tới code PyTutor, không được dùng làm dự báo chất lượng hay giá cho dự án.

Nguyên tắc có thể áp dụng là **định tuyến theo năng lực cần thiết, không khóa cứng theo tên model**. Tên model, alias, quyền truy cập và giá thay đổi; kiểm tra lựa chọn hiện có trong tài khoản Claude của bạn khi bắt đầu task. Claude Code hỗ trợ chọn model cho phiên và tiếp tục/khôi phục session; Anthropic cũng mô tả subagent orchestration nhưng cảnh báo việc delegate quá mức có thể gây lãng phí. Mỗi session phụ không nên được giả định là tự kế thừa toàn bộ trao đổi, quyền hay ngữ cảnh của session khác: truyền brief, file liên quan, ranh giới chỉnh sửa và tiêu chí nghiệm thu tường minh.

| Nhu cầu trong PyTutor | Cấp model phù hợp | Ví dụ giao việc |
|---|---|---|
| Quyết định kiến trúc, thay đổi hợp đồng API/schema, bảo mật/RBAC, đánh giá phương pháp Phase 17 | Mạnh / reasoning cao | Đọc tài liệu và code liên quan, nêu lựa chọn/rủi ro, lập plan; review độc lập trước khi merge. |
| Triển khai một lát cắt đã chốt, viết regression test, sửa UI/API có phạm vi rõ | Cân bằng / coding tốt | Chỉ định file/module được sửa, hành vi phải giữ, lệnh test và đầu ra mong muốn. |
| Tìm file/route, tóm tắt log, đối chiếu danh sách test hoặc lập bản đồ repository | Nhanh / chi phí thấp | Trả về đường dẫn và bằng chứng ngắn; không tự sửa code hoặc kết luận lỗi khi chưa tái hiện. |

### Mô hình session an toàn cho PyTutor

- **Một session điều phối** giữ mục tiêu, phạm vi, quyết định nghiệp vụ, trạng thái git và tích hợp cuối. Session này tránh sửa cùng file trong lúc worker đang làm.
- **Tối đa 1–2 worker cùng lúc** khi có hai lát cắt thực sự độc lập (ví dụ audit backend quyền và rà soát giao diện không đụng cùng file). Con số “khoảng ba session” trong bài Facebook là gợi ý cá nhân, không phải giới hạn kỹ thuật phổ quát; với đồ án này hãy ưu tiên ít phiên, dễ review.
- Mỗi worker nhận brief ngắn: mục tiêu, file sở hữu, file không được chạm, hợp đồng/API, test cần chạy, dữ liệu an toàn và cách báo cáo. Worker trả lại file/diff, lệnh test, kết quả và việc còn dang dở.
- Không cho hai worker cùng sửa migration, `PLAN.md`, handoff, cấu hình chung hoặc cùng component. Với thay đổi cần song song, tách worktree/branch nếu workflow hiện tại hỗ trợ; tích hợp tuần tự, kiểm tra diff và chạy lại test sau khi ghép.
- Không song song hóa những task phụ thuộc quyết định chưa chốt (schema, quyền, tiêu chí thích ứng). Không cần tạo session riêng cho một thay đổi nhỏ hoặc một file.
- Dùng session mới khi mục tiêu đổi hẳn hoặc lịch sử đã nhiễu; trước khi chuyển, cập nhật handoff bằng quyết định, file đổi, test chạy và câu hỏi còn mở. Không coi việc mở nhiều cửa sổ là cách tự động chia sẻ memory/context.

Đây tương thích với hướng dẫn chính thức của Claude Code về [chọn/khôi phục phiên qua CLI](https://docs.anthropic.com/en/docs/claude-code/cli-usage) và hướng dẫn Anthropic về [subagent orchestration, tiêu chí delegate và cảnh báo overuse](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables). Các docs hiện tại có thể cập nhật sau; chọn tên model/flag theo tài liệu tại thời điểm dùng.

## 5. Quy trình làm việc đề xuất cho dự án

### Trước khi sửa

1. Xác nhận đang ở `C:\Users\Admin\Downloads\PyTutor-Thesis`; chạy `git status` và đọc diff trước khi đụng file. Repo hiện có thể chứa `CLAUDE_ONBOARDING_PROMPT.md` chưa commit — giữ nguyên trừ khi chủ dự án yêu cầu.
2. Dùng `PLAN.md` để xác định trạng thái phase và `AI_HANDOFF_CONTEXT.md` làm bản đồ kiến trúc. Đọc đúng mục liên quan và mã nguồn hiện tại; nếu tài liệu và code không khớp, ghi nhận sai lệch rồi xác nhận code/runtime trước khi thay đổi.
3. Mỗi task phải nêu: mục tiêu người dùng, phạm vi không đổi, điều kiện nghiệm thu, test, rủi ro dữ liệu và trạng thái hoàn tất mong muốn. Khi còn quyết định ảnh hưởng nghiệp vụ/phạm vi, hỏi trước khi tự mở rộng.
4. Với phase lớn, lập plan trước. Tách thành lát cắt dọc nhỏ để sớm kiểm tra cả backend, quyền, DB và frontend.

### Trong lúc sửa

- Bảo toàn mọi thay đổi chưa commit; không dùng reset/checkout để “dọn” worktree.
- Giữ ba hành động IDE tách biệt: chạy thử, hỏi gia sư AI và nộp chính thức. Giữ giới hạn EXAM ở backend dù tab thi/thực hành đang ẩn khỏi UI.
- Mọi quyền giảng viên/sinh viên phải được kiểm tra server-side; ẩn nút frontend không phải kiểm soát truy cập.
- Mặc định mock LLM và dùng dữ liệu sinh viên giả lập. Không gửi nội dung người học lên provider ngoài khi chưa được đồng ý; không để test ghi vào database người dùng.
- Dùng MCP server của PyTutor trong môi trường dev/test khi cần kiểm tra tích hợp; không kết nối Claude vào DB hoặc tài khoản sinh viên thật để hỗ trợ code.

### Trước khi báo xong

- Chạy test liên quan; với Phase 17 chạy `py -m unittest test_phase17_adaptive_analytics -v` và `py evaluate_phase17_adaptive.py`; với thay đổi giao diện chạy `npm.cmd run build` trong `frontend` và browser smoke test nếu môi trường cho phép.
- Khi có thay đổi API/quyền/DB, thêm regression test; dùng `PYTUTOR_DB_PATH` (và nếu cần `PYTUTOR_KNOWLEDGE_DB_PATH`) để cô lập DB kiểm thử.
- Báo cáo rõ test nào đạt/không chạy, browser đã kiểm tra hay chưa, giới hạn còn lại, và cập nhật `PLAN.md`/`AI_HANDOFF_CONTEXT.md` nếu trạng thái phase thay đổi.
- Không gọi pilot 2–3 người là bằng chứng learning gain; Phase 17 đang chờ chạy pilot và chỉ nên báo cáo quan sát mô tả.

## 6. Cấu trúc Claude Code gợi ý

Chưa cần tạo toàn bộ ngay. Bắt đầu tối thiểu và thêm khi workflow lặp lại:

```text
CLAUDE.md                         # điểm vào ngắn: cách làm, lệnh, tài liệu chuẩn
.claude/
  rules/
    backend.md                    # FastAPI, JWT/RBAC, SQLite, migration/test data
    frontend.md                  # React, theme, UI accessibility/Playwright
    evaluation.md                # adaptive metrics, synthetic data, pilot limitations
  skills/
    pytutor-phase-workflow/SKILL.md
    pytutor-qa/SKILL.md
```

`CLAUDE.md` nên chứa các bất biến, lệnh và đường dẫn đến tài liệu chuẩn; không chép toàn bộ handoff dài vào mọi session. Kích thước dưới ~200 dòng là gợi ý tổ chức từ repo cộng đồng tham khảo, không phải giới hạn sản phẩm/đảm bảo Claude sẽ luôn tuân thủ. Giữ skill nhỏ, kích hoạt rõ theo loại task, thêm `Gotchas` dựa trên lỗi thực tế. Nếu skill lớn, chuyển ví dụ/checklist sang `references/` để chỉ nạp khi cần.

## 7. Plugins nên cân nhắc

Nếu dùng Claude Code plugin marketplace, cài từng plugin và thử trên một task nhỏ trước khi bật rộng. Tên plugin/marketplace có thể thay đổi; xác nhận trong `/plugin` trước khi cài.

| Mức | Plugin | Vì sao hữu ích cho PyTutor | Lưu ý |
|---|---|---|---|
| Nên thử | `superpowers` | Quy trình lập kế hoạch, TDD, debug có hệ thống, xác minh trước khi hoàn tất. | Có thể trùng quy trình phase hiện có; giữ một luồng review nhất quán, không bắt buộc subagents mọi task. |
| Nên thử | `frontend-design` | Giao diện sinh viên/giảng viên, cải thiện bố cục, typography, contrast và trạng thái responsive. | Kiểm tra bằng screenshot/browser; không chấp nhận chỉ vì CSS build được. |
| Nên thử | `context7` | Tra tài liệu thư viện đúng phiên bản cho React/Vite/FastAPI và các phụ thuộc. | Dùng nguồn chính thức/library docs; không thay kiểm tra code thực tế. |
| Nên thử | `playwright` | Smoke test đăng nhập demo, vai trò, điều hướng, IDE, dashboard; lưu ảnh làm bằng chứng. | Dùng DB và tài khoản test cô lập, không thao tác dữ liệu thật. |
| Có điều kiện | `security-guidance` | Nhắc lỗi phổ biến và review diff cho authentication, IDOR, injection, secrets. | Đọc chính sách dữ liệu plugin; một số review gửi diff tới model và dùng thêm quota. |
| Có điều kiện | `code-review` / `code-simplifier` | Review PR hoặc giảm phức tạp sau khi test đạt. | Tránh bật cả nhiều reviewer chồng lấp; luôn xem diff trước khi chấp nhận thay đổi. |
| Có điều kiện | `document-skills` | Hỗ trợ tạo/chỉnh DOCX, PDF, PPTX, XLSX cho đồ án/báo cáo. | Chỉ cài khi làm artifact tài liệu; render/kiểm tra bố cục vẫn cần thiết. |

Không cần cài tất cả collections hoặc community agents. Plugin có thể kèm hooks, MCP server hoặc mã chạy cục bộ; cài từ nguồn tin cậy, đọc quyền và chỉ bật phần thực sự dùng.

## 8. Thói quen theo tác vụ PyTutor

| Loại việc | Cách Claude nên làm | Bằng chứng nghiệm thu |
|---|---|---|
| Sửa lỗi Backend/API | Tái hiện, test hồi quy, kiểm tra token/role/class ownership và truy cập trực tiếp API. | Test backend/API trên DB cô lập; xác nhận request bị chặn server-side. |
| Chỉnh UI | Duy trì API/business rules; kiểm tra trạng thái loading/empty/error, light/dark, desktop/mobile. | Build + Playwright screenshots và thao tác cả hai role nếu browser khả dụng. |
| Phase 16 AI | LLM mock mặc định, kiểm thử guard/RAG/EXAM/telemetry; không bịa tài liệu NEU. | Unit/API tests, Anti-Spoil cases, latency/false-positive nếu đo. |
| Phase 17 | Phân biệt `submit` và `ask_ai`; hiện sample size/data status; không suy diễn hint use thành năng lực. | Replay và test; pilot 2–3 người chỉ ghi quan sát, không tuyên bố nhân quả. |
| Báo cáo đồ án | Dùng số liệu đã kiểm tra; ghi phương pháp, mẫu và giới hạn; không biến mock benchmark thành thực nghiệm người học. | Đối chiếu với test output và pilot notes ẩn danh; kiểm tra file xuất cuối. |

## 9. Nguồn đã xem và mức truy cập

### Đọc được

- [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) — repo tổng hợp nhiều chủ đề (agents, commands, skills, workflows, hooks, MCP, memory, context và tips). Các nội dung trong tài liệu này là phần chọn lọc phù hợp PyTutor; repository thay đổi thường xuyên, nên xem ngày/phiên bản khi dùng lại.
- [tt-a1i/archify](https://github.com/tt-a1i/archify) — agent skill tạo sơ đồ và explainer; tham khảo mô tả và cookbook ở mục 3. Không cài hoặc chạy trong repo chỉ dựa trên quảng bá; cần rà quyền và thử với artifact không nhạy cảm.
- [Claude Code CLI reference](https://docs.anthropic.com/en/docs/claude-code/cli-usage) và [Anthropic prompting guidance](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables) — nguồn chính thức để kiểm tra session/model và cách dùng subagent; tính năng/model có thể đổi theo phiên bản.





## 10. Hành động tiếp theo gợi ý

1. Dùng `CLAUDE_ONBOARDING_PROMPT.md` hiện có để tạo/hoàn thiện `CLAUDE.md`; rà lại commands với test scripts thực tế, và bảo đảm mọi kiểm thử ghi DB dùng DB cô lập.
2. Bắt đầu bằng ít công cụ: thử workflow Claude Code hiện có trước; thêm `playwright` cho kiểm thử UI và `context7` khi cần tra docs phiên bản. Chỉ thêm `superpowers`/`frontend-design` nếu task thực tế cho thấy còn thiếu quy trình/năng lực tương ứng. Archify là lựa chọn riêng để tạo sơ đồ/explainer, không bắt buộc cho coding loop; xác minh tên, nguồn và quyền qua giao diện cài plugin/skill trước khi bật.
3. Tạo hai skill dự án (`pytutor-phase-workflow`, `pytutor-qa`) sau khi đã có một lần dùng workflow thật, ghi lại gotchas thay vì dự đoán quá sớm.
