from dataclasses import dataclass, field
from typing import Any


@dataclass
class SimulatedState:
    """
    Mutable state of the simulated production infrastructure.

    This represents the actual simulated environment.

    The active fault is simulator-only information and must not
    be exposed to Task 2.
    """

    services: dict[str, dict[str, Any]] = field(default_factory=dict)
    databases: dict[str, dict[str, Any]] = field(default_factory=dict)
    network: dict[str, dict[str, Any]] = field(default_factory=dict)
    infrastructure: dict[str, dict[str, Any]] = field(default_factory=dict)
    dependencies: dict[str, dict[str, Any]] = field(default_factory=dict)

    active_fault: Any | None = None

    def snapshot(self) -> dict[str, Any]:
        """Return a deep-copy snapshot of the current state."""
        import copy

        return copy.deepcopy(
            {
                "services": self.services,
                "databases": self.databases,
                "network": self.network,
                "infrastructure": self.infrastructure,
                "dependencies": self.dependencies,
                "active_fault": self.active_fault,
            }
        )