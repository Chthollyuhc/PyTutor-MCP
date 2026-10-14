"""
Kịch bản kiểm thử tự động toàn diện cho MCP Server (Phase 1 Verification).
- Khởi chạy MCP Server qua tiến trình con stdio
- Kết nối bằng MCP Client chuẩn (ClientSession)
- Kiểm tra 4 công đoạn cốt lõi:
  1. Discovery: Tự động khám phá danh sách Tools qua giao thức MCP
  2. AST Analyzer: Phân tích cú pháp tĩnh cho cả code đúng và code lỗi cú pháp
  3. Sandbox Execution: Chấm điểm code đúng (PASS) và code sai logic (FAIL)
  4. Safety Sandbox Timeout: Thử nghiệm code lặp vô hạn (while True) -> Chứng minh chặn đứng sau 5s
"""
import sys
import os
import json
import asyncio
from pathlib import Path

# Cấu hình UTF-8 trên Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession


async def run_mcp_server_tests():
    print("=" * 70)
    print("🧪 [PHASE 1] BẮT ĐẦU KIỂM THỬ TOÀN DIỆN MCP SERVER")
    print("=" * 70)

    project_root = Path(__file__).resolve().parent.parent
    server_module = "mcp_server.server"

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", server_module],
        env=env,
        cwd=str(project_root),
        encoding="utf-8"
    )

    print(f"\n[1] Đang khởi động MCP Server qua stdio...")
    print(f"    Lệnh: {sys.executable} -m {server_module}")
    print(f"    Thư mục làm việc: {project_root}")

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 1. Handshake
            print("\n[2] Thực hiện Handshake (initialize)...")
            init_res = await session.initialize()
            print(f"    ✅ Handshake thành công!")
            print(f"    Server Info: {getattr(init_res, 'serverInfo', 'PyTutor-Code-Engine')}")

            # 2. Tool Discovery
            print("\n[3] Kiểm tra True MCP Discovery (tools/list)...")
            tools_res = await session.list_tools()
            tool_names = [t.name for t in tools_res.tools]
            print(f"    ✅ Đã phát hiện {len(tool_names)} Tools từ MCP Server:")
            for t in tools_res.tools:
                print(f"       - 🛠️ {t.name}: {t.description.splitlines()[0] if t.description else ''}")

            required_tools = ["run_test_cases", "analyze_code_ast", "get_exercise_list", "get_exercise_details"]
            for req in required_tools:
                assert req in tool_names, f"Thiếu tool bắt buộc: {req}"
            print("    ✅ Tất cả 4 Tools bắt buộc đều có mặt.")

            # 3. Test get_exercise_list
            print("\n[4] Kiểm tra Tool: get_exercise_list...")
            ex_list_res = await session.call_tool("get_exercise_list", arguments={})
            ex_list_data = json.loads(ex_list_res.content[0].text)
            exercises = ex_list_data.get("exercises", [])
            print(f"    ✅ Lấy được {len(exercises)} bài tập:")
            for ex in exercises:
                print(f"       • {ex['id']} - {ex['title']} ({ex['difficulty']} | {ex['test_cases_count']} tests)")
            assert len(exercises) >= 5, "Ngân hàng bài tập cần có ít nhất 5 bài."

            # 4. Test analyze_code_ast (Code đúng và Code lỗi)
            print("\n[5] Kiểm tra Tool: analyze_code_ast...")
            good_code = """
n = int(input())
tong = 0
for i in range(1, n + 1):
    tong += i
print(tong)
"""
            ast_good_res = await session.call_tool("analyze_code_ast", arguments={"code": good_code})
            ast_good_data = json.loads(ast_good_res.content[0].text)
            print("    • Phân tích Code hợp lệ:")
            print(f"      Valid: {ast_good_data['valid']}")
            print(f"      Has loops: {ast_good_data['has_loops']} (for: {ast_good_data['loop_details']['for_count']})")
            print(f"      Has accumulator: {ast_good_data['has_accumulator']}")
            print(f"      Tóm tắt: {ast_good_data['structural_summary']}")
            assert ast_good_data["valid"] is True
            assert ast_good_data["has_loops"] is True
            assert ast_good_data["has_accumulator"] is True

            syntax_err_code = """
n = int(input())
for i in range(1, n + 1)
    print(i)
"""
            ast_err_res = await session.call_tool("analyze_code_ast", arguments={"code": syntax_err_code})
            ast_err_data = json.loads(ast_err_res.content[0].text)
            print("    • Phân tích Code lỗi cú pháp (thiếu dấu hai chấm):")
            print(f"      Valid: {ast_err_data['valid']}")
            print(f"      Lỗi: {ast_err_data['structural_summary']}")
            assert ast_err_data["valid"] is False
            print("    ✅ AST Analyzer bắt lỗi cú pháp và trích xuất cấu trúc chuẩn xác!")

            # 5. Test run_test_cases với Code ĐÚNG
            print("\n[6] Kiểm tra Tool: run_test_cases (Kịch bản: Code đúng 100%)...")
            ex_details_res = await session.call_tool("get_exercise_details", arguments={"exercise_id": "ex_01_sum_1_to_n"})
            ex1 = json.loads(ex_details_res.content[0].text)
            test_cases = ex1["test_cases"]

            run_good_res = await session.call_tool("run_test_cases", arguments={
                "code": good_code,
                "test_cases": test_cases
            })
            run_good_data = json.loads(run_good_res.content[0].text)
            print(f"    Kết quả: {run_good_data['summary']}")
            print(f"    Đạt: {run_good_data['passed_tests']}/{run_good_data['total_tests']} tests (All Passed: {run_good_data['all_passed']})")
            assert run_good_data["all_passed"] is True, "Code đúng phải PASS 100% test cases."
            print("    ✅ Kịch bản Code đúng: PASS 100%!")

            # 6. Test run_test_cases với Code SAI LOGIC
            print("\n[7] Kiểm tra Tool: run_test_cases (Kịch bản: Code sai logic)...")
            wrong_logic_code = """
n = int(input())
# Tính sai công thức nhân thay vì cộng
print(n * 2)
"""
            run_wrong_res = await session.call_tool("run_test_cases", arguments={
                "code": wrong_logic_code,
                "test_cases": test_cases
            })
            run_wrong_data = json.loads(run_wrong_res.content[0].text)
            print(f"    Kết quả: {run_wrong_data['summary']}")
            print(f"    Đạt: {run_wrong_data['passed_tests']}/{run_wrong_data['total_tests']} tests")
            assert run_wrong_data["all_passed"] is False
            assert run_wrong_data["failed_tests"] > 0
            print("    ✅ Kịch bản Code sai logic: Bắt đúng các test case FAIL!")

            # 7. Test run_test_cases với TIMEOUT (VÒNG LẶP VÔ HẠN)
            print("\n[8] Kiểm tra Tool: run_test_cases (Kịch bản: Vòng lặp vô hạn while True - Chờ timeout 5s)...")
            infinite_loop_code = """
n = int(input())
while True:
    pass
"""
            # Chỉ test với 1 test case để xác minh timeout
            run_timeout_res = await session.call_tool("run_test_cases", arguments={
                "code": infinite_loop_code,
                "test_cases": [test_cases[0]]
            })
            run_timeout_data = json.loads(run_timeout_res.content[0].text)
            t_res = run_timeout_data["results"][0]
            print(f"    Trạng thái: {t_res['status']}")
            print(f"    Thông báo: {t_res['error_message']}")
            print(f"    Thời gian chạy: {t_res['execution_time_ms']} ms")
            assert t_res["status"] == "TIMEOUT", f"Kỳ vọng TIMEOUT nhưng nhận: {t_res['status']}"
            assert t_res["execution_time_ms"] >= 4500, "Thời gian thực thi phải xấp xỉ 5000ms"
            print("    ✅ Sandbox cô lập bắt chặn thành công vòng lặp vô hạn sau 5 giây mà không làm crash Server!")

    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ 8 BƯỚC KIỂM THỬ CỦA PHASE 1 ĐỀU ĐẠT CHUẨN 100%!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_mcp_server_tests())
