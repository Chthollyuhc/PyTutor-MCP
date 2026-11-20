"""Đo tải nhẹ cho PyTutor trên backend cô lập (DB tạm, LLM tắt).

Chạy:  py evaluate_load_benchmark.py [--levels 1,5,10,20,30] [--per-level 40] [--port 8012] [--json]

- Tự khởi động một tiến trình uvicorn riêng với PYTUTOR_DB_PATH / PYTUTOR_KNOWLEDGE_DB_PATH trỏ tới tệp tạm
  và PYTUTOR_DISABLE_LLM=1; KHÔNG chạm pytutor.db gốc (so băm SHA-256 trước/sau) và không gọi LLM ngoài.
- Ba kịch bản ứng với ba hành động IDE: run-test (Chạy thử), ask_ai (Hỏi Gia sư AI, phản hồi rule-based
  offline), submit (Nộp bài, mã đạt).
- Giới hạn: một máy cá nhân, client và server chung máy, một tài khoản demo cho mọi luồng, không có độ trễ
  LLM thật. Số liệu chỉ mô tả chi phí của pipeline chấm (tiến trình MCP stdio + sandbox + SQLite), không
  phải năng lực phục vụ khi triển khai thật.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EXERCISE = "ex_01_sum_1_to_n"
PASS_CODE = "n = int(input())\ntotal = 0\nfor i in range(1, n + 1):\n    total += i\nprint(total)\n"
FAIL_CODE = "n = int(input())\ntotal = 0\nfor i in range(1, n):\n    total += i\nprint(total)\n"


def sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def http(base: str, method: str, path: str, body: dict | None = None, token: str | None = None, timeout: float = 120.0):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # timeout, connection reset
        return 0, {"error": type(e).__name__}


def percentile(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    k = (len(s) - 1) * p
    lo, hi = int(k), min(int(k) + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def scenario_request(base: str, token: str, name: str):
    sid = "load_" + uuid.uuid4().hex[:8]
    if name == "run-test":
        return http(base, "POST", "/api/run-test", {"exercise_id": EXERCISE, "code": PASS_CODE}, token)
    if name == "ask_ai":
        return http(base, "POST", "/api/submit", {"exercise_id": EXERCISE, "code": FAIL_CODE, "hint_level": 1,
                                                  "session_id": sid, "action_type": "ask_ai"}, token)
    return http(base, "POST", "/api/submit", {"exercise_id": EXERCISE, "code": PASS_CODE, "hint_level": 1,
                                              "session_id": sid, "action_type": "submit"}, token)


def run_level(base: str, token: str, name: str, concurrency: int, total: int) -> dict:
    def one(_):
        t0 = time.perf_counter()
        status, _body = scenario_request(base, token, name)
        return status, (time.perf_counter() - t0) * 1000.0

    t_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        results = list(pool.map(one, range(total)))
    wall = time.perf_counter() - t_start
    ok = [ms for st, ms in results if st == 200]
    statuses: dict[str, int] = {}
    for st, _ms in results:
        statuses[str(st)] = statuses.get(str(st), 0) + 1
    return {
        "scenario": name, "concurrency": concurrency, "requests": total,
        "ok": len(ok), "error_rate": round(1 - len(ok) / total, 4), "statuses": statuses,
        "p50_ms": round(percentile(ok, 0.50), 1), "p95_ms": round(percentile(ok, 0.95), 1),
        "max_ms": round(max(ok), 1) if ok else None,
        "mean_ms": round(statistics.fmean(ok), 1) if ok else None,
        "throughput_rps": round(len(ok) / wall, 2), "wall_s": round(wall, 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="1,5,10,20,30")
    ap.add_argument("--per-level", type=int, default=40, help="Số yêu cầu tối thiểu mỗi mức (>= 2 x concurrency)")
    ap.add_argument("--port", type=int, default=8012)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "evaluation" / "load_benchmark_results.json"))
    args = ap.parse_args()
    levels = [int(x) for x in args.levels.split(",") if x.strip()]

    real_db = ROOT / "pytutor.db"
    hash_before = sha256(real_db)
    tmp = Path(tempfile.gettempdir())
    tag = uuid.uuid4().hex
    tmp_db, tmp_kb = tmp / f"pytutor_load_{tag}.db", tmp / f"pytutor_load_kb_{tag}.sqlite3"
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTUTOR_DISABLE_LLM="1",
               PYTUTOR_DB_PATH=str(tmp_db), PYTUTOR_KNOWLEDGE_DB_PATH=str(tmp_kb))
    base = f"http://127.0.0.1:{args.port}"
    log_path = tmp / f"pytutor_load_{tag}.log"
    log = open(log_path, "w", encoding="utf-8")
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1",
                               "--port", str(args.port), "--log-level", "warning"],
                              cwd=str(ROOT), env=env, stdout=log, stderr=subprocess.STDOUT)
    rows: list[dict] = []
    try:
        for _ in range(120):
            st, _b = http(base, "GET", "/api/health", timeout=2.0)
            if st == 200:
                break
            if server.poll() is not None:
                print("Backend cô lập không khởi động được; xem log:", log_path)
                return 2
            time.sleep(0.5)
        else:
            print("Hết thời gian chờ backend cô lập.")
            return 2
        st, body = http(base, "POST", "/api/auth/login", {"username": "student", "password": "student123"})
        if st != 200:
            print("Đăng nhập tài khoản demo thất bại, HTTP", st)
            return 2
        token = body["access_token"]
        for name in ("run-test", "ask_ai", "submit"):  # khởi động ấm
            scenario_request(base, token, name)
        for name in ("run-test", "ask_ai", "submit"):
            for c in levels:
                total = max(args.per_level, 2 * c)
                row = run_level(base, token, name, c, total)
                rows.append(row)
                if not args.json:
                    print(f"{name:9s} c={c:<3d} n={total:<3d} ok={row['ok']:<3d} p50={row['p50_ms']} ms "
                          f"p95={row['p95_ms']} ms max={row['max_ms']} ms rps={row['throughput_rps']} "
                          f"lỗi={row['error_rate']:.1%} {row['statuses']}")
    finally:
        server.terminate()
        try:
            server.wait(timeout=15)
        except subprocess.TimeoutExpired:
            server.kill()
        log.close()
        for p in (tmp_db, Path(str(tmp_db) + "-wal"), Path(str(tmp_db) + "-shm"), tmp_kb, log_path):
            try:
                p.unlink()
            except OSError:
                pass

    result = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "offline (PYTUTOR_DISABLE_LLM=1), DB/KB tạm, client và server cùng máy",
        "python": sys.version.split()[0], "cpu_count": os.cpu_count(),
        "real_db_unchanged": hash_before == sha256(real_db),
        "levels": levels, "rows": rows,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("pytutor.db gốc không đổi:", result["real_db_unchanged"], "· kết quả:", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
