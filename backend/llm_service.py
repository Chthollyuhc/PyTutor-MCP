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
from backend.prompt_templates import (
    SYSTEM_RULES_TEXT, render_socratic_prompt, render_instructor_prompt, render_reviewer_prompt,
)
from backend.rag.retriever import retrieve_knowledge
from backend.guardrails import check_student_output, enforce_level3_skeleton
from backend.adaptive_policy import ADAPTATION_INSTRUCTIONS
from pytutor_shared.learner_model import STATE_LABELS

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
    student_model: dict = None,
    adaptive_strategy: dict = None
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

    strategy = adaptive_strategy or {}
    strategy_names = {
        "solution_review": "Sinh viên đã vượt qua bài; tập trung phản hồi và củng cố.",
        "recurring_difficulty": "Có nhiều lần thử; tránh lặp nguyên văn gợi ý trước và chia nhỏ bước tiếp theo.",
        "failed_case_diagnosis": "Có test thất bại; ưu tiên giải thích dựa trên bằng chứng test.",
        "conceptual_start": "Chưa có đủ lịch sử; bắt đầu bằng gợi mở khái niệm an toàn.",
    }
    strategy_section = f"""
[CHIẾN LƯỢC PHẢN HỒI]
- Mã lý do: {strategy.get('reason_code', 'conceptual_start')}
- Căn cứ: {', '.join(strategy.get('evidence', [])) or 'Chưa đủ dữ liệu lịch sử'}
- Trạng thái dữ liệu: {strategy.get('data_status', 'insufficient')}
- Hướng dẫn: {strategy_names.get(strategy.get('strategy'), strategy_names['conceptual_start'])}
- Giữ nguyên cấp độ người học yêu cầu: Level {hint_level}; không tự tăng mức tiết lộ.
"""
    if any(a.get("code") == "no_code_yet" for a in strategy.get("adaptations", [])):
        strategy_section += f"- LƯU Ý QUAN TRỌNG: {ADAPTATION_INSTRUCTIONS['no_code_yet']}\n"

    # Mô hình người học v3: chỉ điều chỉnh cách diễn đạt/độ chia bước, không đổi mức tiết lộ.
    learner_section = ""
    signals = strategy.get("learner_signals") or {}
    if signals:
        kc_lines = [f"  + {v.get('label_vi')}: {STATE_LABELS.get(v.get('state'), v.get('state'))} "
                    f"(dựa trên {v.get('others_attempted', 0)} bài khác đã nộp)" for v in signals.get("exercise_kcs", [])]
        adapt_lines = [f"  + [{a.get('code')}] {ADAPTATION_INSTRUCTIONS.get(a.get('code'), '')}"
                       for a in strategy.get("adaptations", []) if a.get("code") in ADAPTATION_INSTRUCTIONS]
        learner_section = "\n[MÔ HÌNH NGƯỜI HỌC - heuristic chưa hiệu chuẩn, chỉ dùng để điều chỉnh cách diễn đạt]\n"
        learner_section += "- Nhóm kiến thức liên quan tới bài này:\n" + ("\n".join(kc_lines) if kc_lines else "  + (chưa xác định)") + "\n"
        if strategy.get("diagnosis_focus"):
            learner_section += f"- Dạng lỗi quan sát ở lượt này: {strategy['diagnosis_focus']}\n"
        if adapt_lines:
            learner_section += "- Điều chỉnh cần áp dụng:\n" + "\n".join(adapt_lines) + "\n"
        learner_section += ("- Không nhận xét năng lực của sinh viên, không nêu các nhãn trên cho sinh viên như một đánh giá; "
                            f"giữ nguyên Level {hint_level}.\n")

    # Khung phản hồi hình thành (formative feedback): mục tiêu → bằng chứng → bước kế tiếp.
    formative_section = """
[KHUNG PHẢN HỒI HÌNH THÀNH - ÁP DỤNG CHO MỌI CẤP ĐỘ]
Mỗi phản hồi phải trả lời đủ ba ý, theo đúng thứ tự, trong giới hạn tiết lộ của cấp độ được yêu cầu:
1. Mục tiêu / đang ở đâu: bài yêu cầu gì và bài làm hiện đạt đến đâu (dùng số kiểm thử đạt thực tế).
2. Bằng chứng: chỉ nêu điều quan sát được từ kết quả kiểm thử, phân tích AST hoặc lịch sử ở trên. Không suy đoán nguyên nhân không có trong dữ liệu; nếu dữ liệu chưa đủ thì nói rõ là chưa đủ.
3. Bước kế tiếp vừa sức: đúng MỘT việc cụ thể sinh viên có thể tự làm ngay (một câu hỏi tự kiểm hoặc một phép thử), không liệt kê nhiều hướng.
Không lặp lại nguyên văn gợi ý của các lần trước. Không nhận xét về năng lực của sinh viên; chỉ nhận xét về bài làm.
"""

    # Chỉ dẫn sư phạm theo Level
    if all_passed:
        level_instruction = """
[TÌNH HUỐNG: SINH VIÊN ĐÃ ĐẠT 100% TEST CASES - RÚT GIÀN GIÁO]
- Ghi nhận ngắn gọn cách làm đã hiệu quả (nêu cụ thể dựa trên AST, không khen chung chung).
- KHÔNG đưa thêm gợi ý sửa lỗi. Đặt đúng 1 câu hỏi tự kiểm để sinh viên tự giải thích vì sao lời giải đúng (ví dụ: trường hợp biên nào đã được xử lý và ở dòng nào).
- Nêu 1 hướng mở rộng TÙY CHỌN (ví dụ: viết lại gọn hơn, thử đầu vào lớn hơn); nói rõ đây là tùy chọn.
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
🚫 Ranh giới với Mức 2: KHÔNG nêu đầu vào, đầu ra thực tế hay đầu ra kỳ vọng cụ thể của kiểm thử nào (đó là bằng chứng của Mức 2); chỉ nói tổng quát bài đang đạt bao nhiêu kiểm thử. Câu hỏi gợi mở phải nói về KHÁI NIỆM chung, không chỉ ra tham số hay biểu thức nào trong bài làm là sai.
"""
    elif hint_level == 2:
        level_instruction = """
[CẤP ĐỘ GỢI Ý 2: CHẨN ĐOÁN TRỰC DIỆN & KHOANH VÙNG DÒNG LỖI (DIAGNOSTIC & LOCALIZATION HINT)]
🎯 Mục tiêu: Chỉ rõ chính xác dòng code hoặc khối lệnh nào đang gây ra sai số và mổ xẻ nguyên nhân kỹ thuật vì sao kết quả thực tế bị lệch.
📋 Quy chuẩn cấu trúc phản hồi bắt buộc:
1. 📍 **Vị trí lỗi cụ thể trong bài của bạn:** Trích dẫn chính xác MỘT dòng code của sinh viên bị sai hoặc có vấn đề (ví dụ: `⚠️ Chú ý dòng: for i in range(1, n):` hoặc `⚠️ Lỗi ở biểu thức: tong = n * 2`). Chỉ trích MỘT dòng trong cả câu trả lời; nếu có nhiều dòng liên quan, chọn dòng đầu tiên gây sai và mô tả các dòng còn lại bằng lời, không chép lại.
2. 🔍 **Mổ xẻ nguyên nhân sai lệch:** Lấy test case bị FAIL làm ví dụ trực quan:
   - Với đầu vào: `Input = ...`
   - Dòng code trên của bạn cho ra: `Actual Output = ...` vì sao (giải thích máy tính đã chạy như thế nào).
   - Nhưng đề bài kỳ vọng: `Expected Output = ...`.
3. 🧭 **Hướng cần xem lại (KHÔNG nêu cách sửa):** Chỉ ra PHẦN nào của chương trình và KHÁI NIỆM nào cần nghĩ lại, rồi kết thúc bằng đúng MỘT câu hỏi để sinh viên tự đưa ra cách sửa (ví dụ: *"Với `Input = 3`, vòng lặp của bạn chạy qua những giá trị `i` nào, và có giá trị nào đề bài cần mà vòng lặp bỏ qua không?"*).
🚫 Ràng buộc: Không đưa code giải hoàn chỉnh cả bài. Không viết ra điều kiện, biểu thức, giá trị cận hay thuật toán thay thế (đó là việc của Mức 3); không nói "bạn cần đổi X thành Y", "nên dùng điều kiện ...", "hãy in ... khi ...". Chỉ giải phẫu nguyên nhân và hướng suy nghĩ để sinh viên tự sửa.
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
{history_section}{student_model_section}{strategy_section}{learner_section}{formative_section}
{level_instruction}

[QUY TẮC BẮT BUỘC]:
1. Trả lời hoàn toàn bằng tiếng Việt tự nhiên, ấm áp, khuyến khích sinh viên.
2. TUYỆT ĐỐI KHÔNG cung cấp code Python giải hoàn chỉnh bài toán trong bất kỳ trường hợp nào.
3. Giữ dung lượng phản hồi cô đọng, súc tích (khoảng 100 - 200 từ).
"""
    return prompt


