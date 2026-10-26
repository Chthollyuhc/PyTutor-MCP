#!/usr/bin/env bash
# PyTutor - Intelligent Tutoring System (MCP v5.0 NEU LMS)
# Sinh vien: Tran Minh Khanh (SV K65 CNTT - MSV: 11236131)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONIOENCODING=utf-8
export PYTHONUNBUFFERED=1

echo "======================================================================"
echo " PyTutor - Intelligent Tutoring System (MCP v5.0 NEU LMS)"
echo " Sinh vien: Tran Minh Khanh (SV K65 CNTT - MSV: 11236131)"
echo "======================================================================"
echo ""

PY_CMD="python3"
if [ -f "venv/bin/python" ]; then
    PY_CMD="venv/bin/python"
elif [ -f ".venv/bin/python" ]; then
    PY_CMD=".venv/bin/python"
fi

echo "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000..."
$PY_CMD -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "[2/2] Starting Vite Frontend on http://localhost:5173..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT INT TERM

echo ""
echo "======================================================================"
echo " Hệ thống đã khởi chạy thành công!"
echo "  * Giao diện Web: http://localhost:5173"
echo "  * Backend API:   http://127.0.0.1:8000/docs"
echo "======================================================================"
echo "Nhấn Ctrl+C để dừng cả hai tiến trình."

wait
