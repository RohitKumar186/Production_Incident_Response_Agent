from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ApprovalCreate(BaseModel):
    incident_id: str
    remediation_id: int
    decision: str
    approved_by: Optional[str] = None
    reason: Optional[str] = None


class ApprovalResponse(ApprovalCreate):
    id: int
    decided_at: datetime