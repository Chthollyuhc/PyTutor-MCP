"""
PyTutor MCP Visual Demo — Phiên bản dùng đúng MCP SDK
Hiển thị giao thức MCP hoạt động thực sự, real-time trong Streamlit
"""
import streamlit as st
import asyncio
import sys
import io as pyio
import traceback
import time
import threading
import json
from pathlib import Path

st.set_page_config(layout="wide", page_title="PyTutor – MCP Live Demo", page_icon="⚡")

st.markdown("""
<style>
  .panel-title {
    font-weight:700; font-size:14px; letter-spacing:.5px;
    padding:8px 12px; border-radius:6px 6px 0 0; margin-bottom:0;
  }
  .pt-dark  { background:#1a1a2e; color:white; }
  .pt-green { background:#1A4731; color:white; }
  .pt-blue  { background:#1E3A5F; color:white; }
  .log-box {
    background:#0d1117; color:#c9d1d9;
    font-family:Consolas,monospace; font-size:12.5px;
    border:1px solid #30363d; border-radius:0 0 6px 6px;
    padding:12px; height:370px; overflow-y:auto;
    white-space:pre-wrap; word-break:break-all;
  }
  .result-box {
    background:#0d1117; color:#c9d1d9;
    font-family:Consolas,monospace; font-size:13px;
    border:1px solid #30363d; border-radius:0 0 6px 6px;
    padding:14px; min-height:200px; white-space:pre-wrap;
  }
  .c-step  { color:#d2a8ff; font-weight:bold; }
  .c-send  { color:#79c0ff; }
  .c-recv  { color:#56d364; }
  .c-info  { color:#e3b341; }
  .c-error { color:#f85149; }
  .c-ok    { color:#56d364; font-weight:bold; }
  div[data-testid="stTextArea"] textarea {
    font-family:Consolas,monospace!important; font-size:13px!important;
    background:#0d1117!important; color:#c9d1d9!important;
    border:1px solid #30363d!important;
  }
</style>
""", unsafe_allow_html=True)

st.markdown("## ⚡ PyTutor — Demo Giao thức MCP Trực tiếp")
st.caption("Nhập bài toán Python → Nhấn Chạy → Xem JSON-RPC messages thực sự trao đổi giữa Client & Server")

# ─── Bài toán mẫu ─────────────────────────────────────────────────────────────
EXAMPLES = {
    "🔢 Tính tổng 1..n (vòng lặp)": (
        "# Bài toán: Tính tổng các số từ 1 đến n\n"
        "n = 10\ntong = 0\n"
        "for i in range(1, n + 1):\n    tong += i\n"
        'print(f"Tổng từ 1 đến {n} = {tong}")'
    ),
    "🔍 Tìm số nguyên tố": (
        "# Bài toán: Tìm số nguyên tố <= 30\n"
        "def la_nto(n):\n    if n < 2: return False\n"
        "    for i in range(2, int(n**0.5)+1):\n        if n%i==0: return False\n    return True\n\n"
        "nto = [i for i in range(2,31) if la_nto(i)]\n"
        'print(f"Số nguyên tố: {nto}")'
    ),
    "❌ Code có lỗi (xem MCP bắt lỗi)": (
        "# Code bị lỗi — thấy MCP xử lý lỗi an toàn\n"
        "danh_sach = [1, 2, 3]\n"
        "print(danh_sach[10])   # IndexError!"
    ),
    "📊 Tính trung bình & max/min": (
        "diem = [7.5, 8.0, 6.0, 9.5, 8.5, 7.0]\n"
        'print(f"Điểm: {diem}")\n'
        'print(f"Trung bình: {sum(diem)/len(diem):.2f}")\n'
        'print(f"Cao nhất: {max(diem)}, Thấp nhất: {min(diem)}")'
    ),
}

col_ex, _ = st.columns([1.5, 2.5])
with col_ex:
    choice = st.selectbox("📋 Bài toán mẫu:", list(EXAMPLES.keys()))

