# 📋 KẾ HOẠCH TRIỂN KHAI CHI TIẾT: PHASE 7.0
# TỐI ƯU TRẢI NGHIỆM SINH VIÊN, TINH GỌN HEADER & TIỆN ÍCH LẬP TRÌNH (STUDENT UX & ERGONOMICS)

> **Mã kế hoạch:** `PLAN_7.0`  
> **Trạng thái:** ✅ **100% HOÀN THÀNH & ĐÃ KIỂM THỬ ĐẠT CHUẨN (PASSED)**  
> **Áp dụng cho:** `frontend/src/components/Header.jsx`, `frontend/src/components/TutorPanel.jsx`, `frontend/src/components/EditorPanel.jsx`, `frontend/src/components/StudentProfileModal.jsx`, `frontend/src/pages/StudentIDE.jsx`  
> **Định hướng:** Xóa bỏ rào cản thuật ngữ nghiên cứu hàn lâm, tinh gọn diện tích hiển thị và bổ sung các tiện ích lập trình tối quan trọng cho sinh viên.

---

## 1. 🔍 BỐI CẢNH KỸ THUẬT & PHÂN TÍCH VẤN ĐỀ

Qua quá trình chạy thử nghiệm thực tế trên màn hình sinh viên (Phase 6), hệ thống bộc lộ 3 nhóm nhược điểm lớn về mặt Trải nghiệm Người dùng (UX):

1. **Header quá tải & Trùng lặp thông tin (Header Visual Clutter):**
   - Thanh Header hiển thị một dải badge dài liệt kê từng công cụ (`run_test_cases`, `analyze_code_ast`, `get_exercise_list`...). Điều này khiến giao diện trông giống một bảng debug kỹ thuật hơn là một môi trường học tập, gây phân tâm cho người mới học.
   - Góc phải lại có thêm một badge `MCP Online` / `MCP Offline` gây dư thừa diện tích.

2. **Rào cản Thuật ngữ Hàn lâm (Academic Jargon Barrier):**
   - Cột 3 (Trợ lý AI) chứa nhiều cụm từ chuyên ngành sư phạm lý thuyết: *"Scaffolding Pedagogy"*, *"Socratic"*, *"Diagnostic"*, *"Pseudocode"*, *"MCP AST Static Analyzer"*, *"Accumulator"*, *"Ground Truth via MCP"*.
   - Học sinh mới bắt đầu học lập trình Python không hiểu "Accumulator" là gì, cũng không quan tâm "Ground Truth" là khái niệm gì. Sinh viên chỉ cần biết: *Code của mình đúng hay sai? Sai ở đâu? Cần gợi ý như thế nào để tự sửa được?*.

3. **Thiếu Tiện ích Thao tác Cơ bản khi Code (Missing Ergonomic Features):**
   - **Mất code khi tải lại trang:** Nếu học viên lỡ tay bấm F5 hoặc chuyển qua lại giữa các bài tập, toàn bộ code đang gõ dở bị xóa sạch và reset về `starter_code`.
   - **Phải dùng chuột bấm nút:** Không có phím tắt nhanh (`Ctrl + Enter`) để chạy thử hay hỏi AI, làm đứt đoạn mạch tư duy thuật toán khi liên tục phải rời tay khỏi bàn phím để rê chuột bấm nút.

---

## 2. 🏛️ THIẾT KẾ KIẾN TRÚC & GIẢI PHÁP KỸ THUẬT

### 2.1. Cấu trúc Nút Compact MCP Pill Button trên Header
- **Vị trí:** Giữa thanh Header (`frontend/src/components/Header.jsx`).
- **Nguyên lý:** Đóng gói toàn bộ thông tin trạng thái kết nối và số lượng công cụ vào duy nhất 1 nút nhỏ (Compact Pill).
- **Trạng thái hiển thị:**
  - Online: Đèn LED chấm tròn màu xanh ngọc `#34d399` phát sáng nhấp nháy (`animate-pulse`) kèm dòng chữ `⚡ Kết nối MCP (7)`.
  - Offline: Đèn LED màu đỏ `#f43f5e` kèm `⚡ Mất kết nối MCP`.
- **Hành vi tương tác:** Chỉ khi người dùng **Click** vào nút này, hệ thống mới mở Modal **`MCPInspectorModal`** hiển thị chi tiết 7 công cụ và luồng `mcp_trace` JSON-RPC 2.0 stdio.

### 2.2. Bản đồ Chuyển đổi Ngôn ngữ Thân thiện Hóa (Localization Mapping)

