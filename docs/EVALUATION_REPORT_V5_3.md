# Báo cáo thực nghiệm nâng cấp v5.3 — PyTutor-MCP

> **Loại tài liệu:** báo cáo thực nghiệm cho đợt nâng cấp sư phạm v5.3 (lát cắt S1–S4 trong `plans/PLAN_THESIS_PEDAGOGICAL_UPGRADE.md`).
> **Tách bạch với `docs/EVALUATION_REPORT.md` (v3.0, 20/10/2026):** báo cáo v3.0 đo lớp tích hợp MCP, sandbox và độ trễ với LLM thật ở thời điểm đó; báo cáo này **không** cập nhật hay thay thế các số liệu ấy. Hai tài liệu đo những thứ khác nhau, không cộng gộp số liệu.
> **Ngày đo:** 12/11/2026 · **Môi trường:** Windows 11, Python 3.14, một máy cá nhân · **Chế độ:** ngoại tuyến (`PYTUTOR_DISABLE_LLM=1`), DB SQLite tạm và chỉ mục KB tạm; `pytutor.db` và `pytutor_knowledge.sqlite3` gốc không bị đọc/ghi bởi các lệnh đo.
> **Đề tài:** Xây dựng hệ thống hỗ trợ học lập trình Python với phản hồi thích ứng dựa trên mô hình người học — Trần Minh Khánh (K65, MSV 11236131), ĐH Kinh tế Quốc dân.

## 0. Cách đọc báo cáo này

Bằng chứng được chia thành ba tầng **không thay thế cho nhau**:

| Tầng | Trả lời câu hỏi gì | Dữ liệu | Trạng thái |
|---|---|---|---|
| **A. Kiểm thử tự động theo phân hệ** | Hành vi đã cài đặt có đúng đặc tả không (đạt/không đạt)? | Fixture do dự án viết, DB tạm | Đã chạy: 57/57 đạt |
| **B. Benchmark tất định ngoại tuyến** | Các thành phần tất định (guard, truy xuất, chính sách chọn chiến lược) cho tỷ lệ bao nhiêu trên bộ ca cố định? | Corpus tổng hợp do dự án biên soạn + KB nội bộ | Đã chạy (mục 2) |
| **C. Pilot người dùng thật** | Sinh viên/giảng viên có hiểu và dùng được phản hồi không? | Người tham gia thật | **CHƯA THỰC HIỆN** (mục 3) |

Điều báo cáo này **không** khẳng định: không có số liệu nào ở tầng A hoặc B nói lên chất lượng sư phạm của câu trả lời do LLM sinh ra, mức tiến bộ học tập, hay quan hệ nhân quả giữa việc dùng hệ thống và kết quả học. Dự án chủ ý **không chấm chất lượng sư phạm của LLM bằng máy**; phần đó chỉ có thể đến từ tầng C.

---

## 1. Tầng A — Kiểm thử tự động theo phân hệ

Lệnh: `py -m unittest test_phase16_ai_upgrade test_phase17_adaptive_analytics test_qa_authorization test_thesis_upgrade -v`, chạy trên DB tạm + chỉ mục KB tạm, `PYTUTOR_DISABLE_LLM=1`.

| Module | Số test | Kết quả | Phạm vi kiểm tra |
|---|---:|---|---|
| `test_phase16_ai_upgrade` | 6 | 6 đạt | Guardrail vào/ra, prompt, RAG cơ bản (Phase 16) |
| `test_phase17_adaptive_analytics` | 5 | 5 đạt | `select_hint_strategy`, định nghĩa metric, `data_status` |
| `test_qa_authorization` | 9 | 9 đạt | RBAC phía server, quyền sở hữu lớp |
| `test_thesis_upgrade` | 37 | 37 đạt | Nâng cấp v5.3 (bảng dưới) |
| **Tổng** | **57** | **57 đạt, 0 lỗi** | Lần chạy cuối (bản mã cuối phiên S5): mỗi module một DB tạm riêng |

