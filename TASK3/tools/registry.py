from .database import DatabaseTool
from .infrastructure import InfrastructureTool
from .logs import LogsTool
from .metrics import MetricsTool
from .network import NetworkTool


class ToolRegistry:
    """
    Central access point for all read-only investigation tools.
    """

    def __init__(self, infrastructure) -> None:

        self.metrics = MetricsTool(infrastructure)
        self.logs = LogsTool(infrastructure)
        self.database = DatabaseTool(infrastructure)
        self.network = NetworkTool(infrastructure)
        self.infrastructure = InfrastructureTool(
            infrastructure
        )

        # Read-only reference used for investigation routing.
        self._simulated_infrastructure = infrastructure

    @property
    def state(self):
        """
        Expose simulated state for routing only.

        Investigation tools themselves remain read-only.
        """
        return self._simulated_infrastructure.state