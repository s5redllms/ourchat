# Deploy ourChat with Custom Domain (ourchat.ngrok.app)
# Requires: Paid ngrok plan and configured auth token

Write-Host "=== ourChat Custom Domain Deployment ===" -ForegroundColor Green
Write-Host ""

# Check if auth token is configured
$configPath = "$env:LOCALAPPDATA\ngrok\ngrok.yml"
if (-not (Test-Path $configPath)) {
    Write-Host "❌ ERROR: ngrok auth token not configured!" -ForegroundColor Red
    Write-Host "Please run: .\ngrok.exe config add-authtoken YOUR_TOKEN_HERE" -ForegroundColor Yellow
    Write-Host "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Yellow
    exit 1
}

# Check if Flask app is running
$flaskRunning = netstat -an | findstr :5000
if (-not $flaskRunning) {
    Write-Host "🚀 Starting Flask app..." -ForegroundColor Blue
    $env:FLASK_ENV = "production"
    Start-Process python -ArgumentList "app.py" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "✅ Flask app started on port 5000" -ForegroundColor Green
} else {
    Write-Host "✅ Flask app already running on port 5000" -ForegroundColor Green
}

Write-Host ""
Write-Host "🌐 Deploying to custom domain: ourchat.ngrok.app" -ForegroundColor Blue
Write-Host ""
Write-Host "📋 Steps taken:" -ForegroundColor Yellow
Write-Host "   1. ✅ ngrok downloaded and configured" -ForegroundColor White
Write-Host "   2. ✅ Flask app running on localhost:5000" -ForegroundColor White
Write-Host "   3. 🚀 Starting ngrok tunnel with custom domain..." -ForegroundColor White
Write-Host ""

# Start ngrok with custom domain
Write-Host "Starting ngrok tunnel..." -ForegroundColor Blue
Write-Host "Your app will be available at: https://ourchat.ngrok.app" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the tunnel" -ForegroundColor Yellow
Write-Host ""

# Run ngrok with custom domain
.\ngrok.exe http 5000 --domain=ourchat.ngrok.app
