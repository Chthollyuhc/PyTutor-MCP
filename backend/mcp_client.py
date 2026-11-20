"""
MCP Client Layer cho FastAPI Backend.
- TUYỆT ĐỐI KHÔNG import trực tiếp bất kỳ hàm nào từ mcp_server
- Giao tiếp 100% qua chuẩn giao thức JSON-RPC 2.0 stdio
- Thực hiện True MCP Discovery qua session.list_tools()
- Cung cấp các pipeline bất đồng bộ tối ưu hóa Handshake:
  1. execute_submission_pipeline (Full pipeline: Đề bài + Lịch sử + Student Model + Sandbox + AST + MCP Trace)
  2. run_test_only_pipeline (Pipeline chạy thử nhẹ: Đề bài + Sandbox + AST + MCP Trace không gọi LLM)
  3. save_learning_event_via_mcp (Lưu sự kiện học tập vào SQLite qua MCP Tool)
  4. get_student_profile_via_mcp (Truy xuất hồ sơ học sinh thích ứng qua MCP)
"""
import sys
import os
import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Any

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

logger = logging.getLogger("pytutor.mcp_client")
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


async def run_test_only_pipeline(exercise_id: str, code: str) -> dict:
    """
    [Pipeline Chạy thử nhẹ không gọi AI - Ghi nhận MCP Trace]
    1 phiên kết nối duy nhất: Lấy test cases -> Chạy Sandbox -> Phân tích AST.
    """
    mcp_trace = []
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 1. Handshake & tools/list
            t0 = time.time()
            await session.initialize()
            tools_res = await session.list_tools()
            t_ms = round((time.time() - t0) * 1000, 2)
            discovered = [t.name for t in tools_res.tools]
            mcp_trace.append({
                "step": 1,
                "tool_name": "tools/list",
                "action": "Handshake & Discovery",
                "protocol": "JSON-RPC 2.0 (stdio)",
                "duration_ms": t_ms,
                "status": "SUCCESS",
                "summary": f"Khám phá {len(discovered)} công cụ ({', '.join(discovered[:4])}...)"
            })

            # 2. Lấy chi tiết bài tập để có test cases
            t0 = time.time()
            ex_res = await session.call_tool("get_exercise_details", arguments={"exercise_id": exercise_id})
            exercise_data = json.loads(ex_res.content[0].text)
            t_ms = round((time.time() - t0) * 1000, 2)
            if "error" in exercise_data:
                raise ValueError(exercise_data["error"])

            test_cases = exercise_data.get("test_cases", [])
            mcp_trace.append({
                "step": 2,
                "tool_name": "get_exercise_details",
                "action": "Lấy đề bài & Test cases chuẩn",
                "protocol": "JSON-RPC 2.0 (stdio)",
                "duration_ms": t_ms,
                "status": "SUCCESS",
                "summary": f"Nạp {len(test_cases)} test cases từ SQLite qua MCP Server"
            })

            # 3. Chạy Sandbox
            t0 = time.time()
            test_res = await session.call_tool("run_test_cases", arguments={"code": code, "test_cases": test_cases})
            test_results = json.loads(test_res.content[0].text)
            t_ms = round((time.time() - t0) * 1000, 2)
            mcp_trace.append({
                "step": 3,
                "tool_name": "run_test_cases",
                "action": "Thực thi Sandbox cô lập (timeout 5s)",
                "protocol": "JSON-RPC 2.0 (stdio)",
                "duration_ms": t_ms,
                "status": "SUCCESS",
                "summary": f"Đạt {test_results.get('passed_tests')}/{test_results.get('total_tests')} tests (All passed: {test_results.get('all_passed')})"
            })

            # 4. Phân tích AST
            t0 = time.time()
            ast_res = await session.call_tool("analyze_code_ast", arguments={"code": code})
            ast_analysis = json.loads(ast_res.content[0].text)
            t_ms = round((time.time() - t0) * 1000, 2)
            mcp_trace.append({
                "step": 4,
                "tool_name": "analyze_code_ast",
                "action": "Phân tích cây cú pháp trừu tượng AST",
                "protocol": "JSON-RPC 2.0 (stdio)",
                "duration_ms": t_ms,
                "status": "SUCCESS",
                "summary": ast_analysis.get("structural_summary", "AST analysis complete")
            })

            return {
                "exercise": exercise_data,
                "test_results": test_results,
                "ast_analysis": ast_analysis,
                "mcp_trace": mcp_trace
            }


TRACE_TIMEOUT_S = 6.0
TRACE_MAX_STEPS = 200