code_input = st.text_area("Code Python:", value=EXAMPLES[choice], height=170, label_visibility="collapsed")

col_b1, col_b2, col_b3 = st.columns([1.2, 1.2, 2])
with col_b1:
    btn_mcp = st.button("⚡ Chạy với MCP", type="primary", use_container_width=True)
with col_b2:
    btn_direct = st.button("🔧 Chạy trực tiếp (không MCP)", use_container_width=True)

st.divider()

# ─── 3 cửa sổ ─────────────────────────────────────────────────────────────────
col_log, col_result, col_diff = st.columns([1.8, 1.2, 1.1])

with col_log:
    st.markdown('<div class="panel-title pt-dark">🔌 MCP Protocol Log — JSON-RPC 2.0 (Thời gian thực)</div>', unsafe_allow_html=True)
    log_ph = st.empty()

with col_result:
    st.markdown('<div class="panel-title pt-green">✅ Output từ MCP Server</div>', unsafe_allow_html=True)
    res_ph = st.empty()

with col_diff:
    st.markdown('<div class="panel-title pt-blue">⚖️ MCP vs Direct</div>', unsafe_allow_html=True)
    diff_ph = st.empty()


def html_log(lines):
    parts = ['<div class="log-box">']
    for (cls, txt) in lines:
        txt_safe = txt.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        parts.append(f'<span class="{cls}">{txt_safe}</span>\n')
    parts.append("</div>")
    return "".join(parts)


def html_result(text, is_mcp, elapsed_ms):
    text_safe = text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    cls = "c-ok" if text.startswith("OK") else "c-error"
    badge = "MCP Server" if is_mcp else "exec() trực tiếp"
    return f'<div class="result-box"><span class="{cls}">{text_safe}</span>\n\n<span class="c-info">──────────────\n{badge} | {elapsed_ms:.0f}ms</span></div>'


# Khởi ô mặc định
log_ph.markdown('<div class="log-box"><span class="c-info">Chưa chạy. Nhấn "Chạy với MCP" để xem giao thức hoạt động...</span></div>', unsafe_allow_html=True)
res_ph.markdown('<div class="result-box"><span class="c-info">Kết quả sẽ hiển thị ở đây...</span></div>', unsafe_allow_html=True)
diff_ph.markdown("""<div class="result-box" style="font-size:11.5px">
<span class="c-info">Chạy cả 2 cách để so sánh.

Direct (exec):
  - Không có protocol
  - Không có Discovery
  - AI không biết output
    có cấu trúc gì

MCP (JSON-RPC 2.0):
  - Handshake chuẩn
  - Discovery tự động
  - Output có schema
  - Sandbox cô lập
  - Plug-and-play</span>
</div>""", unsafe_allow_html=True)


# ─── Logic chạy MCP ────────────────────────────────────────────────────────────

