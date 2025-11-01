# Railway Deployment Guide

## Step-by-Step Deployment

### 1. Login to Railway

```bash
railway login
```

This will open a browser window for authentication.

### 2. Initialize Project

```bash
cd backend
railway init
```

You'll be prompted to:
- Create a new project or link to existing
- Enter project name (e.g., "pianomove-ai")

### 3. Deploy

```bash
railway up
```

This will:
- Upload your code
- Install dependencies from requirements.txt
- Start the server using the Procfile command
- Give you a deployment URL

### 4. Set Environment Variables

After deployment, you need to set environment variables in the Railway dashboard:

**Option A: Via CLI**
```bash
railway variables set TWILIO_ACCOUNT_SID=your_account_sid
railway variables set TWILIO_AUTH_TOKEN=your_auth_token
railway variables set TWILIO_PHONE_NUMBER=+1234567890
railway variables set ANTHROPIC_API_KEY=sk-ant-xxx
railway variables set DEBUG=False
```

**Option B: Via Dashboard (Easier)**
1. Go to https://railway.app/dashboard
2. Select your project
3. Go to "Variables" tab
4. Add each variable:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
   - `ANTHROPIC_API_KEY` (optional)
   - `DEBUG=False`
   - `SERVER_URL` will be auto-set by Railway

### 5. Get Your Deployment URL

```bash
railway domain
```

Or check the Railway dashboard - you'll see something like:
```
https://pianomove-ai-production.up.railway.app
```

### 6. Configure Twilio Webhook

Once you have your Railway URL:
1. Go to Twilio Console
2. Phone Numbers → Your Number
3. Voice & Fax → Webhook URL:
   ```
   https://your-app.up.railway.app/twilio/voice
   ```
4. Method: POST
5. Save

## Checking Deployment Status

```bash
# View logs
railway logs

# Check service status
railway status

# Open project in browser
railway open
```

## Updating Your Deployment

After making code changes:

```bash
railway up
```

That's it! Railway will rebuild and redeploy.

## Environment Variables Needed

```bash
# Required
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Optional
ANTHROPIC_API_KEY=sk-ant-xxx
DEBUG=False

# Auto-set by Railway
PORT=<railway_assigns>
RAILWAY_ENVIRONMENT=production
```

## Cost

- **Hobby Plan:** $5/month
- **Free Trial:** $5 credit (no credit card required)
- **Usage:** ~$0.01/hour for this app

## Troubleshooting

### Deployment fails
```bash
railway logs
# Check for errors in build process
```

### App crashes after deploy
```bash
railway logs --follow
# Watch real-time logs
```

### Environment variables not set
```bash
railway variables
# List all current variables
```

### Health check failing
- Make sure `/health` endpoint is accessible
- Check `railway.json` healthcheck settings

## Monitoring

Railway dashboard shows:
- CPU usage
- Memory usage
- Request count
- Response times
- Logs

## Alternative: GitHub Integration

1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Auto-deploy on every push to main

```bash
# In Railway dashboard:
# New Project → Deploy from GitHub → Select repo
```

## Rollback

If something breaks:

```bash
railway rollback
# Or use dashboard to select previous deployment
```

## Custom Domain (Optional)

1. Go to Railway dashboard
2. Settings → Domains
3. Add custom domain
4. Update DNS records as shown
5. Use custom domain in Twilio webhook

---

**Ready to deploy!** Run `railway login` to start.
