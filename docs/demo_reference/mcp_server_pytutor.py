"""
MCP Server cho PyTutor Demo
Cung cấp tool run_code để chạy bài toán Python trong sandbox
"""
import sys
import io
import traceback
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("PyTutor-Code-Engine")

@mcp.tool()
def run_code(code: str) -> str:
    """
    Chạy code Python trong sandbox an toàn.
    Trả về stdout, kết quả, hoặc thông báo lỗi chi tiết.
    """
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        namespace = {}
        exec(compile(code, "<mcp_sandbox>", "exec"), namespace)
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        if output.strip():
            return f"OK\n{output.strip()}"
        else:
            return "OK\n(Chương trình chạy thành công, không có output)"
    except Exception as e:
        sys.stdout = old_stdout
        return f"ERROR\n{type(e).__name__}: {e}\n\nTraceback:\n{traceback.format_exc()}"

if __name__ == "__main__":
    mcp.run()
