"""Kiểm tra phần mô hình người học v3 với LLM thật (Gemini) trên hồ sơ tổng hợp.

Chạy:  py evaluate_real_llm_learner_model.py [--delay 1.2] [--output evaluation/real_llm_learner_model_v56.json]
       py evaluate_real_llm_learner_model.py --from-json   (dựng lại phần tổng hợp từ tệp đã có, không gọi API)

Phạm vi: 8 hồ sơ tổng hợp (evaluation/learner_profiles.json) x 2 trạng thái sai (sai lần đầu, sai lặp lại) x 3 mức = 48 lượt gọi
cùng một bài tập mẫu. Chỉ ghi nhận: (1) mô hình có trả lời không (nguồn LLM, không rơi vào nhánh dự phòng), (2) phản hồi có để lộ mã nội bộ
của chính sách không, (3) khung mã ở Mức 3 có chứa biểu thức/lệnh in của lời giải không (so khớp mẫu chuỗi). KHÔNG chấm chất lượng sư phạm
và KHÔNG phải nghiên cứu kết quả học tập.

An toàn: DB tạm (evaluate_learner_model_policy đặt PYTUTOR_DB_PATH tạm và từ chối chạy nếu trỏ tới pytutor.db), chỉ dữ liệu giả lập,
không in/ghi API key. Cần GEMINI_API_KEY trong .env hoặc môi trường.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

INTERNAL = re.compile(r"granularity_|hint_reliance|concept_recurring|model_fields_used|learner_signals|adaptation|no_evidence|attempt_features", re.I)
# Dấu hiệu lời giải của bài mẫu "Chẵn hay lẻ": phép chia dư 2, so sánh với 0, hoặc lệnh in chuỗi kết quả đúng ('Le').
SOLUTION_LIKE = re.compile(r"%\s*2|==\s*0|print\(\s*['\"]Le['\"]", re.I)
CODE = "n = int(input())\nif n % 2 == 0:\n    print('Chan')\nelse:\n    print('le')\n"
EX = {"id": "ex_eval", "title": "Chẵn hay lẻ", "description": "Nhập số nguyên n. In 'Chan' nếu n chẵn, ngược lại in 'Le'."}


def fenced_blocks(hint: str) -> list[str]:
    return re.findall(r"```(?:python)?\n(.*?)```", hint or "", re.S)


def solution_like_in_blocks(hint: str) -> bool:
    for block in fenced_blocks(hint):
        for line in block.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and SOLUTION_LIKE.search(stripped):
                return True
    return False


def summarize(rows: list[dict]) -> dict:
    llm = [r for r in rows if r["source"] and r["source"] != "error" and "fallback" not in r["source"].lower() and "rule" not in r["source"].lower()]
    l3 = [r for r in rows if r["level"] == 3]
    return {
        "scope": "real-LLM smoke check of learner model v3 prompt section on synthetic profiles; NOT quality scoring, NOT learning outcome",
        "calls": len(rows),
        "llm_success": len(llm),
        "fallback_or_error": len(rows) - len(llm),
        "sources": sorted({r["source"] for r in rows}),
        "internal_code_leak": sum(bool(INTERNAL.search(r["hint"])) for r in rows),
        "level3_rows": len(l3),
        "level3_with_code_fence": sum(bool(fenced_blocks(r["hint"])) for r in l3),
        "level3_fenced_blocks_with_solution_like_lines": sum(solution_like_in_blocks(r["hint"]) for r in l3),
    }


async def run(args) -> int:
    sys.path.insert(0, str(ROOT))
    import evaluate_learner_model_policy as E  # đặt DB tạm + tắt LLM, từ chối pytutor.db

    os.environ.pop("PYTUTOR_DISABLE_LLM", None)
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    if not os.environ.get("GEMINI_API_KEY", "").strip():
        print("Thiếu GEMINI_API_KEY: dừng.")
        return 2
    if Path(os.environ["PYTUTOR_DB_PATH"]).expanduser().resolve() == (ROOT / "pytutor.db").resolve():
        print("Từ chối chạy: PYTUTOR_DB_PATH trỏ tới pytutor.db thật.")
        return 2

    from backend.adaptive_policy import select_hint_strategy
    from backend.database import compute_student_model, init_db
    from backend.llm_service import generate_tutor_hint

    states = [s for s in E.STATES if s[0] in ("fail_first", "fail_repeat")]
    init_db()
    rows = []
    for profile in E.load_profiles()["profiles"]:
        user = f"evalp_{profile['id']}"
        E.insert_profile(user, profile)
        model = compute_student_model(user)
        for name, tests, history, ast in states:
            for level in (1, 2, 3):
                strat = select_hint_strategy(level, tests, history, model, exercise_id=profile["target"])
                t0 = time.time()
                try:
                    hint, source, _meta = await generate_tutor_hint(EX, CODE, tests, ast, level, history, model, strat)
                    err = None
                except Exception as ex:  # ghi nhận, không dừng
                    hint, source, err = "", "error", repr(ex)[:200]
                rows.append({
                    "profile": profile["id"], "state": name, "level": level,
                    "strategy": strat["strategy"], "adaptations": strat["adaptation_codes"], "granularity": strat.get("granularity"),
                    "source": source, "error": err, "ms": int((time.time() - t0) * 1000), "chars": len(hint), "hint": hint,
                })
                print(f"{profile['id']:<24}{name:<12}L{level} {source[:30]:<30} {strat['strategy']} {strat['adaptation_codes']}", flush=True)
                await asyncio.sleep(args.delay)
    out = ROOT / args.output
    out.write_text(json.dumps({"model": "gemini-3.5-flash-lite", "summary": summarize(rows), "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summarize(rows), ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output", default="evaluation/real_llm_learner_model_v56.json")
    ap.add_argument("--delay", type=float, default=1.2)
    ap.add_argument("--from-json", action="store_true", help="Không gọi API: dựng lại phần tổng hợp từ --output đã có.")
    args = ap.parse_args()
    if args.from_json:
        path = ROOT / args.output
        data = json.loads(path.read_text(encoding="utf-8"))
        for r in data["rows"]:
            for key in ("level_label_ok", "internal_code_leak", "has_code_fence", "meta"):
                r.pop(key, None)
        data["summary"] = summarize(data["rows"])
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(data["summary"], ensure_ascii=False, indent=2))
        return 0
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
