from typing import Any


class NetworkTool:
    """
    Read-only diagnostics for the simulated network.

    The tool exposes observable network conditions without
    modifying the simulated infrastructure.
    """

    def __init__(self, infrastructure) -> None:
        self.infrastructure = infrastructure

    def inspect(self, component: str) -> dict[str, Any]:
        state = self.infrastructure.state.network.get(component)

        if state is None:
            return {
                "error": f"Unknown network component: {component}"
            }

        return {
            "component": component,
            "status": state["status"],
            "packet_loss_percent": state.get(
                "packet_loss_percent"
            ),
            "latency_ms": state.get("latency_ms"),
            "dns_latency_ms": state.get(
                "dns_latency_ms"
            ),
            "connection_resets": state.get(
                "connection_resets"
            ),
        }