async def _trace_failure(session: ClientSession, code: str, test_results: dict, ast_analysis: dict, mcp_trace: list) -> dict | None:
    """Vết chạy của CHÍNH mã người học trên đầu vào của test lỗi giàu thông tin nhất (cùng phiên MCP, không thêm handshake).

    Chỉ chạy khi mã hợp lệ cú pháp và test lỗi không phải TIMEOUT. Có timeout riêng; mọi lỗi đều chỉ ghi vào `mcp_trace`
    rồi trả None để luồng gợi ý dùng bằng chứng tĩnh. Vết cho thấy mã của người học đang làm gì, không cho thấy mã đúng.
    """
    from backend.hint_evidence import pick_failure
    step_no = len(mcp_trace) + 1
    failure = pick_failure(test_results)
    if not failure or failure.get("status") in ("TIMEOUT", "SYNTAX_ERROR") or not ast_analysis.get("valid", True):
        return None
    t0 = time.time()
    try:
        res = await asyncio.wait_for(session.call_tool("trace_code_execution", arguments={
            "code": code, "stdin_input": (failure.get("input") or "").rstrip("\n") + "\n", "max_steps": TRACE_MAX_STEPS}), timeout=TRACE_TIMEOUT_S)
        data = json.loads(res.content[0].text)
        steps = data.get("steps", [])
        counts: dict[int, int] = {}
        for st in steps:
            if st.get("event") == "line":
                counts[st["line"]] = counts.get(st["line"], 0) + 1
        main_steps = [st for st in steps if st.get("func_name") == "<main>"]
        final_locals = {k: v.get("value", "") for k, v in (main_steps[-1].get("locals", {}) if main_steps else {}).items()
                        if len(str(v.get("value", ""))) <= 40}
        ms = round((time.time() - t0) * 1000, 2)
        mcp_trace.append({"step": step_no, "tool_name": "trace_code_execution", "action": "Vết chạy trên đầu vào của test lỗi",
                          "protocol": "JSON-RPC 2.0 (stdio)", "duration_ms": ms, "status": "SUCCESS",
                          "summary": f"{data.get('total_steps', len(steps))} bước, {len(counts)} dòng được chạy" + (" (bị cắt)" if data.get("truncated") else "")})
        return {"ok": True, "input": failure.get("input", ""), "line_counts": counts, "final_locals": final_locals,
                "total_steps": data.get("total_steps", len(steps)), "truncated": bool(data.get("truncated")), "duration_ms": ms}
    except Exception as exc:  # noqa: BLE001 — vết chạy là phần phụ, không được làm hỏng luồng gợi ý
        ms = round((time.time() - t0) * 1000, 2)
        logger.warning(f"Không lấy được vết chạy: {exc}")
        mcp_trace.append({"step": step_no, "tool_name": "trace_code_execution", "action": "Vết chạy trên đầu vào của test lỗi",
                          "protocol": "JSON-RPC 2.0 (stdio)", "duration_ms": ms, "status": "SKIPPED",
                          "summary": "Không lấy được vết chạy; gợi ý dùng bằng chứng tĩnh từ kiểm thử và AST"})
        return None


