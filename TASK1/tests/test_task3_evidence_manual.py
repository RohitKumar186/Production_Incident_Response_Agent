from simulator.infrastructure import SimulatedInfrastructure
from generator.incident_generator import IncidentGenerator
from models.alert import IncidentAlert
from TASK3.tools.registry import ToolRegistry
from TASK2.investigator.investigator import Investigator


def main():
    infrastructure = SimulatedInfrastructure()

    generator = IncidentGenerator(
        infrastructure,
        seed=42,
    )

    incident = generator.generate()

    alert = IncidentAlert.from_incident(incident)

    tools = ToolRegistry(infrastructure)

    investigator = Investigator(tools)

    card = investigator.investigate(alert)

    print("\n" + "=" * 70)
    print("INCIDENT")
    print("=" * 70)

    print("TYPE:", incident.incident_type)
    print("COMPONENT:", incident.affected_component)
    print("SYMPTOMS:", incident.symptoms)

    print("\n" + "=" * 70)
    print("INVESTIGATION EVIDENCE")
    print("=" * 70)

    for item in card.evidence:
        print("\nSOURCE:", item["source"])
        print("DATA:", item["data"])

    print("\n" + "=" * 70)
    print("ROOT CAUSE VISIBILITY CHECK")
    print("=" * 70)

    print(
        "Incident has root cause:",
        hasattr(incident, "root_cause"),
    )

    print(
        "Alert has root cause:",
        hasattr(alert, "root_cause"),
    )

    print(
        "Investigation card has root cause:",
        hasattr(card, "root_cause"),
    )


if __name__ == "__main__":
    main()