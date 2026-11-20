"""Benchmark tất định cho truy xuất RAG cục bộ (TF-IDF thưa trên SQLite), không gọi LLM, không cần mạng.

Dựng một chỉ mục TẠM từ `docs/knowledge_base/` (không đụng `pytutor_knowledge.sqlite3`), rồi đo trên
bộ câu hỏi cố định `evaluation/rag_questions.json`:
- hit@1, hit@3, MRR cho câu hỏi có nội dung trong KB (đúng = trả về đúng mục kỳ vọng)
- answered_rate: tỷ lệ câu trong KB có ít nhất một nguồn vượt ngưỡng
- no_source_accuracy cho câu hỏi ngoài KB (đúng = KHÔNG trả nguồn nào → hệ thống sẽ nói "không có tài liệu phù hợp")
- độ trễ truy xuất median / p95 / max (ms)

Phạm vi: chỉ đo thành phần truy xuất trên KB nội bộ nhỏ do dự án biên soạn (chưa phải giáo trình NEU);
không đo chất lượng câu trả lời của LLM.

Chạy:  py evaluate_rag_benchmark.py [--json] [--min-score 0.12]
"""
from __future__ import annotations

import json
import statistics
import sys
import tempfile
import time
from pathlib import Path

from backend.rag.retriever import KB_ROOT, MIN_RELEVANCE, ingest_knowledge_base, retrieve_knowledge

QUESTIONS_PATH = Path(__file__).resolve().parent / "evaluation" / "rag_questions.json"
TOP_K = 3
LATENCY_REPEATS = 20


def _percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))] if ordered else 0.0


def run(min_score: float = MIN_RELEVANCE, questions_path: Path = QUESTIONS_PATH, kb_root: Path = KB_ROOT) -> dict:
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="pytutor_rag_bench_") as tmp:
        index = Path(tmp) / "kb.sqlite3"
        chunks = ingest_knowledge_base(kb_root, index)
        latencies: list[float] = []

        def search(question: str) -> list[dict]:
            start = time.perf_counter()
            docs = retrieve_knowledge(question, top_k=TOP_K, index_path=index, min_score=min_score)
            latencies.append((time.perf_counter() - start) * 1000)
            return docs

        in_rows, by_topic = [], {}
        for case in questions["in_kb"]:
            docs = search(case["question"])
            rank = next((pos for pos, doc in enumerate(docs, 1)
                         if doc["source"] == case["expected_source"] and doc["section"] in case["expected_sections"]), None)
            in_rows.append({"id": case["id"], "topic": case["topic"], "rank": rank, "returned": len(docs),
                            "top_section": docs[0]["section"] if docs else None,
                            "top_score": docs[0]["score"] if docs else None})
            topic = by_topic.setdefault(case["topic"], {"total": 0, "hit1": 0, "hit3": 0})
            topic["total"] += 1
            topic["hit1"] += int(rank == 1)
            topic["hit3"] += int(rank is not None)

        out_rows, by_category = [], {}
        for case in questions["out_of_kb"]:
            docs = search(case["question"])
            out_rows.append({"id": case["id"], "category": case["category"], "no_source": not docs,
                             "top_section": docs[0]["section"] if docs else None,
                             "top_score": docs[0]["score"] if docs else None})
            cat = by_category.setdefault(case["category"], {"total": 0, "no_source": 0})
            cat["total"] += 1
            cat["no_source"] += int(not docs)

        for _ in range(LATENCY_REPEATS):
            for case in questions["in_kb"] + questions["out_of_kb"]:
                search(case["question"])

    n_in, n_out = len(in_rows), len(out_rows)

    def rate(part: float, whole: int) -> float:
        return round(part / whole * 100, 2) if whole else 0.0

    hit1 = sum(1 for r in in_rows if r["rank"] == 1)
    hit3 = sum(1 for r in in_rows if r["rank"] is not None)
    mrr = round(sum(1 / r["rank"] for r in in_rows if r["rank"]) / n_in, 4) if n_in else 0.0
    answered = sum(1 for r in in_rows if r["returned"] > 0)
    no_source = sum(1 for r in out_rows if r["no_source"])
    return {
        "scope": "retrieval-only benchmark on the internal project-authored knowledge base; not an answer-quality study",
        "questions_version": questions["version"], "kb_chunks": chunks, "top_k": TOP_K, "min_score": min_score,
        "in_kb": {"total": n_in, "hit_at_1": hit1, "hit_at_1_percent": rate(hit1, n_in),
                  "hit_at_3": hit3, "hit_at_3_percent": rate(hit3, n_in), "mrr": mrr,
                  "answered": answered, "answered_rate_percent": rate(answered, n_in),
                  "by_topic": by_topic, "missed_ids": [r["id"] for r in in_rows if r["rank"] is None]},
        "out_of_kb": {"total": n_out, "no_source": no_source, "no_source_accuracy_percent": rate(no_source, n_out),
                      "by_category": by_category,
                      "wrongly_sourced": [f'{r["id"]}→{r["top_section"]} ({r["top_score"]})' for r in out_rows if not r["no_source"]]},
        "latency": {"samples": len(latencies), "median_ms": round(statistics.median(latencies), 4),
                    "p95_ms": round(_percentile(latencies, 0.95), 4), "max_ms": round(max(latencies), 4)},
        "details": {"in_kb": in_rows, "out_of_kb": out_rows},
    }


def print_report(result: dict) -> None:
    i, o, lat = result["in_kb"], result["out_of_kb"], result["latency"]
    print(f"RAG retrieval benchmark — questions v{result['questions_version']}, {result['kb_chunks']} đoạn KB, "
          f"top_k={result['top_k']}, min_score={result['min_score']}")
    print(f"Phạm vi: {result['scope']}\n")
    print(f"Câu hỏi trong KB ({i['total']}): hit@1 {i['hit_at_1']}/{i['total']} = {i['hit_at_1_percent']}% | "
          f"hit@3 {i['hit_at_3']}/{i['total']} = {i['hit_at_3_percent']}% | MRR {i['mrr']} | "
          f"có nguồn {i['answered']}/{i['total']} = {i['answered_rate_percent']}%")
    for topic, item in sorted(i["by_topic"].items()):
        print(f"  {topic:<16} hit@1 {item['hit1']}/{item['total']}   hit@3 {item['hit3']}/{item['total']}")
    if i["missed_ids"]:
        print("  Không tìm đúng mục (top-3):", ", ".join(i["missed_ids"]))
    print(f"\nCâu hỏi ngoài KB ({o['total']}): trả 'không có nguồn' đúng {o['no_source']}/{o['total']} = {o['no_source_accuracy_percent']}%")
    for cat, item in sorted(o["by_category"].items()):
        print(f"  {cat:<20} {item['no_source']}/{item['total']}")
    if o["wrongly_sourced"]:
        print("  Gắn nguồn không phù hợp:", "; ".join(o["wrongly_sourced"]))
    print(f"\nĐộ trễ truy xuất (ms): median {lat['median_ms']} | p95 {lat['p95_ms']} | max {lat['max_ms']} (n={lat['samples']})")


if __name__ == "__main__":
    threshold = MIN_RELEVANCE
    if "--min-score" in sys.argv:
        threshold = float(sys.argv[sys.argv.index("--min-score") + 1])
    report = run(min_score=threshold)
    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
