"""Test v5.12: nâng cấp gợi ý Mức 2 (đối chứng, dãy giá trị, thiếu bước cập nhật) và Mức 3 (thuật toán chi tiết bằng lời).

Phần đầu không cần DB. Lớp `AlgorithmNotesApiTests` cần DB tạm: chạy bằng `.\\.claude\\run_isolated.ps1 test_hint_l23_v512`
(tự bỏ qua nếu chưa đặt PYTUTOR_DB_PATH).
"""
from __future__ import annotations

import ast
import json
import os
import re
import unittest
from pathlib import Path

os.environ.setdefault("PYTUTOR_DISABLE_LLM", "1")

from backend import hint_algorithm as ha  # noqa: E402
from backend import hint_evidence as he  # noqa: E402
from backend.guardrails import enforce_level3_prose  # noqa: E402
from backend.hint_rules import build_offline_hint  # noqa: E402

SEED = {e["id"]: e for e in json.loads((Path(__file__).parent / "seed" / "exercises_seed.json").read_text(encoding="utf-8"))}


def results(rows):
    return {"all_passed": all(r["status"] == "PASS" for r in rows), "passed_tests": sum(r["status"] == "PASS" for r in rows),
            "total_tests": len(rows), "results": rows}


def row(idx, status, inp, exp, act="", err=""):
    return {"test_idx": idx, "status": status, "input": inp, "expected_output": exp, "actual_output": act, "error_message": err, "stderr": ""}


class Level2EvidenceTests(unittest.TestCase):
    CODE = "n = int(input())\ntong = 0\nprint(tong)\n"

    def test_never_updated_is_reported_as_observation_not_error(self):
        tr = results([row(1, "FAIL", "1", "1", "0")])
        s = he.suspect_line(self.CODE, tr["results"][0], "wrong_output", {"valid": True})
        self.assertEqual(s.basis, "never_updated")
        self.assertEqual(s.lineno, 2)
        self.assertIn("chỉ được gán một lần", s.note)
        text = build_offline_hint(SEED["ex_01_sum_1_to_n"], self.CODE, tr, {"valid": True}, 2)
        self.assertIn("chưa phải kết luận", text)
        self.assertNotRegex(text, r"(?i)đổi\s+.*thành|sửa\s+.*thành|thay\s+.*bằng")

    def test_assignment_inside_loop_is_not_never_updated(self):
        code = "n = int(input())\ntong = 0\nfor i in range(1, n):\n    tong += i\nprint(tong)\n"
        tr = results([row(1, "FAIL", "3", "6", "3")])
        s = he.suspect_line(code, tr["results"][0], "wrong_output", {"valid": True})
        self.assertNotEqual(s.basis, "never_updated")

    def test_contrast_uses_passing_test_and_rotation_changes_failure(self):
        tr = results([row(1, "PASS", "1", "1", "1"), row(2, "FAIL", "5", "15", "10"), row(3, "FAIL", "100", "5050", "4950")])
        self.assertEqual(he.passing_contrast(tr, tr["results"][1])["input"], "1")
        self.assertEqual(he.pick_failure(tr)["test_idx"], 2)
        self.assertEqual(he.pick_failure(tr, rotate=1)["test_idx"], 3)
        self.assertEqual(he.pick_failure(tr, rotate=2)["test_idx"], 2)  # quay vòng
        code = "n = int(input())\ntong = 0\nfor i in range(1, n):\n    tong += i\nprint(tong)\n"
        text = build_offline_hint(SEED["ex_01_sum_1_to_n"], code, tr, {"valid": True, "has_loops": True}, 2)
        self.assertIn("Đối chứng", text)
        self.assertIn("`1`", text)

    def test_value_history_note_sequence_and_constant(self):
        trace = {"input": "3\n", "value_history": {"n": ["3"], "tong": ["0", "1", "3"], "i": ["1", "2"]}}
        note = he.value_history_note("n = int(input())\ntong = 0\nfor i in range(1, n):\n    tong += i\n", trace)
        self.assertIn("lần lượt có giá trị", note)
        self.assertIn("`1`", note)
        const = he.value_history_note("n = int(input())\ntong = 0\nprint(tong)\n", {"input": "3", "value_history": {"n": ["3"], "tong": ["0"]}})
        self.assertIn("giữ nguyên giá trị `0`", const)
        self.assertNotIn("`n` giữ nguyên", const)  # biến đọc từ input không phải điều đáng nói

    def test_observed_difference_names_patterns(self):
        self.assertIn("đúng 1 đơn vị", he.observed_difference("5", "4"))
        self.assertIn("kỳ vọng khác 0", he.observed_difference("15", "0"))
        self.assertIn("cùng", he.observed_difference("olleh", "hello").replace("giống nhau", "cùng"))
        self.assertIn("ngắn hơn", he.observed_difference("abcd", "abc"))


