# Deploy ourChat to Render (No CLI Required)
# This script prepares your files for Render deployment

Write-Host "=== OurChat Render Deployment Preparation ===" -ForegroundColor Green
Write-Host ""

# Create .gitignore if it doesn't exist
if (!(Test-Path ".gitignore")) {
    Write-Host "📝 Creating .gitignore file..." -ForegroundColor Blue
    @"
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv
env/
venv/
instance/
.DS_Store
*.log
"@ | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host "✅ .gitignore created" -ForegroundColor Green
} else {
    Write-Host "✅ .gitignore already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "📋 Files prepared for deployment:" -ForegroundColor Yellow
Write-Host "   ✅ requirements.txt - Python dependencies" -ForegroundColor White
Write-Host "   ✅ Procfile - Web server configuration" -ForegroundColor White
Write-Host "   ✅ railway.json - Hosting configuration" -ForegroundColor White
Write-Host "   ✅ sitemap.xml - SEO optimization" -ForegroundColor White
Write-Host "   ✅ Enhanced HTML with meta tags" -ForegroundColor White
Write-Host "   ✅ .gitignore - Git ignore rules" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Ready for Render deployment!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps - Manual Deployment:" -ForegroundColor Yellow
Write-Host "   1. Create account at https://render.com" -ForegroundColor White
Write-Host "   2. Connect your GitHub account" -ForegroundColor White
Write-Host "   3. Create new GitHub repository with your code" -ForegroundColor White
Write-Host "   4. Deploy from GitHub on Render" -ForegroundColor White
Write-Host "   5. Set up ourchat.strangled.net domain" -ForegroundColor White
Write-Host ""

Write-Host "💡 Alternative - Upload via ZIP:" -ForegroundColor Cyan
Write-Host "   1. Create account at https://render.com" -ForegroundColor White
Write-Host "   2. Choose 'Web Service'" -ForegroundColor White
Write-Host "   3. Select 'Deploy from Git'" -ForegroundColor White
Write-Host "   4. Or upload your project as ZIP" -ForegroundColor White
Write-Host ""

Write-Host "⚙️ Render Configuration:" -ForegroundColor Blue
Write-Host "   Build Command: pip install -r requirements.txt" -ForegroundColor White
Write-Host "   Start Command: gunicorn app:app --host 0.0.0.0 --port `$PORT" -ForegroundColor White
Write-Host "   Environment: Python 3" -ForegroundColor White
Write-Host ""

# Create a README for deployment
Write-Host "📝 Creating deployment instructions..." -ForegroundColor Blue
@"
# OurChat - Render Deployment

## Quick Deployment to Render

1. **Create Render Account**: Go to https://render.com and sign up
2. **New Web Service**: Click "New" → "Web Service"
3. **Connect Repository**: Connect your GitHub repo or upload files
4. **Configure Service**:
   - Name: ourchat
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --host 0.0.0.0 --port $PORT`
   
5. **Environment Variables**:
   - FLASK_ENV=production
   - SECRET_KEY=your-secret-key-here
   
6. **Deploy**: Click "Create Web Service"

## Custom Domain Setup
1. In Render dashboard, go to Settings → Custom Domains  
2. Add: ourchat.strangled.net
3. Get the IP address from Render
4. Update FreeDNS A record with that IP

Your app will be live at https://ourchat.strangled.net
"@ | Out-File -FilePath "RENDER_DEPLOYMENT.md" -Encoding UTF8

Write-Host "✅ Created RENDER_DEPLOYMENT.md with detailed instructions" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Your next steps:" -ForegroundColor Yellow
Write-Host "   1. Go to https://render.com and create account" -ForegroundColor White
Write-Host "   2. Follow instructions in RENDER_DEPLOYMENT.md" -ForegroundColor White
Write-Host "   3. Set up FreeDNS at https://freedns.afraid.org" -ForegroundColor White
Write-Host ""
Write-Host "📖 Full guide available in: DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
