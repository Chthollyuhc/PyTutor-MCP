"""Sinh evaluation/prompt_golden_v510.json từ mã HIỆN TẠI (trước khi đổi nội dung prompt)."""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
from mcp_server.exercises_data import EXERCISES
from mcp_server.sandbox import run_test_cases
from mcp_server.ast_analyzer import analyze_code_ast
from backend.adaptive_policy import select_hint_strategy, is_blank_attempt
from backend.llm_service import build_scaffolding_prompt

ROOT = Path(".").resolve()
ex = {e["id"]: e for e in EXERCISES}
sc = json.loads((ROOT/"evaluation/hint_scenarios.json").read_text(encoding="utf-8"))["scenarios"]
cases = []
SM = {"total_submissions": 4, "summary": "Đã thử 3 bài, thường cần gợi ý Mức 2.", "average_hint_level": 1.7}
for s in sc:
    e = ex[s["exercise"]]
    tr = run_test_cases(s["code"], e["test_cases"])
    ast_a = analyze_code_ast(s["code"])
    hist = [{"hint_level": h["hint_level"], "all_passed": False, "passed": h["passed"], "total": h["total"], "timestamp": "2026-11-20 10:00:00",
             "action_type": "ask_ai", "tutor_hint": h["tutor_hint"], "code": h["code"]} for h in s.get("history", [])]
    for lvl in s["levels"] if s["id"] in ("D03","D09","D10") else (1, 2, 3):
        no_code = is_blank_attempt(s["code"], e.get("starter_code"))
        strat = select_hint_strategy(lvl, tr, hist, None, exercise_id=s["exercise"], no_code=no_code)
        cases.append({"name": f"{s['id']}_L{lvl}", "exercise_id": s["exercise"], "code": s["code"], "test_results": tr,
                      "ast_analysis": ast_a, "hint_level": lvl, "attempt_history": hist, "student_model": None, "adaptive_strategy": strat})
# biến thể có student_model + chiến lược có điều chỉnh
d3 = next(s for s in sc if s["id"] == "D03"); e = ex[d3["exercise"]]
tr = run_test_cases(d3["code"], e["test_cases"]); ast_a = analyze_code_ast(d3["code"])
strat = select_hint_strategy(2, tr, [], None, exercise_id=d3["exercise"])
strat = dict(strat, granularity="fine", adaptations=[{"code": "granularity_fine", "reason_vi": "x", "context": {}},
             {"code": "bridge_from_mastered", "reason_vi": "y", "context": {"kc_label": "Vòng lặp", "exercise_title": "Bài A"}}],
             learner_signals={"exercise_kcs": [{"kc": "loops", "label_vi": "Vòng lặp", "state": "developing", "others_attempted": 2, "sufficient": True}],
                              "error_class": "wrong_output"}, diagnosis_focus="wrong_output")
cases.append({"name": "VAR_model_L2", "exercise_id": d3["exercise"], "code": d3["code"], "test_results": tr, "ast_analysis": ast_a,
              "hint_level": 2, "attempt_history": [], "student_model": SM, "adaptive_strategy": strat})
TR = {"ok": True, "input": "1", "line_counts": {1: 1, 2: 1, 3: 1, 5: 1}, "final_locals": {"n": "1", "tong": "0"}}
cases.append({"name": "VAR_trace_L2", "exercise_id": d3["exercise"], "code": d3["code"], "test_results": tr, "ast_analysis": ast_a,
              "hint_level": 2, "attempt_history": [], "student_model": None, "adaptive_strategy": select_hint_strategy(2, tr, [], None, exercise_id=d3["exercise"]), "trace": TR})
cases.append({"name": "VAR_trace_L3", "exercise_id": d3["exercise"], "code": d3["code"], "test_results": tr, "ast_analysis": ast_a,
              "hint_level": 3, "attempt_history": [], "student_model": None, "adaptive_strategy": select_hint_strategy(3, tr, [], None, exercise_id=d3["exercise"]), "trace": TR})
for c in cases:
    c["expected_prompt"] = build_scaffolding_prompt(
        exercise=ex[c["exercise_id"]], code=c["code"], test_results=c["test_results"], ast_analysis=c["ast_analysis"],
        hint_level=c["hint_level"], attempt_history=c["attempt_history"], student_model=c["student_model"],
        adaptive_strategy=c["adaptive_strategy"], trace=c.get("trace"))
out = {"version": "1", "note": "Prompt vàng v5.10 SAU khi đổi nội dung (bằng chứng theo mức, lịch sử gợi ý, dữ liệu không tin cậy). Bản trước khi đổi đã khớp từng ký tự ở commit ff7a550.", "cases": cases}
(ROOT/"evaluation/prompt_golden_v510.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(cases), "ca;", sum(len(c["expected_prompt"]) for c in cases), "ký tự prompt")
