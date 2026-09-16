"""
Interactive demonstration of Task 4 -> Task 5 remediation.

This demo uses Task 4's existing RCA scenario and lets a human
choose the remediation approval decision.
"""

from TASK4.tests.test_task4 import run_scenario

from TASK5.approval.approval import ApprovalDecision
from TASK5.approval.cli import request_approval_from_human
from TASK5.orchestrator.task4_adapter import convert_task4_output
from TASK5.planner.planner import create_remediation_plan
from TASK5.orchestrator.remediation import run_remediation


def main() -> None:
    """Run the Task 4 -> Task 5 interactive demonstration."""

    print("\n" + "=" * 70)
    print("PIRA - TASK 4 → TASK 5 REMEDIATION DEMO")
    print("=" * 70)

    # -------------------------------------------------
    # TASK 4
    # -------------------------------------------------

    print("\n[1] Running Task 4 RCA...")

    task4_output = run_scenario("database")

    print("\nTask 4 RCA completed.")
    print(f"Incident       : {task4_output.incident_id}")
    print(f"Correlation ID : {task4_output.correlation_id}")
    print(f"Status         : {task4_output.status}")

    # -------------------------------------------------
    # TASK 4 → TASK 5
    # -------------------------------------------------

    print("\n[2] Converting Task 4 output to Task 5 Knowledge Card...")

    rca_card = convert_task4_output(task4_output)

    print("Knowledge Card validated successfully.")

    # -------------------------------------------------
    # TASK 5 PLANNING
    # -------------------------------------------------

    print("\n[3] Creating remediation plan...")

    plan = create_remediation_plan(rca_card)

    # -------------------------------------------------
    # HUMAN APPROVAL
    # -------------------------------------------------

    approval = request_approval_from_human(plan)

    # -------------------------------------------------
    # TASK 5 EXECUTION
    # -------------------------------------------------

    print("\n[4] Processing Task 5 decision...")

    result = run_remediation(
        rca_card=rca_card,
        decision=approval.decision,
        feedback=approval.feedback,
    )

    output = result.to_dict()

    # -------------------------------------------------
    # RESULT
    # -------------------------------------------------

    print("\n" + "=" * 70)
    print("TASK 5 RESULT")
    print("=" * 70)

    print(f"Incident       : {output['incident_id']}")
    print(f"Status         : {output['status']}")
    print(
        "Approval       : "
        f"{output['payload']['approval']['status']}"
    )
    print(
        "Execution      : "
        f"{output['payload']['execution']['status']}"
    )
    print(
        "Message        : "
        f"{output['payload']['execution']['message']}"
    )

    print("\nTask 6-compatible output:")
    print(output)

    print("=" * 70)


if __name__ == "__main__":
    main()