from enum import Enum
from typing import Optional


class ApprovalDecision(str, Enum):
    """Human decision for a remediation plan."""

    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    STOPPED = "STOPPED"
    REVISION_REQUESTED = "REVISION_REQUESTED"


class ApprovalResult:
    """Result of the human approval step."""

    def __init__(
        self,
        decision: ApprovalDecision,
        feedback: Optional[str] = None,
    ) -> None:
        self.decision = decision
        self.feedback = feedback

    @property
    def approved(self) -> bool:
        """Return True only when the remediation is approved."""

        return self.decision == ApprovalDecision.APPROVED

    @property
    def should_execute(self) -> bool:
        """
        Execution gate.

        Only an explicit APPROVED decision can allow
        remediation execution.
        """

        return self.decision == ApprovalDecision.APPROVED

    def to_dict(self) -> dict:
        """Return the approval result as a serializable dictionary."""

        return {
            "status": self.decision.value,
            "approved": self.approved,
            "feedback": self.feedback,
        }


def request_human_approval(
    decision: ApprovalDecision,
    feedback: Optional[str] = None,
) -> ApprovalResult:
    """
    Record a human decision for a remediation plan.

    This function does not execute remediation.
    It only records the approval decision.
    """

    if (
        decision == ApprovalDecision.REVISION_REQUESTED
        and not feedback
    ):
        raise ValueError(
            "Feedback is required when revision is requested"
        )

    return ApprovalResult(
        decision=decision,
        feedback=feedback,
    )