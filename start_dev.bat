@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo ======================================================================
echo 🎓 KHỞI CHẠY HỆ THỐNG PYTUTOR - INTELLIGENT TUTORING SYSTEM (MCP)
echo ======================================================================
echo.
echo [1/2] Đang khởi động FastAPI Backend (Port 8000)...
start "PyTutor Backend (FastAPI + MCP Host)" cmd /k "chcp 65001 > nul && set PYTHONIOENCODING=utf-8 && py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Đang khởi động Vite Frontend (Port 5173)...
start "PyTutor Frontend (React + Monaco Editor)" cmd /k "cd frontend && npm.cmd run dev"

echo.
echo ======================================================================
echo 🎉 HỆ THỐNG ĐÃ ĐƯỢC KHỞI CHẠY THÀNH CÔNG!
echo ======================================================================
echo.
echo  👉 Giao diện Học viên:   http://localhost:5173
echo  👉 Tài liệu Backend API: http://127.0.0.1:8000/docs
echo  👉 Kiểm tra Health:      http://127.0.0.1:8000/api/health
echo.
echo Nhấn phím bất kỳ để đóng cửa sổ điều khiển này (hai dịch vụ vẫn tiếp tục chạy trong cửa sổ riêng)...
pause > nul
