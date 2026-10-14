"""
MCP Client Layer cho FastAPI Backend.
- TUYỆT ĐỐI KHÔNG import trực tiếp bất kỳ hàm nào từ mcp_server
- Giao tiếp 100% qua chuẩn giao thức JSON-RPC 2.0 stdio
- Thực hiện True MCP Discovery qua session.list_tools()
- Cung cấp các hàm wrapper bất đồng bộ gọi công cụ từ MCP Server
"""
import sys
import os
import json
from pathlib import Path
from typing import Any

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

# Đường dẫn thư mục gốc của dự án
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_server_params() -> StdioServerParameters:
    """Khởi tạo tham số kết nối tới MCP Server qua stdio với UTF-8 trên Windows."""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
        env=env,
        cwd=str(PROJECT_ROOT),
        encoding="utf-8"
    )


async def discover_tools() -> list[str]:
    """
    [True MCP Discovery]
    Kết nối tới MCP Server, thực hiện Handshake và hỏi danh sách công cụ thực tế qua tools/list.
    """
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_res = await session.list_tools()
            return [tool.name for tool in tools_res.tools]


async def get_exercise_list() -> list[dict]:
    """Gọi MCP Tool: get_exercise_list qua stdio."""
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            res = await session.call_tool("get_exercise_list", arguments={})
            data = json.loads(res.content[0].text)
            return data.get("exercises", [])


async def get_exercise_details(exercise_id: str) -> dict:
    """Gọi MCP Tool: get_exercise_details qua stdio."""
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            res = await session.call_tool("get_exercise_details", arguments={"exercise_id": exercise_id})
            return json.loads(res.content[0].text)


async def run_test_cases(code: str, test_cases: list[dict]) -> dict:
    """Gọi MCP Tool: run_test_cases qua stdio."""
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            res = await session.call_tool("run_test_cases", arguments={"code": code, "test_cases": test_cases})
            return json.loads(res.content[0].text)


async def analyze_code_ast(code: str) -> dict:
    """Gọi MCP Tool: analyze_code_ast qua stdio."""
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            res = await session.call_tool("analyze_code_ast", arguments={"code": code})
            return json.loads(res.content[0].text)


async def execute_submission_pipeline(exercise_id: str, code: str) -> dict:
    """
    [Tối ưu hóa Pipeline]
    Thực hiện toàn bộ chuỗi: Lấy đề bài -> Chạy Sandbox -> Phân tích AST
    trong CÙNG MỘT MCP Session để chỉ tốn 1 lần Handshake duy nhất.
    """
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_res = await session.list_tools()
            discovered = [t.name for t in tools_res.tools]

            # 1. Lấy chi tiết bài tập để có test cases
            ex_res = await session.call_tool("get_exercise_details", arguments={"exercise_id": exercise_id})
            exercise_data = json.loads(ex_res.content[0].text)
            if "error" in exercise_data:
                raise ValueError(exercise_data["error"])

            test_cases = exercise_data.get("test_cases", [])

            # 2. Gọi Tool run_test_cases
            test_res = await session.call_tool("run_test_cases", arguments={"code": code, "test_cases": test_cases})
            test_results = json.loads(test_res.content[0].text)

            # 3. Gọi Tool analyze_code_ast
            ast_res = await session.call_tool("analyze_code_ast", arguments={"code": code})
            ast_analysis = json.loads(ast_res.content[0].text)

            return {
                "exercise": exercise_data,
                "test_results": test_results,
                "ast_analysis": ast_analysis,
                "discovered_tools": discovered
            }
