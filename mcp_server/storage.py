"""
Module truy vấn dữ liệu và lưu trữ sự kiện học tập cho MCP Server từ SQLite.
"""
import sqlite3
import json
import logging
import os
from pathlib import Path
from typing import Optional

from pytutor_shared.learner_model import derive_learner_model

logger = logging.getLogger("pytutor.mcp.storage")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("PYTUTOR_DB_PATH", PROJECT_ROOT / "pytutor.db")).expanduser().resolve()


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def get_all_exercises_summary() -> list[dict]:
    """Lấy danh sách tóm tắt các bài tập từ SQLite."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, difficulty, category, test_cases FROM exercises WHERE is_active = 1 ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        try:
            tc_list = json.loads(r["test_cases"])
            tc_count = len(tc_list)
        except Exception:
            tc_count = 0
        result.append({
            "id": r["id"],
            "title": r["title"],
            "difficulty": r["difficulty"],
            "category": r["category"],
            "test_cases_count": tc_count
        })
    return result


def get_exercise_by_id(exercise_id: str) -> Optional[dict]:
    """Lấy thông tin chi tiết bài tập theo ID từ SQLite."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, difficulty, category, description, starter_code, test_cases FROM exercises WHERE id = ? AND is_active = 1",
        (exercise_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    try:
        test_cases = json.loads(row["test_cases"])
    except Exception:
        test_cases = []

    return {
        "id": row["id"],
        "title": row["title"],
        "difficulty": row["difficulty"],
        "category": row["category"],
        "description": row["description"],
        "starter_code": row["starter_code"],
        "test_cases": test_cases
    }


def save_submission(
    session_id: str,
    exercise_id: str,
    code: str,
    hint_level: int,
    passed_tests: int,
    total_tests: int,
    all_passed: bool,
    llm_source: str,
    tutor_hint: str,
    action_type: str = "submit",
    attempt_features: Optional[dict] = None
) -> int:
    """Lưu sự kiện học tập vào SQLite (kèm đặc trưng lượt nếu có)."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO submissions (
            session_id, exercise_id, code, hint_level, passed_tests, total_tests, all_passed, llm_source, tutor_hint, action_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        exercise_id,
        code,
        hint_level,
        passed_tests,
        total_tests,
        1 if all_passed else 0,
        llm_source,
        tutor_hint,
        action_type if action_type in {"submit", "ask_ai"} else "submit"
    ))
    last_id = cursor.lastrowid
    if attempt_features:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attempt_features (
                submission_id INTEGER PRIMARY KEY,
                error_class TEXT NOT NULL,
                status_counts TEXT NOT NULL DEFAULT '{}',
                ast_flags TEXT NOT NULL DEFAULT '{}',
                feature_version TEXT NOT NULL DEFAULT '1',
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
            )
        """)
        _have = {row[1] for row in cursor.execute("PRAGMA table_info(attempt_features)").fetchall()}
        for _name in ("failed_tests", "format_mismatch_tests"):
            if _name not in _have:
                cursor.execute(f"ALTER TABLE attempt_features ADD COLUMN {_name} TEXT DEFAULT '[]'")
        cursor.execute(
            "INSERT OR REPLACE INTO attempt_features(submission_id, error_class, status_counts, ast_flags, feature_version, failed_tests, format_mismatch_tests) VALUES (?,?,?,?,?,?,?)",
            (last_id, str(attempt_features.get("error_class") or ""),
             json.dumps(attempt_features.get("status_counts") or {}, ensure_ascii=False),
             json.dumps(attempt_features.get("ast_flags") or {}, ensure_ascii=False),
             str(attempt_features.get("feature_version") or "1"),
             json.dumps(attempt_features.get("failed_tests") or []),
             json.dumps(attempt_features.get("format_mismatch_tests") or [])))
    conn.commit()
    conn.close()
    return last_id


