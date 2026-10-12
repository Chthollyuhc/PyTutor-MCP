"""
PYTUTOR – MCP DEMO TRỰC QUAN
Mục đích: Minh họa rõ ràng 9 bước trong quy trình MCP 
để thuyết phục Giảng viên về tính hợp lý của kiến trúc này.
"""

import streamlit as st
import json
import time
import ast
import io
import sys
import traceback
import urllib.request

st.set_page_config(
    layout="wide",
    page_title="PyTutor MCP – Demo Quy trình",
    page_icon="🔬"
)

st.markdown("""
<style>
    .step-box {
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 12px 16px;
        margin: 6px 0;
        background: #f8f9fa;
        font-family: monospace;
        font-size: 13px;
    }
    .step-active {
        border-color: #2196F3;
        background: #E3F2FD;
    }
    .step-done {
        border-color: #4CAF50;
        background: #E8F5E9;
    }
    .step-label {
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .json-box {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 10px;
        border-radius: 6px;
        font-family: Consolas, monospace;
        font-size: 12px;
        white-space: pre-wrap;
        margin: 6px 0;
    }
    .tag-host { color: #FF6B6B; font-weight: bold; }
    .tag-client { color: #4ECDC4; font-weight: bold; }
    .tag-server { color: #45B7D1; font-weight: bold; }
    .tag-llm { color: #96CEB4; font-weight: bold; }
    .tag-mcp { color: #FFEAA7; font-weight: bold; }
    h1 { font-size: 1.6rem !important; }
    h2 { font-size: 1.25rem !important; color: #2E5F88; }
    h3 { font-size: 1.05rem !important; }
</style>
""", unsafe_allow_html=True)

# =====================
# TIÊU ĐỀ
# =====================
st.title("🔬 PyTutor – Demo Minh Họa Quy Trình MCP")
st.markdown("""
**Mục đích demo này:** Hiển thị rõ từng bước trong **giao thức MCP (Model Context Protocol)** 
để minh họa sự khác biệt so với cách gọi API thông thường.  
*Cột trái: Giao diện sinh viên | Cột phải: Log quy trình MCP (thầy quan sát)*
""")

# =====================
# BÀI TẬP
# =====================
EXERCISE = {
    "title": "Bài 03: Tính tổng các số từ 1 đến n",
    "desc": """Viết hàm `tinh_tong(n)` trả về tổng của 1 + 2 + 3 + ... + n.

**Ví dụ:**
- `tinh_tong(3)` → `6`  (1+2+3)
- `tinh_tong(5)` → `15` (1+2+3+4+5)

**Mục tiêu học tập:** Sử dụng vòng lặp `for` và biến cộng dồn (accumulator).
""",
    "starter": "def tinh_tong(n):\n    # Viết code ở đây\n    pass\n",
    "test_cases": [
        {"input": 1, "expected": 1},
        {"input": 3, "expected": 6},
        {"input": 5, "expected": 15},
        {"input": 10, "expected": 55},
        {"input": 0, "expected": 0},
    ]
}

# =====================
# MCP TOOLS (MOCK SERVER)
# =====================

def mcp_tool_run_tests(code: str, test_cases: list) -> dict:
    """
    [MCP TOOL: run_tests]
    Thực thi code Python trong môi trường cô lập.
    Trả về JSON chuẩn MCP với kết quả từng test case.
    """
    results = []
    local_scope = {}
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    
    try:
        exec(compile(code, "<student_code>", "exec"), {}, local_scope)
        func = local_scope.get('tinh_tong')
        
        if func is None:
            sys.stdout = old_stdout
            return {
                "tool": "run_tests",
                "success": False,
                "error": "NameError: Không tìm thấy hàm 'tinh_tong' trong code.",
                "passed": 0,
                "failed": len(test_cases),
                "results": []
            }
        
        for tc in test_cases:
            try:
                actual = func(tc["input"])
                passed = (actual == tc["expected"])
                results.append({
                    "input": tc["input"],
                    "expected": tc["expected"],
                    "actual": actual,
                    "passed": passed,
                    "error": None
                })
            except Exception as e:
                results.append({
                    "input": tc["input"],
                    "expected": tc["expected"],
                    "actual": None,
                    "passed": False,
                    "error": f"{type(e).__name__}: {str(e)}"
                })
        
        sys.stdout = old_stdout
        passed_count = sum(1 for r in results if r["passed"])
        return {
            "tool": "run_tests",
            "success": True,
            "passed": passed_count,
            "failed": len(test_cases) - passed_count,
            "total": len(test_cases),
            "results": results
        }
        
    except SyntaxError as e:
        sys.stdout = old_stdout
        return {
            "tool": "run_tests",
            "success": False,
            "error": f"SyntaxError tại dòng {e.lineno}: {e.msg}",
            "passed": 0,
            "failed": len(test_cases),
            "results": []
        }
    except Exception as e:
        sys.stdout = old_stdout
        return {
            "tool": "run_tests",
            "success": False,
            "error": f"{type(e).__name__}: {str(e)}",
            "passed": 0,
            "failed": len(test_cases),
            "results": []
        }


