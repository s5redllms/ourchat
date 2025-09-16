# ngrok Setup Guide for ourChat Deployment

## Step 1: Sign up for ngrok Account

1. Go to https://dashboard.ngrok.com/signup
2. Create a free account
3. For custom domains like `ourchat.ngrok.app`, you'll need a **paid plan** (Personal or Pro)

## Step 2: Get Your Auth Token

1. After signing up, go to https://dashboard.ngrok.com/get-started/your-authtoken
2. Copy your auth token
3. Run this command to configure it:
   ```
   .\ngrok.exe config add-authtoken YOUR_TOKEN_HERE
   ```

## Step 3: Reserve Your Custom Domain (Paid Plan Required)

### For Personal/Pro Plan:
1. Go to https://dashboard.ngrok.com/cloud-edge/domains
2. Click "Create Domain" or "New Domain"
3. Enter your desired domain: `ourchat`
4. This will give you: `ourchat.ngrok.app`

## Step 4: Deploy with Custom Domain

Once you have your custom domain reserved, use this command:

```powershell
.\ngrok.exe http 5000 --domain=ourchat.ngrok.app
```

## Step 5: Free Alternative (Random Domain)

If you want to test without a paid plan:

```powershell
.\ngrok.exe http 5000
```

This will give you a random domain like: `https://abc123.ngrok.app`

## Step 6: Access Your App

Once ngrok is running, your ourChat app will be accessible at:
- **Custom domain**: https://ourchat.ngrok.app
- **Random domain**: The URL shown in the ngrok terminal

## Security Notes for Production

1. Change the Flask secret key in `app.py`
2. Consider setting up HTTPS redirects
3. Configure proper CORS if needed
4. Monitor ngrok usage and limits

## Current Setup Status

✅ ngrok downloaded and extracted
✅ Flask app running on localhost:5000
⏳ Awaiting auth token configuration
⏳ Awaiting custom domain setup

## Next Steps

1. Visit https://dashboard.ngrok.com/signup to create an account
2. Copy your auth token and configure it
3. Subscribe to a paid plan for custom domains
4. Reserve the `ourchat` domain
5. Deploy using the custom domain command
