# 🎹 PianoMove AI

> Voice AI quote generator for piano removalists. Call a number, describe your move, get an instant quote via SMS.

**Portfolio project demonstrating production-ready voice AI for service businesses.**

## 📞 Live Demo

**Try it now!**
- **Phone:** +1 (229) 922-3706
- **Backend API:** https://backend-production-178ff.up.railway.app
- **Health Check:** https://backend-production-178ff.up.railway.app/health

**To test the demo:**
1. Email me your phone number (with country code, e.g., +61412345678)
2. I'll verify it in Twilio (takes 30 seconds)
3. Call +1 (229) 922-3706
4. Answer questions about a piano move
5. Receive instant SMS quote!

*Note: Twilio trial requires caller verification. Once I add your number, you can call immediately.*

## 🎯 What This Demonstrates

- **Voice AI orchestration** - Twilio → STT → LLM → TTS pipeline
- **Production Python** - Clean async/await patterns, error handling
- **Conversation design** - Natural multi-turn context management
- **Business value** - Real pricing logic, unit economics, scaling strategy
- **Product thinking** - Dashboard, monitoring, cost tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Twilio account (free trial works)
- Optional: Anthropic API key (Phase 2)

### Phase 1: Core Backend (COMPLETED ✅)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Test setup
python test_setup.py

# Configure environment
cp .env.example .env
# Edit .env with your Twilio credentials

# Start server
python -m app.main
```

Server runs on `http://localhost:8000`

### Expose with Ngrok (for Twilio webhooks)

```bash
ngrok http 8000
# Copy the HTTPS URL to your Twilio phone number webhook settings
# Set to: https://your-ngrok-url.ngrok.io/twilio/voice
```

### Phase 2: Dashboard (Coming Next)

```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:3000
```

## 📞 How It Works

1. **Customer calls** the Twilio number
2. **Twilio webhook** sends audio to your FastAPI server
3. **STT** (Deepgram) converts speech to text
4. **Claude LLM** extracts:
   - Piano type (baby grand, upright, grand)
   - Pickup address
   - Delivery address
   - Stairs count
   - Elevator access
   - Insurance preference
5. **Quote engine** calculates price based on:
   - Distance (Google Maps API)
   - Piano type ($200-500 base)
   - Stairs ($50/10 stairs)
   - Insurance (10% of total)
6. **TTS** (Cartesia) speaks the quote
7. **SMS** sends detailed quote to customer

## 💰 Pricing Logic

```python
base_price = {
    "upright": 200,
    "baby_grand": 350,
    "grand": 500
}

quote = base_price[piano_type]
quote += distance_km * 1.50  # $1.50/km
quote += (stairs_count / 10) * 50  # $50 per 10 stairs
if has_insurance:
    quote *= 1.10  # +10% for insurance
```

## 📊 Dashboard

View at `http://localhost:3000`

- **Recent calls** - timestamp, customer, quote, duration
- **Call recordings** - playback with transcript
- **Cost tracking** - STT, TTS, LLM costs per call
- **Quotes** - downloadable PDFs

## 🏗 Architecture

### MVP (Current)
```
Phone → Twilio → FastAPI → Claude/STT/TTS → SMS
                    ↓
                PostgreSQL
```

### Production Scale (10K calls/day)
```
                    ┌─────────────────┐
Phone → Twilio  →  │  Load Balancer  │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  EKS Cluster    │
                    │  ┌───────────┐  │
                    │  │ API Pods  │  │
                    │  │ (Async)   │  │
                    │  └─────┬─────┘  │
                    └────────┼────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
         │ Redis   │   │Postgres │   │   S3    │
         │ Cluster │   │ (Multi) │   │  (Recs) │
         └─────────┘   └─────────┘   └─────────┘
```

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for full scaling strategy.

## 💸 Unit Economics

**Cost per call:** ~$0.50
- STT: $0.006/min (Deepgram)
- TTS: $0.15/1K chars (Cartesia)
- LLM: $3/1M tokens (Claude)
- Twilio: $0.0085/min

**At $1M ARR:**
- ~11,765 successful quotes @ $850 avg
- ~117,650 total calls (10% conversion)
- **AI infrastructure: $58,825/year**
- **Gross margin: 94%**

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration test (requires running services)
python scripts/test_call_flow.py
```

## 📝 Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost/pianomove
REDIS_URL=redis://localhost:6379
ANTHROPIC_API_KEY=sk-ant-...
DEEPGRAM_API_KEY=...
CARTESIA_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
GOOGLE_MAPS_API_KEY=...

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📂 Project Structure

```
pianomove-ai/
├── .claude/                   # Claude Code team collaboration
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── twilio_handler.py # Voice webhook
│   │   ├── llm.py            # Claude integration
│   │   ├── quote_engine.py   # Pricing logic
│   │   ├── stt.py            # Speech-to-text
│   │   ├── tts.py            # Text-to-speech
│   │   └── models.py         # Database models
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx          # Dashboard
│   │   └── components/       # React components
│   └── package.json
├── docs/
│   ├── ARCHITECTURE.md       # Scaling strategy
│   └── CONVERSATION_DESIGN.md
├── scripts/
│   └── test_call_flow.py
└── PROJECT_PLAN.md           # Full team planning doc
```

## 🎬 Demo

**Live demo:** [Call +1-XXX-XXX-XXXX]

**Video walkthrough:** [Loom link]

**Try it yourself:**
1. Call the number
2. Describe your piano move
3. Get instant quote via SMS

## 🧠 Key Technical Decisions

### Why FastAPI?
- Async/await native (critical for voice latency)
- Excellent webhook handling
- Production-ready (used by Microsoft, Netflix)

### Why Claude Sonnet 4?
- Superior function calling for structured extraction
- Extended thinking for complex quote logic
- Cost-effective at scale ($3/1M tokens)

### Why Twilio (not LiveKit)?
- Faster MVP development (6 hours vs 12+)
- Production-grade phone infrastructure
- Focus on conversation design over plumbing

### Why separate Dashboard?
- Shows product thinking (not just backend work)
- Real-time monitoring critical for production
- Cost tracking essential for unit economics

## 🚀 Deployment

### Railway (MVP)
```bash
railway up
```

### Kubernetes (Production)
```bash
# See docs/ARCHITECTURE.md for full EKS setup
kubectl apply -f k8s/
```

## 📈 Monitoring

- **Prometheus** - API latency, error rates
- **Grafana** - Call volume, costs, conversion rates
- **Sentry** - Error tracking
- **CloudWatch** - Logs (Twilio webhooks, LLM calls)

## 🔒 Security

- API keys in environment variables
- Twilio webhook signature verification
- Rate limiting (10 calls/min per number)
- PII encryption (customer addresses, phone numbers)

## ⚠️ Trial Account Notes

This demo uses Twilio trial account with some limitations:
- **Inbound calls:** Caller's number must be verified in Twilio (free, takes 30 seconds)
- **SMS length:** 160 characters (full quote in production would be longer)
- **Geocoding:** Uses free OpenStreetMap API (production would use Google Maps for accuracy)

These are intentional MVP choices to demonstrate the architecture without API costs. Production deployment would use paid Twilio account and Google Maps API.

## 📄 License

MIT

## 👤 Author

Isaac Asamoah - [LinkedIn](https://linkedin.com/in/isaacasamoah) - [GitHub](https://github.com/isaacasamoah)

**Built for:** Senior AI Engineer role - Gold Coast AI startup

**Timeline:** 8 hours (proof of concept → production-ready demo)

---

⭐ **If this impressed you, [let's talk](mailto:isaacasamoah@gmail.com)** ⭐