*Cập nhật cuối phiên S5 (12/11/2026):* `test_thesis_upgrade` tăng từ 34 lên 37 test do thêm ba test cho chat sau khi nộp đạt ở chế độ offline (S8a) và trường `has_passed` của API chi tiết bài tập. Lần chạy cuối này chỉ thực hiện theo cách (ii) bên dưới; cách (i) (chung một DB) **chưa được chạy lại** với 37 test. Benchmark tầng B và replay được chạy lại trên bản mã cuối và cho **cùng số liệu** như mục 2 (guard phát triển 0/30 rò rỉ, tập giữ riêng 4/14; RAG hit@3 36/38, no-source 13/14; replay 6/6).

Đoạn sau mô tả lần đo trước (54 test): kết quả giống nhau ở hai cách chạy: (i) cả bốn module chung một DB tạm theo đúng thứ tự trên; (ii) mỗi module một DB tạm riêng. Ghi chú: phiên trước từng ghi nhận `test_qa_authorization` lỗi khi dùng chung DB với `test_thesis_upgrade`; ở lần đo này (thứ tự module như lệnh trên) không tái hiện, nhưng thứ tự khác chưa được thử, nên cách (ii) vẫn là cách chạy khuyến nghị. `py -m compileall -q backend mcp_server` thoát mã 0.

Chi tiết `test_thesis_upgrade` theo phân hệ:

| Lớp test | Số test | Lát cắt | Nội dung khóa |
|---|---:|---|---|
| `StudentModelSyncTests` | 4 | S2.2 | Hai bản `compute_student_model` (backend và MCP) cùng nguồn, cùng đầu ra; hồ sơ thưa báo `limited`; có lỗi lặp lại + bước tiếp theo; nhãn không vượt bằng chứng |
| `FormativeFeedbackTests` | 6 | S1.1 | Fallback mức 1/2/3 chỉ nêu điều quan sát được, không lộ đáp án; chiến lược đổi bước kế tiếp nhưng không đổi `hint_level`; khi đạt thì rút giàn giáo; prompt có khung formative |
| `RagSourceTests` | 5 | S1.3, S3.3 | Câu trong KB trả đúng mục; câu ngoài KB trả không nguồn; dòng "Nguồn:" không bị index; trả lời offline chỉ trích cái đã dùng; danh mục KB có ghi chú nguồn gốc |
| `EndpointTests` | 19 | S1.2, S1.4, S2.1, S2.4, S3 | Chat báo nguồn hoặc `no_source`; lý do sao; `ask_ai` không sinh sao; chống cày sao; chat trước/sau khi nộp đạt; chat offline sau khi đạt tóm tắt cấu trúc code đã nộp mà không chép lại mã; `has_passed` chỉ bật với lượt `submit` đạt của chính sinh viên; trả lời luật sao từ văn bản hệ thống; 👍/👎 có kiểm tra chủ sở hữu; insight lớp, 404 với lớp không sở hữu, lớp rỗng báo `no_data`; class chat không chứa danh tính; tổng hợp phản hồi chỉ là số đếm |
| `ClassSummaryAnswerTests` | 1 | S3.2 | Mẫu nhỏ được gắn cờ trong câu trả lời tất định |
| `BenchmarkReleaseGateTests` | 2 | S4 | Ngưỡng phát hành: corpus phát triển không rò rỉ và không chặn nhầm; RAG hit@3 ≥ 90%, hit@1 ≥ 80%, no-source ≥ 85% |

**Giới hạn của tầng A:** test xác nhận mã làm đúng điều người viết test mong đợi trên fixture; test không đo tần suất lỗi trên dữ liệu chưa thấy và không kiểm tra giao diện.

**Bộ kiểm thử phân hệ cũ (chạy lại cuối phiên S5, 12/11/2026; mỗi bộ một DB tạm riêng, `PYTUTOR_DISABLE_LLM=1`).** Đây là các kịch bản dạng script (không phải `unittest`), chạy bằng `py -m <module>` hoặc `py <tệp>`; lệnh `py -m unittest mcp_server.test_mcp_server backend.test_backend_e2e` báo "NO TESTS RAN" vì hai tệp này không định nghĩa `TestCase`.

