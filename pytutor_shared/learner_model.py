"""Mô hình người học v3: hàm thuần, tất định, không truy cập DB.

Dùng chung cho backend/database.py và mcp_server/storage.py để hai bản compute_student_model
không thể lệch nhau về logic. Không import từ backend hoặc mcp_server.

Giới hạn trung thực: mọi ngưỡng ở đây là quy ước vận hành, chưa hiệu chuẩn bằng dữ liệu thực;
trạng thái kiến thức là mô tả bằng chứng đã quan sát (thứ bậc), không phải ước lượng năng lực (không BKT/IRT).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Optional

MODEL_VERSION = "3"
FEATURE_VERSION = "2"

# ---------------------------------------------------------------------------
# Phân nhóm quá trình học (chuyển từ backend/database.py; ngưỡng là quy ước vận hành, chưa hiệu chuẩn)
# ---------------------------------------------------------------------------
PROCESS_INDEPENDENT_MAX_SUBMITS = 2
PROCESS_RETRY_MIN_RUNS = 5
PROCESS_HINT_ASSISTED_LEVEL = 2
PROCESS_STUCK_MIN_ATTEMPTS = 8
PROCESS_PROGRESS_WINDOW = 5
PROCESS_GROUPS = [
    {"key": "independent_pass", "label": "Đạt độc lập",
     "rule": f"Đã nộp đạt; gợi ý cao nhất trước lần đạt ≤ 1; ≤ {PROCESS_INDEPENDENT_MAX_SUBMITS} lượt nộp và < {PROCESS_RETRY_MIN_RUNS} lượt chạy thử."},
    {"key": "retry_pass", "label": "Đạt sau thử–sửa",
     "rule": f"Đã nộp đạt; gợi ý ≤ 1; > {PROCESS_INDEPENDENT_MAX_SUBMITS} lượt nộp hoặc ≥ {PROCESS_RETRY_MIN_RUNS} lượt chạy thử trước khi đạt."},
    {"key": "hint_pass", "label": "Đạt nhờ gợi ý",
     "rule": f"Đã nộp đạt; mức gợi ý cao nhất trước lần đạt đầu ≥ {PROCESS_HINT_ASSISTED_LEVEL}."},
    {"key": "in_progress", "label": "Đang tiến triển",
     "rule": f"Chưa đạt; số test đạt tốt nhất còn tăng trong {PROCESS_PROGRESS_WINDOW} lượt (chạy thử + nộp) gần nhất, hoặc dưới {PROCESS_STUCK_MIN_ATTEMPTS} lượt."},
    {"key": "stuck", "label": "Mắc kẹt",
     "rule": f"Chưa đạt; ≥ {PROCESS_STUCK_MIN_ATTEMPTS} lượt (chạy thử + nộp) và số test đạt tốt nhất không tăng trong {PROCESS_PROGRESS_WINDOW} lượt gần nhất."},
    {"key": "practice_only", "label": "Chỉ chạy thử",
     "rule": "Có chạy thử hoặc hỏi gợi ý nhưng chưa nộp bài lần nào."},
]
PROCESS_GROUP_KEYS = [g["key"] for g in PROCESS_GROUPS]
PROCESS_LABELS = {g["key"]: g["label"] for g in PROCESS_GROUPS}


def classify_learning_process(events: list[dict[str, Any]]) -> Optional[str]:
    """Phân nhóm quá trình của MỘT cặp sinh viên–bài từ chuỗi sự kiện theo thứ tự thời gian (tất định).

    Mỗi sự kiện: {"kind": "run"|"ask"|"submit", "passed_tests": int, "all_passed": bool, "hint_level": int}.
    Trả về một khóa trong PROCESS_GROUP_KEYS, hoặc None nếu không có sự kiện nào.
    Đây là bằng chứng mô tả cho giảng viên, không phải metric chính thức của sinh viên.
    """
    if not events:
        return None
    submits = [e for e in events if e["kind"] == "submit"]
    if not submits:
        return "practice_only"
    pass_idx = next((i for i, e in enumerate(events) if e["kind"] == "submit" and e.get("all_passed")), None)
    if pass_idx is not None:
        before = events[:pass_idx + 1]
        max_hint = max((int(e.get("hint_level") or 0) for e in before if e["kind"] == "ask"), default=0)
        submit_count = sum(1 for e in before if e["kind"] == "submit")
        run_count = sum(1 for e in before if e["kind"] == "run")
        if max_hint >= PROCESS_HINT_ASSISTED_LEVEL:
            return "hint_pass"
        if submit_count <= PROCESS_INDEPENDENT_MAX_SUBMITS and run_count < PROCESS_RETRY_MIN_RUNS:
            return "independent_pass"
        return "retry_pass"
    attempts = [int(e.get("passed_tests") or 0) for e in events if e["kind"] in ("run", "submit")]
    if len(attempts) < PROCESS_STUCK_MIN_ATTEMPTS:
        return "in_progress"
    earlier, recent = attempts[:-PROCESS_PROGRESS_WINDOW], attempts[-PROCESS_PROGRESS_WINDOW:]
    return "in_progress" if max(recent) > max(earlier) else "stuck"


# ---------------------------------------------------------------------------
# v5.8: dấu chân (chuỗi sự kiện) của một cặp sinh viên–bài. Chỉ đọc và trình bày, không đổi luật nào ở trên.
# ---------------------------------------------------------------------------
PROCESS_EVENT_ORDER = {"run": 0, "ask": 1, "submit": 2}


def process_event_sort_key(ev: dict[str, Any]) -> tuple:
    """Tiêu chí sắp xếp dùng chung với get_class_insights: (timestamp, loại, id)."""
    return (ev.get("timestamp") or "", PROCESS_EVENT_ORDER.get(ev.get("kind"), 9), ev.get("id") or 0)


def build_journey_points(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Dựng dấu chân từ chuỗi sự kiện ĐÃ sắp xếp (hàm thuần, tất định, không DB).

    Mỗi sự kiện: {"kind": "run"|"ask"|"submit", "passed_tests", "total_tests", "all_passed", "hint_level",
    "timestamp", "submission_id", "format_only", "error_class"}. Nhóm quá trình lấy từ chính
    `classify_learning_process`, không có luật mới.
    """
    points: list[dict[str, Any]] = []
    best = -1
    counts = {"run": 0, "ask": 0, "submit": 0}
    first_pass_index: Optional[int] = None
    first_pass_at: Optional[str] = None
    attempts_to_first_pass: Optional[int] = None
    best_total = 0
    for ev in events:
        kind = ev.get("kind")
        if kind not in counts:
            continue
        counts[kind] += 1
        passed = int(ev.get("passed_tests") or 0)
        total = int(ev.get("total_tests") or 0)
        all_passed = bool(ev.get("all_passed"))
        is_new_best = False
        if kind in ("run", "submit"):
            if passed > best:
                is_new_best = best >= 0 or passed > 0
                best = passed
                best_total = total or best_total
        point = {
            "kind": kind, "passed": passed if kind != "ask" else None, "total": total if kind != "ask" else None,
            "hint_level": int(ev.get("hint_level") or 0) if kind == "ask" else None,
            "all_passed": all_passed if kind != "ask" else False,
            "is_new_best": is_new_best, "format_only": bool(ev.get("format_only")),
            "timestamp": ev.get("timestamp"), "submission_id": ev.get("submission_id"),
        }
        points.append(point)
        if kind == "submit" and all_passed and first_pass_index is None:
            first_pass_index = len(points) - 1
            first_pass_at = ev.get("timestamp")
            attempts_to_first_pass = counts["run"] + counts["submit"]
    return {
        "points": points,
        "summary": {
            "group": classify_learning_process(
                [{"kind": e.get("kind"), "passed_tests": e.get("passed_tests"), "all_passed": e.get("all_passed"),
                  "hint_level": e.get("hint_level")} for e in events if e.get("kind") in counts]),
            "counts": counts,
            "best": {"passed": max(best, 0), "total": best_total},
            "first_pass_index": first_pass_index,
            "first_pass_at": first_pass_at,
            "attempts_to_first_pass": attempts_to_first_pass,
        },
    }