| Vị trí | Thuật ngữ cũ (Hàn lâm / Kỹ thuật) | Thuật ngữ mới (Gần gũi / Sư phạm) | Ý nghĩa thực tiễn |
|:---|:---|:---|:---|
| **Header** | `MCP Tools (7): run_test_cases...` | `⚡ Kết nối MCP (7)` (Pill Button) | Tinh gọn, click mở modal |
| **Header** | `Tiến độ & Hồ sơ thích ứng` | `📒 Nhật ký học tập` | Tự nhiên, dễ hiểu |
| **Cột 3 Header** | `AI TUTOR (SCAFFOLDING PEDAGOGY)` | `🤖 Trợ lý Học tập PyTutor` | Trợ lý thân thiện |
| **Cột 3 Selector**| `CHỌN MỨC ĐỘ GỢI Ý (HINT LEVEL):` | `Bạn muốn mình gợi ý đến mức nào?` | Câu hỏi tự nhiên |
| **Mức 1** | `Level 1: Gợi Mở Socratic` | `💡 Gợi ý nhẹ` | Gợi mở hướng giải, không lộ code |
| **Mức 2** | `Level 2: Chẩn Đoán Lỗi` | `🔍 Chỉ chỗ sai` | Khoanh vùng đoạn code lỗi và giải thích |
| **Mức 3** | `Level 3: Hướng Dẫn & Mã Giả` | `🧭 Hướng dẫn từng bước` | Dàn ý thuật toán từng bước |
| **Nút Escalation**| `Chưa hiểu? Xem gợi ý rõ hơn (Level X)` | `Vẫn thấy khó? Xem gợi ý chi tiết hơn (Mức X) ▶` | Thấu cảm với học viên |
| **Thẻ AST** | `PHÂN TÍCH CÚ PHÁP TĨNH (MCP AST)` | `📋 Nhận diện nhanh code của bạn` | Thu gọn / mở rộng linh hoạt |
| **Trường AST** | `Accumulator (+=)` | `Biến cộng dồn / tích lũy` | Thuần Việt dễ hiểu |
| **Cột 2 Nút 1** | `Chạy thử` | `▶ Chạy thử code` (Ctrl+Enter) | Nút chạy kiểm thử Sandbox |
| **Cột 2 Nút 2** | `Nhận gợi ý AI` | `🤖 Hỏi Gia sư AI` (Ctrl+Shift+Enter) | Nút nộp bài và nhận hướng dẫn |
| **Cột 2 Bảng test**| `KẾT QUẢ THỰC THI (MCP SANDBOX)` | `🧪 Kết quả chạy thử bộ Test` | Rõ ràng, trực quan |
| **Modal Hồ sơ** | `Hồ sơ Năng lực ITS Student Model` | `📒 Nhật ký Học tập & Tiến độ Bản thân` | Động viên học tập |
| **Modal Hồ sơ** | `Nạp lại mã nguồn này vào Editor` | `⏪ Nạp lại code lần này` | Thao tác 1-click |

### 2.3. Cơ chế Lưu trữ Code Nháp Tự động (`localStorage` Auto-Save)
- **Key cấu trúc:** `pytutor_draft_${exercise_id}`
- **Thuật toán Lifecycle:**
  1. **Khi người dùng gõ code:** Hàm `handleCodeChange(newCode)` được gọi từ Monaco Editor -> Lưu ngay `localStorage.setItem(key, newCode)`.
  2. **Khi chuyển bài tập hoặc F5:** Hook `useEffect([selectedExerciseId])` kiểm tra:
     - Nếu `localStorage.getItem(key)` tồn tại và khác rỗng -> Nạp bản nháp này vào Editor.
     - Nếu không có bản nháp -> Nạp `exerciseDetail.starter_code`.
  3. **Khi bấm nút "Khôi phục code gốc":** Xóa bản nháp khỏi `localStorage.removeItem(key)` -> Khôi phục code ban đầu của bài tập.

### 2.4. Phím tắt Thông minh Kép (Dual Shortcut Binding)
- **Cơ chế 1 (Trong Monaco Editor):** Sử dụng `editor.addCommand()` qua sự kiện `onMount`:
  ```javascript
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => onRunTest());
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter, () => onSubmit());
  ```
- **Cơ chế 2 (Toàn cục Window):** Lắng nghe sự kiện `keydown` trên `window` để đảm bảo ngay cả khi học viên đang click chuột ở bảng đề bài hay khu vực ngoài editor thì phím tắt vẫn hoạt động mượt mà.

---

## 3. 📝 NHẬT KÝ FILE THỰC THI VÀ CHỈNH SỬA