def _first_failed_test(test_results: dict) -> Optional[dict]:
    return next((r for r in (test_results or {}).get("results", [])
                 if r.get("status") not in ("PASS", "SKIPPED")), None)


def _observed_difference(expected: str, actual: str) -> str:
    """Mô tả khác biệt QUAN SÁT ĐƯỢC giữa đầu ra kỳ vọng và thực tế; không suy đoán nguyên nhân."""
    exp, act = (expected or "").strip(), (actual or "").strip()
    if not act:
        return "chương trình không in ra gì cho đầu vào này"
    if exp.lower() == act.lower():
        return "nội dung trùng nhau nhưng khác chữ hoa/chữ thường"
    if "".join(exp.split()) == "".join(act.split()):
        return "nội dung trùng nhau nhưng khác khoảng trắng hoặc xuống dòng"
    try:
        diff = float(act) - float(exp)
        return f"kết quả là số và lệch {diff:+g} so với kỳ vọng"
    except ValueError:
        pass
    if len(act.splitlines()) != len(exp.splitlines()):
        return f"số dòng in ra khác nhau ({len(act.splitlines())} so với {len(exp.splitlines())} dòng kỳ vọng)"
    return "nội dung in ra khác với kỳ vọng"


def _self_check_questions(failed_tc: Optional[dict], ast_analysis: dict) -> list[str]:
    """Chọn câu hỏi tự kiểm theo bằng chứng có thật (loại lỗi của test, cấu trúc AST)."""
    status = (failed_tc or {}).get("status", "")
    questions: list[str] = []
    if status == "RUNTIME_ERROR":
        questions.append("Thông báo lỗi thuộc loại nào, và giá trị nào trong chương trình đã dẫn tới lỗi đó?")
    elif failed_tc and not (failed_tc.get("actual_output") or "").strip():
        questions.append("Chương trình đã gọi `print()` để in kết quả cuối cùng chưa, và lệnh đó có được chạy tới không?")
    else:
        questions.append("Với một đầu vào nhỏ, bạn tự tính tay ra kết quả nào và chương trình in ra kết quả nào?")
    if ast_analysis.get("has_loops"):
        questions.append("Vòng lặp của bạn đi qua giá trị đầu tiên và giá trị cuối cùng nào? Có khớp với yêu cầu đề bài không?")
    if ast_analysis.get("has_accumulator"):
        questions.append("Biến tích lũy được khởi tạo bằng giá trị nào, ở trước hay trong vòng lặp?")
    if len(questions) < 2:
        questions.append("Đề bài có nêu trường hợp đặc biệt nào (giá trị nhỏ nhất, bằng 0, chuỗi rỗng) mà bài làm chưa xét không?")
    return questions[:2]


def build_pass_feedback(exercise: dict, test_results: dict, ast_analysis: Optional[dict] = None,
                        adaptive_strategy: Optional[dict] = None) -> str:
    """Phản hồi tất định khi đã đạt 100% kiểm thử: rút giàn giáo, không gọi LLM.

    Ghi nhận bằng chứng → một câu tự kiểm → một hướng mở rộng tùy chọn.
    """
    total = (test_results or {}).get("total_tests", 0)
    title = (exercise or {}).get("title", "bài tập")
    summary = (ast_analysis or {}).get("structural_summary", "")
    lines = [
        f"🎉 **Chúc mừng!** Bài làm của bạn đã vượt qua {total}/{total} kiểm thử của {title}.",
    ]
    if summary:
        lines.append(f"🔎 **Bằng chứng:** {summary}")
    lines.append("❓ **Tự kiểm lại:** Trường hợp biên nào của đề đã được bài làm xử lý, và ở dòng nào? "
                 "Hãy thử tự giải thích bằng một câu trước khi sang bài mới.")
    lines.append("➡️ **Mở rộng (tùy chọn):** thử viết lại lời giải gọn hơn hoặc mở Thử thách tối ưu code Pythonic.")
    if any(a.get("code") == "independence_check" for a in (adaptive_strategy or {}).get("adaptations", [])):
        lines.append("🧭 **Gợi ý cho bài sau (tùy chọn):** trước khi xin Gia sư AI, thử Chạy thử và tự nêu giả thuyết của bạn; "
                     "cần hỗ trợ thì vẫn xin bình thường.")
    return "\n\n".join(lines)


