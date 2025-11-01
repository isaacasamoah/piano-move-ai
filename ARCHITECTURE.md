# Architecture

## System Overview

PianoMove AI is a voice-first quote generation system that uses Twilio for telephony, Claude for natural language understanding, and FastAPI for orchestration.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Customer Interaction                         │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Twilio Voice    │
                    │  +1-229-922-3706 │
                    └────────┬─────────┘
                             │
                             │ Speech-to-Text (STT)
                             │ Text-to-Speech (TTS)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                               │
│                  (Railway: backend-production-178ff)                 │
│                                                                       │
│  ┌──────────────────┐      ┌──────────────────┐                    │
│  │ Twilio Handler   │      │ Conversation     │                    │
│  │ /twilio/voice    │─────▶│ State Machine    │                    │
│  └──────────────────┘      └─────────┬────────┘                    │
│                                       │                              │
│                                       ▼                              │
│                            ┌──────────────────┐                     │
│                            │  Claude Sonnet 4  │                     │
│                            │  LLM Extraction   │                     │
│                            └─────────┬────────┘                     │
│                                      │                               │
│                                      ▼                               │
│  ┌──────────────────┐      ┌──────────────────┐                    │
│  │  Quote Engine    │◀─────│  Geocoding       │                    │
│  │  Pricing Logic   │      │  (Nominatim)     │                    │
│  └────────┬─────────┘      └──────────────────┘                    │
│           │                                                          │
│           ▼                                                          │
│  ┌──────────────────┐                                               │
│  │   SMS Delivery   │                                               │
│  │   (Twilio)       │                                               │
│  └──────────────────┘                                               │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Customer SMS    │
                    │  Quote Details   │
                    └──────────────────┘
```

## Call Flow

```
┌──────────┐
│ GREETING │  "Hi! I'm Sandra from PianoMove AI..."
└────┬─────┘
     │
     ▼
┌────────────┐
│ PIANO_TYPE │  "What type of piano? Upright, baby grand, or grand?"
└────┬───────┘
     │
     ▼
┌────────────────┐
│ PICKUP_ADDRESS │  "Where are we picking it up from?"
└────┬───────────┘
     │
     ▼
┌──────────────────┐
│ DELIVERY_ADDRESS │  "And where's it going?"
└────┬─────────────┘
     │
     ▼
┌────────┐
│ STAIRS │  "Are there any stairs? If yes, how many?"
└────┬───┘
     │
     ▼
┌───────────┐
│ INSURANCE │  "Would you like piano insurance for the move?"
└────┬──────┘
     │
     ▼
┌─────────────┐
│ QUOTE_READY │  Calculate → Speak quote → Send SMS → Hangup
└─────────────┘
```

## Data Flow

1. **Inbound Call** → Twilio webhook sends to `/twilio/voice`
2. **Speech Input** → Twilio STT converts to text
3. **NLU Extraction** → Claude extracts structured data:
   - Piano type (upright, baby_grand, grand)
   - Pickup address
   - Delivery address
   - Stairs count
   - Insurance preference
4. **Geocoding** → Nominatim API calculates distance
5. **Quote Calculation**:
   ```python
   base_price = {
       "upright": 200,
       "baby_grand": 350,
       "grand": 500
   }

   quote = base_price[piano_type]
   quote += distance_km * 1.50      # $1.50/km
   quote += stairs_count * 15       # $15/stair
   if has_insurance:
       quote *= 1.15                # +15%
   ```
6. **Quote Delivery**:
   - TTS speaks quote over phone
   - SMS sends detailed breakdown
   - Call ends gracefully

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Voice** | Twilio Voice API | Phone calls, STT, TTS |
| **Backend** | FastAPI + Python 3.11 | Async webhook handling |
| **NLU** | Claude Sonnet 4 | Natural language extraction |
| **Geocoding** | Nominatim (OSM) | Distance calculation |
| **Messaging** | Twilio SMS | Quote delivery |
| **Deployment** | Railway | Cloud hosting with auto-deploy |
| **Logging** | structlog | Structured JSON logs |

## State Management

Sessions are stored in-memory (MVP):

```python
sessions: Dict[str, ConversationSession] = {
    "call_sid": {
        "state": ConversationState.GREETING,
        "quote_details": QuoteDetails(),
        "transcript": [...]
    }
}
```

**Production consideration**: Move to Redis for multi-instance deployment.

## Error Handling

The system implements graceful degradation:

1. **Claude unavailable** → Falls back to keyword extraction
2. **Geocoding fails** → Uses 50km fallback distance
3. **SMS fails** → Logs error, user still hears quote
4. **Invalid input** → Repeats question in same state

## Scalability

**Current (MVP):**
- Single Railway dyno
- In-memory sessions
- ~100 concurrent calls

**Production Path:**
- Horizontal scaling with Redis sessions
- Load balancer (Railway/AWS ALB)
- Database for quote history (PostgreSQL)
- Monitoring (Prometheus + Grafana)

## Cost Structure

Per-call costs (3-minute average):
- Twilio voice: $0.026 (3 min × $0.0085/min)
- Twilio SMS: $0.0079
- Claude API: ~$0.003 (200 tokens)
- Geocoding: Free (Nominatim)

**Total: ~$0.037/call**

At 10,000 calls/month: $370 infrastructure cost
