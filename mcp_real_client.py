import asyncio
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from mcp.types import CallToolRequest

async def main():
    print("="*60)
    print("🎓 PYTUTOR: DEMO MCP CLIENT KẾT NỐI VỚI MCP SERVER")
    print("="*60)
    print("\n[Client] Đang khởi động MCP Server thông qua giao thức stdio...")
    
    # Cấu hình để khởi chạy MCP Server (nằm ở mcp_real_server.py)
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_real_server.py"],
        env=None
    )
    
    # Mở kết nối stdio với server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Khởi tạo kết nối (handshake)
            await session.initialize()
            print("[Client] Đã kết nối thành công với MCP Server!\n")
            
            # 1. Khám phá Tools (Discovery)
            print("="*60)
            print("1. DISCOVERY: HỎI SERVER CÓ NHỮNG TOOLS NÀO?")
            print("="*60)
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"🛠️ Tool phát hiện được: {tool.name}")
                print(f"   Mô tả: {tool.description}")
            print()
            
            # 2. Gọi Tool thực thi code (run_student_code)
            print("="*60)
            print("2. EXECUTION: CLIENT GỬI CODE SINH VIÊN ĐỂ SERVER CHẠY")
            print("="*60)
            
            # Một đoạn code đúng
            good_code = """
def tinh_tong(n):
    tong = 0
    for i in range(1, n + 1):
        tong += i
    print("Đang tính toán...")
    return tong
"""
            print(f"[Client] Đang yêu cầu Server chạy đoạn code sau với n=5:\n{good_code.strip()}\n")
            
            result1 = await session.call_tool("run_student_code", arguments={"code": good_code, "n_value": 5})
            print(f"[Server trả về]:\n{result1.content[0].text}\n")
            
            # 3. Gọi Tool phân tích cú pháp (analyze_syntax)
            print("="*60)
            print("3. ANALYSIS: CLIENT YÊU CẦU PHÂN TÍCH CÚ PHÁP (STATIC ANALYSIS)")
            print("="*60)
            
            bad_code = """
def tinh_tong(n):
    # Dùng công thức Gauss thay vì vòng lặp
    return n * (n + 1) // 2
"""
            print(f"[Client] Đang gửi đoạn code sau (không có vòng lặp):\n{bad_code.strip()}\n")
            
            result2 = await session.call_tool("analyze_syntax", arguments={"code": bad_code})
            print(f"[Server trả về]:\n{result2.content[0].text}\n")
            
    print("="*60)
    print("KẾT THÚC DEMO: Bạn vừa thấy một quá trình giao tiếp chuẩn MCP!")

if __name__ == "__main__":
    # Chạy client bất đồng bộ (async)
    asyncio.run(main())