# ---------------------------------------------------------------------------
# Đơn vị kiến thức (KC) cố định, gán bằng bảng từ khóa tất định
# ---------------------------------------------------------------------------
KC_DEFINITIONS = [
    {"kc": "io_format", "label_vi": "Nhập/xuất và định dạng", "keywords": []},  # gán cho mọi bài
    {"kc": "conditional", "label_vi": "Rẽ nhánh / điều kiện",
     "keywords": [r"re nhanh", r"dieu kien", r"\bif\b", r"co hieu"]},
    {"kc": "loop", "label_vi": "Vòng lặp",
     "keywords": [r"vong lap", r"\bfor\b", r"\bwhile\b", r"duyet"]},
    {"kc": "accumulator", "label_vi": "Biến tích lũy",
     "keywords": [r"tich luy", r"bien tich", r"accumulat"]},
    {"kc": "string", "label_vi": "Xử lý chuỗi",
     "keywords": [r"chuoi", r"\bstring\b", r"slicing", r"\btext\b", r"van ban"]},
    {"kc": "recursion", "label_vi": "Đệ quy",
     "keywords": [r"de quy", r"recurs"]},
]
KC_KEYS = [d["kc"] for d in KC_DEFINITIONS]
KC_LABELS = {d["kc"]: d["label_vi"] for d in KC_DEFINITIONS}

