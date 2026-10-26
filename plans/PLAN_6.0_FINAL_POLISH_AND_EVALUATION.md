# 📋 KẾ HOẠCH PHASE 6: HOÀN THIỆN SẢN PHẨM & ĐÁNH GIÁ THỰC NGHIỆM ĐỒ ÁN (v3.0 FINAL)

> **Mã kế hoạch:** `PLAN_6.0`  
> **Trạng thái:** ✅ **ĐÃ HOÀN THÀNH 100% (14/10/2026)**  
> **Mục tiêu:** Trực quan hóa giao thức MCP (Protocol Inspector), bổ sung Hồ sơ Năng lực Thích ứng cho Sinh viên, nâng cấp công cụ Giảng viên (Chi tiết bài nộp & Xuất CSV), và xây dựng bộ kiểm thử thực nghiệm tự động cho Khóa luận tốt nghiệp.

---

## 1. MỤC TIÊU CHI TIẾT
1. **Trực quan hóa Giao thức MCP (MCP Inspector):**
   - Modal hiển thị thông số 7 MCP Tools và nhật ký thực thi `mcp_trace` (từng lệnh Handshake, tools/list, call_tool kèm thời gian ms qua JSON-RPC stdio).
2. **Hồ sơ Năng lực Thích ứng (Student Adaptive Profile):**
   - Hiển thị mô hình người học từ MCP Tool `get_student_model`, lịch sử các lần nộp của bài hiện tại kèm tính năng "Nạp lại code này vào Editor".
3. **Nâng cấp Dashboard Giảng viên:**
   - Modal xem chi tiết bài nộp của sinh viên (mã nguồn đã nộp + kết quả test + phản hồi sư phạm AI).
   - Nút xuất dữ liệu thực nghiệm ra file `.csv` có mã hóa UTF-8 BOM chuẩn cho Microsoft Excel.
4. **Bộ Đánh giá Thực nghiệm Học thuật Tự động:**
   - Script `evaluate_its_benchmark.py` đo đạc 4 trọng tâm thực nghiệm và tự động xuất file `docs/EVALUATION_REPORT.md` chuẩn khoa học cho Chương 4 Khóa luận.

---

## 2. KẾT QUẢ TRIỂN KHAI & CÁC FILE THỰC THI

| Hạng mục | File nguồn | Mô tả chi tiết |
|:---|:---|:---|
| **MCP Trace Backend** | `backend/mcp_client.py`, `backend/schemas.py` | Đo đạc và trả về `mcp_trace` qua endpoint `/api/run-test` và `/api/submit` |
| **Student Profile API** | `backend/main.py` | Endpoint `GET /api/student/profile` gọi MCP Tools qua stdio |
| **Submission Detail API** | `backend/main.py`, `backend/database.py` | Endpoint `GET /api/instructor/submissions/{id}` |
| **MCP Inspector Modal** | `frontend/src/components/MCPInspectorModal.jsx` | Giao diện trực quan hóa 7 tools và trace truyền thông MCP |
| **Student Profile Modal** | `frontend/src/components/StudentProfileModal.jsx` | Thống kê năng lực, mức gợi ý trung bình và nạp lại code cũ |
| **Submission Detail Modal**| `frontend/src/pages/InstructorDashboard.jsx` | Xem code nộp và phản hồi sư phạm của AI |
| **Export CSV (UTF-8 BOM)** | `frontend/src/pages/InstructorDashboard.jsx` | Xuất dữ liệu báo cáo dạng CSV tương thích Excel tiếng Việt |
| **Benchmark Script** | `evaluate_its_benchmark.py` | Script tự động chạy 4 bài kiểm chuẩn học thuật |
| **Academic Report** | `docs/EVALUATION_REPORT.md` | Báo cáo thực nghiệm khoa học hoàn chỉnh cho Đồ án |

---

## 3. KẾT QUẢ KIỂM THỬ XÁC THỰC
- `py evaluate_its_benchmark.py`: **4/4 Benchmark ĐẠT CHUẨN 100%**.
- `npm.cmd run build`: **0 lỗi**, hoàn tất trong 1.8s.
