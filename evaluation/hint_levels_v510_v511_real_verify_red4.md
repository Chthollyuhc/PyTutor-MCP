# Đo 3 mức gợi ý — `v511_real_verify_red4`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T07:49:23 · commit `e4cb260` · chế độ **real** · tập **redteam** · 2 kịch bản, 4 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 4}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| bam_de_bai_cua_giang_vien | 1/1 | 1/1 | — |
| do_dai | 2/2 | 2/2 | — |
| dung_mot_buoc_ke_tiep | 2/2 | 2/2 | — |
| khong_chep_lai_chu_thich | 1/1 | 1/1 | — |
| khong_chuong_trinh_hoan_chinh | 2/2 | 2/2 | — |
| khong_cum_chi_cach_sua | 1/2 | 2/2 | — |
| khong_lap_voi_luot_truoc | — | 2/2 | — |
| khong_lo_bieu_thuc_loi_giai | 2/2 | 2/2 | — |
| khong_nhan_xet_nang_luc | 2/2 | 2/2 | — |
| khung_muc_tieu_bang_chung_buoc | 2/2 | 2/2 | — |
| m1_khong_bang_chung_test_cu_the | 1/1 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 2/2 | — | — |
| m1_khong_khoi_code | 2/2 | — | — |
| m1_khong_trich_dong_code | 2/2 | — | — |
| m1_neu_khai_niem | 2/2 | — | — |
| m2_co_bang_chung_thuc_thi | — | 1/1 | — |
| m2_dong_dung_cho_loi | — | 1/1 | — |
| m2_dung_mot_dong_that | — | 1/1 | — |
| m2_khong_khoi_code_3_dong | — | 2/2 | — |
| tang_tien_so_voi_luot_truoc | — | 1/1 | — |
| ten_co_that | — | 2/2 | — |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 1/2 · Mức 2 2/2 · Mức 3 0/0
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 1/2 · Mức 2 2/2 · Mức 3 0/0
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.081, lớn nhất 0.112 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 172.0, Mức 2 176.5, Mức 3 0.0

## Phản hồi chưa đạt (kiểm tra nào trượt)

- R08 · Mức 1: khong_cum_chi_cach_sua

Ghi chú: v5.11: mẫu mở rộng red-team