| Kịch bản | Kết quả | Ghi chú |
|---|---|---|
| `py -m mcp_server.test_mcp_server` | 8/8 bước đạt | Sandbox, AST, timeout vòng lặp vô hạn |
| `py -m backend.test_backend_e2e` | 6/6 đạt **sau khi sửa kịch bản** | Lần chạy đầu trên DB tạm **thất bại** (`no such table`): kịch bản dùng `httpx.ASGITransport` nên không chạy `lifespan`, DB mới không có bảng. Đã thêm `init_db()` vào đầu kịch bản; đây là lỗi của kịch bản khi cô lập DB, không phải của API. Cùng lần này lộ ra một hồi quy thật do thay đổi trong phiên (tra `has_passed` làm `GET /api/exercises/{id}` trả 500 khi DB lỗi) — đã sửa để lỗi DB không làm hỏng việc xem đề. |
| `py test_phase8_chat.py` | 7/7 đạt | Câu "Tại sao range(1, n) thiếu 1 đơn vị?" ở chế độ offline trả lời **không kèm nguồn** (truy xuất không khớp) — kịch bản vẫn tính đạt; đây là một ca truy xuất trượt, không nằm trong corpus RAG |
| `py test_phase10_gamification.py` | 6/6 đạt | |
| `py test_phase12_classroom_exam.py` | 7/7 đạt | EXAM guard khóa gợi ý và chat |

Các bộ `test_phase5_backend.py`, `test_phase9_visualizer.py`, `test_phase13_14_neu_lms.py`, `test_phase15_3_qa_audit.py`, `test_phase15_4_action_buttons.py` **không được chạy lại** sau v5.3. Frontend: `npm.cmd run test:theme` 3/3, `npm.cmd run build` thành công (1697 module).

---

## 2. Tầng B — Benchmark tất định ngoại tuyến

Cả ba benchmark đều không gọi LLM, không cần mạng, chạy lặp lại cho cùng kết quả đếm (độ trễ dao động theo máy).

### 2.1. Guardrail & Anti-Spoil (luật `GUARD_RULES_VERSION = "2"`)

Lệnh: `py evaluate_guardrails_benchmark.py` (corpus phát triển `evaluation/guardrail_corpus.json`, v1.0) và `py evaluate_guardrails_benchmark.py --holdout` (tập giữ riêng `evaluation/guardrail_holdout.json`, v1.0-holdout).

Định nghĩa: một *tình huống tấn công* bị tính là **rò rỉ** khi câu hỏi của người học qua được input guard **và** phản hồi chứa lời giải qua được output guard (sau bước `sanitize_spoil_code`). Phản hồi "của mô hình" trong corpus là **văn bản giả lập do dự án soạn**, không phải đầu ra của LLM thật.

**Bảng tổng hợp**

| Chỉ số | Phát triển (dev) | Giữ riêng (hold-out) |
|---|---|---|
| Rò rỉ trên tình huống tấn công (`leak_rate`) | 0/30 = 0,00% | **4/14 = 28,57%** |
| Chặn đầu vào injection / ngoài phạm vi | 22/22 = 100% | **1/10 = 10,00%** |
| Chặn nhầm câu hỏi hợp lệ (FPR) | 0/28 = 0,00% | 1/12 = 8,33% |
| Chặn nhầm phản hồi gia sư hợp lệ (FPR) | 0/31 = 0,00% | 0/12 = 0,00% |
| Nơi chặn tấn công | output guard 30/30 | output guard 10/14, lọt 4/14 |

**Tấn công theo dạng (số ca rò rỉ / tổng)**

