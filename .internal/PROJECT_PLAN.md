# PianoMove AI - Voice Quote Generator

**Portfolio project for Senior AI Engineer role**

## 🎯 Purpose

Demonstrate production-ready voice AI capabilities for a Gold Coast startup building conversational AI for service businesses ($0→7fig ARR in 12 months).

## 🏢 Team Decision Summary

**Present:** Kai (CTO), Zara (ML Scientist), Priya (PM), Jordan (Designer), Alex (Frontend), Marcus (Backend)

### Key Insights from Team

**Kai:** Focus on production-quality code, not feature breadth. Show clean async patterns and real engineering.

**Zara:** The conversation design matters more than voice tech. 70% effort on LLM orchestration, 30% on plumbing.

**Priya:** Show business value explicitly. Real pricing logic, professional outputs, unit economics.

**Jordan:** Voice UX is different. Nail conversational pacing, confirmation loops, natural language.

**Alex:** Add a simple dashboard. Transforms "hack" into "product".

**Marcus:** Show you understand scale. Architecture doc with cost breakdown to 7-figure ARR.

## 📋 Scope

### Core MVP (4 hours)
- ✅ FastAPI server with async/await patterns
- ✅ Twilio integration (phone → webhook)
- ✅ Claude LLM with function calling (structured data extraction)
- ✅ Quote calculation logic (stairs, distance, piano type, insurance)
- ✅ SMS delivery with quote summary

### Dashboard (2 hours)
- ✅ Next.js simple page
- ✅ Call log (timestamp, customer, quote amount, duration, cost)
- ✅ Download quotes as PDF
- ✅ Cost tracking per call

### Scaling Doc (1 hour)
- ✅ Architecture diagram (EKS, Redis, multi-region)
- ✅ Cost breakdown (STT, TTS, LLM, Twilio)
- ✅ Unit economics: $0→7fig ARR
- ✅ Monitoring strategy (Prometheus, Grafana, call quality)
- ✅ Bottleneck analysis

### Demo Video (30 min)
- ✅ Call the live number
- ✅ Show dashboard
- ✅ Explain key technical decisions
- ✅ Upload to Loom

## 🛠 Tech Stack

**Backend:**
- Python FastAPI (async/await)
- Twilio (phone interface)
- Deepgram (STT) or OpenAI Whisper
- Cartesia (TTS) or ElevenLabs
- Claude Sonnet 4 with extended thinking (quote logic)
- PostgreSQL + SQLAlchemy
- Redis (session state)

**Frontend:**
- Next.js 14
- Tailwind CSS
- Recharts (cost visualization)

**Infrastructure:**
- Railway or Render (MVP deploy)
- Kubernetes (scaling doc only)

## 💰 Unit Economics (for scaling doc)

**Cost per call (average):**
- STT: $0.006/min (Deepgram)
- TTS: $0.15/1K chars (Cartesia)
- LLM: $3/1M tokens (Claude)
- Twilio: $0.0085/min
- **= ~$0.50/call**

**At 7-figure ARR ($1M/year):**
- Assume $850 avg quote, 10% conversion = $85 per successful quote
- Need ~11,765 successful quotes/year
- = ~117,650 total calls (10% conversion)
- = ~322 calls/day
- **Cost: $58,825/year in AI infrastructure**
- **Gross margin: ~94%**

## 🎯 Conversation Flow Design

```
Agent: "Hi! I'm PianoMove AI. I can help you get an instant quote for moving your piano.
        First, what type of piano are you moving?"

User: "A baby grand"

Agent: "Got it, a baby grand. Beautiful! Where are we picking it up from?"

User: "123 Smith Street, Sydney"

Agent: "Perfect. And where's it going?"

User: "456 Jones Avenue, Melbourne"

Agent: "Sydney to Melbourne - that's a long haul! A few quick questions:
        1. Are there stairs at either location?"

User: "Yeah, 10 stairs at pickup"

Agent: "No problem. And will movers have elevator access, or is it stairs only?"

User: "Stairs only"

Agent: "Got it. Last question - would you like piano insurance for the move?"

User: "Yes please"

Agent: "Excellent choice. Let me calculate that for you...

        Alright! Based on:
        - Baby grand piano
        - Sydney to Melbourne (870km)
        - 10 stairs at pickup
        - Insurance included

        Your total quote is $1,450.

        I'm sending this to your phone now. Sound good?"

User: "Yes"

Agent: "Perfect! You'll get an SMS with the full quote in the next minute.
        Thanks for choosing PianoMove!"
```

