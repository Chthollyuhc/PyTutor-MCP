# Đo 3 mức gợi ý — `v512_real_dev`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-22T16:35:49 · commit `b0fa829` · chế độ **real** · tập **dev** · 12 kịch bản, 24 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 20, "Pedagogical-Rule-Engine (Offline Fallback)": 4}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| do_dai | — | 11/12 | 12/12 |
| dung_mot_buoc_ke_tiep | — | 12/12 | 12/12 |
| khong_chep_lai_chu_thich | — | 2/2 | 2/2 |
| khong_chuong_trinh_hoan_chinh | — | 12/12 | — |
| khong_cum_chi_cach_sua | — | 12/12 | 12/12 |
| khong_lap_voi_luot_truoc | — | — | 12/12 |
| khong_lo_bieu_thuc_loi_giai | — | 12/12 | 12/12 |
| khong_nhan_xet_nang_luc | — | 12/12 | 12/12 |
| khung_muc_tieu_bang_chung_buoc | — | 12/12 | 12/12 |
| m2_co_bang_chung_thuc_thi | — | 12/12 | — |
| m2_co_doi_chung | — | 5/8 | — |
| m2_dong_dung_cho_loi | — | 12/12 | — |
| m2_dung_mot_dong_that | — | 12/12 | — |
| m2_khong_khoi_code_3_dong | — | 12/12 | — |
| m3_co_khung_todo | — | — | 12/12 |
| m3_co_thuat_toan_chi_tiet | — | — | 11/12 |
| m3_dan_y_4_buoc_khop_bai | — | — | 12/12 |
| m3_khong_code_trong_loi | — | — | 12/12 |
| m3_khung_khong_dat_het_test | — | — | 12/12 |
| m3_khung_la_python_hop_le | — | — | 10/12 |
| m3_todo_gan_buoc | — | — | 11/12 |
| tang_tien_so_voi_luot_truoc | — | — | 12/12 |
| ten_co_that | — | 12/12 | 11/12 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 0/0 · Mức 2 9/12 · Mức 3 7/12
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 0/0 · Mức 2 9/12 · Mức 3 7/12
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.041, lớn nhất 0.078 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 0.0, Mức 2 249.8, Mức 3 455.5

## Phản hồi chưa đạt (kiểm tra nào trượt)

- D05 · Mức 3: m3_todo_gan_buoc
- D07 · Mức 3: m3_khung_la_python_hop_le
- D09 · Mức 3: m3_khung_la_python_hop_le
- D11 · Mức 2: m2_co_doi_chung
- D11 · Mức 3: ten_co_that
- D12 · Mức 2: do_dai, m2_co_doi_chung
- D12 · Mức 3: m3_co_thuat_toan_chi_tiet
- D15 · Mức 2: m2_co_doi_chung

Ghi chú: v5.12 Mức 2-3, dữ liệu giả lập
