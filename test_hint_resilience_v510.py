"""Độ tin cậy luồng gợi ý (v5.10): mọi lỗi của Gemini/Qwen/MCP/vết chạy đều dẫn tới gợi ý tất định, không bao giờ 500 hay rỗng.
Hàm thuần + giả lập nhà cung cấp; không cần DB, không gọi LLM thật. Chạy: py -m unittest test_hint_resilience_v510 -v
"""
import asyncio
import os
import unittest
from unittest import mock

os.environ.setdefault("PYTUTOR_DISABLE_LLM", "1")

from backend import hint_evidence as he  # noqa: E402
from backend import llm_service  # noqa: E402
from backend.hint_rules import build_offline_hint  # noqa: E402
from backend import mcp_client  # noqa: E402

EX = {"title": "Bài 01: Tính tổng", "description": "### Đầu vào (Input):\n- Một số nguyên n.\n### Đầu ra (Output):\n- Tổng.", "starter_code": "n = int(input())\n"}
CODE = "n = int(input())\ntong = 0\nfor i in range(1, n):\n    tong += i\nprint(tong)\n"
TR = {"all_passed": False, "passed_tests": 0, "total_tests": 2, "summary": "0/2",
      "results": [{"test_idx": 1, "status": "FAIL", "input": "1", "expected_output": "1", "actual_output": "0", "error_message": None}]}
AST = {"valid": True, "has_loops": True, "structural_summary": "Có vòng lặp for"}
USAGE = {"prompt_tokens": None, "completion_tokens": None}


def run(coro):
    return asyncio.run(coro)


def hint(level, gemini=None, history=None, trace=None, code=CODE, tr=TR, ast_a=AST):
    """Gọi generate_tutor_hint với `call_gemini_with_usage` giả lập; `gemini` là giá trị hoặc ngoại lệ trả về."""
    async def fake_gemini(prompt):
        if isinstance(gemini, Exception):
            raise gemini
        return gemini, USAGE

    async def no_qwen(*a, **k):
        return None
    with mock.patch.object(llm_service, "call_gemini_with_usage", fake_gemini), mock.patch.object(llm_service, "call_qwen_api", no_qwen):
        return run(llm_service.generate_tutor_hint(EX, code, tr, ast_a, level, attempt_history=history, trace=trace))


class ProviderFailureTests(unittest.TestCase):
    def test_no_provider_response_gives_deterministic_hint_for_every_level(self):
        for level in (1, 2, 3):
            text, source, telemetry = hint(level, gemini=None)
            self.assertIn(f"MỨC {level}", text)
            self.assertEqual(source, "Pedagogical-Rule-Engine (Offline Fallback)")
            self.assertEqual(telemetry["status"], "fallback")

    def test_empty_or_tiny_gemini_reply_never_reaches_the_student(self):
        """Bản cũ trả nguyên chuỗi rỗng ở Mức 3 (không qua bộ lọc nào chặn); v5.10 coi như không có phản hồi."""
        for level in (1, 2, 3):
            for bad in ("", "   \n", "ok"):
                text, source, _ = hint(level, gemini=(bad, "Google test"))
                self.assertGreater(len(text.strip()), 60, (level, bad))
                self.assertIn("Pedagogical-Rule-Engine", source)

    def test_good_reply_is_kept(self):
        reply = "💡 Mức 1: " + "Hãy xem lại khái niệm vòng lặp với range. " * 3
        text, source, telemetry = hint(1, gemini=(reply, "Google test"))
        self.assertEqual(text, reply)
        self.assertEqual(telemetry["status"], "success")

    def test_guard_blocked_reply_falls_back_with_history_aware_hint(self):
        leaked = "Đây là lời giải:\n```python\nn = int(input())\ntong = 0\nfor i in range(1, n + 1):\n    tong += i\nprint(tong)\n```"
        text, source, telemetry = hint(2, gemini=(leaked, "Google test"))
        self.assertNotIn("range(1, n + 1)", text)  # bị ẩn hoặc thay bằng gợi ý tất định; lời giải không tới tay người học
        self.assertIn("MỨC 2" if "Rule-Engine" in source else "🔒", text)

    def test_level3_reply_has_logic_masked(self):
        reply = ("### 1. Dàn ý\n- **Bước 1:** đọc n\n- **Bước 2:** khởi tạo\n- **Bước 3:** lặp\n- **Bước 4:** in\n"
                 "```python\nn = int(input())\ntong = 0\nfor i in range(1, n + 1):\n    tong += i\nprint(tong)\n```")
        text, _, telemetry = hint(3, gemini=(reply, "Google test"))
        self.assertNotIn("range(1, n + 1)", text)
        self.assertTrue(telemetry["output_guard"].startswith("level3_masked"))


