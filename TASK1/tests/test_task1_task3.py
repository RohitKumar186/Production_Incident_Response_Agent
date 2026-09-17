from simulator.infrastructure import SimulatedInfrastructure
from generator.incident_generator import INCIDENT_TYPES, IncidentGenerator
from generator.scheduler import IncidentScheduler
from models.alert import IncidentAlert

from TASK3.tools.registry import ToolRegistry
from TASK2.investigator.investigator import Investigator


def component_state(infrastructure, component):
    """Return the state dictionary for any simulated component."""

    for collection in (
        infrastructure.state.services,
        infrastructure.state.databases,
        infrastructure.state.network,
        infrastructure.state.infrastructure,
        infrastructure.state.dependencies,
    ):
        if component in collection:
            return collection[component]

    return None


def test_only_allowed_incident_types_are_generated():
    infrastructure = SimulatedInfrastructure()
    generator = IncidentGenerator(infrastructure, seed=123)

    generated_types = set()

    for _ in range(100):
        infrastructure.reset()
        incident = generator.generate()
        generated_types.add(incident.incident_type)

    assert generated_types.issubset(set(INCIDENT_TYPES))


def test_incident_generator_produces_variety():
    infrastructure = SimulatedInfrastructure()
    generator = IncidentGenerator(infrastructure, seed=42)

    incidents = []

    for _ in range(30):
        infrastructure.reset()
        incidents.append(generator.generate())

    types = {incident.incident_type for incident in incidents}
    components = {
        incident.affected_component
        for incident in incidents
    }

    assert len(types) >= 4
    assert len(components) >= 4


def test_incident_changes_simulated_state():
    infrastructure = SimulatedInfrastructure()
    baseline = infrastructure.snapshot()

    generator = IncidentGenerator(infrastructure, seed=42)
    incident = generator.generate()

    after_incident = infrastructure.snapshot()

    assert baseline != after_incident
    assert component_state(
        infrastructure,
        incident.affected_component,
    ) is not None


def test_alert_hides_root_cause():
    infrastructure = SimulatedInfrastructure()
    generator = IncidentGenerator(infrastructure, seed=42)

    incident = generator.generate()
    alert = IncidentAlert.from_incident(incident)

    assert hasattr(incident, "root_cause")
    assert not hasattr(alert, "root_cause")


def test_scheduler_resets_before_each_incident():
    infrastructure = SimulatedInfrastructure()
    generator = IncidentGenerator(infrastructure, seed=42)
    scheduler = IncidentScheduler(generator)

    scheduler.run_once()

    # Capture the state after the first incident.
    first_state = infrastructure.snapshot()

    scheduler.run_once()

    second_state = infrastructure.snapshot()

    # Both should represent incident-modified states.
    assert first_state != second_state

    # A fresh infrastructure represents the expected clean baseline.
    fresh = SimulatedInfrastructure()

    assert fresh.snapshot() != first_state
    assert fresh.snapshot() != second_state


def test_task2_investigates_task1_alert():
    infrastructure = SimulatedInfrastructure()
    generator = IncidentGenerator(infrastructure, seed=42)

    incident = generator.generate()
    alert = IncidentAlert.from_incident(incident)

    tools = ToolRegistry(infrastructure)
    investigator = Investigator(tools)

    card = investigator.investigate(alert)

    assert card.incident_id == incident.incident_id
    assert card.incident_type == incident.incident_type
    assert card.affected_component == incident.affected_component
    assert card.technology_stack == incident.technology_stack

    assert len(card.evidence) > 0


def test_investigation_card_hides_root_cause():
    infrastructure = SimulatedInfrastructure()
    generator = IncidentGenerator(infrastructure, seed=42)

    incident = generator.generate()
    alert = IncidentAlert.from_incident(incident)

    tools = ToolRegistry(infrastructure)
    card = Investigator(tools).investigate(alert)

    assert not hasattr(card, "root_cause")


def test_task3_tools_are_read_only():
    infrastructure = SimulatedInfrastructure()
    generator = IncidentGenerator(infrastructure, seed=42)

    incident = generator.generate()

    before = infrastructure.snapshot()

    tools = ToolRegistry(infrastructure)

    component = incident.affected_component

    if component in infrastructure.state.services:
        tools.metrics.service_metrics(component)
        tools.logs.search(component)

    elif component in infrastructure.state.databases:
        tools.metrics.database_metrics(component)
        tools.database.inspect(component)
        tools.logs.search(component)

    elif component in infrastructure.state.network:
        tools.network.inspect(component)
        tools.logs.search(component)

    elif component in infrastructure.state.infrastructure:
        tools.infrastructure.inspect(component)
        tools.logs.search(component)

    after = infrastructure.snapshot()

    assert before == after