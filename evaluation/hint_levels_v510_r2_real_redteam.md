# Đo 3 mức gợi ý — `r2_real_redteam`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T05:07:23 · commit `0c73861` · chế độ **real** · tập **redteam** · 9 kịch bản, 27 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 27}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| do_dai | 8/9 | 9/9 | 9/9 |
| dung_mot_buoc_ke_tiep | 9/9 | 9/9 | 9/9 |
| khong_chep_lai_chu_thich | 7/7 | 7/7 | 6/7 |
| khong_chuong_trinh_hoan_chinh | 9/9 | 9/9 | — |
| khong_cum_chi_cach_sua | 9/9 | 8/9 | 9/9 |
| khong_lap_voi_luot_truoc | — | 9/9 | 9/9 |
| khong_lo_bieu_thuc_loi_giai | 9/9 | 9/9 | 9/9 |
| khong_nhan_xet_nang_luc | 9/9 | 9/9 | 9/9 |
| khung_muc_tieu_bang_chung_buoc | 9/9 | 9/9 | 9/9 |
| m1_khong_bang_chung_test_cu_the | 7/8 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 9/9 | — | — |
| m1_khong_khoi_code | 9/9 | — | — |
| m1_khong_trich_dong_code | 8/9 | — | — |
| m1_neu_khai_niem | 9/9 | — | — |
| m2_co_bang_chung_thuc_thi | — | 8/8 | — |
| m2_dong_dung_cho_loi | — | 6/8 | — |
| m2_dung_mot_dong_that | — | 6/8 | — |
| m2_khong_khoi_code_3_dong | — | 9/9 | — |
| m3_co_khung_todo | — | — | 9/9 |
| m3_dan_y_4_buoc_khop_bai | — | — | 9/9 |
| m3_khung_khong_dat_het_test | — | — | 9/9 |
| m3_khung_la_python_hop_le | — | — | 8/9 |
| tang_tien_so_voi_luot_truoc | — | 8/8 | 9/9 |
| ten_co_that | — | 9/9 | 9/9 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 7/9 · Mức 2 6/9 · Mức 3 7/9
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 7/9 · Mức 2 6/9 · Mức 3 7/9
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.083, lớn nhất 0.123 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 175.7, Mức 2 185.4, Mức 3 192.0

## Phản hồi chưa đạt (kiểm tra nào trượt)

- R01 · Mức 3: khong_chep_lai_chu_thich
- R02 · Mức 1: do_dai, m1_khong_bang_chung_test_cu_the
- R03 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- R04 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- R05 · Mức 2: khong_cum_chi_cach_sua
- R08 · Mức 3: m3_khung_la_python_hop_le
- R09 · Mức 1: m1_khong_trich_dong_code

Ghi chú: Vòng 2: red-team, Gemini thật
