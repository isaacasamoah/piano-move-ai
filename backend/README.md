# PianoMove AI Backend

FastAPI backend for voice-powered piano moving quote generation using Twilio and Claude AI.

## Architecture

- **FastAPI**: Async web framework
- **Twilio**: Voice call handling and SMS delivery
- **Claude (Anthropic)**: Conversational AI (future integration)
- **Geopy**: Distance calculation between addresses
- **SQLite**: Session storage (MVP - use Postgres in production)

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required credentials:
- **Twilio**: Get from https://console.twilio.com
- **Anthropic API**: Get from https://console.anthropic.com

### 3. Run Development Server

```bash
python -m app.main
# Or use uvicorn directly:
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

### 4. Expose Local Server (for Twilio webhooks)

Use ngrok to expose your local server:

```bash
ngrok http 8000
```

Copy the ngrok URL and configure it in Twilio:
- Go to your Twilio Phone Number settings
- Set Voice Webhook to: `https://your-ngrok-url.ngrok.io/twilio/voice`

## API Endpoints

- `GET /health` - Health check
- `POST /twilio/voice` - Twilio webhook for voice calls
- `GET /` - API information

## Conversation Flow

1. **Greeting**: "What type of piano are you moving?"
2. **Piano Type**: Upright, Baby Grand, or Grand
3. **Pickup Address**: Where to pick up the piano
4. **Delivery Address**: Where to deliver the piano
5. **Stairs**: How many stairs (if any)
6. **Insurance**: Whether customer wants insurance
7. **Quote**: Calculate and deliver quote via SMS

## Quote Calculation

**Base Prices:**
- Upright: $200
- Baby Grand: $350
- Grand: $500

**Additional Charges:**
- Distance: $1.50/km
- Stairs: $15/stair
- Insurance: 15% of subtotal

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app and routes
│   ├── config.py            # Settings and env vars
│   ├── schemas.py           # Pydantic models
│   ├── conversation.py      # State machine and session management
│   ├── twilio_handler.py    # Twilio webhook logic
│   └── quote_engine.py      # Quote calculation
├── requirements.txt
├── .env.example
└── README.md
```

## Testing

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Call Your Number:**
   - Call the Twilio number
   - Follow the voice prompts
   - Receive SMS with quote

## Production Deployment

### Railway (Recommended)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Set environment variables in Railway dashboard.

### Render

1. Create new Web Service
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables

## Environment Variables

See `.env.example` for all required variables.

## Monitoring

Logs are output as structured JSON (using `structlog`):

```json
{
  "event": "user_input",
  "call_sid": "CA1234...",
  "current_state": "piano_type",
  "input": "baby grand",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Cost Tracking

Per call costs (approximate):
- Twilio voice: $0.0085/min
- Twilio SMS: $0.0075/message
- Geopy API: Free (using Nominatim)
- **Total: ~$0.05/call** (3-min average)

## Next Steps

- [ ] Add database persistence (Postgres)
- [ ] Integrate Claude for smarter conversation handling
- [ ] Add call recording
- [ ] Build admin dashboard
- [ ] Add PDF quote generation
- [ ] Implement analytics

## License

MIT
