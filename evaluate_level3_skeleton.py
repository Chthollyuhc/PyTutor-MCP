"""Đo bước che logic của khung mã Mức 3 (`enforce_level3_skeleton`) bằng cách CHẠY khung đã che.

Chạy:  py evaluate_level3_skeleton.py [--holdout] [--json] [--show ID]

Ý tưởng: trường hợp xấu nhất ở Mức 3 là mô hình trả nguyên một lời giải đầy đủ trong khối code.
Với mỗi lời giải trong `evaluation/level3_solutions.json` (5 bài seed, nhiều phong cách viết):
  1. xác nhận lời giải gốc đạt mọi kiểm thử của bài (nếu không, ca bị loại khỏi phép đo);
  2. bọc lời giải trong khối ```python và cho qua bước che;
  3. chạy khung đã che trên chính bộ kiểm thử của bài.
Chỉ số:
  - solution_survives : khung đã che vẫn đạt MỌI kiểm thử  → lời giải lọt nguyên vẹn (rò rỉ).
  - tests_passed_rate : tỷ lệ kiểm thử mà khung đã che còn đạt (đạt lẻ tẻ có thể do in hằng như "NO").
  - valid_python      : khung đã che còn là Python hợp lệ (người học chạy thử được).
  - masked_lines      : số dòng bị che / số dòng lệnh.

Không gọi LLM, không dùng DB (bài tập lấy từ seed `mcp_server/exercises_data.py`, chạy bằng sandbox của dự án).
Giới hạn: lời giải do dự án tự soạn; đây là tập phát triển của bộ luật che, không phải tập giữ riêng.
Phép đo chỉ nói về việc LỜI GIẢI CHẠY ĐƯỢC có lọt hay không, không nói khung còn lại có ích cho người học hay không.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

from backend.guardrails import enforce_level3_skeleton
from mcp_server.exercises_data import EXERCISES
from mcp_server.sandbox import run_test_cases

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "evaluation" / "level3_solutions.json"
HOLDOUT = ROOT / "evaluation" / "level3_solutions_holdout.json"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def _code_lines(code: str) -> list[str]:
    return [ln for ln in code.splitlines() if ln.strip() and not ln.strip().startswith("#")]


def run(corpus_path: Path = CORPUS) -> dict:
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    tests = {ex["id"]: ex["test_cases"] for ex in EXERCISES}
    rows, excluded = [], []
    for sol in corpus["solutions"]:
        cases = tests[sol["exercise"]]
        base = run_test_cases(sol["code"], cases)
        if not base.get("all_passed"):
            excluded.append(sol["id"])
            continue
        masked_reply, masked = enforce_level3_skeleton("Khung mã:\n```python\n" + sol["code"] + "```\n")
        block = re.search(r"```python\n(.*?)```", masked_reply, flags=re.DOTALL).group(1)
        try:
            ast.parse(block)
            valid = True
        except SyntaxError:
            valid = False
        after = run_test_cases(block, cases) if valid else {"passed_tests": 0, "all_passed": False}
        rows.append({
            "id": sol["id"], "exercise": sol["exercise"], "style": sol["style"],
            "code_lines": len(_code_lines(sol["code"])), "masked_lines": masked,
            "valid_python": valid, "tests_total": len(cases),
            "tests_passed_after": after.get("passed_tests", 0),
            "solution_survives": bool(after.get("all_passed")),
            "masked_block": block,
        })
    n = len(rows)
    total_tests = sum(r["tests_total"] for r in rows)
    return {
        "corpus_version": corpus["version"], "cases": n, "excluded_baseline_fail": excluded,
        "solution_survives": sum(r["solution_survives"] for r in rows),
        "survivors": [r["id"] for r in rows if r["solution_survives"]],
        "valid_python": sum(r["valid_python"] for r in rows),
        "tests_passed_after": sum(r["tests_passed_after"] for r in rows), "tests_total": total_tests,
        "masked_lines": sum(r["masked_lines"] for r in rows), "code_lines": sum(r["code_lines"] for r in rows),
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--holdout", action="store_true", help="Đo trên tập giữ riêng (không dùng để chỉnh luật)")
    ap.add_argument("--show", default="", help="In khung đã che của một ca, ví dụ --show L08")
    args = ap.parse_args()
    res = run(HOLDOUT if args.holdout else CORPUS)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0
    print(f"Che khung mã Mức 3 — corpus v{res['corpus_version']}, {res['cases']} lời giải đạt kiểm thử gốc "
          f"(loại: {res['excluded_baseline_fail'] or 'không'})")
    for r in res["rows"]:
        flag = "LỌT" if r["solution_survives"] else "ok "
        print(f"  {flag} {r['id']} {r['exercise']:22s} {r['style']:24s} che {r['masked_lines']}/{r['code_lines']} dòng · "
              f"còn đạt {r['tests_passed_after']}/{r['tests_total']} kiểm thử · hợp lệ={r['valid_python']}")
    n = res["cases"]
    print(f"\nLời giải lọt nguyên vẹn sau khi che: {res['solution_survives']}/{n} {res['survivors']}")
    print(f"Khung còn là Python hợp lệ: {res['valid_python']}/{n}")
    print(f"Kiểm thử còn đạt sau khi che: {res['tests_passed_after']}/{res['tests_total']}")
    print(f"Dòng lệnh bị che: {res['masked_lines']}/{res['code_lines']}")
    if args.show:
        for r in res["rows"]:
            if r["id"] == args.show:
                print(f"\n--- {r['id']} sau khi che ---\n{r['masked_block']}")
    return 1 if (res["solution_survives"] and not args.holdout) else 0  # chỉ tập phát triển là ngưỡng phát hành


if __name__ == "__main__":
    sys.exit(main())
