# OurChat Deployment Guide: ourchat.strangled.net

This guide will help you deploy OurChat so it appears on Google when searching for "ourchat.strangled.net".

## Prerequisites

1. **Git** - For version control and deployment
2. **Node.js** - For Railway CLI installation
3. **Railway Account** - Free hosting service ([railway.app](https://railway.app))
4. **FreeDNS Account** - Free DNS service ([freedns.afraid.org](https://freedns.afraid.org))

## Step 1: Set up FreeDNS

1. **Create FreeDNS Account**
   - Go to [https://freedns.afraid.org](https://freedns.afraid.org)
   - Click "Sign Up" and create a free account
   - Verify your email address

2. **Register ourchat.strangled.net**
   - After login, go to "Subdomains" in the menu
   - Click "Add a subdomain"
   - Choose "strangled.net" from the available domains
   - Enter "ourchat" as the subdomain
   - Select "A" record type
   - For now, enter a placeholder IP like "1.2.3.4" (we'll update this later)
   - Click "Save!"

## Step 2: Initialize Git Repository

```powershell
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: OurChat application"
```

## Step 3: Deploy to Railway

1. **Install Railway CLI**
   ```powershell
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```powershell
   railway login
   ```

3. **Run the deployment script**
   ```powershell
   .\deploy_to_railway.ps1
   ```

4. **Get your Railway app URL**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Find your deployed app
   - Copy the generated URL (something like: `yourapp-production.railway.app`)

## Step 4: Configure Custom Domain in Railway

1. **In Railway Dashboard:**
   - Select your deployed project
   - Go to "Settings" tab
   - Click "Domains"
   - Click "Custom Domain"
   - Enter: `ourchat.strangled.net`
   - Railway will show you the IP address to point your domain to

2. **Get the IP address from Railway** (it will be something like: `143.244.xxx.xxx`)

## Step 5: Update FreeDNS with Railway IP

1. **Back in FreeDNS:**
   - Go to "Subdomains" 
   - Find your "ourchat.strangled.net" entry
   - Click "Edit"
   - Replace the placeholder IP with the Railway IP address
   - Click "Save!"

## Step 6: Wait for DNS Propagation

- DNS changes can take 5 minutes to 24 hours to propagate
- You can check propagation status at [https://dnschecker.org](https://dnschecker.org)
- Enter "ourchat.strangled.net" to see if it resolves to your Railway IP

## Step 7: Set up Google Search Console

1. **Add your site to Google Search Console:**
   - Go to [Google Search Console](https://search.google.com/search-console)
   - Click "Add Property"
   - Enter "https://ourchat.strangled.net"
   - Choose DNS verification method
   - Add the TXT record to FreeDNS (same process as step 5, but choose "TXT" record type)

2. **Submit sitemap:**
   - In Search Console, go to "Sitemaps"
   - Add "https://ourchat.strangled.net/sitemap.xml"
   - Click "Submit"

## Step 8: Test Everything

1. **Test domain access:**
   ```powershell
   curl https://ourchat.strangled.net
   ```

2. **Test Google search:**
   - Wait a few days for Google to index
   - Search "ourchat.strangled.net" on Google
   - Your site should appear in results

## Troubleshooting

### Domain not resolving
- Check DNS propagation: [dnschecker.org](https://dnschecker.org)
- Verify IP address in FreeDNS matches Railway
- Wait longer (up to 24 hours)

### Railway deployment failed
- Check Railway logs in dashboard
- Ensure all required files are present (requirements.txt, Procfile)
- Verify Python dependencies are correct

### Google not indexing
- Submit sitemap in Google Search Console
- Check robots.txt: `https://ourchat.strangled.net/robots.txt`
- Wait 1-2 weeks for Google to discover and index

## Files Created for Deployment

- `requirements.txt` - Python dependencies
- `Procfile` - Railway deployment configuration  
- `railway.json` - Railway specific settings
- `static/sitemap.xml` - SEO sitemap
- `deploy_to_railway.ps1` - Automated deployment script
- Enhanced HTML with SEO meta tags

Your OurChat application should now be accessible at `https://ourchat.strangled.net` and discoverable on Google!
