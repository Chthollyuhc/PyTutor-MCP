"""
MCP Server chính thức cho PyTutor (sử dụng mcp SDK 2.2.0).
Cung cấp các Tool phục vụ Hệ thống Gia sư Thông minh:
- run_test_cases: Thực thi code sinh viên trong Sandbox cô lập
- analyze_code_ast: Phân tích tĩnh cấu trúc cây cú pháp AST
- get_exercise_list: Lấy danh sách bài tập mẫu
- get_exercise_details: Lấy chi tiết đề bài và test cases
"""
import sys
import os

# Cấu hình UTF-8 bắt buộc trên Windows để tránh lỗi encoding qua stdio
if sys.platform == "win32":
    try:
        if sys.stdin:
            sys.stdin.reconfigure(encoding="utf-8")
        if sys.stdout:
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr:
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from mcp.server.mcpserver import MCPServer
from mcp_server.sandbox import run_test_cases as sandbox_run_tests
from mcp_server.ast_analyzer import analyze_code_ast as ast_analyze
from mcp_server.exercises_data import get_all_exercises_summary, get_exercise_by_id

# Khởi tạo MCP Server
mcp = MCPServer("PyTutor-Code-Engine")


@mcp.tool()
def run_test_cases(code: str, test_cases: list[dict]) -> dict:
    """
    [MCP Tool] Chạy mã nguồn Python của sinh viên với danh sách test cases.
    Thực thi trong subprocess độc lập với timeout an toàn 5.0 giây (chống lặp vô hạn).
    Trả về chi tiết số test PASS/FAIL, actual_output, exception và thời gian chạy.
    """
    return sandbox_run_tests(code, test_cases, timeout_seconds=5.0)


@mcp.tool()
def analyze_code_ast(code: str) -> dict:
    """
    [MCP Tool] Phân tích cây cú pháp tĩnh (AST) của mã nguồn Python.
    Phát hiện sự hiện diện của vòng lặp (For, While), đệ quy, biến accumulator (+=, *=, append)
    và bắt lỗi cú pháp nếu có.
    """
    return ast_analyze(code)


@mcp.tool()
def get_exercise_list() -> dict:
    """
    [MCP Tool] Lấy danh mục các bài tập lập trình Python có sẵn trong hệ thống.
    """
    items = get_all_exercises_summary()
    return {"total": len(items), "exercises": items}


@mcp.tool()
def get_exercise_details(exercise_id: str) -> dict:
    """
    [MCP Tool] Lấy toàn bộ thông tin chi tiết của một bài tập: đề bài, code mẫu khởi tạo,
    và bộ test cases chuẩn.
    """
    ex = get_exercise_by_id(exercise_id)
    if not ex:
        return {"error": f"Không tìm thấy bài tập có mã '{exercise_id}'"}
    return ex


if __name__ == "__main__":
    # Chạy MCP Server qua giao thức stdio (chuẩn JSON-RPC 2.0)
    mcp.run()
