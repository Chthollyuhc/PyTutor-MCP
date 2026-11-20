# Đo 3 mức gợi ý — `r1_real_dev`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T04:58:36 · commit `528bc92` · chế độ **real** · tập **dev** · 15 kịch bản, 44 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 44}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| do_dai | 2/15 | 14/14 | 15/15 |
| dung_mot_buoc_ke_tiep | 14/15 | 14/14 | 14/15 |
| khong_chep_lai_chu_thich | 2/2 | 2/2 | 2/2 |
| khong_chuong_trinh_hoan_chinh | 14/14 | 14/14 | — |
| khong_cum_chi_cach_sua | 11/14 | 13/14 | 14/14 |
| khong_lap_voi_luot_truoc | 1/1 | 13/13 | 15/15 |
| khong_lo_bieu_thuc_loi_giai | 14/15 | 14/14 | 15/15 |
| khong_nhan_xet_nang_luc | 15/15 | 14/14 | 15/15 |
| khung_muc_tieu_bang_chung_buoc | 15/15 | 14/14 | 15/15 |
| m1_khong_bang_chung_test_cu_the | 9/13 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 14/14 | — | — |
| m1_khong_khoi_code | 14/14 | — | — |
| m1_khong_trich_dong_code | 14/14 | — | — |
| m1_neu_khai_niem | 13/14 | — | — |
| m2_co_bang_chung_thuc_thi | — | 13/13 | — |
| m2_dong_dung_cho_loi | — | 12/13 | — |
| m2_dung_mot_dong_that | — | 12/13 | — |
| m2_khong_khoi_code_3_dong | — | 14/14 | — |
| m3_co_khung_todo | — | — | 14/14 |
| m3_dan_y_4_buoc_khop_bai | — | — | 14/14 |
| m3_khung_khong_dat_het_test | — | — | 14/14 |
| m3_khung_la_python_hop_le | — | — | 13/14 |
| tang_tien_so_voi_luot_truoc | — | 12/12 | 14/14 |
| ten_co_that | — | 14/14 | 14/15 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 1/15 · Mức 2 12/14 · Mức 3 12/15
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 2/15 · Mức 2 12/14 · Mức 3 13/15
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.109, lớn nhất 0.278 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 213.9, Mức 2 199.1, Mức 3 222.1

## Phản hồi chưa đạt (kiểm tra nào trượt)

- D01 · Mức 1: do_dai
- D02 · Mức 2: m2_dung_mot_dong_that, m2_dong_dung_cho_loi
- D03 · Mức 1: do_dai
- D03 · Mức 1: do_dai, m1_khong_bang_chung_test_cu_the
- D04 · Mức 1: do_dai, m1_khong_bang_chung_test_cu_the
- D05 · Mức 1: do_dai, m1_khong_bang_chung_test_cu_the
- D06 · Mức 1: do_dai
- D07 · Mức 1: do_dai
- D08 · Mức 1: do_dai, khong_cum_chi_cach_sua
- D09 · Mức 3: m3_khung_la_python_hop_le
- D10 · Mức 1: dung_mot_buoc_ke_tiep
- D10 · Mức 3: dung_mot_buoc_ke_tiep
- D11 · Mức 1: do_dai, khong_cum_chi_cach_sua, m1_neu_khai_niem
- D11 · Mức 3: ten_co_that
- D12 · Mức 1: do_dai, khong_lo_bieu_thuc_loi_giai
- D13 · Mức 1: do_dai, m1_khong_bang_chung_test_cu_the
- D14 · Mức 1: do_dai
- D15 · Mức 1: do_dai, khong_cum_chi_cach_sua
- D15 · Mức 2: khong_cum_chi_cach_sua

Ghi chú: Vòng 1: Gemini thật sau khi đổi prompt/bằng chứng/vết chạy
