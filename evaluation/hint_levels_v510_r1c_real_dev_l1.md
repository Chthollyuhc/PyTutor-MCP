# Đo 3 mức gợi ý — `r1c_real_dev_l1`

> Sinh bởi `evaluate_hint_levels.py` lúc 2026-11-21T05:05:17 · commit `0c73861` · chế độ **real** · tập **dev** · 14 kịch bản, 15 phản hồi · nguồn: {"Google gemini-3.5-flash-lite": 15}

Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.

| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |
|---|---|---|---|
| do_dai | 12/15 | — | — |
| dung_mot_buoc_ke_tiep | 14/15 | — | — |
| khong_chep_lai_chu_thich | 2/2 | — | — |
| khong_chuong_trinh_hoan_chinh | 14/14 | — | — |
| khong_cum_chi_cach_sua | 13/14 | — | — |
| khong_lap_voi_luot_truoc | 1/1 | — | — |
| khong_lo_bieu_thuc_loi_giai | 15/15 | — | — |
| khong_nhan_xet_nang_luc | 15/15 | — | — |
| khung_muc_tieu_bang_chung_buoc | 15/15 | — | — |
| m1_khong_bang_chung_test_cu_the | 13/13 | — | — |
| m1_khong_chi_la_cau_hoi_suong | 14/14 | — | — |
| m1_khong_khoi_code | 14/14 | — | — |
| m1_khong_trich_dong_code | 14/14 | — | — |
| m1_neu_khai_niem | 13/14 | — | — |

**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 9/15 · Mức 2 0/0 · Mức 3 0/0
**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 10/15 · Mức 2 0/0 · Mức 3 0/0
· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình 0.235, lớn nhất 0.235 (ngưỡng < 0.3)
· Số từ trung bình: Mức 1 174.2, Mức 2 0.0, Mức 3 0.0

## Phản hồi chưa đạt (kiểm tra nào trượt)

- D02 · Mức 1: do_dai
- D05 · Mức 1: m1_neu_khai_niem
- D10 · Mức 1: dung_mot_buoc_ke_tiep
- D11 · Mức 1: do_dai
- D12 · Mức 1: do_dai
- D15 · Mức 1: khong_cum_chi_cach_sua

Ghi chú: Vòng 1c: chỉ Mức 1 sau khi hạ trần độ dài (90 từ)
