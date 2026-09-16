from copy import deepcopy
from typing import Any

from TASK5.approval.approval import ApprovalResult
from TASK5.planner.planner import RemediationPlan


class SimulatedEnvironment:
    """
    Controlled environment used to simulate remediation.

    This class never connects to a real production system.
    """

    def __init__(
        self,
        db_query_latency_ms: float = 4200.0,
        api_latency_ms: float = 500.0,
        error_rate: float = 8.0,
        service_status: str = "DEGRADED",
    ) -> None:
        self.state: dict[str, Any] = {
            "db_query_latency_ms": db_query_latency_ms,
            "api_latency_ms": api_latency_ms,
            "error_rate": error_rate,
            "service_status": service_status,
        }

    def snapshot(self) -> dict[str, Any]:
        """Return a copy of the current simulated state."""

        return deepcopy(self.state)

    def execute(
        self,
        plan: RemediationPlan,
        approval: ApprovalResult,
    ) -> dict[str, Any]:
        """
        Execute an approved remediation in the simulated environment.

        Execution is blocked unless the human decision is APPROVED.
        """

        if not approval.should_execute:
            return {
                "status": "NOT_EXECUTED",
                "message": (
                    "Remediation was not executed because "
                    f"approval status was {approval.decision.value}"
                ),
                "state": self.snapshot(),
            }

        before_state = self.snapshot()

        self._apply_recommendation(plan)

        after_state = self.snapshot()

        return {
            "status": "SUCCESS",
            "message": "Remediation executed successfully",
            "before": before_state,
            "after": after_state,
        }

    def rollback(self, previous_state: dict[str, Any]) -> dict[str, Any]:
        """Restore the simulated environment to a previous state."""

        self.state = deepcopy(previous_state)

        return {
            "status": "SUCCESS",
            "message": "Simulated environment rolled back successfully",
            "state": self.snapshot(),
        }

    def _apply_recommendation(
        self,
        plan: RemediationPlan,
    ) -> None:
        """
        Apply the exact supported recommendation supplied by Task 4.

        Task 5 does not infer a fix from the RCA category alone.
        The action type and recommendation text both participate
        in selecting a controlled simulation.
        """

        action_type = plan.action_type.upper().strip()
        action = plan.action.strip().lower()

        if not action:
            raise ValueError(
                "Remediation action cannot be empty"
            )

        if action_type == "DATABASE_REMEDIATION":
            self._apply_database_remediation(action)

        elif action_type == "APPLICATION_REMEDIATION":
            self._apply_application_remediation(action)

        elif action_type == "NETWORK_REMEDIATION":
            self._apply_network_remediation(action)

        elif action_type == "INFRASTRUCTURE_REMEDIATION":
            self._apply_infrastructure_remediation(action)

        else:
            raise ValueError(
                f"Unsupported remediation action type: "
                f"{plan.action_type}"
            )

    def _apply_database_remediation(
        self,
        action: str,
    ) -> None:
        """Simulate supported database remediation operations."""

        if "optimize" in action and "query" in action:
            self.state["db_query_latency_ms"] = 300.0
            self.state["api_latency_ms"] = 120.0
            self.state["error_rate"] = 1.0
            self.state["service_status"] = "HEALTHY"
            return

        raise ValueError(
            "Unsupported database remediation recommendation: "
            f"{action}"
        )

    def _apply_application_remediation(
        self,
        action: str,
    ) -> None:
        """Simulate supported application remediation operations."""

        if (
            "rollback" in action
            or "deploy" in action
            or "restart" in action
            or "fix" in action
        ):
            self.state["api_latency_ms"] = 120.0
            self.state["error_rate"] = 1.0
            self.state["service_status"] = "HEALTHY"
            return

        raise ValueError(
            "Unsupported application remediation recommendation: "
            f"{action}"
        )

    def _apply_network_remediation(
        self,
        action: str,
    ) -> None:
        """Simulate supported network remediation operations."""

        if (
            "route" in action
            or "connection" in action
            or "network" in action
            or "restart" in action
            or "fix" in action
        ):
            self.state["api_latency_ms"] = 120.0
            self.state["error_rate"] = 1.0
            self.state["service_status"] = "HEALTHY"
            return

        raise ValueError(
            "Unsupported network remediation recommendation: "
            f"{action}"
        )

    def _apply_infrastructure_remediation(
        self,
        action: str,
    ) -> None:
        """Simulate supported infrastructure remediation operations."""

        if (
            "scale" in action
            or "restart" in action
            or "resource" in action
            or "deploy" in action
            or "fix" in action
        ):
            self.state["api_latency_ms"] = 120.0
            self.state["error_rate"] = 1.0
            self.state["service_status"] = "HEALTHY"
            return

        raise ValueError(
            "Unsupported infrastructure remediation recommendation: "
            f"{action}"
        )