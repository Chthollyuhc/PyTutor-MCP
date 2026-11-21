# Đo 3 mức gợi ý — `before_offline_dev`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T04:23:54 · commit `4c15c32` · chế độ **offline** · tập **dev** · 15 kịch bản, 44 phản hồi · nguồn: {"Pedagogical-Rule-Engine (Offline Fallback)": 44}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| bam_de_bai_cua_giang_vien | 0/1 | 0/1 | 1/1 |
| do_dai | 15/15 | 13/14 | 13/15 |
| dung_mot_buoc_ke_tiep | 15/15 | 14/14 | 15/15 |
| khong_chep_lai_chu_thich | 2/2 | 2/2 | 2/2 |
| khong_chuong_trinh_hoan_chinh | 14/14 | 14/14 | — |
| khong_cum_chi_cach_sua | 14/14 | 14/14 | 14/14 |
| khong_lap_voi_luot_truoc | 0/1 | 10/13 | 12/15 |
| khong_lo_bieu_thuc_loi_giai | 15/15 | 14/14 | 15/15 |
| khong_nhan_xet_nang_luc | 15/15 | 14/14 | 15/15 |
| khung_muc_tieu_bang_chung_buoc | 14/15 | 13/14 | 15/15 |
| m1_khong_bang_chung_test_cu_the | 13/13 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 13/14 | — | — |
| m1_khong_khoi_code | 14/14 | — | — |
| m1_khong_trich_dong_code | 14/14 | — | — |
| m1_neu_khai_niem | 10/14 | — | — |
| m2_co_bang_chung_thuc_thi | — | 11/13 | — |
| m2_dong_dung_cho_loi | — | 0/13 | — |
| m2_dung_mot_dong_that | — | 0/13 | — |
| m2_khong_khoi_code_3_dong | — | 14/14 | — |
| m3_co_khung_todo | — | — | 12/14 |
| m3_dan_y_4_buoc_khop_bai | — | — | 0/14 |
| m3_khung_khong_dat_het_test | — | — | 12/12 |
| m3_khung_la_python_hop_le | — | — | 12/12 |
| tang_tien_so_voi_luot_truoc | — | 9/12 | 12/14 |
| ten_co_that | — | 14/14 | 15/15 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 9/15 · Mức 2 0/14 · Mức 3 0/15
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 9/15 · Mức 2 0/14 · Mức 3 0/15
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.321, lớn nhất 1.0 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 131.9, Mức 2 126.6, Mức 3 240.6

## Phản hồi chưa đạt (kiểm tra nào trượt)

- D01 · Mức 1: khung_muc_tieu_bang_chung_buoc, bam_de_bai_cua_giang_vien
- D01 · Mức 2: khung_muc_tieu_bang_chung_buoc, bam_de_bai_cua_giang_vien, khong_lap_voi_luot_truoc
- D01 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D02 · Mức 2: do_dai, m2_dung_mot_dong_that, m2_dong_dung_cho_loi, khong_lap_voi_luot_truoc, tang_tien_so_voi_luot_truoc
- D02 · Mức 3: do_dai, m3_dan_y_4_buoc_khop_bai, m3_co_khung_todo, khong_lap_voi_luot_truoc, tang_tien_so_voi_luot_truoc
- D03 · Mức 1: m1_neu_khai_niem
- D03 · Mức 1: m1_neu_khai_niem, khong_lap_voi_luot_truoc
- D03 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D03 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D04 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D04 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D05 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D05 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D06 · Mức 1: m1_khong_chi_la_cau_hoi_suong
- D06 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi, m2_co_bang_chung_thuc_thi, khong_lap_voi_luot_truoc, tang_tien_so_voi_luot_truoc
- D06 · Mức 3: do_dai, m3_dan_y_4_buoc_khop_bai, m3_co_khung_todo, khong_lap_voi_luot_truoc, tang_tien_so_voi_luot_truoc
- D07 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D07 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D08 · Mức 1: m1_neu_khai_niem
- D08 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D08 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D09 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D09 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D10 · Mức 3: khong_lap_voi_luot_truoc
- D11 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D11 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D12 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D12 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D13 · Mức 1: m1_neu_khai_niem
- D13 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi, m2_co_bang_chung_thuc_thi, tang_tien_so_voi_luot_truoc
- D13 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D14 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D14 · Mức 3: m3_dan_y_4_buoc_khop_bai
- D15 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D15 · Mức 3: m3_dan_y_4_buoc_khop_bai

Ghi chú: Mốc trước cải tiến, mã tại commit chứa bộ đo
