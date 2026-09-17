import pytest

from generator.incident_generator import INCIDENT_TYPES, IncidentGenerator
from models.alert import IncidentAlert
from simulator.infrastructure import SimulatedInfrastructure
from TASK2.investigator.investigator import Investigator
from TASK3.tools.registry import ToolRegistry


@pytest.mark.parametrize(
    "incident_type",
    INCIDENT_TYPES,
)
def test_incident_type(incident_type):
    infrastructure = SimulatedInfrastructure()

    generator = IncidentGenerator(
        infrastructure=infrastructure
    )

    tools = ToolRegistry(
        infrastructure
    )

    investigator = Investigator(
        tools
    )

    original_generate = generator.generate

    def generate_requested_type():
        incident = original_generate()

        while incident.incident_type != incident_type:
            infrastructure.reset()
            incident = original_generate()

        return incident

    generator.generate = generate_requested_type

    incident = generator.generate()

    assert incident.incident_type == incident_type

    alert = IncidentAlert.from_incident(incident)

    assert not hasattr(alert, "root_cause")
    assert not hasattr(alert, "fault_mechanism")

    investigation_card = investigator.investigate(alert)

    assert investigation_card.incident_id == incident.incident_id
    assert investigation_card.incident_type == incident.incident_type
    assert investigation_card.affected_component == incident.affected_component

    assert len(investigation_card.evidence) > 0

    assert not hasattr(investigation_card, "root_cause")
    assert not hasattr(investigation_card, "fault_mechanism")