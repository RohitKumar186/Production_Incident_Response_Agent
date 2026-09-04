from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class InvestigationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class Evidence(BaseModel):
    source: str
    reference: str
    details: str


class Incident(BaseModel):
    incident_id: str
    service_name: str
    service_version: str
    severity: Severity
    detected_at: datetime
    symptom: str
    baseline_latency_ms: float
    current_latency_ms: float
    increase_percent: float
    environment: str


class Finding(BaseModel):
    finding_id: str
    agent: str
    category: str
    finding: str
    value: str
    expected_value: str
    evidence: list[Evidence]
    confidence: float = Field(ge=0.0, le=1.0)
    severity: Severity


class AgentError(BaseModel):
    code: str
    message: str
    retryable: bool


class AgentResult(BaseModel):
    agent: str
    status: InvestigationStatus
    error: AgentError | None = None
    findings: list[Finding] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class InvestigationPayload(BaseModel):
    incident: Incident
    findings: list[Finding]
    overall_confidence: float = Field(ge=0.0, le=1.0)


class KnowledgeCard(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    schema_version: str = "1.0"
    incident_id: str
    correlation_id: str
    timestamp: datetime
    producer: str = "investigation"
    consumer: str = "rca"
    status: InvestigationStatus
    payload: InvestigationPayload

    @field_validator("schema_version")
    @classmethod
    def supported_schema(cls, value: str) -> str:
        if value != "1.0":
            raise ValueError("Only knowledge card schema version 1.0 is supported")
        return value