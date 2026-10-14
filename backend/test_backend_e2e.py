"""
Kịch bản kiểm thử Tích hợp Toàn diện (End-to-End Integration Test) cho Backend.
Kiểm tra luồng hoạt động từ FastAPI App -> MCP Server (qua stdio) -> LLM Service (Qwen / Fallback)
"""
import sys
import os
import asyncio
from pathlib import Path
import httpx

# Cấu hình UTF-8 trên Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.main import app


async def run_backend_e2e_tests():
    print("=" * 70)
    print("🧪 [PHASE 2] BẮT ĐẦU KIỂM THỬ TÍCH HỢP TOÀN DIỆN BACKEND E2E")
    print("=" * 70)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:

        # -------------------------------------------------------------
        # 1. Test GET /api/health (True MCP Discovery)
        # -------------------------------------------------------------
        print("\n[1] Kiểm thử GET /api/health (Xác nhận True MCP Discovery)...")
        res = await client.get("/api/health")
        print(f"    HTTP Status: {res.status_code}")
        data = res.json()
        print(f"    Trạng thái: {data.get('status')}")
        print(f"    MCP Server Connected: {data.get('mcp_server_connected')}")
        print(f"    Discovered Tools: {data.get('discovered_tools')}")
        assert res.status_code == 200, f"Lỗi health check: {res.text}"
        assert data["mcp_server_connected"] is True, "MCP Server phải kết nối thành công"
        assert len(data["discovered_tools"]) >= 4, "Cần khám phá đủ ít nhất 4 tools"
        print("    ✅ Health check & True MCP Discovery: PASS!")

        # -------------------------------------------------------------
        # 2. Test GET /api/exercises
        # -------------------------------------------------------------
        print("\n[2] Kiểm thử GET /api/exercises (Lấy danh mục bài tập từ MCP)...")
        res = await client.get("/api/exercises")
        assert res.status_code == 200
        ex_list = res.json()
        print(f"    Số lượng bài tập: {len(ex_list)}")
        for ex in ex_list:
            print(f"    • [{ex['difficulty']}] {ex['title']} ({ex['category']})")
        assert len(ex_list) >= 5, "Cần có ít nhất 5 bài tập"
        print("    ✅ Danh mục bài tập: PASS!")

        # -------------------------------------------------------------
        # 3. Test GET /api/exercises/{id}
        # -------------------------------------------------------------
        print("\n[3] Kiểm thử GET /api/exercises/ex_01_sum_1_to_n...")
        res = await client.get("/api/exercises/ex_01_sum_1_to_n")
        assert res.status_code == 200
        ex_detail = res.json()
        print(f"    Tiêu đề: {ex_detail['title']}")
        print(f"    Số test cases: {len(ex_detail['test_cases'])}")
        assert len(ex_detail["test_cases"]) > 0
        assert "starter_code" in ex_detail
        print("    ✅ Chi tiết bài tập: PASS!")

        # -------------------------------------------------------------
        # 4. Test POST /api/submit với CODE SAI LOGIC ở 3 mức gợi ý
        # -------------------------------------------------------------
        wrong_code = """
n = int(input())
# Tính sai logic
tong = n * 2
print(tong)
"""
        for level in [1, 2, 3]:
            print(f"\n[4.{level}] Kiểm thử POST /api/submit (Code sai logic, Hint Level {level})...")
            payload = {
                "exercise_id": "ex_01_sum_1_to_n",
                "code": wrong_code,
                "hint_level": level
            }
            res = await client.post("/api/submit", json=payload)
            assert res.status_code == 200, f"Submit failed: {res.text}"
            sub_res = res.json()
            
            t_res = sub_res["test_results"]
            print(f"    Kết quả Test: {t_res['passed_tests']}/{t_res['total_tests']} pass (All passed: {t_res['all_passed']})")
            print(f"    Nguồn sinh gợi ý: {sub_res['llm_source']}")
            print(f"    Nội dung gợi ý AI (trích đoạn 150 ký tự đầu):")
            hint_snippet = sub_res['tutor_hint'][:150].replace('\n', ' ')
            print(f"    \"{hint_snippet}...\"")
            
            assert t_res["all_passed"] is False, "Code sai logic không được pass 100%"
            assert len(sub_res["tutor_hint"]) > 30, "Gợi ý AI phải có nội dung đầy đủ"
            assert sub_res["hint_level"] == level
            print(f"    ✅ Hint Level {level}: PASS!")

        # -------------------------------------------------------------
        # 5. Test POST /api/submit với CODE ĐÚNG 100%
        # -------------------------------------------------------------
        print("\n[5] Kiểm thử POST /api/submit (Code đúng 100%)...")
        correct_code = """
n = int(input())
tong = 0
for i in range(1, n + 1):
    tong += i
print(tong)
"""
        payload_correct = {
            "exercise_id": "ex_01_sum_1_to_n",
            "code": correct_code,
            "hint_level": 1
        }
        res = await client.post("/api/submit", json=payload_correct)
        assert res.status_code == 200
        sub_correct = res.json()
        t_res = sub_correct["test_results"]
        print(f"    Kết quả Test: {t_res['passed_tests']}/{t_res['total_tests']} pass (All passed: {t_res['all_passed']})")
        print(f"    Tóm tắt: {t_res['summary']}")
        print(f"    Phản hồi AI Tutor chúc mừng/tối ưu:")
        print(f"    \"{sub_correct['tutor_hint'][:180].replace(chr(10), ' ')}...\"")
        assert t_res["all_passed"] is True, "Code đúng phải pass 100%"
        print("    ✅ Kịch bản Code đúng 100%: PASS!")

        # -------------------------------------------------------------
        # 6. Test POST /api/submit với CODE LỖI CÚ PHÁP
        # -------------------------------------------------------------
        print("\n[6] Kiểm thử POST /api/submit (Code lỗi cú pháp)...")
        syntax_bad_code = """
n = int(input())
for i in range(1, n + 1)
    tong += i
"""
        payload_syntax = {
            "exercise_id": "ex_01_sum_1_to_n",
            "code": syntax_bad_code,
            "hint_level": 2
        }
        res = await client.post("/api/submit", json=payload_syntax)
        assert res.status_code == 200
        sub_syntax = res.json()
        print(f"    AST Valid: {sub_syntax['ast_analysis']['valid']}")
        print(f"    Tóm tắt AST: {sub_syntax['ast_analysis']['structural_summary']}")
        print(f"    Gợi ý AI cho lỗi cú pháp:")
        print(f"    \"{sub_syntax['tutor_hint'][:150].replace(chr(10), ' ')}...\"")
        assert sub_syntax["ast_analysis"]["valid"] is False
        print("    ✅ Kịch bản lỗi cú pháp: PASS!")

    print("\n" + "=" * 70)
    print("🎉 TẤT CẢ 6 BÀI KIỂM THỬ BACKEND E2E ĐỀU ĐẠT CHUẨN 100%!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_backend_e2e_tests())
