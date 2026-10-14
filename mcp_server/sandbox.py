"""
Module Sandbox thực thi mã nguồn Python cô lập.
- Sử dụng subprocess độc lập
- Bắt buộc giới hạn thời gian (Timeout 5.0s mặc định) chống vòng lặp vô hạn
- Thu thập toàn bộ stdout, stderr, exception trace
- Hỗ trợ mã hóa UTF-8 chuẩn trên Windows
"""
import sys
import os
import time
import subprocess
import traceback


def execute_single_test(code: str, stdin_data: str, timeout_seconds: float = 5.0) -> dict:
    """
    Thực thi mã nguồn với một chuỗi dữ liệu đầu vào stdin trong subprocess cô lập.
    """
    t_start = time.time()
    
    # Chuẩn bị môi trường UTF-8 trên Windows
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    
    try:
        proc = subprocess.Popen(
            [sys.executable, "-u", "-c", code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        try:
            stdout_data, stderr_data = proc.communicate(input=stdin_data, timeout=timeout_seconds)
            elapsed_ms = (time.time() - t_start) * 1000
            
            if proc.returncode == 0:
                return {
                    "status": "SUCCESS",
                    "stdout": stdout_data,
                    "stderr": stderr_data,
                    "error_type": None,
                    "error_message": None,
                    "elapsed_ms": round(elapsed_ms, 2)
                }
            else:
                # Phân loại lỗi từ stderr
                stderr_clean = stderr_data.strip()
                error_type = "RUNTIME_ERROR"
                if "SyntaxError" in stderr_clean:
                    error_type = "SYNTAX_ERROR"
                elif "IndentationError" in stderr_clean:
                    error_type = "SYNTAX_ERROR"
                elif "ZeroDivisionError" in stderr_clean:
                    error_type = "RUNTIME_ERROR"
                elif "IndexError" in stderr_clean or "KeyError" in stderr_clean:
                    error_type = "RUNTIME_ERROR"
                elif "NameError" in stderr_clean:
                    error_type = "RUNTIME_ERROR"
                elif "ValueError" in stderr_clean:
                    error_type = "RUNTIME_ERROR"
                    
                # Trích xuất dòng thông báo lỗi chính
                lines = stderr_clean.splitlines()
                last_line = lines[-1] if lines else "Quá trình thực thi kết thúc với mã lỗi non-zero."
                
                return {
                    "status": error_type,
                    "stdout": stdout_data,
                    "stderr": stderr_clean,
                    "error_type": error_type,
                    "error_message": last_line,
                    "elapsed_ms": round(elapsed_ms, 2)
                }
                
        except subprocess.TimeoutExpired:
            # Chấm dứt tiến trình con nếu chạy quá thời gian
            proc.kill()
            try:
                proc.communicate(timeout=1.0)
            except Exception:
                pass
            elapsed_ms = (time.time() - t_start) * 1000
            return {
                "status": "TIMEOUT",
                "stdout": "",
                "stderr": f"Lỗi: Quá thời gian thực thi tối đa ({timeout_seconds} giây). Có thể chương trình chứa vòng lặp vô hạn.",
                "error_type": "TIMEOUT",
                "error_message": f"Time Limit Exceeded (>{timeout_seconds}s)",
                "elapsed_ms": round(elapsed_ms, 2)
            }
            
    except Exception as e:
        elapsed_ms = (time.time() - t_start) * 1000
        return {
            "status": "SYSTEM_ERROR",
            "stdout": "",
            "stderr": str(e),
            "error_type": "SYSTEM_ERROR",
            "error_message": f"Lỗi khởi chạy Sandbox: {e}",
            "elapsed_ms": round(elapsed_ms, 2)
        }


def run_test_cases(code: str, test_cases: list[dict], timeout_seconds: float = 5.0) -> dict:
    """
    Chạy toàn bộ test cases cho một đoạn code sinh viên.
    So sánh actual_output với expected_output.
    """
    total = len(test_cases)
    passed_count = 0
    results = []
    
    for idx, tc in enumerate(test_cases, start=1):
        stdin_input = tc.get("input", "")
        expected = str(tc.get("expected_output", "")).strip()
        desc = tc.get("description", f"Test case #{idx}")
        
        exec_res = execute_single_test(code, stdin_input, timeout_seconds=timeout_seconds)
        actual = exec_res["stdout"].strip()
        status = exec_res["status"]
        error_msg = exec_res["error_message"]
        
        test_status = "FAIL"
        if status == "SUCCESS":
            if actual == expected:
                test_status = "PASS"
                passed_count += 1
            else:
                test_status = "FAIL"
        elif status == "TIMEOUT":
            test_status = "TIMEOUT"
        elif status == "SYNTAX_ERROR":
            test_status = "SYNTAX_ERROR"
        else:
            test_status = "RUNTIME_ERROR"
            
        results.append({
            "test_idx": idx,
            "description": desc,
            "input": stdin_input.strip(),
            "expected_output": expected,
            "actual_output": actual if status == "SUCCESS" else "",
            "status": test_status,
            "error_message": error_msg,
            "stderr": exec_res["stderr"] if test_status != "PASS" else "",
            "execution_time_ms": exec_res["elapsed_ms"]
        })
        
        # Nếu gặp lỗi cú pháp hoặc timeout thì dừng các test sau để tiết kiệm thời gian
        if test_status in ("SYNTAX_ERROR", "TIMEOUT"):
            skip_reason = (
                "Bỏ qua do có lỗi cú pháp phía trước."
                if test_status == "SYNTAX_ERROR"
                else "Bỏ qua do phát hiện vòng lặp vô hạn (Timeout) ở test trước."
            )
            for rem_idx in range(idx + 1, total + 1):
                rem_tc = test_cases[rem_idx - 1]
                results.append({
                    "test_idx": rem_idx,
                    "description": rem_tc.get("description", f"Test case #{rem_idx}"),
                    "input": rem_tc.get("input", "").strip(),
                    "expected_output": str(rem_tc.get("expected_output", "")).strip(),
                    "actual_output": "",
                    "status": "SKIPPED",
                    "error_message": skip_reason,
                    "stderr": "",
                    "execution_time_ms": 0.0
                })
            break

    failed_count = total - passed_count
    all_passed = (passed_count == total and total > 0)
    
    summary = f"Đạt {passed_count}/{total} test cases."
    if all_passed:
        summary = f"Tuyệt vời! Đã vượt qua toàn bộ {total}/{total} test cases."
    elif any(r["status"] == "TIMEOUT" for r in results):
        summary = f"Cảnh báo: Phát hiện lỗi quá thời gian thực thi (Timeout). Kiểm tra vòng lặp vô hạn."
    elif any(r["status"] == "SYNTAX_ERROR" for r in results):
        summary = f"Mã nguồn có lỗi cú pháp (SyntaxError). Cần sửa lỗi cú pháp trước khi kiểm thử logic."
        
    return {
        "total_tests": total,
        "passed_tests": passed_count,
        "failed_tests": failed_count,
        "all_passed": all_passed,
        "summary": summary,
        "results": results
    }
