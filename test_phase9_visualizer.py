"""
Kịch bản Kiểm thử Tự động Phase 9: Trực quan hóa Từng bước Thực thi & Cây Lộ trình Kỹ năng.
Kiểm tra:
1. MCP Server Discovery: Phát hiện đủ 8 MCP Tools (gồm trace_code_execution)
2. Tracer Engine: Tracing thuật toán tính tổng 1 đến 3 (bắt đúng biến số và stdout)
3. Tracer Engine: Tracing đệ quy giaithua(3) (bắt đúng frame call và return)
4. Tracer Engine: Vòng lặp vô hạn while True (tự dừng an toàn tại 150 bước / 3s)
5. POST /api/trace-execution: Endpoint FastAPI trả về dữ liệu chuẩn xác
6. POST /api/trace-execution: Bắt lỗi cú pháp sạch sẽ
7. GET /api/skill-roadmap: Trả về đồ thị DAG bài tập với trạng thái thích ứng
"""
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi.testclient import TestClient
from backend.main import app
from mcp_server.tracer import trace_code_execution

client = TestClient(app)


def test_phase9_comprehensive():
    print("=" * 75)
    print("🧪 [PHASE 9] BẮT ĐẦU KIỂM THỬ EXECUTION VISUALIZER & SKILL ROADMAP")
    print("=" * 75)

    # 1. MCP Discovery (Đủ 8 Tools)
    print("\n[1] Kiểm tra Discovery: Hệ thống MCP có đủ 8 MCP Tools...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check thất bại: {res.text}"
    health = res.json()
    assert health.get("mcp_server_connected") is True, "MCP Server chưa kết nối!"
    tools = health.get("discovered_tools", [])
    print(f"    -> Đã phát hiện {len(tools)} MCP Tools: {tools}")
    assert len(tools) >= 8, f"Kỳ vọng ít nhất 8 tools, thực tế có {len(tools)}"
    assert "trace_code_execution" in tools, "Thiếu MCP Tool: trace_code_execution!"
    print("    ✅ PASS: MCP Tool thứ 8 'trace_code_execution' đã sẵn sàng.")

    # 2. Tracing thuật toán tính tổng 1..3
    print("\n[2] Kiểm tra Tracer Engine: Thuật toán tính tổng 1 đến 3...")
    code_sum = """tong = 0
for i in range(1, 4):
    tong += i
print(tong)
"""
    trace_res = trace_code_execution(code_sum, stdin_input="", max_steps=150)
    assert trace_res["success"] is True, f"Trace thất bại: {trace_res.get('error')}"
    steps = trace_res["steps"]
    assert len(steps) > 0, "Không ghi nhận được bước thực thi nào!"

    # Kiểm tra biến tong và i
    final_step = steps[-1]
    stdout = final_step["stdout"].strip()
    assert stdout == "6", f"Kỳ vọng stdout='6', thực tế: '{stdout}'"

    found_tong = any("tong" in s["locals"] for s in steps)
    found_i = any("i" in s["locals"] for s in steps)
    assert found_tong and found_i, "Không bắt được biến 'tong' hoặc 'i' trong locals!"
    print(f"    ✅ PASS: Đã ghi nhận {len(steps)} bước thực thi | stdout: '{stdout}' | Biến: tong, i")

    # 3. Tracing Đệ quy giaithua(3)
    print("\n[3] Kiểm tra Tracer Engine: Đệ quy giaithua(3) bắt frame call & return...")
    code_fact = """def giaithua(n):
    if n <= 1:
        return 1
    return n * giaithua(n - 1)

res = giaithua(3)
print(res)
"""
    trace_fact = trace_code_execution(code_fact, max_steps=150)
    assert trace_fact["success"] is True
    fact_steps = trace_fact["steps"]
    events = [s["event"] for s in fact_steps]
    assert "call" in events, "Không ghi nhận được sự kiện 'call' trong đệ quy!"
    assert "return" in events, "Không ghi nhận được sự kiện 'return' trong đệ quy!"
    fact_stdout = fact_steps[-1]["stdout"].strip()
    assert fact_stdout == "6", f"Kỳ vọng giai thừa 3! = 6, thực tế: '{fact_stdout}'"
    print(f"    ✅ PASS: Đã ghi nhận đệ quy với {len(fact_steps)} bước | Call/Return events: OK")

    # 4. Tracing Vòng lặp vô hạn (Chống treo hệ thống)
    print("\n[4] Kiểm tra Tracer Engine: Chống vòng lặp vô hạn (Limit 150 bước)...")
    code_inf = """i = 0
while True:
    i += 1
"""
    t0 = time.time()
    trace_inf = trace_code_execution(code_inf, max_steps=150, timeout_seconds=3.0)
    elapsed = time.time() - t0
    assert trace_inf["truncated"] is True, "Hệ thống không đánh dấu truncated khi lặp vô hạn!"
    assert len(trace_inf["steps"]) <= 150, f"Vượt quá giới hạn bước: {len(trace_inf['steps'])}"
    assert elapsed < 4.0, f"Thời gian chạy quá lâu: {elapsed}s"
    print(f"    ✅ PASS: Tự ngắt an toàn tại bước {len(trace_inf['steps'])} trong {round(elapsed, 2)}s.")

    # 5. Endpoint POST /api/trace-execution (FastAPI API)
    print("\n[5] Kiểm tra POST /api/trace-execution qua FastAPI...")
    api_res = client.post(
        "/api/trace-execution",
        json={
            "code": "x = 10\ny = 20\nprint(x + y)",
            "stdin_input": "",
            "max_steps": 100
        }
    )
    assert api_res.status_code == 200, f"API trace thất bại: {api_res.text}"
    api_data = api_res.json()
    assert api_data["success"] is True
    assert api_data["total_steps"] > 0
    assert len(api_data["steps"]) == api_data["total_steps"]
    assert api_data["steps"][-1]["stdout"].strip() == "30"
    print(f"    ✅ PASS: API trả về {api_data['total_steps']} bước | Kết quả: 30")

    # 6. Endpoint POST /api/trace-execution: Bắt SyntaxError
    print("\n[6] Kiểm tra POST /api/trace-execution với lỗi cú pháp...")
    err_res = client.post(
        "/api/trace-execution",
        json={
            "code": "def loi_cu_phap(: pass",
            "stdin_input": "",
            "max_steps": 50
        }
    )
    assert err_res.status_code == 200
    err_data = err_res.json()
    assert err_data["success"] is False
    assert err_data["error"] is not None
    assert "Lỗi cú pháp" in err_data["error"]
    print(f"    ✅ PASS: Bắt lỗi cú pháp chính xác: '{err_data['error']}'")

    # 7. Endpoint GET /api/skill-roadmap (Cây Lộ trình Kỹ năng DAG)
    print("\n[7] Kiểm tra GET /api/skill-roadmap (Đồ thị DAG phụ thuộc)...")
    road_res = client.get("/api/skill-roadmap?session_id=test_phase9_session")
    assert road_res.status_code == 200, f"Skill roadmap thất bại: {road_res.text}"
    road_data = road_res.json()
    nodes = road_data.get("nodes", [])
    assert len(nodes) >= 5, f"Kỳ vọng ít nhất 5 bài tập, có {len(nodes)}"

    node_map = {n["id"]: n for n in nodes}
    assert "ex_01_sum_1_to_n" in node_map, "Thiếu bài 01 trong cây kỹ năng!"
    assert "ex_02_prime_check" in node_map, "Thiếu bài 02 trong cây kỹ năng!"

    # Kiểm tra liên kết tiên quyết
    ex01 = node_map["ex_01_sum_1_to_n"]
    ex02 = node_map["ex_02_prime_check"]
    assert ex01["prerequisites"] == [], "Bài 01 không được có bài tiên quyết!"
    assert "ex_01_sum_1_to_n" in ex02["prerequisites"], "Bài 02 phải có bài 01 là tiên quyết!"
    assert ex01["status"] in ["AVAILABLE", "MASTERED", "IN_PROGRESS"]
    print(f"    ✅ PASS: Cây lộ trình trả về {len(nodes)} bài | Tiên quyết DAG: Chuẩn xác")

    print("\n" + "=" * 75)
    print("🎉 TẤT CẢ 7 BÀI TEST TỰ ĐỘNG CỦA PHASE 9 ĐỀU ĐẠT 100% (ALL PASSED)!")
    print("=" * 75)


if __name__ == "__main__":
    test_phase9_comprehensive()
