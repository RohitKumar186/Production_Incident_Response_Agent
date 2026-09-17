from simulator.infrastructure import SimulatedInfrastructure
from generator.incident_generator import IncidentGenerator
from models.alert import IncidentAlert

from TASK2.investigator.investigator import Investigator
from TASK2.models.task4_adapter import Task4Adapter
from TASK3.tools.registry import ToolRegistry


def main():

    infrastructure = SimulatedInfrastructure()

    generator = IncidentGenerator(
        infrastructure,
        seed=42,
    )

    incident = generator.generate()

    alert = IncidentAlert.from_incident(
        incident
    )

    tools = ToolRegistry(
        infrastructure
    )

    investigator = Investigator(
        tools
    )

    investigation_card = (
        investigator.investigate(alert)
    )

    adapter = Task4Adapter()

    task4_input = adapter.convert(
        investigation_card
    )

    print("\n" + "=" * 70)
    print("TASK 2 → TASK 4 ADAPTER TEST")
    print("=" * 70)

    print(
        "Incident ID:",
        task4_input.incident_id,
    )

    print(
        "Incident Type:",
        task4_input.payload.incident.incident_type,
    )

    print(
        "Service:",
        task4_input.payload.incident.service,
    )

    print(
        "Symptom:",
        task4_input.payload.incident.symptom,
    )

    print(
        "Technology:",
        task4_input.payload.incident.technology_stack,
    )

    print(
        "Findings:",
        len(task4_input.payload.findings),
    )

    print("\n" + "-" * 70)

    for finding in task4_input.payload.findings:

        print(
            "\nFinding ID:",
            finding.finding_id,
        )

        print(
            "Agent:",
            finding.agent,
        )

        print(
            "Category:",
            finding.category,
        )

        print(
            "Confidence:",
            finding.confidence,
        )

        print(
            "Finding:",
            finding.finding,
        )

    print("\n" + "=" * 70)

    print(
        "Original incident has root cause:",
        hasattr(
            incident,
            "root_cause",
        ),
    )

    print(
        "Task 4 input has root cause:",
        hasattr(
            task4_input,
            "root_cause",
        )
        or hasattr(
            task4_input.payload.incident,
            "root_cause",
        ),
    )

    print("=" * 70)


if __name__ == "__main__":
    main()