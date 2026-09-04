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
from tools.ecommerce_monitor import measure_order_api, create_incident


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def run_investigation(incident: Incident) -> KnowledgeCard:
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

    if findings:
        overall_confidence = round(
            sum(finding.confidence for finding in findings) / len(findings),
            2,
        )
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
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_file = DATA_DIR / "knowledge_card.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(
            knowledge_card.model_dump(mode="json"),
            file,
            indent=2,
        )

    return output_file


def run_simulation_mode() -> Incident:
    """Generate an incident using the existing simulation environment."""
    return generate_simulation_data()


def run_ecommerce_mode() -> Incident | None:
    """Detect an incident from the real e-commerce application."""

    monitor_result = measure_order_api("INCIDENT-MONITOR-001")

    print("\nE-COMMERCE MONITOR RESULT")
    print("=" * 50)
    print(f"Status            : {monitor_result.get('status_code')}")
    print(f"Baseline          : {monitor_result.get('baseline_latency_ms')} ms")
    print(f"Current Latency   : {monitor_result.get('latency_ms')} ms")
    print(f"Increase          : {monitor_result.get('increase_percent')}%")
    print(f"Incident Detected : {monitor_result.get('incident_detected')}")
    print(f"Successful        : {monitor_result.get('success')}")

    if monitor_result.get("error"):
        print(f"Error             : {monitor_result['error']}")

    incident = create_incident(monitor_result)

    return incident


def main() -> None:
    print("\nPRODUCTION INCIDENT RESPONSE")
    print("=" * 50)
    print("Monitoring real e-commerce application...")

    incident = run_ecommerce_mode()

    if incident is None:
        print("\n✅ No incident detected.")
        print("The e-commerce application appears healthy.")
        return

    print("\n🚨 INCIDENT DETECTED")
    print("=" * 50)
    print(f"Incident ID       : {incident.incident_id}")
    print(f"Service           : {incident.service_name}")
    print(f"Severity          : {incident.severity}")
    print(f"Baseline Latency  : {incident.baseline_latency_ms} ms")
    print(f"Current Latency   : {incident.current_latency_ms} ms")
    print(f"Increase          : {incident.increase_percent}%")

    print("\nStarting investigation agents...")

    knowledge_card = run_investigation(incident)

    output_file = save_knowledge_card(knowledge_card)

    print("\nINVESTIGATION COMPLETE")
    print("=" * 50)
    print(f"Status            : {knowledge_card.status}")
    print(
        f"Findings          : "
        f"{len(knowledge_card.payload.findings)}"
    )
    print(
        f"Overall Confidence: "
        f"{knowledge_card.payload.overall_confidence}"
    )
    print(f"Knowledge Card    : {output_file}")


if __name__ == "__main__":
    main()