STATE_NO_EVIDENCE, STATE_DEVELOPING, STATE_STRUGGLING, STATE_SECURE = "no_evidence", "developing", "struggling", "secure"
STATE_LABELS = {
    STATE_NO_EVIDENCE: "Chưa có bằng chứng",
    STATE_DEVELOPING: "Đang hình thành",
    STATE_STRUGGLING: "Đang vướng",
    STATE_SECURE: "Khá vững",
}

THRESHOLDS = {
    "struggling_min_failed_submits": 2,
    "secure_min_passed_exercises": 2,
    "secure_min_avg_autonomy": 70,
    "concept_sufficient_min_exercises": 2,
    "hint_reliance_high_share": 0.5,
    "hint_reliance_high_min_exercises": 3,
    "hint_reliance_medium_share": 0.25,
    "hint_reliance_unknown_below_exercises": 2,
    "fine_granularity_autonomy_below": 45,
    "coarse_granularity_autonomy_min": 80,
    "note": "Quy ước vận hành, chưa hiệu chuẩn bằng dữ liệu thực.",
}

DISCLAIMER = (
    "Đây là mô hình heuristic mô tả bằng chứng đã quan sát từ các lượt nộp chính thức, với ngưỡng quy ước chưa hiệu chuẩn. "
    "Nó không phải điểm năng lực, không phải kết luận về hiệu quả học tập, và có thể sai khi dữ liệu còn ít. "
    "Số lần hỏi gợi ý, chạy thử và nhóm quá trình chỉ là mô tả quá trình, không ảnh hưởng đến sao hay chỉ số chính thức."
)


def _fold(text: Any) -> str:
    s = unicodedata.normalize("NFD", str(text or "").lower().replace("đ", "d"))
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")


def assign_kcs(category: Any = "", module_name: Any = "", skill_tag: Any = "", exercise_category: Any = "", kc_definitions: Optional[list[dict]] = None) -> list[str]:
    """Gán KC bằng từ khóa trên category/module_name/skill_tag/exercise_category (đã bỏ dấu); io_format luôn có. Tất định.
    Nếu truyền kc_definitions thì dùng danh sách đó, ngược lại dùng KC_DEFINITIONS mặc định.
    """
    haystack = " | ".join(_fold(x) for x in (category, module_name, skill_tag, exercise_category))
    kcs = ["io_format"]
    defs = kc_definitions if kc_definitions is not None else KC_DEFINITIONS
    for d in defs:
        if d.get("kc") == "io_format":
            continue
        if any(re.search(p, haystack) for p in d.get("keywords", [])):
            kcs.append(d["kc"])
    return kcs


# ---------------------------------------------------------------------------
# Đặc trưng mỗi lượt (Phase A)
# ---------------------------------------------------------------------------
ERROR_CLASSES = ["passed", "syntax", "runtime", "timeout", "logic_partial", "logic_none"]
_ERROR_ORDER = ["syntax", "runtime", "timeout", "logic_partial", "logic_none", "zero_pass"]


def normalize_output_for_diagnosis(text: Any) -> str:
    """Chuẩn hóa đầu ra để CHẨN ĐOÁN sai định dạng: casefold + gộp khoảng trắng + strip.

    Chỉ dùng để gắn nhãn mô tả (bài vẫn chưa đạt, không đổi chấm điểm, sao hay error_class).
    """
    return " ".join(str(text or "").casefold().split())


