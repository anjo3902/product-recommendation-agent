# Quick Status Checker for Product Recommendation System
# Run this anytime to check if all services are running

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  SERVICE STATUS CHECK" -ForegroundColor Yellow
Write-Host "================================================`n" -ForegroundColor Cyan

$allRunning = $true

# Check Ollama
Write-Host "Checking Ollama (port 11434)..." -ForegroundColor White
try {
    Invoke-WebRequest -Uri "http://localhost:11434" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "  ✅ Ollama is RUNNING`n" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Ollama is NOT running`n" -ForegroundColor Red
    $allRunning = $false
}

# Check Backend
Write-Host "Checking Backend (port 8000)..." -ForegroundColor White
try {
    Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "  ✅ Backend is RUNNING`n" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Backend is NOT running`n" -ForegroundColor Red
    $allRunning = $false
}

# Check Frontend
Write-Host "Checking Frontend (port 3000)..." -ForegroundColor White
try {
    Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop | Out-Null
    Write-Host "  ✅ Frontend is RUNNING`n" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Frontend is NOT running`n" -ForegroundColor Red
    $allRunning = $false
}

Write-Host "================================================" -ForegroundColor Cyan

if ($allRunning) {
    Write-Host "🎉 ALL SERVICES ARE READY!" -ForegroundColor Green
    Write-Host "`n👉 Open: http://localhost:3000" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  Some services are not running" -ForegroundColor Yellow
    Write-Host "`nTo start all services, run:" -ForegroundColor White
    Write-Host "  .\start-all.ps1" -ForegroundColor Cyan
}

Write-Host "================================================`n" -ForegroundColor Cyan
