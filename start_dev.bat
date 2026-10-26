@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo ======================================================================
echo  PyTutor - Intelligent Tutoring System (MCP v5.0 NEU LMS)
echo  Sinh vien: Tran Minh Khanh (SV K65 CNTT - MSV: 11236131)
echo ======================================================================
echo.

set PY_CMD=py -3
where py >nul 2>nul
if %errorlevel% neq 0 (
    set PY_CMD=python
)
if exist venv\Scripts\python.exe (
    set PY_CMD=venv\Scripts\python.exe
) else if exist .venv\Scripts\python.exe (
    set PY_CMD=.venv\Scripts\python.exe
)

echo [1/2] Starting FastAPI Backend (Host: 127.0.0.1, Port: 8000)...
start "PyTutor Backend" /D "%~dp0" cmd /k "%PY_CMD% -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Vite Frontend (Port: 5173)...
start "PyTutor Frontend" /D "%~dp0frontend" cmd /k "npm.cmd run dev"

echo.
echo ======================================================================
echo  He thong da khoi chay thanh cong!
echo   * Cong Sinh vien / Giang vien: http://localhost:5173
echo   * Backend API (Swagger UI):    http://127.0.0.1:8000/docs
echo   * True MCP Health Check:       http://127.0.0.1:8000/api/health
echo ======================================================================
echo.
pause
