from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class RemediationCreate(BaseModel):
    incident_id: str
    action: str
    rationale: Optional[str] = None
    risk_level: str = "MEDIUM"
    proposed_by: str = "remediation-agent"


class RemediationResponse(RemediationCreate):
    id: int
    approval_status: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    execution_status: str
    execution_result: Dict[str, Any] = Field(default_factory=dict)