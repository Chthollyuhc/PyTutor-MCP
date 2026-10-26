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
    hint_level: int,
    attempt_history: list[dict] = None,
    student_model: dict = None
) -> str:
    """
    Đóng gói Context Bundle và thiết lập System Prompt sư phạm theo cấp độ và mô hình thích ứng.
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

    # Ngữ cảnh lịch sử nộp bài (Attempt History)
    history_section = ""
    if attempt_history and len(attempt_history) > 0:
        history_lines = []
        for i, att in enumerate(attempt_history[:3]):
            status_str = "PASS toàn bộ" if att.get("all_passed") else f"Đạt {att.get('passed')}/{att.get('total')} tests"
            history_lines.append(f"  + Lần nộp trước #{i+1}: Mức gợi ý {att.get('hint_level', 1)} | Kết quả: {status_str} ({att.get('timestamp', '')})")
        history_section = f"""
[LỊCH SỬ NỘP BÀI TRƯỚC ĐÓ CỦA HỌC VIÊN TRONG PHIÊN NÀY]:
{"\n".join(history_lines)}
* Chỉ dẫn: Học viên đang thử nghiệm lại bài. Hãy xem xét tiến trình của họ để đưa ra gợi ý tiếp nối mang tính xây dựng, tránh lặp lại các câu hỏi mở mà họ đã xem!
"""

    # Ngữ cảnh mô hình học sinh (Student Model)
    student_model_section = ""
    if student_model and student_model.get("total_submissions", 0) > 0:
        student_model_section = f"""