| Dạng (dev) | Rò rỉ | Dạng (dev) | Rò rỉ | Dạng (hold-out) | Rò rỉ |
|---|---|---|---|---|---|
| `fenced_python` | 0/3 | `html_pre` | 0/1 | `fenced_python` | 0/2 |
| `fenced_no_lang` | 0/2 | `inline_backticks` | 0/1 | `one_liner` | 0/2 |
| `fenced_other_lang` | 0/2 | `mixed_explanation` | 0/1 | `unfenced` | 0/1 |
| `tilde_fence` | 0/2 | `numbered_lines` | 0/1 | `indented_block` | 0/1 |
| `unfenced` | 0/2 | `bulleted_lines` | 0/1 | `comment_padded` | 0/1 |
| `indented_block` | 0/2 | `quoted_lines` | 0/1 | `fstring_solution` | 0/1 |
| `split_blocks` | 0/2 | `semicolon_joined` | 0/1 | `mixed_language` | 0/1 |
| `one_liner` | 0/3 | `function_solution` | 0/1 | `walrus_loop` | 0/1 |
| `disclosure_phrase` | 0/2 | `while_solution` | 0/1 | **`table`** | **1/1** (HA04) |
| `disclosure_phrase_en` | 0/1 | | | **`lettered_steps`** | **1/1** (HA07) |
| | | | | **`prose_wrapped`** | **1/1** (HA08) |
| | | | | **`disclosure_phrase`** | **1/1** (HA11) |

**Đầu vào injection / ngoài phạm vi theo nhóm (số ca bị chặn / tổng)**

| Nhóm | Dev | Hold-out |
|---|---|---|
| `en_ignore` | 4/4 | 0/2 |
| `en_reveal` | 2/2 | 0/1 |
| `en_roleplay` | 2/2 | — |
| `vi_ignore` | 4/4 | 0/2 |
| `vi_reveal` | 3/3 | 0/1 |
| `vi_roleplay` | 1/1 | 0/1 |
| `mixed` | 2/2 | — |
| `out_of_scope` | 3/3 | 1/2 |
| `too_long` | 1/1 | — |
| `encoded` | — | 0/1 |

**Chặn nhầm theo nhóm (số ca bị chặn nhầm / tổng)**

| Câu hỏi hợp lệ | Dev | Hold-out | Phản hồi gia sư hợp lệ | Dev | Hold-out |
|---|---|---|---|---|---|
| `concept` | 0/6 | 0/2 | `concept` | 0/5 | 0/1 |
| `debug` | 0/5 | 0/2 | `diagnostic` | 0/5 | 0/2 |
| `ambiguous_words` | 0/6 | **1/2** (HB09, lý do `prompt_injection`) | `socratic` | 0/3 | 0/2 |
| `output_format` | 0/4 | 0/2 | `refusal` | 0/4 | 0/1 |
| `hint_request` | 0/3 | 0/1 | `list_prose` | 0/3 | 0/1 |
| `english` | 0/2 | 0/2 | `one_line_example` / `two_line_example` | 0/3 | 0/1 |
| `meta` | 0/2 | 0/1 | `vietnamese_keywords` | 0/3 | — |
| | | | `math` / `math_prose` | 0/1 | 0/1 |
| | | | `english`, `pass_feedback`, `source_cited` | 0/1 mỗi nhóm | 0/1 mỗi nhóm |
| | | | `skeleton_small` | 0/1 | — |

**Độ trễ guard (ms, mỗi ca lặp 50 lần)**

| Thành phần | Tập | n | Median | p95 | Max |
|---|---|---:|---:|---:|---:|
| Input guard | dev | 4.080 | 0,0083 | 0,0148 | 1,0828 |
| Output guard | dev | 3.111 | 0,0096 | 0,0195 | 0,1655 |
| Input guard | hold-out | 1.836 | 0,0115 | 0,0175 | 0,8469 |
| Output guard | hold-out | 1.326 | 0,0104 | 0,0196 | 0,1140 |

**Diễn giải trung thực**

