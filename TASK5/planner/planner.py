from datetime import datetime, timezone

from TASK5.models.schemas import Task4RCAKnowledgeCard


class RemediationPlan:
    """Represents a remediation plan prepared from a Task 4 RCA."""

    def __init__(
        self,
        incident_id: str,
        correlation_id: str,
        action: str,
        action_type: str,
        target: str,
        risk: str,
        target_version: str,
        rollback_description: str,
        requires_human_approval: bool,
    ) -> None:
        self.incident_id = incident_id
        self.correlation_id = correlation_id
        self.action = action
        self.action_type = action_type
        self.target = target
        self.risk = risk
        self.target_version = target_version
        self.rollback_description = rollback_description
        self.requires_human_approval = requires_human_approval
        self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """Return the plan as a serializable dictionary."""

        return {
            "incident_id": self.incident_id,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at,
            "action": self.action,
            "action_type": self.action_type,
            "target": self.target,
            "risk": self.risk,
            "target_version": self.target_version,
            "rollback_plan": {
                "description": self.rollback_description
            },
            "requires_human_approval": self.requires_human_approval,
        }


def create_remediation_plan(
    rca_card: Task4RCAKnowledgeCard,
) -> RemediationPlan:
    """
    Convert a validated Task 4 RCA Knowledge Card into
    a Task 5 remediation plan.

    This function plans the remediation only.
    It does not execute any change.
    """

    rca_card.validate_for_remediation()

    recommended_action = rca_card.payload.recommended_action

    return RemediationPlan(
        incident_id=rca_card.incident_id,
        correlation_id=rca_card.correlation_id,
        action=recommended_action.action,
        action_type=recommended_action.action_type,
        target=recommended_action.target,
        risk=recommended_action.risk,
        target_version=rca_card.payload.target_version,
        rollback_description=(
            rca_card.payload.rollback_plan.description
        ),
        requires_human_approval=(
            recommended_action.requires_human_approval
        ),
    )