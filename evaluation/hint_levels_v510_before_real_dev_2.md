# Đo 3 mức gợi ý — `before_real_dev_2`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T04:32:38 · commit `4c15c32` · chế độ **real** · tập **dev** · 15 kịch bản, 44 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 42, "Pedagogical-Rule-Engine (Offline Fallback)": 1, "Pedagogical-Rule-Engine (Output Guard Fallback)": 1}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| do_dai | 10/15 | 13/14 | 15/15 |
| dung_mot_buoc_ke_tiep | 1/15 | 0/14 | 1/15 |
| khong_chep_lai_chu_thich | 2/2 | 2/2 | 2/2 |
| khong_chuong_trinh_hoan_chinh | 14/14 | 14/14 | — |
| khong_cum_chi_cach_sua | 14/14 | 14/14 | 13/14 |
| khong_lap_voi_luot_truoc | 1/1 | 13/13 | 15/15 |
| khong_lo_bieu_thuc_loi_giai | 13/15 | 14/14 | 13/15 |
| khong_nhan_xet_nang_luc | 15/15 | 14/14 | 15/15 |
| khung_muc_tieu_bang_chung_buoc | 14/15 | 14/14 | 14/15 |
| m1_khong_bang_chung_test_cu_the | 12/13 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 14/14 | — | — |
| m1_khong_khoi_code | 14/14 | — | — |
| m1_khong_trich_dong_code | 14/14 | — | — |
| m1_neu_khai_niem | 13/14 | — | — |
| m2_co_bang_chung_thuc_thi | — | 13/13 | — |
| m2_dong_dung_cho_loi | — | 11/13 | — |
| m2_dung_mot_dong_that | — | 10/13 | — |
| m2_khong_khoi_code_3_dong | — | 14/14 | — |
| m3_co_khung_todo | — | — | 14/14 |
| m3_dan_y_4_buoc_khop_bai | — | — | 12/14 |
| m3_khung_khong_dat_het_test | — | — | 14/14 |
| m3_khung_la_python_hop_le | — | — | 11/14 |
| tang_tien_so_voi_luot_truoc | — | 9/12 | 10/14 |
| ten_co_that | — | 14/14 | 15/15 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 0/15 · Mức 2 0/14 · Mức 3 0/15
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 8/15 · Mức 2 9/14 · Mức 3 7/15
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.053, lớn nhất 0.223 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 178.3, Mức 2 190.8, Mức 3 299.9

## Phản hồi chưa đạt (kiểm tra nào trượt)

- D01 · Mức 1: do_dai, khung_muc_tieu_bang_chung_buoc, dung_mot_buoc_ke_tiep
- D01 · Mức 2: dung_mot_buoc_ke_tiep
- D01 · Mức 3: dung_mot_buoc_ke_tiep
- D02 · Mức 1: dung_mot_buoc_ke_tiep
- D02 · Mức 2: dung_mot_buoc_ke_tiep, tang_tien_so_voi_luot_truoc
- D02 · Mức 3: khung_muc_tieu_bang_chung_buoc, dung_mot_buoc_ke_tiep, m3_khung_la_python_hop_le, tang_tien_so_voi_luot_truoc
- D03 · Mức 1: dung_mot_buoc_ke_tiep
- D03 · Mức 1: dung_mot_buoc_ke_tiep
- D03 · Mức 2: dung_mot_buoc_ke_tiep
- D03 · Mức 3: dung_mot_buoc_ke_tiep
- D04 · Mức 1: do_dai, dung_mot_buoc_ke_tiep
- D04 · Mức 2: dung_mot_buoc_ke_tiep
- D04 · Mức 3: dung_mot_buoc_ke_tiep
- D05 · Mức 1: dung_mot_buoc_ke_tiep, m1_khong_bang_chung_test_cu_the
- D05 · Mức 2: dung_mot_buoc_ke_tiep
- D05 · Mức 3: dung_mot_buoc_ke_tiep, khong_lo_bieu_thuc_loi_giai, khong_cum_chi_cach_sua, tang_tien_so_voi_luot_truoc
- D06 · Mức 1: dung_mot_buoc_ke_tiep
- D06 · Mức 2: dung_mot_buoc_ke_tiep
- D06 · Mức 3: dung_mot_buoc_ke_tiep
- D07 · Mức 1: dung_mot_buoc_ke_tiep
- D07 · Mức 2: dung_mot_buoc_ke_tiep, m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D07 · Mức 3: dung_mot_buoc_ke_tiep, m3_dan_y_4_buoc_khop_bai
- D08 · Mức 1: dung_mot_buoc_ke_tiep
- D08 · Mức 2: dung_mot_buoc_ke_tiep, m2_dung_mot_dong_that, tang_tien_so_voi_luot_truoc
- D08 · Mức 3: m3_dan_y_4_buoc_khop_bai, tang_tien_so_voi_luot_truoc
- D09 · Mức 2: dung_mot_buoc_ke_tiep
- D09 · Mức 3: dung_mot_buoc_ke_tiep, khong_lo_bieu_thuc_loi_giai
- D10 · Mức 1: dung_mot_buoc_ke_tiep
- D10 · Mức 3: dung_mot_buoc_ke_tiep
- D11 · Mức 1: do_dai, dung_mot_buoc_ke_tiep, khong_lo_bieu_thuc_loi_giai
- D11 · Mức 2: dung_mot_buoc_ke_tiep
- D11 · Mức 3: dung_mot_buoc_ke_tiep, tang_tien_so_voi_luot_truoc
- D12 · Mức 1: do_dai, dung_mot_buoc_ke_tiep
- D12 · Mức 2: dung_mot_buoc_ke_tiep, m2_dung_mot_dong_that, m2_dong_dung_cho_loi, tang_tien_so_voi_luot_truoc
- D12 · Mức 3: dung_mot_buoc_ke_tiep, m3_khung_la_python_hop_le
- D13 · Mức 1: m1_neu_khai_niem
- D13 · Mức 2: do_dai, dung_mot_buoc_ke_tiep
- D13 · Mức 3: dung_mot_buoc_ke_tiep, m3_khung_la_python_hop_le
- D14 · Mức 1: do_dai, dung_mot_buoc_ke_tiep, khong_lo_bieu_thuc_loi_giai
- D14 · Mức 2: dung_mot_buoc_ke_tiep
- D14 · Mức 3: dung_mot_buoc_ke_tiep
- D15 · Mức 1: dung_mot_buoc_ke_tiep
- D15 · Mức 2: dung_mot_buoc_ke_tiep
- D15 · Mức 3: dung_mot_buoc_ke_tiep

Ghi chú: Gemini thật, mốc trước cải tiến, lần 2