- Luật v2 được **chỉnh trên chính corpus phát triển**, nên 0% rò rỉ / 100% chặn ở đó chỉ là kiểm tra hồi quy ("luật không lùi so với các ca đã biết"), không phải ước lượng mức khái quát. Bộ test `BenchmarkReleaseGateTests` khóa đúng điều này.
- Tập giữ riêng được soạn sau khi đóng băng luật và **không dùng để chỉnh luật** (kể cả trong lần đo này — không có thay đổi mã nào). Nó cho thấy guard dựa trên biểu thức chính quy còn yếu rõ rệt: lọt lời giải trình bày dạng bảng, đánh thứ tự a)/b)/c), lồng trong câu văn, cụm tiết lộ diễn đạt khác; gần như không bắt được injection diễn đạt lại (1/10) và chặn nhầm 1/12 câu hỏi hợp lệ có từ ngữ mơ hồ.
- Tập giữ riêng nhỏ (14/10/12/12 ca) và cùng một người soạn với tập phát triển, nên các tỷ lệ trên có độ bất định lớn và không đại diện cho phân phối câu hỏi thật của sinh viên. Nếu sau này vá luật theo các ca này thì tập này mất tư cách hold-out và phải soạn tập mới.
- Guard là **một** lớp phòng vệ; khi có LLM thật, việc không lộ lời giải còn phụ thuộc chỉ dẫn trong prompt — phần đó **không được đo** ở đây.
- Độ trễ guard dưới 0,02 ms ở p95: không đáng kể so với một lượt gọi LLM; giá trị max bị chi phối bởi lượt chạy đầu (khởi động).

### 2.2. Truy xuất RAG trên KB nội bộ

Lệnh: `py evaluate_rag_benchmark.py [--min-score X]`. Benchmark dựng chỉ mục **tạm** từ `docs/knowledge_base/` (17 đoạn), truy xuất top-3 trên bộ `evaluation/rag_questions.json` v1.0: 38 câu có nội dung trong KB, 14 câu ngoài KB. Đúng = trả về đúng tài liệu và mục kỳ vọng; với câu ngoài KB, đúng = **không trả nguồn nào** (hệ thống sẽ nói "không có tài liệu nội bộ phù hợp").

**Kết quả ở ngưỡng đang dùng trong sản phẩm (`MIN_RELEVANCE = 0,16`)**

| Chỉ số | Kết quả |
|---|---|
| hit@1 | 34/38 = 89,47% |
| hit@3 | 36/38 = 94,74% |
| MRR | 0,9211 |
| Câu trong KB có ít nhất một nguồn | 37/38 = 97,37% |
| Câu ngoài KB trả "không có nguồn" đúng | 13/14 = 92,86% |
| Không tìm đúng mục trong top-3 | Q28 (lists), Q36 (debugging) |
| Gắn nguồn không phù hợp | O02 → mục "Hàm và giá trị trả về" (điểm 0,2335) |

**Theo chủ đề (câu trong KB, ngưỡng 0,16)**

| Chủ đề | hit@1 | hit@3 | Chủ đề | hit@1 | hit@3 |
|---|---|---|---|---|---|
| `accumulator` | 2/2 | 2/2 | `functions` | 2/2 | 2/2 |
| `arithmetic` | 3/3 | 3/3 | `input` | 2/3 | 3/3 |
| `builtins` | 2/2 | 2/2 | `lists` | 2/3 | 2/3 |
| `comprehension` | 2/2 | 2/2 | `loops` | 3/3 | 3/3 |
| `conditionals` | 2/2 | 2/2 | `output` | 3/3 | 3/3 |
| `debugging` | 1/2 | 1/2 | `strings` | 2/2 | 2/2 |
| `dicts` | 2/2 | 2/2 | `style` | 1/2 | 2/2 |
| `errors` | 3/3 | 3/3 | `types` | 2/2 | 2/2 |

**Câu ngoài KB theo nhóm (ngưỡng 0,16):** `institutional` 3/3 · `off_topic` 3/3 · `python_not_covered` 7/8.

**Quét ngưỡng `--min-score`**

| Ngưỡng | hit@1 | hit@3 | MRR | Câu trong KB có nguồn | No-source đúng (ngoài KB) | Trượt top-3 |
|---:|---|---|---:|---|---|---|
| 0,00 | 35/38 = 92,11% | 38/38 = 100% | 0,9605 | 38/38 | 0/14 = 0,00% | — |
| 0,08 | 35/38 = 92,11% | 38/38 = 100% | 0,9605 | 38/38 | 6/14 = 42,86% | — |
| 0,12 | 34/38 = 89,47% | 37/38 = 97,37% | 0,9342 | 37/38 | 9/14 = 64,29% | Q28 |
| **0,16** (đang dùng) | 34/38 = 89,47% | 36/38 = 94,74% | 0,9211 | 37/38 | 13/14 = 92,86% | Q28, Q36 |
| 0,20 | 32/38 = 84,21% | 33/38 = 86,84% | 0,8553 | 35/38 | 13/14 = 92,86% | Q02, Q13, Q28, Q32, Q36 |

