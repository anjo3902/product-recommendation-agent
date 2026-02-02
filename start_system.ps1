# Complete System Startup Script
# Starts both Backend (FastAPI) and Frontend (React)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Product Recommendation System Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Start Backend
Write-Host "1️⃣  Starting Backend Server (FastAPI)..." -ForegroundColor Yellow
Write-Host "   URL: http://localhost:8000" -ForegroundColor White
Write-Host ""

# Kill any existing Python processes on port 8000
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend in a new window
$backendJob = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location 'c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent'; `$env:PYTHONIOENCODING='utf-8'; Write-Host '🔧 Backend Server Starting...' -ForegroundColor Cyan; python -m uvicorn main:app --host 127.0.0.1 --port 8000"
) -PassThru -WindowStyle Normal

Write-Host "✅ Backend starting (PID: $($backendJob.Id))" -ForegroundColor Green
Write-Host "   Waiting for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Step 2: Start Frontend
Write-Host ""
Write-Host "2️⃣  Starting Frontend (React)..." -ForegroundColor Yellow
Write-Host "   URL: http://localhost:3000" -ForegroundColor White
Write-Host ""

# Navigate to frontend and start
Set-Location -Path "$PSScriptRoot\frontend"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host "✅ Dependencies installed!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "🚀 Starting React development server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  System Ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "🔌 Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the frontend" -ForegroundColor Gray
Write-Host "(Backend will continue running in separate window)" -ForegroundColor Gray
Write-Host ""

# Start frontend (this will block)
npm start