async def execute_submission_pipeline(exercise_id: str, code: str, session_id: str = "default_session",
                                      class_id: str | None = None, with_trace: bool = False) -> dict:
    """
    [Pipeline Nộp bài & Thích ứng Sư phạm - Ghi nhận MCP Trace]
    1 phiên kết nối MCP duy nhất:
    1. tools/list (Handshake)
    2. get_exercise_details (Lấy đề bài & test cases)
    3. get_attempt_history (Lịch sử làm bài trước đó)
    4. get_student_model (Mô hình học sinh thích ứng)
    5. run_test_cases (Sandbox Ground Truth)
    6. analyze_code_ast (Phân tích cú pháp AST)
    7. (với_trace=True, chưa đạt) trace_code_execution trên đầu vào của test lỗi, có timeout và fallback
    """
    mcp_trace = []
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 1. Handshake & Discovery
            t0 = time.time()
            await session.initialize()
            tools_res = await session.list_tools()
            t_ms = round((time.time() - t0) * 1000, 2)
            discovered = [t.name for t in tools_res.tools]
            mcp_trace.append({
                "step": 1,
                "tool_name": "tools/list",
                "action": "Handshake & Discovery",
                "protocol": "JSON-RPC 2.0 (stdio)",
                "duration_ms": t_ms,
                "status": "SUCCESS",
                "summary": f"Khám phá {len(discovered)} MCP Tools hoạt động"
            })

            # 2. Chi tiết bài tập
            t0 = time.time()
            ex_res = await session.call_tool("get_exercise_details", arguments={"exercise_id": exercise_id})
            exercise_data = json.loads(ex_res.content[0].text)
            t_ms = round((time.time() - t0) * 1000, 2)
            if "error" in exercise_data:
                raise ValueError(exercise_data["error"])
            test_cases = exercise_data.get("test_cases", [])
            mcp_trace.append({
                "step": 2,
                "tool_name": "get_exercise_details",
                "action": "Lấy đề bài & Test cases",
                "protocol": "JSON-RPC 2.0 (stdio)",
                "duration_ms": t_ms,
                "status": "SUCCESS",
                "summary": f"Tải {len(test_cases)} test cases của '{exercise_data.get('title')}'"
            })

            # 3. Lịch sử làm bài trước đó (Attempt History)
            history_data = []
            if "get_attempt_history" in discovered:
                t0 = time.time()
                try:
                    hist_res = await session.call_tool(
                        "get_attempt_history",
                        arguments={"session_id": session_id, "exercise_id": exercise_id}
                    )
                    hist_json = json.loads(hist_res.content[0].text)
                    history_data = hist_json.get("attempts", [])
                    t_ms = round((time.time() - t0) * 1000, 2)
                    mcp_trace.append({
                        "step": 3,
                        "tool_name": "get_attempt_history",
                        "action": "Truy xuất lịch sử làm bài thích ứng",
                        "protocol": "JSON-RPC 2.0 (stdio)",
                        "duration_ms": t_ms,
                        "status": "SUCCESS",
                        "summary": f"Tìm thấy {len(history_data)} lần nộp bài trước đó trong phiên"
                    })
                except Exception as e:
                    logger.warning(f"Lỗi gọi get_attempt_history: {e}")

            # 4. Mô hình học sinh (Student Model)
            student_model = None
            if "get_student_model" in discovered:
                t0 = time.time()
                try:
                    sm_args = {"session_id": session_id}
                    if class_id:
                        sm_args["class_id"] = class_id
                    sm_res = await session.call_tool("get_student_model", arguments=sm_args)
                    student_model = json.loads(sm_res.content[0].text)
                    t_ms = round((time.time() - t0) * 1000, 2)
                    mcp_trace.append({
                        "step": 4,
                        "tool_name": "get_student_model",
                        "action": "Tính toán Mô hình Học sinh (ITS Model)",
                        "protocol": "JSON-RPC 2.0 (stdio)",
                        "duration_ms": t_ms,
                        "status": "SUCCESS",
                        "summary": student_model.get("summary", "Đã nạp hồ sơ năng lực học sinh")
                    })
                except Exception as e:
                    logger.warning(f"Lỗi gọi get_student_model: {e}")

            # 5. Chạy Sandbox
            t0 = time.time()
            test_res = await session.call_tool("run_test_cases", arguments={"code": code, "test_cases": test_cases})
            test_results = json.loads(test_res.content[0].text)
            t_ms = round((time.time() - t0) * 1000, 2)
            mcp_trace.append({
                "step": 5,
                "tool_name": "run_test_cases",
                "action": "Thực thi Sandbox độc lập (Ground Truth)",
                "protocol": "JSON-RPC 2.0 (stdio)",
                "duration_ms": t_ms,
                "status": "SUCCESS",
                "summary": f"Đạt {test_results.get('passed_tests')}/{test_results.get('total_tests')} tests (All passed: {test_results.get('all_passed')})"
            })

            # 6. Phân tích AST
            t0 = time.time()
            ast_res = await session.call_tool("analyze_code_ast", arguments={"code": code})
            ast_analysis = json.loads(ast_res.content[0].text)
            t_ms = round((time.time() - t0) * 1000, 2)
            mcp_trace.append({
                "step": 6,
                "tool_name": "analyze_code_ast",
                "action": "Phân tích cấu trúc ngữ nghĩa AST",
                "protocol": "JSON-RPC 2.0 (stdio)",
                "duration_ms": t_ms,
                "status": "SUCCESS",
                "summary": ast_analysis.get("structural_summary", "AST analysis complete")
            })

            # 7. Vết chạy (chỉ khi xin gợi ý và bài chưa đạt hết)
            failure_trace = None
            if with_trace and "trace_code_execution" in discovered and not test_results.get("all_passed") and (code or "").strip():
                failure_trace = await _trace_failure(session, code, test_results, ast_analysis, mcp_trace)

            return {
                "exercise": exercise_data,
                "test_results": test_results,
                "ast_analysis": ast_analysis,
                "attempt_history": history_data,
                "student_model": student_model,
                "discovered_tools": discovered,
                "mcp_trace": mcp_trace,
                "failure_trace": failure_trace,
            }