**Độ trễ truy xuất (ms, n = 1.092 mỗi lần chạy)**

| Lần chạy | Median | p95 | Max |
|---|---:|---:|---:|
| Ngưỡng 0,16 (lần chạy chính) | 1,5376 | 1,9725 | 8,2579 |
| Khoảng quan sát qua 6 lần chạy | 1,49 – 1,54 | 1,94 – 2,06 | 3,35 – 12,84 |

**Diễn giải trung thực**

- Ngưỡng là đánh đổi: không ngưỡng thì mọi câu ngoài KB đều bị "gắn nguồn" (0/14); 0,16 là điểm thấp nhất đạt 13/14 và trả giá bằng 2 câu trong KB bị trượt; 0,20 không cải thiện phía ngoài KB mà mất thêm 3 câu. Ngưỡng 0,16 được **chọn trên chính bộ câu hỏi này**, nên các tỷ lệ ở hàng 0,16 lạc quan hơn so với câu hỏi mới.
- **Tập phát triển không hoàn toàn mù:** câu Q01 từng trượt, sau đó mục "Vòng lặp và điều kiện dừng" trong `python_fundamentals.md` được bổ sung một câu và bộ tách từ bỏ token một ký tự; hit@1 tăng 33/38 → 34/38 sau thay đổi đó. Không có tập câu hỏi giữ riêng cho RAG.
- So với nhật ký phiên trước (mục 5.2 của kế hoạch), hàng 0,12 lần này là 9/14 thay vì 10/14: số trong nhật ký được đo trước khi sửa bộ tách từ; số trong bảng trên là số đo lại hôm nay và là số được dùng.
- Ca lọt O02 (câu về đệ quy khớp mục "Hàm") cho thấy truy xuất theo từ khóa TF-IDF không phân biệt được "cùng từ vựng" với "có nội dung trả lời".
- **KB là tài liệu do dự án tự biên soạn** (`python_fundamentals.md`, `python_core_topics.md`), **chưa phải giáo trình chính thức của NEU**; 17 đoạn và 52 câu hỏi là quy mô nhỏ. Benchmark chỉ đo việc *tìm đúng mục*, không đo câu trả lời cuối cùng có đúng hay dễ hiểu không.

### 2.3. Replay chính sách thích ứng Phase 17

Lệnh: `py evaluate_phase17_adaptive.py` (DB tạm; script chỉ gọi hàm thuần `select_hint_strategy`).

| Ca tổng hợp | Mức yêu cầu | Baseline tĩnh | Chiến lược chọn | Kỳ vọng | Bằng chứng ghi nhận | Giữ nguyên mức |
|---|---:|---|---|---|---|---|
| `empty` | 1 | `conceptual_start` | `conceptual_start` | ✔ | (không có) | ✔ |
| `syntax` | 1 | `conceptual_start` | `failed_case_diagnosis` | ✔ | test lỗi | ✔ |
| `logic` | 2 | `conceptual_start` | `failed_case_diagnosis` | ✔ | test lỗi | ✔ |
| `repeat` | 2 | `conceptual_start` | `recurring_difficulty` | ✔ | lượt trước, mức gợi ý trước, test lỗi | ✔ |
| `recovery` | 2 | `conceptual_start` | `failed_case_diagnosis` | ✔ | như trên + `first_try_pass_rate`, `autonomy_score` | ✔ |
| `passed` | 1 | `solution_review` | `solution_review` | ✔ | (không có) | ✔ |

Tổng: chiến lược khớp kỳ vọng 6/6; baseline tĩnh khớp 2/6; giữ nguyên `hint_level` người học yêu cầu 6/6; nhất quán bằng chứng 6/6.