class OfflineRobustnessTests(unittest.TestCase):
    def test_missing_or_odd_inputs_do_not_raise(self):
        weird_results = [
            {}, {"results": []}, {"results": [{"status": "FAIL"}]},
            {"results": [{"status": "RUNTIME_ERROR", "input": None, "expected_output": None, "actual_output": None, "error_message": None, "stderr": None}]},
            {"results": [{"status": "TIMEOUT", "input": "1"}]},
        ]
        for tr in weird_results:
            for level in (1, 2, 3):
                for code in ("", None, "x", "for", CODE):
                    for ast_a in ({}, None, {"valid": False, "syntax_error": "chuỗi lạ"}, {"valid": False, "syntax_error": {"lineno": 99}}):
                        text = build_offline_hint({"title": "t"}, code, dict(tr, all_passed=False), ast_a, level)
                        self.assertGreater(len(text.strip()), 40)

    def test_malformed_history_entries_are_tolerated(self):
        history = [None, {}, {"tutor_hint": None, "action_type": "ask_ai", "hint_level": None}, {"hint_level": "x"}, {"tutor_hint": "x" * 5000, "action_type": "ask_ai", "hint_level": 1}]
        history = [h for h in history if h is not None]
        for level in (1, 2, 3):
            self.assertGreater(len(hint(level, gemini=None, history=history)[0]), 60)
        prompt = llm_service.build_scaffolding_prompt(EX, CODE, TR, AST, 2, attempt_history=history)
        self.assertLess(prompt.count("x" * 400), 1)  # gợi ý cũ bị cắt ngắn, không đưa nguyên 5000 ký tự vào prompt

    def test_trace_with_garbage_is_ignored(self):
        for trace in ({}, {"line_counts": {"a": 1}}, {"final_locals": {"n": None}}, {"line_counts": None, "final_locals": None}):
            try:
                text = hint(2, gemini=None, trace=trace)[0]
            except Exception as exc:  # noqa: BLE001
                self.fail(f"trace {trace!r} làm hỏng gợi ý: {exc}")
            self.assertIn("MỨC 2", text)


class TraceStepFailureTests(unittest.TestCase):
    """`_trace_failure` là phần phụ: mọi lỗi chỉ ghi SKIPPED vào mcp_trace và trả None."""

    class FakeSession:
        def __init__(self, behaviour):
            self.behaviour = behaviour

        async def call_tool(self, name, arguments=None):
            if self.behaviour == "timeout":
                await asyncio.sleep(10)
            if self.behaviour == "raise":
                raise RuntimeError("máy chủ MCP đóng kết nối")

            class Content:
                text = "đây không phải JSON"
            return type("Res", (), {"content": [Content()]})()

    def _run(self, behaviour):
        trace_log: list = []
        with mock.patch.object(mcp_client, "TRACE_TIMEOUT_S", 0.05):
            result = run(mcp_client._trace_failure(self.FakeSession(behaviour), CODE, TR, AST, trace_log))
        return result, trace_log

    def test_errors_timeout_and_bad_json_return_none_with_skipped_step(self):
        for behaviour in ("raise", "timeout", "garbage"):
            result, log = self._run(behaviour)
            self.assertIsNone(result, behaviour)
            self.assertEqual(log[-1]["status"], "SKIPPED", behaviour)
            self.assertEqual(log[-1]["tool_name"], "trace_code_execution")

    def test_not_traced_for_syntax_error_timeout_or_pass(self):
        syntax_ast = {"valid": False, "syntax_error": {"lineno": 1, "message": "x"}}
        timeout_tr = {"results": [{"status": "TIMEOUT", "input": "1"}]}
        for tr, ast_a in ((TR, syntax_ast), (timeout_tr, AST), ({"results": [{"status": "PASS"}]}, AST)):
            log: list = []
            self.assertIsNone(run(mcp_client._trace_failure(self.FakeSession("raise"), CODE, tr, ast_a, log)))
            self.assertEqual(log, [])  # không gọi, không ghi bước nào


class EvidenceDefensiveTests(unittest.TestCase):
    def test_pick_failure_and_suspect_on_empty(self):
        self.assertIsNone(he.pick_failure(None))
        self.assertIsNone(he.suspect_line(None, None, "wrong_output", None))
        self.assertEqual(he.traceback_line(None), None)
        self.assertEqual(he.error_type(None), "")


if __name__ == "__main__":
    unittest.main()