def _level3_progress_note(code: str, adaptive_strategy: Optional[dict] = None) -> str:
    """Đối chiếu bài làm hiện tại với dàn ý 4 bước và chọn MỘT bước kế tiếp còn thiếu.

    Chỉ dựa vào dấu hiệu quan sát được trong mã (có `input(`, có `print(`, có rẽ nhánh/vòng lặp);
    không đánh giá các bước đó đúng hay sai. Mục đích: rút giàn giáo cho phần người học đã tự viết.
    """
    lines = [ln for ln in (code or "").splitlines() if ln.strip() and not ln.strip().startswith("#")]
    has_input = any("input(" in ln for ln in lines)
    has_print = any("print(" in ln for ln in lines)
    has_flow = any(re.match(r"\s*(if|for|while)\b", ln) for ln in lines)
    seen = [name for name, ok in (("Bước 1 (đọc dữ liệu)", has_input), ("Bước 3 (rẽ nhánh/vòng lặp)", has_flow),
                                  ("Bước 4 (in kết quả)", has_print)) if ok]
    observed = (f"👀 **Đã thấy trong bài làm:** {', '.join(seen)}. Hệ thống chỉ thấy các phần này *có mặt*, "
                f"chưa biết chúng đã đúng hay chưa.\n\n") if seen else ""
    if not has_input:
        step = "viết Bước 1 trước, rồi in thử giá trị vừa đọc và bấm Chạy thử để chắc phần nhập đúng."
    elif not has_print:
        step = ("bạn đã có Bước 1. Hãy viết Bước 4 trước (in tạm một giá trị), Chạy thử để chắc phần nhập/xuất "
                "đúng định dạng, rồi mới viết Bước 3.")
    elif not has_flow:
        step = ("phần nhập và in đã có. Giờ tập trung vào Bước 3: tự tính tay với một đầu vào nhỏ, "
                "viết lại các thao tác bạn vừa làm thành lệnh.")
    else:
        step = ("bài làm đã có đủ bốn phần của dàn ý, nên chỗ cần xem lại là Bước 2 và Bước 3. Dùng **Chạy từng bước** "
                "với một đầu vào chưa đạt và tìm dòng đầu tiên mà giá trị biến khác điều bạn dự tính.")
    return f"{observed}{_next_step_line(step, adaptive_strategy)}"


def _adaptation(adaptive_strategy: Optional[dict], code: str) -> Optional[dict]:
    return next((a for a in (adaptive_strategy or {}).get("adaptations", []) if a.get("code") == code), None)


def _next_step_line(step: str, adaptive_strategy: Optional[dict]) -> str:
    """Dòng 'Bước kế tiếp' theo độ chi tiết đã chọn. Mẫu cố định, chỉ nói về quy trình, không nêu lời giải."""
    gran = (adaptive_strategy or {}).get("granularity")
    if gran == "fine":
        return ("➡️ **Bước kế tiếp (chia nhỏ thành 2 bước):**\n"
                f"1. {step[:1].upper() + step[1:]}\n"
                "2. Sau đó bấm Chạy thử và ghi lại một điều bạn quan sát được (kết quả in ra hoặc thông báo lỗi) trước khi sửa tiếp.")
    if gran == "coarse":
        return ("➡️ **Bước kế tiếp (tự kiểm trước):** hãy tự nêu một câu giả thuyết: *chỗ nào trong chương trình có thể làm kết quả lệch?* "
                "Rồi bấm Chạy thử để tự kiểm giả thuyết đó trước khi đọc thêm.")
    return f"➡️ **Bước kế tiếp:** {step}"


def _model_notes(adaptive_strategy: Optional[dict]) -> str:
    """Các câu ghi chú cố định theo mã điều chỉnh của mô hình người học (ngoài khối mã)."""
    notes = []
    bridge = _adaptation(adaptive_strategy, "bridge_from_mastered")
    if bridge:
        ctx = bridge.get("context", {})
        notes.append(f"🌉 **Nối với điều bạn đã làm:** nhóm **{ctx.get('kc_label', '')}** bạn đã nộp đạt ở bài "
                     f"**{ctx.get('exercise_title', '')}**. Hãy nhớ lại bạn đã tách phần việc ở bài đó thành những bước nào.")
    rep = _adaptation(adaptive_strategy, "repeated_error_type")
    if rep:
        ctx = rep.get("context", {})
        notes.append(f"🔎 **Dạng lỗi lặp lại:** loại lỗi lần này (`{ctx.get('error_class', '')}`) giống loại lỗi bạn từng gặp ở nhóm "
                     f"**{ctx.get('kc_label', '')}**; hãy so sánh với cách bạn đã sửa trước đó.")
    return "\n\n".join(notes)


def _no_code_reply(exercise: dict, test_results: dict, hint_level: int, adaptive_strategy: Optional[dict]) -> str:
    """Gợi ý Mức 1/2 khi sinh viên chưa viết code: giúp hiểu đề, không nói về test thất bại."""
    title = exercise.get("title", "Bài tập")
    example = next((r for r in test_results.get("results", []) if (r.get("expected_output") or "").strip()), None)
    sample = ""
    if hint_level == 2 and example:
        sample = (f"\n\n🔎 **Một ví dụ từ đề:** với đầu vào `{(example.get('input') or '').strip() or '(không có)'}` "
                  f"chương trình cần in `{(example.get('expected_output') or '').strip()}`.")
    head = ("💡 **[MỨC 1: GỢI MỞ TƯ DUY & KHÁI NIỆM]**" if hint_level == 1
            else "🔍 **[MỨC 2: HIỂU ĐỀ & XÁC ĐỊNH ĐẦU VÀO/ĐẦU RA]**")
    questions = ["Đề bài cho bạn dữ liệu gì, và dữ liệu đó nhập vào theo định dạng nào?",
                 "Chương trình cần in ra điều gì? Thử nói bằng lời với một ví dụ nhỏ.",
                 "Nếu tự tính bằng tay với ví dụ đó, bạn sẽ làm những thao tác nào, theo thứ tự nào?"]
    if hint_level == 2:
        questions = questions[:2]
    step = ("chọn một câu hỏi ở trên, trả lời bằng lời hoặc ghi chú, rồi viết một dòng đầu tiên (ví dụ dòng đọc dữ liệu "
            "bằng `input()`) và bấm Chạy thử. Cần dàn ý chi tiết hơn thì xin gợi ý Mức 3.")
    return (f"{head}\n\n🎯 **Đang ở đâu:** bài **{title}**, bạn chưa viết dòng code nào, bắt đầu từ việc hiểu đề là hợp lý.{sample}\n\n"
            "❓ **Câu hỏi để bắt đầu:**\n" + "\n".join(f"- {q}" for q in questions) + "\n\n"
            f"{_next_step_line(step, adaptive_strategy)}")


