from typing import Any, Optional

from TASK5.approval.approval import ApprovalDecision

from integration.task4_to_task6 import (
    run_task5_and_task6,
)

from backend.services.pira_service import (
    run_investigation_and_rca,
)


class PIRAOrchestrator:
    """
    Backend-controlled PIRA workflow.

    Existing Task 1–6 core logic remains untouched.
    """

    def investigate_and_run_rca(
        self,
        incident: Any,
    ) -> dict:
        """
        Run:

            Incident
               ↓
            Task 1
               ↓
            Task 3
               ↓
            Task 2
               ↓
            Task 4 RCA/RAG
        """

        return run_investigation_and_rca(
            incident
        )

    def run_remediation_and_verification(
        self,
        rca_output: Any,
        decision: ApprovalDecision,
        feedback: Optional[str] = None,
    ) -> dict:
        """
        Run:

            Task 4 RCA
                ↓
            Task 5 Remediation
                ↓
            Task 6 Verification

        Task 5 execution is controlled by the
        ApprovalDecision.
        """

        return run_task5_and_task6(
            task4_output=rca_output,
            decision=decision,
            feedback=feedback,
        )

    def run_after_approval(
        self,
        rca_output: Any,
        decision: ApprovalDecision,
        feedback: Optional[str] = None,
    ) -> dict:
        """
        Continue the workflow after human approval.
        """

        return self.run_remediation_and_verification(
            rca_output=rca_output,
            decision=decision,
            feedback=feedback,
        )


# Shared orchestrator instance
pira_orchestrator = PIRAOrchestrator()