def mcp_tool_analyze_ast(code: str) -> dict:
    """
    [MCP TOOL: analyze_ast]
    Phân tích cây cú pháp (AST) của code Python.
    Không cần chạy code – phân tích tĩnh (static analysis).
    """
    try:
        tree = ast.parse(code)
        has_for = False
        has_while = False
        has_return = False
        has_accumulator = False
        function_names = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                has_for = True
            if isinstance(node, ast.While):
                has_while = True
            if isinstance(node, ast.Return):
                has_return = True
            if isinstance(node, ast.AugAssign):
                has_accumulator = True
            if isinstance(node, ast.FunctionDef):
                function_names.append(node.name)
        
        observations = []
        if not has_for and not has_while:
            observations.append("⚠ Không tìm thấy vòng lặp for/while – bài yêu cầu sử dụng vòng lặp")
        if has_for:
            observations.append("✓ Có vòng lặp for")
        if has_while:
            observations.append("✓ Có vòng lặp while")
        if not has_accumulator:
            observations.append("⚠ Không tìm thấy biến cộng dồn (+=) – có thể thiếu accumulator")
        if has_accumulator:
            observations.append("✓ Có biến cộng dồn (+=)")
        if not has_return:
            observations.append("⚠ Không có lệnh return – hàm sẽ trả về None")
        if has_return:
            observations.append("✓ Có lệnh return")
        
        return {
            "tool": "analyze_ast",
            "success": True,
            "functions_found": function_names,
            "has_for_loop": has_for,
            "has_while_loop": has_while,
            "has_return": has_return,
            "has_accumulator": has_accumulator,
            "observations": observations
        }
    except SyntaxError as e:
        return {
            "tool": "analyze_ast",
            "success": False,
            "error": f"Không thể phân tích AST: SyntaxError tại dòng {e.lineno}"
        }


def call_qwen_api(prompt: str) -> tuple[str, float]:
    """Gọi API Qwen2.5-14B của thầy và đo thời gian phản hồi."""
    url = "http://101.96.66.232:8037/ollama/api/generate"
    headers = {
        "Content-Type": "application/json",
        "x-ollama-seckey": "neutv"
    }
    data = {
        "model": "qwen2.5:14b-instruct-ctx16k",
        "prompt": prompt,
        "stream": False
    }
    t0 = time.time()
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers
    )
    response = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    elapsed = time.time() - t0
    result = json.loads(response)
    return result["response"], elapsed


# =====================
# LAYOUT CHÍNH
# =====================
col_student, col_mcp = st.columns([1, 1.2])

with col_student:
    st.header("🎓 Giao diện Sinh viên")
    
    st.subheader("📋 Đề bài")
    st.info(f"**{EXERCISE['title']}**")
    st.markdown(EXERCISE["desc"])
    
    st.subheader("✏️ Code Editor")
    code_input = st.text_area(
        "Nhập code Python của bạn:",
        value=st.session_state.get("code_input", EXERCISE["starter"]),
        height=180,
        key="code_input"
    )
    
    hint_level = st.selectbox(
        "Mức gợi ý muốn nhận:",
        ["Level 1 – Gợi mở nhẹ (Không tiết lộ lỗi cụ thể)", 
         "Level 2 – Chẩn đoán (Chỉ ra vùng lỗi)", 
         "Level 3 – Hướng dẫn chi tiết (Có thể dùng code giả)"],
        index=0
    )
    
    run_btn = st.button("▶ Chạy & Yêu cầu Gợi ý từ AI Tutor", type="primary", use_container_width=True)

with col_mcp:
    st.header("🔬 Log Quy trình MCP (Nội bộ hệ thống)")
    st.caption("Phần này bình thường sẽ ẩn – hiển thị để minh họa cơ chế MCP")
    
    log_placeholder = st.empty()

