"""Pydantic models for the CityPulse hybrid assistant endpoint."""

from typing import Any

from pydantic import BaseModel, Field

from app.models.intent import IntentDetection, IntentType


class ConversationMessageResponse(BaseModel):
    """Serialized conversation message returned by the assistant endpoint."""

    role: str
    content: str
    timestamp: str
    intent: IntentType | None = None


class AssistantRequest(BaseModel):
    """Request body for the unified CityPulse assistant."""

    message: str = Field(..., min_length=1)
    session_id: str | None = Field(default=None, min_length=1)


class AssistantResponse(BaseModel):
    """Hybrid assistant response with routing metadata and task result."""

    intent: IntentType
    confidence: float
    reason: str
    response_type: IntentType
    result: dict[str, Any]
    session_id: str
    history: list[ConversationMessageResponse]

    @classmethod
    def from_result(
        cls,
        intent: IntentDetection,
        result: dict[str, Any],
        session_id: str,
        history: list[ConversationMessageResponse],
    ) -> "AssistantResponse":
        """Create a response from detected intent and routed result."""
        return cls(
            intent=intent.intent,
            confidence=intent.confidence,
            reason=intent.reason,
            response_type=intent.intent,
            result=result,
            session_id=session_id,
            history=history,
        )
