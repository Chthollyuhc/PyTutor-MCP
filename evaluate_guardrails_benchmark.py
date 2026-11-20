"""Benchmark tất định cho Input/Output Guardrails & Anti-Spoil (không gọi LLM, không cần mạng, không cần DB).

Đo trên corpus phiên bản hóa `evaluation/guardrail_corpus.json`:
- leak_rate            = số tình huống tấn công mà phản hồi chứa lời giải vẫn tới được người học / tổng tình huống tấn công
- injection_block_rate = số đầu vào injection/ngoài phạm vi bị chặn / tổng
- false_positive_rate  = số câu hỏi (hoặc phản hồi gia sư) hợp lệ bị chặn nhầm / tổng hợp lệ
- độ trễ guard: median / p95 / max (ms)

Phạm vi: đây là kiểm thử kỹ thuật trên dữ liệu tổng hợp do dự án biên soạn; phản hồi "mô hình" là giả lập.
Kết quả KHÔNG nói lên chất lượng sư phạm hay hành vi của LLM thật.

Chạy:  py evaluate_guardrails_benchmark.py [--json]
"""
from __future__ import annotations

import json
import statistics
import sys
import time
from pathlib import Path

from backend.guardrails import GUARD_RULES_VERSION, check_student_input, check_student_output
from backend.llm_service import sanitize_spoil_code

CORPUS_PATH = Path(__file__).resolve().parent / "evaluation" / "guardrail_corpus.json"
LATENCY_REPEATS = 50


def _percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))
    return ordered[index]


def _timed(fn, *args) -> tuple[object, float]:
    start = time.perf_counter()
    result = fn(*args)
    return result, (time.perf_counter() - start) * 1000


def _reply_reaches_student(reply: str) -> tuple[bool, str]:
    """Mô phỏng đúng thứ tự xử lý của chat: sanitize khối code dài rồi kiểm tra output guard."""
    sanitized = sanitize_spoil_code(reply, hint_level=1, all_passed=False)
    safe, reason = check_student_output(reply)
    if safe:
        safe, reason = check_student_output(sanitized)
    return safe, reason


def run(corpus_path: Path = CORPUS_PATH) -> dict:
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    latencies_in: list[float] = []
    latencies_out: list[float] = []

    # 1) Tình huống tấn công đầu-cuối: rò rỉ khi input được cho qua VÀ phản hồi chứa lời giải cũng được cho qua.
    attack_rows, by_category = [], {}
    for case in corpus["attack_scenarios"]:
        (input_ok, input_reason), t_in = _timed(check_student_input, case["input"])
        (output_ok, output_reason), t_out = _timed(_reply_reaches_student, case["model_reply"])
        latencies_in.append(t_in)
        latencies_out.append(t_out)
        leaked = input_ok and output_ok
        stage = "leaked" if leaked else ("input_guard" if not input_ok else "output_guard")
        attack_rows.append({"id": case["id"], "category": case["category"], "leaked": leaked, "blocked_by": stage,
                            "reason": input_reason if not input_ok else output_reason})
        cat = by_category.setdefault(case["category"], {"total": 0, "leaked": 0})
        cat["total"] += 1
        cat["leaked"] += int(leaked)

    # 2) Đầu vào injection / ngoài phạm vi: phải bị chặn ở input guard.
    injection_rows = []
    for case in corpus["injection_inputs"]:
        (ok, reason), t_in = _timed(check_student_input, case["text"])
        latencies_in.append(t_in)
        injection_rows.append({"id": case["id"], "category": case["category"], "blocked": not ok, "reason": reason})

    # 3) Câu hỏi hợp lệ: không được chặn.
    benign_input_rows = []
    for case in corpus["benign_inputs"]:
        (ok, reason), t_in = _timed(check_student_input, case["text"])
        latencies_in.append(t_in)
        benign_input_rows.append({"id": case["id"], "category": case["category"], "blocked": not ok, "reason": reason})

    # 4) Phản hồi gia sư hợp lệ: không được chặn.
    benign_reply_rows = []
    for case in corpus["benign_replies"]:
        (ok, reason), t_out = _timed(_reply_reaches_student, case["text"])
        latencies_out.append(t_out)
        benign_reply_rows.append({"id": case["id"], "category": case["category"], "blocked": not ok, "reason": reason})

    # Độ trễ: lặp lại toàn bộ corpus để có mẫu ổn định hơn.
    all_inputs = [c["input"] for c in corpus["attack_scenarios"]] + [c["text"] for c in corpus["injection_inputs"] + corpus["benign_inputs"]]
    all_replies = [c["model_reply"] for c in corpus["attack_scenarios"]] + [c["text"] for c in corpus["benign_replies"]]
    for _ in range(LATENCY_REPEATS):
        for text in all_inputs:
            latencies_in.append(_timed(check_student_input, text)[1])
        for text in all_replies:
            latencies_out.append(_timed(_reply_reaches_student, text)[1])

    def rate(part: int, whole: int) -> float:
        return round(part / whole * 100, 2) if whole else 0.0

    leaks = sum(r["leaked"] for r in attack_rows)
    injection_blocked = sum(r["blocked"] for r in injection_rows)
    fp_inputs = sum(r["blocked"] for r in benign_input_rows)
    fp_replies = sum(r["blocked"] for r in benign_reply_rows)

    def latency_summary(values: list[float]) -> dict:
        return {"samples": len(values), "median_ms": round(statistics.median(values), 4),
                "p95_ms": round(_percentile(values, 0.95), 4), "max_ms": round(max(values), 4)}

    return {
        "scope": "deterministic guard benchmark on a synthetic corpus; simulated model replies; not an LLM quality study",
        "corpus_version": corpus["version"],
        "guard_rules_version": GUARD_RULES_VERSION,
        "attack": {"total": len(attack_rows), "leaked": leaks, "leak_rate_percent": rate(leaks, len(attack_rows)),
                   "block_rate_percent": rate(len(attack_rows) - leaks, len(attack_rows)),
                   "by_category": by_category, "leaked_ids": [r["id"] for r in attack_rows if r["leaked"]]},
        "injection": {"total": len(injection_rows), "blocked": injection_blocked,
                      "block_rate_percent": rate(injection_blocked, len(injection_rows)),
                      "missed_ids": [r["id"] for r in injection_rows if not r["blocked"]]},
        "benign_inputs": {"total": len(benign_input_rows), "false_positives": fp_inputs,
                          "false_positive_rate_percent": rate(fp_inputs, len(benign_input_rows)),
                          "false_positive_ids": [r["id"] for r in benign_input_rows if r["blocked"]]},
        "benign_replies": {"total": len(benign_reply_rows), "false_positives": fp_replies,
                           "false_positive_rate_percent": rate(fp_replies, len(benign_reply_rows)),
                           "false_positive_ids": [f'{r["id"]}:{r["reason"]}' for r in benign_reply_rows if r["blocked"]]},
        "latency": {"input_guard": latency_summary(latencies_in), "output_guard": latency_summary(latencies_out)},
        "details": {"attack": attack_rows, "injection": injection_rows,
                    "benign_inputs": benign_input_rows, "benign_replies": benign_reply_rows},
    }


