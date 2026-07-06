"""Hybrid assistant routing service for CityPulse AI."""

from typing import Any

from app.models.assistant import (
    AssistantResponse,
    ConversationMessageResponse,
)
from app.models.intent import IntentDetection
from app.services.conversation_memory import conversation_memory
from app.services.department_routing_service import route_complaint_payload
from app.services.gemini_service import classify_complaint
from app.services.intent_service import detect_intent
from app.services.rag_service import answer_municipal_question


def handle_assistant_message(
    message: str,
    session_id: str | None = None,
) -> AssistantResponse:
    """Route a user message to the correct CityPulse AI capability.

    Args:
        message: Raw user message. It may be either a municipal complaint or a
            municipal knowledge question.
        session_id: Optional conversation session identifier.

    Returns:
        A unified assistant response containing detected intent metadata and
        the routed result.

    Raises:
        ValueError: If the message is empty or intent detection returns an
            invalid result.
        RuntimeError: If the selected downstream capability fails.
    """
    message_text = message.strip()
    if not message_text:
        raise ValueError("message cannot be empty.")

    active_session_id = conversation_memory.get_or_create_session(session_id)
    conversation_memory.add_user_message(active_session_id, message_text)

    intent = detect_intent(message_text)
    result = _route_by_intent(message_text, intent)
    conversation_memory.add_assistant_message(
        session_id=active_session_id,
        content=_summarize_result(result),
        intent=intent.intent,
    )

    return AssistantResponse.from_result(
        intent=intent,
        result=result,
        session_id=active_session_id,
        history=_serialize_history(active_session_id),
    )


def _route_by_intent(
    message: str,
    intent: IntentDetection,
) -> dict[str, Any]:
    """Route a message to the capability selected by intent detection."""
    if intent.intent == "complaint":
        classification = classify_complaint(message)
        routing = route_complaint_payload(classification)
        return {
            **classification,
            "routing": _serialize_model(routing),
        }

    if intent.intent == "question":
        return answer_municipal_question(message)

    raise ValueError(f"Unsupported intent: {intent.intent}")


def _summarize_result(result: dict[str, Any]) -> str:
    """Return a compact text summary suitable for conversation memory."""
    answer = result.get("answer")
    if isinstance(answer, str):
        return answer

    summary = result.get("summary")
    if isinstance(summary, str):
        return summary

    return str(result)


def _serialize_model(model: Any) -> dict[str, Any]:
    """Serialize a Pydantic model across supported Pydantic versions."""
    if hasattr(model, "model_dump"):
        return model.model_dump()

    return model.dict()


def _serialize_history(session_id: str) -> list[ConversationMessageResponse]:
    """Serialize stored conversation history for API responses."""
    return [
        ConversationMessageResponse(
            role=message.role,
            content=message.content,
            timestamp=message.timestamp,
            intent=message.intent,
        )
        for message in conversation_memory.get_history(session_id)
    ]
