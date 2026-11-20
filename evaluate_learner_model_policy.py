"""Replay hành vi chính sách thích ứng dựa trên mô hình người học v3 (offline, tất định, không LLM).

Phạm vi: policy-behaviour replay; not a learning-outcome study. Kết quả CHỈ cho biết mô hình người học làm thay đổi
quyết định/văn bản phản hồi của chính sách như thiết kế, KHÔNG cho biết sinh viên học tốt hơn.

Cách chạy:  py evaluate_learner_model_policy.py [--json]
Hồ sơ nằm ở evaluation/learner_profiles.json: mỗi hồ sơ là chuỗi sự kiện được chèn vào DB TẠM, rồi đi qua
compute_student_model + select_hint_strategy. Nếu PYTUTOR_DB_PATH chưa đặt, script tự tạo DB tạm; không bao giờ dùng pytutor.db.
Thoát mã 1 nếu mức Level không được giữ 100%, bằng chứng không nhất quán, hoặc cổng dữ liệu mở sai.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_TMP_DIR = None
if not os.environ.get("PYTUTOR_DB_PATH"):
    _TMP_DIR = tempfile.mkdtemp(prefix="pytutor_eval_lm_")
    os.environ["PYTUTOR_DB_PATH"] = str(Path(_TMP_DIR) / "eval.db")
os.environ.setdefault("PYTUTOR_KNOWLEDGE_DB_PATH", str(Path(tempfile.gettempdir()) / "pytutor_eval_lm_kb.sqlite3"))
os.environ["PYTUTOR_DISABLE_LLM"] = "1"
if Path(os.environ["PYTUTOR_DB_PATH"]).expanduser().resolve() == (ROOT / "pytutor.db").resolve():
    sys.exit("Từ chối chạy: PYTUTOR_DB_PATH trỏ tới pytutor.db thật. Dùng DB tạm.")

from backend.adaptive_policy import select_hint_strategy  # noqa: E402
from backend.database import compute_student_model, get_db_connection, init_db  # noqa: E402
from backend.llm_service import build_pass_feedback, generate_rule_based_fallback  # noqa: E402
from pytutor_shared.learner_model import assign_kcs, legacy_error_class  # noqa: E402

PROFILES_PATH = ROOT / "evaluation" / "learner_profiles.json"
SCOPE = "policy-behaviour replay; not a learning-outcome study"
EXERCISE = {"title": "Bài mục tiêu", "description": ""}
AST = {"valid": True, "has_loops": True, "has_accumulator": False, "structural_summary": "Có 1 vòng lặp for."}
FAIL = {"all_passed": False, "passed_tests": 1, "total_tests": 3, "summary": "1/3", "results": [
    {"test_idx": 1, "status": "PASS", "input": "4", "expected_output": "Chan", "actual_output": "Chan"},
    {"test_idx": 2, "status": "FAIL", "description": "Số lẻ", "input": "7", "expected_output": "Le", "actual_output": "le"}]}
SYNTAX = {"all_passed": False, "passed_tests": 0, "total_tests": 3,
          "results": [{"test_idx": 1, "status": "SYNTAX_ERROR", "error_message": "invalid syntax"}]}
PASSED = {"all_passed": True, "passed_tests": 3, "total_tests": 3, "results": []}
HIST = [{"hint_level": 1, "action_type": "submit"}, {"hint_level": 2, "action_type": "ask_ai"}]
# 5 trạng thái của bài mục tiêu: (tên, kết quả kiểm thử, lịch sử bài này, ast)
STATES = [
    ("passed", PASSED, [], AST),
    ("fail_first", FAIL, [], AST),
    ("fail_repeat", FAIL, HIST, AST),
    ("syntax_error", SYNTAX, [], {"valid": False}),
    ("no_results", {"results": []}, [], AST),
]
LEVELS = (1, 2, 3)
ERROR_ORDER = ["syntax", "runtime", "timeout", "logic_partial", "logic_none", "zero_pass"]


def load_profiles() -> dict:
    return json.loads(PROFILES_PATH.read_text(encoding="utf-8"))


def insert_profile(user: str, profile: dict) -> None:
    conn = get_db_connection()
    try:
        for i, ev in enumerate(profile["events"]):
            ts = f"2026-01-01 08:{i // 60:02d}:{i % 60:02d}"
            if ev["kind"] == "run":
                conn.execute("INSERT INTO practice_runs(username,exercise_id,passed_tests,total_tests,all_passed,timestamp) VALUES(?,?,?,?,?,?)",
                             (user, ev["ex"], ev["passed"], ev["total"], int(ev["passed"] == ev["total"]), ts))
                continue
            if ev["kind"] == "ask":
                row = (user, ev["ex"], "x=1", ev.get("hint", 1), 0, 3, 0, "ask_ai", "", ts)
            else:
                row = (user, ev["ex"], "x=1", ev.get("hint", 1), ev["passed"], ev["total"], int(ev["passed"] == ev["total"]),
                       "submit", "", ts)
            cur = conn.execute(
                "INSERT INTO submissions(session_id,exercise_id,code,hint_level,passed_tests,total_tests,all_passed,action_type,llm_source,timestamp) "
                "VALUES(?,?,?,?,?,?,?,?,?,?)", row)
            if ev["kind"] == "submit" and ev.get("error_class"):
                conn.execute("INSERT INTO attempt_features(submission_id,error_class,status_counts,ast_flags) VALUES(?,?,?,?)",
                             (cur.lastrowid, ev["error_class"], "{}", "{}"))
        conn.commit()
    finally:
        conn.close()


def exercise_categories() -> dict:
    conn = get_db_connection()
    try:
        return {r["id"]: r["category"] for r in conn.execute("SELECT id, category FROM exercises")}
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Bộ kiểm độc lập: tính lại các mã điều chỉnh kỳ vọng thẳng từ sự kiện thô (không dùng learner_model/policy)
# ---------------------------------------------------------------------------
def expected_codes(profile: dict, state: tuple, cats: dict) -> set[str]:
    name, tests, history, _ = state
    target = profile["target"]
    subs: dict[str, list[dict]] = {}
    asks: dict[str, int] = {}
    for ev in profile["events"]:
        if ev["kind"] == "submit":
            subs.setdefault(ev["ex"], []).append(ev)
        elif ev["kind"] == "ask":
            asks[ev["ex"]] = max(asks.get(ev["ex"], 0), ev.get("hint", 1))

    def info(ex: str) -> dict:
        s = subs[ex]
        failed = [e for e in s if e["passed"] != e["total"]]
        passed = any(e["passed"] == e["total"] for e in s)
        classes = [e.get("error_class") or legacy_error_class(e["passed"], False) for e in failed]
        dom = sorted(set(classes), key=lambda c: (-classes.count(c), ERROR_ORDER.index(c) if c in ERROR_ORDER else 99, c))[0] if classes else None
        if passed:
            first = next(e for e in s if e["passed"] == e["total"])
            auto = 100 if first.get("hint", 1) == 1 else (70 if first.get("hint") == 2 else 40)
        else:
            auto = round(max(e["passed"] / max(1, e["total"]) for e in s) * 40)
        status = "passed" if passed else ("struggling" if len(failed) >= 2 else "attempted")
        return {"status": status, "dom": dom, "auto": auto}

    infos = {ex: info(ex) for ex in subs}

    def struggling(kc: str, i: dict) -> bool:
        if i["status"] != "struggling":
            return False
        return i["dom"] in ("syntax", "runtime", "timeout", "zero_pass") if kc == "io_format" else True

    def kc_state(kc: str, exes: list[str]) -> str:
        det = [infos[e] for e in exes]
        if not det:
            return "no_evidence"
        if any(struggling(kc, d) for d in det):
            return "struggling"
        passed = [d for d in det if d["status"] == "passed"]
        if len(passed) >= 2 and sum(d["auto"] for d in passed) / len(passed) >= 70:
            return "secure"
        return "developing"

    kcs_of = lambda ex: assign_kcs(cats.get(ex))  # noqa: E731
    codes: set[str] = set()
    engaged = set(asks) | set(subs)
    n_ge2 = sum(1 for e in engaged if asks.get(e, 0) >= 2)
    reliance = "unknown" if len(engaged) < 2 else (
        "high" if n_ge2 >= 3 and n_ge2 / len(engaged) >= 0.5 else ("medium" if n_ge2 >= 1 and n_ge2 / len(engaged) >= 0.25 else "low"))
    failed_now = bool(tests.get("results")) and not tests.get("all_passed")
    passed_now = bool(tests.get("all_passed"))
    cur_class = None
    if failed_now:
        statuses = [r.get("status") for r in tests["results"]]
        cur_class = ("syntax" if "SYNTAX_ERROR" in statuses else "timeout" if "TIMEOUT" in statuses else
                     "runtime" if "RUNTIME_ERROR" in statuses else "logic_partial" if tests.get("passed_tests", 0) > 0 else "logic_none")

    if passed_now:
        if reliance == "high":
            codes.add("independence_check")
    elif len(history) >= 2:
        codes.add("same_exercise_repeat")
    else:
        views = []
        for kc in kcs_of(target):
            others = [e for e in subs if e != target and kc in kcs_of(e)]
            views.append((kc, others))
        suff = [(kc, o) for kc, o in views if len(o) >= 2]
        if failed_now and any(struggling(kc, infos[e]) for kc, o in suff for e in o):
            codes.add("concept_recurring_difficulty")
        elif failed_now:
            for kc, o in suff:
                classes = [infos[e]["dom"] for e in o if infos[e]["dom"] and infos[e]["status"] != "passed"]
                dom = sorted(set(classes), key=lambda c: (-classes.count(c), ERROR_ORDER.index(c) if c in ERROR_ORDER else 99, c))[0] if classes else None
                if dom and dom == cur_class:
                    codes.add("repeated_error_type")
                    break
        elif not passed_now and not failed_now:
            if any(kc_state(kc, o) == "secure" and any(infos[e]["status"] == "passed" for e in o) for kc, o in suff):
                codes.add("bridge_from_mastered")

    distinct = len(subs)
    autos = [infos[e]["auto"] for e in subs]
    autonomy = round(sum(autos) / max(1, len(autos))) if autos else None
    if not passed_now and distinct >= 3:
        states = {}
        for kc in ("io_format", "conditional", "loop", "accumulator", "string", "recursion"):
            exes = [e for e in subs if kc in kcs_of(e)]
            states[kc] = (kc_state(kc, exes), len(exes))
        evid = {k: v for k, v in states.items() if v[0] != "no_evidence"}
        if reliance == "high" or (autonomy is not None and autonomy < 45):
            codes.add("granularity_fine")
        elif (autonomy is not None and autonomy >= 80 and sum(1 for v in evid.values() if v[0] == "secure") >= 2
              and not any(v[0] == "struggling" for v in evid.values())
              and all(v[0] == "secure" for v in evid.values() if v[1] >= 2)):
            codes.update({"granularity_coarse", "self_check_first"})
    return codes


def run() -> dict:
    init_db()
    cats = exercise_categories()
    spec = load_profiles()
    cells, per_state_pairs = [], {s[0]: set() for s in STATES}
    totals = dict(cells=0, policy_diff=0, level_ok=0, evidence_ok=0, closed_cells=0, closed_ok=0, text_diff=0, text_diff_of_changed=0)
    profile_rows = []
    for profile in spec["profiles"]:
        user = f"evalp_{profile['id']}"
        insert_profile(user, profile)
        model = compute_student_model(user)
        profile_changed = 0
        for state in STATES:
            name, tests, history, ast = state
            expected = expected_codes(profile, state, cats)
            for level in LEVELS:
                on = select_hint_strategy(level, tests, history, model, exercise_id=profile["target"])
                off = select_hint_strategy(level, tests, history, model, exercise_id=profile["target"], use_learner_model=False)
                pair_on = (on["strategy"], tuple(sorted(on["adaptation_codes"])))
                pair_off = (off["strategy"], tuple(sorted(off["adaptation_codes"])))
                changed = pair_on != pair_off
                if tests.get("all_passed"):
                    text_on = build_pass_feedback(EXERCISE, tests, ast, adaptive_strategy=on)
                    text_off = build_pass_feedback(EXERCISE, tests, ast, adaptive_strategy=off)
                else:
                    text_on = generate_rule_based_fallback(EXERCISE, "x", tests, ast, level, adaptive_strategy=on)
                    text_off = generate_rule_based_fallback(EXERCISE, "x", tests, ast, level, adaptive_strategy=off)
                text_changed = text_on != text_off
                level_ok = on["requested_level"] == level and off["requested_level"] == level
                evidence_ok = set(on["adaptation_codes"]) == expected
                gate_ok = None
                if profile["expected_gate"] == "closed":
                    gate_ok = not (set(on["adaptation_codes"]) - {"same_exercise_repeat"}) and on["model_fields_used"] == []
                    totals["closed_cells"] += 1
                    totals["closed_ok"] += bool(gate_ok)
                totals["cells"] += 1
                totals["policy_diff"] += changed
                totals["level_ok"] += level_ok
                totals["evidence_ok"] += evidence_ok
                totals["text_diff"] += text_changed
                totals["text_diff_of_changed"] += (changed and text_changed)
                profile_changed += changed
                if level == 2:
                    per_state_pairs[name].add(pair_on)
                cells.append({"profile": profile["id"], "state": name, "level": level, "baseline": [pair_off[0], list(pair_off[1])],
                              "adaptive": [pair_on[0], list(pair_on[1])], "policy_changed": changed, "text_changed": text_changed,
                              "level_preserved": level_ok, "evidence_consistent": evidence_ok, "expected_codes": sorted(expected),
                              "gate_correct": gate_ok})
        profile_rows.append({"id": profile["id"], "description": profile["description"], "expected_gate": profile["expected_gate"],
                             "data_status": model["analytics_metrics"]["data_status"],
                             "concept_states": {c["kc"]: c["state"] for c in model["learner_model"]["concepts"]},
                             "hint_reliance": model["learner_model"]["support_profile"]["hint_reliance"],
                             "cells_changed_vs_baseline": profile_changed, "cells": len(STATES) * len(LEVELS)})
    n = totals["cells"]
    changed = totals["policy_diff"]
    return {
        "scope": SCOPE,
        "disclaimer": "Chỉ đo hành vi chính sách trên hồ sơ tổng hợp (offline, không LLM). Không phải nghiên cứu kết quả học tập; không có kết luận về learning gain.",
        "cells": n, "profiles": len(spec["profiles"]), "states": [s[0] for s in STATES], "levels": list(LEVELS),
        "policy_difference_rate": round(changed / n, 3),
        "policy_changed_cells": changed,
        "distinct_strategy_adaptation_pairs_per_state_level2": {k: len(v) for k, v in per_state_pairs.items()},
        "level_preserved": f"{totals['level_ok']}/{n}",
        "evidence_consistency": f"{totals['evidence_ok']}/{n}",
        "gate_correct_on_closed_profiles": f"{totals['closed_ok']}/{totals['closed_cells']}",
        "fallback_text_difference_rate": round(totals["text_diff"] / n, 3),
        "fallback_text_differs_when_policy_changed": f"{totals['text_diff_of_changed']}/{changed}",
        "profile_summary": profile_rows,
        "details": cells,
        "ok": (totals["level_ok"] == n and totals["evidence_ok"] == n and totals["closed_ok"] == totals["closed_cells"]),
    }


def main() -> int:
    try:
        result = run()
    finally:
        if _TMP_DIR:
            shutil.rmtree(_TMP_DIR, ignore_errors=True)
    if "--json" in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Phạm vi: {result['scope']}")
        print(result["disclaimer"])
        print(f"Hồ sơ: {result['profiles']} | trạng thái bài: {len(result['states'])} | mức: {result['levels']} | tổng ô: {result['cells']}")
        print(f"Tỷ lệ chính sách khác baseline (use_learner_model=False): {result['policy_difference_rate']:.1%} ({result['policy_changed_cells']}/{result['cells']})")
        print(f"Số cặp (strategy, adaptations) khác nhau theo trạng thái (Mức 2): {result['distinct_strategy_adaptation_pairs_per_state_level2']}")
        print(f"Giữ nguyên Level yêu cầu: {result['level_preserved']}")
        print(f"Nhất quán bằng chứng (bộ kiểm độc lập tính lại từ sự kiện thô): {result['evidence_consistency']}")
        print(f"Cổng đúng trên hồ sơ no_data/limited: {result['gate_correct_on_closed_profiles']}")
        print(f"Văn bản fallback khác baseline: {result['fallback_text_difference_rate']:.1%}; khi chính sách đổi: {result['fallback_text_differs_when_policy_changed']}")
        for row in result["profile_summary"]:
            print(f"  - {row['id']}: data_status={row['data_status']}, hint_reliance={row['hint_reliance']}, "
                  f"khác baseline {row['cells_changed_vs_baseline']}/{row['cells']} ô")
        print("KẾT QUẢ:", "ĐẠT" if result["ok"] else "KHÔNG ĐẠT")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
