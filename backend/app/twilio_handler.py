"""Twilio webhook handlers for voice calls and SMS."""

import structlog
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client

from app.config import get_settings
from app.conversation import (
    get_or_create_session,
    add_to_transcript,
    get_next_prompt,
    process_user_input,
    update_session_state,
    is_session_complete,
    ConversationState
)
from app.quote_engine import calculate_quote, format_quote_summary

logger = structlog.get_logger()


async def handle_incoming_call(call_sid: str, from_number: str) -> str:
    """
    Handle initial incoming call.
    Returns TwiML to greet user and start conversation.
    """
    # Create new session
    session = get_or_create_session(call_sid, from_number)

    # Get greeting prompt
    greeting = get_next_prompt(session)

    # Add to transcript
    add_to_transcript(call_sid, "assistant", greeting)

    # Create TwiML response
    response = VoiceResponse()

    # Use <Gather> to collect speech input
    gather = Gather(
        input="speech",
        action="/twilio/voice",
        method="POST",
        speech_timeout="auto",
        language="en-US"
    )
    gather.say(greeting, voice="Polly.Joanna")

    response.append(gather)

    # If user doesn't say anything, prompt again
    response.say("I didn't hear anything. Please call back when you're ready!", voice="Polly.Joanna")

    return str(response)


async def handle_voice_input(call_sid: str, from_number: str, speech_result: str) -> str:
    """
    Handle user's voice input during conversation.
    Returns TwiML with next prompt or quote summary.
    """
    # Get session
    session = get_or_create_session(call_sid, from_number)

    # Add user input to transcript
    add_to_transcript(call_sid, "user", speech_result)

    logger.info(
        "user_input",
        call_sid=call_sid,
        current_state=session.state.value,
        input=speech_result
    )

    # Process input and get next state
    next_state = process_user_input(session, speech_result)

    # Update session state
    update_session_state(call_sid, next_state)

    # Check if we have all information for quote
    if next_state == ConversationState.INSURANCE and is_session_complete(session):
        # Generate quote
        return await generate_and_deliver_quote(call_sid, from_number)

    # Get next prompt
    next_prompt = get_next_prompt(session)

    # Add to transcript
    add_to_transcript(call_sid, "assistant", next_prompt)

    # Create TwiML response
    response = VoiceResponse()

    gather = Gather(
        input="speech",
        action="/twilio/voice",
        method="POST",
        speech_timeout="auto",
        language="en-US"
    )
    gather.say(next_prompt, voice="Polly.Joanna")

    response.append(gather)

    # Fallback if no input
    response.say("Sorry, I didn't catch that. Let me ask again.", voice="Polly.Joanna")
    response.redirect("/twilio/voice")

    return str(response)


async def generate_and_deliver_quote(call_sid: str, from_number: str) -> str:
    """
    Generate quote, send SMS, and end call gracefully.
    """
    session = get_or_create_session(call_sid, from_number)
    details = session.quote_details

    # Calculate quote
    calculation = await calculate_quote(details)

    # Update session with quote amount
    details.quote_amount = calculation.total
    details.distance_km = calculation.distance_km

    # Format summary message
    piano_name = details.piano_type.value.replace('_', ' ') if details.piano_type else "piano"

    summary_speech = (
        f"Alright! Based on your {piano_name}, "
        f"traveling {calculation.distance_km:.0f} kilometers, "
        f"with {details.stairs_count or 0} stairs, "
        f"{'and insurance included, ' if details.has_insurance else ''}"
        f"your total quote is ${calculation.total:.0f}. "
        f"I'm sending the full details to your phone right now. "
        f"Thanks for choosing PianoMove!"
    )

    # Add to transcript
    add_to_transcript(call_sid, "assistant", summary_speech)

    # Send SMS with detailed quote
    await send_quote_sms(from_number, details, calculation)

    # Mark session as completed
    update_session_state(call_sid, ConversationState.COMPLETED)

    # Create final TwiML response
    response = VoiceResponse()
    response.say(summary_speech, voice="Polly.Joanna")
    response.hangup()

    logger.info(
        "quote_delivered",
        call_sid=call_sid,
        phone_number=from_number,
        quote_amount=calculation.total
    )

    return str(response)


async def send_quote_sms(phone_number: str, details, calculation) -> None:
    """
    Send SMS with detailed quote to customer.
    """
    settings = get_settings()

    # Format quote summary
    message_body = format_quote_summary(details, calculation)

    try:
        # Initialize Twilio client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_=settings.twilio_phone_number,
            to=phone_number
        )

        logger.info(
            "sms_sent",
            to=phone_number,
            message_sid=message.sid,
            quote_amount=calculation.total
        )

    except Exception as e:
        logger.error(
            "sms_send_failed",
            to=phone_number,
            error=str(e)
        )
