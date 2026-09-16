from datetime import datetime, timezone
from typing import Optional

from TASK5.approval.approval import (
    ApprovalDecision,
    request_human_approval,
)
from TASK5.execution.simulator import SimulatedEnvironment
from TASK5.models.schemas import Task4RCAKnowledgeCard
from TASK5.planner.planner import create_remediation_plan


class RemediationResult:
    def __init__(self, incident_id, correlation_id, plan, approval, execution):
        self.incident_id = incident_id
        self.correlation_id = correlation_id
        self.plan = plan
        self.approval = approval
        self.execution = execution
        self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def status(self):
        if self.approval.decision == ApprovalDecision.APPROVED:
            if self.execution.get("status") == "SUCCESS":
                return "SUCCESS"
            return "FAILED"

        return "PARTIAL"

    def to_dict(self):
        return {
            "schema_version": "1.0",
            "incident_id": self.incident_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "producer": "remediation",
            "consumer": "verification",
            "status": self.status,
            "payload": {
                "remediation": {
                    "action": self.plan.action,
                    "action_type": self.plan.action_type,
                    "target": self.plan.target,
                    "risk": self.plan.risk,
                },
                "approval": {
                    "required": self.plan.requires_human_approval,
                    "status": self.approval.decision.value,
                    "feedback": self.approval.feedback,
                },
                "execution": {
                    "status": self.execution.get("status"),
                    "message": self.execution.get("message"),
                },
                "rollback_plan": {
                    "description": self.plan.rollback_description,
                },
            },
        }


def run_remediation(
    rca_card: Task4RCAKnowledgeCard,
    decision,
    feedback: Optional[str] = None,
    environment=None,
):
    plan = create_remediation_plan(rca_card)

    approval = request_human_approval(
        decision=decision,
        feedback=feedback,
    )

    if environment is None:
        environment = SimulatedEnvironment()

    # Safety gate:
    # only APPROVED remediation is allowed to reach execution.
    if approval.decision != ApprovalDecision.APPROVED:
        execution = {
            "status": "NOT_EXECUTED",
            "message": (
                "Remediation was not executed because "
                f"approval status was {approval.decision.value}"
            ),
        }
    else:
        execution = environment.execute(
            plan=plan,
            approval=approval,
        )

    return RemediationResult(
        incident_id=rca_card.incident_id,
        correlation_id=rca_card.correlation_id,
        plan=plan,
        approval=approval,
        execution=execution,
    )