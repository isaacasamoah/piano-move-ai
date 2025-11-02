"""
Runtime prompt composition for multi-tenant conversational AI platform.

Composes constitutional layer + business config into agent system prompt.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class PromptComposer:
    """Composes agent prompts at runtime from constitutional layer + business config."""

    def __init__(self, constitutional_layer_path: Optional[str] = None):
        """
        Initialize prompt composer.

        Args:
            constitutional_layer_path: Path to constitutional layer markdown file
        """
        if constitutional_layer_path is None:
            constitutional_layer_path = Path(__file__).parent.parent / "configs" / "constitutional_layer.md"

        self.constitutional_layer = self._load_constitutional_layer(constitutional_layer_path)

    def _load_constitutional_layer(self, path: str) -> str:
        """Load constitutional layer from file."""
        with open(path, 'r') as f:
            return f.read()

    def compose_system_prompt(
        self,
        business_config: Dict[str, Any],
        session_data: Dict[str, Any],
        transcript: List[Dict[str, str]]
    ) -> str:
        """
        Compose full system prompt for agent.

        Args:
            business_config: Business-specific configuration (loaded from JSON/database)
            session_data: Current session state (collected fields)
            transcript: Conversation history

        Returns:
            Complete system prompt for Claude
        """

        # Extract business details
        agent_persona = business_config.get("agent_persona", {})
        agent_name = agent_persona.get("name", "AI Assistant")
        company_name = business_config.get("display_name", "Service AI")

        # Get required fields from business config
        required_fields = business_config.get("quote_calculation", {}).get("required_fields", [])

        # Build field descriptions
        field_descriptions = self._build_field_descriptions(business_config)

        # Format current state
        current_state = self._format_current_state(session_data, required_fields)

        # Format transcript
        transcript_text = self._format_transcript(transcript)

        # Compose prompt
        system_prompt = f"""You are {agent_name}, an AI assistant for {company_name}. You're on a phone call with a customer who needs a quote.

## YOUR GOAL
Extract these {len(required_fields)} pieces of information through natural conversation:

{field_descriptions}

When you have all {len(required_fields)} pieces confirmed, end the conversation with "Let me calculate that for you now."

---

## CONSTITUTIONAL PRINCIPLES (CRITICAL - READ CAREFULLY)

### 1. RESPECT CUSTOMER TIME
- Keep each response under 3 sentences (this is a phone call, not a text chat)
- Be efficient and direct
- Extract multiple pieces of information if the customer volunteers them
- Don't waste time with unnecessary pleasantries or repetition

### 2. BUILD TRUST THROUGH TRANSPARENCY
- NEVER assume or guess information
- If anything is ambiguous, ask for clarification
- Confirm critical details (especially addresses, dates, measurements)
- You can say "I don't know" or "Let me check with the team"

### 3. ENABLE BUSINESS SUCCESS
- Gather ACCURATE information for fair quotes
- Represent {company_name} professionally
- Protect business from bad data (vague information leads to wrong quotes)
- Every field must be clear and confirmed

### 4. HUMAN-CENTRIC SERVICE
- If customer asks complex questions → "That's a great question. Let me connect you with our team who can explain that in detail."
- If you can't extract information after 2 attempts → "I'm having trouble understanding. Let me transfer you to someone who can help."
- Customer can always ask to speak to a person
- You facilitate, humans decide

---

## CRITICAL RULES

1. **NEVER ASSUME**
   - Don't fill in missing information
   - Don't use "common sense" to infer data
   - Always ask for clarification when ambiguous

2. **CONFIRM CRITICAL INFORMATION**
   - Read back important details to confirm
   - Especially: addresses, measurements, pricing-sensitive details

3. **STAY IN YOUR LANE**
   You CAN handle: Quote information gathering, basic pricing questions
   You CANNOT handle: Booking/scheduling, complaints, complex policy questions, damage claims
   → If asked something outside your lane: "Let me connect you with our team for that."

4. **BE EFFICIENT, NOT ROBOTIC**
   - Use conversational tone ("Got it", "Perfect", "Great")
   - Mirror customer's language
   - Don't sound like you're reading a script

5. **FAIL GRACEFULLY**
   - If stuck after 2 attempts → offer to transfer to human
   - Don't loop forever on the same question
   - Don't frustrate the customer

---

## CONVERSATION STYLE

**Tone:** Friendly, professional, efficient
**Length:** 1-3 sentences per response
**Approach:** Natural conversation, not interrogation

---

## CURRENT CONVERSATION STATE

**Information collected so far:**
{current_state}

**Conversation history:**
{transcript_text}

---

## YOUR RESPONSE FORMAT

Return ONLY a JSON object with this exact structure:

{{
  "response": "Your natural conversational response to the customer (1-3 sentences)",
  "extracted": {{
    {self._format_extracted_fields(required_fields)}
  }},
  "thinking": "Brief note about what you're doing (internal, not spoken)",
  "needs_clarification": ["field_name"],
  "is_complete": false,
  "should_transfer_to_human": false,
  "transfer_reason": null
}}

**Field explanations:**

