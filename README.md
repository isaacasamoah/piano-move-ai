# 🎹 PianoMove AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

> Production-ready voice AI system for automated quote generation. Customers call, describe their piano move, and receive instant quotes via SMS.

## 🎯 Overview

PianoMove AI demonstrates a complete voice AI pipeline for service businesses. The system uses Twilio for telephony, Claude Sonnet 4 for natural language understanding, and FastAPI for orchestration.

**Live Demo:**
- **Phone:** +1 (229) 922-3706
- **API:** https://backend-production-178ff.up.railway.app
- **Health:** https://backend-production-178ff.up.railway.app/health

*Note: Demo uses Twilio trial - phone numbers require verification. Contact to be added.*

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Twilio account ([free trial](https://www.twilio.com/try-twilio))
- Anthropic API key ([get one](https://console.anthropic.com/))

### Installation

```bash
# Clone repository
git clone https://github.com/isaacasamoah/pianomove-ai.git
cd pianomove-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Start server
python -m app.main
```

Server runs on `http://localhost:8000`

### Expose with Ngrok

For Twilio webhooks:

```bash
ngrok http 8000
# Configure Twilio webhook: https://your-url.ngrok.io/twilio/voice
```

## 📞 How It Works

1. Customer calls Twilio number
2. Twilio STT converts speech to text
3. Claude extracts structured data (piano type, addresses, stairs, insurance)
4. System geocodes addresses and calculates distance
5. Quote engine applies pricing logic
6. TTS speaks quote over phone
7. SMS delivers detailed breakdown

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed diagrams and technical deep-dive.

## 💰 Pricing Logic

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
    quote *= 1.15                # +15% insurance
```

## 🏗 Architecture

```
Customer Call → Twilio → FastAPI → Claude NLU
                           ↓
                    Quote Engine → SMS Delivery
```

**Key Components:**
- **FastAPI** - Async webhook orchestration
- **Twilio** - Voice, STT, TTS, SMS
- **Claude Sonnet 4** - Natural language extraction
- **Nominatim** - Free geocoding (OSM)
- **Railway** - Cloud deployment

Full architecture documentation: [ARCHITECTURE.md](ARCHITECTURE.md)

## 📂 Project Structure

```
pianomove-ai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── twilio_handler.py  # Voice webhooks
│   │   ├── llm.py             # Claude integration
│   │   ├── conversation.py    # State machine
│   │   ├── quote_engine.py    # Pricing logic
│   │   ├── schemas.py         # Pydantic models
│   │   └── config.py          # Settings
│   ├── requirements.txt
│   └── .env.example
├── ARCHITECTURE.md            # Technical documentation
├── LICENSE
└── README.md
```

## 🔧 Configuration

Environment variables (`.env`):

```bash
# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Optional
SERVER_URL=http://localhost:8000
DEBUG=True
```

## 🧪 Testing

```bash
# Test basic setup
python backend/test_setup.py

# Make a test call
# Call +1 (229) 922-3706 and follow prompts
```

## 💸 Cost Structure

Per-call costs (3-minute average):
- Twilio voice: $0.026
- Twilio SMS: $0.008
- Claude API: $0.003
- Geocoding: Free

**Total: ~$0.04/call**

At 10,000 calls/month: **$400 infrastructure cost**

## 🚀 Deployment

### Railway (Recommended)

```bash
# Connect GitHub repository
railway link

# Deploy
railway up
```

Auto-deploys on git push to main.

### Manual Deployment

Requires:
- Python 3.11+ runtime
- Environment variables configured
- Public HTTPS endpoint for Twilio webhooks

## 🔒 Security

- Environment variables for all secrets
- Twilio webhook signature verification (recommended)
- In-memory sessions (MVP) - use Redis for production
- Structured logging (no PII in logs)

## 🎓 Technical Highlights

**Async/await throughout:**
```python
async def handle_voice_input(call_sid: str, speech_result: str):
    session = get_or_create_session(call_sid)
    next_state = await process_user_input(session, speech_result)
    # ...
```

**Graceful fallbacks:**
- Claude unavailable → keyword extraction
- Geocoding fails → 50km default
- Invalid input → re-prompt in same state

**State machine design:**
```
GREETING → PIANO_TYPE → PICKUP → DELIVERY → STAIRS → INSURANCE → QUOTE
```

## 📖 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design, call flow, scaling
- [backend/README.md](backend/README.md) - Backend setup details
- [.env.example](backend/.env.example) - Configuration template

## 🤝 Contributing

This is an open-source project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

**Isaac Asamoah**
- LinkedIn: [linkedin.com/in/isaacasamoah](https://linkedin.com/in/isaacasamoah)
- GitHub: [github.com/isaacasamoah](https://github.com/isaacasamoah)
- Email: isaacasamoah@gmail.com

---

Built with FastAPI, Claude, and Twilio. Deployed on Railway.
