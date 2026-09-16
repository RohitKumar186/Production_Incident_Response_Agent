"""
Command-line human approval interface for Task 5.

This module presents a remediation plan to a human and records
the approval decision. It does not execute remediation itself.
"""

from TASK5.approval.approval import (
    ApprovalDecision,
    ApprovalResult,
    request_human_approval,
)
from TASK5.planner.planner import RemediationPlan


def display_remediation_plan(plan: RemediationPlan) -> None:
    """Display the proposed remediation plan."""

    print("\n" + "=" * 60)
    print("TASK 5 - REMEDIATION APPROVAL")
    print("=" * 60)

    print(f"Incident ID       : {plan.incident_id}")
    print(f"Correlation ID    : {plan.correlation_id}")
    print(f"Action            : {plan.action}")
    print(f"Action Type       : {plan.action_type}")
    print(f"Target            : {plan.target}")
    print(f"Risk              : {plan.risk}")
    print(f"Target Version    : {plan.target_version}")
    print(f"Human Approval    : {plan.requires_human_approval}")

    print("\nRollback Plan:")
    print(f"  {plan.rollback_description}")

    print("=" * 60)


def request_approval_from_human(
    plan: RemediationPlan,
) -> ApprovalResult:
    """
    Ask the human to approve, reject, stop, or request revision.

    This function only records the decision. It never executes
    the remediation.
    """

    display_remediation_plan(plan)

    print("\nChoose an action:")
    print("  1. APPROVE")
    print("  2. REJECT")
    print("  3. STOP")
    print("  4. REQUEST REVISION")

    while True:
        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            return request_human_approval(
                ApprovalDecision.APPROVED
            )

        if choice == "2":
            return request_human_approval(
                ApprovalDecision.REJECTED
            )

        if choice == "3":
            return request_human_approval(
                ApprovalDecision.STOPPED
            )

        if choice == "4":
            feedback = input(
                "Enter revision feedback: "
            ).strip()

            if not feedback:
                print(
                    "Revision feedback is required. "
                    "Please try again."
                )
                continue

            return request_human_approval(
                ApprovalDecision.REVISION_REQUESTED,
                feedback=feedback,
            )

        print("Invalid choice. Please enter 1, 2, 3, or 4.")