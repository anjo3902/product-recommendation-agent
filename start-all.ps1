# Product Recommendation Agent - Startup Script
# This script starts all required services: Ollama, Backend, and Frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Product Recommendation Agent Startup  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if services are already running
Write-Host "[1/4] Checking for existing services..." -ForegroundColor Yellow

$ollamaRunning = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
$pythonRunning = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
$nodeRunning = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

if ($ollamaRunning) {
    Write-Host "  [OK] Ollama is already running" -ForegroundColor Green
} else {
    Write-Host "  [!] Ollama not running - will start" -ForegroundColor Yellow
}

if ($pythonRunning) {
    Write-Host "  [OK] Backend is already running on port 8000" -ForegroundColor Green
} else {
    Write-Host "  [!] Backend not running - will start" -ForegroundColor Yellow
}

if ($nodeRunning) {
    Write-Host "  [OK] Frontend is already running on port 3000" -ForegroundColor Green
} else {
    Write-Host "  [!] Frontend not running - will start" -ForegroundColor Yellow
}

Write-Host ""

# Start Ollama if not running
if (-not $ollamaRunning) {
    Write-Host "[2/4] Starting Ollama..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Minimized
    Write-Host "  [OK] Ollama started" -ForegroundColor Green
    Start-Sleep -Seconds 3
} else {
    Write-Host "[2/4] Ollama already running - skipping" -ForegroundColor Green
}

# Start Backend if not running
if (-not $pythonRunning) {
    Write-Host "[3/4] Starting Backend API..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python -m uvicorn main:app --host 127.0.0.1 --port 8000" -WindowStyle Normal
    Write-Host "  [OK] Backend started on http://127.0.0.1:8000" -ForegroundColor Green
    Start-Sleep -Seconds 5
} else {
    Write-Host "[3/4] Backend already running - skipping" -ForegroundColor Green
}

# Start Frontend if not running
if (-not $nodeRunning) {
    Write-Host "[4/4] Starting Frontend..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm start" -WindowStyle Normal
    Write-Host "  [OK] Frontend starting on http://localhost:3000" -ForegroundColor Green
    Write-Host "  [i] Frontend will open in browser automatically" -ForegroundColor Cyan
} else {
    Write-Host "[4/4] Frontend already running - skipping" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All Services Started Successfully!    " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor White
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend:   http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "  API Docs:  http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
