"""Intent detection service for the CityPulse hybrid AI agent."""

import json

from pydantic import ValidationError

from app.models.intent import IntentDetection
from app.services.gemini_service import ask_gemini


def detect_intent(message: str) -> IntentDetection:
    """Classify a user message as a complaint or knowledge question.

    Args:
        message: Raw user message from a citizen or municipal staff member.

    Returns:
        A validated intent detection result containing intent, confidence, and
        reasoning.

    Raises:
        ValueError: If the message is empty, Gemini returns invalid JSON, or
            the JSON does not match the required schema.
    """
    message_text = message.strip()
    if not message_text:
        raise ValueError("message cannot be empty.")

    response_text = ask_gemini(_build_intent_prompt(message_text))

    try:
        payload = json.loads(response_text)
        return IntentDetection(**payload)
    except json.JSONDecodeError as exc:
        raise ValueError("Gemini returned invalid JSON for intent detection.") from exc
    except ValidationError as exc:
        raise ValueError(
            "Gemini returned an invalid intent detection schema."
        ) from exc


def _build_intent_prompt(message: str) -> str:
    """Build a strict JSON prompt for intent classification."""
    return f"""
You are the Intent Detection Agent for CityPulse AI.

Classify the user's message into exactly one intent:

1. "complaint"
   Use this when the user reports a civic issue, incident, hazard, outage,
   damaged public asset, missed service, or requests municipal action.

2. "question"
   Use this when the user asks for municipal information, schedules, policy,
   eligibility, department guidance, rules, or general knowledge.

Return ONLY valid JSON with this exact schema:

{{
  "intent": "complaint",
  "confidence": 0.0,
  "reason": ""
}}

Rules:
- The "intent" value must be exactly "complaint" or "question".
- The "confidence" value must be a number between 0.0 and 1.0.
- The "reason" must be one short sentence.
- Do not include markdown.
- Do not include extra keys.
- Do not include explanations outside JSON.

Examples:

User message: "There is a pothole near MG Road causing accidents."
JSON:
{{
  "intent": "complaint",
  "confidence": 0.95,
  "reason": "The user is reporting a road hazard that needs municipal action."
}}

User message: "When is garbage collected in Ward 12?"
JSON:
{{
  "intent": "question",
  "confidence": 0.95,
  "reason": "The user is asking for municipal service schedule information."
}}

User message:
{message}
"""
