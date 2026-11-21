# Đo 3 mức gợi ý — `v511_real_verify_dev3`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T07:45:54 · commit `5106048` · chế độ **real** · tập **dev** · 1 kịch bản, 2 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 2}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| bam_de_bai_cua_giang_vien | 1/1 | 1/1 | — |
| do_dai | 1/1 | 1/1 | — |
| dung_mot_buoc_ke_tiep | 1/1 | 1/1 | — |
| khong_chuong_trinh_hoan_chinh | 1/1 | 1/1 | — |
| khong_cum_chi_cach_sua | 1/1 | 1/1 | — |
| khong_lap_voi_luot_truoc | — | 1/1 | — |
| khong_lo_bieu_thuc_loi_giai | 1/1 | 1/1 | — |
| khong_nhan_xet_nang_luc | 1/1 | 1/1 | — |
| khung_muc_tieu_bang_chung_buoc | 1/1 | 1/1 | — |
| m1_khong_chi_la_cau_hoi_suong | 1/1 | — | — |
| m1_khong_khoi_code | 1/1 | — | — |
| m1_khong_trich_dong_code | 1/1 | — | — |
| m1_neu_khai_niem | 1/1 | — | — |
| m2_khong_khoi_code_3_dong | — | 1/1 | — |
| ten_co_that | — | 1/1 | — |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 1/1 · Mức 2 1/1 · Mức 3 0/0
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 1/1 · Mức 2 1/1 · Mức 3 0/0
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.101, lớn nhất 0.101 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 150.0, Mức 2 162.0, Mức 3 0.0

## Phản hồi chưa đạt (kiểm tra nào trượt)


Ghi chú: v5.11: sau bộ chặn cấu trúc cho ca chưa viết code