def run_mcp_sync(code: str) -> dict:
    """
    Chạy MCP Client → Server bằng SDK chính thức mcp 2.x
    Dùng asyncio.run trong thread riêng để tương thích Streamlit
    """
    result_holder = {}
    
    async def _run():
        from mcp.client.stdio import stdio_client, StdioServerParameters
        from mcp.client.session import ClientSession

        server_path = str(Path(__file__).parent / "mcp_server_pytutor.py")
        params = StdioServerParameters(
            command=sys.executable,
            args=[server_path],
            encoding="utf-8"
        )
        
        log_lines = []
        t_global = time.time()
        
        try:
            log_lines.append(("c-step", "▶ BƯỚC 1 — KHỞI ĐỘNG MCP SERVER (subprocess)"))
            log_lines.append(("c-info", f"  Lệnh: python mcp_server_pytutor.py\n  Giao thức: stdio (JSON-RPC 2.0)"))
            
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    
                    # ── Init ──────────────────────────────────
                    log_lines.append(("c-step", "\n▶ BƯỚC 2 — HANDSHAKE (initialize)"))
                    log_lines.append(("c-send", "→ CLIENT → SERVER:\n" + json.dumps({
                        "jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {"protocolVersion": "2024-11-05",
                                   "clientInfo": {"name": "PyTutor-Client", "version": "1.0"},
                                   "capabilities": {}}
                    }, indent=2, ensure_ascii=False)))
                    
                    t0 = time.time()
                    init = await session.initialize()
                    t1 = time.time()
                    
                    log_lines.append(("c-recv", f"← SERVER → CLIENT ({(t1-t0)*1000:.0f}ms):\n" + json.dumps({
                        "jsonrpc": "2.0", "id": 1, "result": {
                            "protocolVersion": "2024-11-05",
                            "serverInfo": {"name": init.serverInfo.name if hasattr(init,'serverInfo') else "PyTutor-Code-Engine"},
                            "capabilities": {}
                        }
                    }, indent=2, ensure_ascii=False)))
                    log_lines.append(("c-info", f"  ✓ Server xác nhận kết nối thành công!"))
                    
                    # ── List Tools ────────────────────────────
                    log_lines.append(("c-step", "\n▶ BƯỚC 3 — KHÁM PHÁ TOOLS (tools/list)"))
                    log_lines.append(("c-send", "→ CLIENT → SERVER:\n" + json.dumps(
                        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, indent=2)))
                    
                    t0 = time.time()
                    tools = await session.list_tools()
                    t1 = time.time()
                    
                    tool_list = [{"name": t.name, "description": t.description} for t in tools.tools]
                    log_lines.append(("c-recv", f"← SERVER → CLIENT ({(t1-t0)*1000:.0f}ms):\n" + json.dumps({
                        "jsonrpc": "2.0", "id": 2, "result": {"tools": tool_list}
                    }, indent=2, ensure_ascii=False)))
                    log_lines.append(("c-info", f"  ✓ Phát hiện {len(tools.tools)} tool(s): {[t.name for t in tools.tools]}"))
                    
                    # ── Call Tool ─────────────────────────────
                    log_lines.append(("c-step", "\n▶ BƯỚC 4 — GỌI TOOL run_code"))
                    log_lines.append(("c-send", "→ CLIENT → SERVER:\n" + json.dumps({
                        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                        "params": {
                            "name": "run_code",
                            "arguments": {"code": code[:120] + "..." if len(code) > 120 else code}
                        }
                    }, indent=2, ensure_ascii=False)))
                    
                    t0 = time.time()
                    call_result = await session.call_tool("run_code", arguments={"code": code})
                    t1 = time.time()
                    
                    result_text = call_result.content[0].text if call_result.content else "(Không có kết quả)"
                    log_lines.append(("c-recv", f"← SERVER → CLIENT ({(t1-t0)*1000:.0f}ms):\n" + json.dumps({
                        "jsonrpc": "2.0", "id": 3,
                        "result": {
                            "content": [{"type": "text", "text": result_text}]
                        }
                    }, indent=2, ensure_ascii=False)))
                    
                    total = (time.time() - t_global) * 1000
                    log_lines.append(("c-step", f"\n▶ HOÀN TẤT — Tổng thời gian: {total:.0f}ms"))
                    log_lines.append(("c-ok", f"  ✓ Giao thức MCP hoạt động thành công!"))
                    
                    result_holder["log"] = log_lines
                    result_holder["result"] = result_text
                    result_holder["elapsed_ms"] = total
                    
        except Exception as e:
            log_lines.append(("c-error", f"\n✗ LỖI: {traceback.format_exc()}"))
            result_holder["log"] = log_lines
            result_holder["result"] = f"ERROR\n{e}"
            result_holder["elapsed_ms"] = (time.time() - t_global) * 1000
    
    # Chạy async trong thread mới (tránh conflict event loop với Streamlit)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_run())
    loop.close()
    return result_holder


