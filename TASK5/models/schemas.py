from typing import Any, Optional

from pydantic import BaseModel, Field


class RCAInputIncident(BaseModel):
    """Incident information received from Task 4."""

    incident_id: str
    service: dict[str, Any]
    severity: str
    detected_at: str
    symptom: dict[str, Any]
    environment: str


class RCARootCause(BaseModel):
    """Root cause identified by Task 4."""

    description: str
    category: str
    confidence: float = Field(ge=0.0, le=1.0)


class RCASupportingEvidence(BaseModel):
    """Evidence supporting the Task 4 RCA."""

    finding_id: str
    source: str
    evidence: str
    expected_value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class RCARecommendedAction(BaseModel):
    """Recommended remediation supplied by Task 4."""

    action: str
    action_type: str
    target: str
    risk: str
    requires_human_approval: bool = True


class RCARollbackPlan(BaseModel):
    """Rollback information supplied by Task 4."""

    description: str


class RCAInputPayload(BaseModel):
    """Payload of the Task 4 -> Task 5 Knowledge Card."""

    incident: RCAInputIncident
    root_cause: RCARootCause
    supporting_evidence: list[RCASupportingEvidence]
    rag_context: list[dict[str, Any]] = Field(default_factory=list)
    recommended_action: RCARecommendedAction
    target_version: str
    rollback_plan: RCARollbackPlan


class Task4RCAKnowledgeCard(BaseModel):
    """
    Frozen interface consumed by Task 5.

    Task 5 depends on this contract, not on Task 4's
    internal RAG/RCA implementation.
    """

    schema_version: str = "1.0"
    incident_id: str
    correlation_id: str
    timestamp: str
    producer: str = "rca"
    consumer: str = "remediation"
    status: str
    payload: RCAInputPayload

    def validate_for_remediation(self) -> None:
        """
        Validate that this RCA result is suitable for
        creating a remediation plan.
        """

        if self.schema_version != "1.0":
            raise ValueError(
                "Unsupported Task 4 Knowledge Card schema version"
            )

        if self.status != "SUCCESS":
            raise ValueError(
                "Task 5 can only remediate a successful Task 4 RCA"
            )

        if self.producer != "rca":
            raise ValueError(
                "Invalid producer: expected 'rca'"
            )

        if self.consumer != "remediation":
            raise ValueError(
                "Invalid consumer: expected 'remediation'"
            )

        if self.incident_id != self.payload.incident.incident_id:
            raise ValueError(
                "Top-level incident_id does not match payload incident_id"
            )

        if not self.payload.root_cause.description.strip():
            raise ValueError(
                "Root cause description cannot be empty"
            )

        if not self.payload.root_cause.category.strip():
            raise ValueError(
                "Root cause category cannot be empty"
            )

        if not self.payload.supporting_evidence:
            raise ValueError(
                "Task 4 must provide supporting evidence"
            )

        action = self.payload.recommended_action

        if not action.action.strip():
            raise ValueError(
                "Recommended remediation action cannot be empty"
            )

        if not action.action_type.strip():
            raise ValueError(
                "Recommended action type cannot be empty"
            )

        if not action.target.strip():
            raise ValueError(
                "Remediation target cannot be empty"
            )

        if not action.risk.strip():
            raise ValueError(
                "Remediation risk cannot be empty"
            )

        if not self.payload.rollback_plan.description.strip():
            raise ValueError(
                "Rollback plan cannot be empty"
            )