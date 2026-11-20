# Đo 3 mức gợi ý — `before_real_holdout`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T04:34:26 · commit `4c15c32` · chế độ **real** · tập **holdout** · 7 kịch bản, 21 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 20, "Pedagogical-Rule-Engine (Output Guard Fallback)": 1}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| do_dai | 6/7 | 6/7 | 7/7 |
| dung_mot_buoc_ke_tiep | 0/7 | 1/7 | 0/7 |
| khong_chuong_trinh_hoan_chinh | 7/7 | 7/7 | — |
| khong_cum_chi_cach_sua | 7/7 | 7/7 | 6/7 |
| khong_lap_voi_luot_truoc | — | 7/7 | 7/7 |
| khong_lo_bieu_thuc_loi_giai | 7/7 | 7/7 | 6/7 |
| khong_nhan_xet_nang_luc | 7/7 | 7/7 | 7/7 |
| khung_muc_tieu_bang_chung_buoc | 7/7 | 7/7 | 7/7 |
| m1_khong_bang_chung_test_cu_the | 6/7 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 7/7 | — | — |
| m1_khong_khoi_code | 7/7 | — | — |
| m1_khong_trich_dong_code | 7/7 | — | — |
| m1_neu_khai_niem | 7/7 | — | — |
| m2_co_bang_chung_thuc_thi | — | 5/7 | — |
| m2_dong_dung_cho_loi | — | 4/7 | — |
| m2_dung_mot_dong_that | — | 4/7 | — |
| m2_khong_khoi_code_3_dong | — | 7/7 | — |
| m3_co_khung_todo | — | — | 7/7 |
| m3_dan_y_4_buoc_khop_bai | — | — | 6/7 |
| m3_khung_khong_dat_het_test | — | — | 7/7 |
| m3_khung_la_python_hop_le | — | — | 6/7 |
| tang_tien_so_voi_luot_truoc | — | 5/7 | 4/7 |
| ten_co_that | 7/7 | 7/7 | 7/7 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 0/7 · Mức 2 0/7 · Mức 3 0/7
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 5/7 · Mức 2 3/7 · Mức 3 2/7
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.037, lớn nhất 0.08 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 163.3, Mức 2 195.7, Mức 3 314.4

## Phản hồi chưa đạt (kiểm tra nào trượt)

- H01 · Mức 1: dung_mot_buoc_ke_tiep
- H01 · Mức 2: do_dai, dung_mot_buoc_ke_tiep
- H01 · Mức 3: dung_mot_buoc_ke_tiep, m3_dan_y_4_buoc_khop_bai, tang_tien_so_voi_luot_truoc
- H02 · Mức 1: dung_mot_buoc_ke_tiep
- H02 · Mức 2: dung_mot_buoc_ke_tiep
- H02 · Mức 3: dung_mot_buoc_ke_tiep
- H03 · Mức 1: dung_mot_buoc_ke_tiep
- H03 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi, m2_co_bang_chung_thuc_thi, tang_tien_so_voi_luot_truoc
- H03 · Mức 3: dung_mot_buoc_ke_tiep, khong_cum_chi_cach_sua
- H04 · Mức 1: dung_mot_buoc_ke_tiep
- H04 · Mức 2: dung_mot_buoc_ke_tiep
- H04 · Mức 3: dung_mot_buoc_ke_tiep, khong_lo_bieu_thuc_loi_giai, m3_khung_la_python_hop_le
- H05 · Mức 1: do_dai, dung_mot_buoc_ke_tiep
- H05 · Mức 2: dung_mot_buoc_ke_tiep, m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- H05 · Mức 3: dung_mot_buoc_ke_tiep, tang_tien_so_voi_luot_truoc
- H06 · Mức 1: dung_mot_buoc_ke_tiep, m1_khong_bang_chung_test_cu_the
- H06 · Mức 2: dung_mot_buoc_ke_tiep
- H06 · Mức 3: dung_mot_buoc_ke_tiep
- H07 · Mức 1: dung_mot_buoc_ke_tiep
- H07 · Mức 2: dung_mot_buoc_ke_tiep, m2_dung_mot_dong_that, m2_dong_dung_cho_loi, m2_co_bang_chung_thuc_thi, tang_tien_so_voi_luot_truoc
- H07 · Mức 3: dung_mot_buoc_ke_tiep, tang_tien_so_voi_luot_truoc

Ghi chú: Gemini thật, mốc trước cải tiến, tập giữ riêng
