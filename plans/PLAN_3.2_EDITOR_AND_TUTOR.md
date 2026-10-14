# 💻 PLAN 3.2: MONACO CODE EDITOR & AI TUTOR INTERACTIVE PANELS

> **Phân hệ:** `frontend/`  
> **Trạng thái:** ⏸️ CHƯA BẮT ĐẦU

---

## 🎯 1. Mục tiêu (Objective)
Xây dựng Cột 2 (`EditorPanel.jsx`) với Monaco Editor chuyên nghiệp hỗ trợ viết code Python, đổi theme Dark/Light, thanh nút bấm thực thi và bảng hiển thị kết quả Test Cases trực quan. Xây dựng Cột 3 (`TutorPanel.jsx`) hiển thị bộ chọn mức độ gợi ý sư phạm (Level 1, 2, 3), thẻ phân tích tĩnh AST và khung phản hồi sư phạm giàn giáo từ AI Tutor.

---

## 🏗️ 2. Chi tiết 2 Cột Chức năng

### Cột 2: `EditorPanel.jsx`
- **Monaco Code Editor:**
  - Ngôn ngữ: `python`
  - Theme: `vs-dark` hoặc `light` (hỗ trợ chuyển đổi nhanh)
  - Cấu hình: `minimap: { enabled: false }`, `fontSize: 14`, `lineNumbers: "on"`, `automaticLayout: true`, `tabSize: 4`.
- **Thanh công cụ (Toolbar):** Nút Reset code mẫu, Nút Đổi Theme, Nút Chạy & Nộp bài (kèm animation spinner khi đang chạy).
- **Bảng Test Results (nửa dưới):**
  - Tóm tắt tỷ lệ PASS (ví dụ: `4/5 Test Cases Đạt`).
  - Danh sách từng test case với badge trạng thái: `PASS` (xanh lá), `FAIL` (đỏ), `TIMEOUT` (vàng/cam), `SYNTAX_ERROR` (đỏ tím).
  - Chi tiết Input, Expected Output, Actual Output và thời gian thực thi (ms).

### Cột 3: `TutorPanel.jsx`
- **Bộ chọn Hint Level:**
  - *Level 1 - Gợi mở Socratic:* Nút chọn kèm mô tả ngắn gọn.
  - *Level 2 - Chẩn đoán vùng lỗi:* Khoanh vùng dòng lỗi và nguyên nhân lệch kết quả.
  - *Level 3 - Hướng dẫn từng bước & Pseudocode:* Thuật toán chia nhỏ.
- **Thẻ AST Analysis:** Hiển thị số lượng vòng lặp, đệ quy, biến accumulator được phát hiện từ code sinh viên.
- **Khung Chat AI Tutor:**
  - Hiển thị phản hồi sư phạm của AI bằng tiếng Việt, định dạng đẹp mắt với Markdown.
  - Badge nguồn gốc: `Qwen2.5-14B (Ground Truth via MCP)` hoặc `Pedagogical Fallback`.

---

## ✅ 3. Danh sách Công việc (Checklist)

- [ ] Xây dựng `frontend/src/components/EditorPanel.jsx`.
- [ ] Xây dựng `frontend/src/components/TutorPanel.jsx`.
- [ ] Tích hợp toàn diện vào `frontend/src/App.jsx`.
- [ ] Chạy lệnh `npm.cmd run build` kiểm tra đóng gói thành công không có lỗi cú pháp.

---

## 📁 4. Danh sách File Đầu ra (Deliverables)
- `frontend/src/components/EditorPanel.jsx`
- `frontend/src/components/TutorPanel.jsx`
- `frontend/src/App.jsx`