def summarize_attempt_features(test_results: Optional[dict], ast_analysis: Optional[dict] = None) -> dict:
    """Rút đặc trưng nhỏ gọn của một lượt: loại lỗi (từ trạng thái test + AST) và cờ cấu trúc."""
    tr = test_results or {}
    results = tr.get("results") or []
    counts: dict[str, int] = {}
    for r in results:
        st = str(r.get("status") or "UNKNOWN")
        counts[st] = counts.get(st, 0) + 1
    failed_tests: list[int] = []
    format_mismatch_tests: list[int] = []
    for r in results:
        st = str(r.get("status") or "")
        if st in ("PASS", "SKIPPED"):
            continue
        idx = r.get("test_idx")
        if idx is None:
            continue
        failed_tests.append(int(idx))
        if st == "FAIL" and normalize_output_for_diagnosis(r.get("actual_output")) == normalize_output_for_diagnosis(r.get("expected_output")):
            format_mismatch_tests.append(int(idx))
    ast = ast_analysis or {}
    passed = int(tr.get("passed_tests") or counts.get("PASS", 0))
    if tr.get("all_passed"):
        error_class = "passed"
    elif ast.get("valid") is False or counts.get("SYNTAX_ERROR"):
        error_class = "syntax"
    elif counts.get("TIMEOUT"):
        error_class = "timeout"
    elif counts.get("RUNTIME_ERROR") or counts.get("SYSTEM_ERROR"):
        error_class = "runtime"
    elif passed > 0:
        error_class = "logic_partial"
    else:
        error_class = "logic_none"
    flags = {
        "has_loops": bool(ast.get("has_loops")),
        "has_accumulator": bool(ast.get("has_accumulator")),
        "has_recursion": bool(ast.get("has_recursion")),
        "has_return": bool(ast.get("has_return")),
        "line_count": int(ast.get("line_count") or 0),
    }
    format_only = bool(failed_tests) and len(format_mismatch_tests) == len(failed_tests)
    return {"error_class": error_class, "status_counts": counts, "ast_flags": flags, "feature_version": FEATURE_VERSION,
            "failed_tests": failed_tests, "format_mismatch_tests": format_mismatch_tests, "format_only": format_only}


def legacy_error_class(passed_tests: int, all_passed: bool) -> str:
    """Heuristic cho lượt cũ chưa có đặc trưng: chỉ phân biệt được đạt/lệch một phần/không đạt test nào."""
    if all_passed:
        return "passed"
    return "logic_partial" if int(passed_tests or 0) > 0 else "zero_pass"


# ---------------------------------------------------------------------------
# Suy ra mô hình người học
# ---------------------------------------------------------------------------
def _ts_key(ev: dict) -> tuple:
    return (ev.get("timestamp") or "", ev.get("order", 0), ev.get("id", 0))


def _dominant(classes: list[str]) -> Optional[str]:
    if not classes:
        return None
    return sorted(set(classes), key=lambda c: (-classes.count(c), _ERROR_ORDER.index(c) if c in _ERROR_ORDER else 99, c))[0]


def dominant_class(classes: list[str]) -> Optional[str]:
    return _dominant(classes)


def is_struggling_detail(kc: str, item: dict) -> bool:
    """Một bài (đã có chi tiết) có tính là 'đang vướng' đối với KC này không."""
    if item.get("status") != "struggling":
        return False
    if kc == "io_format":
        # io_format gán cho mọi bài: chỉ coi là "vướng" khi lỗi chủ yếu là cú pháp/runtime/hết giờ/không đạt test nào,
        # để không lặp lại trạng thái vướng của mọi KC khác.
        return item.get("dominant_error_class") in ("syntax", "runtime", "timeout", "zero_pass")
    return True