class AlgorithmPlanTests(unittest.TestCase):
    def test_kind_detection_for_seed_exercises(self):
        kinds = {k: ha.kind_of(v) for k, v in SEED.items()}
        self.assertEqual(kinds["ex_01_sum_1_to_n"], "sum")
        self.assertEqual(kinds["ex_02_prime_check"], "prime")
        self.assertEqual(kinds["ex_03_factorial"], "product")
        self.assertEqual(kinds["ex_04_reverse_string"], "reverse")
        self.assertEqual(kinds["ex_05_count_vowels"], "count")

    def test_notes_become_substeps_and_code_is_dropped(self):
        ex = dict(SEED["ex_01_sum_1_to_n"], algorithm_notes="Dùng biến tích lũy bắt đầu từ 0.\n```python\ntong = 0\n```\n"
                  "tong += i\nDuyệt các số từ 1 tới n và cộng vào biến tích lũy.")
        plan = ha.algorithm_plan(ex)
        self.assertEqual(plan["source"], "instructor")
        subs = plan["steps"][2][1]
        self.assertTrue(any("Duyệt các số" in s for s in subs))
        self.assertFalse(any("tong += i" in s or "tong = 0" in s for s in subs))

    def test_without_notes_uses_template_and_says_so(self):
        ex = {k: v for k, v in SEED["ex_04_reverse_string"].items() if k != "algorithm_notes"}
        plan = ha.algorithm_plan(ex)
        self.assertEqual(plan["source"], "template")
        self.assertIn("tổng quát", ha.SOURCE_NOTE["template"])
        self.assertEqual(len(plan["steps"]), 4)

    def test_every_template_is_words_only(self):
        for kind, tpl in ha._TEMPLATES.items():
            blob = tpl["idea"] + " " + " ".join(l + " " + " ".join(s) for l, s in tpl["steps"]) + " " + " ".join(tpl["edges"])
            self.assertNotIn("`", blob, kind)
            self.assertIsNone(re.search(r"range\s*\(|\+=|\[::|\bfor\s+\w+\s+in\b", blob), kind)


class ProseGuardTests(unittest.TestCase):
    def test_masks_expressions_but_keeps_names_and_test_values(self):
        reply = "Duyệt `range(1, n + 1)` rồi `tong += i`. Giá trị `15` và `tong` và `Hello World` và `s[::-1]`.\ntong = tong + i"
        out, n = enforce_level3_prose(reply, ["15"])
        self.assertEqual(n, 4)
        self.assertIn("`15`", out)
        self.assertIn("`tong`", out)
        self.assertIn("`Hello World`", out)
        self.assertNotIn("range(", out)
        self.assertNotIn("[::-1]", out)
        self.assertIn("🔒", out)

    def test_does_not_touch_code_fence_or_clean_text(self):
        reply = "Chỉ có lời.\n```python\nx = ...  # TODO (Bước 3.1)\n```\n"
        out, n = enforce_level3_prose(reply, [])
        self.assertEqual((out, n), (reply, 0))

    def test_test_value_with_operators_is_allowed(self):
        out, n = enforce_level3_prose("Đầu vào `a+b` cho ra `3`.", ["a+b"])
        self.assertEqual(n, 0)