def get_attempts(session_id: str, exercise_id: str, limit: int = 5) -> list[dict]:
    """Lấy lịch sử làm bài trước đó của học viên kèm mã nguồn đã nộp."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, code, hint_level, passed_tests, total_tests, all_passed, llm_source, tutor_hint, timestamp, action_type
        FROM submissions
        WHERE session_id = ? AND exercise_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (session_id, exercise_id, limit))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": r["id"],
            "exercise_id": exercise_id,
            "code": r["code"] or "",
            "hint_level": r["hint_level"],
            "passed": r["passed_tests"],
            "total": r["total_tests"],
            "all_passed": bool(r["all_passed"]),
            "llm_source": r["llm_source"],
            "tutor_hint": r["tutor_hint"] or "",
            "timestamp": r["timestamp"],
            "action_type": r["action_type"] or "submit"
        }
        for r in rows
    ]


# LƯU Ý ĐỒNG BỘ: hàm dưới đây phải giống hệt backend/database.py::compute_student_model
# (chỉ khác tên hàm mở kết nối). test_thesis_upgrade.py kiểm tra tính đồng bộ này.
def compute_student_model(session_id: str, class_id: Optional[str] = None) -> dict:
    """
    [Phase 13-14] Tính toán Mô hình Học sinh (Student Model) & Bộ Phân tích Học tập Định lượng 4 Chiều (4D Learning Analytics Engine)
    kèm Đánh giá Tự động từ Hệ thống Gia sư (Diagnostic Evaluation) chính xác 100% dựa trên số liệu thực nghiệm SQLite.
    """
    conn = get_conn()
    cursor = conn.cursor()

    # 1. Lọc theo lớp học phần nếu có class_id
    class_filter_eids = None
    if class_id:
        try:
            cursor.execute("SELECT exercise_id FROM class_exercises WHERE class_id = ?", (class_id,))
            c_rows = cursor.fetchall()
            if c_rows:
                class_filter_eids = set(r["exercise_id"] for r in c_rows)
        except Exception:
            class_filter_eids = None

    # Lấy toàn bộ bài nộp của học viên này (order by id ASC để biết bài nộp đầu tiên)
    cursor.execute("""
        SELECT id, exercise_id, hint_level, passed_tests, total_tests, all_passed, timestamp
        FROM submissions
        WHERE session_id = ? AND action_type = 'submit'
        ORDER BY id ASC
    """, (session_id,))
    sub_rows = [dict(r) for r in cursor.fetchall()]

    # Lấy thông tin sao từ user_exercise_stars nếu có
    stars_map = {}
    try:
        cursor.execute("SELECT exercise_id, stars_earned, highest_clean_score FROM user_exercise_stars WHERE username = ?", (session_id,))
        stars_map = {r["exercise_id"]: dict(r) for r in cursor.fetchall()}
    except Exception:
        stars_map = {}

    # Lấy danh mục bài tập (để phân tích topic_mastery)
    ex_meta_rows = []
    try:
        if class_id:
            cursor.execute("""
                SELECT ce.exercise_id as id, ce.module_name as category, ce.module_name as module_name, ce.skill_tag as skill_tag, e.category as exercise_category, e.title, ce.min_stars_required
                FROM class_exercises ce
                JOIN exercises e ON ce.exercise_id = e.id
                WHERE ce.class_id = ?
                ORDER BY ce.order_idx ASC
            """, (class_id,))
            ex_meta_rows = [dict(r) for r in cursor.fetchall()]
        else:
            cursor.execute("SELECT id, title, category FROM exercises WHERE is_active = 1 ORDER BY id ASC")
            ex_meta_rows = [dict(r) for r in cursor.fetchall()]
    except Exception:
        ex_meta_rows = []

    # Mô hình người học v3: đọc thêm lượt hỏi AI (bỏ Exam-Mode-Guard), lượt chạy thử và đặc trưng lượt.
    ask_rows, run_rows, feature_rows = [], [], []
    kc_defs = None
    try:
        cursor.execute("""
            SELECT id, exercise_id, hint_level, passed_tests, timestamp
            FROM submissions
            WHERE session_id = ? AND action_type = 'ask_ai' AND COALESCE(llm_source, '') != 'Exam-Mode-Guard'
            ORDER BY id ASC
        """, (session_id,))
        ask_rows = [dict(r) for r in cursor.fetchall()]
        cursor.execute("""
            SELECT id, exercise_id, passed_tests, all_passed, timestamp
            FROM practice_runs
            WHERE username = ?
            ORDER BY id ASC
        """, (session_id,))
        run_rows = [dict(r) for r in cursor.fetchall()]
        cursor.execute("""
            SELECT f.submission_id, f.error_class
            FROM attempt_features f JOIN submissions s ON s.id = f.submission_id
            WHERE s.session_id = ?
        """, (session_id,))
        feature_rows = [dict(r) for r in cursor.fetchall()]
        cursor.execute("SELECT kc, label_vi, keywords FROM knowledge_components WHERE is_active = 1 ORDER BY rowid ASC")
        kc_raw_rows = [dict(r) for r in cursor.fetchall()]
        kc_defs = []
        for r in kc_raw_rows:
            try:
                kw = json.loads(r["keywords"]) if isinstance(r["keywords"], str) else (r["keywords"] or [])
            except Exception:
                kw = [k.strip() for k in str(r["keywords"]).split(",") if k.strip()]
            kc_defs.append({"kc": r["kc"], "label_vi": r["label_vi"], "keywords": kw})
        kc_defs = kc_defs or None  # rỗng -> dùng KC mặc định trong pytutor_shared
    except Exception:
        kc_defs = None

    conn.close()

    # Áp dụng bộ lọc bài tập nếu có class_filter_eids
    if class_filter_eids is not None:
        sub_rows = [s for s in sub_rows if s["exercise_id"] in class_filter_eids]
        ask_rows = [a for a in ask_rows if a["exercise_id"] in class_filter_eids]
        run_rows = [r for r in run_rows if r["exercise_id"] in class_filter_eids]

    total_submissions = len(sub_rows)

    # Nhóm theo bài tập
    grouped_by_exercise: dict[str, list[dict]] = {}
    for s in sub_rows:
        eid = s["exercise_id"]
        if eid not in grouped_by_exercise:
            grouped_by_exercise[eid] = []
        grouped_by_exercise[eid].append(s)

    mastered_exercises = []
    struggling_exercises = []
    in_progress_exercises = []

    first_try_pass_count = 0
    exercise_autonomy_scores = []
    autonomy_by_exercise: dict[str, int] = {}
    total_hint_sum = 0
    total_hint_count = 0

    for eid, s_list in grouped_by_exercise.items():
        first_sub = s_list[0]
        if first_sub["all_passed"] == 1:
            first_try_pass_count += 1

        has_passed = any(s["all_passed"] == 1 for s in s_list)
        max_hint = max(s["hint_level"] for s in s_list)
        total_hint_sum += max_hint
        total_hint_count += 1

        # Tính điểm tự lực cho bài này
        if has_passed:
            mastered_exercises.append(eid)
            passed_sub = next(s for s in s_list if s["all_passed"] == 1)
            star_info = stars_map.get(eid)
            stars = star_info["stars_earned"] if star_info else (3 if passed_sub["hint_level"] == 1 else (2 if passed_sub["hint_level"] == 2 else 1))
            if stars == 3:
                exercise_autonomy_scores.append(100)
            elif stars == 2:
                exercise_autonomy_scores.append(70)
            else:
                exercise_autonomy_scores.append(40)
            autonomy_by_exercise[eid] = exercise_autonomy_scores[-1]
        else:
            if len(s_list) >= 2 or max_hint >= 3:
                struggling_exercises.append(eid)
            else:
                in_progress_exercises.append(eid)
            best_ratio = max((s["passed_tests"] / max(1, s["total_tests"])) for s in s_list)
            exercise_autonomy_scores.append(round(best_ratio * 40))
            autonomy_by_exercise[eid] = exercise_autonomy_scores[-1]

    distinct_count = len(grouped_by_exercise)
    autonomy_score = round(sum(exercise_autonomy_scores) / max(1, len(exercise_autonomy_scores))) if exercise_autonomy_scores else 0
    first_try_pass_rate = round((first_try_pass_count / max(1, distinct_count)) * 100, 1) if distinct_count > 0 else 0.0
    avg_attempts_to_solve = round(total_submissions / max(1, distinct_count), 1) if distinct_count > 0 else 0.0
    avg_hint = round(total_hint_sum / max(1, total_hint_count), 1) if total_hint_count > 0 else 1.0

    # Phổ lỗi (Error Breakdown)
    passed_runs = sum(1 for s in sub_rows if s["all_passed"] == 1)
    logic_errors = sum(1 for s in sub_rows if s["all_passed"] == 0 and s["passed_tests"] > 0)
    syntax_or_runtime_errors = sum(1 for s in sub_rows if s["all_passed"] == 0 and s["passed_tests"] == 0)

    error_breakdown = {
        "total_runs": total_submissions,
        "passed_runs": passed_runs,
        "passed_percent": round((passed_runs / max(1, total_submissions)) * 100, 1) if total_submissions > 0 else 0.0,
        "logic_errors": logic_errors,
        "logic_error_percent": round((logic_errors / max(1, total_submissions)) * 100, 1) if total_submissions > 0 else 0.0,
        "syntax_or_runtime_errors": syntax_or_runtime_errors,
        "syntax_error_percent": round((syntax_or_runtime_errors / max(1, total_submissions)) * 100, 1) if total_submissions > 0 else 0.0
    }

    # Phân tích theo từng Chương / Chủ đề (Topic Mastery)
    topics_dict: dict[str, list[dict]] = {}
    for em in ex_meta_rows:
        cat = em.get("category", "Chương trình")
        if cat not in topics_dict:
            topics_dict[cat] = []
        topics_dict[cat].append(em)

    topic_mastery = []
    for cat_name, ex_list in topics_dict.items():
        t_total = len(ex_list)
        t_completed = sum(1 for e in ex_list if e["id"] in mastered_exercises)
        t_pct = round((t_completed / max(1, t_total)) * 100)
        t_stars = [stars_map[e["id"]]["stars_earned"] for e in ex_list if e["id"] in stars_map and e["id"] in mastered_exercises]
        avg_stars_topic = round(sum(t_stars) / max(1, len(t_stars)), 1) if t_stars else 0.0
        topic_mastery.append({
            "topic_name": cat_name,
            "completed": t_completed,
            "total": t_total,
            "percentage": t_pct,
            "avg_stars": avg_stars_topic
        })

    # Lỗi lặp lại: bài có từ 2 lượt nộp chính thức chưa đạt trở lên (quy ước vận hành).
    title_map = {em["id"]: em.get("title") or em["id"] for em in ex_meta_rows}
    recurring_difficulties = []
    for eid, s_list in grouped_by_exercise.items():
        failed_subs = [s for s in s_list if s["all_passed"] == 0]
        if len(failed_subs) < 2:
            continue
        zero_pass = sum(1 for s in failed_subs if s["passed_tests"] == 0)
        recurring_difficulties.append({
            "exercise_id": eid,
            "title": title_map.get(eid, eid),
            "unsuccessful_submissions": len(failed_subs),
            "total_submissions": len(s_list),
            "dominant_error": "syntax_or_runtime" if zero_pass * 2 > len(failed_subs) else "logic",
            "resolved": eid in mastered_exercises,
        })
    recurring_difficulties.sort(key=lambda item: (item["resolved"], -item["unsuccessful_submissions"], item["exercise_id"]))

    # Bước luyện tập tiếp theo: ưu tiên bài đang nghẽn → bài dở dang → bài chưa thử → bài chưa đạt 3 sao.
    next_practice = None
    unresolved = [item for item in recurring_difficulties if not item["resolved"]]
    attempted_ids = set(grouped_by_exercise.keys())
    if unresolved:
        target = unresolved[0]
        next_practice = {"exercise_id": target["exercise_id"], "title": target["title"], "reason_code": "unresolved_recurring",
                         "reason": f"Bài này đã có {target['unsuccessful_submissions']} lượt nộp chưa đạt và chưa hoàn thành."}
    elif struggling_exercises or in_progress_exercises:
        eid = (struggling_exercises or in_progress_exercises)[0]
        next_practice = {"exercise_id": eid, "title": title_map.get(eid, eid), "reason_code": "in_progress",
                         "reason": "Bài đã nộp nhưng chưa vượt qua toàn bộ kiểm thử."}
    else:
        untried = next((em for em in ex_meta_rows if em["id"] not in attempted_ids), None)
        if untried:
            next_practice = {"exercise_id": untried["id"], "title": untried.get("title") or untried["id"],
                             "reason_code": "next_unattempted", "reason": "Bài kế tiếp trong danh sách mà bạn chưa nộp."}
        else:
            below_three = next((eid for eid in mastered_exercises
                                if (stars_map.get(eid) or {}).get("stars_earned", 3) < 3), None)
            if below_three:
                next_practice = {"exercise_id": below_three, "title": title_map.get(below_three, below_three),
                                 "reason_code": "retry_for_autonomy",
                                 "reason": "Bài đã hoàn thành với gợi ý mức cao; có thể tự làm lại không cần gợi ý."}

    # Đánh giá Tự động từ Hệ thống Gia sư (Diagnostic Evaluation)
    if total_submissions == 0:
        level_classification = "Chưa có dữ liệu thực hành (Bắt đầu làm bài tập đầu tiên)"
        strengths_analysis = "Học viên vừa tham gia hệ thống. Hãy chọn bài tập cơ sở đầu tiên trên Lộ trình để bắt đầu tích lũy kinh nghiệm!"
        weaknesses_and_bottlenecks = "Chưa ghi nhận điểm nghẽn nào."
        recommended_next_action = "Mở bài tập Chương 1 để bắt đầu thực hành viết mã nguồn Python đầu tiên."
    elif len(mastered_exercises) >= 4 and autonomy_score >= 80:
        level_classification = "Hoàn thành nhiều bài với mức hỗ trợ thấp"
        strengths_analysis = (
            f"Đã hoàn thành {len(mastered_exercises)}/{distinct_count} bài tập đã thử với chỉ số tự lực {autonomy_score}/100. "
            f"Tỷ lệ hoàn thành ngay lần đầu đạt {first_try_pass_rate}%, trung bình chỉ mất {avg_attempts_to_solve} lần nộp/bài."
        )
        if struggling_exercises:
            weaknesses_and_bottlenecks = f"Cần lưu ý xử lý dứt điểm các bài tập đang vướng mắc: {', '.join(struggling_exercises)}."
        elif error_breakdown["logic_errors"] > 0:
            weaknesses_and_bottlenecks = f"Thỉnh thoảng vẫn gặp sai lệch ở các test case biên (lỗi logic kiểm thử chiếm {error_breakdown['logic_error_percent']}%)."
        else:
            weaknesses_and_bottlenecks = "Không có điểm nghẽn kỹ thuật nào đáng kể."
        recommended_next_action = "Thử các thử thách 'Tối ưu Code Pythonic' hoặc bài kế tiếp trên lộ trình."
    elif len(mastered_exercises) >= 2 and autonomy_score >= 60:
        level_classification = "Hoàn thành ổn định, còn dùng gợi ý ở một số bài"
        strengths_analysis = (
            f"Đã hoàn thành {len(mastered_exercises)}/{distinct_count} bài tập với chỉ số tự lực {autonomy_score}/100. "
            f"Vượt qua bài tập với mức trợ giúp trung bình Level {avg_hint} (chủ yếu dùng Gợi ý nhẹ hoặc Chỉ chỗ sai)."
        )
        if struggling_exercises:
            weaknesses_and_bottlenecks = (
                f"Đang gặp điểm nghẽn tại bài tập: {', '.join(struggling_exercises)}. "
                f"Phổ lỗi ghi nhận: {error_breakdown['logic_error_percent']}% lỗi logic test case và {error_breakdown['syntax_error_percent']}% lỗi cú pháp/runtime."
            )
        else:
            weaknesses_and_bottlenecks = "Chưa ghi nhận bài nào bị nghẽn; một số bài hoàn thành sau khi dùng gợi ý mức cao."
        recommended_next_action = "Tiếp tục bài tập kế tiếp và xem lại các bước giải để củng cố tính độc lập khi lập trình."
    else:
        level_classification = "Đang xây nền tảng, còn nhiều lượt nộp chưa đạt"
        strengths_analysis = (
            f"Đã tích cực nộp bài {total_submissions} lượt và hoàn thành {len(mastered_exercises)} bài tập. "
            f"Trung bình {avg_attempts_to_solve} lượt nộp cho mỗi bài đã thử."
        )
        weaknesses_and_bottlenecks = (
            f"Tỷ lệ lỗi logic chiếm {error_breakdown['logic_error_percent']}% và lỗi cú pháp chiếm {error_breakdown['syntax_error_percent']}%. "
            f"Bài đang nghẽn: {', '.join(struggling_exercises) if struggling_exercises else 'chưa xác định được bài cụ thể'}."
        )
        recommended_next_action = next_practice["reason"] if next_practice else ""

    evidence_status = "no_data" if total_submissions == 0 else ("limited" if distinct_count < 3 else "sufficient")
    if evidence_status == "limited":
        level_classification = "Chưa đủ dữ liệu để phân loại"
        strengths_analysis = "Đã ghi nhận hoạt động học tập; cần thêm bài làm để nhận diện điểm mạnh ổn định."
        weaknesses_and_bottlenecks = "Chưa đủ dữ liệu để kết luận về điểm nghẽn hoặc dạng lỗi thường gặp."
        recommended_next_action = "Tiếp tục luyện thêm bài tập trong học phần để hồ sơ có đủ dữ liệu phân tích."

    diagnostic_evaluation = {
        "level_classification": level_classification,
        "strengths_analysis": strengths_analysis,
        "weaknesses_and_bottlenecks": weaknesses_and_bottlenecks,
        "recommended_next_action": recommended_next_action
    }

    analytics_metrics = {
        "total_submissions": total_submissions,
        "distinct_exercises_attempted": distinct_count,
        "mastered_exercises": mastered_exercises,
        "struggling_exercises": struggling_exercises,
        "in_progress_exercises": in_progress_exercises,
        "autonomy_score": autonomy_score,
        "first_try_pass_rate": first_try_pass_rate,
        "avg_attempts_to_solve": avg_attempts_to_solve,
        "average_hint_level": avg_hint,
        "error_breakdown": error_breakdown,
        "topic_mastery": topic_mastery,
        "data_status": evidence_status,
        "sample_size": distinct_count,
        "recurring_difficulties": recurring_difficulties,
        "next_practice": next_practice,
        "metric_definition_version": "2"
    }

    learner_model = derive_learner_model(
        exercises=ex_meta_rows,
        submissions=sub_rows,
        asks=ask_rows,
        runs=run_rows,
        features={r["submission_id"]: r for r in feature_rows},
        autonomy_by_exercise=autonomy_by_exercise,
        analytics_data_status=evidence_status,
        kc_definitions=kc_defs,
    )

    summary = (
        f"🎯 Xếp loại: {level_classification} | Chỉ số tự lực: {autonomy_score}/100.\n"
        f"🌟 Điểm mạnh: {strengths_analysis}\n"
        f"⚠️ Cần lưu ý: {weaknesses_and_bottlenecks}\n"
        f"🧭 Khuyến nghị: {recommended_next_action}"
    )

    return {
        "session_id": session_id,
        "class_id": class_id,
        "total_exercises_attempted": distinct_count,
        "total_submissions": total_submissions,
        "mastered_exercises": mastered_exercises,
        "struggling_exercises": struggling_exercises,
        "in_progress_exercises": in_progress_exercises,
        "average_hint_level": avg_hint,
        "summary": summary,
        "analytics_metrics": analytics_metrics,
        "diagnostic_evaluation": diagnostic_evaluation,
        "learner_model": learner_model
    }
