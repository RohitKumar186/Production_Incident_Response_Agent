from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class InvestigationCard:
    """
    Evidence collected by Task 2.

    Task 2 describes observations and evidence.
    It does not contain the simulator's hidden root cause.
    """

    incident_id: str
    timestamp: datetime
    incident_type: str
    affected_component: str
    technology_stack: list[str]
    observed_symptoms: list[str]
    evidence: list[dict[str, Any]]
    current_state: dict[str, Any]
    producer: str = "TASK2"
    consumer: str = "TASK4"
    schema_version: str = "1.0"