async def save_learning_event_via_mcp(
    session_id: str,
    exercise_id: str,
    code: str,
    hint_level: int,
    passed_tests: int,
    total_tests: int,
    all_passed: bool,
    llm_source: str,
    tutor_hint: str,
    action_type: str = "submit",
    attempt_features: dict | None = None
) -> dict:
    """Lưu sự kiện học tập thông qua MCP Tool save_learning_event (kèm đặc trưng lượt nếu có)."""
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            res = await session.call_tool(
                "save_learning_event",
                arguments={
                    "session_id": session_id,
                    "exercise_id": exercise_id,
                    "code": code,
                    "hint_level": hint_level,
                    "passed_tests": passed_tests,
                    "total_tests": total_tests,
                    "all_passed": all_passed,
                    "llm_source": llm_source,
                    "tutor_hint": tutor_hint,
                    "action_type": action_type,
                    **({"attempt_features": attempt_features} if attempt_features else {})
                }
            )
            return json.loads(res.content[0].text)


async def get_student_profile_via_mcp(session_id: str, exercise_id: str = "", class_id: str = "") -> dict:
    """Truy xuất toàn bộ hồ sơ năng lực và các lần nộp gần nhất qua MCP."""
    params = get_server_params()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # 1. Gọi get_student_model kèm class_id nếu có
            sm_args = {"session_id": session_id}
            if class_id:
                sm_args["class_id"] = class_id
            sm_res = await session.call_tool("get_student_model", arguments=sm_args)
            student_model = json.loads(sm_res.content[0].text)

            # 2. Gọi get_attempt_history nếu có exercise_id
            attempts = []
            if exercise_id:
                hist_res = await session.call_tool(
                    "get_attempt_history",
                    arguments={"session_id": session_id, "exercise_id": exercise_id}
                )
                hist_json = json.loads(hist_res.content[0].text)
                attempts = hist_json.get("attempts", [])

            return {
                "student_model": student_model,
                "recent_attempts": attempts
            }


async def run_custom_test_pipeline(code: str, custom_input: str) -> dict:
    """
    Thực thi mã nguồn với dữ liệu đầu vào tùy ý (Custom Input) qua MCP tool run_test_cases.
    """
    try:
        params = get_server_params()
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                custom_cases = [{"input": custom_input, "expected_output": "", "description": "Custom Stdin"}]
                t0 = time.time()
                res = await session.call_tool("run_test_cases", arguments={"code": code, "test_cases": custom_cases})
                t_ms = round((time.time() - t0) * 1000, 2)
                data = json.loads(res.content[0].text)
                r = data.get("results", [{}])[0]
                status_raw = r.get("status", "SUCCESS")
                # Nếu status là FAIL chỉ vì expected_output rỗng nhưng không có lỗi runtime/syntax -> SUCCESS
                status = "SUCCESS" if (status_raw == "FAIL" and not r.get("error_message")) else status_raw
                return {
                    "stdout": r.get("actual_output", ""),
                    "stderr": r.get("stderr", ""),
                    "execution_time_ms": r.get("execution_time_ms", t_ms),
                    "status": status,
                    "error_message": r.get("error_message", None)
                }
    except Exception as e:
        # Backend không import mcp_server (luật kiến trúc): lỗi MCP được báo lên endpoint (HTTP 500).
        logger.error(f"Lỗi khi gọi custom test qua MCP: {e}")
        raise


async def get_code_structure_summary(code: str) -> str:
    """Tóm tắt cấu trúc (AST) của một đoạn code qua MCP tool analyze_code_ast; trả "" nếu MCP lỗi.

    Dùng cho chat `code_review` (S8a): chỉ lấy `structural_summary` (số vòng lặp, biến tích lũy, đệ quy, số dòng),
    không chứa mã nguồn.
    """
    if not (code or "").strip():
        return ""
    try:
        async with stdio_client(get_server_params()) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                res = await session.call_tool("analyze_code_ast", arguments={"code": code})
                data = json.loads(res.content[0].text)
                return str(data.get("structural_summary") or "") if data.get("valid", True) else ""
    except Exception as e:
        logger.warning(f"Không lấy được tóm tắt AST qua MCP cho chat code_review: {e}")
        return ""


async def execute_trace_pipeline(code: str, stdin_input: str = "", max_steps: int = 150) -> dict:
    """
    Thực thi pipeline tracing từng bước thông qua MCP Tool trace_code_execution.
    Giao tiếp 100% qua chuẩn JSON-RPC 2.0 stdio với MCP Server.
    """
    try:
        params = get_server_params()
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                res = await session.call_tool(
                    "trace_code_execution",
                    arguments={"code": code, "stdin_input": stdin_input, "max_steps": max_steps}
                )
                return json.loads(res.content[0].text)
    except Exception as e:
        # Backend không import mcp_server (luật kiến trúc): lỗi MCP được báo lên endpoint (HTTP 500).
        logger.error(f"Lỗi khi gọi trace_code_execution qua MCP: {e}")
        raise


