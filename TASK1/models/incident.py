from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Incident:
    """
    Complete simulator-side incident representation.

    root_cause and fault information are simulator ground truth.
    They must never be exposed to Task 2.
    """

    incident_id: str
    timestamp: datetime
    incident_type: str
    title: str
    description: str
    affected_component: str
    technology_stack: list[str]
    symptoms: list[str]
    abnormal_state: dict[str, Any]

    root_cause: str
    fault_domain: str
    fault_mechanism: str