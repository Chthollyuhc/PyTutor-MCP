"""
MCP Server chính thức cho PyTutor (sử dụng mcp SDK 2.2.0).
Cung cấp 8 Tool phục vụ Hệ thống Gia sư Thông minh theo chuẩn Model Context Protocol:
- run_test_cases: Thực thi code sinh viên trong Sandbox cô lập (timeout 5s)
- analyze_code_ast: Phân tích tĩnh cấu trúc cây cú pháp AST
- get_exercise_list: Lấy danh sách bài tập từ SQLite (hoặc fallback)
- get_exercise_details: Lấy chi tiết đề bài và test cases
- save_learning_event: Lưu lịch sử nộp bài và sự kiện học tập
- get_attempt_history: Lấy lịch sử làm bài trước đó của sinh viên
- get_student_model: Tính toán mô hình học sinh thích ứng (Student Model)
- trace_code_execution: Tracing từng bước thực thi (dòng lệnh, hàm, biến số, stdout)
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
from mcp_server.tracer import trace_code_execution as tracer_trace_code
from mcp_server import storage
from mcp_server import exercises_data

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
    [MCP Tool] Lấy danh mục các bài tập lập trình Python có sẵn trong hệ thống (từ SQLite).
    """
    try:
        items = storage.get_all_exercises_summary()
        if not items:
            items = exercises_data.get_all_exercises_summary()
    except Exception:
        items = exercises_data.get_all_exercises_summary()
    return {"total": len(items), "exercises": items}


@mcp.tool()
def get_exercise_details(exercise_id: str) -> dict:
    """
    [MCP Tool] Lấy toàn bộ thông tin chi tiết của một bài tập: đề bài, code mẫu khởi tạo,
    và bộ test cases chuẩn.
    """
    try:
        ex = storage.get_exercise_by_id(exercise_id)
        if not ex:
            ex = exercises_data.get_exercise_by_id(exercise_id)
    except Exception:
        ex = exercises_data.get_exercise_by_id(exercise_id)

    if not ex:
        return {"error": f"Không tìm thấy bài tập có mã '{exercise_id}'"}
    return ex


@mcp.tool()
def save_learning_event(
    session_id: str,
    exercise_id: str,
    code: str,
    hint_level: int,
    passed_tests: int,
    total_tests: int,
    all_passed: bool,
    llm_source: str,
    tutor_hint: str
) -> dict:
    """
    [MCP Tool] Lưu sự kiện học tập và kết quả nộp bài vào cơ sở dữ liệu SQLite.
    """
    try:
        submission_id = storage.save_submission(
            session_id=session_id,
            exercise_id=exercise_id,
            code=code,
            hint_level=hint_level,
            passed_tests=passed_tests,
            total_tests=total_tests,
            all_passed=all_passed,
            llm_source=llm_source,
            tutor_hint=tutor_hint
        )
        return {"status": "saved", "submission_id": submission_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def get_attempt_history(session_id: str, exercise_id: str) -> dict:
    """
    [MCP Tool] Lấy lịch sử các lần nộp bài gần nhất của học viên để cung cấp ngữ cảnh thích ứng cho AI Tutor.
    """
    try:
        attempts = storage.get_attempts(session_id=session_id, exercise_id=exercise_id, limit=5)
        return {"session_id": session_id, "exercise_id": exercise_id, "attempts": attempts}
    except Exception as e:
        return {"session_id": session_id, "exercise_id": exercise_id, "attempts": [], "error": str(e)}


@mcp.tool()
def get_student_model(session_id: str, class_id: str = "") -> dict:
    """
    [MCP Tool] Truy xuất Mô hình Học sinh (Student Model) & Đánh giá Tự động Định lượng 4 Chiều từ SQLite.
    Hỗ trợ lọc theo Lớp học phần class_id nếu được chỉ định.
    """
    try:
        model = storage.compute_student_model(session_id=session_id, class_id=class_id if class_id else None)
        return model
    except Exception as e:
        return {
            "session_id": session_id,
            "class_id": class_id,
            "total_exercises_attempted": 0,
            "total_submissions": 0,
            "mastered_exercises": [],
            "struggling_exercises": [],
            "average_hint_level": 1.0,
            "summary": "Chưa có dữ liệu học tập.",
            "error": str(e)
        }


@mcp.tool()
def trace_code_execution(code: str, stdin_input: str = "", max_steps: int = 150) -> dict:
    """
    [MCP Tool] Tracing từng bước thực thi (dòng lệnh, hàm, biến số, stdout) của mã Python.
    Hỗ trợ sinh viên trực quan hóa luồng dữ liệu (Visualizer), an toàn với giới hạn max_steps và timeout 3s.
    """
    return tracer_trace_code(code=code, stdin_input=stdin_input, max_steps=max_steps, timeout_seconds=3.0)


if __name__ == "__main__":
    # Chạy MCP Server qua giao thức stdio (chuẩn JSON-RPC 2.0)
    mcp.run()
