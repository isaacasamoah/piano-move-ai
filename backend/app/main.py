"""FastAPI application for PianoMove AI voice assistant."""

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
import structlog
from datetime import datetime

from app.config import get_settings
from app.twilio_handler import handle_incoming_call, handle_voice_input
from app.twilio_handler_agent import (
    handle_incoming_call_agent,
    handle_voice_input_agent
)
import random

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    settings = get_settings()
    logger.info("startup", app_name=settings.app_name)
    yield
    logger.info("shutdown")


app = FastAPI(
    title="PianoMove AI",
    description="Voice-powered piano moving quote generator",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "pianomove-ai"
    }


@app.post("/twilio/voice", response_class=PlainTextResponse)
async def twilio_voice_webhook(request: Request):
    """
    Twilio webhook for incoming voice calls.

    This endpoint handles the initial call and all subsequent user inputs.
    Returns TwiML (Twilio Markup Language) to control the call flow.

    Supports A/B testing between agent and state machine.
    """
    settings = get_settings()
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    to_number = form_data.get("To")
    speech_result = form_data.get("SpeechResult")

    # Determine which handler to use (A/B testing)
    use_agent = _should_use_agent(call_sid, settings)

    logger.info(
        "twilio_webhook",
        call_sid=call_sid,
        from_number=from_number,
        to_number=to_number,
        speech_result=speech_result,
        handler="agent" if use_agent else "state_machine"
    )

    # Route to appropriate handler
    if use_agent:
        # NEW: Claude agent handler
        if not speech_result:
            return await handle_incoming_call_agent(call_sid, from_number, to_number)
        return await handle_voice_input_agent(call_sid, from_number, speech_result)
    else:
        # OLD: State machine handler
        if not speech_result:
            return await handle_incoming_call(call_sid, from_number)
        return await handle_voice_input(call_sid, from_number, speech_result)


def _should_use_agent(call_sid: str, settings) -> bool:
    """
    Determine whether to use agent or state machine for this call.

    Supports:
    1. Full rollout (use_agent=True, rollout=100%)
    2. A/B testing (use_agent=True, rollout=50% for example)
    3. State machine only (use_agent=False)

    Args:
        call_sid: Unique call identifier (for consistent assignment)
        settings: Application settings

    Returns:
        True if should use agent, False for state machine
    """
    if not settings.use_agent:
        return False

    # Full rollout
    if settings.agent_rollout_percentage >= 100:
        return True

    # No rollout
    if settings.agent_rollout_percentage <= 0:
        return False

    # A/B test: Use call_sid hash for consistent assignment
    # Same call_sid always gets same handler (important for multi-turn conversations)
    hash_value = abs(hash(call_sid)) % 100
    return hash_value < settings.agent_rollout_percentage


@app.get("/")
async def root():
    """Root endpoint with basic info."""
    return {
        "service": "PianoMove AI",
        "version": "1.0.0",
        "description": "Voice-powered piano moving quote generator",
        "endpoints": {
            "health": "/health",
            "twilio_webhook": "/twilio/voice"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