[HỒ SƠ HỌC SINH THÍCH ỨNG (STUDENT MODEL)]:
- Tóm tắt năng lực: {student_model.get('summary', '')}
- Mức độ cần hỗ trợ trung bình: Level {student_model.get('average_hint_level', 1.0)}
"""

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
[CẤP ĐỘ GỢI Ý 1: GỢI MỞ TƯ DUY & KHÁI NIỆM (SOCRATIC CONCEPTUAL HINT)]
🎯 Mục tiêu: Giúp sinh viên tự định hình lại hướng tiếp cận thông qua câu hỏi gợi mở, TUYỆT ĐỐI KHÔNG can thiệp vào code hay chỉ dòng cụ thể.
📋 Quy chuẩn cấu trúc phản hồi bắt buộc:
1. 💡 **Đánh giá hướng đi:** Tóm tắt ngắn gọn giải thuật hiện tại của sinh viên đang đi đúng hay lệch hướng so với đề bài.
2. ❓ **Câu hỏi Socratic gợi mở (1-2 câu):** Đặt câu hỏi kích thích sinh viên tự suy ngẫm (về điều kiện biên, giá trị khởi tạo, hoặc cách hoạt động của vòng lặp/hàm).
3. 📖 **Khái niệm trọng tâm:** Nhắc tên các kiến thức/từ khóa Python cốt lõi cần xem lại (ví dụ: `range(start, stop)`, cách chuyển kiểu số nguyên, toán tử tích lũy).
🚫 Ràng buộc: KHÔNG trích dòng code lỗi cụ thể, KHÔNG đưa code sửa, KHÔNG tiết lộ thuật toán hoàn chỉnh.
"""
    elif hint_level == 2:
        level_instruction = """
[CẤP ĐỘ GỢI Ý 2: CHẨN ĐOÁN TRỰC DIỆN & KHOANH VÙNG DÒNG LỖI (DIAGNOSTIC & LOCALIZATION HINT)]
🎯 Mục tiêu: Chỉ rõ chính xác dòng code hoặc khối lệnh nào đang gây ra sai số và mổ xẻ nguyên nhân kỹ thuật vì sao kết quả thực tế bị lệch.
📋 Quy chuẩn cấu trúc phản hồi bắt buộc:
1. 📍 **Vị trí lỗi cụ thể trong bài của bạn:** Trích dẫn chính xác dòng code của sinh viên bị sai hoặc có vấn đề (ví dụ: `⚠️ Chú ý dòng: for i in range(1, n):` hoặc `⚠️ Lỗi ở biểu thức: tong = n * 2`).
2. 🔍 **Mổ xẻ nguyên nhân sai lệch:** Lấy test case bị FAIL làm ví dụ trực quan:
   - Với đầu vào: `Input = ...`
   - Dòng code trên của bạn cho ra: `Actual Output = ...` vì sao (giải thích máy tính đã chạy như thế nào).
   - Nhưng đề bài kỳ vọng: `Expected Output = ...`.
3. 🛠️ **Chỉ dẫn kỹ thuật để sửa:** Nêu rõ cần sửa điều kiện/biểu thức đó như thế nào bằng lời giải thích kỹ thuật (ví dụ: *"Bạn cần cho vòng lặp chạy đến `n + 1` thay vì `n` để không bỏ sót phần tử cuối cùng"*).
🚫 Ràng buộc: Không đưa code giải hoàn chỉnh cả bài, chỉ tập trung giải phẫu dòng lỗi để sinh viên tự sửa.
"""
    else:  # Level 3
        level_instruction = """
[CẤP ĐỘ GỢI Ý 3: DÀN Ý THUẬT TOÁN CHI TIẾT & KHUNG CODE MẪU (STEP-BY-STEP & CODE SKELETON)]
🎯 Mục tiêu: Hướng dẫn chi tiết từng bước thuật toán từ đầu đến cuối và cung cấp KHUNG CODE MẪU (Code Skeleton) có chỗ trống `...` hoặc `# TODO` để sinh viên điền vào.
📋 Quy chuẩn cấu trúc phản hồi bắt buộc:
1. 📝 **Các bước thực hiện thuật toán (Dàn ý 4 bước):**
   - **Bước 1:** Nhập dữ liệu đầu vào và chuyển đổi kiểu thích hợp.
   - **Bước 2:** Khởi tạo biến lưu trữ với giá trị ban đầu chính xác.
   - **Bước 3:** Tổ chức vòng lặp duyệt qua các phần tử và cập nhật kết quả.
   - **Bước 4:** In kết quả ra màn hình bằng hàm `print()`.
2. 💻 **Khung mã nguồn gợi ý (Scaffolded Code Skeleton):**
   Cung cấp một khung code Python có cấu trúc sẵn, nhưng ĐỂ TRỐNG phần biểu thức cốt lõi bằng dấu `...` hoặc `# TODO` để học sinh tự hoàn thành (tuyệt đối không điền sẵn đáp án hoàn chỉnh để copy-paste).
   *Ví dụ minh họa cấu trúc khung code:*
   ```python
   # Khung code hướng dẫn giải:
   n = int(input())
   # Khởi tạo biến
   ket_qua = ...
   for i in range(1, ...):  # TODO: Điền cận trên đúng
       ket_qua = ...       # TODO: Cập nhật biến tích lũy
   print(ket_qua)
   ```
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
{history_section}{student_model_section}
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
            f"💡 **[MỨC 1: GỢI MỞ TƯ DUY & KHÁI NIỆM]**\n\n"
            f"Hiện tại code của bạn đã đạt **{passed_count}/{total_count}** test cases. Hãy suy ngẫm về hướng tiếp cận thuật toán:\n\n"
            f"1. 🎯 **Đánh giá hướng đi:** {ast_analysis.get('structural_summary', 'Bạn đang tiếp cận bài toán bằng các cấu trúc lập trình cơ bản.')}\n\n"
            f"2. ❓ **Câu hỏi Socratic gợi mở:**\n"
            f"   - Biến lưu trữ kết quả của bạn đã được gán giá trị khởi tạo chính xác cho trường hợp đầu tiên chưa?\n"
            f"   - Trong Python, dải `range(start, stop)` sẽ dừng lại ở giá trị nào? Có bao gồm giá trị `stop` không hay dừng ở `stop - 1`?\n\n"
            f"3. 📖 **Khái niệm trọng tâm:** Xem lại cú pháp vòng lặp `for ... in range(...)`, kỹ thuật tích lũy biến số `+=`, và cách đọc dữ liệu bằng `input()`."
        )
    elif hint_level == 2:
        if failed_tc:
            inp_val = failed_tc.get('input', '').strip()
            exp_val = failed_tc.get('expected_output', '').strip()
            act_val = failed_tc.get('actual_output', '').strip() or '(không in ra gì hoặc chương trình kết thúc sớm)'
            return (
                f"🔍 **[MỨC 2: CHẨN ĐOÁN CHI TIẾT & KHOANH VÙNG LỖI]**\n\n"
                f"1. 📍 **Khoanh vùng vị trí lỗi trong code:**\n"
                f"   - Cấu trúc mã nguồn AST: {ast_analysis.get('structural_summary', 'Kiểm tra cấu trúc vòng lặp hoặc biểu thức gán')}.\n"
                f"   - Lỗi nằm ở **cận trên của vòng lặp** hoặc **biểu thức cập nhật giá trị** khiến kết quả bị lệch.\n\n"
                f"2. 🔍 **Mổ xẻ Test Case bị lỗi:**\n"
                f"   - **Đầu vào (Input):** `{inp_val}`\n"
                f"   - **Kết quả thực tế từ code của bạn:** `{act_val}`\n"
                f"   - **Kết quả đề bài kỳ vọng (Expected):** `{exp_val}`\n\n"
                f"3. 🛠️ **Chỉ dẫn sửa lỗi:**\n"
                f"   - Kết quả thực tế bị lệch so với kỳ vọng do vòng lặp của bạn đang dừng sớm hơn 1 bước hoặc biểu thức tính toán chưa đúng.\n"
                f"   - Nếu bạn muốn vòng lặp tính đến $n$, hãy đảm bảo cận trên là `n + 1` vì `range(1, n)` chỉ chạy đến $n - 1$."
            )
        else:
            return (
                f"🔍 **[MỨC 2: CHẨN ĐOÁN CHI TIẾT]**\n\n"
                f"Code của bạn đã đạt {passed_count}/{total_count} test cases nhưng chưa bao quát được các trường hợp đặc biệt. Hãy rà soát lại điều kiện biên (giá trị nhỏ nhất hoặc chuỗi rỗng)."
            )
    else:  # Level 3
        return (
            f"📘 **[MỨC 3: DÀN Ý THUẬT TOÁN CHI TIẾT & KHUNG CODE MẪU]**\n\n"
            f"Dưới đây là dàn ý thuật toán chi tiết và khung code mẫu từng bước cho bài **{title}**:\n\n"
            f"### 1. Dàn ý các bước thuật toán:\n"
            f"- **Bước 1:** Nhập dữ liệu đầu vào và chuyển về kiểu số thích hợp: `n = int(input())`.\n"
            f"- **Bước 2:** Khởi tạo biến lưu kết quả với giá trị ban đầu chính xác (ví dụ `ans = 0` khi tính tổng, hoặc `ans = 1` khi tính giai thừa/tích).\n"
            f"- **Bước 3:** Sử dụng vòng lặp duyệt qua các giá trị cần xử lý và thực hiện phép tính tích lũy.\n"
            f"- **Bước 4:** In kết quả cuối cùng ra màn hình bằng hàm `print(ans)`.\n\n"
            f"### 2. Khung mã nguồn mẫu (Hãy tự điền vào các chỗ trống `...`):\n"
            f"```python\n"
            f"# Khung code hướng dẫn giải:\n"
            f"n = int(input())\n\n"
            f"# Bước 2: Khởi tạo biến kết quả ban đầu\n"
            f"ans = 0\n\n"
            f"# Bước 3: Duyệt và cộng dồn\n"
            f"for i in range(1, ...):  # TODO: Điền cận trên đúng (gợi ý: n + 1)\n"
            f"    ans += ...          # TODO: Điền biến cần cộng dồn vào ans\n\n"
            f"# Bước 4: In kết quả\n"
            f"print(ans)\n"
            f"```\n\n"
            f"*(Bạn hãy quan sát khung code trên, suy nghĩ và tự điền các phần `...` vào trình biên dịch nhé!)*"
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
    hint_level: int,
    attempt_history: list[dict] = None,
    student_model: dict = None
) -> tuple[str, str]:
    """
    Hàm điều phối sinh gợi ý gia sư sư phạm:
    1. Đóng gói Context Bundle, Lịch sử nộp bài, Mô hình học sinh & Prompt
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
        hint_level=hint_level,
        attempt_history=attempt_history,
        student_model=student_model
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


