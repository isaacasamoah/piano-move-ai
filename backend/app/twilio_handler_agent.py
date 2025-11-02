"""
Twilio webhook handlers using Claude agent (replaces state machine).

This is the NEW implementation that uses flexible Claude-driven conversations.
"""

from twilio.twiml.voice_response import VoiceResponse, Gather
import structlog

from app.agent import claude_agent_turn
from app.business_config import get_business_from_twilio_number, load_business_config
from app.quote_engine import calculate_quote, format_quote_summary
from app.config import get_settings
from app.schemas import QuoteDetails, PianoType

logger = structlog.get_logger()

# In-memory sessions (MVP - use Redis in production)
sessions = {}


async def handle_incoming_call_agent(call_sid: str, from_number: str, to_number: str) -> str:
    """
    Handle initial incoming call using agent.

    Args:
        call_sid: Twilio call identifier
        from_number: Customer phone number
        to_number: Twilio number that was called

    Returns:
        TwiML response as string
    """
    # Identify which business this call is for
    business_id = get_business_from_twilio_number(to_number)

    if not business_id:
        logger.error("business_not_identified", to_number=to_number)
        return _generate_error_twiml("I'm sorry, I couldn't identify which service you're calling. Please try again later.")

    # Load business config
    try:
        business_config = load_business_config(business_id)
    except FileNotFoundError:
        logger.error("business_config_load_failed", business_id=business_id)
        return _generate_error_twiml("I'm sorry, there was a configuration error. Please call back later.")

    # Create session
    required_fields = business_config.get("quote_calculation", {}).get("required_fields", [])

    session_data = {field: None for field in required_fields}

    sessions[call_sid] = {
        "business_id": business_id,
        "from_number": from_number,
        "to_number": to_number,
        "session_data": session_data,
        "transcript": [],
        "business_config": business_config
    }

    logger.info(
        "call_started_with_agent",
        call_sid=call_sid,
        business_id=business_id,
        from_number=from_number
    )

    # Get initial greeting from agent
    initial_input = ""  # Empty input triggers greeting
    response = await claude_agent_turn(
        user_input=initial_input,
        business_id=business_id,
        business_config=business_config,
        collected_data=session_data,
        transcript=[]
    )

    # Add to transcript
    sessions[call_sid]["transcript"].append({
        "role": "agent",
        "content": response.get("response", "")
    })

    # Generate TwiML
    return _generate_gather_twiml(response.get("response", "Hello!"))


async def handle_voice_input_agent(call_sid: str, from_number: str, speech_result: str) -> str:
    """
    Handle voice input using Claude agent.

    Args:
        call_sid: Twilio call identifier
        from_number: Customer phone number
        speech_result: What customer said (from Twilio STT)

    Returns:
        TwiML response as string
    """
    # Get session
    if call_sid not in sessions:
        logger.warning("session_not_found", call_sid=call_sid)
        return _generate_error_twiml("I'm sorry, I lost track of our conversation. Please call back.")

    session = sessions[call_sid]
    business_id = session["business_id"]
    business_config = session["business_config"]
    session_data = session["session_data"]
    transcript = session["transcript"]

    # Add user input to transcript
    transcript.append({
        "role": "user",
        "content": speech_result
    })

    logger.info(
        "user_input_received",
        call_sid=call_sid,
        business_id=business_id,
        user_input=speech_result
    )

    # Get agent response
    response = await claude_agent_turn(
        user_input=speech_result,
        business_id=business_id,
        business_config=business_config,
        collected_data=session_data,
        transcript=transcript
    )

    # Update session with extracted data
    extracted = response.get("extracted", {})
    for field, value in extracted.items():
        if value is not None:
            session_data[field] = value

    # Add agent response to transcript
    transcript.append({
        "role": "agent",
        "content": response.get("response", "")
    })

    logger.info(
        "agent_response_generated",
        call_sid=call_sid,
        extracted_fields=list(extracted.keys()),
        is_complete=response.get("is_complete", False),
        should_transfer=response.get("should_transfer_to_human", False)
    )

    # Check if should transfer to human
    if response.get("should_transfer_to_human"):
        logger.info(
            "transferring_to_human",
            call_sid=call_sid,
            reason=response.get("transfer_reason")
        )
        settings = get_settings()
        return _generate_transfer_twiml(
            response.get("response", "Let me connect you with our team."),
            transfer_number=settings.transfer_phone_number if hasattr(settings, 'transfer_phone_number') else None
        )

    # Check if quote is ready
    if response.get("is_complete"):
        logger.info("quote_ready", call_sid=call_sid)
        return await _generate_and_deliver_quote_agent(call_sid, session_data, business_config)

    # Continue conversation
    return _generate_gather_twiml(response.get("response", "Could you repeat that?"))