## 📊 Database Schema

```sql
-- Calls table
CREATE TABLE calls (
    id UUID PRIMARY KEY,
    phone_number VARCHAR(20),
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INT,
    transcript JSONB,
    quote_generated BOOLEAN,
    quote_amount DECIMAL,
    cost_usd DECIMAL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Quotes table
CREATE TABLE quotes (
    id UUID PRIMARY KEY,
    call_id UUID REFERENCES calls(id),
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    pickup_address TEXT,
    delivery_address TEXT,
    piano_type VARCHAR(50),
    stairs_count INT,
    has_elevator BOOLEAN,
    has_insurance BOOLEAN,
    distance_km INT,
    quote_amount DECIMAL,
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Deployment Phases

### Phase 1: MVP (Railway/Render)
- Single region (US-West)
- Postgres (managed)
- Redis (managed)
- FastAPI + Next.js on same dyno
- Cost: ~$25/month

### Phase 2: Scale to 1000 calls/day
- Multi-region (US, AU, EU)
- Load balancer
- Redis Cluster
- Separate API and web services
- Cost: ~$500/month

### Phase 3: Scale to 10K calls/day (7-fig ARR)
- Kubernetes (EKS)
- Auto-scaling pods
- Prometheus + Grafana
- S3 for call recordings
- Multi-region Postgres replication
- Cost: ~$2-3K/month

## 📝 Key Differentiators

1. **Conversation Design** - Natural pacing, confirmation loops, graceful errors
2. **Production Quality** - Async patterns, structured logging, error handling
3. **Business Thinking** - Unit economics, scaling strategy, bottleneck analysis
4. **Real Demo** - Live phone number anyone can call
5. **Dashboard** - Shows this isn't just a hack, it's a product

## ⏱ Timeline

- **Tonight (3-4 hrs):** Core FastAPI + Twilio + Claude integration
- **Tomorrow AM (2-3 hrs):** Dashboard + polish
- **Tomorrow PM (1-2 hrs):** Scaling doc + demo video
- **Tomorrow EOD:** Send to recruiter

## 🎬 Demo Video Structure

1. **The Problem** (30 sec)
   - Service businesses lose customers who call after hours
   - Manual quoting is slow and expensive

2. **The Solution** (1 min)
   - Live demo: call the number, get instant quote
   - Show SMS with professional quote

3. **The Tech** (1 min)
   - Dashboard: call log, costs, quotes
   - Explain key decisions (async FastAPI, Claude function calling)

4. **The Scale** (30 sec)
   - Architecture diagram
   - Cost breakdown: $0.50/call → 94% margin at scale

5. **Why This Matters** (30 sec)
   - Real business value
   - Production-ready code
   - Scalable architecture

**Total: 3 minutes**

---

## 📂 Repository Structure

```
pianomove-ai/
├── .claude/
│   ├── founding-team/          # Team member profiles
│   └── commands/
│       └── team.md             # Full team collaboration
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── twilio_handler.py  # Webhook processing
│   │   ├── llm.py             # Claude integration
│   │   ├── quote_engine.py    # Pricing logic
│   │   └── models.py          # Database models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Dashboard
│   │   └── api/               # Next.js API routes
│   ├── package.json
│   └── Dockerfile
├── docs/
│   ├── ARCHITECTURE.md        # Scaling strategy
│   └── DEMO.md                # Demo script
├── PROJECT_PLAN.md            # This file
└── README.md                  # Setup & overview
```

---

**Let's ship this.** 🚀