def generate_rule_based_fallback(
    exercise: dict,
    code: str,
    test_results: dict,
    ast_analysis: dict,
    hint_level: int,
    adaptive_strategy: Optional[dict] = None,
) -> str:
    """
    Bộ sinh gợi ý sư phạm dự phòng (Rule-based Fallback), chạy khi không có LLM.

    Tuân theo khung phản hồi hình thành: (1) đang ở đâu → (2) bằng chứng quan sát được
    → (3) một bước kế tiếp. Chỉ nêu điều có trong kết quả kiểm thử/AST; không khẳng định
    nguyên nhân mà dữ liệu không cho thấy.
    """
    title = exercise.get("title", "Bài tập")
    all_passed = test_results.get("all_passed", False)
    passed_count = test_results.get("passed_tests", 0)
    total_count = test_results.get("total_tests", 0)
    ast_analysis = ast_analysis or {}
    strategy = (adaptive_strategy or {}).get("strategy", "")

    if all_passed:
        return build_pass_feedback(exercise, test_results, ast_analysis)

    # Chưa có code: AST coi code rỗng là lỗi cú pháp, nên phải xử lý trước các nhánh lỗi bên dưới.
    no_code = bool(_adaptation(adaptive_strategy, "no_code_yet"))
    if no_code and hint_level in (1, 2):
        return _no_code_reply(exercise, test_results, hint_level, adaptive_strategy)

    # Lỗi cú pháp: bằng chứng là thông báo của trình phân tích cú pháp.
    if not no_code and not ast_analysis.get("valid", True):
        err = ast_analysis.get("syntax_error", {})
        err_msg = err.get("message", "Lỗi cú pháp") if isinstance(err, dict) else str(err)
        err_line = err.get("lineno", "?") if isinstance(err, dict) else "?"
        return (
            f"⚠️ **Mã nguồn đang gặp lỗi cú pháp (SyntaxError)!**\n\n"
            f"🎯 **Đang ở đâu:** chương trình chưa chạy được nên chưa kiểm thử nào được chấm.\n\n"
            f"🔎 **Bằng chứng:** `{err_msg}` tại dòng **{err_line}**.\n\n"
            f"➡️ **Bước kế tiếp:** đọc lại dòng {err_line} và dòng ngay phía trên; kiểm tra dấu hai chấm `:`, "
            f"cặp ngoặc và khoảng thụt lề rồi bấm Chạy thử lại."
        )

    # Quá thời gian: bằng chứng là trạng thái TIMEOUT của sandbox.
    if not no_code and any(r.get("status") == "TIMEOUT" for r in test_results.get("results", [])):
        loop_note = ("Bài làm có dùng vòng lặp." if ast_analysis.get("has_loops")
                     else "Phân tích cấu trúc chưa thấy vòng lặp; hãy xem chương trình có đang chờ thêm dữ liệu nhập không.")
        return (
            "⏳ **Chương trình chạy quá thời gian tối đa (Time Limit Exceeded - 5.0s)!**\n\n"
            f"🎯 **Đang ở đâu:** đạt {passed_count}/{total_count} kiểm thử.\n\n"
            f"🔎 **Bằng chứng:** có kiểm thử bị dừng vì quá 5 giây. {loop_note}\n\n"
            "➡️ **Bước kế tiếp:** với mỗi vòng lặp, tự trả lời: biến nào thay đổi sau mỗi lượt và điều kiện dừng trở thành sai khi nào?"
        )

    failed_tc = _first_failed_test(test_results)
    questions = _self_check_questions(failed_tc, ast_analysis)
    progress = f"🎯 **Đang ở đâu:** bài **{title}** đang đạt **{passed_count}/{total_count}** kiểm thử."
    if _adaptation(adaptive_strategy, "no_code_yet"):
        progress = f"🎯 **Đang ở đâu:** bài **{title}**, bạn chưa viết dòng code nào; đây là khung để bắt đầu."
    repeat_note = ""
    concept_rec = _adaptation(adaptive_strategy, "concept_recurring_difficulty")
    if concept_rec:
        ctx = concept_rec.get("context", {})
        repeat_note = (f"\n\n🔁 Nhóm kiến thức **{ctx.get('kc_label', '')}** từng gây vướng ở bài **{ctx.get('exercise_title', '')}**. "
                       "Lần này hãy dùng **Chạy từng bước** với đúng đầu vào của kiểm thử chưa đạt và ghi lại giá trị biến ở từng dòng.")
    elif strategy == "recurring_difficulty":
        repeat_note = ("\n\n🔁 Bạn đã thử bài này vài lần. Thay vì sửa tiếp theo cảm tính, lần này hãy dùng "
                       "**Chạy từng bước** với đúng đầu vào của kiểm thử chưa đạt và ghi lại giá trị biến ở từng dòng.")

    extra = _model_notes(adaptive_strategy)
    if extra:
        repeat_note += "\n\n" + extra

    if hint_level == 1:
        if failed_tc:
            desc = failed_tc.get("description") or f"kiểm thử #{failed_tc.get('test_idx', '?')}"
            kind = {"RUNTIME_ERROR": "chương trình dừng vì lỗi khi chạy",
                    "FAIL": "kết quả in ra khác kỳ vọng"}.get(failed_tc.get("status"), "chưa đạt")
            evidence = f"🔎 **Bằng chứng:** {desc} — {kind}."
        else:
            evidence = "🔎 **Bằng chứng:** chưa có kiểm thử nào được ghi nhận là lỗi cụ thể; dữ liệu chưa đủ để khoanh vùng."
        structure = ast_analysis.get("structural_summary")
        if structure:
            evidence += f" Cấu trúc bài làm: {structure}"
        return (
            f"💡 **[MỨC 1: GỢI MỞ TƯ DUY & KHÁI NIỆM]**\n\n"
            f"{progress}\n\n{evidence}\n\n"
            f"❓ **Câu hỏi để tự kiểm:**\n" + "\n".join(f"- {q}" for q in questions) + "\n\n"
            f"{_next_step_line('chọn một câu hỏi ở trên, tự trả lời bằng một ví dụ nhỏ rồi bấm Chạy thử để đối chiếu.', adaptive_strategy)}"
            f"{repeat_note}"
        )

    if hint_level == 2:
        if not failed_tc:
            return (
                f"🔍 **[MỨC 2: CHẨN ĐOÁN CHI TIẾT]**\n\n{progress}\n\n"
                "🔎 **Bằng chứng:** kết quả chấm chưa cho biết kiểm thử cụ thể nào lỗi, nên chưa thể khoanh vùng dòng lệnh.\n\n"
                "➡️ **Bước kế tiếp:** bấm Chạy thử để xem bảng kiểm thử, rồi xin lại gợi ý Mức 2." + repeat_note
            )
        inp_val = (failed_tc.get("input") or "").strip()
        exp_val = (failed_tc.get("expected_output") or "").strip()
        act_val = (failed_tc.get("actual_output") or "").strip()
        err_msg = (failed_tc.get("error_message") or "").strip()
        if failed_tc.get("status") == "RUNTIME_ERROR":
            observed = f"chương trình dừng với lỗi `{err_msg or 'lỗi khi chạy'}`"
            next_step = ("tìm dòng mà thông báo lỗi nhắc tới, xác định biến nào ở dòng đó mang giá trị gây lỗi "
                         "với đầu vào trên.")
        else:
            observed = _observed_difference(exp_val, act_val)
            next_step = ("dùng **Chạy từng bước** với đúng đầu vào này và dừng ở dòng đầu tiên mà giá trị biến "
                         "khác với điều bạn dự tính.")
        return (
            f"🔍 **[MỨC 2: CHẨN ĐOÁN CHI TIẾT & KHOANH VÙNG LỖI]**\n\n{progress}\n\n"
            f"🔎 **Bằng chứng từ kiểm thử #{failed_tc.get('test_idx', '?')}:**\n"
            f"- **Đầu vào:** `{inp_val}`\n"
            f"- **Kỳ vọng:** `{exp_val}`\n"
            f"- **Thực tế:** `{act_val or '(không in ra gì)'}`\n"
            f"- **Quan sát:** {observed}.\n\n"
            f"❓ **Câu hỏi khoanh vùng:** {questions[0]}\n\n"
            f"{_next_step_line(next_step, adaptive_strategy)}"
            f"{repeat_note}\n\n"
            "*(Gợi ý tự động khi không có mô hình AI: chỉ nêu điều quan sát được, chưa chỉ ra được dòng lệnh cụ thể.)*"
        )

    # Level 3: dàn ý 4 bước + khung code có chỗ trống; không điền sẵn biểu thức cốt lõi.
    target = ""
    if failed_tc and failed_tc.get("status") == "FAIL":
        target = (f"\n\n🔎 **Dùng để tự kiểm:** với đầu vào `{(failed_tc.get('input') or '').strip()}` "
                  f"chương trình cần in `{(failed_tc.get('expected_output') or '').strip()}`.")
    return (
        f"📘 **[MỨC 3: DÀN Ý THUẬT TOÁN CHI TIẾT & KHUNG CODE MẪU]**\n\n"
        f"{progress}{target}\n\n"
        f"### 1. Dàn ý các bước thuật toán:\n"
        f"- **Bước 1:** Đọc dữ liệu đầu vào đúng định dạng đề nêu và ép về kiểu phù hợp.\n"
        f"- **Bước 2:** Khởi tạo biến lưu kết quả bằng giá trị ban đầu hợp lý cho phép tính của đề.\n"
        f"- **Bước 3:** Xử lý dữ liệu (rẽ nhánh hoặc lặp) và cập nhật biến kết quả.\n"
        f"- **Bước 4:** In kết quả đúng định dạng đề yêu cầu bằng `print()`.\n\n"
        f"### 2. Khung mã nguồn (tự điền các chỗ `...`):\n"
        f"```python\n"
        f"# Bước 1: đọc dữ liệu\n"
        f"du_lieu = ...          # TODO: đọc và ép kiểu đầu vào\n\n"
        f"# Bước 2: khởi tạo kết quả\n"
        f"ket_qua = ...          # TODO: giá trị ban đầu\n\n"
        f"# Bước 3: xử lý\n"
        f"...                    # TODO: rẽ nhánh / vòng lặp cập nhật ket_qua\n\n"
        f"# Bước 4: in kết quả\n"
        f"print(ket_qua)\n"
        f"```\n\n"
        f"{_level3_progress_note(code, adaptive_strategy)}"
        f"{repeat_note}"
    )


