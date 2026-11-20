"""Deterministic, evidence-backed hint strategy selection (Phase 17, nâng cấp mô hình người học v3).

Bất biến: chính sách chỉ chọn CHIẾN LƯỢC và các điều chỉnh diễn đạt; `requested_level` luôn bằng đầu vào,
không có trường nào trong đầu ra làm tăng mức tiết lộ (hint_level).
Luật dựa trên mô hình chỉ kích hoạt khi nhóm kiến thức liên quan có đủ dữ liệu (>= 2 bài KHÁC bài hiện tại)
và chỉ dùng bằng chứng từ các bài khác, không đếm trùng lịch sử bài hiện tại.
"""
from __future__ import annotations

from pytutor_shared.learner_model import (
    KC_LABELS, THRESHOLDS, dominant_class, is_struggling_detail, summarize_attempt_features,
)

POLICY_VERSION = "3"

# Chỉ dẫn cố định cho prompt theo mã điều chỉnh (không chứa nội dung lời giải).
ADAPTATION_INSTRUCTIONS = {
    "same_exercise_repeat": "Sinh viên đã thử bài này nhiều lần: không lặp lại nguyên văn gợi ý cũ, chia nhỏ bước kế tiếp.",
    "concept_recurring_difficulty": "Nhóm kiến thức của bài này từng gây vướng ở bài khác: nhắc nhẹ sự liên hệ giữa hai bài, không kết luận về năng lực.",
    "repeated_error_type": "Dạng lỗi lần này trùng với dạng lỗi thường gặp ở các bài khác cùng nhóm: gọi tên dạng lỗi bằng lời, dựa trên bằng chứng kiểm thử.",
    "bridge_from_mastered": "Nhóm kiến thức này sinh viên đã nộp đạt ở bài khác: mời sinh viên nhớ lại cách đã làm ở bài đó, không chép lại lời giải.",
    "independence_check": "Sinh viên đã đạt bài; mời tự kiểm trước khi xin gợi ý ở bài sau (khuyến khích, không ép buộc).",
    "granularity_fine": "Chia bước kế tiếp thành hai bước nhỏ về quy trình (chạy thử, quan sát, rồi sửa), vẫn trong giới hạn tiết lộ của Level hiện tại.",
    "granularity_coarse": "Sinh viên đã làm khá vững các bài trước: chỉ đặt MỘT câu hỏi và để sinh viên tự kiểm trước, không giải thích dài.",
    "self_check_first": "Yêu cầu sinh viên nêu giả thuyết của mình và tự kiểm bằng Chạy thử trước khi đọc thêm gợi ý.",
    "no_code_yet": "Sinh viên chưa viết dòng code nào (editor trống hoặc chỉ còn khung mẫu): KHÔNG nhận xét bài làm, KHÔNG nói test thất bại; "
                   "giúp hiểu đề (đề cho gì, cần in ra gì) và chọn bước đầu tiên, đúng giới hạn tiết lộ của Level được yêu cầu.",
}


def is_blank_attempt(code: str | None, starter_code: str | None = None) -> bool:
    """True nếu chưa có dòng code thật: rỗng, chỉ còn bình luận/`pass`/`...`, hoặc y hệt khung mẫu của bài."""
    def meaningful(src: str | None) -> list[str]:
        return [ln.strip() for ln in (src or "").splitlines()
                if ln.strip() and not ln.strip().startswith("#") and ln.strip() not in ("pass", "...")]
    mine = meaningful(code)
    return not mine or mine == meaningful(starter_code)


