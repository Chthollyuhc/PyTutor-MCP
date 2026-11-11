"""Deterministic, evidence-backed hint strategy selection for Phase 17."""
from __future__ import annotations


def select_hint_strategy(hint_level: int, test_results: dict, attempt_history: list[dict] | None,
                         student_model: dict | None) -> dict:
    history = attempt_history or []
    model = student_model or {}
    metrics = model.get("analytics_metrics") or {}
    evidence: list[str] = []
    if history:
        evidence.append("prior_attempts")
        evidence.append("previous_hint_levels")
    failed = [r for r in (test_results or {}).get("results", []) if r.get("status") != "PASS"]
    if failed:
        evidence.append("failed_test_cases")
    enough = metrics.get("distinct_exercises_attempted", 0) > 0
    if enough and metrics.get("first_try_pass_rate") is not None:
        evidence.append("first_try_pass_rate")
    if enough and metrics.get("autonomy_score") is not None:
        evidence.append("autonomy_score")
    if (test_results or {}).get("all_passed"):
        strategy = "solution_review"
    elif len(history) >= 2:
        strategy = "recurring_difficulty"
    elif failed:
        strategy = "failed_case_diagnosis"
    else:
        strategy = "conceptual_start"
    return {"strategy": strategy, "reason_code": strategy, "evidence": evidence,
            "previous_hint_levels": [int(item.get("hint_level", 1) or 1) for item in history[:3]],
            "data_status": "sufficient" if evidence else "insufficient", "requested_level": hint_level}