def llm_disabled() -> bool:
    """PYTUTOR_DISABLE_LLM=1 ép chế độ offline (không gọi provider ngoài) cho kiểm thử, benchmark và pilot mặc định."""
    return os.getenv("PYTUTOR_DISABLE_LLM", "").strip().lower() in ("1", "true", "yes")


async def call_qwen_api(prompt: str, timeout_seconds: float = 45.0) -> Optional[str]:
    """
    Gọi trực tiếp API Qwen2.5-14B qua HTTP POST.
    """
    if llm_disabled():
        return None
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
    if not GEMINI_API_KEY or llm_disabled():
        return None
    try:
        return await asyncio.to_thread(_sync_call_gemini, prompt)
    except Exception as e:
        logger.error(f"Lỗi bất đồng bộ khi gọi Gemini: {e}")
        return None


async def call_gemini_with_usage(prompt: str) -> tuple[Optional[tuple[str, str]], dict]:
    """Call Gemini and return provider usage counts when the SDK exposes them."""
    if not GEMINI_API_KEY or llm_disabled():
        return None, {"prompt_tokens": None, "completion_tokens": None}
    try:
        result = await asyncio.to_thread(_sync_call_gemini_with_usage, prompt)
        return result
    except Exception as exc:
        logger.warning("Gemini usage metadata unavailable: %s", exc)
        return None, {"prompt_tokens": None, "completion_tokens": None}


def _sync_call_gemini_with_usage(prompt: str) -> tuple[Optional[tuple[str, str]], dict]:
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        for model_name in GEMINI_MODELS:
            try:
                response = client.models.generate_content(model=model_name, contents=prompt)
                if response.text and response.text.strip():
                    usage = getattr(response, "usage_metadata", None)
                    return (response.text.strip(), f"Google {model_name}"), {
                        "prompt_tokens": getattr(usage, "prompt_token_count", None),
                        "completion_tokens": getattr(usage, "candidates_token_count", None),
                    }
            except Exception as exc:
                logger.warning("Gemini %s failed: %s", model_name, exc)
        return None, {"prompt_tokens": None, "completion_tokens": None}
    except Exception:
        return None, {"prompt_tokens": None, "completion_tokens": None}


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
    student_model: dict = None,
    adaptive_strategy: dict = None
) -> tuple[str, str, dict]:
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
        student_model=student_model,
        adaptive_strategy=adaptive_strategy
    )
    
    all_passed = test_results.get("all_passed", False)

    # 1. Ưu tiên hàng đầu: Gọi Google Gemini AI
    started = asyncio.get_running_loop().time()
    gemini_res, usage = await call_gemini_with_usage(prompt)
    if gemini_res:
        raw_hint, model_name = gemini_res
        sanitized_hint = sanitize_spoil_code(
            response_text=raw_hint,
            hint_level=hint_level,
            all_passed=all_passed
        )
        # Chẩn đoán được phép trích lại dòng code của chính người học (không tính là lời giải).
        safe, reason = check_student_output(sanitized_hint, quoted_context=code or "")
        if not safe and hint_level in (1, 2) and not all_passed:
            fallback = generate_rule_based_fallback(exercise, code, test_results, ast_analysis, hint_level,
                                                    adaptive_strategy=adaptive_strategy)
            return fallback, "Pedagogical-Rule-Engine (Output Guard Fallback)", {
                "latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
                "model_name": model_name, **usage, "input_guard": "allowed",
                "output_guard": reason, "status": "blocked_fallback"}
        guard_label = "allowed" if safe else "post_acceptance_review"
        if hint_level == 3 and not all_passed:
            # Mức 3 cho cấu trúc, không cho logic: che biểu thức lời giải trong khung mã.
            sanitized_hint, masked = enforce_level3_skeleton(sanitized_hint)
            guard_label = f"level3_masked:{masked}" if masked else "level3_skeleton_ok"
        return sanitized_hint, model_name, {"latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
                "model_name": model_name, **usage, "input_guard": "allowed",
                "output_guard": guard_label, "status": "success"}

    # 2. Dự phòng: Thử Qwen2.5-14B (nếu server trường mở)
    qwen_response = await call_qwen_api(prompt, timeout_seconds=15.0)
    if qwen_response and len(qwen_response) > 20:
        sanitized_hint = sanitize_spoil_code(
            response_text=qwen_response,
            hint_level=hint_level,
            all_passed=all_passed
        )
        qwen_guard = "checked"
        if hint_level == 3 and not all_passed:
            sanitized_hint, masked = enforce_level3_skeleton(sanitized_hint)
            qwen_guard = f"level3_masked:{masked}" if masked else "level3_skeleton_ok"
        return sanitized_hint, QWEN_MODEL, {"latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
                "model_name": QWEN_MODEL, "prompt_tokens": None, "completion_tokens": None,
                "input_guard": "allowed", "output_guard": qwen_guard, "status": "success"}

    # 3. Dự phòng cấp cuối: Rule-based Fallback
    fallback_hint = generate_rule_based_fallback(
        exercise=exercise,
        code=code,
        test_results=test_results,
        ast_analysis=ast_analysis,
        hint_level=hint_level,
        adaptive_strategy=adaptive_strategy
    )
    return fallback_hint, "Pedagogical-Rule-Engine (Offline Fallback)", {
        "latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
        "model_name": "Pedagogical-Rule-Engine", "prompt_tokens": None, "completion_tokens": None,
        "input_guard": "allowed", "output_guard": "fallback", "status": "fallback"}


