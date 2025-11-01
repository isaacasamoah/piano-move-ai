"""FastAPI application for PianoMove AI voice assistant."""

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from contextlib import asynccontextmanager
import structlog
from datetime import datetime

from app.config import get_settings
from app.twilio_handler import handle_incoming_call, handle_voice_input

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
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    from_number = form_data.get("From")
    speech_result = form_data.get("SpeechResult")

    logger.info(
        "twilio_webhook",
        call_sid=call_sid,
        from_number=from_number,
        speech_result=speech_result
    )

    # If this is the initial call (no speech result yet)
    if not speech_result:
        return await handle_incoming_call(call_sid, from_number)

    # Handle user's voice input
    return await handle_voice_input(call_sid, from_number, speech_result)


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
