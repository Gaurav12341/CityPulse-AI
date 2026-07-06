from pydantic import BaseModel

class ComplaintClassification(BaseModel):
    category: str
    department: str
    severity: str
    priority: int
    location: str
    summary: str

    ward: str
    estimated_resolution_hours: int
    citizen_impact: str
    recommended_action: str