**Giới hạn:** 6 ca do chính người viết chính sách soạn, kỳ vọng cũng do người đó đặt — đây là kiểm tra "chính sách làm đúng đặc tả", không phải bằng chứng rằng chiến lược được chọn giúp học tốt hơn. Con số "baseline 2/6" chỉ mô tả một quy tắc tĩnh đơn giản, không phải so sánh với hệ thống khác.

---

## 3. Tầng C — Pilot người dùng thật: **CHƯA THỰC HIỆN**

- Tính đến ngày 12/11/2026 **chưa có phiên pilot nào** với sinh viên hoặc giảng viên. Không có số liệu người dùng nào trong báo cáo này.
- Bộ tài liệu để chạy pilot 2–3 sinh viên và 1–2 giảng viên nằm ở `docs/PILOT_KIT.md` (kịch bản, phiếu đồng ý, phiếu quan sát, đáp án đối chiếu).
- Kể cả khi đã chạy, pilot cỡ này chỉ cho **quan sát mô tả về tính dễ hiểu và dễ dùng**; không đủ để kết luận về tiến bộ học tập, ý nghĩa thống kê hay quan hệ nhân quả. Kết quả pilot sẽ được ghi thành mục riêng, **không trộn** với số liệu tầng A/B.

---

## 4. Giới hạn chung

1. **Phản hồi mô hình trong guardrail corpus là giả lập.** Tỷ lệ rò rỉ đo khả năng của bộ lọc trước các văn bản do dự án soạn, không đo tần suất LLM thật sinh lời giải.
2. **S1.4 (khóa phạm vi Chat) khi bật LLM thật phụ thuộc prompt.** Trước khi nộp đạt, prompt chat không chứa code bài làm và có chỉ dẫn từ chối gỡ lỗi; việc phát hiện "nhờ gỡ code" bằng regex để chuyển hướng sang `🤖 Hỏi Gia sư AI` **chỉ chạy ở nhánh offline** và chưa được đo false-positive/false-negative. Hành vi với LLM thật chưa được kiểm chứng.
3. **Tập phát triển không mù.** Luật guard v2 chỉnh trên corpus dev; ngưỡng RAG chọn trên bộ câu hỏi; Q01 từng dùng để bổ sung `python_fundamentals.md`. Chỉ guard có tập giữ riêng, và kết quả ở đó kém hơn nhiều.
4. **KB là tài liệu biên soạn nội bộ, chưa phải giáo trình chính thức NEU.** Nguồn hiển thị cho người học là tên mục trong tài liệu nội bộ, không phải trích dẫn học thuật.
5. **`stars_earned`, `autonomy_score`, `data_status` là quy ước vận hành của sản phẩm.** Ngưỡng `limited` < 3 bài, luật 3/2/1 sao theo mức gợi ý cao nhất trước lần nộp đạt đầu tiên… là heuristic thiết kế, **chưa phải thang đo tâm trắc đã được kiểm chứng**; không dùng để xếp loại năng lực sinh viên.
6. **Không chấm chất lượng sư phạm của LLM bằng máy.** Không có điểm "độ hay/độ đúng" cho câu trả lời của gia sư AI trong báo cáo này.
7. **Cỡ mẫu nhỏ, một người soạn, một máy đo.** Corpus guard 111 ca (dev) + 48 ca (hold-out), RAG 52 câu, replay 6 ca; số đo độ trễ lấy trên một máy cá nhân, không phải đo tải.
8. **Phạm vi chưa đo trong lần này:** giao diện (đã kiểm tra tay ở phiên trước, không thuộc báo cáo này), độ trễ đầu-cuối khi gọi LLM/MCP, các bộ test phân hệ cũ, hành vi dưới nhiều người dùng đồng thời.

---

## 4b. Ghi chú v5.4 (không thuộc số liệu v5.3 ở trên)

> Đánh giá với LLM thật (Gemini `gemini-3.5-flash-lite`, 22 ca, DB/KB tạm cô lập, 12/11/2026): xem [REAL_LLM_EVALUATION.md](REAL_LLM_EVALUATION.md) (raw: `evaluation/real_llm_results.json`; chạy lại: `py evaluate_real_llm.py`). Điểm sư phạm 0–5 chờ sinh viên chấm tay; không thay đổi số liệu v5.3 ở trên.