class Level3OfflineTests(unittest.TestCase):
    CASES = [
        ("ex_01_sum_1_to_n", "n = int(input())\ntong = 0\nfor i in range(1, n):\n    tong += i\nprint(tong)\n"),
        ("ex_02_prime_check", "n = int(input())\nif n > 1:\n    print('YES')\nelse:\n    print('NO')\n"),
        ("ex_03_factorial", "n = int(input())\ngiai_thua = 0\nfor i in range(1, n + 1):\n    giai_thua *= i\nprint(giai_thua)\n"),
        ("ex_04_reverse_string", "s = input()\nprint(s)\n"),
        ("ex_05_count_vowels", "s = input()\ndem = 0\nfor c in s:\n    if c == 'a':\n        dem += 1\nprint(dem)\n"),
    ]

    def run_case(self, ex_id, code):
        from mcp_server.sandbox import run_test_cases
        ex = SEED[ex_id]
        tr = run_test_cases(code, ex["test_cases"])
        self.assertFalse(tr["all_passed"], ex_id)
        return ex, tr, build_offline_hint(ex, code, tr, {"valid": True, "has_loops": "for" in code}, 3)

    def test_algorithm_detail_structure_and_no_code_in_prose(self):
        import hint_quality_checks as hq
        for ex_id, code in self.CASES:
            ex, tr, text = self.run_case(ex_id, code)
            self.assertTrue(hq.check_l3_algorithm_detail(text), ex_id)
            self.assertTrue(hq.check_l3_no_code_in_prose(text, [v for t in ex["test_cases"] for v in (t["input"], t["expected_output"])]), ex_id)
            self.assertIn("Ý tưởng", text)
            for k in "1234":
                self.assertIn(f"**Bước {k}:**", text, ex_id)

    def test_skeleton_still_fails_tests_is_valid_python_and_todos_labeled(self):
        import hint_quality_checks as hq
        for ex_id, code in self.CASES:
            ex, tr, text = self.run_case(ex_id, code)
            block = hq.skeleton_block(text)
            ast.parse(block)
            self.assertTrue(hq.check_l3_skeleton_not_passing(text, ex["test_cases"]), ex_id)
            self.assertTrue(hq.check_l3_todo_labeled(text), ex_id)

    def test_core_expressions_do_not_leak(self):
        leaks = [r"range\(\s*1\s*,\s*n\s*\+\s*1\s*\)", r"n\s*\*\s*\(\s*n\s*\+\s*1\s*\)\s*//\s*2", r"\[\s*::\s*-1\s*\]", r"sum\(\s*range", r"int\(n\s*\*\*\s*0\.5\)"]
        import hint_quality_checks as hq
        for ex_id, code in self.CASES:
            _, _, text = self.run_case(ex_id, code)
            self.assertEqual(hq.leaked_core(text, code, leaks), [], ex_id)

    def test_instructor_notes_are_used_and_labelled(self):
        ex, tr, text = self.run_case(*self.CASES[1])
        self.assertIn("dựa trên ghi chú của giảng viên", text)
        plain = {k: v for k, v in SEED["ex_02_prime_check"].items() if k != "algorithm_notes"}
        from mcp_server.sandbox import run_test_cases
        code = self.CASES[1][1]
        text2 = build_offline_hint(plain, code, run_test_cases(code, plain["test_cases"]), {"valid": True}, 3)
        self.assertIn("thuật toán tổng quát theo dạng bài", text2)

    def test_prompt_level3_gets_notes_but_levels_1_2_do_not(self):
        from backend.llm_service import build_scaffolding_prompt
        ex = SEED["ex_02_prime_check"]
        marker = "kết luận NO ngay"
        self.assertIn(marker, ex["algorithm_notes"])
        code = self.CASES[1][1]
        from mcp_server.sandbox import run_test_cases
        tr = run_test_cases(code, ex["test_cases"])
        for level in (1, 2):
            self.assertNotIn(marker, build_scaffolding_prompt(ex, code, tr, {"valid": True}, level), level)
        p3 = build_scaffolding_prompt(ex, code, tr, {"valid": True}, 3)
        self.assertIn("THUẬT TOÁN NỀN", p3)
        self.assertIn(marker, p3)


@unittest.skipUnless(os.environ.get("PYTUTOR_DB_PATH"), "cần DB tạm (PYTUTOR_DB_PATH)")
class AlgorithmNotesApiTests(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from backend.auth import create_token
        from backend.main import app
        self.client = TestClient(app)
        self.client.__enter__()
        self.h = lambda u, r: {"Authorization": f"Bearer {create_token(u, r, u)}"}
        self.ex_id = "ex_01_sum_1_to_n"

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def test_student_never_sees_notes_but_instructor_does(self):
        stu = self.client.get(f"/api/exercises/{self.ex_id}", headers=self.h("student", "student")).json()
        self.assertFalse(stu.get("algorithm_notes"))
        self.assertNotIn("bộ cộng dồn", json.dumps(stu, ensure_ascii=False))
        ins = self.client.get(f"/api/exercises/{self.ex_id}", headers=self.h("gv_tran", "instructor")).json()
        self.assertTrue(ins.get("algorithm_notes"))

    def test_ask_ai_level3_uses_notes_and_response_does_not_leak_field(self):
        r = self.client.post("/api/submit", headers=self.h("student", "student"), json={
            "exercise_id": self.ex_id, "code": "n = int(input())\ntong = 0\nfor i in range(1, n):\n    tong += i\nprint(tong)\n",
            "hint_level": 3, "action_type": "ask_ai", "session_id": "student"})
        self.assertEqual(r.status_code, 200, r.text)
        body = r.json()
        self.assertNotIn("algorithm_notes", body)
        self.assertIn("Bước 3", body["tutor_hint"])
        self.assertNotRegex(body["tutor_hint"], r"range\(\s*1\s*,\s*n\s*\+\s*1\s*\)")

    def test_instructor_can_save_notes_and_limit_is_enforced(self):
        payload = {"id": "ex_v512_notes", "title": "Bài thử v5.12", "difficulty": "Dễ", "category": "Vòng lặp",
                   "description": "### Mô tả\nTest", "starter_code": "n = int(input())\n",
                   "test_cases": [{"input": "1\n", "expected_output": "1", "description": "t"}],
                   "algorithm_notes": "Duyệt các số rồi cộng dồn."}
        r = self.client.post("/api/instructor/exercises", headers=self.h("gv_tran", "instructor"), json=payload)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["algorithm_notes"], "Duyệt các số rồi cộng dồn.")
        too_long = dict(payload, id="ex_v512_long", algorithm_notes="x" * 3001)
        self.assertEqual(self.client.post("/api/instructor/exercises", headers=self.h("gv_tran", "instructor"), json=too_long).status_code, 422)


if __name__ == "__main__":
    unittest.main()