### Task 7.1 — Cải tiến Header (`frontend/src/components/Header.jsx`)
- Loại bỏ dải `tools.slice(0, 4)` và badge `MCP Online`.
- Tạo nút `⚡ Kết nối MCP (7)` nhỏ gọn dạng Pill Button với hiệu ứng phát sáng.
- Đổi nút mở hồ sơ thành `📒 Nhật ký học tập` kèm icon `BookOpen`.
- Nâng nhãn phiên bản lên `v3.1 Pro`.

### Task 7.2 — Thân thiện hóa Trợ lý AI (`frontend/src/components/TutorPanel.jsx`)
- Tiêu đề: `🤖 Trợ lý Học tập PyTutor`.
- Chuyển đổi 3 mức gợi ý sang tiếng Việt dễ hiểu (`💡 Gợi ý nhẹ`, `🔍 Chỉ chỗ sai`, `🧭 Hướng dẫn từng bước`).
- Thẻ AST đổi tên thành `📋 Nhận diện nhanh code của bạn` kèm nút bấm `ChevronDown` / `ChevronUp` để thu gọn / mở rộng.
- Chuyển đổi các chỉ số: `Vòng lặp`, `Biến cộng dồn / tích lũy`, `Đệ quy`, `Độ dài dòng lệnh`.

### Task 7.3 — Nâng cấp Trình soạn thảo & Phím tắt (`frontend/src/components/EditorPanel.jsx`)
- Tích hợp phím tắt `Ctrl + Enter` (Chạy thử) và `Ctrl + Shift + Enter` (Hỏi Gia sư AI).
- Cập nhật nhãn nút: `▶ Chạy thử code (Ctrl+↵)` và `🤖 Hỏi Gia sư AI (Ctrl+Shift+↵)`.
- Cập nhật bảng kết quả: `🧪 Kết quả chạy thử bộ Test`, `Đầu vào (Input)`, `Kết quả mong đợi (Expected)`, `Kết quả của bạn (Actual)`.

### Task 7.4 — Nâng cấp Modal Nhật ký (`frontend/src/components/StudentProfileModal.jsx`)
- Đổi tiêu đề: `📒 Nhật ký Học tập & Tiến độ Bản thân`.
- Hiển thị 4 thẻ: Số bài đã hoàn thành, Tổng bài đã thử sức, Tổng số lần chạy & nộp, Mức độ tự lực.
- Đổi nút khôi phục code thành `⏪ Nạp lại code lần này`.

### Task 7.5 — Tích hợp Auto-Save trên Trang IDE (`frontend/src/pages/StudentIDE.jsx`)
- Bổ sung `handleCodeChange` lưu tự động vào `localStorage`.
- Bổ sung logic khôi phục nháp trong `loadExercise`.
- Reset nháp khi người dùng bấm khôi phục code mẫu.

---

## 4. 🧪 KẾT QUẢ KIỂM THỬ VÀ NGHIỆM THU

| Kịch bản kiểm thử | Hành động thực hiện | Kết quả kỳ vọng | Trạng thái |
|:---|:---|:---|:---:|
| **Header Compactness** | Mở trang chủ IDE | Header hiển thị 1 nút nhỏ `⚡ Kết nối MCP (7)`, không còn dải chữ dài | ✅ PASS |
| **MCP Inspector Modal** | Bấm vào nút `⚡ Kết nối MCP (7)` | Mở modal hiển thị 7 công cụ và log JSON-RPC `mcp_trace` | ✅ PASS |
| **Shortcut Run Test** | Bấm tổ hợp `Ctrl + Enter` trong editor | Kích hoạt ngay chức năng chạy thử test cases không gọi AI | ✅ PASS |
| **Shortcut Ask AI** | Bấm `Ctrl + Shift + Enter` trong editor | Kích hoạt nộp bài và gọi Gia sư AI Gemini | ✅ PASS |
| **Auto-save per-exercise** | Gõ `print("Hello")` ở bài 1, chuyển sang bài 2 rồi quay lại bài 1 | Đoạn mã `print("Hello")` vẫn nguyên vẹn, không bị mất | ✅ PASS |
| **F5 Refresh Persistence** | Gõ code dở, bấm F5 tải lại trang | Code nháp được khôi phục tức thì từ `localStorage` | ✅ PASS |
| **Code Reset** | Bấm nút "Khôi phục code gốc" | Bản nháp bị xóa, editor trở về code mẫu `starter_code` | ✅ PASS |
| **Frontend Production Build**| Chạy `npm.cmd run build` | Biên dịch thành công 100%, 0 errors, thời gian ~1.8s | ✅ PASS |
