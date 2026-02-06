# Product Recommendation Agent - Complete Startup Script
# This script: Saves work → Starts Ollama → Starts Backend → Starts Frontend

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🚀 Product Recommendation Agent - Startup Manager 🚀        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Save all work to GitHub
Write-Host "📝 Step 1: Saving all work to GitHub..." -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow

$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "   📦 Found uncommitted changes - committing..." -ForegroundColor Cyan
    git add .
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    git commit -m "Auto-save: $timestamp"
    
    Write-Host "   📤 Pushing to GitHub..." -ForegroundColor Cyan
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Changes saved to GitHub successfully!" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "   ⚠️  Warning: Push failed, continuing anyway..." -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "   ✅ No changes to commit - working tree clean" -ForegroundColor Green
    Write-Host ""
}

# Step 2: Start Ollama
Write-Host "🤖 Step 2: Starting Ollama LLM Server..." -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow

$ollamaRunning = Get-Process -Name ollama -ErrorAction SilentlyContinue
if ($ollamaRunning) {
    Write-Host "   ✅ Ollama already running" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "   🚀 Launching Ollama..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList '-NoExit', '-Command', "`$host.UI.RawUI.WindowTitle='Ollama Server'; ollama serve" -WindowStyle Minimized
    Start-Sleep -Seconds 5
    Write-Host "   ✅ Ollama started" -ForegroundColor Green
    Write-Host ""
}

# Step 3: Start Backend
Write-Host "⚙️  Step 3: Starting Backend Server..." -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow

# Kill any existing Python processes
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

$projectPath = "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent"
Write-Host "   🚀 Launching Backend on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit', '-Command', `
    "Set-Location '$projectPath'; `$env:PYTHONIOENCODING='utf-8'; `$host.UI.RawUI.WindowTitle='Backend Server'; Write-Host '🔥 Backend Server Running on http://localhost:8000' -ForegroundColor Green; & '.\.venv\Scripts\python.exe' -m uvicorn main:app --host 127.0.0.1 --port 8000" `
    -WindowStyle Normal

Start-Sleep -Seconds 10

# Verify backend
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3
    Write-Host "   ✅ Backend is running - Status: $($health.status)" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "   ⚠️  Backend starting... (may take a moment)" -ForegroundColor Yellow
    Write-Host ""
}

# Step 4: Start Frontend
Write-Host "🎨 Step 4: Starting Frontend..." -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow

Set-Location "$projectPath\frontend"

# Check dependencies
if (-not (Test-Path "node_modules")) {
    Write-Host "   📦 Installing dependencies..." -ForegroundColor Cyan
    npm install
}

# Kill any existing node processes on port 3000
$nodePort = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($nodePort) {
    Stop-Process -Id $nodePort.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host "   🚀 Launching Frontend on http://localhost:3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit', '-Command', `
    "Set-Location '$projectPath\frontend'; `$host.UI.RawUI.WindowTitle='Frontend Server'; Write-Host '🎨 Frontend Running on http://localhost:3000' -ForegroundColor Magenta; npm start" `
    -WindowStyle Normal

Start-Sleep -Seconds 5

# Final Status
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    ✅ ALL SYSTEMS RUNNING! ✅                       ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Service Status:" -ForegroundColor Cyan
Write-Host "   🤖 Ollama:   http://localhost:11434 (AI LLM Server)" -ForegroundColor White
Write-Host "   ⚙️  Backend:  http://localhost:8000 (FastAPI + 5 Agents)" -ForegroundColor White
Write-Host "   🎨 Frontend: http://localhost:3000 (React App)" -ForegroundColor White

Write-Host ""
Write-Host "💡 Quick Commands:" -ForegroundColor Yellow
Write-Host "   • Frontend will auto-open in browser" -ForegroundColor White
Write-Host "   • Check backend API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Check status: .\check_status.ps1" -ForegroundColor White
Write-Host "   • Stop all: .\stop_all.ps1" -ForegroundColor White

Write-Host ""
Write-Host "🎯 Ready to use! Open http://localhost:3000 to start shopping!" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
