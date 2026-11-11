"""Offline deterministic replay for Phase 17; uses synthetic fixtures only."""
import json
from backend.adaptive_policy import select_hint_strategy

CASES = [
    {"id":"empty", "level":1, "tests":{"results":[]}, "history":[], "model":{}, "expected":"conceptual_start"},
    {"id":"syntax", "level":1, "tests":{"results":[{"status":"ERROR"}]}, "history":[], "model":{}, "expected":"failed_case_diagnosis"},
    {"id":"logic", "level":2, "tests":{"results":[{"status":"FAIL"}]}, "history":[], "model":{}, "expected":"failed_case_diagnosis"},
    {"id":"repeat", "level":2, "tests":{"results":[{"status":"FAIL"}]}, "history":[{"hint_level":1},{"hint_level":2}], "model":{}, "expected":"recurring_difficulty"},
    {"id":"recovery", "level":2, "tests":{"results":[{"status":"FAIL"}]}, "history":[{"hint_level":1}], "model":{"analytics_metrics":{"distinct_exercises_attempted":2,"autonomy_score":65,"first_try_pass_rate":50}}, "expected":"failed_case_diagnosis"},
    {"id":"passed", "level":1, "tests":{"all_passed":True,"results":[]}, "history":[], "model":{}, "expected":"solution_review"},
]

def run():
    adaptive_ok = baseline_ok = safe_level = evidence_ok = 0
    rows = []
    for case in CASES:
        result = select_hint_strategy(case["level"], case["tests"], case["history"], case["model"])
        baseline = "solution_review" if case["tests"].get("all_passed") else "conceptual_start"
        adaptive_ok += result["strategy"] == case["expected"]
        baseline_ok += baseline == case["expected"]
        safe_level += result["requested_level"] == case["level"]
        evidence_ok += bool(result["evidence"]) == bool(case["history"] or case["tests"].get("results") or case["model"].get("analytics_metrics"))
        rows.append({"case":case["id"],"baseline":baseline,"adaptive":result["strategy"],"expected":case["expected"],"evidence":result["evidence"],"data_status":result["data_status"],"requested_level_preserved":result["requested_level"]==case["level"]})
    return {"scope":"synthetic technical replay; not a learning-outcome study", "cases":len(CASES),
            "adaptive_correct":adaptive_ok,"baseline_correct":baseline_ok,"requested_level_preserved":safe_level,
            "evidence_consistent":evidence_ok,"details":rows}

if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
