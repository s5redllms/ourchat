# Deploy ourChat with Free ngrok Tunnel (Random Domain)
# Works without paid plan - gets random domain like abc123.ngrok.app

Write-Host "=== ourChat Free Tunnel Deployment ===" -ForegroundColor Green
Write-Host ""

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
Write-Host "🌐 Deploying with free ngrok tunnel..." -ForegroundColor Blue
Write-Host ""
Write-Host "📋 Steps taken:" -ForegroundColor Yellow
Write-Host "   1. ✅ ngrok downloaded and ready" -ForegroundColor White
Write-Host "   2. ✅ Flask app running on localhost:5000" -ForegroundColor White
Write-Host "   3. 🚀 Starting ngrok tunnel with random domain..." -ForegroundColor White
Write-Host ""

# Start ngrok with free tunnel
Write-Host "Starting ngrok tunnel..." -ForegroundColor Blue
Write-Host "📝 Note: You'll get a random domain (e.g., abc123.ngrok.app)" -ForegroundColor Yellow
Write-Host "📝 For custom domains like 'ourchat.ngrok.app', use the paid plan script" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the tunnel" -ForegroundColor Yellow
Write-Host ""

# Run ngrok with free tunnel
.\ngrok.exe http 5000
