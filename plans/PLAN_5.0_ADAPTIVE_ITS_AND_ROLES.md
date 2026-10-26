# 📋 KẾ HOẠCH PHASE 5: HỆ THỐNG GIA SƯ THÍCH ỨNG & PHÂN QUYỀN GIẢNG VIÊN (v2.5)

> **Mã kế hoạch:** `PLAN_5.0`  
> **Trạng thái:** ✅ **ĐÃ HOÀN THÀNH 100% (14/10/2026)**  
> **Mục tiêu:** Nâng cấp hệ thống từ mô hình Stateless sang Hệ thống Gia sư Thông minh Thích ứng (Adaptive ITS) thực thụ có lưu vết học tập và phân quyền người dùng.

---

## 1. MỤC TIÊU CHI TIẾT
1. **Lưu trữ Bền vững SQLite:** Thay thế cấu hình hardcode bằng cơ sở dữ liệu `pytutor.db` quản lý 3 bảng: `exercises`, `submissions`, `users`.
2. **Hệ thống Phân quyền JWT:** Cung cấp xác thực đăng nhập bảo mật với 2 vai trò:
   - Sinh viên (`student`/`student123`): Học lập trình trên IDE 3 cột.
   - Giảng viên (`gv_tran`/`gv123`): Bảng điều khiển quản trị, CRUD bài tập và thống kê.
3. **Mở rộng MCP Server lên 7 Tools:**
   - Thêm `save_learning_event`, `get_attempt_history`, `get_student_model`.
4. **Gia sư Sư phạm Thích ứng:**
   - Tích hợp lịch sử nộp bài và mô hình năng lực người học vào Scaffolding Prompt của Gemini 3.5 Flash Lite.
5. **Tách biệt Chạy thử vs Nộp bài:**
   - Nút "▶ Chạy thử" chạy nhanh qua Sandbox & AST (< 0.8s, miễn phí quota AI).
   - Nút "🤖 Nhận gợi ý AI" thực hiện đầy đủ pipeline sư phạm 3 cấp độ.

---

## 2. KẾT QUẢ TRIỂN KHAI & CÁC FILE THỰC THI

| Hạng mục | File nguồn | Mô tả chi tiết |
|:---|:---|:---|
| **Database SQLite** | `backend/database.py` | Tạo bảng `exercises`, `submissions`, `users`; seed dữ liệu ban đầu |
| **Xác thực JWT** | `backend/auth.py` | Tạo token JWT (24h), phân quyền `require_instructor` |
| **MCP Server Tools** | `mcp_server/server.py` | Khai báo 7 MCP Tools giao tiếp stdio JSON-RPC 2.0 |
| **MCP Storage** | `mcp_server/storage.py` | Module truy xuất dữ liệu SQLite cho MCP Server |
| **Adaptive Prompt** | `backend/llm_service.py` | Nhúng `attempt_history` & `student_model` vào prompt Gemini |
| **Login Page** | `frontend/src/pages/LoginPage.jsx` | Màn hình đăng nhập kèm 2 nút 1-Click Demo |
| **Instructor Dashboard** | `frontend/src/pages/InstructorDashboard.jsx` | 4 thẻ thống kê + bảng CRUD bài tập + bảng lịch sử |
| **Exercise Form** | `frontend/src/pages/ExerciseFormPage.jsx` | Form thêm/sửa bài tập và quản lý test cases trực quan |

---

## 3. KIỂM THỬ XÁC THỰC
- `py test_phase5_backend.py`: **100% PASS** (True Discovery 7 tools, Auth, Run-test, Submit, Student Model, Instructor CRUD).
- `py -m backend.test_backend_e2e`: **6/6 tests PASS 100%**.