def _kc_views(lm: dict, exercise_id: str | None) -> list[dict]:
    """Quan điểm của từng KC liên quan tới bài hiện tại, chỉ dựa trên các bài KHÁC."""
    if not lm or not exercise_id:
        return []
    kcs = (lm.get("exercise_kcs") or {}).get(exercise_id) or []
    concepts = {c["kc"]: c for c in lm.get("concepts") or []}
    min_ex = THRESHOLDS["concept_sufficient_min_exercises"]
    views = []
    for kc in kcs:
        concept = concepts.get(kc)
        if not concept:
            continue
        others = [d for d in concept.get("exercise_details") or [] if d.get("exercise_id") != exercise_id]
        struggling = [d for d in others if is_struggling_detail(kc, d)]
        passed = [d for d in others if d.get("status") == "passed"]
        autos = [d["autonomy"] for d in passed if d.get("autonomy") is not None]
        avg = (sum(autos) / len(autos)) if autos else None
        if struggling:
            state = "struggling"
        elif len(passed) >= THRESHOLDS["secure_min_passed_exercises"] and avg is not None and avg >= THRESHOLDS["secure_min_avg_autonomy"]:
            state = "secure"
        elif others:
            state = "developing"
        else:
            state = "no_evidence"
        views.append({
            "kc": kc, "label_vi": KC_LABELS.get(kc, kc), "state": state, "others_attempted": len(others),
            "sufficient": len(others) >= min_ex, "struggling": struggling, "passed": passed,
            "dominant_error_class": dominant_class([d["dominant_error_class"] for d in others
                                                    if d.get("dominant_error_class") and d.get("status") != "passed"]),
        })
    return views


