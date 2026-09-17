from typing import Any


class InfrastructureTool:
    """
    Read-only diagnostics for simulated compute infrastructure.

    Exposes resource utilization and workload-capacity evidence.
    """

    def __init__(self, infrastructure) -> None:
        self.infrastructure = infrastructure

    def inspect(self, component: str) -> dict[str, Any]:
        state = self.infrastructure.state.infrastructure.get(
            component
        )

        if state is None:
            return {
                "error": (
                    f"Unknown infrastructure component: {component}"
                )
            }

        return {
            "component": component,
            "status": state["status"],
            "cpu_percent": state.get("cpu_percent"),
            "memory_percent": state.get("memory_percent"),
            "disk_percent": state.get("disk_percent"),
            "pods_restarting": state.get(
                "pods_restarting"
            ),
            "queue_depth": state.get("queue_depth"),
            "available_workers": state.get(
                "available_workers"
            ),
            "total_workers": state.get(
                "total_workers"
            ),
        }