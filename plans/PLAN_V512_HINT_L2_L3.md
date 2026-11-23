# PLAN v5.12 — Nâng cấp gợi ý Mức 2 và Mức 3

Yêu cầu: Mức 3 chưa đủ mạnh → thêm gợi ý chi tiết về thuật toán của bài; nâng tổng thể Mức 2 và Mức 3. Kết quả đo: `docs/HINT_L2_L3_V512.md`.

Quyết định đã chốt (theo đề xuất): Mức 3 cho thuật toán **bằng lời**, khung mã vẫn che logic; thêm ô ghi chú thuật toán cho giảng viên (cột `algorithm_notes`); kiểm chứng Gemini thật để sau (còn 6/335 lượt).

| Bước | Nội dung | Trạng thái |
|---|---|---|
| 0 | Đo mốc offline (tag `v512_before*`) | xong |
| 1 | Cột `algorithm_notes`: DB, MCP storage, schema, API (chỉ giảng viên thấy), form, seed 5 bài | xong |
| 2 | Mức 2: đối chứng, dãy giá trị (backend `_trace_failure`), dạng lệch, thiếu bước cập nhật, xoay vòng test lỗi; prompt `_LEVEL_2` | xong |
| 3 | Mức 3: `backend/hint_algorithm.py`, `_level3`, TODO gắn số bước, `enforce_level3_prose`, prompt `_LEVEL_3` | xong |
| 4 | Bộ đo: 4 kiểm tra mới, nới biên độ dài; test `test_hint_l23_v512` (20 test) | xong |
| 5 | Giao diện `TutorPanel`; QA trình duyệt (form giảng viên, IDE sinh viên, 375px) | xong |
| 6 | Hồi quy, tệp vàng prompt, tài liệu | xong |
| 7 | (việc mở) Đo với Gemini thật theo lượt được cấp; điền ghi chú cho các bài trong DB thật | chưa |
