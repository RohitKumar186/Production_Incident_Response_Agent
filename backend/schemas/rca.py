
from typing import Any, List

from pydantic import BaseModel, Field


class RCACreate(BaseModel):
    incident_id: str
    root_cause: Any
    confidence: float
    contributing_factors: List[Any] = Field(default_factory=list)
    recommended_action: str


class RCAResponse(RCACreate):
    id: int
    status: str