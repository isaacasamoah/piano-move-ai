"""Conversation state management and flow control."""

from typing import Dict, Optional
import structlog
from datetime import datetime

from app.schemas import ConversationSession, ConversationState, QuoteDetails, PianoType

logger = structlog.get_logger()

# In-memory session storage (for MVP - use Redis in production)
sessions: Dict[str, ConversationSession] = {}


def get_or_create_session(call_sid: str, phone_number: str) -> ConversationSession:
    """Get existing session or create new one."""
    if call_sid not in sessions:
        session = ConversationSession(
            call_sid=call_sid,
            phone_number=phone_number,
            state=ConversationState.GREETING
        )
        sessions[call_sid] = session
        logger.info("session_created", call_sid=call_sid, phone_number=phone_number)
    return sessions[call_sid]


def update_session_state(call_sid: str, new_state: ConversationState):
    """Update session state."""
    if call_sid in sessions:
        old_state = sessions[call_sid].state
        sessions[call_sid].state = new_state
        logger.info(
            "state_transition",
            call_sid=call_sid,
            from_state=old_state.value,
            to_state=new_state.value
        )


def add_to_transcript(call_sid: str, role: str, content: str):
    """Add message to conversation transcript."""
    if call_sid in sessions:
        sessions[call_sid].transcript.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })


def get_next_prompt(session: ConversationSession) -> str:
    """
    Get the next prompt based on current conversation state.

    This implements the conversational flow:
    GREETING → PIANO_TYPE → PICKUP → DELIVERY → STAIRS → INSURANCE → QUOTE
    """
    state = session.state
    details = session.quote_details

    prompts = {
        ConversationState.GREETING: (
            "Hi! I'm Sandra from PianoMove AI. I can help you get an instant quote for moving your piano. "
            "First, what type of piano are you moving? Is it an upright, baby grand, or grand piano?"
        ),
        ConversationState.PIANO_TYPE: (
            f"Got it, a {details.piano_type.value.replace('_', ' ') if details.piano_type else 'piano'}. "
            "Beautiful! Where are we picking it up from? Please give me the full address."
        ),
        ConversationState.PICKUP_ADDRESS: (
            "Perfect. And where's it going? What's the delivery address?"
        ),
        ConversationState.DELIVERY_ADDRESS: (
            "Great! A few quick questions to finalize the quote. "
            "Are there any stairs at either location? If yes, how many?"
        ),
        ConversationState.STAIRS: (
            "Got it. Last question - would you like piano insurance for the move? "
            "This covers any potential damage during transport."
        ),
        ConversationState.INSURANCE: (
            "Excellent. Let me calculate that for you now..."
        ),
    }

    return prompts.get(state, "I'm ready to help with your piano move!")


def extract_piano_type(user_input: str) -> Optional[PianoType]:
    """Extract piano type from user input using simple keyword matching."""
    user_input = user_input.lower()

    if "baby grand" in user_input or "baby-grand" in user_input:
        return PianoType.BABY_GRAND
    elif "grand" in user_input:
        return PianoType.GRAND
    elif "upright" in user_input:
        return PianoType.UPRIGHT

    return None


def extract_yes_no(user_input: str) -> Optional[bool]:
    """Extract yes/no from user input."""
    user_input = user_input.lower()

    yes_words = ["yes", "yeah", "yep", "sure", "ok", "okay", "definitely", "absolutely"]
    no_words = ["no", "nope", "nah", "not"]

    if any(word in user_input for word in yes_words):
        return True
    elif any(word in user_input for word in no_words):
        return False

    return None


def extract_stairs_count(user_input: str) -> Optional[int]:
    """Extract number of stairs from user input."""
    import re

    # Look for numbers in the input
    numbers = re.findall(r'\d+', user_input)

    if numbers:
        return int(numbers[0])

    # Check for "no stairs" or similar
    if any(word in user_input.lower() for word in ["no stairs", "no", "none", "zero"]):
        return 0

    return None


def process_user_input(session: ConversationSession, user_input: str) -> ConversationState:
    """
    Process user input and update session data.
    Returns the next state to transition to.
    """
    current_state = session.state
    details = session.quote_details

    # State machine transitions
    if current_state == ConversationState.GREETING:
        # Extract piano type
        piano_type = extract_piano_type(user_input)
        if piano_type:
            details.piano_type = piano_type
            return ConversationState.PIANO_TYPE
        else:
            # Stay in same state, will ask again
            return ConversationState.GREETING

    elif current_state == ConversationState.PIANO_TYPE:
        # Extract pickup address
        details.pickup_address = user_input.strip()
        return ConversationState.PICKUP_ADDRESS

    elif current_state == ConversationState.PICKUP_ADDRESS:
        # Extract delivery address
        details.delivery_address = user_input.strip()
        return ConversationState.DELIVERY_ADDRESS

    elif current_state == ConversationState.DELIVERY_ADDRESS:
        # Extract stairs count
        stairs = extract_stairs_count(user_input)
        if stairs is not None:
            details.stairs_count = stairs
            return ConversationState.STAIRS
        else:
            # Stay in same state
            return ConversationState.DELIVERY_ADDRESS

    elif current_state == ConversationState.STAIRS:
        # Extract insurance preference
        wants_insurance = extract_yes_no(user_input)
        if wants_insurance is not None:
            details.has_insurance = wants_insurance
            return ConversationState.INSURANCE
        else:
            return ConversationState.STAIRS

    elif current_state == ConversationState.INSURANCE:
        return ConversationState.QUOTE_READY

    return current_state


def is_session_complete(session: ConversationSession) -> bool:
    """Check if we have all information needed for quote."""
    d = session.quote_details
    return all([
        d.piano_type is not None,
        d.pickup_address is not None,
        d.delivery_address is not None,
        d.stairs_count is not None,
        d.has_insurance is not None
    ])
