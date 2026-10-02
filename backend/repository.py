from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import (
    Evidence,
    Incident,
    Investigation,
    RCAResult,
    Remediation,
    Approval,
)


class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # INCIDENT
    # ============================================================

    def create_incident(
        self,
        incident_id: str,
        incident_type: str | None,
        status: str | None,
        severity: str | None,
        raw_data: dict[str, Any] | None,
    ) -> Incident:

        incident = Incident(
            incident_id=incident_id,
            type=incident_type,
            status=status,
            severity=severity,
            raw_data=raw_data,
        )

        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        return incident

    def get_incident(
        self,
        incident_id: str,
    ) -> Incident | None:

        statement = select(Incident).where(
            Incident.incident_id == incident_id
        )

        return self.db.scalar(statement)

    def list_incidents(self) -> list[Incident]:

        statement = select(Incident).order_by(
            Incident.created_at.desc()
        )

        return list(
            self.db.scalars(statement).all()
        )

    def update_incident_status(
        self,
        incident_id: str,
        status: str,
    ) -> Incident:

        incident = self.get_incident(
            incident_id
        )

        if incident is None:
            raise KeyError(
                f"Incident not found: {incident_id}"
            )

        incident.status = status

        self.db.commit()
        self.db.refresh(incident)

        return incident

    # ============================================================
    # INVESTIGATION
    # ============================================================

    def create_investigation(
        self,
        incident: Incident,
        status: str,
        findings: dict[str, Any] | list[Any] | None,
    ) -> Investigation:

        investigation = Investigation(
            incident_id=incident.id,
            status=status,
            findings=findings,
        )

        self.db.add(investigation)
        self.db.commit()
        self.db.refresh(investigation)

        return investigation

    # ============================================================
    # EVIDENCE
    # ============================================================

    def create_evidence(
        self,
        incident: Incident,
        source: str | None,
        evidence_type: str | None,
        content: str | None,
        metadata: dict[str, Any] | None,
    ) -> Evidence:

        evidence = Evidence(
            incident_id=incident.id,
            source=source,
            type=evidence_type,
            content=content,
            metadata_json=metadata,
        )

        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)

        return evidence

    # ============================================================
    # RCA
    # ============================================================

    def create_rca(
        self,
        incident: Incident,
        root_cause: str | None,
        category: str | None,
        confidence: float | None,
        supporting_evidence: (
            dict[str, Any]
            | list[Any]
            | None
        ),
        rag_context: (
            dict[str, Any]
            | list[Any]
            | None
        ),
        recommended_action: (
            dict[str, Any]
            | str
            | None
        ),
    ) -> RCAResult:

        rca = RCAResult(
            incident_id=incident.id,
            root_cause=root_cause,
            category=category,
            confidence=confidence,
            supporting_evidence=supporting_evidence,
            rag_context=rag_context,
            recommended_action=recommended_action,
        )

        self.db.add(rca)
        self.db.commit()
        self.db.refresh(rca)

        return rca

    # ============================================================
    # REMEDIATION
    # ============================================================

    def create_remediation(
        self,
        incident: Incident,
        action: str | None,
        action_type: str | None,
        target: str | None,
        risk: str | None,
        execution_status: str | None,
        execution_message: str | None,
    ) -> Remediation:

        remediation = Remediation(
            incident_id=incident.id,
            action=action,
            action_type=action_type,
            target=target,
            risk=risk,
            execution_status=execution_status,
            execution_message=execution_message,
        )

        self.db.add(remediation)
        self.db.commit()
        self.db.refresh(remediation)

        return remediation

    # ============================================================
    # APPROVAL
    # ============================================================

    def create_approval(
        self,
        incident: Incident,
        required: bool,
        status: str | None,
        feedback: str | None,
        approved_at: Any = None,
    ) -> Approval:

        approval = Approval(
            incident_id=incident.id,
            required=required,
            status=status,
            feedback=feedback,
            approved_at=approved_at,
        )

        self.db.add(approval)
        self.db.commit()
        self.db.refresh(approval)

        return approval