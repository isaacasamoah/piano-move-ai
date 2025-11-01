"""Claude LLM integration for conversation intelligence."""

import structlog
from anthropic import Anthropic
from typing import Optional, Dict, Any

from app.config import get_settings
from app.schemas import PianoType, ConversationState

logger = structlog.get_logger()


def get_claude_client() -> Optional[Anthropic]:
    """Get initialized Anthropic client."""
    settings = get_settings()

    # Check if API key is set (not the placeholder)
    if not settings.anthropic_api_key or settings.anthropic_api_key == "not_set":
        logger.warning("anthropic_api_key_not_configured")
        return None

    try:
        return Anthropic(api_key=settings.anthropic_api_key)
    except Exception as e:
        logger.error("claude_client_init_failed", error=str(e))
        return None


async def extract_quote_data(
    user_input: str,
    current_state: ConversationState,
    conversation_history: list[dict]
) -> Optional[Dict[str, Any]]:
    """
    Use Claude to extract structured data from user's natural language input.

    This is much more robust than keyword matching - handles variations,
    typos, and natural conversational patterns.

    Falls back to keyword matching if Claude is unavailable.
    """
    client = get_claude_client()

    # If Claude client not available, fall back to keyword extraction
    if client is None:
        logger.warning("claude_unavailable_using_fallback", state=current_state.value)
        return _fallback_keyword_extraction(user_input, current_state)

    # Build context-aware prompt based on conversation state
    system_prompt = _build_system_prompt(current_state)

    # Add conversation history for context
    messages = _build_messages(conversation_history, user_input)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            temperature=0.3,  # Low temperature for consistent extraction
            system=system_prompt,
            messages=messages
        )

        # Extract the content
        extracted_data = _parse_claude_response(response, current_state)

        logger.info(
            "claude_extraction",
            state=current_state.value,
            user_input=user_input,
            extracted=extracted_data
        )

        return extracted_data

    except Exception as e:
        logger.error(
            "claude_extraction_failed",
            error=str(e),
            state=current_state.value
        )
        # Fall back to keyword extraction on error
        return _fallback_keyword_extraction(user_input, current_state)


def _build_system_prompt(state: ConversationState) -> str:
    """Build context-specific system prompt for Claude."""

    base_prompt = """You are helping extract specific information from user responses in a piano moving quote conversation.
Extract ONLY the requested information. Be lenient with variations in how people speak.
Respond with JUST the extracted value, nothing else."""

    state_prompts = {
        ConversationState.GREETING: """
Extract the piano type from the user's response.
Valid types: upright, baby_grand, grand
Handle variations like "baby grand piano", "it's an upright", "grand", etc.
Respond with one word: upright, baby_grand, or grand
If unclear, respond: unknown
""",
        ConversationState.PIANO_TYPE: """
Extract the pickup address from the user's response.
Return the full address as stated by the user.
""",
        ConversationState.PICKUP_ADDRESS: """
Extract the delivery address from the user's response.
Return the full address as stated by the user.
""",
        ConversationState.DELIVERY_ADDRESS: """
Extract the number of stairs from the user's response.
Look for: "10 stairs", "ten steps", "no stairs", "none", etc.
Respond with just a number (e.g., "10" or "0")
If they say no stairs/none, respond: 0
""",
        ConversationState.STAIRS: """
Extract whether the user wants insurance.
Look for: yes, yeah, sure, definitely, no, nope, not needed, etc.
Respond with exactly: yes or no
"""
    }

    return base_prompt + state_prompts.get(state, "")


def _build_messages(history: list[dict], user_input: str) -> list[dict]:
    """Build message history for Claude with context."""
    messages = []

    # Add last few turns for context (keep it short for speed)
    recent_history = history[-4:] if len(history) > 4 else history
    for turn in recent_history:
        if turn["role"] == "user":
            messages.append({"role": "user", "content": turn["content"]})
        elif turn["role"] == "assistant":
            messages.append({"role": "assistant", "content": turn["content"]})

    # Add current user input
    messages.append({"role": "user", "content": user_input})

    return messages


def _parse_claude_response(response, state: ConversationState) -> Optional[Dict[str, Any]]:
    """Parse Claude's response into structured data."""

    content = response.content[0].text.strip().lower()

    # Parse based on state
    if state == ConversationState.GREETING:
        # Extract piano type
        if "upright" in content:
            return {"piano_type": PianoType.UPRIGHT}
        elif "baby" in content or "baby_grand" in content:
            return {"piano_type": PianoType.BABY_GRAND}
        elif "grand" in content:
            return {"piano_type": PianoType.GRAND}
        else:
            return None

    elif state == ConversationState.PIANO_TYPE:
        # Extract pickup address
        return {"pickup_address": response.content[0].text.strip()}

    elif state == ConversationState.PICKUP_ADDRESS:
        # Extract delivery address
        return {"delivery_address": response.content[0].text.strip()}

    elif state == ConversationState.DELIVERY_ADDRESS:
        # Extract stairs count
        try:
            stairs = int(''.join(filter(str.isdigit, content)))
            return {"stairs_count": stairs}
        except (ValueError, IndexError):
            if "no" in content or "none" in content or "zero" in content:
                return {"stairs_count": 0}
            return None

    elif state == ConversationState.STAIRS:
        # Extract insurance preference
        if "yes" in content or "yeah" in content or "sure" in content:
            return {"has_insurance": True}
        elif "no" in content or "nope" in content:
            return {"has_insurance": False}
        return None

    return None


def _fallback_keyword_extraction(user_input: str, state: ConversationState) -> Optional[Dict[str, Any]]:
    """
    Fallback keyword-based extraction when Claude is unavailable.
    Simple but functional - same as original implementation.
    """
    import re
    from app.schemas import PianoType

    user_input_lower = user_input.lower()

    if state == ConversationState.GREETING:
        # Extract piano type
        if "baby grand" in user_input_lower or "baby-grand" in user_input_lower:
            return {"piano_type": PianoType.BABY_GRAND}
        elif "grand" in user_input_lower:
            return {"piano_type": PianoType.GRAND}
        elif "upright" in user_input_lower:
            return {"piano_type": PianoType.UPRIGHT}
        return None

    elif state == ConversationState.PIANO_TYPE:
        return {"pickup_address": user_input.strip()}

    elif state == ConversationState.PICKUP_ADDRESS:
        return {"delivery_address": user_input.strip()}

    elif state == ConversationState.DELIVERY_ADDRESS:
        # Extract stairs count
        numbers = re.findall(r'\d+', user_input)
        if numbers:
            return {"stairs_count": int(numbers[0])}
        if any(word in user_input_lower for word in ["no stairs", "no", "none", "zero"]):
            return {"stairs_count": 0}
        return None

    elif state == ConversationState.STAIRS:
        # Extract insurance
        yes_words = ["yes", "yeah", "yep", "sure", "ok", "okay", "definitely"]
        no_words = ["no", "nope", "nah", "not"]
        if any(word in user_input_lower for word in yes_words):
            return {"has_insurance": True}
        elif any(word in user_input_lower for word in no_words):
            return {"has_insurance": False}
        return None

    return None