def select_hint_strategy(hint_level: int, test_results: dict, attempt_history: list[dict] | None,
                         student_model: dict | None, exercise_id: str | None = None,
                         use_learner_model: bool = True, no_code: bool = False) -> dict:
    history = attempt_history or []
    model = student_model or {}
    metrics = model.get("analytics_metrics") or {}
    tests = test_results or {}
    evidence: list[str] = []
    if history:
        evidence.append("prior_attempts")
        evidence.append("previous_hint_levels")
    failed = [r for r in tests.get("results", []) if r.get("status") != "PASS"]
    if failed:
        evidence.append("failed_test_cases")
    enough = metrics.get("distinct_exercises_attempted", 0) > 0
    if enough and metrics.get("first_try_pass_rate") is not None:
        evidence.append("first_try_pass_rate")
    if enough and metrics.get("autonomy_score") is not None:
        evidence.append("autonomy_score")

    lm = (model.get("learner_model") or None) if use_learner_model else None
    views = _kc_views(lm, exercise_id) if lm else []
    support = (lm or {}).get("support_profile") or {}
    reliance = support.get("hint_reliance", "unknown")
    autonomy = metrics.get("autonomy_score")
    data_sufficient = metrics.get("data_status") == "sufficient"

    adaptations: list[dict] = []
    fields_used: list[str] = []

    def add(code: str, reason: str, context: dict | None = None, fields: list[str] | None = None) -> None:
        adaptations.append({"code": code, "reason_vi": reason, "context": context or {}})
        for f in fields or []:
            if f not in fields_used:
                fields_used.append(f)

    error_class = summarize_attempt_features(tests)["error_class"] if failed and not tests.get("all_passed") else None
    diagnosis_focus = error_class  # dạng lỗi quan sát được ở lượt này (từ trạng thái kiểm thử), không dùng mô hình

    # --- Chọn chiến lược ---
    if tests.get("all_passed"):
        strategy = "solution_review"
        if reliance == "high":
            add("independence_check",
                "Bạn thường xin gợi ý từ Mức 2 trở lên ở nhiều bài; lần này bạn đã đạt, thử tự kiểm trước khi xin gợi ý ở bài sau.",
                {"hint_reliance": reliance}, ["learner_model.support_profile.hint_reliance"])
    elif no_code:
        # Chưa có code: kết quả kiểm thử không mang thông tin, nên không dùng làm căn cứ chẩn đoán.
        strategy = "conceptual_start"
        add("no_code_yet", "Bạn chưa viết dòng code nào, nên gợi ý tập trung vào hiểu đề và bước đầu tiên.")
        failed = []
        error_class = None
    elif len(history) >= 2:
        strategy = "recurring_difficulty"
        submits = sum(1 for h in history if h.get("action_type") == "submit")
        asks = sum(1 for h in history if h.get("action_type") == "ask_ai")
        add("same_exercise_repeat", f"Bạn đã thử bài này {len(history)} lần gần đây ({submits} lần nộp, {asks} lần hỏi gợi ý).",
            {"attempts": len(history), "submits": submits, "asks": asks})
    else:
        struggling_views = [v for v in views if v["sufficient"] and v["struggling"]]
        if failed and struggling_views:
            strategy = "recurring_difficulty"
            v = struggling_views[0]
            add("concept_recurring_difficulty",
                f"Nhóm kiến thức \"{v['label_vi']}\" đã có bài chưa giải được ({v['struggling'][0]['title']}); "
                "bài này cùng nhóm nên hệ thống đề nghị làm chậm và có phương pháp.",
                {"kc": v["kc"], "kc_label": v["label_vi"], "exercise_title": v["struggling"][0]["title"]},
                [f"learner_model.concepts[{v['kc']}].state", f"learner_model.concepts[{v['kc']}].exercise_details"])
        elif failed:
            strategy = "failed_case_diagnosis"
            for v in views:
                if v["sufficient"] and error_class and v["dominant_error_class"] == error_class:
                    add("repeated_error_type",
                        f"Dạng lỗi lần này ({error_class}) trùng dạng lỗi thường gặp ở các bài khác thuộc nhóm \"{v['label_vi']}\".",
                        {"error_class": error_class, "kc": v["kc"], "kc_label": v["label_vi"]},
                        [f"learner_model.concepts[{v['kc']}].dominant_error_class"])
                    break
        else:
            strategy = "conceptual_start"
            for v in views:
                if v["sufficient"] and v["state"] == "secure" and v["passed"]:
                    add("bridge_from_mastered",
                        f"Nhóm kiến thức \"{v['label_vi']}\" bạn đã nộp đạt ở bài \"{v['passed'][0]['title']}\"; có thể nhớ lại cách đã làm.",
                        {"kc": v["kc"], "kc_label": v["label_vi"], "exercise_title": v["passed"][0]["title"]},
                        [f"learner_model.concepts[{v['kc']}].state"])
                    break
    # --- Độ chi tiết diễn đạt (không đổi mức tiết lộ) ---
    granularity = "standard"
    if lm and not tests.get("all_passed") and data_sufficient:
        with_evidence = [c for c in lm.get("concepts") or [] if c.get("state") != "no_evidence"]
        if reliance == "high":
            granularity = "fine"
            add("granularity_fine", "Chia bước kế tiếp nhỏ hơn vì bạn thường cần nhiều hỗ trợ ở các bài trước (mô tả quá trình).",
                {"hint_reliance": reliance}, ["learner_model.support_profile.hint_reliance"])
        elif autonomy is not None and autonomy < THRESHOLDS["fine_granularity_autonomy_below"]:
            granularity = "fine"
            add("granularity_fine", f"Chia bước kế tiếp nhỏ hơn vì chỉ số tự lực hiện tại là {autonomy}/100 (heuristic).",
                {"autonomy_score": autonomy}, ["analytics_metrics.autonomy_score"])
        elif (autonomy is not None and autonomy >= THRESHOLDS["coarse_granularity_autonomy_min"]
              and sum(1 for c in with_evidence if c.get("state") == "secure") >= 2
              and not any(c.get("state") == "struggling" for c in with_evidence)
              and all(c.get("state") == "secure" for c in with_evidence if c.get("data_status") == "sufficient")):
            granularity = "coarse"
            add("granularity_coarse", "Các nhóm kiến thức đã có đủ dữ liệu đều ở trạng thái khá vững nên phản hồi được rút gọn.",
                {"autonomy_score": autonomy}, ["analytics_metrics.autonomy_score", "learner_model.concepts[*].state"])
            add("self_check_first", "Bạn tự nêu giả thuyết và tự kiểm bằng Chạy thử trước khi đọc thêm gợi ý.", {})

    signals: dict = {}
    if lm:
        signals = {
            "exercise_kcs": [{"kc": v["kc"], "label_vi": v["label_vi"], "state": v["state"],
                              "others_attempted": v["others_attempted"], "sufficient": v["sufficient"]} for v in views],
            "hint_reliance": reliance,
            "autonomy_score": autonomy,
            "analytics_data_status": metrics.get("data_status"),
            "error_class": error_class,
        }

    return {"strategy": strategy, "reason_code": strategy, "evidence": evidence,
            "previous_hint_levels": [int(item.get("hint_level", 1) or 1) for item in history[:3]],
            "data_status": "sufficient" if evidence else "insufficient", "requested_level": hint_level,
            "adaptations": adaptations, "adaptation_codes": [a["code"] for a in adaptations],
            "model_fields_used": fields_used, "learner_signals": signals,
            "granularity": granularity, "diagnosis_focus": diagnosis_focus,
            "policy_version": POLICY_VERSION}