async def _generate_and_deliver_quote_agent(
    call_sid: str,
    session_data: dict,
    business_config: dict
) -> str:
    """
    Generate quote and deliver via voice + SMS.

    Args:
        call_sid: Twilio call identifier
        session_data: Collected quote data
        business_config: Business configuration

    Returns:
        TwiML response
    """
    from app.schemas import QuoteDetails, PianoType

    # Convert session_data to QuoteDetails
    # This is piano-specific - would be generalized for platform
    quote_details = QuoteDetails(
        piano_type=PianoType(session_data.get("piano_type")),
        pickup_address=session_data.get("pickup_address"),
        delivery_address=session_data.get("delivery_address"),
        stairs_count=session_data.get("stairs_count", 0),
        has_insurance=session_data.get("has_insurance", False)
    )

    # Calculate quote
    calculation = await calculate_quote(quote_details)

    logger.info(
        "quote_calculated_via_agent",
        call_sid=call_sid,
        total=calculation.total,
        distance_km=calculation.distance_km
    )

    # Build voice response
    company_name = business_config.get("display_name", "our service")
    voice_template = business_config.get("quote_delivery", {}).get("voice", {}).get("template")

    if voice_template:
        # Use configured template
        voice_response = voice_template.format(
            piano_type=quote_details.piano_type.value.replace('_', ' '),
            total=f"{calculation.total:.2f}",
            distance_km=f"{calculation.distance_km:.0f}",
            stairs_text=f", {quote_details.stairs_count} stairs" if quote_details.stairs_count > 0 else "",
            insurance_text=", and insurance" if quote_details.has_insurance else ""
        )
    else:
        # Default template
        voice_response = (
            f"Your quote is ${calculation.total:.2f}. "
            f"That includes {calculation.distance_km:.0f} kilometers of travel. "
            f"I'm sending the details to your phone now. Thanks for choosing {company_name}!"
        )

    # Send SMS
    session = sessions.get(call_sid)
    if session:
        await _send_quote_sms_agent(
            to_number=session["from_number"],
            quote_details=quote_details,
            calculation=calculation,
            business_config=business_config
        )

    # Generate TwiML
    twiml = VoiceResponse()
    twiml.say(voice_response, voice="Polly.Joanna")
    twiml.pause(length=2)
    twiml.hangup()

    # Mark session as complete
    sessions[call_sid]["completed"] = True

    return str(twiml)


async def _send_quote_sms_agent(
    to_number: str,
    quote_details: QuoteDetails,
    calculation,
    business_config: dict
):
    """Send quote via SMS using business config."""
    from twilio.rest import Client

    settings = get_settings()

    # Check if Twilio is configured
    if settings.twilio_account_sid == "not_set":
        logger.warning("twilio_not_configured_skipping_sms")
        return

    try:
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

        # Format SMS using business config
        trial_mode = business_config.get("quote_delivery", {}).get("sms", {}).get("trial_mode", True)
        sms_body = format_quote_summary(quote_details, calculation, trial_mode=trial_mode)

        # Send SMS
        message = client.messages.create(
            body=sms_body,
            from_=settings.twilio_phone_number,
            to=to_number
        )

        logger.info(
            "sms_sent_via_agent",
            to=to_number,
            message_sid=message.sid,
            trial_mode=trial_mode
        )

    except Exception as e:
        logger.error("sms_send_failed", error=str(e), to=to_number)


def _generate_gather_twiml(prompt: str) -> str:
    """Generate TwiML with Gather for STT."""
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/twilio/voice",
        method="POST",
        timeout=5,  # Increased from 3 to give user more time
        speech_timeout=3,  # Wait 3 seconds after user stops talking
        hints="upright, baby grand, grand piano, yes, no"  # Help Twilio STT
    )
    gather.say(prompt, voice="Polly.Joanna")
    response.append(gather)

    # Fallback if no input
    response.say("I didn't hear anything. Please call back when you're ready.", voice="Polly.Joanna")
    response.hangup()

    return str(response)


def _generate_transfer_twiml(message: str, transfer_number: str = None) -> str:
    """Generate TwiML to transfer call to human."""
    response = VoiceResponse()
    response.say(message, voice="Polly.Joanna")

    if transfer_number:
        response.say(f"Transferring you now...", voice="Polly.Joanna")
        response.dial(transfer_number)
    else:
        response.say("Please call our main office for assistance. Thank you.", voice="Polly.Joanna")
        response.hangup()

    return str(response)


def _generate_error_twiml(message: str) -> str:
    """Generate error TwiML."""
    response = VoiceResponse()
    response.say(message, voice="Polly.Joanna")
    response.hangup()
    return str(response)
