"""
Task 5 - Remediation and Human Approval.

Public interface for consuming Task 4 RCA Knowledge Cards
and producing Task 6-compatible remediation results.
"""

from TASK5.approval.approval import ApprovalDecision
from TASK5.orchestrator.remediation import (
    RemediationResult,
    run_remediation,
)
from TASK5.orchestrator.task4_adapter import convert_task4_output

__all__ = [
    "ApprovalDecision",
    "RemediationResult",
    "run_remediation",
    "convert_task4_output",
]