from simulator.infrastructure import SimulatedInfrastructure
from generator.incident_generator import IncidentGenerator
from generator.scheduler import IncidentScheduler


def get_component_state(infrastructure, component):
    for collection in (
        infrastructure.state.services,
        infrastructure.state.databases,
        infrastructure.state.network,
        infrastructure.state.infrastructure,
    ):
        if component in collection:
            return collection[component]

    return None


infrastructure = SimulatedInfrastructure()
generator = IncidentGenerator(infrastructure, seed=42)
scheduler = IncidentScheduler(generator)

print("\nTesting 5 independent incidents...\n")

for number in range(1, 6):
    incident = scheduler.run_once()
    state = get_component_state(
        infrastructure,
        incident.affected_component,
    )

    print(f"{number}. {incident.incident_type}")
    print(f"   Component : {incident.affected_component}")
    print(f"   State     : {state}")
    print()