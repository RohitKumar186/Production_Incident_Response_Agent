from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Evidence(BaseModel):
    source: str
    reference: str
    details: Optional[str] = None


class Finding(BaseModel):
    finding_id: str
    agent: str
    category: str
    finding: str
    value: str
    expected_value: Optional[str] = None
    evidence: List[Evidence]
    confidence: float = Field(ge=0.0, le=1.0)
    severity: str


class AgentError(BaseModel):
    code: str
    message: str


class AgentResult(BaseModel):
    agent: str
    status: str
    findings: List[Finding] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    error: Optional[AgentError] = None


class Incident(BaseModel):
    incident_id: str
    service: Dict[str, Any]
    severity: str
    detected_at: str
    symptom: Dict[str, Any]
    environment: str


class InvestigationPayload(BaseModel):
    incident: Incident
    findings: List[Finding]
    overall_confidence: float = Field(ge=0.0, le=1.0)


class InvestigationOutput(BaseModel):
    schema_version: str
    incident_id: str
    correlation_id: str
    timestamp: str
    producer: str
    consumer: str
    status: str
    payload: InvestigationPayload