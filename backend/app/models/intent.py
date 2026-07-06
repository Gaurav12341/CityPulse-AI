"""Pydantic models for hybrid-agent intent detection."""

from typing import Literal

from pydantic import BaseModel, Field


IntentType = Literal["complaint", "question"]


class IntentDetection(BaseModel):
    """Detected user intent for routing through the hybrid AI agent."""

    intent: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., min_length=1)
