# Đo 3 mức gợi ý — `v511_real_verify_dev4`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T07:48:47 · commit `e4cb260` · chế độ **real** · tập **dev** · 5 kịch bản, 10 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 10}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| bam_de_bai_cua_giang_vien | 1/1 | 1/1 | — |
| do_dai | 3/5 | 5/5 | — |
| dung_mot_buoc_ke_tiep | 5/5 | 5/5 | — |
| khong_chuong_trinh_hoan_chinh | 5/5 | 5/5 | — |
| khong_cum_chi_cach_sua | 5/5 | 5/5 | — |
| khong_lap_voi_luot_truoc | — | 5/5 | — |
| khong_lo_bieu_thuc_loi_giai | 5/5 | 5/5 | — |
| khong_nhan_xet_nang_luc | 5/5 | 5/5 | — |
| khung_muc_tieu_bang_chung_buoc | 5/5 | 5/5 | — |
| m1_khong_bang_chung_test_cu_the | 4/4 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 5/5 | — | — |
| m1_khong_khoi_code | 5/5 | — | — |
| m1_khong_trich_dong_code | 5/5 | — | — |
| m1_neu_khai_niem | 4/5 | — | — |
| m2_co_bang_chung_thuc_thi | — | 4/4 | — |
| m2_dong_dung_cho_loi | — | 4/4 | — |
| m2_dung_mot_dong_that | — | 4/4 | — |
| m2_khong_khoi_code_3_dong | — | 5/5 | — |
| tang_tien_so_voi_luot_truoc | — | 4/4 | — |
| ten_co_that | — | 5/5 | — |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 3/5 · Mức 2 5/5 · Mức 3 0/0
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 3/5 · Mức 2 5/5 · Mức 3 0/0
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.079, lớn nhất 0.099 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 185.6, Mức 2 189.4, Mức 3 0.0

## Phản hồi chưa đạt (kiểm tra nào trượt)

- D05 · Mức 1: do_dai, m1_neu_khai_niem
- D08 · Mức 1: do_dai

Ghi chú: v5.11: mẫu mở rộng, Mức 1-2, 5 kịch bản dev
