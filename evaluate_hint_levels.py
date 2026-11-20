"""Đo chất lượng 3 mức gợi ý của "🤖 Hỏi Gia sư AI" qua ĐÚNG đường sản phẩm (v5.10).

Mỗi kịch bản trong `evaluation/hint_scenarios.json` (phát triển) hoặc `hint_scenarios_holdout.json` (giữ riêng,
CHỈ để đo, không dùng chỉnh luật/prompt) được chạy tuần tự qua `POST /api/submit` với `action_type='ask_ai'`
(TestClient, DB tạm), theo dãy mức của kịch bản (mặc định 1 → 2 → 3). Lịch sử nộp được nạp vào DB tạm trước.

Chạy:
  py evaluate_hint_levels.py --offline --tag before_offline_dev                 # nhánh rule-based, LLM tắt, miễn phí
  py evaluate_hint_levels.py --real --tag before_real_dev_1 [--delay 1.5]      # Gemini thật (đếm lượt, trần 300)
  py evaluate_hint_levels.py --offline --holdout --quiet --tag ...             # --quiet: chỉ lưu tệp, không in nguyên văn
  py evaluate_hint_levels.py --rescore evaluation/hint_levels_v510_X.json      # tính lại kiểm tra từ phản hồi đã lưu (không gọi gì)

Ràng buộc an toàn: DB/KB tạm trong %TEMP% (đặt TRƯỚC khi import backend), so sánh băm pytutor.db trước/sau;
không in/ghi API key; Qwen bị tắt trong script này; mỗi yêu cầu --real gọi đúng MỘT lần Gemini (mô hình chính),
giãn tối thiểu --delay giây; gặp 429/hết hạn ngạch thì dừng phần đo thật; không thử lại. Tổng lượt cả đêm
ghi ở evaluation/v510_gemini_calls.json (trần 300). Thiếu GEMINI_API_KEY ở --real: thoát mã 2, không fallback âm thầm.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVAL = ROOT / "evaluation"
CALLS_FILE = EVAL / "v510_gemini_calls.json"
CALL_LIMIT = 300
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import hint_quality_checks as hq  # noqa: E402  (thuần, không đụng DB)


def sha256(path: Path):
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def key_present() -> bool:
    """Chỉ kiểm tra có/không, không bao giờ in giá trị."""
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


def load_calls() -> dict:
    if CALLS_FILE.exists():
        return json.loads(CALLS_FILE.read_text(encoding="utf-8"))
    return {"limit": CALL_LIMIT, "total": 0, "runs": []}


def save_calls(data: dict) -> None:
    CALLS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def git_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:
        return "?"


# ----------------------------------------------------------------------------------------------
# Kiểm tra cho một phản hồi
# ----------------------------------------------------------------------------------------------
# Kiểm tra thuần ĐỊNH DẠNG (nhãn "Bước kế tiếp"): bản prompt cũ không yêu cầu nhãn này, nên tách ra khỏi tổng hợp "nội dung".
FORMAT_CHECKS = {"dung_mot_buoc_ke_tiep"}


def score_reply(rec: dict, sc: dict, profile: dict, exercise: dict) -> dict:
    """Chạy các kiểm tra tất định cho một phản hồi (rec chứa reply, level, test_results, ast_analysis)."""
    reply, level, code = rec["reply"], rec["level"], sc["code"]
    starter = exercise.get("starter_code", "") or ""
    expect = sc["expect"]
    tests = exercise.get("test_cases", [])
    tr, ast_a = rec.get("test_results") or {}, rec.get("ast_analysis") or {}
    applicable_failing = expect not in ("PASS",)
    c: dict = {}
    c["do_dai"] = hq.check_length(reply, level, passed=(expect == "PASS"))
    c["khong_nhan_xet_nang_luc"] = hq.check_no_ability_remark(reply)
    c["khong_chep_lai_chu_thich"] = hq.check_no_comment_echo(reply, code, starter)
    c["khung_muc_tieu_bang_chung_buoc"] = hq.check_frame(reply)
    c["dung_mot_buoc_ke_tiep"] = hq.check_single_next_step(reply)
    err_text = " ".join(f"{t.get('error_message') or ''} {t.get('stderr') or ''}" for t in hq.first_failures(tr))
    # Mức 1 dùng ví dụ với dữ kiện KHÁC bài (đúng theo thiết kế) nên tên trong ví dụ không thể đối chiếu với mã người học: chỉ kiểm Mức 2-3.
    c["ten_co_that"] = hq.check_grounded_names(reply, code, exercise, err_text) if level != 1 else None
    leaks = hq.leaked_core(reply, code, profile.get("core", []) + sc.get("extra_core", [])) if applicable_failing else []
    c["khong_lo_bieu_thuc_loi_giai"] = not leaks
    c["khong_chuong_trinh_hoan_chinh"] = hq.check_no_full_program(reply, code, level) if applicable_failing else None
    c["khong_cum_chi_cach_sua"] = hq.check_no_fix_phrases(reply) if applicable_failing else None
    if expect == "PASS":
        c["khong_cum_chi_cach_sua"] = None
    if level == 1:
        c["m1_khong_bang_chung_test_cu_the"] = hq.check_l1_no_test_specifics(reply, tr) if expect not in ("BLANK", "PASS") else None
        c["m1_khong_trich_dong_code"] = hq.check_l1_no_code_quote(reply, code, starter) if expect not in ("PASS",) else None
        c["m1_khong_khoi_code"] = hq.check_no_code_block(reply) if expect != "PASS" else None
        c["m1_neu_khai_niem"] = hq.check_names_concept(reply, sc["concept_terms"]) if expect != "PASS" else None
        c["m1_khong_chi_la_cau_hoi_suong"] = hq.check_l1_informative(reply, sc["concept_terms"]) if expect != "PASS" else None
    elif level == 2:
        blank_or_pass = expect in ("BLANK", "PASS")
        c["m2_dung_mot_dong_that"] = hq.check_l2_quotes_one_line(reply, code, starter) if not blank_or_pass else None
        c["m2_dong_dung_cho_loi"] = hq.check_l2_points_at_expected(reply, code, starter, sc.get("expected_lines", [])) if not blank_or_pass else None
        c["m2_co_bang_chung_thuc_thi"] = hq.check_l2_evidence(reply, tr, ast_a, expect)
        c["m2_khong_khoi_code_3_dong"] = hq.check_no_full_program(reply, code, 2) if applicable_failing else None
    else:
        c["m3_dan_y_4_buoc_khop_bai"] = hq.check_l3_steps(reply, sc["_exercise_terms"]) if expect != "PASS" else None
        c["m3_co_khung_todo"] = hq.check_l3_has_skeleton(reply) if expect != "PASS" else None
        c["m3_khung_khong_dat_het_test"] = hq.check_l3_skeleton_not_passing(reply, tests) if expect != "PASS" else None
        c["m3_khung_la_python_hop_le"] = hq.check_l3_skeleton_valid_python(reply) if expect != "PASS" else None
    # Thông tin tính năng (không tính vào đạt/không đạt)
    info = {"words": len(hq.words(reply)), "leaks": leaks}
    if level == 2:
        info["quoted_lines"] = hq.quoted_student_lines(reply, code, starter)
    if level == 3:
        info["co_bang_chay_tay"] = hq.check_l3_has_trace_table(reply)
        info["giu_dong_cua_nguoi_hoc"] = hq.check_l3_keeps_student_lines(reply, code, starter)
    return {"checks": c, "info": info}


def score_all(results: list, profiles: dict, exercises: dict, scenarios: dict) -> None:
    """Gắn checks cho từng phản hồi và độ trùng/tăng tiến giữa các lượt liên tiếp của cùng kịch bản."""
    by_sc: dict[str, list] = {}
    for rec in results:
        sc = scenarios[rec["scenario"]]
        sc["_exercise_terms"] = profiles[sc["exercise"]]["terms"]
        rec.update(score_reply(rec, sc, profiles[sc["exercise"]], exercises[sc["exercise"]]))
        by_sc.setdefault(rec["scenario"], []).append(rec)
    for sid, seq in by_sc.items():
        sc = scenarios[sid]
        for i, rec in enumerate(seq):
            rec["overlap_prev"] = round(hq.jaccard(seq[i - 1]["reply"], rec["reply"]), 3) if i else None
            rec["checks"]["khong_lap_voi_luot_truoc"] = (rec["overlap_prev"] < hq.OVERLAP_MAX) if i else None
            rec["checks"]["tang_tien_so_voi_luot_truoc"] = None
            if i:
                prev = seq[i - 1]
                if prev["level"] == 1 and rec["level"] == 2:
                    rec["checks"]["tang_tien_so_voi_luot_truoc"] = hq.check_progress_l1_to_l2(
                        prev["reply"], rec["reply"], rec.get("test_results") or {}, rec.get("ast_analysis") or {}, sc["expect"])
                elif prev["level"] == 2 and rec["level"] == 3 and sc["expect"] != "PASS":
                    rec["checks"]["tang_tien_so_voi_luot_truoc"] = hq.check_progress_l2_to_l3(prev["reply"], rec["reply"])
        for rec in seq:
            applicable = [v for v in rec["checks"].values() if v is not None]
            rec["all_pass"] = bool(applicable) and all(applicable)
            content = [v for k, v in rec["checks"].items() if v is not None and k not in FORMAT_CHECKS]
            rec["all_pass_content"] = bool(content) and all(content)


def summarize(results: list) -> dict:
    """Bảng: kiểm tra → mức → (đạt, áp dụng). Cộng thêm số phản hồi đạt mọi kiểm tra."""
    table: dict[str, dict[int, list]] = {}
    for rec in results:
        for name, val in rec["checks"].items():
            if val is None:
                continue
            cell = table.setdefault(name, {}).setdefault(rec["level"], [0, 0])
            cell[0] += int(bool(val))
            cell[1] += 1
    strict, strict_content = {}, {}
    for lvl in (1, 2, 3):
        rs = [r for r in results if r["level"] == lvl]
        strict[lvl] = [sum(1 for r in rs if r.get("all_pass")), len(rs)]
        strict_content[lvl] = [sum(1 for r in rs if r.get("all_pass_content")), len(rs)]
    src = {}
    for r in results:
        src[r.get("llm_source") or "-"] = src.get(r.get("llm_source") or "-", 0) + 1
    overlaps = [r["overlap_prev"] for r in results if r.get("overlap_prev") is not None]
    return {"checks": {k: {str(l): v for l, v in d.items()} for k, d in table.items()},
            "all_pass_by_level": {str(k): v for k, v in strict.items()},
            "all_pass_content_by_level": {str(k): v for k, v in strict_content.items()}, "sources": src,
            "overlap_mean": round(sum(overlaps) / len(overlaps), 3) if overlaps else None,
            "overlap_max": max(overlaps) if overlaps else None,
            "words_mean_by_level": {str(l): round(sum(r["info"]["words"] for r in results if r["level"] == l) /
                                                max(1, sum(1 for r in results if r["level"] == l)), 1) for l in (1, 2, 3)}}


def render_md(out: dict) -> str:
    m, s = out["meta"], out["summary"]
    L = [f"# Đo 3 mức gợi ý — `{m['tag']}`", "",
         f"> Sinh bởi `evaluate_hint_levels.py` lúc {m['finished']} · commit `{m['git_head']}` · chế độ **{m['mode']}** · "
         f"tập **{m['set']}** · {m['scenarios']} kịch bản, {m['replies']} phản hồi · nguồn: {json.dumps(s['sources'], ensure_ascii=False)}", "",
         "Kiểm tra tất định (so khớp quy tắc, **không phải điểm sư phạm**). Ô = đạt/áp dụng theo mức 1 | 2 | 3.", "",
         "| Kiểm tra | Mức 1 | Mức 2 | Mức 3 |", "|---|---|---|---|"]
    for name, d in sorted(s["checks"].items()):
        cells = [f"{d[str(l)][0]}/{d[str(l)][1]}" if str(l) in d else "—" for l in (1, 2, 3)]
        L.append(f"| {name} | {cells[0]} | {cells[1]} | {cells[2]} |")
    ap = s["all_pass_by_level"]
    ac = s.get("all_pass_content_by_level") or ap
    L += ["", f"**Phản hồi đạt MỌI kiểm tra áp dụng:** Mức 1 {ap['1'][0]}/{ap['1'][1]} · Mức 2 {ap['2'][0]}/{ap['2'][1]} · Mức 3 {ap['3'][0]}/{ap['3'][1]}",
          f"**Đạt mọi kiểm tra NỘI DUNG (bỏ kiểm tra định dạng nhãn `dung_mot_buoc_ke_tiep`):** Mức 1 {ac['1'][0]}/{ac['1'][1]} · Mức 2 {ac['2'][0]}/{ac['2'][1]} · Mức 3 {ac['3'][0]}/{ac['3'][1]}",
          f"· Độ trùng Jaccard 3-gram giữa hai lượt liên tiếp: trung bình {s['overlap_mean']}, lớn nhất {s['overlap_max']} (ngưỡng < {hq.OVERLAP_MAX})",
          f"· Số từ trung bình: Mức 1 {s['words_mean_by_level']['1']}, Mức 2 {s['words_mean_by_level']['2']}, Mức 3 {s['words_mean_by_level']['3']}", ""]
    fails = [(r["scenario"], r["level"], [k for k, v in r["checks"].items() if v is False]) for r in out["results"] if not r.get("all_pass")]
    L += ["## Phản hồi chưa đạt (kiểm tra nào trượt)", ""]
    for sid, lvl, bad in fails:
        L.append(f"- {sid} · Mức {lvl}: {', '.join(bad) or '(không có kiểm tra áp dụng)'}")
    if m.get("note"):
        L += ["", f"Ghi chú: {m['note']}"]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------------------------
# Chạy
# ----------------------------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--holdout", action="store_true")
    ap.add_argument("--redteam", action="store_true", help="Tập tấn công (thuộc tập phát triển): evaluation/hint_scenarios_redteam.json")
    ap.add_argument("--quiet", action="store_true", help="Chỉ lưu tệp, không in nguyên văn phản hồi")
    ap.add_argument("--tag", required=False, default="adhoc")
    ap.add_argument("--delay", type=float, default=1.5)
    ap.add_argument("--only", default="", help="Danh sách id kịch bản, ngăn bằng dấu phẩy")
    ap.add_argument("--levels", default="", help="Chỉ chạy các mức này (ví dụ 1 hoặc 1,2); kịch bản không còn mức nào bị bỏ. Dùng để tiết kiệm lượt Gemini.")
    ap.add_argument("--rescore", default="", help="Tính lại kiểm tra từ tệp JSON đã lưu, không gọi gì")
    ap.add_argument("--note", default="")
    ap.add_argument("--verify-scenarios", action="store_true", help="Chỉ kiểm tra kịch bản có đúng loại lỗi mong đợi (sandbox)")
    args = ap.parse_args()
    if sum([args.offline, args.real, bool(args.rescore), args.verify_scenarios]) != 1:
        print("Chọn đúng một trong: --offline, --real, --rescore, --verify-scenarios", file=sys.stderr)
        return 2

    from mcp_server.exercises_data import EXERCISES
    exercises = {e["id"]: e for e in EXERCISES}
    sc_file = EVAL / ("hint_scenarios_holdout.json" if args.holdout else "hint_scenarios_redteam.json" if args.redteam else "hint_scenarios.json")

    if args.rescore:
        path = ROOT / args.rescore
        out = json.loads(path.read_text(encoding="utf-8"))
        set_file = {"holdout": "hint_scenarios_holdout.json", "redteam": "hint_scenarios_redteam.json"}.get(out["meta"]["set"], "hint_scenarios.json")
        corpus = json.loads((EVAL / set_file).read_text(encoding="utf-8"))
        scs = {s["id"]: s for s in corpus["scenarios"]}
        score_all(out["results"], corpus["exercise_profiles"], exercises, scs)
        out["summary"] = summarize(out["results"])
        out["meta"]["rescored"] = datetime.now().isoformat(timespec="seconds")
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        path.with_suffix(".md").write_text(render_md(out), encoding="utf-8")
        print(f"Đã tính lại {len(out['results'])} phản hồi → {path.name}")
        return 0

    corpus = json.loads(sc_file.read_text(encoding="utf-8"))
    profiles = corpus["exercise_profiles"]
    scenarios = [s for s in corpus["scenarios"] if not args.only or s["id"] in args.only.split(",")]
    if args.levels:
        keep = {int(x) for x in args.levels.split(",")}
        scenarios = [dict(s, levels=[l for l in s["levels"] if l in keep]) for s in scenarios]
        scenarios = [s for s in scenarios if s["levels"]]

    if args.verify_scenarios:
        from mcp_server.sandbox import run_test_cases
        bad = 0
        for s in scenarios:
            r = run_test_cases(s["code"], exercises[s["exercise"]]["test_cases"])
            first = next((x for x in r["results"] if x["status"] != "PASS"), None)
            st = "PASS" if r["all_passed"] else first["status"]
            ok = st == s["expect"] or (s["expect"] == "BLANK" and st == "FAIL")
            bad += 0 if ok else 1
            print(f"{s['id']} expect={s['expect']} got={st} {'OK' if ok else 'MISMATCH'}")
        return 1 if bad else 0

    planned = sum(len(s["levels"]) for s in scenarios)
    calls = load_calls()
    if args.real:
        if not key_present():
            print("LỖI: chưa có GEMINI_API_KEY. Dừng, không fallback offline.", file=sys.stderr)
            return 2
        if calls["total"] + planned > calls["limit"]:
            print(f"LỖI: sẽ vượt trần {calls['limit']} lượt Gemini (đã dùng {calls['total']}, kế hoạch {planned}).", file=sys.stderr)
            return 3
        os.environ.pop("PYTUTOR_DISABLE_LLM", None)
    else:
        os.environ["PYTUTOR_DISABLE_LLM"] = "1"

    real_db = ROOT / "pytutor.db"
    hash_before = sha256(real_db)
    tag = uuid.uuid4().hex
    tmp_db = Path(tempfile.gettempdir()) / f"pytutor_hint_{tag}.db"
    tmp_kb = Path(tempfile.gettempdir()) / f"pytutor_hint_kb_{tag}.sqlite3"
    os.environ["PYTUTOR_DB_PATH"] = str(tmp_db)
    os.environ["PYTUTOR_KNOWLEDGE_DB_PATH"] = str(tmp_kb)

    from fastapi.testclient import TestClient
    from backend import llm_service
    from backend.auth import create_token
    from backend.database import get_db_connection, init_db
    from backend.main import app

    state = {"prompt": None, "used": 0, "stopped": "", "last_call": 0.0}
    real_build = llm_service.build_scaffolding_prompt

    def capture_prompt(*a, **kw):
        p = real_build(*a, **kw)
        state["prompt"] = p
        return p
    llm_service.build_scaffolding_prompt = capture_prompt

    async def no_qwen(*a, **kw):
        return None
    llm_service.call_qwen_api = no_qwen  # không gửi dữ liệu tới máy chủ Qwen ngoài trong lúc đo

    if args.real:
        def one_call(prompt: str):
            """Đúng một lần gọi Gemini (mô hình chính). Dừng khi gặp 429/hết hạn ngạch. Không thử lại."""
            none = (None, {"prompt_tokens": None, "completion_tokens": None})
            if state["stopped"] or calls["total"] + state["used"] >= calls["limit"]:
                state["stopped"] = state["stopped"] or "đạt trần lượt gọi"
                return none
            wait = args.delay - (time.time() - state["last_call"])
            if wait > 0:
                time.sleep(wait)
            try:
                from google import genai
                client = genai.Client(api_key=llm_service.GEMINI_API_KEY)
                state["used"] += 1
                state["last_call"] = time.time()
                res = client.models.generate_content(model=llm_service.PRIMARY_MODEL, contents=prompt)
                if res.text and res.text.strip():
                    usage = getattr(res, "usage_metadata", None)
                    return (res.text.strip(), f"Google {llm_service.PRIMARY_MODEL}"), {
                        "prompt_tokens": getattr(usage, "prompt_token_count", None),
                        "completion_tokens": getattr(usage, "candidates_token_count", None)}
                return none
            except Exception as exc:  # noqa: BLE001
                msg = str(exc)
                state["last_call"] = time.time()
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                    state["stopped"] = "429/hết hạn ngạch"
                state.setdefault("errors", []).append(msg[:160])
                return none
        llm_service._sync_call_gemini_with_usage = one_call

    def sql(query, params=()):
        conn = get_db_connection()
        try:
            conn.execute(query, params)
            conn.commit()
        finally:
            conn.close()

    results: list = []
    started = datetime.now().isoformat(timespec="seconds")
    try:
        init_db()
        with TestClient(app) as client:
            for sc in scenarios:
                user = f"hs_{sc['id'].lower()}"
                ex = exercises[sc["exercise"]]
                for h in sc.get("history", []):
                    sql("INSERT INTO submissions(session_id,exercise_id,code,hint_level,passed_tests,total_tests,all_passed,llm_source,tutor_hint,action_type) "
                        "VALUES(?,?,?,?,?,?,?,?,?,?)",
                        (user, sc["exercise"], h["code"], h["hint_level"], h.get("passed", 0), h.get("total", len(ex["test_cases"])), 0,
                         "Pedagogical-Rule-Engine (Offline Fallback)", h.get("tutor_hint", ""), "ask_ai"))
                headers = {"Authorization": f"Bearer {create_token(user, 'student', user)}"}
                for level in sc["levels"]:
                    if args.real and state["stopped"]:
                        break
                    state["prompt"] = None
                    t0 = time.perf_counter()
                    resp = client.post("/api/submit", headers=headers, json={
                        "exercise_id": sc["exercise"], "code": sc["code"], "hint_level": level,
                        "session_id": user, "action_type": "ask_ai"})
                    wall = round((time.perf_counter() - t0) * 1000, 1)
                    body = resp.json() if resp.status_code == 200 else {}
                    rec = {"scenario": sc["id"], "level": level, "http": resp.status_code, "wall_ms": wall,
                           "reply": body.get("tutor_hint", ""), "llm_source": body.get("llm_source"),
                           "strategy": (body.get("adaptive_strategy") or {}).get("strategy"),
                           "diagnosis_focus": (body.get("adaptive_strategy") or {}).get("diagnosis_focus"),
                           "test_results": body.get("test_results"), "ast_analysis": body.get("ast_analysis"),
                           "mcp_trace_ms": [t.get("duration_ms") for t in body.get("mcp_trace", [])],
                           "prompt": state["prompt"] if (args.offline or args.real) else None}
                    if resp.status_code != 200:
                        rec["error"] = resp.text[:300]
                    results.append(rec)
                    if not args.quiet:
                        print(f"--- {sc['id']} Mức {level} [{rec['llm_source']}] {wall:.0f}ms ---\n{rec['reply']}\n", flush=True)
                    else:
                        print(f"{sc['id']} L{level} http={resp.status_code} src={rec['llm_source']} {wall:.0f}ms", flush=True)
    finally:
        os.environ.pop("PYTUTOR_DISABLE_LLM", None)
        for suffix in ("", "-wal", "-shm"):
            tmp_db.with_name(tmp_db.name + suffix).unlink(missing_ok=True)
            tmp_kb.with_name(tmp_kb.name + suffix).unlink(missing_ok=True)

    scs = {s["id"]: s for s in scenarios}
    ok_results = [r for r in results if r["http"] == 200]
    score_all(ok_results, profiles, exercises, scs)
    hash_after = sha256(real_db)
    gem_ok = sum(1 for r in ok_results if str(r.get("llm_source", "")).startswith("Google"))
    out = {
        "meta": {"tag": args.tag, "mode": "real" if args.real else "offline", "set": "holdout" if args.holdout else "redteam" if args.redteam else "dev",
                 "started": started, "finished": datetime.now().isoformat(timespec="seconds"), "git_head": git_head(),
                 "model_configured": llm_service.PRIMARY_MODEL if args.real else None, "scenarios": len(scenarios),
                 "replies": len(ok_results), "gemini_calls_this_run": state["used"], "gemini_success_replies": gem_ok,
                 "stopped_reason": state["stopped"], "errors_sample": state.get("errors", [])[:3],
                 "pytutor_db_unchanged": hash_before == hash_after, "note": args.note,
                 "command": "py evaluate_hint_levels.py " + " ".join(sys.argv[1:])},
        "summary": summarize(ok_results), "results": results,
    }
    out_path = EVAL / f"hint_levels_v510_{args.tag}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    out_path.with_suffix(".md").write_text(render_md(out), encoding="utf-8")
    if args.real:
        calls["total"] += state["used"]
        calls["runs"].append({"tag": args.tag, "calls": state["used"], "finished": out["meta"]["finished"],
                              "gemini_success_replies": gem_ok, "stopped": state["stopped"]})
        save_calls(calls)
    print(f"\nĐã ghi {out_path.relative_to(ROOT)} · pytutor.db không đổi: {hash_before == hash_after}")
    if args.real:
        print(f"Gemini: {state['used']} lượt gọi lần này, tổng {calls['total']}/{calls['limit']} · phản hồi từ Gemini {gem_ok}/{len(ok_results)}"
              + (f" · DỪNG: {state['stopped']}" if state["stopped"] else ""))
    s = out["summary"]["all_pass_by_level"]
    print(f"Đạt mọi kiểm tra: Mức 1 {s['1'][0]}/{s['1'][1]} · Mức 2 {s['2'][0]}/{s['2'][1]} · Mức 3 {s['3'][0]}/{s['3'][1]}")
    return 0 if len(ok_results) == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
