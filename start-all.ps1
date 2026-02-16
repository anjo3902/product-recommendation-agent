# Start All Services for Product Recommendation System
# This starts Ollama, Backend, and Frontend in separate windows

Write-Host "`n================================================" -ForegroundColor Green
Write-Host "  STARTING ALL SERVICES" -ForegroundColor Yellow
Write-Host "================================================`n" -ForegroundColor Green

# Start Ollama
Write-Host "[1/3] Starting Ollama..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '>>> OLLAMA SERVICE <<<' -ForegroundColor Green; ollama serve" -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host "      ✅ Ollama window opened`n" -ForegroundColor White

# Start Backend
Write-Host "[2/3] Starting Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\ANJO JAISON\Downloads\Product Recommendation Agent'; Write-Host '>>> BACKEND SERVER <<<' -ForegroundColor Green; python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload" -WindowStyle Normal
Start-Sleep -Seconds 2
Write-Host "      ✅ Backend window opened`n" -ForegroundColor White

# Start Frontend
Write-Host "[3/3] Starting Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\ANJO JAISON\Downloads\Product Recommendation Agent\frontend'; Write-Host '>>> FRONTEND SERVER <<<' -ForegroundColor Green; npm start" -WindowStyle Normal
Write-Host "      ✅ Frontend window opened`n" -ForegroundColor White

Write-Host "================================================" -ForegroundColor Green
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Write-Host "================================================`n" -ForegroundColor Green

Write-Host "Services are starting in separate windows." -ForegroundColor White
Write-Host "Please wait 20-30 seconds for all to load.`n" -ForegroundColor White

Write-Host "To check status, run:" -ForegroundColor Cyan
Write-Host "  .\check-status.ps1`n" -ForegroundColor Yellow

Write-Host "Your browser will open automatically to:" -ForegroundColor White
Write-Host "  http://localhost:3000`n" -ForegroundColor Yellow
