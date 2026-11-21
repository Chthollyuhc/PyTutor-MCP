# Đo 3 mức gợi ý — `v511_real_verify_dev`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T07:41:52 · commit `0ff5b3b` · chế độ **real** · tập **dev** · 2 kịch bản, 7 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 7}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| bam_de_bai_cua_giang_vien | 1/1 | 1/1 | 1/1 |
| do_dai | 1/3 | 2/2 | 2/2 |
| dung_mot_buoc_ke_tiep | 3/3 | 2/2 | 2/2 |
| khong_chuong_trinh_hoan_chinh | 3/3 | 2/2 | — |
| khong_cum_chi_cach_sua | 3/3 | 2/2 | 2/2 |
| khong_lap_voi_luot_truoc | 1/1 | 2/2 | 2/2 |
| khong_lo_bieu_thuc_loi_giai | 3/3 | 2/2 | 2/2 |
| khong_nhan_xet_nang_luc | 3/3 | 2/2 | 2/2 |
| khung_muc_tieu_bang_chung_buoc | 3/3 | 2/2 | 2/2 |
| m1_khong_bang_chung_test_cu_the | 2/2 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 3/3 | — | — |
| m1_khong_khoi_code | 3/3 | — | — |
| m1_khong_trich_dong_code | 3/3 | — | — |
| m1_neu_khai_niem | 3/3 | — | — |
| m2_co_bang_chung_thuc_thi | — | 1/1 | — |
| m2_dong_dung_cho_loi | — | 1/1 | — |
| m2_dung_mot_dong_that | — | 1/1 | — |
| m2_khong_khoi_code_3_dong | — | 2/2 | — |
| m3_co_khung_todo | — | — | 2/2 |
| m3_dan_y_4_buoc_khop_bai | — | — | 2/2 |
| m3_khung_khong_dat_het_test | — | — | 2/2 |
| m3_khung_la_python_hop_le | — | — | 1/2 |
| tang_tien_so_voi_luot_truoc | — | 1/1 | 2/2 |
| ten_co_that | — | 2/2 | 2/2 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 1/3 · Mức 2 2/2 · Mức 3 1/2
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 1/3 · Mức 2 2/2 · Mức 3 1/2
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.091, lớn nhất 0.177 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 189.0, Mức 2 173.0, Mức 3 193.5

## Phản hồi chưa đạt (kiểm tra nào trượt)

- D01 · Mức 3: m3_khung_la_python_hop_le
- D03 · Mức 1: do_dai
- D03 · Mức 1: do_dai

Ghi chú: v5.11: kiểm chứng với Gemini thật (ca chưa viết code D01, ca sai cận D03)
