# Khởi chạy đồng thời Backend và Frontend cho PyTutor
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🎓 KHỞI CHẠY HỆ THỐNG PYTUTOR - INTELLIGENT TUTORING SYSTEM (MCP)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Khởi động Backend
Write-Host "[1/2] Đang khởi động FastAPI Backend (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONIOENCODING='utf-8'; `$Host.UI.RawUI.WindowTitle='PyTutor Backend (FastAPI + MCP Host)'; py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

# 2. Khởi động Frontend
Write-Host "[2/2] Đang khởi động Vite Frontend (Port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$Host.UI.RawUI.WindowTitle='PyTutor Frontend (React + Monaco)'; cd '$PSScriptRoot\frontend'; npm.cmd run dev"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🎉 HỆ THỐNG ĐÃ ĐƯỢC KHỞI CHẠY THÀNH CÔNG!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " 👉 Giao diện Học viên:   http://localhost:5173" -ForegroundColor White
Write-Host " 👉 Tài liệu Backend API: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host " 👉 Kiểm tra Health:      http://127.0.0.1:8000/api/health" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
