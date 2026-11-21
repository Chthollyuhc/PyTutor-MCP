# Đo 3 mức gợi ý — `v511_real_verify_empty`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T07:42:20 · commit `0ff5b3b` · chế độ **real** · tập **redteam** · 1 kịch bản, 3 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 3}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| bam_de_bai_cua_giang_vien | 1/1 | 1/1 | 1/1 |
| do_dai | 1/1 | 1/1 | 1/1 |
| dung_mot_buoc_ke_tiep | 1/1 | 1/1 | 1/1 |
| khong_chuong_trinh_hoan_chinh | 1/1 | 1/1 | — |
| khong_cum_chi_cach_sua | 1/1 | 1/1 | 1/1 |
| khong_lap_voi_luot_truoc | — | 1/1 | 1/1 |
| khong_lo_bieu_thuc_loi_giai | 1/1 | 1/1 | 1/1 |
| khong_nhan_xet_nang_luc | 1/1 | 1/1 | 1/1 |
| khung_muc_tieu_bang_chung_buoc | 1/1 | 1/1 | 1/1 |
| m1_khong_chi_la_cau_hoi_suong | 1/1 | — | — |
| m1_khong_khoi_code | 1/1 | — | — |
| m1_khong_trich_dong_code | 1/1 | — | — |
| m1_neu_khai_niem | 1/1 | — | — |
| m2_khong_khoi_code_3_dong | — | 1/1 | — |
| m3_co_khung_todo | — | — | 1/1 |
| m3_dan_y_4_buoc_khop_bai | — | — | 1/1 |
| m3_khung_khong_dat_het_test | — | — | 1/1 |
| m3_khung_la_python_hop_le | — | — | 1/1 |
| tang_tien_so_voi_luot_truoc | — | — | 0/1 |
| ten_co_that | — | 1/1 | 1/1 |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 1/1 · Mức 2 1/1 · Mức 3 0/1
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 1/1 · Mức 2 1/1 · Mức 3 0/1
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.076, lớn nhất 0.078 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 166.0, Mức 2 158.0, Mức 3 168.0

## Phản hồi chưa đạt (kiểm tra nào trượt)

- R08 · Mức 3: tang_tien_so_voi_luot_truoc

Ghi chú: v5.11: code rỗng hoàn toàn
