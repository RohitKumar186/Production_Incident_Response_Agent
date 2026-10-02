import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TASK1_ROOT = PROJECT_ROOT / "TASK1"

if str(TASK1_ROOT) not in sys.path:
    sys.path.insert(0, str(TASK1_ROOT))


from TASK1.generator.incident_generator import IncidentGenerator
from TASK1.models.alert import IncidentAlert
from TASK1.models.incident import Incident
from TASK1.simulator.infrastructure import SimulatedInfrastructure

from TASK2.investigator.investigator import Investigator
from TASK2.models.schemas import Evidence as Task2Evidence
from TASK2.models.task4_adapter import Task4Adapter

from TASK3.tools.registry import ToolRegistry

from TASK4.orchestrator.investigation import run_rca

from TASK5.approval.approval import ApprovalDecision

from integration.task4_to_task6 import run_task5_and_task6

from backend.database import SessionLocal
from backend.repository import IncidentRepository


class PIRAPipeline:
    def __init__(self):
        self.infrastructure = SimulatedInfrastructure()
        self.generator = IncidentGenerator(self.infrastructure)
        self.tools = ToolRegistry(self.infrastructure)
        self.investigator = Investigator(self.tools)

        # Runtime cache only.
        #
        # PostgreSQL is the source of truth.
        # This dictionary is allowed to be empty after a backend restart.
        self.incidents: dict[str, dict[str, Any]] = {}

    # ============================================================
    # INCIDENT CREATION + INVESTIGATION + RCA
    # ============================================================

    def generate_and_investigate(self) -> dict:
        incident: Incident = self.generator.generate()

        alert = IncidentAlert.from_incident(incident)

        investigation = self.investigator.investigate(alert)

        task4_input = self._build_task4_input(
            incident=incident,
            investigation=investigation,
        )

        rca = run_rca(task4_input)

        incident_id = incident.incident_id

        self.incidents[incident_id] = {
            "incident": incident,
            "alert": alert,
            "investigation": investigation,
            "task4_input": task4_input,
            "rca": rca,
        }

        db = SessionLocal()

        try:
            repository = IncidentRepository(db)

            db_incident = repository.create_incident(
                incident_id=incident_id,
                incident_type=self._get_incident_type(incident),
                status="RCA_COMPLETE",
                severity=self._get_severity(incident),
                raw_data={
                    "incident": self._serialize(incident),
                    "alert": self._serialize(alert),
                },
            )

            repository.create_investigation(
                incident=db_incident,
                status="COMPLETED",
                findings=self._serialize(investigation),
            )

            raw_evidence = getattr(
                investigation,
                "evidence",
                [],
            )

            for item in raw_evidence:
                repository.create_evidence(
                    incident=db_incident,
                    source=str(
                        item.get(
                            "source",
                            "unknown",
                        )
                    ),
                    evidence_type="INVESTIGATION",
                    content=str(
                        item.get(
                            "data",
                            {},
                        )
                    ),
                    metadata={
                        "component": item.get(
                            "component",
                            self._get_affected_component(
                                incident
                            ),
                        ),
                    },
                )

            rca_data = self._serialize(rca)

            if isinstance(rca_data, dict):
                payload = rca_data.get(
                    "payload",
                    {},
                )

                root_cause = payload.get(
                    "root_cause",
                    {},
                )

                if isinstance(root_cause, dict):
                    root_cause_description = root_cause.get(
                        "description"
                    )
                else:
                    root_cause_description = str(root_cause)

                repository.create_rca(
                    incident=db_incident,
                    root_cause=root_cause_description,
                    category=(
                        root_cause.get("category")
                        if isinstance(root_cause, dict)
                        else None
                    ),
                    confidence=(
                        root_cause.get("confidence")
                        if isinstance(root_cause, dict)
                        else None
                    ),
                    supporting_evidence=payload.get(
                        "supporting_evidence"
                    ),
                    rag_context=payload.get(
                        "rag_context"
                    ),
                    recommended_action=payload.get(
                        "recommended_action"
                    ),
                )

            repository.update_incident_status(
                incident_id=incident_id,
                status="AWAITING_APPROVAL",
            )

        finally:
            db.close()

        return {
            "incident": self._serialize(incident),
            "alert": self._serialize(alert),
            "investigation": self._serialize(investigation),
            "rca": self._serialize(rca),
        }

    # ============================================================
    # TASK 4 INPUT ADAPTER
    # ============================================================

    def _build_task4_input(
        self,
        incident: Incident,
        investigation: Any,
    ) -> Any:
        adapter = Task4Adapter()

        return adapter.convert(
            investigation,
            source_incident=incident,
        )

    # ============================================================
    # APPROVAL + REMEDIATION + VERIFICATION
    # ============================================================

    def remediate(
        self,
        incident_id: str,
        approved: bool,
        feedback: str | None = None,
    ) -> dict:

        # --------------------------------------------------------
        # Load the incident from PostgreSQL.
        #
        # This is intentionally NOT dependent on self.incidents.
        # Therefore approval continues to work after a backend
        # restart.
        # --------------------------------------------------------

        record = self._get_or_restore_record(
            incident_id
        )

        decision = (
            ApprovalDecision.APPROVED
            if approved
            else ApprovalDecision.REJECTED
        )

        # --------------------------------------------------------
        # First database transaction:
        # validate current lifecycle state and persist the
        # approval/rejection transition.
        # --------------------------------------------------------

        db = SessionLocal()

        try:
            repository = IncidentRepository(db)

            db_incident = repository.get_incident(
                incident_id
            )

            if db_incident is None:
                raise KeyError(
                    f"Incident not found: {incident_id}"
                )

            current_status = str(
                db_incident.status
            )

            # Approval is only valid while waiting for approval.
            if approved:
                if current_status != "AWAITING_APPROVAL":
                    raise ValueError(
                        "Incident cannot be approved from "
                        f"current status: {current_status}"
                    )

                repository.update_incident_status(
                    incident_id=incident_id,
                    status="APPROVED",
                )

                repository.update_incident_status(
                    incident_id=incident_id,
                    status="REMEDIATING",
                )

            else:
                if current_status != "AWAITING_APPROVAL":
                    raise ValueError(
                        "Incident cannot be rejected from "
                        f"current status: {current_status}"
                    )

                repository.update_incident_status(
                    incident_id=incident_id,
                    status="REJECTED",
                )

        finally:
            db.close()

        # --------------------------------------------------------
        # Run Task 5 + Task 6.
        #
        # The restored RCA is reconstructed in the same shape
        # expected by the existing Task 5 adapter.
        # --------------------------------------------------------

        results = run_task5_and_task6(
            task4_output=record["rca"],
            decision=decision,
            feedback=feedback,
        )

        task5_result = results["task5"]
        task6_result = results["task6"]

        # Runtime cache.
        record["remediation"] = task6_result

        # --------------------------------------------------------
        # Persist remediation + approval + verification.
        # --------------------------------------------------------

        db = SessionLocal()

        try:
            repository = IncidentRepository(db)

            db_incident = repository.get_incident(
                incident_id
            )

            if db_incident is None:
                raise KeyError(
                    f"Persisted incident not found: {incident_id}"
                )

            task5_payload = task5_result.get(
                "payload",
                {},
            )

            remediation_data = task5_payload.get(
                "remediation",
                {},
            )

            approval_data = task5_payload.get(
                "approval",
                {},
            )

            execution_data = task5_payload.get(
                "execution",
                {},
            )

            approved_at = (
                datetime.now(timezone.utc)
                if approval_data.get("status") == "APPROVED"
                else None
            )

            # ----------------------------------------------------
            # Persist remediation
            # ----------------------------------------------------

            repository.create_remediation(
                incident=db_incident,
                action=remediation_data.get(
                    "action"
                ),
                action_type=remediation_data.get(
                    "action_type"
                ),
                target=remediation_data.get(
                    "target"
                ),
                risk=remediation_data.get(
                    "risk"
                ),
                execution_status=execution_data.get(
                    "status"
                ),
                execution_message=execution_data.get(
                    "message"
                ),
            )

            # ----------------------------------------------------
            # Persist approval
            # ----------------------------------------------------

            repository.create_approval(
                incident=db_incident,
                required=bool(
                    approval_data.get(
                        "required",
                        False,
                    )
                ),
                status=approval_data.get(
                    "status"
                ),
                feedback=approval_data.get(
                    "feedback"
                ),
                approved_at=approved_at,
            )

            # ----------------------------------------------------
            # Rejected path
            # ----------------------------------------------------

            if not approved:
                repository.update_incident_status(
                    incident_id=incident_id,
                    status="REJECTED",
                )

            # ----------------------------------------------------
            # Approved path
            # ----------------------------------------------------

            else:
                repository.update_incident_status(
                    incident_id=incident_id,
                    status="VERIFYING",
                )

                verification = (
                    task6_result
                    .get(
                        "payload",
                        {},
                    )
                    .get(
                        "verification",
                        {},
                    )
                )

                if (
                    verification.get("status")
                    == "SUCCESS"
                    and verification.get(
                        "service_recovered"
                    )
                    is True
                ):
                    repository.update_incident_status(
                        incident_id=incident_id,
                        status="RESOLVED",
                    )

                else:
                    repository.update_incident_status(
                        incident_id=incident_id,
                        status="VERIFICATION_FAILED",
                    )

        finally:
            db.close()

        return task6_result

    # ============================================================
    # DATABASE-BACKED RECORD RESTORATION
    # ============================================================

    def _get_or_restore_record(
        self,
        incident_id: str,
    ) -> dict:
        """
        Return the runtime record if available.

        If the backend was restarted, reconstruct the record from
        PostgreSQL so API operations continue to work.
        """

        if incident_id in self.incidents:
            return self.incidents[incident_id]

        db = SessionLocal()

        try:
            repository = IncidentRepository(db)

            db_incident = repository.get_incident(
                incident_id
            )

            if db_incident is None:
                raise KeyError(
                    f"Incident not found: {incident_id}"
                )

            raw_data = (
                db_incident.raw_data
                if isinstance(
                    db_incident.raw_data,
                    dict,
                )
                else {}
            )

            incident_data = raw_data.get(
                "incident",
                {},
            )

            alert_data = raw_data.get(
                "alert",
                {},
            )

            investigation_model = (
                db_incident.investigation
            )

            investigation_data = (
                investigation_model.findings
                if investigation_model is not None
                else {}
            )

            rca_model = (
                db_incident.rca_result
            )

            if rca_model is None:
                raise KeyError(
                    f"RCA not found for incident: {incident_id}"
                )

            # Reconstruct the Task 4 output contract from the
            # normalized RCA persistence.
            rca_data = self._restore_rca(
                incident_id=incident_id,
                rca_model=rca_model,
            )

            remediation_data = None

            if db_incident.remediation is not None:
                remediation_data = (
                    self._restore_remediation(
                        db_incident.remediation,
                        db_incident.approval,
                        db_incident.verification,
                    )
                )

            record = {
                "incident": incident_data,
                "alert": alert_data,
                "investigation": investigation_data,
                "task4_input": None,
                "rca": rca_data,
                "remediation": remediation_data,
            }

            self.incidents[incident_id] = record

            return record

        finally:
            db.close()

    def _restore_rca(
        self,
        incident_id: str,
        rca_model: Any,
    ) -> dict:
        """
        Rebuild the RCA object in the Task 4 output shape.

        Task 5's existing adapter accepts this dictionary contract.
        """

        root_cause = {
            "description": rca_model.root_cause,
            "category": rca_model.category,
            "confidence": rca_model.confidence,
        }

        return {
            "status": "SUCCESS",
            "producer": "TASK4",
            "schema_version": "1.0",
            "incident_id": incident_id,
            "payload": {
                "root_cause": {
                    "description": rca_model.root_cause,
                    "category": rca_model.category,
                    "confidence": rca_model.confidence,
                },
                "supporting_evidence": rca_model.supporting_evidence or [],
                "rag_context": rca_model.rag_context or [],
                "recommended_action": rca_model.recommended_action,
            },
        }

    def _restore_remediation(
        self,
        remediation_model: Any,
        approval_model: Any,
        verification_model: Any,
    ) -> dict:
        """
        Rebuild the persisted Task 5/6 result shape used by the
        frontend and existing backend read APIs.
        """

        approval_status = (
            approval_model.status
            if approval_model is not None
            else None
        )

        approval_required = (
            bool(
                approval_model.required
            )
            if approval_model is not None
            else False
        )

        approval_feedback = (
            approval_model.feedback
            if approval_model is not None
            else None
        )

        verification = {}

        if verification_model is not None:
            verification = {
                "status": verification_model.status,
                "service_recovered": (
                    verification_model.service_recovered
                ),
                "checks": (
                    verification_model.checks
                    or []
                ),
                "message": verification_model.message,
                "recommended_next_step": (
                    verification_model.recommended_next_step
                ),
            }

        return {
            "status": "SUCCESS",
            "payload": {
                "approval": {
                    "required": approval_required,
                    "status": approval_status,
                    "feedback": approval_feedback,
                },
                "remediation": {
                    "action": remediation_model.action,
                    "action_type": (
                        remediation_model.action_type
                    ),
                    "target": remediation_model.target,
                    "risk": remediation_model.risk,
                },
                "execution": {
                    "status": (
                        remediation_model.execution_status
                    ),
                    "message": (
                        remediation_model.execution_message
                    ),
                },
                "verification": verification,
            },
        }

    # ============================================================
    # READ APIs
    # ============================================================

    def list_incidents(self) -> list[dict]:
        """
        Read incident summaries directly from PostgreSQL.

        This guarantees that the frontend still sees incidents
        after a backend restart.
        """

        db = SessionLocal()

        try:
            repository = IncidentRepository(db)

            db_incidents = repository.list_incidents()

            results = []

            for db_incident in db_incidents:
                raw_data = (
                    db_incident.raw_data
                    if isinstance(
                        db_incident.raw_data,
                        dict,
                    )
                    else {}
                )

                incident_data = raw_data.get(
                    "incident",
                    {},
                )

                rca_model = (
                    db_incident.rca_result
                )

                root_cause = None

                if rca_model is not None:
                    root_cause = (
                        rca_model.root_cause
                    )

                results.append(
                    {
                        "incident_id": (
                            db_incident.incident_id
                        ),
                        "timestamp": (
                            incident_data.get(
                                "detected_at"
                            )
                            or incident_data.get(
                                "timestamp"
                            )
                            or (
                                db_incident.created_at.isoformat()
                                if db_incident.created_at
                                else ""
                            )
                        ),
                        "incident_type": (
                            db_incident.type
                        ),
                        "affected_component": (
                            incident_data.get(
                                "affected_component"
                            )
                            or incident_data.get(
                                "service_name"
                            )
                            or "unknown"
                        ),
                        "severity": (
                            db_incident.severity
                        ),
                        "status": (
                            db_incident.status
                        ),
                        "root_cause": root_cause,
                    }
                )

            return results

        finally:
            db.close()

    def get_incident(
        self,
        incident_id: str,
    ) -> dict:

        record = self._get_or_restore_record(
            incident_id
        )

        db = SessionLocal()

        try:
            repository = IncidentRepository(db)

            db_incident = repository.get_incident(
                incident_id
            )

            if db_incident is None:
                raise KeyError(
                    f"Incident not found: {incident_id}"
                )

            incident_data = self._serialize(
                record["incident"]
            )

            incident_data["status"] = db_incident.status

            return {
                "incident": incident_data,
                "alert": self._serialize(
                    record["alert"]
                ),
                "investigation": self._serialize(
                    record["investigation"]
                ),
                "rca": self._serialize(
                    record["rca"]
                ),
                "remediation": self._serialize(
                    record.get("remediation")
                ),
            }

        finally:
            db.close()

    def get_investigation(
        self,
        incident_id: str,
    ) -> dict:

        record = self._get_or_restore_record(
            incident_id
        )

        return self._serialize(
            record["investigation"]
        )

    def get_evidence(
        self,
        incident_id: str,
    ) -> list:

        db = SessionLocal()

        try:
            repository = IncidentRepository(db)

            db_incident = repository.get_incident(
                incident_id
            )

            if db_incident is None:
                raise KeyError(
                    f"Incident not found: {incident_id}"
                )

            return [
                {
                    "id": item.id,
                    "source": item.source,
                    "type": item.type,
                    "content": item.content,
                    "metadata": item.metadata_json,
                }
                for item in db_incident.evidence
            ]

        finally:
            db.close()

    def get_rca(
        self,
        incident_id: str,
    ) -> dict:

        record = self._get_or_restore_record(
            incident_id
        )

        return self._serialize(
            record["rca"]
        )

    def get_remediation(
        self,
        incident_id: str,
    ) -> dict:

        record = self._get_or_restore_record(
            incident_id
        )

        remediation = record.get(
            "remediation"
        )

        if remediation is None:
            return {
                "status": "PENDING",
                "message": (
                    "Remediation has not been "
                    "executed yet."
                ),
            }

        return self._serialize(
            remediation
        )

    def get_verification(
        self,
        incident_id: str,
    ) -> dict:

        record = self._get_or_restore_record(
            incident_id
        )

        remediation = record.get(
            "remediation"
        )

        if remediation is None:
            return {
                "status": "PENDING",
                "message": (
                    "Verification is not available "
                    "until remediation is executed."
                ),
            }

        remediation_data = self._serialize(
            remediation
        )

        if isinstance(
            remediation_data,
            dict,
        ):
            payload = remediation_data.get(
                "payload",
                {},
            )

            return payload.get(
                "verification",
                {
                    "status": "PENDING",
                    "message": (
                        "Verification result not available."
                    ),
                },
            )

        return {
            "status": "PENDING",
            "message": (
                "Verification result not available."
            ),
        }

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def _serialize(
        self,
        value: Any,
    ) -> Any:

        if value is None:
            return None

        if isinstance(
            value,
            (
                str,
                int,
                float,
                bool,
            ),
        ):
            return value

        if isinstance(value, datetime):
            return value.isoformat()

        if hasattr(
            value,
            "model_dump",
        ):
            return self._serialize(
                value.model_dump()
            )

        if hasattr(
            value,
            "to_dict",
        ):
            return self._serialize(
                value.to_dict()
            )

        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): self._serialize(item)
                for key, item in value.items()
            }

        if isinstance(
            value,
            (list, tuple),
        ):
            return [
                self._serialize(item)
                for item in value
            ]

        if hasattr(
            value,
            "__dict__",
        ):
            return {
                key: self._serialize(item)
                for key, item in value.__dict__.items()
                if not key.startswith("_")
            }

        return value

    # ============================================================
    # INCIDENT HELPERS
    # ============================================================

    def _get_incident_timestamp(
        self,
        incident: Any,
    ) -> str:

        if incident is None:
            return ""

        if isinstance(
            incident,
            dict,
        ):
            for field in (
                "timestamp",
                "detected_at",
                "created_at",
            ):
                value = incident.get(field)

                if value is not None:
                    return str(value)

            return ""

        for field in (
            "timestamp",
            "detected_at",
            "created_at",
        ):
            value = getattr(
                incident,
                field,
                None,
            )

            if value is not None:
                return str(value)

        return ""

    def _get_incident_type(
        self,
        incident: Any,
    ) -> str:

        if isinstance(
            incident,
            dict,
        ):
            value = incident.get(
                "incident_type"
            )
        else:
            value = getattr(
                incident,
                "incident_type",
                None,
            )

        if value is not None:
            return str(value)

        return "UNKNOWN"

    def _get_affected_component(
        self,
        incident: Any,
    ) -> str:

        if isinstance(
            incident,
            dict,
        ):
            value = (
                incident.get(
                    "affected_component"
                )
                or incident.get(
                    "service_name"
                )
            )
        else:
            value = getattr(
                incident,
                "affected_component",
                None,
            )

        if value is not None:
            return str(value)

        return "unknown"

    def _get_severity(
        self,
        incident: Any,
    ) -> str:

        if isinstance(
            incident,
            dict,
        ):
            value = incident.get(
                "severity"
            )
        else:
            value = getattr(
                incident,
                "severity",
                None,
            )

        if value is not None:
            return str(value)

        return "UNKNOWN"


pipeline = PIRAPipeline()