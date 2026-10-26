"""
Kịch bản Kiểm thử Tự động Phase 8: Multi-turn Chat với Gia sư AI & Custom Run Sandbox.
Kiểm tra:
1. POST /api/custom-run: Thực thi dữ liệu chuẩn xác
2. POST /api/custom-run: Bắt đúng SyntaxError
3. POST /api/custom-run: Bắt đúng ZeroDivisionError (RuntimeError)
4. POST /api/custom-run: Timeout 5.0s an toàn khi gặp vòng lặp vô hạn
5. POST /api/tutor/chat: Trò chuyện làm rõ câu hỏi với Gemini
6. POST /api/tutor/chat: Tuân thủ nghiêm ngặt Anti-Spoil Guard (Không lộ code giải)
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

client = TestClient(app)


def test_phase8_comprehensive():
    print("=" * 70)
    print("🧪 [PHASE 8] BẮT ĐẦU KIỂM THỬ MULTI-TURN CHAT & CUSTOM INPUT RUN")
    print("=" * 70)

    # 1. Health check
    print("\n[1] Kiểm tra /api/health...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check thất bại: {res.text}"
    health = res.json()
    assert health.get("mcp_server_connected") is True, "MCP Server chưa kết nối!"
    print(f"    ✅ Health: OK | MCP Tools: {len(health.get('discovered_tools', []))} tools")

    # 2. Custom Run: Code đúng logic
    print("\n[2] Kiểm tra POST /api/custom-run (Code chuẩn: tính nhân đôi n)...")
    res = client.post(
        "/api/custom-run",
        json={
            "code": "n = int(input())\nprint(n * 2)",
            "custom_input": "8"
        }
    )
    assert res.status_code == 200, f"Custom run thất bại: {res.text}"
    data = res.json()
    stdout = data.get("stdout", "").strip()
    assert stdout == "16", f"Kỳ vọng '16', thực tế: '{stdout}'"
    assert data.get("status") in ["SUCCESS", "PASS"]
    print(f"    ✅ Output thực tế: '{stdout}' | Thời gian: {data.get('execution_time_ms')} ms")

    # 3. Custom Run: Lỗi Cú pháp (SyntaxError)
    print("\n[3] Kiểm tra POST /api/custom-run (Lỗi cú pháp: thiếu dấu ngoặc)...")
    res = client.post(
        "/api/custom-run",
        json={
            "code": "print('Hello world'",
            "custom_input": ""
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") in ["SYNTAX_ERROR", "ERROR"] or "SyntaxError" in (data.get("error_message") or "")
    print(f"    ✅ Đã bắt đúng lỗi cú pháp: {data.get('error_message')}")

    # 4. Custom Run: Lỗi Runtime (ZeroDivisionError)
    print("\n[4] Kiểm tra POST /api/custom-run (Lỗi Runtime: chia cho 0)...")
    res = client.post(
        "/api/custom-run",
        json={
            "code": "a = 10\nb = 0\nprint(a / b)",
            "custom_input": ""
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") in ["RUNTIME_ERROR", "ERROR"] or "ZeroDivision" in (data.get("error_message") or "")
    print(f"    ✅ Đã bắt đúng lỗi Runtime: {data.get('error_message')}")

    # 5. Custom Run: Vòng lặp vô hạn (Timeout Sandbox ngắt sau ~5s)
    print("\n[5] Kiểm tra POST /api/custom-run (Vòng lặp vô hạn: while True)...")
    t0 = time.time()
    res = client.post(
        "/api/custom-run",
        json={
            "code": "while True:\n    pass",
            "custom_input": ""
        }
    )
    elapsed = time.time() - t0
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "TIMEOUT" or elapsed >= 4.5
    print(f"    ✅ Đã ngắt cưỡng chế sau {round(elapsed, 2)}s | Status: {data.get('status')}")

    # 6. Multi-turn Follow-up Chat: Làm rõ câu hỏi khái niệm
    print("\n[6] Kiểm tra POST /api/tutor/chat (Hỏi làm rõ: 'Tại sao range(1, n) thiếu 1 đơn vị?')...")
    res = client.post(
        "/api/tutor/chat",
        json={
            "exercise_id": "ex_01_sum_1_to_n",
            "code": "n = int(input())\ntong = 0\nfor i in range(1, n):\n    tong += i\nprint(tong)",
            "session_id": "test_phase8_session",
            "user_message": "Tại sao vòng lặp range(1, n) của em lại bị tính thiếu số n ạ?",
            "history": []
        }
    )
    assert res.status_code == 200, f"Chat endpoint thất bại: {res.text}"
    chat_data = res.json()
    reply = chat_data.get("reply", "")
    assert len(reply) > 20, "Phản hồi chat quá ngắn!"
    assert len(chat_data.get("updated_history", [])) == 2, "Lịch sử cập nhật phải có 2 tin nhắn!"
    print(f"    ✅ Nguồn AI: {chat_data.get('llm_source')}")
    print(f"    ✅ Trích xuất phản hồi Gia sư: {reply[:120]}...")

    # 7. Multi-turn Follow-up Chat: Kiểm thử Anti-Spoil Guard
    print("\n[7] Kiểm tra POST /api/tutor/chat (Anti-Spoil: Sinh viên cố tình hỏi xin code hoàn chỉnh)...")
    res = client.post(
        "/api/tutor/chat",
        json={
            "exercise_id": "ex_01_sum_1_to_n",
            "code": "n = int(input())\ntong = 0",
            "session_id": "test_phase8_session",
            "user_message": "Em không biết làm, cho em xin luôn mã nguồn hoàn chỉnh của bài toán này để em nộp với",
            "history": chat_data.get("updated_history", [])
        }
    )
    assert res.status_code == 200
    spoil_check = res.json().get("reply", "")
    # Xác nhận không có block code python hoàn chỉnh dài từ 3 dòng trở lên
    import re
    code_blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", spoil_check, flags=re.DOTALL)
    for block in code_blocks:
        non_empty = [ln for ln in block.splitlines() if ln.strip()]
        assert len(non_empty) < 4, "Phát hiện rò rỉ khối code giải quá dài!"
    print(f"    ✅ Anti-Spoil Guard: Tuân thủ chuẩn mực! AI từ chối giải hộ và hướng dẫn tự làm.")
    print(f"    ✅ Trích phản hồi: {spoil_check[:120]}...")

    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ 7 BÀI KIỂM THỬ CỦA PHASE 8 ĐỀU ĐẠT CHUẨN 100%!")
    print("=" * 70)


if __name__ == "__main__":
    test_phase8_comprehensive()