def print_report(result: dict) -> None:
    a, i, bi, br, lat = (result["attack"], result["injection"], result["benign_inputs"],
                         result["benign_replies"], result["latency"])
    print(f"Guardrail benchmark — corpus v{result['corpus_version']}, guard rules v{result['guard_rules_version']}")
    print(f"Phạm vi: {result['scope']}\n")
    print(f"{'Nhóm':<38}{'Tổng':>6}{'Kết quả':>28}")
    print(f"{'Tình huống tấn công (đầu-cuối)':<38}{a['total']:>6}{'rò rỉ ' + str(a['leaked']) + ' → leak_rate ' + str(a['leak_rate_percent']) + '%':>28}")
    print(f"{'Đầu vào injection/ngoài phạm vi':<38}{i['total']:>6}{'chặn ' + str(i['blocked']) + ' → ' + str(i['block_rate_percent']) + '%':>28}")
    print(f"{'Câu hỏi hợp lệ':<38}{bi['total']:>6}{'chặn nhầm ' + str(bi['false_positives']) + ' → FPR ' + str(bi['false_positive_rate_percent']) + '%':>28}")
    print(f"{'Phản hồi gia sư hợp lệ':<38}{br['total']:>6}{'chặn nhầm ' + str(br['false_positives']) + ' → FPR ' + str(br['false_positive_rate_percent']) + '%':>28}")
    print("\nTấn công theo dạng (rò rỉ/tổng):")
    for name, item in sorted(a["by_category"].items()):
        print(f"  {name:<24}{item['leaked']}/{item['total']}")
    if a["leaked_ids"]:
        print("  Rò rỉ:", ", ".join(a["leaked_ids"]))
    if i["missed_ids"]:
        print("  Injection bị lọt:", ", ".join(i["missed_ids"]))
    if bi["false_positive_ids"]:
        print("  Câu hỏi hợp lệ bị chặn:", ", ".join(bi["false_positive_ids"]))
    if br["false_positive_ids"]:
        print("  Phản hồi hợp lệ bị chặn:", ", ".join(br["false_positive_ids"]))
    print("\nĐộ trễ guard (ms):")
    for name in ("input_guard", "output_guard"):
        item = lat[name]
        print(f"  {name:<14}median {item['median_ms']:<9} p95 {item['p95_ms']:<9} max {item['max_ms']:<9} (n={item['samples']})")


HOLDOUT_PATH = CORPUS_PATH.with_name("guardrail_holdout.json")


if __name__ == "__main__":
    # --holdout: đo trên tập giữ riêng (không dùng để chỉnh luật; chỉ báo cáo, không phải điều kiện phát hành).
    use_holdout = "--holdout" in sys.argv
    report = run(HOLDOUT_PATH if use_holdout else CORPUS_PATH)
    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    # Điều kiện phát hành: không rò rỉ trên corpus phát triển cố định.
    sys.exit(0 if use_holdout or report["attack"]["leaked"] == 0 else 1)
