from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class IncidentCreate(BaseModel):
    incident_id: str
    incident_type: str
    severity: str
    affected_service: str
    title: str
    description: Optional[str] = None
    detected_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IncidentResponse(IncidentCreate):
    status: str = "OPEN"