def derive_learner_model(
    *,
    exercises: list[dict],
    submissions: list[dict],
    asks: list[dict],
    runs: list[dict],
    features: dict,
    autonomy_by_exercise: dict,
    analytics_data_status: str = "no_data",
    kc_definitions: Optional[list[dict]] = None,
) -> dict:
    """Suy ra learner_model v3 từ dữ liệu thô đã đọc (không DB).

    exercises: [{id,title,category,module_name,skill_tag}] của phạm vi hiện tại.
    submissions: lượt `submit` chính thức [{id,exercise_id,passed_tests,total_tests,all_passed,hint_level,timestamp}].
    asks: lượt `ask_ai` (đã bỏ Exam-Mode-Guard) [{id,exercise_id,hint_level,timestamp}].
    runs: lượt chạy thử [{id,exercise_id,passed_tests,all_passed,timestamp}].
    features: {submission_id: {error_class, ...}} (có thể thiếu với lượt cũ).
    autonomy_by_exercise: {exercise_id: 0..100} (đã tính trong compute_student_model).
    kc_definitions: danh sách KC động (nếu None sẽ dùng KC_DEFINITIONS mặc định).
    Trạng thái KC và hồ sơ lỗi chỉ dùng `submissions`; asks/runs chỉ vào support_profile và process_by_exercise.
    """
    defs = kc_definitions if kc_definitions is not None else KC_DEFINITIONS
    meta = {e["id"]: e for e in exercises}
    exercise_kcs = {e["id"]: assign_kcs(e.get("category"), e.get("module_name"), e.get("skill_tag"), e.get("exercise_category"), kc_definitions=defs) for e in exercises}
    by_ex: dict[str, list[dict]] = {}
    for s in submissions:
        by_ex.setdefault(s["exercise_id"], []).append(s)

    def sub_error_class(sub: dict) -> str:
        feat = features.get(sub["id"])
        if feat and feat.get("error_class"):
            return feat["error_class"]
        return legacy_error_class(sub.get("passed_tests", 0), bool(sub.get("all_passed")))

    # Chi tiết theo bài (chỉ submit)
    ex_detail: dict[str, dict] = {}
    for eid, subs in by_ex.items():
        failed = [s for s in subs if not s.get("all_passed")]
        passed = any(s.get("all_passed") for s in subs)
        dominant = _dominant([sub_error_class(s) for s in failed])
        status = "passed" if passed else (
            "struggling" if len(failed) >= THRESHOLDS["struggling_min_failed_submits"] else "attempted")
        ex_detail[eid] = {
            "exercise_id": eid, "title": (meta.get(eid) or {}).get("title") or eid, "status": status,
            "submits": len(subs), "failed_submits": len(failed), "dominant_error_class": dominant,
            "autonomy": autonomy_by_exercise.get(eid),
        }

    concepts = []
    for d in defs:
        kc = d["kc"]
        label_vi = d.get("label_vi") or KC_LABELS.get(kc, kc)
        details = [ex_detail[e] for e in ex_detail if kc in exercise_kcs.get(e, ["io_format"])]
        n = len(details)
        struggling = [x for x in details if is_struggling_detail(kc, x)]
        passed = [x for x in details if x["status"] == "passed"]
        autos = [x["autonomy"] for x in passed if x["autonomy"] is not None]
        avg_auto = (sum(autos) / len(autos)) if autos else None
        if n == 0:
            state = STATE_NO_EVIDENCE
            why = "Chưa có lượt nộp chính thức nào ở bài thuộc nhóm này."
        elif struggling:
            state = STATE_STRUGGLING
            why = (f"Có {len(struggling)} bài thuộc nhóm này với từ {THRESHOLDS['struggling_min_failed_submits']} lượt nộp chưa đạt "
                   f"mà chưa giải được: {', '.join(x['title'] for x in struggling[:3])}.")
        elif (len(passed) >= THRESHOLDS["secure_min_passed_exercises"] and avg_auto is not None
              and avg_auto >= THRESHOLDS["secure_min_avg_autonomy"]):
            state = STATE_SECURE
            why = (f"Đã nộp đạt {len(passed)} bài thuộc nhóm này, chỉ số tự lực trung bình {round(avg_auto)}/100, "
                   "chưa có bài nào đang vướng.")
        else:
            state = STATE_DEVELOPING
            why = (f"Đã nộp {n} bài thuộc nhóm này, đạt {len(passed)}; chưa đủ điều kiện để coi là khá vững "
                   f"(cần ≥ {THRESHOLDS['secure_min_passed_exercises']} bài đạt với tự lực trung bình ≥ {THRESHOLDS['secure_min_avg_autonomy']}).")
        unresolved = [x["dominant_error_class"] for x in details if x["dominant_error_class"] and x["status"] != "passed"]
        everything = [x["dominant_error_class"] for x in details if x["dominant_error_class"]]
        concepts.append({
            "kc": kc, "label_vi": label_vi, "state": state, "state_label_vi": STATE_LABELS[state],
            "exercises": [x["exercise_id"] for x in details],
            "exercise_details": details,
            "evidence_count": sum(x["submits"] for x in details),
            "dominant_error_class": _dominant(unresolved or everything),
            "data_status": "no_data" if n == 0 else (
                "limited" if n < THRESHOLDS["concept_sufficient_min_exercises"] else "sufficient"),
            "explanation": why,
        })

    # Hồ sơ lỗi (chỉ submit)
    error_counts: dict[str, int] = {}
    for s in submissions:
        if s.get("all_passed"):
            continue
        c = sub_error_class(s)
        error_counts[c] = error_counts.get(c, 0) + 1
    with_feature = sum(1 for s in submissions if (features.get(s["id"]) or {}).get("error_class"))
    coverage = round(with_feature / len(submissions) * 100, 1) if submissions else 0.0
    error_profile = {
        "counts": error_counts, "total_failed_submits": sum(error_counts.values()),
        "dominant_error_class": (sorted(error_counts, key=lambda c: (-error_counts[c], c))[0] if error_counts else None),
        "feature_coverage_percent": coverage,
        "basis": "Chỉ các lượt nộp chính thức. Lượt cũ chưa có đặc trưng được phân loại thô (logic_partial / zero_pass).",
    }

    # Hồ sơ hỗ trợ (ask_ai) - mô tả quá trình, không vào chỉ số chính thức
    max_ask: dict[str, int] = {}
    for a in asks:
        max_ask[a["exercise_id"]] = max(max_ask.get(a["exercise_id"], 0), int(a.get("hint_level") or 1))
    engaged = set(max_ask) | set(by_ex)
    n_ge2 = sum(1 for e in engaged if max_ask.get(e, 0) >= 2)
    share = round(n_ge2 / len(engaged), 3) if engaged else None
    if len(engaged) < THRESHOLDS["hint_reliance_unknown_below_exercises"]:
        reliance = "unknown"
    elif n_ge2 >= THRESHOLDS["hint_reliance_high_min_exercises"] and share >= THRESHOLDS["hint_reliance_high_share"]:
        reliance = "high"
    elif n_ge2 >= 1 and share >= THRESHOLDS["hint_reliance_medium_share"]:
        reliance = "medium"
    else:
        reliance = "low"
    support_profile = {
        "label": "descriptive_process", "ask_ai_count": len(asks), "exercises_engaged": len(engaged),
        "exercises_with_hint_ge2": n_ge2, "share_hint_ge2": share, "hint_reliance": reliance,
        "explanation": ("Chưa đủ bài để nhận xét mức dùng gợi ý." if reliance == "unknown" else
                        f"{n_ge2}/{len(engaged)} bài đã xin gợi ý từ Mức 2 trở lên (mô tả quá trình, không tính vào sao)."),
    }

    # Nhóm quá trình theo bài (ask + run + submit)
    events: dict[str, list[dict]] = {}
    for r in runs:
        events.setdefault(r["exercise_id"], []).append({**r, "kind": "run", "order": 0})
    for a in asks:
        events.setdefault(a["exercise_id"], []).append({**a, "kind": "ask", "order": 1})
    for s in submissions:
        events.setdefault(s["exercise_id"], []).append({**s, "kind": "submit", "order": 2})
    process_by_exercise = []
    for eid in sorted(events):
        group = classify_learning_process(sorted(events[eid], key=_ts_key))
        if group:
            process_by_exercise.append({"exercise_id": eid, "title": (meta.get(eid) or {}).get("title") or eid,
                                        "group": group, "label_vi": PROCESS_LABELS[group], "label": "descriptive_process"})

    return {
        "model_version": MODEL_VERSION,
        "data_status": analytics_data_status,
        "scope": "KC và hồ sơ lỗi: chỉ lượt nộp chính thức. Hồ sơ hỗ trợ và nhóm quá trình: mô tả quá trình (descriptive_process).",
        "concepts": concepts,
        "exercise_kcs": exercise_kcs,
        "error_profile": error_profile,
        "support_profile": support_profile,
        "process_by_exercise": process_by_exercise,
        "feature_coverage_percent": coverage,
        "thresholds": dict(THRESHOLDS),
        "disclaimer": DISCLAIMER,
    }
