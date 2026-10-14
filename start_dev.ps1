# Khởi chạy đồng thời Backend và Frontend cho PyTutor
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "PyTutor - Intelligent Tutoring System (MCP Architecture)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Khởi động Backend
Write-Host "[1/2] Dang khoi dong FastAPI Backend (Port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONIOENCODING='utf-8'; Set-Location '$PSScriptRoot'; py -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

# 2. Khởi động Frontend
Write-Host "[2/2] Dang khoi dong Vite Frontend (Port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\frontend'; npm.cmd run dev"

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "HE THONG DA DUOC KHOI CHAY THANH CONG!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " 👉 Giao dien Hoc vien:   http://localhost:5173" -ForegroundColor White
Write-Host " 👉 Tai lieu Backend API: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host " 👉 Kiem tra Health:      http://127.0.0.1:8000/api/health" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan
