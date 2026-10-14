"""
Module Tích hợp Mô hình Ngôn ngữ Lớn (LLM) Qwen2.5-14B và Chiến lược Sư phạm Giàn giáo (Scaffolding Pedagogy).
- Kết nối tới Ollama API: http://101.96.66.232:8037/ollama/api/generate
- Đóng gói Context Bundle Ground Truth (Đề bài + Code + Sandbox + AST)
- Triển khai 3 Cấp độ Gợi ý Thích ứng (Level 1: Gợi mở, Level 2: Chẩn đoán, Level 3: Mã giả)
- Bộ lọc cấm giải hộ (Anti-Spoil Guard)
- Bộ tạo phản hồi sư phạm dự phòng (Rule-based Pedagogical Fallback)
"""
import json
import logging
import os
import re
import asyncio
from typing import Optional
from pathlib import Path
import httpx

logger = logging.getLogger("pytutor.llm")

# Tự động nạp biến môi trường từ file .env ở thư mục gốc
PROJECT_ROOT = Path(__file__).resolve().parent.parent
env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception as e:
        logger.warning(f"Không thể đọc file .env: {e}")

# Cấu hình Gemini AI (Mô hình chính chất lượng cao & hạn mức RPD dồi dào)
PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODELS = [PRIMARY_MODEL, "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]

# Cấu hình Qwen (Dự phòng theo đề tài nếu server trường online)
QWEN_API_URL = os.getenv("QWEN_API_URL", "http://101.96.66.232:8037/ollama/api/generate")
QWEN_SECKEY = os.getenv("QWEN_SECKEY", "neutv")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen2.5:14b-instruct-ctx16k")


def build_scaffolding_prompt(
    exercise: dict,
    code: str,
    test_results: dict,
    ast_analysis: dict,
    hint_level: int
) -> str:
    """
    Đóng gói Context Bundle và thiết lập System Prompt sư phạm theo cấp độ.
    """
    title = exercise.get("title", "Bài tập lập trình Python")
    desc = exercise.get("description", "")
    all_passed = test_results.get("all_passed", False)
    passed_count = test_results.get("passed_tests", 0)
    total_count = test_results.get("total_tests", 0)
    
    # Trích xuất lỗi hoặc test cases thất bại
    failed_details = []
    for r in test_results.get("results", []):
        if r.get("status") != "PASS":
            status = r.get("status")
            inp = r.get("input", "")
            exp = r.get("expected_output", "")
            act = r.get("actual_output", "")
            err = r.get("error_message", "")
            failed_details.append(
                f"- Test #{r.get('test_idx')} ({status}): Input='{inp}' | Kỳ vọng='{exp}' | Nhận được='{act}' | Lỗi='{err}'"
            )
            if len(failed_details) >= 3:
                break
                
    failed_text = "\n".join(failed_details) if failed_details else "(Không có test case nào bị lỗi)"
    ast_summary = ast_analysis.get("structural_summary", "Không có thông tin AST")

    # Chỉ dẫn sư phạm theo Level
    if all_passed:
        level_instruction = """
[TÌNH HUỐNG: SINH VIÊN ĐÃ ĐẠT 100% TEST CASES]
- Hãy nhiệt liệt chúc mừng thành tích của sinh viên!
- Dựa trên kết quả phân tích AST, hãy nhận xét về phong cách lập trình (code style) và độ tối ưu.
- Gợi ý 1 mẹo nhỏ để viết code Pythonic hơn hoặc tối ưu hơn (ví dụ: dùng hàm có sẵn, list comprehension, tối ưu vòng lặp).
"""
    elif hint_level == 1:
        level_instruction = """
[CẤP ĐỘ GỢI Ý 1: GỢI MỞ SOCRATIC - CONCEPTUAL HINT]
- Mục tiêu: Định hướng tư duy bằng câu hỏi gợi mở, giúp sinh viên tự nhận ra vấn đề.
- RÀNG BUỘC TUYỆT ĐỐI:
  + KHÔNG chỉ ra vị trí dòng lỗi cụ thể.
  + KHÔNG nói đáp án hay cách sửa.
  + KHÔNG viết bất kỳ đoạn code Python nào.
- Hãy đặt 1-2 câu hỏi gợi mở nhắc sinh viên xem lại điều kiện khởi tạo, giới hạn vòng lặp hoặc kiểu dữ liệu đầu ra.
"""
    elif hint_level == 2:
        level_instruction = """
[CẤP ĐỘ GỢI Ý 2: CHẨN ĐOÁN & KHOANH VÙNG LỖI - DIAGNOSTIC HINT]
- Mục tiêu: Chỉ ra nguyên nhân gốc rễ dẫn đến việc đầu ra thực tế lệch so với kỳ vọng.
- RÀNG BUỘC:
  + Dựa vào Test Case bị FAIL và phân tích AST, chỉ rõ khối lệnh hoặc điều kiện đang bị lỗi logic.
  + Giải thích vì sao với Input đó thì chương trình lại in ra Actual Output thay vì Expected Output.
  + KHÔNG viết code sửa hoàn chỉnh, để sinh viên tự sửa lỗi.
"""
    else:  # Level 3
        level_instruction = """
[CẤP ĐỘ GỢI Ý 3: HƯỚNG DẪN TỪNG BƯỚC & MÃ GIẢ - STEP-BY-STEP & PSEUDOCODE]
- Mục tiêu: Hướng dẫn chi tiết từng bước thuật toán để sinh viên giải quyết được bài toán.
- NỘI DUNG:
  + Liệt kê thuật toán theo từng bước (Bước 1, Bước 2, Bước 3...).
  + Có thể cung cấp mã giả (Pseudocode) hoặc dàn ý logic.
  + RÀNG BUỘC CỨNG: TUYỆT ĐỐI KHÔNG cung cấp code Python hoàn chỉnh để copy-paste.
"""

    prompt = f"""Bạn là PyTutor - một Gia sư Trí tuệ Nhân tạo dạy lập trình Python thân thiện, thấu cảm và tuân thủ phương pháp sư phạm giàn giáo (Scaffolding Pedagogy).

[BỐI CẢNH BÀI TẬP]:
Tên bài: {title}
{desc}

[MÃ NGUỒN CỦA SINH VIÊN]:
```python
{code}
```

[KẾT QUẢ THỰC THI THỰC TẾ TỪ MCP SANDBOX (GROUND TRUTH)]:
- Trạng thái kiểm thử: Đạt {passed_count}/{total_count} test cases
- Tóm tắt: {test_results.get('summary', '')}
- Các test case lỗi mẫu:
{failed_text}

[KẾT QUẢ PHÂN TÍCH CẤU TRÚC CÚ PHÁP TỪ MCP AST]:
- {ast_summary}

{level_instruction}

[QUY TẮC BẮT BUỘC]:
1. Trả lời hoàn toàn bằng tiếng Việt tự nhiên, ấm áp, khuyến khích sinh viên.
2. TUYỆT ĐỐI KHÔNG cung cấp code Python giải hoàn chỉnh bài toán trong bất kỳ trường hợp nào.
3. Giữ dung lượng phản hồi cô đọng, súc tích (khoảng 100 - 200 từ).
"""
    return prompt


def generate_rule_based_fallback(
    exercise: dict,
    code: str,
    test_results: dict,
    ast_analysis: dict,
    hint_level: int
) -> str:
    """
    Bộ sinh gợi ý sư phạm dự phòng (Rule-based Fallback).
    Đảm bảo hệ thống luôn trả về gợi ý chất lượng ngay cả khi server LLM ngoại tuyến.
    """
    title = exercise.get("title", "Bài tập")
    all_passed = test_results.get("all_passed", False)
    passed_count = test_results.get("passed_tests", 0)
    total_count = test_results.get("total_tests", 0)
    
    if all_passed:
        return (
            f"🎉 **Chúc mừng bạn đã vượt qua toàn bộ {total_count}/{total_count} test cases của {title}!**\n\n"
            f"Đánh giá cấu trúc code: {ast_analysis.get('structural_summary', 'Cấu trúc rõ ràng, logic hợp lý.')}\n\n"
            "💡 *Gợi ý nâng cao:* Bạn hãy thử xem lại xem có thể rút gọn code hoặc sử dụng các hàm có sẵn của Python để code ngắn gọn và 'Pythonic' hơn nhé!"
        )

    # Kiểm tra lỗi cú pháp
    if not ast_analysis.get("valid", True):
        err = ast_analysis.get("syntax_error", {})
        err_msg = err.get("message", "Lỗi cú pháp") if isinstance(err, dict) else str(err)
        err_line = err.get("lineno", "?") if isinstance(err, dict) else "?"
        return (
            f"⚠️ **Mã nguồn đang gặp lỗi cú pháp (SyntaxError)!**\n\n"
            f"- Chi tiết: `{err_msg}` tại dòng **{err_line}**.\n"
            f"- *Hướng dẫn:* Bạn hãy kiểm tra lại các ký tự như dấu hai chấm `:`, dấu ngoặc `()`, hoặc khoảng cách thụt lề (indentation) ở dòng trên nhé!"
        )

    # Kiểm tra lỗi Timeout
    if any(r.get("status") == "TIMEOUT" for r in test_results.get("results", [])):
        return (
            "⏳ **Chương trình chạy quá thời gian tối đa (Time Limit Exceeded - 5.0s)!**\n\n"
            "- Nguyên nhân: Chương trình có thể chứa vòng lặp vô hạn (vòng lặp không có điều kiện dừng hoặc biến đếm không thay đổi).\n"
            "- *Gợi ý:* Hãy kiểm tra kỹ điều kiện dừng của vòng lặp `while` hoặc bước tăng của biến điều khiển."
        )

    # Tìm test case đầu tiên bị fail
    failed_tc = next((r for r in test_results.get("results", []) if r.get("status") != "PASS"), None)
    
    if hint_level == 1:
        return (
            f"🌱 **Gợi ý Level 1 (Gợi mở tư duy) cho {title}:**\n\n"
            f"Hiện tại code của bạn đã đạt **{passed_count}/{total_count}** test cases. "
            "Bạn hãy đọc lại yêu cầu đề bài và tự đặt câu hỏi:\n"
            "- Biến tích lũy của bạn đã được khởi tạo đúng giá trị ban đầu chưa?\n"
            "- Giới hạn vòng lặp `range()` đã bao gồm đầy đủ các giá trị cần tính chưa (chú ý cận trên của range)?"
        )
    elif hint_level == 2:
        if failed_tc:
            return (
                f"🔍 **Gợi ý Level 2 (Chẩn đoán lỗi) cho {title}:**\n\n"
                f"- Chương trình chưa đạt ở trường hợp: Input = `{failed_tc.get('input')}`.\n"
                f"- Kết quả kỳ vọng: `{failed_tc.get('expected_output')}`, nhưng chương trình in ra: `{failed_tc.get('actual_output') or '(không in ra gì)'}`.\n"
                f"- Phân tích: {ast_analysis.get('structural_summary', '')}\n"
                "- Hãy kiểm tra xem biến kết quả có đang tính thừa hoặc thiếu phần tử nào không nhé!"
            )
        else:
            return f"🔍 **Gợi ý Level 2:** Đã đạt {passed_count}/{total_count} test cases. Hãy rà soát lại các trường hợp biên."
    else:  # Level 3
        return (
            f"📘 **Gợi ý Level 3 (Hướng dẫn từng bước) cho {title}:**\n\n"
            "Dưới đây là dàn ý thuật toán gợi ý:\n"
            "1. Nhận dữ liệu đầu vào và chuyển về kiểu số nguyên thích hợp.\n"
            "2. Khởi tạo biến lưu kết quả với giá trị ban đầu chính xác.\n"
            "3. Sử dụng vòng lặp duyệt qua các phần tử cần thiết và cập nhật biến kết quả.\n"
            "4. In kết quả cuối cùng ra màn hình bằng hàm `print()`.\n\n"
            "*(Bạn hãy tự viết lại thành mã Python dựa trên dàn ý này nhé, cố lên!)*"
        )


async def call_qwen_api(prompt: str, timeout_seconds: float = 45.0) -> Optional[str]:
    """
    Gọi trực tiếp API Qwen2.5-14B qua HTTP POST.
    """
    headers = {
        "Content-Type": "application/json",
        "x-ollama-seckey": QWEN_SECKEY
    }
    payload = {
        "model": QWEN_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(QWEN_API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.warning(f"Qwen API trả về status code non-200: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logger.warning(f"Không thể kết nối tới Qwen API ({QWEN_API_URL}): {e}")
        return None


def _sync_call_gemini(prompt: str) -> Optional[tuple[str, str]]:
    """Hàm đồng bộ gọi Gemini API qua google-genai SDK."""
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        for model_name in GEMINI_MODELS:
            try:
                res = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                if res.text and len(res.text.strip()) > 10:
                    return res.text.strip(), f"Google {model_name}"
            except Exception as e:
                logger.warning(f"Thử nghiệm Gemini {model_name} chưa thành công: {e}")
        return None
    except Exception as e:
        logger.error(f"Lỗi khởi tạo Gemini SDK: {e}")
        return None


async def call_gemini_api(prompt: str) -> Optional[tuple[str, str]]:
    """Gọi Gemini API qua thread pool để tránh block event loop."""
    if not GEMINI_API_KEY:
        return None
    try:
        return await asyncio.to_thread(_sync_call_gemini, prompt)
    except Exception as e:
        logger.error(f"Lỗi bất đồng bộ khi gọi Gemini: {e}")
        return None


def sanitize_spoil_code(response_text: str, hint_level: int, all_passed: bool) -> str:
    """
    Bộ lọc hậu kiểm chống lộ lời giải (Anti-Spoil Guard).
    Nếu chưa pass 100% và ở hint_level 1 hoặc 2:
    Kiểm tra xem trong response_text có chứa khối code ```python ... ``` hoặc ``` ... ```
    nào dài từ 3 dòng lệnh trở lên không. Nếu có, tự động thay thế bằng thông báo sư phạm.
    """
    if all_passed or hint_level not in (1, 2):
        return response_text

    def replace_long_code_block(match):
        code_body = match.group(1).strip()
        lines = [ln for ln in code_body.splitlines() if ln.strip()]
        if len(lines) >= 3:
            return "\n\n🔒 *[Đoạn mã minh họa đã được PyTutor ẩn tự động ở Level 1-2 để bạn tự rèn luyện tư duy lập trình]*\n\n"
        return match.group(0)

    # Tìm các khối ```python ... ``` hoặc ``` ... ```
    pattern = r"```(?:python)?\s*\n(.*?)```"
    sanitized = re.sub(pattern, replace_long_code_block, response_text, flags=re.DOTALL | re.IGNORECASE)
    return sanitized


async def generate_tutor_hint(
    exercise: dict,
    code: str,
    test_results: dict,
    ast_analysis: dict,
    hint_level: int
) -> tuple[str, str]:
    """
    Hàm điều phối sinh gợi ý gia sư sư phạm:
    1. Đóng gói Context Bundle & Prompt
    2. Gọi Google Gemini AI (Chất lượng cao nhất, tiếng Việt sư phạm chuẩn mực)
    3. Thử Qwen2.5-14B nếu Gemini lỗi
    4. Kích hoạt Rule-based Fallback nếu toàn bộ mạng ngoại tuyến
    Trả về: (tutor_hint_content, source_label)
    """
    prompt = build_scaffolding_prompt(
        exercise=exercise,
        code=code,
        test_results=test_results,
        ast_analysis=ast_analysis,
        hint_level=hint_level
    )
    
    all_passed = test_results.get("all_passed", False)

    # 1. Ưu tiên hàng đầu: Gọi Google Gemini AI
    gemini_res = await call_gemini_api(prompt)
    if gemini_res:
        raw_hint, model_name = gemini_res
        sanitized_hint = sanitize_spoil_code(
            response_text=raw_hint,
            hint_level=hint_level,
            all_passed=all_passed
        )
        return sanitized_hint, model_name

    # 2. Dự phòng: Thử Qwen2.5-14B (nếu server trường mở)
    qwen_response = await call_qwen_api(prompt, timeout_seconds=15.0)
    if qwen_response and len(qwen_response) > 20:
        sanitized_hint = sanitize_spoil_code(
            response_text=qwen_response,
            hint_level=hint_level,
            all_passed=all_passed
        )
        return sanitized_hint, QWEN_MODEL

    # 3. Dự phòng cấp cuối: Rule-based Fallback
    fallback_hint = generate_rule_based_fallback(
        exercise=exercise,
        code=code,
        test_results=test_results,
        ast_analysis=ast_analysis,
        hint_level=hint_level
    )
    return fallback_hint, "Pedagogical-Rule-Engine (Offline Fallback)"

