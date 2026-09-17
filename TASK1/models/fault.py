from dataclasses import dataclass
from typing import Any


@dataclass
class SimulatedFault:
    """
    Represents the underlying fault injected into the simulated
    infrastructure.

    This is internal simulator state.

    IMPORTANT:
    Task 2 must never receive this object directly.
    """

    fault_id: str
    fault_domain: str
    mechanism: str
    component: str
    parameters: dict[str, Any]
    description: str