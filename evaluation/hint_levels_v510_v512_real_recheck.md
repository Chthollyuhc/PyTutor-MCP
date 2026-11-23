# Đo 3 mức gợi ý — `v512_real_recheck`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-22T16:44:53 · commit `b0fa829` · chế độ **real** · tập **dev** · 4 kịch bản, 8 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 6, "Pedagogical-Rule-Engine (Offline Fallback)": 1, "Pedagogical-Rule-Engine (Output Guard Fallback)": 1}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| do_dai | — | 4/4 | 4/4 |
| dung_mot_buoc_ke_tiep | — | 4/4 | 4/4 |
| khong_chep_lai_chu_thich | — | 1/2 | 1/2 |
| khong_chuong_trinh_hoan_chinh | — | 4/4 | — |
| khong_cum_chi_cach_sua | — | 3/4 | 3/4 |
| khong_lap_voi_luot_truoc | — | — | 4/4 |
| khong_lo_bieu_thuc_loi_giai | — | 4/4 | 4/4 |
| khong_nhan_xet_nang_luc | — | 4/4 | 4/4 |
| khung_muc_tieu_bang_chung_buoc | — | 4/4 | 4/4 |
| m2_co_bang_chung_thuc_thi | — | 4/4 | — |
| m2_co_doi_chung | — | 2/3 | — |
| m2_dong_dung_cho_loi | — | 4/4 | — |
| m2_dung_mot_dong_that | — | 4/4 | — |
| m2_khong_khoi_code_3_dong | — | 4/4 | — |
| m3_co_khung_todo | — | — | 4/4 |
| m3_co_thuat_toan_chi_tiet | — | — | 4/4 |
| m3_dan_y_4_buoc_khop_bai | — | — | 4/4 |
| m3_khong_code_trong_loi | — | — | 4/4 |
| m3_khung_khong_dat_het_test | — | — | 4/4 |
| m3_khung_la_python_hop_le | — | — | 4/4 |
| m3_todo_gan_buoc | — | — | 4/4 |
| tang_tien_so_voi_luot_truoc | — | — | 4/4 |
| ten_co_that | — | 4/4 | 3/4 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 0/0 · Mức 2 1/4 · Mức 3 3/4
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 0/0 · Mức 2 1/4 · Mức 3 3/4
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.047, lớn nhất 0.1 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 0.0, Mức 2 248.8, Mức 3 493.8

## Phản hồi chưa đạt (kiểm tra nào trượt)

- D09 · Mức 2: khong_cum_chi_cach_sua
- D11 · Mức 2: khong_chep_lai_chu_thich
- D11 · Mức 3: khong_chep_lai_chu_thich, ten_co_that, khong_cum_chi_cach_sua
- D12 · Mức 2: m2_co_doi_chung

Ghi chú: v5.12 đo lại sau sửa
