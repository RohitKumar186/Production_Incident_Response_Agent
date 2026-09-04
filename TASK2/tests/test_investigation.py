from TASK2.models.schemas import Incident
from TASK2.orchestrator.investigation import investigate_incident


def main():

    # Simulated incident coming from Task 1
    incident = Incident(
        incident_id="INC-001",
        service={
            "name": "order-api",
            "version": "v1.8"
        },
        severity="HIGH",
        detected_at="2026-09-02T10:25:00Z",
        symptom={
            "description": "API latency increased by 400%",
            "baseline_latency_ms": 100,
            "current_latency_ms": 500,
            "increase_percent": 400
        },
        environment="production"
    )

    # Run complete investigation
    investigation_card = investigate_incident(incident)

    # Display final Knowledge Card
    print("\n" + "=" * 70)
    print("FINAL INVESTIGATION KNOWLEDGE CARD")
    print("=" * 70)

    print(
        investigation_card.model_dump_json(indent=2)
    )


if __name__ == "__main__":
    main()