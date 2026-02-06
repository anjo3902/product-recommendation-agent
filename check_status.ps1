# Quick Check - Verify all services are running

Write-Host "`n🔍 System Status Check" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# Check Ollama
Write-Host "`n🤖 Ollama Status:" -ForegroundColor Yellow
$ollama = Get-Process -Name ollama -ErrorAction SilentlyContinue
if ($ollama) {
    Write-Host "   ✅ Running" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not running" -ForegroundColor Red
}

# Check Backend
Write-Host "`n⚙️  Backend Status:" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 2
    Write-Host "   ✅ Running - Status: $($health.status)" -ForegroundColor Green
    Write-Host "   📊 Database: $($health.database)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Not running" -ForegroundColor Red
}

# Check Frontend
Write-Host "`n🎨 Frontend Status:" -ForegroundColor Yellow
$node = Get-Process -Name node -ErrorAction SilentlyContinue
if ($node) {
    Write-Host "   ✅ Running" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not running" -ForegroundColor Red
}

# Check Git Status
Write-Host "`n📝 Git Status:" -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    Write-Host "   ⚠️  Uncommitted changes" -ForegroundColor Yellow
    git status -s
} else {
    Write-Host "   ✅ Working tree clean" -ForegroundColor Green
}

Write-Host "`n" -ForegroundColor White
