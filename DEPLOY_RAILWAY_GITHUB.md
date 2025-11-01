# Deploy PianoMove AI to Railway from GitHub

## ✅ What's Ready

- ✅ Code pushed to GitHub: https://github.com/isaacasamoah/piano-move-ai
- ✅ Railway project created: `pianomove-ai`
- ✅ Deployment configs ready (Procfile, railway.json, runtime.txt)

## 🚀 Deploy Steps

### Step 1: Go to Railway Dashboard

Open: https://railway.app/dashboard

### Step 2: Open Your Project

Click on your `pianomove-ai` project

### Step 3: Create New Service from GitHub

1. Click **"+ New"** button
2. Select **"GitHub Repo"**
3. You may need to **"Configure GitHub App"** first:
   - Click "Configure GitHub App"
   - Select your GitHub account
   - Choose "All repositories" or select `piano-move-ai`
   - Click "Install & Authorize"
4. Back in Railway, click **"+ New"** → **"GitHub Repo"**
5. Select **`isaacasamoah/piano-move-ai`**

### Step 4: Configure Service Settings

Railway will auto-detect it's a Python app. You need to:

1. **Set Root Directory:**
   - In service settings → **"Root Directory"**
   - Set to: `backend`
   - This tells Railway the app is in the `/backend` folder

2. **Service Name (Optional):**
   - Rename service to `backend` for clarity

### Step 5: Initial Deployment

Railway will automatically:
- Install Python 3.11
- Install dependencies from `requirements.txt`
- Run the start command from `Procfile`
- Deploy your app!

**Wait 2-3 minutes for deployment to complete.**

### Step 6: Check Deployment Status

In Railway dashboard you'll see:
- ✅ **Build Logs** - Watch dependencies install
- ✅ **Deploy Logs** - Watch app start
- ✅ **Health Check** - Should turn green when `/health` responds

### Step 7: Get Your URL

1. Click on your service
2. Go to **"Settings"** tab
3. Scroll to **"Domains"**
4. Click **"Generate Domain"**
5. You'll get something like:
   ```
   https://piano-move-ai-production.up.railway.app
   ```

**Copy this URL!**

### Step 8: Test Your Deployment

Open in browser:
```
https://your-app.up.railway.app/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "service": "pianomove-ai"
}
```

## 🔧 Set Environment Variables (Important!)

Your app is running but without Twilio credentials. To add them:

### Via Railway Dashboard:

1. In your service, go to **"Variables"** tab
2. Click **"+ New Variable"**
3. Add these:

```
TWILIO_ACCOUNT_SID = your_account_sid_here
TWILIO_AUTH_TOKEN = your_auth_token_here
TWILIO_PHONE_NUMBER = +1234567890
DEBUG = False
```

4. Click **"Add"** for each
5. Service will auto-redeploy with new variables

### Via CLI (Alternative):

```bash
railway variables set TWILIO_ACCOUNT_SID=ACxxxxxxxx
railway variables set TWILIO_AUTH_TOKEN=your_token
railway variables set TWILIO_PHONE_NUMBER=+1234567890
railway variables set DEBUG=False
```

## 📞 Configure Twilio Webhook

Once deployed:

1. **Go to Twilio Console:**
   https://console.twilio.com/us1/develop/phone-numbers/manage/incoming

2. **Select your phone number**

3. **Configure Voice Webhook:**
   - A call comes in: **Webhook**
   - URL: `https://your-app.up.railway.app/twilio/voice`
   - Method: **HTTP POST**
   - Click **Save**

## ✅ Test End-to-End

1. Call your Twilio number
2. Follow voice prompts
3. Receive SMS quote!

## 🔄 Auto-Deployment

Now every time you push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push
```

Railway automatically:
- Detects the push
- Rebuilds your app
- Deploys the new version
- Zero downtime!

## 📊 Monitoring

In Railway dashboard:

- **Metrics** - CPU, Memory, Network usage
- **Logs** - Real-time application logs
- **Deployments** - History of all deploys
- **Health** - Uptime monitoring

## 💰 Cost

- **Free Trial:** $5 credit (no CC required)
- **Hobby Plan:** $5/month after trial
- **This App:** ~$0.01/hour = ~$7/month

## 🐛 Troubleshooting

### Build Fails

Check **Build Logs** tab:
- Missing dependencies? Check `requirements.txt`
- Python version issue? Check `runtime.txt`

### Deploy Fails

Check **Deploy Logs** tab:
- Port binding issue? Railway auto-sets `$PORT`
- Import errors? Check all files pushed to GitHub

### Health Check Failing

- Check `/health` endpoint is accessible
- Verify `railway.json` healthcheck path
- Check deploy logs for startup errors

### Variables Not Working

- Variables tab → Verify they're set
- Redeploy after adding variables
- Check logs for "config error"

## 🎯 Next Steps After Deployment

1. ✅ Get Twilio account (if you don't have one)
2. ✅ Add Twilio credentials to Railway variables
3. ✅ Configure Twilio webhook
4. ✅ Make test call!
5. ✅ Share the number in your portfolio/demo video

## 📝 Your Deployment URLs

**GitHub Repo:**
https://github.com/isaacasamoah/piano-move-ai

**Railway Dashboard:**
https://railway.app/dashboard

**Live App:**
https://your-app.up.railway.app (get this after Step 7)

**Twilio Console:**
https://console.twilio.com

---

**Ready to deploy!** Follow steps 1-8 above. Should take ~10 minutes total.

Good luck! 🚀