def run_direct_sync(code: str) -> dict:
    """Chạy code trực tiếp bằng exec() — KHÔNG qua MCP."""
    t0 = time.time()
    old_stdout = sys.stdout
    sys.stdout = pyio.StringIO()
    try:
        exec(compile(code, "<direct>", "exec"), {})
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        result = f"OK\n{output.strip()}" if output.strip() else "OK\n(Không có output)"
    except Exception as e:
        sys.stdout = old_stdout
        result = f"ERROR\n{type(e).__name__}: {e}"
    return {"result": result, "elapsed_ms": (time.time()-t0)*1000}


# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "mcp_elapsed" not in st.session_state:
    st.session_state.mcp_elapsed = None
if "direct_elapsed" not in st.session_state:
    st.session_state.direct_elapsed = None


def render_diff(mcp_ms, direct_ms):
    if mcp_ms and direct_ms:
        overhead = mcp_ms - direct_ms
        diff_ph.markdown(f"""<div class="result-box" style="font-size:11.5px">
<span class="c-step">KẾT QUẢ SO SÁNH:</span>

<span class="c-error">Direct: {direct_ms:.0f}ms</span>
<span class="c-recv">MCP:    {mcp_ms:.0f}ms</span>

<span class="c-info">Overhead MCP: ~{overhead:.0f}ms
(Process spawn + Handshake
 + JSON-RPC encode/decode)</span>

<span class="c-step">TẠI SAO MCP HƠN?</span>
<span class="c-recv">✓ Agent tự khám phá Tool
✓ Output có schema chuẩn
✓ Sandbox: code cô lập
✓ Thêm tool = thêm hàm
✓ Mọi AI dùng được ngay
✓ Giải N×M problem

</div>""", unsafe_allow_html=True)



# ─── XỬ LÝ NÚT ────────────────────────────────────────────────────────────────
if btn_mcp:
    # Hiển thị "đang chạy"
    log_ph.markdown('<div class="log-box"><span class="c-info">🔄 Đang khởi động MCP Server và thiết lập kết nối...</span></div>', unsafe_allow_html=True)
    res_ph.markdown('<div class="result-box"><span class="c-info">⏳ Đang xử lý qua MCP...</span></div>', unsafe_allow_html=True)
    
    out = run_mcp_sync(code_input)
    
    st.session_state.mcp_elapsed = out.get("elapsed_ms", 0)
    log_ph.markdown(html_log(out.get("log", [])), unsafe_allow_html=True)
    res_ph.markdown(html_result(out.get("result", ""), is_mcp=True, elapsed_ms=out.get("elapsed_ms", 0)), unsafe_allow_html=True)
    render_diff(st.session_state.mcp_elapsed, st.session_state.direct_elapsed)


if btn_direct:
    res_ph.markdown('<div class="result-box"><span class="c-info">⏳ Đang chạy trực tiếp...</span></div>', unsafe_allow_html=True)
    out = run_direct_sync(code_input)
    
    st.session_state.direct_elapsed = out["elapsed_ms"]
    log_ph.markdown('<div class="log-box"><span class="c-error">✗ KHÔNG CÓ PROTOCOL LOG</span>\n\n<span class="c-info">Khi chạy trực tiếp (exec), không có:\n- Bước Handshake\n- Bước Discovery\n- JSON-RPC messages\n- Schema chuẩn cho AI đọc\n- Sandbox cô lập\n\nCode chạy thẳng vào process hiện tại.\nNếu code vô tận loop → crash toàn app!\n\n→ Nhấn "Chạy với MCP" để thấy sự khác biệt.</span></div>', unsafe_allow_html=True)
    res_ph.markdown(html_result(out["result"], is_mcp=False, elapsed_ms=out["elapsed_ms"]), unsafe_allow_html=True)
    render_diff(st.session_state.mcp_elapsed, st.session_state.direct_elapsed)