async def generate_chat_followup(
    exercise: dict,
    code: str,
    user_message: str,
    history: list = None,
    ast_summary: str = "",
    student_model: dict = None,
    chat_scope: str = "legacy",
    class_id: str | None = None,
) -> tuple[str, str, dict]:
    """
    Sinh phản hồi cho câu hỏi làm rõ của sinh viên trong phiên chat đa lượt (Phase 8).
    Tuân thủ nghiêm ngặt nguyên tắc Socratic và Anti-Spoil Guard (Không giải hộ).

    `chat_scope` (S1.4): "concept_only" khi chưa có lượt nộp pass → prompt không chứa code bài làm;
    "code_review" khi đã nộp pass → `code` là code đã nộp; "legacy" giữ hành vi cũ.
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

    rag_docs = retrieve_knowledge(user_message, top_k=3, class_id=class_id)
    rag_context = "\n\n".join(
        f"Nguồn: {doc['source']} — mục \"{doc.get('section') or 'Tổng quan'}\"\n{doc['content']}" for doc in rag_docs
    ) or ("Không tìm thấy tài liệu nội bộ liên quan. Chỉ giải thích ở mức khái niệm chung, "
          "KHÔNG trích dẫn hay nêu tên bất kỳ tài liệu/giáo trình nào.")
    # Nguồn hiển thị cho người học: chỉ tên tệp + mục, không kèm nội dung.
    source_refs = _source_refs(rag_docs)
    metrics = (student_model or {}).get("analytics_metrics") or {}
    prompt = render_socratic_prompt(
        exercise={"title": title, "description": desc}, code=code,
        user_message=user_message, history=history_text, rag_context=rag_context,
        hint_level=1,
        autonomy_score=float(metrics.get("autonomy_score", 0) or 0),
        first_try_pass_rate=float(metrics.get("first_try_pass_rate", 0) or 0),
        chat_scope=chat_scope,
    )
    if ast_summary and chat_scope != "concept_only":
        prompt += f"\n<ast_summary>{ast_summary}</ast_summary>\n"

    started = asyncio.get_running_loop().time()
    # Gọi Gemini
    gemini_res, usage = await call_gemini_with_usage(prompt)
    if gemini_res:
        raw_reply, model_name = gemini_res
        quoted_ctx = code if chat_scope == "code_review" else ""
        safe, reason = check_student_output(raw_reply, quoted_context=quoted_ctx)
        sanitized = sanitize_spoil_code(raw_reply, hint_level=1, all_passed=(chat_scope == "code_review"))
        if safe:
            safe, reason = check_student_output(sanitized, quoted_context=quoted_ctx)
        telemetry = {
            "latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
            "model_name": model_name, **usage,
            "input_guard": "allowed", "output_guard": "allowed" if safe else reason,
            "status": "success" if safe else "blocked",
            "rag_sources": [doc["source"] for doc in rag_docs],
            # Phản hồi bị chặn không dùng nội dung nguồn nên không gắn nguồn cho người học.
            "source_refs": source_refs if safe else [],
        }
        if safe and source_refs and reply_says_no_source(sanitized):
            # Mô hình tự nhận mục truy xuất không liên quan: không hiển thị nguồn trái với lời của chính câu trả lời.
            telemetry["source_refs"] = []
            telemetry["knowledge_status"] = "no_source"
        if safe:
            return sanitized, model_name, telemetry
        return ("Mình chưa thể gửi phản hồi đó vì có thể chứa quá nhiều nội dung giải sẵn. "
                "Bạn hãy hỏi về một khái niệm hoặc bước cụ thể để mình gợi mở nhé!"), model_name, telemetry

    # Dự phòng offline. Thứ tự: (1) câu hỏi về luật nút/sao → trả đúng luật hệ thống; (2) chưa nộp pass mà nhờ gỡ
    # code bài đang làm → chuyển hướng sang "Hỏi Gia sư AI"; (3) trích đoạn tài liệu nội bộ (có nguồn) hoặc nói rõ
    # giới hạn, không bịa nguồn.
    system_reply = build_system_rule_reply(user_message, chat_scope)
    if system_reply:
        return system_reply, "Rule-Based Assistant", {
            "latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
            "model_name": "Rule-Based Assistant", "prompt_tokens": None, "completion_tokens": None,
            "input_guard": "allowed", "output_guard": "fallback", "status": "fallback",
            "rag_sources": [], "source_refs": [], "knowledge_status": "not_applicable",
        }
    reply, used_refs = build_offline_chat_reply(rag_docs)
    if chat_scope == "code_review":
        # S8a offline: nói về bài ĐÃ NỘP bằng tóm tắt cấu trúc (AST), kèm trích đoạn tài liệu nếu có.
        reply = build_offline_code_review_reply(title, ast_summary, reply if used_refs else "")
        return reply, "Rule-Based Assistant", {
            "latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
            "model_name": "Rule-Based Assistant", "prompt_tokens": None, "completion_tokens": None,
            "input_guard": "allowed", "output_guard": "fallback", "status": "fallback",
            "rag_sources": [ref["source"] for ref in used_refs], "source_refs": used_refs,
            "knowledge_status": "grounded" if used_refs else "not_applicable",
        }
    return reply, "Rule-Based Assistant", {
        "latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
        "model_name": "Rule-Based Assistant", "prompt_tokens": None, "completion_tokens": None,
        "input_guard": "allowed", "output_guard": "fallback", "status": "fallback",
        "rag_sources": [ref["source"] for ref in used_refs],
        "source_refs": used_refs,
    }


_STAR_RULE_QUESTION = re.compile(
    r"sao tự lực|[123]\s*(?:⭐|sao)\b|mấy sao|bao nhiêu sao|số sao|tăng sao|cày sao|luật (?:tính )?sao|cách tính sao|⭐|(?:ba|3) nút",
    flags=re.IGNORECASE)
_DEBUG_MY_CODE_REQUEST = re.compile(
    r"(?:sửa|fix|gỡ|chữa|xem|kiểm tra|soát)\s+(?:giúp |hộ |giùm |lại |cho |em |mình |tôi |tớ )*(?:lỗi |bug )?(?:trong |ở |của )?"
    r"(?:code|bài làm|bài của|bài này|chương trình|đoạn mã)"
    r"|(?:code|bài làm|bài|chương trình)\s+(?:của\s+)?(?:em|mình|tôi|tớ)\b.*(?:sai|lỗi|không chạy|fail)"
    r"|(?:sai|lỗi)\s+(?:ở|chỗ|dòng)\s+(?:đâu|nào)|dòng nào\s+(?:bị\s+)?(?:sai|lỗi)"
    r"|tại sao\s+(?:code|bài)\b.*(?:sai|lỗi|không chạy|fail|không pass)|\bdebug\b",
    flags=re.IGNORECASE)


def build_system_rule_reply(user_message: str, chat_scope: str = "legacy") -> Optional[str]:
    """Câu trả lời tất định cho hai tình huống không cần LLM (S1.4); None nếu không thuộc hai tình huống này."""
    text = user_message or ""
    if _STAR_RULE_QUESTION.search(text):
        return ("Luật của PyTutor về ba nút và Sao tự lực:\n\n" + SYSTEM_RULES_TEXT +
                "\n\n❓ Với bài đang làm, bạn muốn thử tự giải tới đâu trước khi cần gợi ý?")
    if chat_scope == "concept_only" and _DEBUG_MY_CODE_REQUEST.search(text):
        return ("Ở khung trò chuyện này mình chỉ giải thích **khái niệm Python tổng quát** khi bạn chưa nộp bài đạt, "
                "nên mình không xem hay chẩn đoán code bài bạn đang làm tại đây. Để được gợi ý dựa trên kết quả chấm thật, "
                "hãy bấm nút **🤖 Hỏi Gia sư AI** và chọn mức gợi ý 1–3 (Mức 2 sẽ khoanh vùng lỗi). "
                "Sau khi **🚀 Nộp bài** đạt 100% kiểm thử, bạn có thể quay lại đây hỏi chi tiết về code đã nộp.\n\n"
                "❓ Trong lúc đó, bạn muốn mình giải thích khái niệm nào (ví dụ: vòng lặp, `range`, ép kiểu)?")
    return None


_SAYS_NO_SOURCE = re.compile(r"không\s+tìm\s+thấy\s+tài\s+liệu\s+(nội\s+bộ|nào)", flags=re.IGNORECASE)


def reply_says_no_source(reply: str) -> bool:
    """Câu trả lời tự nói không có tài liệu phù hợp (đúng cụm prompt yêu cầu mô hình dùng).

    Dùng để giao diện không hiện "Tài liệu nội bộ liên quan" ngược với lời của chính câu trả lời.
    Chỉ nhìn phần đầu câu trả lời; nếu mô hình diễn đạt khác cụm này thì không phát hiện được.
    """
    return bool(_SAYS_NO_SOURCE.search((reply or "")[:400]))


def _source_refs(rag_docs: list[dict]) -> list[dict]:
    refs: list[dict] = []
    for doc in rag_docs:
        ref = {"source": doc["source"], "section": doc.get("section") or "Tổng quan"}
        if doc.get("scope", "global") != "global":
            ref["origin"] = "class"  # tài liệu do giảng viên lớp cung cấp
        if ref not in refs:
            refs.append(ref)
    return refs


def build_offline_chat_reply(rag_docs: list[dict]) -> tuple[str, list[dict]]:
    """Câu trả lời chat tất định khi không có LLM. Trả về (nội dung, nguồn thực sự được dùng)."""
    no_source_reply = (
        "Hiện mô hình AI chưa sẵn sàng và mình không tìm thấy đoạn tài liệu nội bộ nào khớp với câu hỏi này, "
        "nên mình không trích nguồn nào cả. Bạn có thể hỏi lại bằng tên khái niệm Python cụ thể "
        "(ví dụ: vòng lặp, `range`, ép kiểu, lỗi `TypeError`), hoặc bấm Chạy thử và xin gợi ý theo mức ở phía trên."
    )
    if not rag_docs:
        return no_source_reply, []
    top = rag_docs[0]
    # Bỏ khối code khỏi trích đoạn để không vượt giới hạn Anti-Spoil.
    excerpt = re.sub(r"```.*?```", "", top["content"], flags=re.DOTALL).strip()
    if len(excerpt) > 520:
        excerpt = excerpt[:520].rsplit(" ", 1)[0] + "…"
    origin = (f"tài liệu **{top['source']}** do giảng viên lớp cung cấp" if top.get("scope", "global") != "global"
              else "tài liệu nội bộ của PyTutor")
    reply = (
        f"Theo {origin}, mục **{top.get('section') or 'Tổng quan'}**:\n\n{excerpt}\n\n"
        "❓ Từ đoạn trên, điều nào áp dụng được vào bài bạn đang làm? Hãy thử nói lại bằng lời của mình rồi chạy thử để kiểm chứng."
    )
    safe, _ = check_student_output(reply)
    if not safe or not excerpt:
        return no_source_reply, []
    return reply, _source_refs([top])


def build_offline_code_review_reply(title: str, ast_summary: str, knowledge_reply: str = "") -> str:
    """Câu trả lời chat tất định sau khi đã nộp đạt (S8a) khi không có LLM.

    Chỉ nêu điều quan sát được từ phân tích cấu trúc (AST) của code đã nộp; không chép lại mã nguồn,
    không diễn giải từng dòng (việc đó cần mô hình AI).
    """
    if ast_summary:
        observed = f"Cấu trúc quan sát được từ **code bạn đã nộp** (phân tích tự động, không chép lại mã): {ast_summary}"
    else:
        observed = "Hiện mình chưa phân tích được cấu trúc của code bạn đã nộp."
    reply = (
        f"Ở **{title}**, bạn đã có lượt nộp đạt 100% kiểm thử, nên ở đây mình nói về chính code đã nộp đó. "
        "Mô hình AI hiện chưa sẵn sàng, vì vậy mình chưa giải thích được từng dòng mà chỉ tóm tắt cấu trúc.\n\n"
        f"{observed}\n\n"
        "❓ Tự kiểm: bạn hãy thử nói bằng lời của mình vì sao cấu trúc này cho kết quả đúng với mọi bộ kiểm thử, "
        "và trường hợp biên nào (đầu vào nhỏ nhất, rỗng, bằng 0) dễ làm nó sai nhất?"
    )
    if knowledge_reply:
        reply += f"\n\n---\n{knowledge_reply}"
    safe, _ = check_student_output(reply)
    if not safe:
        return ("Bài của bạn đã có lượt nộp đạt 100% kiểm thử. Mô hình AI hiện chưa sẵn sàng nên mình chưa giải thích "
                "chi tiết được code đã nộp; bạn có thể mở Pythonic Review hoặc hỏi lại sau.")
    return reply


def build_class_summary_answer(summary: dict) -> str:
    """Trả lời tất định cho giảng viên từ số liệu tổng hợp của lớp (dùng khi không có LLM).

    Luôn nêu khoảng thời gian, cỡ mẫu và giới hạn diễn giải; không chứa danh tính sinh viên.
    """
    metrics = (summary or {}).get("metrics") or {}
    cls = (summary or {}).get("class") or {}
    days = (summary or {}).get("days", 7)
    header = f"**Lớp {cls.get('class_code', '')} — {days} ngày gần nhất** (chỉ tính lượt *Nộp bài* chính thức)."
    if metrics.get("data_status", "no_data") == "no_data":
        return (f"{header}\n\nChưa có lượt nộp bài chính thức nào trong khoảng thời gian này, "
                "nên chưa thể nhận xét về tiến độ hay điểm nghẽn. Hãy thử mở rộng khoảng thời gian hoặc chờ sinh viên nộp bài.")
    lines = [
        header,
        f"- **Cỡ mẫu:** {metrics.get('submissions', 0)} lượt nộp từ {metrics.get('active_students', 0)}"
        f"/{metrics.get('enrolled_students', 0)} sinh viên ghi danh, trên {metrics.get('exercises_attempted', 0)} bài.",
    ]
    groups = (summary or {}).get("process_groups") or {}
    overall = groups.get("overall") or {}
    if groups.get("pairs"):
        labels = {d["key"]: d["label"] for d in groups.get("definitions", [])}
        counts = " · ".join(f"{labels.get(k, k)} {v}" for k, v in overall.items() if v)
        lines.append(f"- **Quá trình học (số cặp sinh viên–bài):** {counts}.")
    else:
        lines.append(f"- **Tỷ lệ lượt nộp đạt:** {metrics.get('pass_rate', 0)}%.")
    mix = (summary or {}).get("error_mix") or {}
    if mix:
        lines.append(f"- **Cơ cấu kết quả:** đạt {mix.get('passed_percent', 0)}% · sai một phần kiểm thử "
                     f"{mix.get('partial_percent', 0)}% · không đạt kiểm thử nào (cú pháp/runtime) {mix.get('zero_pass_percent', 0)}%.")
    bottlenecks = [b for b in (summary or {}).get("bottlenecks") or [] if b.get("unsuccessful", 0) > 0][:3]
    if bottlenecks:
        lines.append("- **Bài có nhiều lượt chưa đạt nhất:**")
        for item in bottlenecks:
            lines.append(f"  - {item.get('title', item.get('exercise_id', ''))}: {item.get('unsuccessful', 0)}/{item.get('submissions', 0)} "
                         f"lượt chưa đạt, {item.get('students_passed', 0)}/{item.get('students_attempted', 0)} sinh viên đã qua.")
    else:
        lines.append("- Chưa ghi nhận bài nào có lượt nộp chưa đạt trong khoảng này.")
    if metrics.get("data_status") == "limited":
        lines.append("\n⚠️ **Giới hạn:** dưới 3 sinh viên có hoạt động trong khoảng này; số liệu chỉ mang tính mô tả, "
                     "chưa nên dùng để kết luận về cả lớp.")
    else:
        lines.append("\nℹ️ **Giới hạn:** đây là thống kê mô tả từ lượt nộp; không cho biết nguyên nhân và không thay thế quan sát trên lớp.")
    lines.append("*(Trả lời tự động từ số liệu tổng hợp; mô hình AI hiện không khả dụng.)*")
    return "\n".join(lines)


_PROCESS_AS_STUDENTS = re.compile(
    r"\d+\s+sinh viên\s+(?:đạt độc lập|đạt sau thử|đạt nhờ gợi ý|đang tiến triển|đang trong quá trình tiến triển|chỉ chạy thử)",
    flags=re.IGNORECASE)
PROCESS_UNIT_NOTE = ("\n\n*Lưu ý về đơn vị (PyTutor bổ sung): các nhóm quá trình học được đếm theo cặp sinh viên–bài; "
                     "một sinh viên làm nhiều bài được đếm nhiều lần, nên các con số nhóm ở trên không phải số sinh viên.*")


def add_process_unit_note(reply: str, summary: dict) -> str:
    """Nếu câu trả lời của mô hình gọi số đếm nhóm quá trình là "N sinh viên ...", gắn ghi chú đơn vị tất định.

    Nhóm quá trình đếm theo cặp sinh viên–bài (xem docs/PROCESS_GROUPS.md); gọi nhầm thành số sinh viên
    làm giảng viên đọc sai quy mô. Không sửa câu chữ của mô hình, chỉ thêm ghi chú.
    """
    groups = (summary or {}).get("process_groups") or {}
    if groups.get("pairs") and _PROCESS_AS_STUDENTS.search(reply) and PROCESS_UNIT_NOTE.strip() not in reply:
        return reply.rstrip() + PROCESS_UNIT_NOTE
    return reply


async def generate_instructor_answer(summary: dict, user_message: str) -> tuple[str, str, dict]:
    prompt = render_instructor_prompt(summary=summary, user_message=user_message)
    started = asyncio.get_running_loop().time()
    result, usage = await call_gemini_with_usage(prompt)
    if result:
        reply, source = result
        safe, reason = check_student_output(reply)
        if safe and 0 < len(reply) <= 5000:
            reply = add_process_unit_note(reply, summary)
            return reply, source, {"latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
                                  "model_name": source, **usage,
                                  "input_guard": "allowed", "output_guard": "allowed", "status": "success"}
        logger.warning("Instructor output blocked by output guard: %s", reason)
    # Không có LLM hoặc đầu ra bị chặn: trả lời tất định từ chính số liệu tổng hợp đã được phân quyền.
    return (build_class_summary_answer(summary),
            "Rule-Based Assistant",
            {"latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
             "model_name": "Rule-Based Assistant", "prompt_tokens": None, "completion_tokens": None,
             "input_guard": "allowed", "output_guard": "fallback", "status": "fallback"})


async def generate_pythonic_review(
    exercise: dict,
    student_code: str
) -> tuple[dict, str, dict]:
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

    prompt = render_reviewer_prompt(exercise={"title": title, "description": desc}, code=student_code)

    started = asyncio.get_running_loop().time()
    gemini_res, usage = await call_gemini_with_usage(prompt)
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
            def as_review_text(value, fallback: str) -> str:
                if isinstance(value, list):
                    return "\n".join(str(item) for item in value)
                return str(value) if value is not None else fallback
            return {
                "clean_score": int(data.get("clean_score", 85)),
                "strengths": as_review_text(data.get("strengths"), "Bạn đã áp dụng tư duy thuật toán chính xác và giải quyết trọn vẹn bài toán."),
                "improvements": as_review_text(data.get("improvements"), "Có thể tận dụng các hàm built-in để mã nguồn ngắn gọn hơn."),
                "pythonic_code": data.get("pythonic_code", student_code),
                "explanation": data.get("explanation", "Phiên bản Pythonic tận dụng tối đa các hàm cốt lõi tối ưu của Python.")
            }, model_name, {"latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
                           "model_name": model_name, **usage, "input_guard": "allowed",
                           "output_guard": "review_checked", "status": "success"}
        except Exception as e:
            logger.warning(f"Lỗi phân tích JSON từ phản hồi review của Gemini: {e}")

    # Fallback chất lượng cao nếu offline
    code_lines = len(student_code.strip().splitlines())
    return {
        "clean_score": 85 if code_lines > 3 else 92,
        "strengths": "Cấu trúc chương trình rõ ràng, biến được khởi tạo và cập nhật logic chuẩn xác.",
        "improvements": "Trong Python hiện đại, bạn có thể tận dụng các hàm tích hợp sẵn (built-in) như sum() hoặc slicing để mã nguồn tinh gọn hơn.",
        "pythonic_code": student_code.strip(),
        "explanation": "Nhận xét tự động khi mô hình AI không khả dụng: điểm và nhận xét chỉ dựa trên độ dài mã, mang tính tham khảo và chưa phân tích cụ thể lời giải của bạn."
    }, "Pedagogical-Rule-Reviewer", {"latency_ms": (asyncio.get_running_loop().time() - started) * 1000,
        "model_name": "Pedagogical-Rule-Reviewer", "prompt_tokens": None, "completion_tokens": None,
        "input_guard": "allowed", "output_guard": "fallback", "status": "fallback"}



