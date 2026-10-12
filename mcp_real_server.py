import sys
import io
import ast
from mcp.server.mcpserver import MCPServer

# Khởi tạo MCP Server với tên "PyTutor-Execution-Engine"
mcp = MCPServer("PyTutor-Execution-Engine")

@mcp.tool()
def run_student_code(code: str, n_value: int) -> str:
    """
    [MCP Tool] Chạy code Python của sinh viên trong Sandbox.
    Yêu cầu sinh viên viết hàm tinh_tong(n). Tool sẽ tự động test với n_value.
    Trả về stdout, kết quả hoặc thông báo lỗi thực thi.
    """
    # 1. Capture stdout
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    local_scope = {}
    
    try:
        # Chạy code của sinh viên để định nghĩa hàm
        exec(compile(code, "<student_code>", "exec"), {}, local_scope)
        
        # Lấy hàm tinh_tong
        func = local_scope.get("tinh_tong")
        if not func:
            sys.stdout = old_stdout
            return "LỖI: Không tìm thấy hàm 'tinh_tong(n)'. Sinh viên chưa định nghĩa đúng tên hàm."
        
        # Gọi hàm với input n_value
        result = func(n_value)
        stdout_output = sys.stdout.getvalue()
        
        sys.stdout = old_stdout
        return f"CHẠY THÀNH CÔNG!\n- Kết quả trả về của hàm: {result}\n- Những gì in ra màn hình (stdout): {stdout_output.strip()}"
        
    except SyntaxError as e:
        sys.stdout = old_stdout
        return f"LỖI CÚ PHÁP (SyntaxError) tại dòng {e.lineno}: {e.msg}"
    except Exception as e:
        sys.stdout = old_stdout
        return f"LỖI THỰC THI (RuntimeError): {type(e).__name__} - {str(e)}"

@mcp.tool()
def analyze_syntax(code: str) -> str:
    """
    [MCP Tool] Phân tích cây cú pháp (AST) xem mã có dùng vòng lặp for không.
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For) or isinstance(node, ast.While):
                return "Phân tích tĩnh: TỐT - Tìm thấy vòng lặp (For/While) trong code."
        return "Phân tích tĩnh: CẢNH BÁO - Không tìm thấy vòng lặp nào trong code."
    except Exception as e:
        return f"Phân tích tĩnh thất bại: {e}"

if __name__ == "__main__":
    # Khởi chạy server qua giao thức stdio (chuẩn MCP để các Agent kết nối)
    mcp.run()