async def generate_chat_followup(
    exercise: dict,
    code: str,
    user_message: str,
    history: list = None,
    ast_summary: str = ""
) -> tuple[str, str]:
    """
    Sinh phản hồi cho câu hỏi làm rõ của sinh viên trong phiên chat đa lượt (Phase 8).
    Tuân thủ nghiêm ngặt nguyên tắc Socratic và Anti-Spoil Guard (Không giải hộ).
    """
    title = exercise.get("title", "Bài tập lập trình Python")
    desc = exercise.get("description", "")
    
    # Giới hạn 6 lượt chat gần nhất để tránh tràn token
    recent_history = history[-6:] if history else []
    history_turns = []
    for msg in recent_history:
        r = msg.get("role", "user") if isinstance(msg, dict) else getattr(msg, "role", "user")
        c = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
        speaker = "Sinh viên" if r == "user" else "Gia sư PyTutor"
        history_turns.append(f"{speaker}: {c}")

    history_text = "\n".join(history_turns) if history_turns else "(Bắt đầu cuộc trò chuyện làm rõ)"

    prompt = f"""
Bạn là PyTutor AI — Gia sư Sư phạm Thông minh Hỗ trợ Học Lập trình Python.
Sinh viên đang làm bài tập: "{title}".
[MÔ TẢ BÀI TẬP]:
{desc}

[MÃ NGUỒN HIỆN TẠI CỦA SINH VIÊN]:
```python
{code}
```
{f"[PHÂN TÍCH CẤU TRÚC CODE (AST)]:\n{ast_summary}" if ast_summary else ""}

[LỊCH SỬ TRAO ĐỔI TRƯỚC ĐÓ]:
{history_text}

[CÂU HỎI TIẾP THEO CỦA SINH VIÊN]:
"{user_message}"

[CHỈ DẪN SƯ PHẠM & NGUYÊN TẮC BẢO VỆ (ANTI-SPOIL GUARD)]:
1. Trả lời trực tiếp, thân thiện, dễ hiểu bằng tiếng Việt về câu hỏi/thắc mắc của sinh viên.
2. TUYỆT ĐỐI KHÔNG BAO GIỜ viết code giải hoàn chỉnh của bài toán dù sinh viên có yêu cầu hay nài nỉ.
3. Nếu sinh viên hỏi cú pháp (như vòng lặp for, range, split, len...), hãy giải thích cơ chế hoạt động và chỉ đưa ra 1 ví dụ trừu tượng ngắn (1-2 dòng) KHÔNG liên quan trực tiếp đến dữ liệu bài tập để sinh viên tự áp dụng.
4. Động viên sinh viên tự viết tiếp và thử chạy lại chương trình.
"""

    # Gọi Gemini
    gemini_res = await call_gemini_api(prompt)
    if gemini_res:
        raw_reply, model_name = gemini_res
        sanitized = sanitize_spoil_code(raw_reply, hint_level=1, all_passed=False)
        return sanitized, model_name

    # Dự phòng offline
    return (
        "Chào bạn! Gia sư PyTutor đã ghi nhận câu hỏi của bạn. "
        "Hãy đối chiếu với gợi ý ở các mức 1, 2, 3 bên trên và thử chạy lại từng bước để quan sát kết quả nhé! "
        "Nếu gặp lỗi cú pháp, bạn hãy chú ý thụt dòng (indentation) và dấu hai chấm ':' ở cuối câu lệnh.",
        "Rule-Based Assistant"
    )


