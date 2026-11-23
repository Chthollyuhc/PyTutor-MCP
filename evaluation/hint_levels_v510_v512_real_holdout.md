# Đo 3 mức gợi ý — `v512_real_holdout`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-22T16:39:14 · commit `b0fa829` · chế độ **real** · tập **holdout** · 7 kịch bản, 14 phản hồi · nguồn: {"Pedagogical-Rule-Engine (Offline Fallback)": 2, "Pedagogical-Rule-Engine (Output Guard Fallback)": 4, "Google gemini-3.5-flash-lite": 8}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| do_dai | — | 7/7 | 7/7 |
| dung_mot_buoc_ke_tiep | — | 7/7 | 7/7 |
| khong_chuong_trinh_hoan_chinh | — | 7/7 | — |
| khong_cum_chi_cach_sua | — | 6/7 | 7/7 |
| khong_lap_voi_luot_truoc | — | — | 7/7 |
| khong_lo_bieu_thuc_loi_giai | — | 7/7 | 7/7 |
| khong_nhan_xet_nang_luc | — | 7/7 | 7/7 |
| khung_muc_tieu_bang_chung_buoc | — | 7/7 | 7/7 |
| m2_co_bang_chung_thuc_thi | — | 7/7 | — |
| m2_co_doi_chung | — | 3/3 | — |
| m2_dong_dung_cho_loi | — | 3/7 | — |
| m2_dung_mot_dong_that | — | 6/7 | — |
| m2_khong_khoi_code_3_dong | — | 7/7 | — |
| m3_co_khung_todo | — | — | 7/7 |
| m3_co_thuat_toan_chi_tiet | — | — | 7/7 |
| m3_dan_y_4_buoc_khop_bai | — | — | 7/7 |
| m3_khong_code_trong_loi | — | — | 7/7 |
| m3_khung_khong_dat_het_test | — | — | 7/7 |
| m3_khung_la_python_hop_le | — | — | 7/7 |
| m3_todo_gan_buoc | — | — | 7/7 |
| tang_tien_so_voi_luot_truoc | — | — | 7/7 |
| ten_co_that | — | 7/7 | 6/7 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 0/0 · Mức 2 3/7 · Mức 3 6/7
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 0/0 · Mức 2 3/7 · Mức 3 6/7
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.033, lớn nhất 0.042 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 0.0, Mức 2 249.7, Mức 3 524.6

## Phản hồi chưa đạt (kiểm tra nào trượt)

- H01 · Mức 2: m2_dong_dung_cho_loi
- H02 · Mức 3: ten_co_that
- H03 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- H04 · Mức 2: m2_dong_dung_cho_loi
- H06 · Mức 2: khong_cum_chi_cach_sua, m2_dong_dung_cho_loi

Ghi chú: v5.12 Mức 2-3, dữ liệu giả lập
