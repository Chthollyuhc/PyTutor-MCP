# 🎨 PLAN 3.1: FRONTEND PROJECT SETUP & 3-COLUMN LAYOUT

> **Phân hệ:** `frontend/`  
> **Trạng thái:** ⏸️ CHƯA BẮT ĐẦU

---

## 🎯 1. Mục tiêu (Objective)
Khởi tạo ứng dụng Frontend hiện đại bằng React 18, Vite và Tailwind CSS bằng lệnh `npm.cmd`. Xây dựng khung giao diện 3 cột chuẩn theo wireframe của đồ án, tích hợp thanh trạng thái kết nối Backend & MCP Tools, và hoàn thiện Cột 1 (Problem Panel).

---

## 🏗️ 2. Kiến trúc Giao diện (UI Layout)

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 🎓 PyTutor - Intelligent Tutoring System      [MCP Tools: 4 Connected] │
├───────────────────┬───────────────────────────────┬────────────────────┤
│   CỘT 1 (30%)     │          CỘT 2 (45%)          │    CỘT 3 (25%)     │
│   ProblemPanel    │          EditorPanel          │     TutorPanel     │
│                   │                               │                    │
│ • Chọn bài tập    │ • Monaco Code Editor          │ • Chọn Hint Level  │
│ • Đề bài Markdown │   (Python syntax, dark theme) │ • Nhận xét AST     │
│ • Ví dụ Input/Out │ • Nút Chạy / Nộp bài          │ • Phản hồi AI      │
│ • Mục tiêu học    │ • Bảng Test Cases PASS/FAIL   │   Scaffolding      │
└───────────────────┴───────────────────────────────┴────────────────────┘
```

---

## ✅ 3. Danh sách Công việc (Checklist)

- [ ] Khởi tạo dự án Vite React tại thư mục `frontend/` bằng lệnh `npm.cmd create vite@latest frontend -- --template react`.
- [ ] Cài đặt các thư viện phụ thuộc: `tailwindcss`, `postcss`, `autoprefixer`, `@monaco-editor/react`, `lucide-react`, `axios`, `canvas-confetti`.
- [ ] Cấu hình Tailwind CSS (`tailwind.config.js` và `index.css`).
- [ ] Xây dựng `frontend/src/services/api.js`: Axios client gọi FastAPI endpoints (`/api/health`, `/api/exercises`, `/api/submit`).
- [ ] Xây dựng Header component: Hiển thị logo PyTutor, trạng thái Backend health và huy hiệu danh sách MCP Tools khám phá được.
- [ ] Xây dựng `ProblemPanel.jsx`: Dropdown chọn bài tập, hiển thị độ khó, mô tả bài tập (hỗ trợ hiển thị bảng, code blocks, công thức toán).

---

## 📁 4. Danh sách File Đầu ra (Deliverables)
- `frontend/package.json`
- `frontend/vite.config.js`
- `frontend/src/services/api.js`
- `frontend/src/components/Header.jsx`
- `frontend/src/components/ProblemPanel.jsx`
