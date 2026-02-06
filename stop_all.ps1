# Product Recommendation Agent - Stop All Services

Write-Host "`n🛑 Stopping All Services..." -ForegroundColor Yellow
Write-Host "=" * 70 -ForegroundColor Yellow

# Stop Frontend (Node)
Write-Host "`n🎨 Stopping Frontend..." -ForegroundColor Cyan
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force
$nodePort = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($nodePort) {
    Stop-Process -Id $nodePort.OwningProcess -Force -ErrorAction SilentlyContinue
}
Write-Host "   ✅ Frontend stopped" -ForegroundColor Green

# Stop Backend (Python)
Write-Host "`n⚙️  Stopping Backend..." -ForegroundColor Cyan
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "   ✅ Backend stopped" -ForegroundColor Green

# Stop Ollama
Write-Host "`n🤖 Stopping Ollama..." -ForegroundColor Cyan
Get-Process -Name ollama -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "   ✅ Ollama stopped" -ForegroundColor Green

Write-Host "`n✅ All services stopped successfully!`n" -ForegroundColor Green
