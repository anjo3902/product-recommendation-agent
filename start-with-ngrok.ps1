# Start Backend and ngrok Together
# Double-click this file to start both services

Write-Host "🚀 Starting Product Recommendation System with ngrok" -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if backend is already running
$backendRunning = Get-Process | Where-Object { $_.Path -like "*python*" -and $_.CommandLine -like "*uvicorn*" }
if ($backendRunning) {
    Write-Host "⚠️  Backend is already running" -ForegroundColor Yellow
} else {
    Write-Host "Starting Backend Server..." -ForegroundColor Green
    $backendScript = @"
Set-Location 'c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent'
Write-Host 'Backend Server Running on http://localhost:8000' -ForegroundColor Green
python -m uvicorn main:app --host 127.0.0.1 --port 8000
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript
    Start-Sleep -Seconds 8
    Write-Host "✓ Backend started" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting ngrok tunnel..." -ForegroundColor Green

# Check if ngrok is installed
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Host ""
    Write-Host "❌ ngrok not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Download ngrok from https://ngrok.com/download" -ForegroundColor White
    Write-Host "2. Install it or extract to any folder" -ForegroundColor White
    Write-Host "3. Run: ngrok config add-authtoken YOUR_TOKEN" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Start ngrok
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting ngrok tunnel..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "After ngrok starts, copy the HTTPS URL (e.g., https://abc123.ngrok-free.app)" -ForegroundColor Yellow
Write-Host ""

ngrok http 8000
