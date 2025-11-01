# Backend Setup

FastAPI backend for PianoMove AI voice quote system.

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Twilio (get from console.twilio.com)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Anthropic (get from console.anthropic.com)
ANTHROPIC_API_KEY=sk-ant-...

# Optional
SERVER_URL=http://localhost:8000
DEBUG=True
```

### 3. Run Server

```bash
python -m app.main
```

Server runs on `http://localhost:8000`

### 4. Expose for Twilio (Development)

```bash
ngrok http 8000
```

Configure Twilio webhook:
- Go to Phone Number settings in Twilio Console
- Set Voice Webhook: `https://your-url.ngrok.io/twilio/voice`
- Method: POST

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/twilio/voice` | POST | Twilio voice webhook |
| `/` | GET | API info |

## Architecture

```
app/
├── main.py              # FastAPI app, routes
├── config.py            # Environment settings
├── schemas.py           # Pydantic models
├── conversation.py      # State machine
├── twilio_handler.py    # Voice webhooks
├── quote_engine.py      # Pricing logic
└── llm.py              # Claude integration
```

## Conversation States

```
GREETING → PIANO_TYPE → PICKUP_ADDRESS → DELIVERY_ADDRESS → STAIRS → INSURANCE → QUOTE
```

## Quote Calculation

**Base Prices:**
- Upright: $200
- Baby Grand: $350
- Grand: $500

**Additional:**
- Distance: $1.50/km (geocoded)
- Stairs: $15/stair
- Insurance: +15%

Implementation: `app/quote_engine.py:46`

## Testing

```bash
# Health check
curl http://localhost:8000/health

# Test call
# Call your Twilio number and follow prompts
```

## Deployment

### Railway

```bash
railway link
railway up
```

Set environment variables in Railway dashboard.

### Manual

Requirements:
- Python 3.11+ runtime
- Environment variables configured
- Public HTTPS endpoint

Start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Logging

Structured JSON logs via `structlog`:

```json
{
  "event": "user_input",
  "call_sid": "CAxxxx",
  "current_state": "piano_type",
  "input": "baby grand"
}
```

## Production Considerations

- **Sessions:** Currently in-memory. Use Redis for multi-instance deployment.
- **Geocoding:** Uses free Nominatim. Consider Google Maps API for accuracy.
- **Rate limiting:** Add rate limiting middleware.
- **Webhook verification:** Implement Twilio signature verification.

## License

MIT