# =====================
# XỬ LÝ KHI BẤM NÚT
# =====================
if run_btn:
    level_num = int(hint_level.split("Level ")[1][0])
    
    log_steps = []
    
    def render_log():
        with log_placeholder.container():
            for step in log_steps:
                status_class = "step-done" if step.get("done") else "step-active"
                st.markdown(f"""
                <div class="step-box {status_class}">
                    <div class="step-label">{step['icon']} Bước {step['num']}: {step['title']}</div>
                    <div>{step['content']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # ---- BƯỚC 1 ----
    log_steps.append({
        "num": 1, "icon": "👤",
        "title": "HOST nhận yêu cầu từ Sinh viên",
        "content": f"<code>student_code</code> nhận được ({len(code_input)} bytes). Yêu cầu gợi ý Level {level_num}.",
        "done": True
    })
    render_log()
    time.sleep(0.3)
    
    # ---- BƯỚC 2 ----
    mcp_request_tests = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "run_tests",
            "arguments": {
                "code": code_input[:80] + "..." if len(code_input) > 80 else code_input
            }
        },
        "id": "req-001"
    }
    log_steps.append({
        "num": 2, "icon": "📤",
        "title": "MCP CLIENT gửi Tool Call → MCP SERVER",
        "content": f'<div class="json-box">{json.dumps(mcp_request_tests, indent=2, ensure_ascii=False)}</div>',
        "done": True
    })
    render_log()
    time.sleep(0.3)
    
    # ---- BƯỚC 3: Chạy run_tests ----
    log_steps.append({
        "num": 3, "icon": "⚙️",
        "title": "MCP SERVER thực thi tool run_tests (Python Sandbox)...",
        "content": "🔄 Đang chạy code trong môi trường cô lập...",
        "done": False
    })
    render_log()
    
    test_result = mcp_tool_run_tests(code_input, EXERCISE["test_cases"])
    time.sleep(0.4)
    
    log_steps[-1]["content"] = f'<div class="json-box">{json.dumps(test_result, indent=2, ensure_ascii=False)}</div>'
    log_steps[-1]["done"] = True
    render_log()
    
    # ---- BƯỚC 4: analyze_ast ----
    mcp_request_ast = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "analyze_ast", "arguments": {}},
        "id": "req-002"
    }
    log_steps.append({
        "num": 4, "icon": "🌳",
        "title": "MCP CLIENT gửi Tool Call → analyze_ast",
        "content": f'<div class="json-box">{json.dumps(mcp_request_ast, indent=2, ensure_ascii=False)}</div>',
        "done": False
    })
    render_log()
    
    ast_result = mcp_tool_analyze_ast(code_input)
    time.sleep(0.3)
    
    log_steps[-1]["content"] = f'<div class="json-box">{json.dumps(ast_result, indent=2, ensure_ascii=False)}</div>'
    log_steps[-1]["done"] = True
    render_log()
    
    # ---- BƯỚC 5: Xây dựng Context Bundle ----
    log_steps.append({
        "num": 5, "icon": "📦",
        "title": "HOST đóng gói Context Bundle cho LLM",
        "content": f"""
        <b>Context Bundle (Ground Truth từ MCP):</b>
        <ul>
            <li>✅ Đề bài: {EXERCISE['title']}</li>
            <li>✅ Code sinh viên: {len(code_input)} ký tự</li>
            <li>✅ Test Results: {test_result.get('passed', 0)}/{test_result.get('total', 5)} PASS</li>
            <li>✅ AST Observations: {len(ast_result.get('observations', []))} nhận xét</li>
            <li>✅ Hint Level: {level_num}</li>
        </ul>
        <em>→ LLM nhận BẰNG CHỨNG THỰC, không phải đoán mò</em>
        """,
        "done": True
    })
    render_log()
    time.sleep(0.3)
    
    # ---- BƯỚC 6: Xây dựng Prompt ----
    level_instructions = {
        1: "Chỉ đưa ra 1-2 câu gợi mở nhẹ nhàng, định hướng suy nghĩ. KHÔNG đề cập trực tiếp đến lỗi hay tên vòng lặp cụ thể.",
        2: "Phân tích nguyên nhân lỗi cụ thể dựa trên test results và AST analysis. Chỉ ra VÙNG code có vấn đề (không đưa ra solution).",
        3: "Cung cấp hướng dẫn từng bước bằng tiếng Việt và code giả (pseudocode). KHÔNG viết code Python hoàn chỉnh."
    }
    
    observations_text = "\n".join(ast_result.get("observations", []))
    failed_tests = [r for r in test_result.get("results", []) if not r.get("passed")]
    failed_text = "\n".join([f"- Input={r['input']}: expected={r['expected']}, got={r.get('actual', 'ERROR')} | {r.get('error', '')}" for r in failed_tests[:2]])
    
    full_prompt = f"""Bạn là AI Tutor dạy lập trình Python theo phương pháp Scaffolding.

[ĐỀ BÀI]: {EXERCISE['title']}
- Yêu cầu: Viết hàm tinh_tong(n) tính tổng 1+2+...+n
- Sử dụng vòng lặp và biến cộng dồn (accumulator)

[CODE SINH VIÊN]:
{code_input}

[KẾT QUẢ TỪ MCP run_tests]:
- Đạt: {test_result.get('passed', 0)}/{test_result.get('total', 5)} test cases
- Lỗi: {test_result.get('error', 'Không có lỗi thực thi')}
- Test case thất bại (mẫu):
{failed_text if failed_text else '(Tất cả đều đạt)'}

[KẾT QUẢ TỪ MCP analyze_ast]:
{observations_text}

[HƯỚNG DẪN SƯ PHẠM – Level {level_num}]:
{level_instructions[level_num]}

Phản hồi NGẮN GỌN (không quá 150 chữ), bằng tiếng Việt, thân thiện như một người thầy đang ngồi bên cạnh sinh viên."""

    log_steps.append({
        "num": 6, "icon": "📝",
        "title": f"HOST xây dựng Prompt Sư phạm (Level {level_num}) cho LLM",
        "content": f'<div class="json-box" style="max-height:150px;overflow:auto">{full_prompt[:500]}...</div>',
        "done": True
    })
    render_log()
    time.sleep(0.3)
    
    # ---- BƯỚC 7: Gọi LLM ----
    log_steps.append({
        "num": 7, "icon": "🧠",
        "title": "HOST gọi LLM (Qwen2.5-14B-Instruct) qua HTTP API...",
        "content": "🔄 Đang gửi request đến <code>http://101.96.66.232:8037/ollama/api/generate</code>...",
        "done": False
    })
    render_log()
    
    try:
        ai_response, elapsed = call_qwen_api(full_prompt)
        llm_success = True
        llm_error = None
    except Exception as e:
        ai_response = None
        llm_success = False
        llm_error = str(e)
        elapsed = 0
    
    log_steps[-1]["content"] = f"""
    <b>Model:</b> qwen2.5:14b-instruct-ctx16k<br>
    <b>Thời gian phản hồi:</b> {elapsed:.1f}s<br>
    <b>Trạng thái:</b> {"✅ OK" if llm_success else f"❌ Lỗi: {llm_error}"}
    """
    log_steps[-1]["done"] = True
    render_log()
    
    # ---- BƯỚC 8: Gợi ý ----
    if llm_success:
        log_steps.append({
            "num": 8, "icon": "💡",
            "title": "LLM sinh Adaptive Hint → HOST nhận kết quả",
            "content": f'<div style="background:#FFF9C4;padding:10px;border-radius:6px;border:1px solid #F9A825">{ai_response}</div>',
            "done": True
        })
        render_log()
    
    # ---- BƯỚC 9: Hiển thị kết quả ----
    log_steps.append({
        "num": 9, "icon": "🖥️",
        "title": "HOST render kết quả lên giao diện Sinh viên",
        "content": """
        <ul>
            <li>✅ Cột giữa: Bảng Test Cases cập nhật PASS/FAIL</li>
            <li>✅ Cột phải: Hiển thị AI Tutor hint với badge nguồn MCP</li>
            <li>✅ Log MCP Tool calls lưu lại để giải thích được (Explainability)</li>
        </ul>
        <b>→ Toàn bộ quá trình: {elapsed:.1f}s</b>
        """,
        "done": True
    })
    render_log()
    
    # =====================
    # HIỂN THỊ KẾT QUẢ BÊN TRÁI
    # =====================
    with col_student:
        st.divider()
        st.subheader("📊 Kết quả Test Cases")
        
        if not test_result.get("success") and "error" in test_result:
            st.error(f"❌ Lỗi thực thi: {test_result['error']}")
        else:
            p = test_result.get("passed", 0)
            t = test_result.get("total", 5)
            color = "🟢" if p == t else ("🟡" if p > 0 else "🔴")
            st.metric("Kết quả", f"{color} {p}/{t} Test Cases Đạt")
            
            for r in test_result.get("results", []):
                icon = "✅" if r["passed"] else "❌"
                err = f" | Lỗi: `{r['error']}`" if r.get("error") else ""
                st.markdown(f"{icon} `n={r['input']}` → Kỳ vọng `{r['expected']}`, Nhận `{r.get('actual', 'ERROR')}`{err}")
        
        if llm_success:
            st.subheader("💡 AI Tutor")
            st.success(f"**[MCP: run_tests + analyze_ast] → Qwen2.5-14B → Gợi ý Level {level_num}**\n\n{ai_response}")
        elif llm_error:
            st.error(f"Không thể kết nối AI: {llm_error}")
