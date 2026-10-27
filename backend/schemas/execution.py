from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ExecutionCreate(BaseModel):
    incident_id: str
    remediation_id: int
    execution_status: str
    execution_result: Dict[str, Any] = Field(default_factory=dict)
    executed_by: Optional[str] = None


class ExecutionResponse(ExecutionCreate):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None