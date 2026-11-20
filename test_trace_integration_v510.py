"""Tích hợp bước vết chạy (v5.10) với MCP server THẬT: `execute_submission_pipeline(with_trace=True)` trả `failure_trace`
đúng dạng, và dạng đó đủ để `suspect_line` chọn đúng dòng. Cần cơ sở dữ liệu tạm (không đọc pytutor.db):
  .\\.claude\\run_isolated.ps1 test_trace_integration_v510
"""
import asyncio
import os
import unittest

NEEDS_ISOLATION = not os.environ.get("PYTUTOR_DB_PATH")

CODE = "n = int(input())\ntong = 0\nfor i in range(1, n):\n    tong += i\nprint(tong)\n"
EX = "ex_01_sum_1_to_n"


@unittest.skipIf(NEEDS_ISOLATION, "cần PYTUTOR_DB_PATH trỏ tới DB tạm (dùng .claude/run_isolated.ps1)")
class TraceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from backend.database import init_db
        init_db()

    def _run(self, code, with_trace):
        from backend.mcp_client import execute_submission_pipeline
        return asyncio.run(execute_submission_pipeline(EX, code, session_id="trace_it", with_trace=with_trace))

    def test_trace_shape_and_suspect_line_from_real_mcp(self):
        from backend import hint_evidence as he
        res = self._run(CODE, True)
        tr = res["failure_trace"]
        self.assertIsNotNone(tr, "vết chạy phải có cho mã hợp lệ cú pháp, bài chưa đạt")
        self.assertTrue(tr["ok"])
        self.assertEqual(tr["final_locals"].get("tong"), "0")
        # vòng lặp ở dòng 3 được chạy (kiểm tra điều kiện) nhưng thân (dòng 4) không chạy lần nào với n = 1
        self.assertGreater(tr["line_counts"].get(3, 0), 0)
        self.assertEqual(tr["line_counts"].get(4, 0), 0)
        step = [t for t in res["mcp_trace"] if t["tool_name"] == "trace_code_execution"][-1]
        self.assertEqual(step["status"], "SUCCESS")
        failure = he.pick_failure(res["test_results"])
        s = he.suspect_line(CODE, failure, "wrong_output", res["ast_analysis"], tr)
        self.assertEqual((s.text, s.basis), ("for i in range(1, n):", "block_not_run"))

    def test_no_trace_when_not_requested_or_when_passed_or_risky(self):
        self.assertIsNone(self._run(CODE, False)["failure_trace"])
        passed = "n = int(input())\ntong = 0\nfor i in range(1, n + 1):\n    tong += i\nprint(tong)\n"
        self.assertIsNone(self._run(passed, True)["failure_trace"])
        risky = self._run("import os\nn = int(input())\nprint(n)\n", True)
        self.assertIsNone(risky["failure_trace"])
        self.assertFalse([t for t in risky["mcp_trace"] if t["tool_name"] == "trace_code_execution"])


if __name__ == "__main__":
    unittest.main()
