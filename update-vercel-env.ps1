# Update Vercel Environment Variable with Current ngrok URL
# Run this script whenever ngrok URL changes

Write-Host "=== Vercel Environment Variable Updater ===" -ForegroundColor Cyan
Write-Host ""

# Get current ngrok URL
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:4040/api/tunnels" -ErrorAction Stop
    $ngrokUrl = $response.tunnels[0].public_url
    Write-Host "âœ“ Current ngrok URL: $ngrokUrl" -ForegroundColor Green
} catch {
    Write-Host "âœ— Error: ngrok is not running!" -ForegroundColor Red
    Write-Host "  Please start ngrok first: ngrok http 8000" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to Vercel Dashboard:" -ForegroundColor Yellow
Write-Host "   https://vercel.com/anjo3902s-projects/product-recommendation-agent/settings/environment-variables" -ForegroundColor White
Write-Host ""
Write-Host "2. Find REACT_APP_API_URL and click 'Edit'" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Update the value to:" -ForegroundColor Yellow
Write-Host "   $ngrokUrl" -ForegroundColor Green
Write-Host ""
Write-Host "4. Click 'Save'" -ForegroundColor Yellow
Write-Host ""
Write-Host "5. Go to Deployments tab and click 'Redeploy'" -ForegroundColor Yellow
Write-Host ""
Write-Host "6. Wait 2-3 minutes for deployment to complete" -ForegroundColor Yellow
Write-Host ""
Write-Host "The URL has been copied to clipboard!" -ForegroundColor Green
Set-Clipboard -Value $ngrokUrl

Write-Host ""
Write-Host "Press any key to open Vercel settings in browser..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Start-Process "https://vercel.com/anjo3902s-projects/product-recommendation-agent/settings/environment-variables"

