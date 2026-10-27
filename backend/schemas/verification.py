from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class VerificationCreate(BaseModel):
    incident_id: str
    execution_id: int
    verification_status: str
    service_recovered: bool = False
    verification_details: Dict[str, Any] = Field(default_factory=dict)
    recommended_next_step: str


class VerificationResponse(VerificationCreate):
    id: int
    verified_at: datetime