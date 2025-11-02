# Agent-Based Architecture (Multi-Tenant Platform)

## Overview

This document describes the NEW agent-based architecture that replaces the rigid state machine with a flexible, Claude-driven conversational system.

**Key Innovation:** Runtime prompt composition allows a single codebase to serve multiple businesses seamlessly.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Customer Calls Twilio                        │
│                    (+1-229-922-3706)                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Twilio Webhook        │
              │  POST /twilio/voice    │
              └────────┬───────────────┘
                       │
                       ├─ Extract: call_sid, from_number, to_number
                       │
                       ▼
      ┌────────────────────────────────────┐
      │  Business Config Manager           │
      │  get_business_from_twilio_number() │
      └────────┬───────────────────────────┘
               │
               ├─ Lookup: "+1229922370 6" → "piano_moving_001"
               │
               ▼
      ┌────────────────────────┐
      │  Load Business Config  │
      │  configs/piano_moving.json │
      └────────┬───────────────┘
               │
               │  {
               │    "business_type": "piano_moving",
               │    "agent_persona": {...},
               │    "required_fields": [...],
               │    "quote_calculation": {...}
               │  }
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      PROMPT COMPOSER                              │
│  compose_agent_prompt(business_config, session_data, transcript) │
└──────────────────────────┬───────────────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
            ▼                             ▼
   ┌────────────────┐           ┌────────────────────┐
   │ Constitutional │           │ Business Config    │
   │ Layer (fixed)  │           │ (flexible)         │
   │                │           │                    │
   │ - Respect time │           │ - Piano types      │
   │ - Build trust  │     +     │ - Field definitions│
   │ - Never assume │           │ - Domain guidance  │
   │ - Human-centric│           │ - Quote formula    │
   └────────────────┘           └────────────────────┘
            │                             │
            └──────────────┬──────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  Complete System     │
                │  Prompt for Claude   │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  Claude Sonnet 4     │
                │  (Agent Brain)       │
                └──────────┬───────────┘
                           │
                           ▼
                    {
                      "response": "What to say",
                      "extracted": {"field": "value"},
                      "is_complete": false,
                      "should_transfer": false
                    }
                           │
                           ▼
          ┌────────────────────────────────┐
          │  Update Session Data           │
          │  session_data.update(extracted)│
          └────────────┬───────────────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
    ┌──────────────┐   ┌──────────────────┐
    │ is_complete? │   │ should_transfer? │
    └──────┬───────┘   └────────┬─────────┘
           │                    │
    Yes    │             Yes    │
           ▼                    ▼
  ┌─────────────────┐  ┌───────────────────┐
  │ Calculate Quote │  │ Transfer to Human │
  │ Send SMS        │  │ (Dial number)     │
  │ Hangup          │  │                   │
  └─────────────────┘  └───────────────────┘
           │
     No    │
           ▼
  ┌─────────────────┐
  │ Continue Conv.  │
  │ TwiML Gather    │
  └─────────────────┘
```

---

## Call Flow (Multi-Tenant)

### 1. Call Arrives

```
Customer → Dials +1-229-922-3706 → Twilio → POST /twilio/voice
```

**Webhook receives:**
```python
{
  "CallSid": "CAxxxx",
  "From": "+61494182675",  # Customer
  "To": "+12299223706"     # Which business?
}
```

### 2. Business Identification

```python
business_id = get_business_from_twilio_number("+12299223706")
# Returns: "piano_moving_001"

business_config = load_business_config("piano_moving_001")
# Loads: configs/piano_moving.json
```

**Config contains:**
- Business type (piano_moving, house_cleaning, etc.)
- Agent persona (name, company)
- Required fields to extract
- Quote calculation formula
- Domain-specific guidance

### 3. Prompt Composition

```python
system_prompt = compose_agent_prompt(
    business_id="piano_moving_001",
    business_config=config,
    session_data={"piano_type": None, ...},
    transcript=[]
)
```

**Composed prompt = Constitutional Layer + Business Config**

```
You are Sandra, an AI assistant for PianoMove AI...

## YOUR GOAL
Extract these 5 pieces of information:
1. Piano type (upright, baby_grand, grand)
2. Pickup address (full street address)
3. Delivery address (full street address)
4. Stairs count (number)
5. Insurance preference (yes/no)

## CONSTITUTIONAL PRINCIPLES
1. RESPECT CUSTOMER TIME - under 3 sentences
2. BUILD TRUST - never assume
3. ENABLE SUCCESS - accurate data
4. HUMAN-CENTRIC - transfer when appropriate

## DOMAIN GUIDANCE
Piano types: upright, baby grand, grand
Addresses: Need full street address with suburb and state
...
```

### 4. Agent Turn

```python
response = await claude_agent_turn(
    user_input="Baby grand from Brisbane to Gold Coast",
    business_id="piano_moving_001",
    business_config=config,
    collected_data=session_data,
    transcript=history
)
```

**Claude returns:**
```json
{
  "response": "Perfect! What's the full address in Brisbane?",
  "extracted": {
    "piano_type": "baby_grand"
  },
  "thinking": "Extracted piano type, need full addresses",
  "needs_clarification": ["pickup_address", "delivery_address"],
  "is_complete": false,
  "should_transfer_to_human": false,
  "transfer_reason": null
}
```

### 5. Update Session

```python
session_data["piano_type"] = "baby_grand"
transcript.append({"role": "user", "content": "Baby grand from Brisbane..."})
transcript.append({"role": "agent", "content": "Perfect! What's the full address..."})
```

### 6. TwiML Response

```python
if response["is_complete"]:
    return await generate_quote()
