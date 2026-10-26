"""
Module Tracing Thực thi Từng bước (Execution Step Visualizer Engine) cho PyTutor.
Ghi lại từng bước chuyển dòng, gọi hàm, biến thiên của biến số và dữ liệu stdout.
Bảo vệ an toàn bằng Timeout 3.0s và giới hạn max_steps để chống treo hệ thống.
"""
import sys
import io
import time
from typing import Dict, Any, List, Optional


class StepLimitExceeded(Exception):
    """Ngoại lệ khi vượt quá số bước thực thi tối đa."""
    pass


class StepTimeoutExceeded(Exception):
    """Ngoại lệ khi thời gian thực thi vượt quá giới hạn an toàn."""
    pass


def sanitize_local_vars(local_dict: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    Lọc và rút gọn các biến cục bộ để trả về JSON an toàn.
    Loại bỏ các biến nội bộ (__name__, __builtins__...) và cắt ngắn chuỗi quá dài.
    """
    sanitized = {}
    for k, v in local_dict.items():
        if k.startswith("__"):
            continue
        # Tránh các module hoặc hàm nội bộ
        type_name = type(v).__name__
        if type_name in ("module", "function", "builtin_function_or_method"):
            continue

        try:
            val_str = repr(v)
            if len(val_str) > 80:
                val_str = val_str[:77] + "..."
        except Exception:
            val_str = "<unprintable>"

        sanitized[k] = {
            "type": type_name,
            "value": val_str
        }
    return sanitized


def trace_code_execution(code: str, stdin_input: str = "", max_steps: int = 150, timeout_seconds: float = 3.0) -> dict:
    """
    Thực thi mã nguồn Python và ghi lại từng bước (Execution Steps).
    Trả về cấu trúc dữ liệu gồm code_lines, total_steps, và danh sách các steps.
    """
    code_lines = code.splitlines()
    steps: List[dict] = []
    
    # Chuẩn bị luồng giả lập I/O
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    simulated_stdin = io.StringIO(stdin_input)
    simulated_stdout = io.StringIO()
    
    start_time = time.time()
    truncated = False
    error_message: Optional[str] = None
    user_filename = "<user_code>"

    def tracer(frame, event, arg):
        nonlocal truncated, error_message
        # Chỉ theo dõi code người dùng (tránh các frame hệ thống hoặc thư viện)
        if frame.f_code.co_filename != user_filename:
            return tracer

        # Kiểm tra timeout
        if time.time() - start_time > timeout_seconds:
            truncated = True
            error_message = f"Thời gian chạy từng bước vượt quá {timeout_seconds}s (Time Limit Exceeded)."
            raise StepTimeoutExceeded(error_message)

        # Kiểm tra số bước tối đa
        if len(steps) >= max_steps:
            truncated = True
            error_message = f"Số bước thực thi đã đạt giới hạn tối đa ({max_steps} bước)."
            raise StepLimitExceeded(error_message)

        # Ghi nhận frame
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name
        current_stdout = simulated_stdout.getvalue()
        local_vars = sanitize_local_vars(frame.f_locals)

        steps.append({
            "step": len(steps) + 1,
            "line": lineno,
            "event": event,
            "func_name": "<main>" if func_name == "<module>" else func_name,
            "locals": local_vars,
            "stdout": current_stdout
        })

        return tracer

    # Biên dịch mã nguồn trước để bắt lỗi cú pháp nếu có
    try:
        compiled = compile(code, user_filename, "exec")
    except SyntaxError as se:
        return {
            "success": False,
            "total_steps": 0,
            "code_lines": code_lines,
            "steps": [],
            "truncated": False,
            "error": f"Lỗi cú pháp tại dòng {se.lineno}: {se.msg}"
        }
    except Exception as e:
        return {
            "success": False,
            "total_steps": 0,
            "code_lines": code_lines,
            "steps": [],
            "truncated": False,
            "error": str(e)
        }

    # Thực thi với sys.settrace
    sys.stdin = simulated_stdin
    sys.stdout = simulated_stdout
    user_globals = {
        "__name__": "__main__",
        "__doc__": None,
    }

    try:
        sys.settrace(tracer)
        exec(compiled, user_globals)
    except (StepLimitExceeded, StepTimeoutExceeded):
        pass  # Đã ghi nhận truncated
    except EOFError:
        error_message = "EOFError: Lệnh input() không thể đọc dữ liệu do đầu vào (stdin) đang trống. Hãy bấm 'Nhập Stdin' để cung cấp giá trị cho hàm input()."
    except Exception as e:
        error_message = f"{type(e).__name__}: {str(e)}"
    finally:
        sys.settrace(None)
        sys.stdin = old_stdin
        sys.stdout = old_stdout

    return {
        "success": True if not error_message or len(steps) > 0 else False,
        "total_steps": len(steps),
        "code_lines": code_lines,
        "steps": steps,
        "truncated": truncated,
        "error": error_message
    }
