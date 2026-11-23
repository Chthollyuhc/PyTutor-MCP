# Đo 3 mức gợi ý — `v512_after`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-22T16:20:34 · commit `b0fa829` · chế độ **offline** · tập **dev** · 15 kịch bản, 44 phản hồi · nguồn: {"Pedagogical-Rule-Engine (Offline Fallback)": 44}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| bam_de_bai_cua_giang_vien | 1/1 | 1/1 | 1/1 |
| do_dai | 15/15 | 14/14 | 15/15 |
| dung_mot_buoc_ke_tiep | 15/15 | 14/14 | 15/15 |
| khong_chep_lai_chu_thich | 2/2 | 2/2 | 2/2 |
| khong_chuong_trinh_hoan_chinh | 14/14 | 14/14 | — |
| khong_cum_chi_cach_sua | 14/14 | 14/14 | 14/14 |
| khong_lap_voi_luot_truoc | 1/1 | 13/13 | 15/15 |
| khong_lo_bieu_thuc_loi_giai | 15/15 | 14/14 | 15/15 |
| khong_nhan_xet_nang_luc | 15/15 | 14/14 | 15/15 |
| khung_muc_tieu_bang_chung_buoc | 15/15 | 14/14 | 15/15 |
| m1_khong_bang_chung_test_cu_the | 13/13 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 14/14 | — | — |
| m1_khong_khoi_code | 14/14 | — | — |
| m1_khong_trich_dong_code | 14/14 | — | — |
| m1_neu_khai_niem | 14/14 | — | — |
| m2_co_bang_chung_thuc_thi | — | 13/13 | — |
| m2_co_doi_chung | — | 8/8 | — |
| m2_dong_dung_cho_loi | — | 13/13 | — |
| m2_dung_mot_dong_that | — | 13/13 | — |
| m2_khong_khoi_code_3_dong | — | 14/14 | — |
| m3_co_khung_todo | — | — | 14/14 |
| m3_co_thuat_toan_chi_tiet | — | — | 14/14 |
| m3_dan_y_4_buoc_khop_bai | — | — | 14/14 |
| m3_khong_code_trong_loi | — | — | 14/14 |
| m3_khung_khong_dat_het_test | — | — | 14/14 |
| m3_khung_la_python_hop_le | — | — | 14/14 |
| m3_todo_gan_buoc | — | — | 14/14 |
| tang_tien_so_voi_luot_truoc | — | 12/12 | 14/14 |
| ten_co_that | — | 14/14 | 15/15 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 15/15 · Mức 2 14/14 · Mức 3 15/15
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 15/15 · Mức 2 14/14 · Mức 3 15/15
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.074, lớn nhất 0.219 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 161.7, Mức 2 232.6, Mức 3 563.6

## Phản hồi chưa đạt (kiểm tra nào trượt)

