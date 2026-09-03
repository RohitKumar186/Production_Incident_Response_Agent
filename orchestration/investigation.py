"""
Investigation orchestrator.

Coordinates the specialist investigation agents and combines
their findings into the shared Knowledge Card used by Member 2.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from agents.database_agent import investigate_database
from agents.logs_agent import investigate_logs
from agents.metrics_agent import investigate_metrics
from agents.network_agent import investigate_network
from models.schemas import (
    AgentResult,
    Incident,
    InvestigationPayload,
    InvestigationStatus,
    KnowledgeCard,
)
from simulation.incident_generator import generate_simulation_data


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def run_investigation(incident: Incident) -> KnowledgeCard:
    """
    Run all investigation agents and create a Knowledge Card.
    """

    agent_results: list[AgentResult] = [
        investigate_logs(incident),
        investigate_metrics(incident),
        investigate_database(incident),
        investigate_network(incident),
    ]

    findings = []

    for result in agent_results:
        findings.extend(result.findings)

    successful_results = [
        result
        for result in agent_results
        if result.status == InvestigationStatus.SUCCESS
    ]

    failed_results = [
        result
        for result in agent_results
        if result.status == InvestigationStatus.FAILED
    ]

    if failed_results and successful_results:
        overall_status = InvestigationStatus.PARTIAL
    elif failed_results:
        overall_status = InvestigationStatus.FAILED
    else:
        overall_status = InvestigationStatus.SUCCESS

    if successful_results:
        overall_confidence = sum(
            result.confidence for result in successful_results
        ) / len(successful_results)
    else:
        overall_confidence = 0.0

    payload = InvestigationPayload(
        incident=incident,
        findings=findings,
        overall_confidence=overall_confidence,
    )

    return KnowledgeCard(
        schema_version="1.0",
        incident_id=incident.incident_id,
        correlation_id=incident.incident_id,
        timestamp=datetime.now(timezone.utc),
        producer="investigation",
        consumer="rca",
        status=overall_status,
        payload=payload,
    )


def save_knowledge_card(knowledge_card: KnowledgeCard) -> Path:
    """
    Save the Knowledge Card as JSON for Member 2.
    """

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_file = DATA_DIR / "knowledge_card.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            knowledge_card.model_dump(mode="json"),
            file,
            indent=2,
        )

    return output_file


def main() -> None:
    """
    Run the complete investigation pipeline.

    1. Generate a fresh simulated incident
    2. Generate all production data
    3. Run investigation agents
    4. Create the Knowledge Card
    5. Save the Knowledge Card
    """

    incident = generate_simulation_data()

    knowledge_card = run_investigation(incident)

    output_file = save_knowledge_card(knowledge_card)

    print("\n" + "=" * 60)
    print("INVESTIGATION COMPLETE")
    print("=" * 60)

    print(f"Incident ID       : {knowledge_card.incident_id}")
    print(f"Status            : {knowledge_card.status}")
    print(
        f"Overall Confidence: "
        f"{knowledge_card.payload.overall_confidence:.2f}"
    )
    print(
        f"Total Findings    : "
        f"{len(knowledge_card.payload.findings)}"
    )

    print("\nKnowledge Card saved to:")
    print(f"  {output_file}")

    print("\n" + "=" * 60)
    print("INVESTIGATION KNOWLEDGE CARD")
    print("=" * 60)

    print(knowledge_card.model_dump_json(indent=2))


if __name__ == "__main__":
    main()