- **response**: What you say to the customer next (via TTS)
- **extracted**: Data extracted from customer's latest input (only include fields you extracted THIS turn)
- **thinking**: Your reasoning (helps with debugging, not shown to customer)
- **needs_clarification**: List of fields that are ambiguous and need confirmation
- **is_complete**: Set to `true` only when ALL {len(required_fields)} fields are filled AND confirmed
- **should_transfer_to_human**: Set to `true` if you need to transfer (complex question, stuck, customer request)
- **transfer_reason**: Why you're transferring (if should_transfer_to_human is true)

---

## DOMAIN-SPECIFIC GUIDANCE

{self._build_domain_guidance(business_config)}

---

## FINAL REMINDERS

1. **Be natural** - You're having a conversation, not filling out a form
2. **Be efficient** - Respect customer's time, get to the point
3. **Never assume** - Ask for clarification when needed
4. **Confirm critical info** - Read back important details
5. **Fail gracefully** - Transfer to human if stuck
6. **Stay in your lane** - Quote gathering only, complex questions → human

You're representing {company_name}. Be professional, efficient, and trustworthy.

Now respond to the customer's latest input.
"""

        return system_prompt

    def _build_field_descriptions(self, business_config: Dict[str, Any]) -> str:
        """Build numbered list of fields to extract."""
        required_fields = business_config.get("quote_calculation", {}).get("required_fields", [])

        # Get field metadata from conversation flow states
        states = business_config.get("conversation_flow", {}).get("states", [])

        descriptions = []
        for i, field in enumerate(required_fields, 1):
            # Find corresponding state
            state_config = next((s for s in states if s.get("extraction", {}).get("field") == field), None)

            if state_config:
                extraction = state_config.get("extraction", {})
                field_type = extraction.get("type", "string")
                options = extraction.get("options", [])

                if options:
                    desc = f"{i}. **{field}** ({field_type}: {', '.join(options)})"
                else:
                    desc = f"{i}. **{field}** ({field_type})"

                descriptions.append(desc)
            else:
                descriptions.append(f"{i}. **{field}**")

        return "\n".join(descriptions)

    def _format_current_state(self, session_data: Dict[str, Any], required_fields: List[str]) -> str:
        """Format current session state."""
        lines = []
        for field in required_fields:
            value = session_data.get(field)
            if value is not None:
                lines.append(f"- {field}: ✅ {value}")
            else:
                lines.append(f"- {field}: ❌ NOT YET")

        return "\n".join(lines)

    def _format_transcript(self, transcript: List[Dict[str, str]]) -> str:
        """Format conversation transcript."""
        if not transcript:
            return "(No conversation history yet - this is the start)"

        lines = []
        for turn in transcript[-5:]:  # Last 5 turns for context
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def _format_extracted_fields(self, required_fields: List[str]) -> str:
        """Format extracted fields template for JSON response."""
        lines = []
        for field in required_fields:
            lines.append(f'    "{field}": null')

        return ",\n".join(lines)

    def _build_domain_guidance(self, business_config: Dict[str, Any]) -> str:
        """Build domain-specific guidance section."""
        guidance_parts = []

        # Add business type specific guidance
        business_type = business_config.get("business_type", "")

        if business_type == "piano_moving":
            guidance_parts.append("""**Piano Moving Specifics:**
- Piano types: upright, baby grand, grand
- Addresses: Need full street address including suburb and state
- Stairs: Total count at both pickup and delivery locations
- Insurance: Covers damage during transport (15% of subtotal)
- Distance calculated via geocoding - accurate addresses are critical""")

        elif business_type == "house_cleaning":
            guidance_parts.append("""**House Cleaning Specifics:**
- Property type: apartment, house, townhouse
- Size: Number of bedrooms and bathrooms
- Cleaning type: regular, deep clean, move-out
- Frequency: one-time, weekly, fortnightly, monthly
- Special requirements: Any specific areas or tasks""")

        elif business_type == "junk_removal":
            guidance_parts.append("""**Junk Removal Specifics:**
- Volume: Estimate in cubic meters or truck loads
- Item types: Furniture, appliances, green waste, construction debris
- Access: Can truck access the property? Any stairs?
- Disposal: Landfill, recycling, donation
- Hazardous materials: Must transfer to human""")

        # Add any custom guidance from config
        custom_guidance = business_config.get("agent_guidance", {}).get("custom_notes")
        if custom_guidance:
            guidance_parts.append(f"\n**Additional Notes:**\n{custom_guidance}")

        return "\n\n".join(guidance_parts) if guidance_parts else "No additional domain guidance."


# Singleton instance for easy import
_composer = None


def get_prompt_composer() -> PromptComposer:
    """Get singleton prompt composer instance."""
    global _composer
    if _composer is None:
        _composer = PromptComposer()
    return _composer


def compose_agent_prompt(
    business_id: str,
    business_config: Dict[str, Any],
    session_data: Dict[str, Any],
    transcript: List[Dict[str, str]]
) -> str:
    """
    Convenience function to compose agent prompt.

    Args:
        business_id: Unique business identifier
        business_config: Business configuration (from database/JSON)
        session_data: Current session state
        transcript: Conversation history

    Returns:
        Complete system prompt for Claude
    """
    composer = get_prompt_composer()
    return composer.compose_system_prompt(business_config, session_data, transcript)
