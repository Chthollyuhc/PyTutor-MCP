# Tổng hợp nhiều lần chạy với mô hình thật

> Sinh bởi `summarize_real_llm_runs.py` từ **5 lần chạy** `evaluate_real_llm.py` (cùng mã nguồn, cùng 22 ca, mô hình `gemini-3.5-flash-lite`).
> Chỉ đếm hành vi của bộ lọc và kiểm tra tất định; **không** nói gì về chất lượng sư phạm. Ca không gọi mô hình (S1, S4) luôn hiện 0 lần thành công.

| Ca | Bị bộ lọc chặn/thay | Kiểm tra tất định không đạt | Mô hình trả lời thành công | Tín hiệu bộ lọc |
|---|---:|---:|---:|---|
| C1 | 0/5 | 0/5 | 5/5 | — |
| C2 | 0/5 | 0/5 | 5/5 | — |
| C3 | 0/5 | 0/5 | 5/5 | — |
| C4 | 0/5 | 0/5 | 5/5 | — |
| C5 | 0/5 | 0/5 | 5/5 | — |
| H1 | 0/5 | 0/5 | 5/5 | — |
| H2 | 0/5 | 0/5 | 5/5 | — |
| H3 | 0/5 | 1/5 | 5/5 | — |
| H4 | 0/5 | 0/5 | 5/5 | level3_masked:2 ×3, level3_masked:1 ×1, level3_masked:3 ×1 |
| H5 | 0/5 | 0/5 | 5/5 | — |
| I1 | 0/5 | 0/5 | 5/5 | — |
| I2 | 0/5 | 0/5 | 5/5 | — |
| I3 | 0/5 | 0/5 | 5/5 | — |
| R1 | 0/5 | 0/5 | 5/5 | — |
| R2 | 0/5 | 0/5 | 5/5 | — |
| R3 | 0/5 | 0/5 | 5/5 | — |
| R4 | 0/5 | 0/5 | 5/5 | — |
| R5 | 0/5 | 0/5 | 5/5 | — |
| S1 | 0/5 | 0/5 | 0/5 | — |
| S2 | 0/5 | 0/5 | 5/5 | — |
| S3 | 0/5 | 0/5 | 5/5 | — |
| S4 | 0/5 | 0/5 | 0/5 | — |

- Ca dao động (bị chặn một số lần, không phải mọi lần): không có.
- Ca luôn bị chặn: không có (S2 và H3 bị chặn là hành vi mong đợi hoặc đã biết).
