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
   - SECRET_KEY=your-secure-secret-key-minimum-32-characters (CRITICAL: Generate secure key!)
   
   **Generate SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   
6. **Deploy**: Click "Create Web Service"

## Security Verification

After deployment, run security tests:
```bash
pip install requests
python security_test.py https://your-app-url.onrender.com
```

## Custom Domain Setup
1. In Render dashboard, go to Settings → Custom Domains  
2. Add: ourchat.strangled.net
3. Get the IP address from Render
4. Update FreeDNS A record with that IP

Your app will be live at https://ourchat.strangled.net
