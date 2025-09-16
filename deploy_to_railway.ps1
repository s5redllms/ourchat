# Deploy ourChat to Railway with Custom Domain
# This script will deploy your app to Railway and configure the custom domain

Write-Host "=== OurChat Railway Deployment ===`n" -ForegroundColor Green

# Check if Railway CLI is installed
if (!(Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Railway CLI not found. Installing Railway CLI..." -ForegroundColor Yellow
    Write-Host "Please install Railway CLI from: https://railway.app/cli" -ForegroundColor Yellow
    Write-Host "Or run: npm install -g @railway/cli" -ForegroundColor Yellow
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in to Railway
try {
    railway whoami | Out-Null
} catch {
    Write-Host "❌ Not logged in to Railway. Please login first:" -ForegroundColor Red
    Write-Host "railway login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Railway CLI found and user is logged in`n" -ForegroundColor Green

# Initialize Railway project if not already done
if (!(Test-Path ".railway")) {
    Write-Host "🚀 Initializing Railway project..." -ForegroundColor Blue
    railway login
    railway init
    Write-Host "✅ Railway project initialized`n" -ForegroundColor Green
} else {
    Write-Host "✅ Railway project already initialized`n" -ForegroundColor Green
}

# Set environment variables
Write-Host "⚙️ Setting environment variables..." -ForegroundColor Blue
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=(New-Guid).ToString()
Write-Host "✅ Environment variables set`n" -ForegroundColor Green

# Deploy to Railway
Write-Host "🚀 Deploying to Railway..." -ForegroundColor Blue
railway up

Write-Host "`n✅ Deployment completed!" -ForegroundColor Green
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Your app is now deployed to Railway" -ForegroundColor White
Write-Host "   2. Get your Railway app URL from the dashboard" -ForegroundColor White
Write-Host "   3. Set up FreeDNS (ourchat.strangled.net) to point to your Railway app" -ForegroundColor White
Write-Host "   4. Configure custom domain in Railway dashboard" -ForegroundColor White
Write-Host "`n📱 Railway Dashboard: https://railway.app/dashboard" -ForegroundColor Cyan
Write-Host "🌐 FreeDNS: https://freedns.afraid.org" -ForegroundColor Cyan
