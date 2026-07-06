"""Pydantic models for municipal knowledge RAG endpoints."""

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request body for municipal knowledge questions."""

    question: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    """Grounded municipal knowledge answer with source filenames."""

    answer: str
    sources: list[str]
