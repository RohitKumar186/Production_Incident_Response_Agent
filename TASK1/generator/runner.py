from datetime import datetime

from generator.incident_generator import INCIDENT_TYPES, IncidentGenerator
from generator.scheduler import IncidentScheduler
from simulator.infrastructure import SimulatedInfrastructure

from models.alert import IncidentAlert
from TASK2.investigator.investigator import Investigator
from TASK3.tools.registry import ToolRegistry


# Simulation/demo interval.
# In a real production environment incidents would occur unpredictably.
# For this project demo, we generate one independent incident every 10 minutes.
INTERVAL_SECONDS = 600


def print_header() -> None:
    print("\n" + "=" * 80)
    print("PRODUCTION INCIDENT RESPONSE AGENT")
    print("=" * 80)
    print("Continuous Production Incident Simulation")
    print()
    print("Pipeline:")
    print("  Production Simulation")
    print("        ↓")
    print("  TASK 1 — Incident Generation")
    print("        ↓")
    print("  TASK 2 — Investigation")
    print("        ↓")
    print("  TASK 3 — Diagnostic Evidence")
    print()
    print("Simulation interval: 10 minutes")
    print("Incident types are selected independently and randomly.")
    print()
    print("Available incident types:")

    for incident_type in INCIDENT_TYPES:
        print(f"  - {incident_type}")

    print()
    print("The first incident is generated immediately.")
    print("The next independent incident is generated after 10 minutes.")
    print("Press CTRL+C to stop.")
    print("=" * 80)


def print_incident(incident) -> None:
    print("\n" + "=" * 80)
    print("TASK 1 — INCIDENT GENERATED")
    print("=" * 80)

    print("Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Incident ID:", incident.incident_id)
    print("Type:", incident.incident_type)
    print("Title:", incident.title)
    print("Affected Component:", incident.affected_component)
    print("Technology Stack:", ", ".join(incident.technology_stack))

    print("\nSymptoms:")
    for symptom in incident.symptoms:
        print(f"  - {symptom}")

    print("\nObserved Abnormal State:")
    for key, value in incident.abnormal_state.items():
        print(f"  {key}: {value}")


def process_incident(incident, investigator) -> None:
    """
    Pass the public incident alert to Task 2.

    Task 2 does not receive the simulator's hidden root cause
    or hidden fault mechanism.
    """

    alert = IncidentAlert.from_incident(incident)

    print("\n" + "-" * 80)
    print("TASK 2 — INVESTIGATION STARTED")
    print("-" * 80)

    print("Incident ID:", alert.incident_id)
    print("Incident Type:", alert.incident_type)
    print("Affected Component:", alert.affected_component)

    investigation_card = investigator.investigate(alert)

    print("\nInvestigation completed.")
    print("InvestigationCard created.")
    print("Evidence items collected:", len(investigation_card.evidence))

    print("\n" + "-" * 80)
    print("TASK 3 — DIAGNOSTIC EVIDENCE")
    print("-" * 80)

    for evidence in investigation_card.evidence:
        source = evidence.get("source", "unknown")
        component = evidence.get("component", "unknown")
        data = evidence.get("data", {})

        print(f"\n[{source}] {component}")
        print(f"  {data}")

    print("\n" + "-" * 80)
    print("TASK 2 → TASK 4 HANDOFF OBJECT")
    print("-" * 80)

    print("Producer:", investigation_card.producer)
    print("Consumer:", investigation_card.consumer)
    print("Schema Version:", investigation_card.schema_version)
    print("Incident ID:", investigation_card.incident_id)
    print("Incident Type:", investigation_card.incident_type)
    print("Affected Component:", investigation_card.affected_component)
    print("Evidence Items:", len(investigation_card.evidence))

    print("\nBoundary Check:")
    print(
        "  Hidden root cause available to Task 2:",
        hasattr(alert, "root_cause"),
    )
    print(
        "  Hidden fault mechanism available to Task 2:",
        hasattr(alert, "fault_mechanism"),
    )
    print(
        "  Root cause available in InvestigationCard:",
        hasattr(investigation_card, "root_cause"),
    )

    print("\n" + "=" * 80)
    print("INCIDENT PROCESSING COMPLETE")
    print("TASK 1 → TASK 2 → TASK 3 COMPLETE")
    print("=" * 80)


def main() -> None:
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

    def handle_incident(incident) -> None:
        print_incident(incident)
        process_incident(
            incident,
            investigator,
        )

        print("\n" + "=" * 80)
        print("SIMULATION WAITING")
        print("=" * 80)
        print("Production simulation continues running.")
        print("Next independent incident will be generated in 10 minutes.")
        print("Press CTRL+C to stop.")
        print("=" * 80)

    scheduler = IncidentScheduler(
        generator=generator,
        interval_seconds=INTERVAL_SECONDS,
        on_incident=handle_incident,
    )

    print_header()

    try:
        scheduler.run_forever()

    except KeyboardInterrupt:
        print("\n\n" + "=" * 80)
        print("PRODUCTION INCIDENT RESPONSE AGENT STOPPED")
        print("=" * 80)
        print("Continuous incident simulation terminated by user.")
        print("TASK 1 → TASK 2 → TASK 3 runner stopped.")
        print("=" * 80)


if __name__ == "__main__":
    main()