# Voice Agent - Config-Driven Conversational Extraction

> Add a JSON config, get a voice agent. That's it.

## The Vision

A voice agent system where adding a new business is as simple as adding a JSON file. No code changes. No complex configuration. Just pure, elegant simplicity.

## How It Works

```
Customer calls → Greeting (from config) → Claude conversation → Extract data → Calculate quote → SMS quote
```

**The magic:** Everything is config-driven. The code never changes.

## Quick Start

### 1. Add a Business Config

Create `config/your_business.json`:

```json
{
  "business_id": "your_business",
  "display_name": "Your Business Name",
  "phone_number": "+1234567890",

  "agent": {
    "name": "Alex",
    "voice": "Polly.Joanna",
    "greeting": "Hi, I'm Alex from Your Business. I can help you get a quote..."
  },

  "extract": {
    "field_name": {
      "type": "string",
      "required": true,
      "hint": "What question to ask?"
    }
  },

  "quote_calculator": "your_calculator_function",
  "completion_message": "Your quote is ${total}..."
}
```

### 2. Create Quote Calculator

Create `calculators/your_business.py`:

```python
def your_calculator_function(data, business):
    """Calculate quote from extracted data."""
    # Your business logic here
    return {
        "total": 100.00,
        # ... more fields
    }
```

### 3. Deploy

```bash
git add config/your_business.json calculators/your_business.py
git push
```

Done. Your voice agent is live.

## Architecture

**Files:**
- `voice_agent.py` - The entire system (~230 lines)
- `config/*.json` - Business configurations
- `calculators/*.py` - Quote calculation logic

**That's it.** No database. No admin UI. No complexity.

## Why This is Beautiful

1. **Config-Driven**: Add business = add JSON file
2. **Scales Horizontally**: 1 call or 100,000 calls, same code
3. **Git is the Database**: Version control your configs
4. **Obvious**: New dev understands it in 5 minutes
5. **Extensible**: Add features via config, not code

## The Core Insight

> Voice calls are just ephemeral conversations with structured extraction.

We're not managing state machines. We're having natural conversations and extracting data. Claude handles the conversation. Config defines what to extract. Simple.

## Future Enhancements

- [ ] Constitutional layer in prompt (A/B test effectiveness)
- [ ] Redis for sessions (production scale)
- [ ] Database for configs (dynamic loading)
- [ ] SMS sending integration
- [ ] Geocoding for distance calculation
- [ ] Transfer to human logic
- [ ] Multi-language support
- [ ] Voice recording storage

But for MVP? We have everything we need.

---

**Built the Voyager way: Everything you need, nothing you don't.** 🚀
