"""
Claude agent implementation for conversational quote gathering.

This replaces the state machine with a flexible Claude-driven conversation.
"""

from typing import Dict, Any, List, Optional
import structlog
from anthropic import Anthropic
import json

from app.config import get_settings
from app.prompt_composer import compose_agent_prompt

logger = structlog.get_logger()


class ClaudeAgent:
    """Claude-powered conversational agent for quote gathering."""

    def __init__(self):
        """Initialize Claude client."""
        self.settings = get_settings()
        self.client = self._get_claude_client()

    def _get_claude_client(self) -> Optional[Anthropic]:
        """Get Claude client if API key is configured."""
        if not self.settings.anthropic_api_key or self.settings.anthropic_api_key == "not_set":
            logger.warning("anthropic_api_key_not_configured")
            return None
        return Anthropic(api_key=self.settings.anthropic_api_key)

    async def process_turn(
        self,
        user_input: str,
        business_id: str,
        business_config: Dict[str, Any],
        session_data: Dict[str, Any],
        transcript: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process a single conversation turn.

        Args:
            user_input: What the customer just said
            business_id: Which business this call is for
            business_config: Business configuration (loaded from DB/JSON)
            session_data: Current session state (collected fields)
            transcript: Full conversation history

        Returns:
            Agent response with extracted data and instructions
            {
                "response": "What to say to customer",
                "extracted": {"field": "value", ...},
                "thinking": "Internal reasoning",
                "needs_clarification": ["field"],
                "is_complete": bool,
                "should_transfer_to_human": bool,
                "transfer_reason": str | null
            }
        """

        # Check if Claude is available
        if self.client is None:
            logger.warning("claude_not_available_using_fallback", business_id=business_id)
            return self._fallback_response(user_input, session_data, business_config)

        try:
            # Compose system prompt at runtime
            system_prompt = compose_agent_prompt(
                business_id=business_id,
                business_config=business_config,
                session_data=session_data,
                transcript=transcript
            )

            # Add user input to transcript
            messages = transcript.copy()
            messages.append({
                "role": "user",
                "content": user_input
            })

            # Call Claude
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                temperature=0.7,  # Slightly higher for natural conversation
                system=system_prompt,
                messages=self._format_messages_for_api(messages)
            )

            # Parse JSON response
            response_text = response.content[0].text
            agent_response = json.loads(response_text)

            logger.info(
                "agent_turn_complete",
                business_id=business_id,
                extracted_fields=list(agent_response.get("extracted", {}).keys()),
                is_complete=agent_response.get("is_complete", False),
                should_transfer=agent_response.get("should_transfer_to_human", False)
            )

            return agent_response

        except json.JSONDecodeError as e:
            logger.error(
                "agent_json_parse_failed",
                error=str(e),
                response_text=response_text if 'response_text' in locals() else None
            )
            return self._fallback_response(user_input, session_data, business_config)

        except Exception as e:
            logger.error(
                "agent_turn_failed",
                error=str(e),
                business_id=business_id
            )
            return self._fallback_response(user_input, session_data, business_config)

    def _format_messages_for_api(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Format messages for Anthropic API (alternating user/assistant)."""
        formatted = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            # API expects "user" and "assistant", not "customer" and "agent"
            if role in ["user", "customer"]:
                formatted.append({"role": "user", "content": content})
            elif role in ["assistant", "agent"]:
                formatted.append({"role": "assistant", "content": content})

        return formatted

    def _fallback_response(
        self,
        user_input: str,
        session_data: Dict[str, Any],
        business_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fallback response when Claude is unavailable.

        Uses simple keyword matching (like original state machine fallback).
        """
        logger.info("using_fallback_agent")

        # Simple fallback: ask for first missing field
        required_fields = business_config.get("quote_calculation", {}).get("required_fields", [])

        for field in required_fields:
            if session_data.get(field) is None:
                return {
                    "response": f"Could you provide {field.replace('_', ' ')}?",
                    "extracted": {},
                    "thinking": f"Claude unavailable, asking for {field}",
                    "needs_clarification": [field],
                    "is_complete": False,
                    "should_transfer_to_human": False,
                    "transfer_reason": None
                }

        # All fields collected (somehow)
        return {
            "response": "Let me calculate that for you now.",
            "extracted": {},
            "thinking": "All fields collected via fallback",
            "needs_clarification": [],
            "is_complete": True,
            "should_transfer_to_human": False,
            "transfer_reason": None
        }


# Singleton instance
_agent = None


def get_agent() -> ClaudeAgent:
    """Get singleton Claude agent instance."""
    global _agent
    if _agent is None:
        _agent = ClaudeAgent()
    return _agent


async def claude_agent_turn(
    user_input: str,
    business_id: str = "piano_moving_001",
    business_config: Optional[Dict[str, Any]] = None,
    collected_data: Optional[Dict[str, Any]] = None,
    transcript: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Convenience function for single agent turn.

    Args:
        user_input: What customer just said
        business_id: Which business
        business_config: Business configuration (if None, loads default)
        collected_data: Current session data
        transcript: Conversation history

    Returns:
        Agent response dictionary
    """
    if business_config is None:
        # Load default piano moving config
        import json
        from pathlib import Path
        config_path = Path(__file__).parent.parent / "configs" / "piano_moving.json"
        with open(config_path) as f:
            business_config = json.load(f)

    if collected_data is None:
        collected_data = {
            "piano_type": None,
            "pickup_address": None,
            "delivery_address": None,
            "stairs_count": None,
            "has_insurance": None
        }

    if transcript is None:
        transcript = []

    agent = get_agent()
    return await agent.process_turn(
        user_input=user_input,
        business_id=business_id,
        business_config=business_config,
        session_data=collected_data,
        transcript=transcript
    )