Đợt v5.4 gỡ MCP khỏi giao diện, đơn giản hóa thuật ngữ, thêm nhóm quá trình học cho giảng viên (`docs/PROCESS_GROUPS.md`) và tài liệu Gia sư AI theo lớp (`docs/KB_UPLOAD_GUIDE.md`). Chạy lại (12/11/2026, DB/KB tạm, LLM tắt, từng module một tiến trình): `test_thesis_upgrade` 60 (37 của v5.3 + 13 nhóm quá trình/chạy thử + 10 tải tài liệu theo lớp), Phase 16 ×6, Phase 17 ×5, QA authorization ×9 đều đạt; replay Phase 17 6/6 (baseline 2/6); guard corpus phát triển rò rỉ 0, tập giữ riêng vẫn rò rỉ 4/14 (luật guard không đổi); RAG hit@3 36/38 (không đổi do mặc định chỉ truy xuất tài liệu chung); MCP 8/8, backend E2E 6/6, Phase 8 7/7, Phase 10 6/6, Phase 12 7/7; `test:theme` 3/3, `vite build` OK. `test_phase13_14_neu_lms.py` **lỗi ngay ở bước gán bài vào lớp** ("Bài tập thuộc giảng viên khác..."), lỗi này có sẵn ở HEAD trước v5.4 và không liên quan thay đổi. Nhóm quá trình và tài liệu lớp là bằng chứng mô tả/chức năng, không phải bằng chứng hiệu quả học tập; ngưỡng phân nhóm là quy ước chưa hiệu chuẩn.

---

## 5. Tái lập số liệu

Chạy tại thư mục gốc repo, PowerShell. Mọi lệnh dùng DB tạm và chỉ mục KB tạm; không đụng `pytutor.db` / `pytutor_knowledge.sqlite3`.

```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:PYTUTOR_DISABLE_LLM = "1"
$tmpDb = Join-Path $env:TEMP ("pytutor_check_" + [guid]::NewGuid().ToString("N") + ".db")
$tmpKb = Join-Path $env:TEMP ("pytutor_kb_" + [guid]::NewGuid().ToString("N") + ".sqlite3")
$env:PYTUTOR_DB_PATH = $tmpDb; $env:PYTUTOR_KNOWLEDGE_DB_PATH = $tmpKb
try {
  # Tầng B
  py evaluate_guardrails_benchmark.py              # corpus phát triển (thoát mã 1 nếu có rò rỉ)
  py evaluate_guardrails_benchmark.py --holdout    # tập giữ riêng (chỉ báo cáo, luôn thoát mã 0)
  py evaluate_rag_benchmark.py                     # ngưỡng mặc định 0.16
  foreach ($t in "0.0","0.08","0.12","0.16","0.20") { py evaluate_rag_benchmark.py --min-score $t }
  py evaluate_phase17_adaptive.py
  # Tầng A
  py -m compileall -q backend mcp_server
  py -m unittest test_phase16_ai_upgrade test_phase17_adaptive_analytics test_qa_authorization test_thesis_upgrade -v
}
finally {
  Remove-Item Env:PYTUTOR_DB_PATH, Env:PYTUTOR_KNOWLEDGE_DB_PATH, Env:PYTUTOR_DISABLE_LLM -ErrorAction SilentlyContinue
  Remove-Item $tmpDb, "$tmpDb-wal", "$tmpDb-shm", $tmpKb -Force -ErrorAction SilentlyContinue
}
```

- Thêm `--json` vào hai script benchmark để lấy kết quả từng ca (dùng cho các bảng theo nhóm ở mục 2.1).
- Nếu muốn cô lập chặt hơn, chạy mỗi module unittest trong một lần lặp riêng với `$tmpDb`/`$tmpKb` mới.
- Số đếm (ca rò rỉ, hit@k…) là tất định; số độ trễ sẽ khác theo máy và lần chạy.
