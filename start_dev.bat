@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1

echo ======================================================================
echo  PyTutor - Intelligent Tutoring System (MCP Architecture)
echo ======================================================================
echo.
echo [1/2] Starting FastAPI Backend on port 8000...
start "PyTutor Backend" /D "%~dp0" cmd /k "py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting Vite Frontend on port 5173...
start "PyTutor Frontend" /D "%~dp0frontend" cmd /k "npm.cmd run dev"

echo.
echo ======================================================================
echo  System started successfully!
echo   Frontend: http://localhost:5173
echo   Backend:  http://127.0.0.1:8000/docs
echo ======================================================================
echo.
pause