async def generate_pythonic_review(
    exercise: dict,
    student_code: str
) -> tuple[dict, str]:
    """
    [Phase 10: Senior Pythonista Code Review Engine]
    Đóng vai trò Senior Python Tech Lead đánh giá mã nguồn sinh viên đã giải đúng (Passed):
    - Đánh giá Điểm Clean Code (0-100, tối thiểu 70 cho bài đã pass để khích lệ).
    - Chỉ ra điểm mạnh (strengths).
    - Chỉ ra các cơ hội tối ưu hoá (improvements) theo chuẩn PEP 8 và Pythonic idioms.
    - Cung cấp đoạn mã Pythonic chuẩn mực mẫu (pythonic_code).
    - Giải thích lý do tối ưu (explanation).
    """
    title = exercise.get("title", "Bài tập lập trình Python")
    desc = exercise.get("description", "")

    prompt = f"""
Bạn là một Senior Python Architect và Giảng viên Cao cấp tận tâm của hệ thống PyTutor.
Học viên vừa hoàn thành xuất sắc (Passed 100% test cases) bài tập: "{title}".

[MÔ TẢ BÀI TẬP]:
{desc}

[MÃ NGUỒN CỦA HỌC VIÊN ĐÃ GIẢI ĐÚNG]:
```python
{student_code}
```

Nhiệm vụ của bạn là thực hiện "Post-Acceptance Code Review" để giúp học viên nâng tầm phong cách lập trình từ "người mới học viết code chạy được" thành "Pythonista chuyên nghiệp viết code thanh lịch, chuẩn mực và tối ưu".

YÊU CẦU ĐÁNH GIÁ (BẮT BUỘC TRẢ VỀ ĐỊNH DẠNG JSON HỢP LỆ VỚI CÁC TRƯỜNG SAU):
1. "clean_score": Một số nguyên từ 70 đến 98 đánh giá độ sạch, tuân thủ PEP 8 và tính Pythonic (không chấm dưới 70 vì học viên đã giải đúng).
2. "strengths": Nhận xét 1-2 câu khen ngợi cụ thể về điểm tốt trong code của học viên (ví dụ: tư duy thuật toán đúng, đặt tên biến rõ ràng, xử lý logic mạch lạc).
3. "improvements": 1-2 điểm cụ thể có thể làm code ngắn gọn, thanh lịch hơn bằng các đặc trưng tinh hoa của Python (ví dụ: dùng sum() thay vì for loop, dùng list comprehension, toán tử ba ngôi ternary, chuỗi f-string, built-in functions...).
4. "pythonic_code": Đoạn mã Python viết lại hoàn chỉnh nhất theo phong cách Pythonic chuẩn mực (ngắn gọn, tối ưu, dễ đọc).
5. "explanation": Lời giải thích dễ hiểu (2-3 câu) tại sao đoạn mã Pythonic này lại tốt hơn (ví dụ: chạy ở tầng C tối ưu, không tốn biến trung gian, tuân thủ Zen of Python "Readability counts").

LƯU Ý: Chỉ trả về duy nhất chuỗi JSON hợp lệ với đúng 5 khóa trên, không kèm lời dẫn giải bên ngoài.
"""

    gemini_res = await call_gemini_api(prompt)
    if gemini_res:
        raw_text, model_name = gemini_res
        try:
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return {
                "clean_score": int(data.get("clean_score", 85)),
                "strengths": data.get("strengths", "Bạn đã áp dụng tư duy thuật toán rất chính xác và giải quyết trọn vẹn bài toán."),
                "improvements": data.get("improvements", "Có thể sử dụng các hàm built-in của Python để mã nguồn ngắn gọn và tối ưu hơn."),
                "pythonic_code": data.get("pythonic_code", student_code),
                "explanation": data.get("explanation", "Phiên bản Pythonic tận dụng tối đa các hàm cốt lõi tối ưu của Python.")
            }, model_name
        except Exception as e:
            logger.warning(f"Lỗi phân tích JSON từ phản hồi review của Gemini: {e}")

    # Fallback chất lượng cao nếu offline
    code_lines = len(student_code.strip().splitlines())
    return {
        "clean_score": 85 if code_lines > 3 else 92,
        "strengths": "Cấu trúc chương trình rõ ràng, biến được khởi tạo và cập nhật logic chuẩn xác.",
        "improvements": "Trong Python hiện đại, bạn có thể tận dụng các hàm tích hợp sẵn (built-in) như sum() hoặc slicing để mã nguồn tinh gọn hơn.",
        "pythonic_code": student_code.strip(),
        "explanation": "Viết mã nguồn chuẩn Pythonic giúp tiết kiệm bộ nhớ, tăng tốc độ thực thi và thể hiện phong cách của một lập trình viên chuyên nghiệp."
    }, "Pedagogical-Rule-Reviewer"



