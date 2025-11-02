"""
Voice Agent - Config-Driven Conversational Extraction

The entire voice agent system in ~200 lines.
Add a JSON config, get a voice agent.

Architecture:
- Twilio handles voice + STT/TTS
- Claude handles conversation + extraction
- Config defines what to extract
- Calculator functions handle quote logic
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import structlog
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from anthropic import Anthropic

# Setup
app = FastAPI()
logger = structlog.get_logger()
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# In-memory sessions (use Redis for production)
sessions: Dict[str, Dict[str, Any]] = {}

# Config cache
configs: Dict[str, Dict[str, Any]] = {}


def load_config(phone_number: str) -> Optional[Dict[str, Any]]:
    """Load business config by phone number."""
    # Check cache
    if phone_number in configs:
        return configs[phone_number]

    # Load all configs and find match
    config_dir = Path(__file__).parent / "config"
    for config_file in config_dir.glob("*.json"):
        with open(config_file) as f:
            config = json.load(f)
            if config.get("phone_number") == phone_number:
                configs[phone_number] = config
                return config

    return None


def build_claude_prompt(business: Dict[str, Any], session: Dict[str, Any]) -> str:
    """Build Claude system prompt from config."""
    agent_name = business["agent"]["name"]
    company_name = business["display_name"]
    extract_fields = business["extract"]

    # Build field descriptions
    field_list = []
    for field_name, field_config in extract_fields.items():
        field_type = field_config["type"]
        options = field_config.get("options", [])
        hint = field_config.get("hint", "")

        if options:
            field_list.append(f"- {field_name} ({field_type}: {', '.join(options)})")
        else:
            field_list.append(f"- {field_name} ({field_type})")

        if hint:
            field_list.append(f"  Example: \"{hint}\"")

    fields_text = "\n".join(field_list)

    # Current extraction state
    current_data = {k: v for k, v in session["data"].items() if v is not None}
    missing_fields = [k for k, v in session["data"].items() if v is None]

    return f"""You're {agent_name}, helping a customer get a quote from {company_name}.

EXTRACT these fields through natural conversation:

{fields_text}

RULES:
- Be warm, friendly, and efficient (like a helpful human)
- Keep responses under 2 sentences
- Extract multiple fields if customer volunteers them
- Never assume - ask for clarification if ambiguous
- Acknowledge what the customer says ("Got it", "Perfect", "Thanks")

CURRENT STATE:
Collected: {json.dumps(current_data, indent=2) if current_data else "Nothing yet"}
Still need: {', '.join(missing_fields) if missing_fields else 'All fields collected!'}

CONVERSATION HISTORY:
{chr(10).join([f"{t['role']}: {t['content']}" for t in session['transcript'][-4:]])}

RESPOND with ONLY this JSON format:
{{
  "message": "What you say to the customer next (1-2 sentences)",
  "extracted": {{"field_name": "value"}},
  "is_complete": false
}}

Set "is_complete": true only when ALL required fields are collected and confirmed.
"""


async def claude_turn(user_speech: str, business: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
    """Get Claude's response to user input."""
    # Add user input to transcript
    session["transcript"].append({"role": "customer", "content": user_speech})

    # Build prompt
    system_prompt = build_claude_prompt(business, session)

    # Call Claude
    response = claude_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Customer just said: \"{user_speech}\""}]
    )

    # Parse JSON response
    response_text = response.content[0].text
    agent_response = json.loads(response_text)

    # Add to transcript
    session["transcript"].append({"role": "agent", "content": agent_response["message"]})

    # Update extracted data
    for field, value in agent_response.get("extracted", {}).items():
        if value is not None:
            session["data"][field] = value

    logger.info(
        "claude_turn_complete",
        extracted=agent_response.get("extracted"),
        is_complete=agent_response.get("is_complete"),
        message_length=len(agent_response["message"])
    )

    return agent_response


def generate_twiml(message: str, business: Dict[str, Any]) -> str:
    """Generate TwiML for voice response."""
    voice_settings = business.get("voice_settings", {})
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/voice",
        method="POST",
        timeout=voice_settings.get("listen_timeout", 4),
        speech_timeout=voice_settings.get("speech_end_timeout", 1.5),
        hints=voice_settings.get("stt_hints", "")
    )

    gather.say(message, voice=business["agent"]["voice"])
    response.append(gather)

    # Fallback if no input
    response.say(
        "Sorry, I didn't catch that. Could you please repeat that?",
        voice=business["agent"]["voice"]
    )

    return str(response)


@app.get("/")
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {"status": "healthy", "service": "voice_agent"}


@app.post("/voice", response_class=PlainTextResponse)
async def handle_voice(
    CallSid: str = Form(...),
    From: str = Form(...),
    To: str = Form(...),
    SpeechResult: Optional[str] = Form(None)
):
    """Handle Twilio voice webhook."""
    logger.info("voice_webhook", call_sid=CallSid, from_number=From, to_number=To, has_speech=bool(SpeechResult))

    # Load business config
    business = load_config(To)
    if not business:
        logger.error("business_not_found", to_number=To)
        response = VoiceResponse()
        response.say("Sorry, there was a configuration error. Please try again later.")
        response.hangup()
        return str(response)

    # New call? Initialize session and send greeting
    if CallSid not in sessions:
        # Initialize session
        sessions[CallSid] = {
            "business_id": business["business_id"],
            "from_number": From,
            "data": {field: None for field in business["extract"].keys()},
            "transcript": []
        }

        logger.info("new_call_started", call_sid=CallSid, business_id=business["business_id"])

        # Send greeting (from config, no Claude call needed)
        greeting = business["agent"]["greeting"]
        return generate_twiml(greeting, business)

    # No speech? Timeout or error
    if not SpeechResult:
        logger.warning("no_speech_result", call_sid=CallSid)
        return generate_twiml("I didn't catch that. Could you tell me again?", business)

    # Get session
    session = sessions[CallSid]

    # Get Claude's response
    try:
        agent_response = await claude_turn(SpeechResult, business, session)
    except Exception as e:
        logger.error("claude_turn_failed", error=str(e), call_sid=CallSid)
        response = VoiceResponse()
        response.say("Sorry, I'm having trouble processing that. Let me transfer you to someone who can help.")
        response.hangup()
        return str(response)

    # Complete? Calculate quote and send SMS
    if agent_response.get("is_complete"):
        # Import calculator dynamically
        calculator_name = business.get("quote_calculator", "calculate_quote")
        from calculators import piano_quote
        calculator_func = getattr(piano_quote, calculator_name)

        # Calculate quote
        quote = calculator_func(session["data"], business)

        # Send SMS
        # TODO: Implement SMS sending via Twilio

        # Build completion message
        completion_msg = business.get("completion_message", "Your quote is ${total}. I'm texting you the details now!")
        completion_msg = completion_msg.format(
            total=quote["total"],
            company_name=business["display_name"]
        )

        # Clean up session
        del sessions[CallSid]

        # Send final message and hang up
        response = VoiceResponse()
        response.say(completion_msg, voice=business["agent"]["voice"])
        response.hangup()
        return str(response)

    # Not complete - continue conversation
    return generate_twiml(agent_response["message"], business)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
