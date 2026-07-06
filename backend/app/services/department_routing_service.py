"""Department routing service for classified municipal complaints."""

from app.models.classification import ComplaintClassification
from app.models.routing import DepartmentRoute


CATEGORY_DEPARTMENT_MAP = {
    "Road Damage": "Road Maintenance",
    "Garbage": "Sanitation",
    "Water Leakage": "Water Supply",
    "Illegal Parking": "Traffic Police",
    "Pollution": "Pollution Control",
    "Street Light": "Electrical",
    "Traffic": "Traffic Police",
    "Public Safety": "Public Works",
    "Other": "Public Works",
}

DEPARTMENT_OFFICER_MAP = {
    "Road Maintenance": "Road Maintenance Duty Officer",
    "Sanitation": "Sanitation Duty Officer",
    "Water Supply": "Water Supply Duty Officer",
    "Traffic Police": "Traffic Control Duty Officer",
    "Pollution Control": "Pollution Control Duty Officer",
    "Electrical": "Electrical Maintenance Duty Officer",
    "Public Works": "Public Works Duty Officer",
}

PRIORITY_LABELS = {
    1: "Critical",
    2: "High",
    3: "Medium",
    4: "Low",
}

PRIORITY_SLA_MAP = {
    1: "4 hours",
    2: "12 hours",
    3: "48 hours",
    4: "96 hours",
}

SEVERITY_PRIORITY_FLOOR = {
    "Critical": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4,
}


def route_complaint(
    complaint: ComplaintClassification,
) -> DepartmentRoute:
    """Route a classified complaint to the right department and officer.

    Args:
        complaint: Structured complaint classification produced by the
            complaint classification agent.

    Returns:
        A department routing decision containing department, priority, SLA,
        officer assignment, and escalation metadata.

    Raises:
        ValueError: If complaint fields required for routing are invalid.
    """
    _validate_complaint(complaint)

    priority = _resolve_priority(complaint)
    department = _resolve_department(complaint)
    escalation_required = _requires_escalation(complaint, priority)

    return DepartmentRoute(
        department=department,
        priority=PRIORITY_LABELS[priority],
        sla=PRIORITY_SLA_MAP[priority],
        officer=_resolve_officer(department, escalation_required),
        escalation_required=escalation_required,
        escalation_level=_resolve_escalation_level(
            escalation_required=escalation_required,
            priority=priority,
        ),
        reason=_build_reason(
            complaint=complaint,
            department=department,
            priority=priority,
        ),
    )


def route_complaint_payload(payload: dict) -> DepartmentRoute:
    """Route a complaint classification dictionary.

    Args:
        payload: Dictionary matching ``ComplaintClassification`` fields.

    Returns:
        A validated department routing decision.
    """
    return route_complaint(ComplaintClassification(**payload))


def _validate_complaint(complaint: ComplaintClassification) -> None:
    """Validate fields required for department routing."""
    if not complaint.category.strip():
        raise ValueError("category is required for department routing.")

    if not complaint.department.strip():
        raise ValueError("department is required for department routing.")

    if complaint.priority not in PRIORITY_LABELS:
        raise ValueError("priority must be an integer between 1 and 4.")

    if not complaint.severity.strip():
        raise ValueError("severity is required for department routing.")


def _resolve_department(complaint: ComplaintClassification) -> str:
    """Resolve the owning department using category mapping first."""
    mapped_department = CATEGORY_DEPARTMENT_MAP.get(complaint.category)
    if mapped_department:
        return mapped_department

    return complaint.department


def _resolve_priority(complaint: ComplaintClassification) -> int:
    """Resolve final routing priority from classifier priority and severity."""
    severity_priority = SEVERITY_PRIORITY_FLOOR.get(complaint.severity)
    if severity_priority is None:
        return complaint.priority

    return min(complaint.priority, severity_priority)


def _requires_escalation(
    complaint: ComplaintClassification,
    priority: int,
) -> bool:
    """Return whether a complaint needs escalation."""
    return priority == 1 or complaint.severity == "Critical"


def _resolve_officer(
    department: str,
    escalation_required: bool,
) -> str:
    """Assign the correct duty officer for the routing decision."""
    if escalation_required:
        return "Municipal Incident Commander"

    return DEPARTMENT_OFFICER_MAP.get(department, "Public Works Duty Officer")


def _resolve_escalation_level(
    escalation_required: bool,
    priority: int,
) -> str:
    """Return an escalation level label."""
    if escalation_required:
        return "department_head"

    if priority == 2:
        return "supervisor"

    return "standard"


def _build_reason(
    complaint: ComplaintClassification,
    department: str,
    priority: int,
) -> str:
    """Build a concise human-readable routing reason."""
    location = complaint.location or "Unknown location"
    return (
        f"{complaint.category} complaint at {location} routed to "
        f"{department} with {PRIORITY_LABELS[priority].lower()} priority."
    )
