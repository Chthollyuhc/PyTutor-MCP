# Đo 3 mức gợi ý — `before_real_dev_1`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T04:28:41 · commit `4c15c32` · chế độ **real** · tập **dev** · 15 kịch bản, 44 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 43, "Pedagogical-Rule-Engine (Output Guard Fallback)": 1}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| do_dai | 12/15 | 12/14 | 15/15 |
| dung_mot_buoc_ke_tiep | 0/15 | 2/14 | 0/15 |
| khong_chuong_trinh_hoan_chinh | 14/14 | 14/14 | — |
| khong_cum_chi_cach_sua | 14/14 | 14/14 | 10/14 |
| khong_lap_voi_luot_truoc | 1/1 | 13/13 | 15/15 |
| khong_lo_bieu_thuc_loi_giai | 14/15 | 14/14 | 13/15 |
| khong_nhan_xet_nang_luc | 15/15 | 14/14 | 15/15 |
| khung_muc_tieu_bang_chung_buoc | 11/15 | 14/14 | 12/15 |
| m1_khong_bang_chung_test_cu_the | 10/13 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 14/14 | — | — |
| m1_khong_khoi_code | 14/14 | — | — |
| m1_khong_trich_dong_code | 12/14 | — | — |
| m1_neu_khai_niem | 14/14 | — | — |
| m2_co_bang_chung_thuc_thi | — | 11/13 | — |
| m2_dong_dung_cho_loi | — | 10/13 | — |
| m2_dung_mot_dong_that | — | 10/13 | — |
| m2_khong_khoi_code_3_dong | — | 14/14 | — |
| m3_co_khung_todo | — | — | 14/14 |
| m3_dan_y_4_buoc_khop_bai | — | — | 7/14 |
| m3_khung_khong_dat_het_test | — | — | 14/14 |
| m3_khung_la_python_hop_le | — | — | 11/14 |
| tang_tien_so_voi_luot_truoc | — | 7/12 | 11/14 |
| ten_co_that | 14/15 | 13/14 | 14/15 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 0/15 · Mức 2 0/14 · Mức 3 0/15
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 5/15 · Mức 2 5/14 · Mức 3 3/15
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.056, lớn nhất 0.169 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 168.3, Mức 2 195.1, Mức 3 265.1

## Phản hồi chưa đạt (kiểm tra nào trượt)

- D01 · Mức 1: dung_mot_buoc_ke_tiep
- D01 · Mức 2: dung_mot_buoc_ke_tiep
- D01 · Mức 3: dung_mot_buoc_ke_tiep
- D02 · Mức 1: dung_mot_buoc_ke_tiep
- D02 · Mức 2: do_dai, tang_tien_so_voi_luot_truoc
- D02 · Mức 3: dung_mot_buoc_ke_tiep, m3_dan_y_4_buoc_khop_bai, m3_khung_la_python_hop_le, tang_tien_so_voi_luot_truoc
- D03 · Mức 1: khung_muc_tieu_bang_chung_buoc, dung_mot_buoc_ke_tiep
- D03 · Mức 1: dung_mot_buoc_ke_tiep
- D03 · Mức 2: dung_mot_buoc_ke_tiep, m2_co_bang_chung_thuc_thi, tang_tien_so_voi_luot_truoc
- D03 · Mức 3: khung_muc_tieu_bang_chung_buoc, dung_mot_buoc_ke_tiep
- D04 · Mức 1: dung_mot_buoc_ke_tiep, m1_khong_trich_dong_code
- D04 · Mức 2: dung_mot_buoc_ke_tiep
- D04 · Mức 3: dung_mot_buoc_ke_tiep, m3_dan_y_4_buoc_khop_bai
- D05 · Mức 1: khung_muc_tieu_bang_chung_buoc, dung_mot_buoc_ke_tiep, m1_khong_bang_chung_test_cu_the
- D05 · Mức 2: dung_mot_buoc_ke_tiep
- D05 · Mức 3: dung_mot_buoc_ke_tiep, khong_lo_bieu_thuc_loi_giai, khong_cum_chi_cach_sua, m3_dan_y_4_buoc_khop_bai, tang_tien_so_voi_luot_truoc
- D06 · Mức 1: dung_mot_buoc_ke_tiep
- D06 · Mức 2: dung_mot_buoc_ke_tiep, tang_tien_so_voi_luot_truoc
- D06 · Mức 3: dung_mot_buoc_ke_tiep, khong_cum_chi_cach_sua, m3_khung_la_python_hop_le
- D07 · Mức 1: dung_mot_buoc_ke_tiep, m1_khong_bang_chung_test_cu_the
- D07 · Mức 2: dung_mot_buoc_ke_tiep, tang_tien_so_voi_luot_truoc
- D07 · Mức 3: dung_mot_buoc_ke_tiep
- D08 · Mức 1: dung_mot_buoc_ke_tiep, ten_co_that
- D08 · Mức 2: dung_mot_buoc_ke_tiep, ten_co_that
- D08 · Mức 3: dung_mot_buoc_ke_tiep, ten_co_that
- D09 · Mức 2: do_dai, dung_mot_buoc_ke_tiep
- D09 · Mức 3: dung_mot_buoc_ke_tiep, khong_lo_bieu_thuc_loi_giai, m3_dan_y_4_buoc_khop_bai
- D10 · Mức 1: do_dai, khung_muc_tieu_bang_chung_buoc, dung_mot_buoc_ke_tiep
- D10 · Mức 3: dung_mot_buoc_ke_tiep
- D11 · Mức 1: do_dai, dung_mot_buoc_ke_tiep, m1_khong_trich_dong_code
- D11 · Mức 2: dung_mot_buoc_ke_tiep
- D11 · Mức 3: dung_mot_buoc_ke_tiep, m3_dan_y_4_buoc_khop_bai
- D12 · Mức 1: do_dai, dung_mot_buoc_ke_tiep, m1_khong_bang_chung_test_cu_the
- D12 · Mức 2: dung_mot_buoc_ke_tiep, m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D12 · Mức 3: dung_mot_buoc_ke_tiep, khong_cum_chi_cach_sua, m3_dan_y_4_buoc_khop_bai
- D13 · Mức 1: khung_muc_tieu_bang_chung_buoc, dung_mot_buoc_ke_tiep
- D13 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi, m2_co_bang_chung_thuc_thi, tang_tien_so_voi_luot_truoc
- D13 · Mức 3: khung_muc_tieu_bang_chung_buoc, dung_mot_buoc_ke_tiep, m3_khung_la_python_hop_le
- D14 · Mức 1: dung_mot_buoc_ke_tiep, khong_lo_bieu_thuc_loi_giai
- D14 · Mức 2: dung_mot_buoc_ke_tiep
- D14 · Mức 3: dung_mot_buoc_ke_tiep, m3_dan_y_4_buoc_khop_bai
- D15 · Mức 1: dung_mot_buoc_ke_tiep
- D15 · Mức 2: dung_mot_buoc_ke_tiep, m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D15 · Mức 3: khung_muc_tieu_bang_chung_buoc, dung_mot_buoc_ke_tiep, khong_cum_chi_cach_sua, tang_tien_so_voi_luot_truoc

Ghi chú: Gemini thật, mốc trước cải tiến, lần 1
