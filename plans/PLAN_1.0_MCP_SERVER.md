# 📦 PLAN 1.0: MCP SERVER & EXECUTION SANDBOX CORE

> **Phân hệ:** `mcp_server/`  
> **Phiên bản:** 1.1 (Bao gồm Patch tối ưu dừng sớm khi Timeout)  
> **Trạng thái:** ✅ ĐÃ HOÀN THÀNH (100% Tests Passed)

---

## 🎯 1. Mục tiêu (Objective)
Xây dựng một MCP Server độc lập tuân thủ chuẩn giao thức JSON-RPC 2.0 qua `stdio` sử dụng `mcp` SDK 2.2.0. Server cung cấp các công cụ thực thi mã nguồn Python an toàn trong Sandbox (timeout 5s), phân tích tĩnh cây cú pháp trừu tượng (AST) và cung cấp dữ liệu bài tập mẫu chuẩn hóa.

---

## 🏗️ 2. Kiến trúc & Luồng Xử lý (Architecture & Data Flow)

```text
[MCP Client (Backend)]
        │ JSON-RPC 2.0 (stdio)
        ▼
[mcp_server/server.py: MCPServer("PyTutor-Code-Engine")]
   ├── 🛠️ run_test_cases     ──► [mcp_server/sandbox.py: Subprocess + 5s Timeout + Early Break]
   ├── 🛠️ analyze_code_ast   ──► [mcp_server/ast_analyzer.py: AST Inspector]
   ├── 🛠️ get_exercise_list  ──► [mcp_server/exercises_data.py: 5 Classic Exercises]
   └── 🛠️ get_exercise_details ─► [mcp_server/exercises_data.py]
```

---

## ✅ 3. Danh sách Công việc (Checklist)

- [x] **Phase 1.0 - Khởi tạo hạ tầng & ngân hàng bài tập:**
  - [x] Tạo `mcp_server/__init__.py`.
  - [x] Tạo `mcp_server/exercises_data.py` gồm 5 bài tập kinh điển (Tổng 1..n, Số nguyên tố, Giai thừa, Đảo ngược chuỗi, Đếm nguyên âm) kèm bộ test cases đa dạng.
  - [x] Tạo `mcp_server/ast_analyzer.py` phân tích số lượng vòng lặp `for`/`while`, phát hiện đệ quy, biến accumulator (`+=`, `*=`, `.append()`), và bắt lỗi `SyntaxError` thân thiện.
  - [x] Tạo `mcp_server/sandbox.py` thực thi code cô lập qua subprocess độc lập, ép kiểu encoding UTF-8 trên Windows, bắt timeout an toàn 5 giây.
  - [x] Tạo `mcp_server/server.py` khởi tạo `MCPServer`, cấu hình `sys.stdin`/`sys.stdout` UTF-8 và đăng ký 4 tools.
  - [x] Viết `mcp_server/test_mcp_server.py` kiểm thử tự động toàn diện qua `ClientSession`.
- [x] **Phase 1.1 - Optimization Patch (Tối ưu dừng sớm khi Timeout):**
  - [x] Cập nhật `mcp_server/sandbox.py`: Bổ sung điều kiện dừng sớm khi gặp `TIMEOUT` (tương tự `SYNTAX_ERROR`) để không phải chờ $5s \times N$ test cases khi code sinh viên chứa vòng lặp vô hạn.
  - [x] Cập nhật thông báo `error_message` phù hợp cho các test bị `SKIPPED`.
  - [x] Chạy lại `test_mcp_server.py` xác nhận 100% PASS.

---

## 📁 4. Danh sách File Đầu ra (Deliverables)
- `mcp_server/__init__.py`
- `mcp_server/exercises_data.py`
- `mcp_server/ast_analyzer.py`
- `mcp_server/sandbox.py`
- `mcp_server/server.py`
- `mcp_server/test_mcp_server.py`

---

## 🧪 5. Kịch bản Kiểm thử & Lệnh chạy (Verification)
```powershell
$env:PYTHONIOENCODING="utf-8"; py -m mcp_server.test_mcp_server
```
- **Tiêu chuẩn đạt (DoD):**
  - Khám phá đủ 4 Tools qua `tools/list`.
  - Lấy danh sách 5 bài tập mẫu.
  - Phân tích AST đúng cấu trúc code và bắt lỗi `SyntaxError`.
  - Chấm code đúng (5/5 PASS), code sai logic (FAIL).
  - Bắt chặn thành công vòng lặp vô hạn `while True:` sau 5 giây với trạng thái `TIMEOUT`.
