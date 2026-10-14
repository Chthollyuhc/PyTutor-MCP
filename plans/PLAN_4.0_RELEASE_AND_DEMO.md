# 🚢 PLAN 4.0: SYSTEM INTEGRATION, ONE-CLICK LAUNCH & RELEASE

> **Phân hệ:** Toàn hệ thống (Root)  
> **Trạng thái:** ⏸️ CHƯA BẮT ĐẦU

---

## 🎯 1. Mục tiêu (Objective)
Tích hợp toàn bộ 3 phân hệ (`mcp_server`, `backend`, `frontend`) thành một thể thống nhất. Tạo các script khởi chạy 1-click trên Windows (`start_dev.bat` và `start_dev.ps1`) để sinh viên hoặc giảng viên có thể mở ứng dụng ngay lập tức. Hoàn thiện tài liệu `README.md` với các hướng dẫn kịch bản demo phục vụ bảo vệ đồ án.

---

## 🏗️ 2. Kiến trúc Khởi chạy (Runtime Deployment)

```text
[start_dev.bat / start_dev.ps1]
   ├──► Terminal 1: Uvicorn Backend (FastAPI trên port 8000)
   │        └── Subprocess: MCP Server (JSON-RPC 2.0 stdio)
   └──► Terminal 2: Vite Dev Server (Frontend trên port 5173)
            └── Tự động mở trình duyệt tới http://localhost:5173
```

---

## ✅ 3. Danh sách Công việc (Checklist)

- [ ] Tạo `start_dev.ps1` (PowerShell launcher với kiểm tra môi trường và chạy đồng thời).
- [ ] Tạo `start_dev.bat` (Batch script 1-click cho người dùng Windows).
- [ ] Kiểm thử kịch bản thực nghiệm trên cả 5 bài tập:
  - [ ] Code đúng 100% -> Chúc mừng + nhận xét tối ưu code.
  - [ ] Code sai logic -> Kiểm tra gợi ý Level 1, 2, 3 từ Qwen2.5-14B.
  - [ ] Code lặp vô hạn `while True:` -> Kiểm tra bắt timeout 5s mượt mà trên UI.
  - [ ] Code lỗi cú pháp -> Kiểm tra thông báo chỉ rõ dòng lỗi.
- [ ] Cập nhật `README.md` hoàn chỉnh: Giới thiệu, kiến trúc, hướng dẫn cài đặt & kịch bản demo bảo vệ đồ án.
- [ ] Cập nhật toàn bộ các file kế hoạch trong `plans/` và `PLAN.md` thành `[x] ✅ PASSED`.

---

## 📁 4. Danh sách File Đầu ra (Deliverables)
- `start_dev.ps1`
- `start_dev.bat`
- `README.md` (cập nhật)
