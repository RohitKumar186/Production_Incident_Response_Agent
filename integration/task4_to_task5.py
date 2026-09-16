"""
Integration between Task 4 RCA and Task 5 Remediation.

This module connects the two tasks through the agreed
Task 4 -> Task 5 Knowledge Card contract.
"""

from typing import Any, Optional

from TASK5 import (
    ApprovalDecision,
    convert_task4_output,
    run_remediation,
)


def run_task4_to_task5(
    task4_output: Any,
    decision: ApprovalDecision,
    feedback: Optional[str] = None,
) -> dict:
    """
    Pass Task 4 RCA output through Task 5 remediation.

    Flow:

        Task 4 RCAOutput
            ↓
        Knowledge Card validation
            ↓
        Task 5 remediation plan
            ↓
        Human approval
            ↓
        Controlled remediation
            ↓
        Task 6-compatible output
    """

    # Convert and validate the Task 4 -> Task 5 contract.
    rca_card = convert_task4_output(task4_output)

    # Run the Task 5 remediation workflow.
    result = run_remediation(
        rca_card=rca_card,
        decision=decision,
        feedback=feedback,
    )

    return result.to_dict()