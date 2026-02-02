# Complete System Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Product Recommendation System Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing Python processes
Write-Host "Stopping existing processes..." -ForegroundColor Yellow
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Backend
Write-Host "Starting Backend Server..." -ForegroundColor Cyan
$projectPath = "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent"
$backendScript = @"
Set-Location '$projectPath'
`$env:PYTHONIOENCODING='utf-8'
Write-Host 'Backend Server Starting on http://localhost:8000' -ForegroundColor Green
python -m uvicorn main:app --host 127.0.0.1 --port 8000
"@

$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -PassThru -WindowStyle Normal
Write-Host "Backend started (PID: $($backendJob.Id))" -ForegroundColor Green
Write-Host "Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Start Frontend
Write-Host ""
Write-Host "Starting Frontend..." -ForegroundColor Cyan
Set-Location "$projectPath\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  System Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""

npm start
