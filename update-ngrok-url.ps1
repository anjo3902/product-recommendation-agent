# Quick Update Frontend with New ngrok URL
# Run this whenever ngrok URL changes

Write-Host "🔄 Update Frontend with New ngrok URL" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$ngrokUrl = Read-Host "Enter your ngrok URL (e.g., https://abc123.ngrok-free.app)"

if (-not $ngrokUrl) {
    Write-Host "❌ No URL provided" -ForegroundColor Red
    exit 1
}

# Validate URL
if ($ngrokUrl -notmatch "^https://.*\.ngrok") {
    Write-Host "⚠️  URL doesn't look like a ngrok URL. Continue anyway? (Y/N)" -ForegroundColor Yellow
    $confirm = Read-Host
    if ($confirm -ne "Y") {
        exit 1
    }
}

Write-Host ""
Write-Host "[1/3] Updating frontend .env.production..." -ForegroundColor Blue
Set-Location "c:\Users\ANJO JAISON\Downloads\Product Recommendation Agent\frontend"
"REACT_APP_API_URL=$ngrokUrl" | Out-File -FilePath ".env.production" -Encoding UTF8
Write-Host "✓ .env.production updated" -ForegroundColor Green

Write-Host ""
Write-Host "[2/3] Removing old Vercel environment variable..." -ForegroundColor Blue
vercel env rm REACT_APP_API_URL production --yes 2>$null
Write-Host "✓ Old variable removed" -ForegroundColor Green

Write-Host ""
Write-Host "[3/3] Adding new Vercel environment variable..." -ForegroundColor Blue
Write-Host "When prompted, paste this URL: $ngrokUrl" -ForegroundColor Yellow
vercel env add REACT_APP_API_URL production

Write-Host ""
Write-Host "Redeploying frontend..." -ForegroundColor Blue
vercel --prod

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Frontend Updated!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend URL: $ngrokUrl" -ForegroundColor White
Write-Host "Test: $ngrokUrl/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "Your frontend will update in ~1 minute" -ForegroundColor Cyan