elif response["should_transfer_to_human"]:
    return transfer_to_human()
else:
    return gather_more_input(response["response"])
```

---

## Multi-Tenant Support

### Same Backend, Different Businesses

**Piano Moving:**
```json
{
  "business_id": "piano_moving_001",
  "twilio_number": "+12299223706",
  "agent_persona": {
    "name": "Sandra",
    "company": "PianoMove AI"
  },
  "required_fields": [
    "piano_type",
    "pickup_address",
    "delivery_address",
    "stairs_count",
    "has_insurance"
  ]
}
```

**House Cleaning:**
```json
{
  "business_id": "house_cleaning_001",
  "twilio_number": "+15551234567",
  "agent_persona": {
    "name": "Emma",
    "company": "Sparkle Clean"
  },
  "required_fields": [
    "property_type",
    "bedrooms",
    "bathrooms",
    "cleaning_type",
    "frequency"
  ]
}
```

**Same code, different config** → Different agent behavior!

---

## Code Structure

```
backend/
├── app/
│   ├── agent.py                  # Claude agent core
│   ├── prompt_composer.py        # Runtime prompt builder
│   ├── business_config.py        # Multi-tenant config loader
│   ├── twilio_handler_agent.py   # NEW webhook handler
│   ├── twilio_handler.py         # OLD state machine (for comparison)
│   ├── quote_engine.py           # Quote calculation
│   └── llm.py                    # Claude API wrapper
│
├── configs/
│   ├── constitutional_layer.md   # Universal principles
│   ├── piano_moving.json         # Piano moving config
│   ├── house_cleaning.json       # House cleaning config (future)
│   └── junk_removal.json         # Junk removal config (future)
│
├── evals/
│   ├── eval_framework.py         # Evaluation system
│   ├── test_cases.json           # Test scenarios
│   ├── run_evals.py              # Test runner
│   └── README.md                 # Eval docs
│
└── main.py                       # FastAPI routes
```

---

## Migration Path

### Phase 1: Run Both Systems in Parallel

```python
# main.py
@app.post("/twilio/voice")
async def twilio_voice_webhook(request: Request):
    # Use agent for new businesses
    if use_agent_for_business(business_id):
        return await handle_voice_agent(...)
    # Fall back to state machine for existing
    else:
        return await handle_voice_state_machine(...)
```

### Phase 2: Test Agent with Piano Moving

1. Run evals: `python -m evals.run_evals`
2. Test with real calls
3. Compare to state machine
4. Measure: accuracy, efficiency, user satisfaction

### Phase 3: Add Second Business Type

1. Create `configs/house_cleaning.json`
2. Define required fields
3. Set up Twilio number
4. Test with eval framework
5. Deploy

### Phase 4: Full Platform

1. Move configs to database
2. Add admin UI for business management
3. Multi-region support
4. Analytics dashboard

---

## Benefits of Agent Architecture

### vs State Machine

| Feature | State Machine | Agent |
|---------|--------------|-------|
| **Flexibility** | Rigid flow | Adapts to conversation |
| **Efficiency** | Always 6 turns | 2-6 turns (batch info) |
| **Backtracking** | Can't handle | Handles naturally |
| **Edge cases** | Breaks | Transfers gracefully |
| **Multi-tenant** | Hard to configure | JSON config |
| **Code complexity** | Complex state logic | Simple prompt composition |

### Platform Benefits

1. **Add new business in <1 day**
   - Write JSON config
   - Set up Twilio number
   - Deploy (same code)

2. **Constitutional consistency**
   - All businesses follow same principles
   - Brand trust across domains

3. **Easy iteration**
   - Update prompt → redeploy
   - No code changes for config tweaks

4. **Testable**
   - Eval framework for quality
   - Systematic testing

---

## Production Considerations

### Database Schema (Future)

```sql
CREATE TABLE businesses (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  business_type TEXT NOT NULL,
  config JSONB NOT NULL,
  twilio_number TEXT UNIQUE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  business_id TEXT REFERENCES businesses(id),
  call_sid TEXT NOT NULL,
  from_number TEXT,
  session_data JSONB,
  transcript JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quotes (
  id TEXT PRIMARY KEY,
  session_id TEXT REFERENCES sessions(id),
  business_id TEXT REFERENCES businesses(id),
  total_amount DECIMAL(10,2),
  details JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Caching Strategy

- **Constitutional layer:** Loaded once at startup
- **Business configs:** Cached in-memory, TTL 1 hour
- **Sessions:** Redis (multi-instance support)

### Cost Optimization

- **Prompt length:** ~1500 tokens (constitutional + config)
- **Average conversation:** 6 turns × 2000 tokens = 12K tokens
- **Cost per call:** ~$0.036 (Claude Sonnet 4)
- **At 10K calls/month:** $360/month for LLM

---

## Next Steps

1. ✅ **Constitutional layer defined**
2. ✅ **Agent prompt created**
3. ✅ **Eval framework built**
4. ✅ **Runtime prompt composition**
5. ✅ **Backend integration**
6. ⏳ **Test with real calls**
7. ⏳ **Add second business type**
8. ⏳ **Move to database**

**Ready to deploy and test!**
