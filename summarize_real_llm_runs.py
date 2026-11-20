"""Tổng hợp nhiều lần chạy `evaluate_real_llm.py` thành tỷ lệ theo từng ca.

Chạy:  py summarize_real_llm_runs.py [--dir evaluation/runs] [--md docs/REAL_LLM_RUNS_SUMMARY.md]

Mỗi tệp `run_*.json` là một lần chạy đầy đủ 22 ca với mô hình thật. Với mỗi ca đếm: số lần bộ lọc đầu ra chặn
hoặc thay thế phản hồi, số lần kiểm tra tất định không đạt, số lần mô hình trả lời thành công. Mục đích là ước lượng
mức DAO ĐỘNG giữa các lần chạy thay vì dựa vào một mẫu. Không thay cho việc chấm tay chất lượng sư phạm.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent


def load(dir_: Path) -> list[dict]:
    runs = []
    for p in sorted(dir_.glob("run_*.json")):
        runs.append(json.loads(p.read_text(encoding="utf-8")))
    return runs


def summarize(runs: list[dict]) -> dict:
    per = defaultdict(lambda: {"runs": 0, "guard_intervened": 0, "check_failed": 0, "success": 0, "guards": defaultdict(int)})
    for run in runs:
        for c in run["results"]["gemini"]:
            row = per[c["id"]]
            row["runs"] += 1
            inter = c.get("interaction") or {}
            guard = inter.get("output_guard")
            status = inter.get("status")
            if status in ("blocked", "blocked_fallback"):
                row["guard_intervened"] += 1
            if status == "success":
                row["success"] += 1
            if guard and guard != "allowed":
                row["guards"][guard] += 1
            checks = c.get("auto_checks") or {}
            if any(v is False for v in checks.values()):
                row["check_failed"] += 1
    return {"n_runs": len(runs), "per_case": {k: {**v, "guards": dict(v["guards"])} for k, v in sorted(per.items())}}


def render_md(res: dict) -> str:
    n = res["n_runs"]
    lines = [
        "# Tổng hợp nhiều lần chạy với mô hình thật",
        "",
        f"> Sinh bởi `summarize_real_llm_runs.py` từ **{n} lần chạy** `evaluate_real_llm.py` (cùng mã nguồn, cùng 22 ca, mô hình `gemini-3.5-flash-lite`).",
        "> Chỉ đếm hành vi của bộ lọc và kiểm tra tất định; **không** nói gì về chất lượng sư phạm. Ca không gọi mô hình (S1, S4) luôn hiện 0 lần thành công.",
        "",
        "| Ca | Bị bộ lọc chặn/thay | Kiểm tra tất định không đạt | Mô hình trả lời thành công | Tín hiệu bộ lọc |",
        "|---|---:|---:|---:|---|",
    ]
    for cid, r in res["per_case"].items():
        guards = ", ".join(f"{k} ×{v}" for k, v in r["guards"].items()) or "—"
        lines.append(f"| {cid} | {r['guard_intervened']}/{r['runs']} | {r['check_failed']}/{r['runs']} | {r['success']}/{r['runs']} | {guards} |")
    flaky = [cid for cid, r in res["per_case"].items() if 0 < r["guard_intervened"] < r["runs"]]
    always = [cid for cid, r in res["per_case"].items() if r["guard_intervened"] == r["runs"] and r["runs"]]
    lines += ["", f"- Ca dao động (bị chặn một số lần, không phải mọi lần): {', '.join(flaky) or 'không có'}.",
              f"- Ca luôn bị chặn: {', '.join(always) or 'không có'} (S2 và H3 bị chặn là hành vi mong đợi hoặc đã biết)."]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(ROOT / "evaluation" / "runs"))
    ap.add_argument("--md", default="")
    args = ap.parse_args()
    runs = load(Path(args.dir))
    if not runs:
        print("Không có tệp run_*.json trong", args.dir)
        return 2
    res = summarize(runs)
    md = render_md(res)
    print(md)
    if args.md:
        Path(args.md).write_text(md, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
