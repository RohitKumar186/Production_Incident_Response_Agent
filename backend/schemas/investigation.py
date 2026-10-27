from typing import Any, Dict, List

from pydantic import BaseModel, Field


class InvestigationCreate(BaseModel):
    incident_id: str
    investigator: str = "investigation-agent"
    summary: str
    findings: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[Any] = Field(default_factory=list)


class InvestigationResponse(InvestigationCreate):
    id: int
    status: str