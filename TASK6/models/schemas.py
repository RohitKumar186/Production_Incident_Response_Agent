from typing import Any, Optional

from pydantic import BaseModel, Field


class RemediationInput(BaseModel):
    action: str
    action_type: str
    target: str
    risk: str


class ApprovalInput(BaseModel):
    required: bool
    status: str
    feedback: Optional[str] = None


class ExecutionInput(BaseModel):
    status: str
    message: str


class RollbackInput(BaseModel):
    description: str


class Task5RemediationPayload(BaseModel):
    remediation: RemediationInput
    approval: ApprovalInput
    execution: ExecutionInput
    rollback_plan: RollbackInput


class Task5RemediationOutput(BaseModel):
    schema_version: str
    incident_id: str
    correlation_id: str
    timestamp: str
    producer: str
    consumer: str
    status: str
    payload: Task5RemediationPayload


class VerificationResult(BaseModel):
    status: str
    service_recovered: bool
    checks: dict[str, Any] = Field(default_factory=dict)
    message: str
    recommended_next_step: str