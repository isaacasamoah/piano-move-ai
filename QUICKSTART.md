# Quick Start Guide

Get PianoMove AI running in 10 minutes.

## Prerequisites

- Python 3.11 or higher
- Twilio account (free trial: https://www.twilio.com/try-twilio)
- ngrok (for webhooks: https://ngrok.com/)

## Step 1: Clone & Setup Python

```bash
cd pianomove-ai/backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Verify installation
python test_setup.py
```

You should see: ✅ ALL TESTS PASSED!

## Step 2: Get Twilio Credentials

1. Sign up at https://www.twilio.com/try-twilio
2. Go to Console: https://console.twilio.com
3. Copy these values:
   - **Account SID** (starts with AC...)
   - **Auth Token** (click to reveal)
4. Get a phone number:
   - Click "Get a Twilio phone number"
   - Accept the suggested number
   - Copy the number (format: +1234567890)

## Step 3: Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` file with your credentials:

```bash
# Paste your values here
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# Optional (for Phase 2)
ANTHROPIC_API_KEY=sk-ant-xxx

# Leave these as default for now
SERVER_URL=http://localhost:8000
DEBUG=True
```

## Step 4: Start the Server

```bash
# Make sure you're in backend/ with venv activated
python -m app.main
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it works:
```bash
# In a new terminal
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "pianomove-ai"
}
```

## Step 5: Expose with ngrok

In a **new terminal** (keep the server running):

```bash
ngrok http 8000
```

You'll see something like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

## Step 6: Configure Twilio Webhook

1. Go to: https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on your phone number
3. Scroll to "Voice & Fax"
4. Under "A CALL COMES IN":
   - Select "Webhook"
   - Paste: `https://abc123.ngrok.io/twilio/voice`
   - Method: HTTP POST
5. Click "Save configuration"

## Step 7: Test the Voice Call!

1. Call your Twilio number from your phone
2. Follow the prompts:
   - "What type of piano?" → Say "baby grand"
   - "Where's pickup?" → Say "123 Smith Street, Sydney"
   - "Where's delivery?" → Say "456 Jones Avenue, Melbourne"
   - "Any stairs?" → Say "10 stairs"
   - "Want insurance?" → Say "yes"
3. Listen to the quote
4. Check your phone for SMS with detailed breakdown!

## Watch the Logs

In the terminal where the server is running, you'll see structured logs:

```json
{"event": "session_created", "call_sid": "CA...", "timestamp": "..."}
{"event": "user_input", "input": "baby grand", ...}
{"event": "state_transition", "from_state": "greeting", "to_state": "piano_type"}
{"event": "quote_calculated", "total": 1450.0, ...}
{"event": "sms_sent", "message_sid": "SM...", ...}
```

## Troubleshooting

### "Module not found" error
```bash
# Make sure venv is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Twilio webhook not working
- Check ngrok is running
- Check ngrok URL is HTTPS (not HTTP)
- Check webhook URL ends with `/twilio/voice`
- Check server is running on port 8000

### Call connects but no response
- Check server logs for errors
- Verify environment variables in `.env`
- Test health endpoint: `curl http://localhost:8000/health`

### SMS not sending
- Check Twilio account has SMS enabled
- Verify phone number in `.env` matches Twilio console
- Check server logs for `sms_sent` or `sms_send_failed`

### Geocoding fails
- Geopy uses free OpenStreetMap data (no API key needed)
- If address not found, system falls back to 50km estimate
- For better accuracy, add Google Maps API in Phase 2

## Next Steps

### Phase 2: Build Dashboard
- Real-time call monitoring
- Cost tracking
- PDF quote generation
- See `PROJECT_PLAN.md` for details

### Deploy to Production
```bash
# Railway (recommended)
railway login
railway init
railway up

# Update Twilio webhook to Railway URL
# https://your-app.railway.app/twilio/voice
```

### Add Claude Integration
- Get API key: https://console.anthropic.com
- Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-xxx`
- Smarter conversation handling (Phase 2)

## Cost Breakdown (Free Tier)

**Twilio Free Trial:**
- $15.50 credit
- ~1,800 minutes of calling
- ~2,000 SMS messages

**This demo uses:**
- ~3 minutes per call
- 1 SMS per quote
- **≈ 500 free test calls**

## Architecture Overview

```
Phone Call
    ↓
Twilio (Speech-to-Text)
    ↓
FastAPI Backend
    ↓
    ├── Conversation State Machine
    ├── Quote Calculation Engine
    └── Geopy (Distance)
    ↓
Twilio (Text-to-Speech + SMS)
    ↓
Customer receives quote
```

## File Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app + /health + /twilio/voice
│   ├── config.py            # Environment variables
│   ├── schemas.py           # Data models (Pydantic)
│   ├── conversation.py      # State machine
│   ├── twilio_handler.py    # Voice + SMS logic
│   └── quote_engine.py      # Pricing + distance
├── requirements.txt
├── .env                     # Your secrets (git-ignored)
└── test_setup.py           # Verify installation
```

## Support

Issues? Check:
1. Server logs (terminal where `python -m app.main` runs)
2. ngrok logs (terminal where `ngrok http 8000` runs)
3. Twilio debugger: https://console.twilio.com/us1/monitor/debugger

## Success Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Test setup passes (`python test_setup.py`)
- [ ] `.env` file configured with Twilio credentials
- [ ] Server starts without errors (`python -m app.main`)
- [ ] Health check works (`curl http://localhost:8000/health`)
- [ ] ngrok running and forwarding to port 8000
- [ ] Twilio webhook configured with ngrok URL
- [ ] Test call completes successfully
- [ ] SMS received with quote

## Time Estimate

- First time: 15-20 minutes
- Subsequent runs: 2 minutes (start server + ngrok)

---

**Ready to ship!** 🚀

For deployment, monitoring, and scaling strategy, see:
- `PHASE1_COMPLETE.md` - What we built
- `PROJECT_PLAN.md` - Full roadmap
- `backend/README.md` - Detailed backend docs
