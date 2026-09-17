from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class IncidentAlert:
    """
    Public incident information passed from Task 1 to Task 2.

    IMPORTANT:
    The simulator's hidden root cause is intentionally NOT included.
    Task 2 must discover the cause through investigation.
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

    @classmethod
    def from_incident(cls, incident):
        return cls(
            incident_id=incident.incident_id,
            timestamp=incident.timestamp,
            incident_type=incident.incident_type,
            title=incident.title,
            description=incident.description,
            affected_component=incident.affected_component,
            technology_stack=incident.technology_stack,
            symptoms=incident.symptoms,
            abnormal_state=incident.abnormal_state,
        )