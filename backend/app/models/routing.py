"""Pydantic models for department routing decisions."""

from pydantic import BaseModel, Field


class DepartmentRoute(BaseModel):
    """Routing decision for a classified municipal complaint."""

    department: str
    priority: str
    sla: str
    officer: str
    escalation_required: bool
    escalation_level: str
    reason: str = Field(..., min_length=1)
