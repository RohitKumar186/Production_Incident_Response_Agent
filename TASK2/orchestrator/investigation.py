from TASK2.models.schemas import Incident
from TASK2.agents.logs_agent import investigate_logs
from TASK2.agents.metrics_agent import investigate_metrics
from TASK2.agents.database_agent import investigate_database
from TASK2.agents.network_agent import investigate_network
from TASK2.aggregator.evidence_aggregator import aggregate_findings


def investigate_incident(incident: Incident):
    """
    Run all investigation agents for an incident
    and generate the final Investigation Knowledge Card.
    """

    print(f"\n🚨 Investigating Incident: {incident.incident_id}")
    print(f"Service: {incident.service['name']}")
    print(f"Severity: {incident.severity}")
    print(f"Symptom: {incident.symptom['description']}")
    print("-" * 60)

    # -------------------------------------------------
    # Run Logs Agent
    # -------------------------------------------------

    logs_result = investigate_logs(incident)

    print(
        f"[Logs Agent] "
        f"{logs_result.status} | "
        f"Findings: {len(logs_result.findings)}"
    )

    # -------------------------------------------------
    # Run Metrics Agent
    # -------------------------------------------------

    metrics_result = investigate_metrics(incident)

    print(
        f"[Metrics Agent] "
        f"{metrics_result.status} | "
        f"Findings: {len(metrics_result.findings)}"
    )

    # -------------------------------------------------
    # Run Database Agent
    # -------------------------------------------------

    database_result = investigate_database(incident)

    print(
        f"[Database Agent] "
        f"{database_result.status} | "
        f"Findings: {len(database_result.findings)}"
    )

    # -------------------------------------------------
    # Run Network Agent
    # -------------------------------------------------

    network_result = investigate_network(incident)

    print(
        f"[Network Agent] "
        f"{network_result.status} | "
        f"Findings: {len(network_result.findings)}"
    )

    # -------------------------------------------------
    # Collect all agent results
    # -------------------------------------------------

    agent_results = [
        logs_result,
        metrics_result,
        database_result,
        network_result,
    ]

    # -------------------------------------------------
    # Aggregate findings
    # -------------------------------------------------

    investigation_card = aggregate_findings(
        incident,
        agent_results
    )

    print("-" * 60)
    print(
        f"Investigation Status: "
        f"{investigation_card.status}"
    )

    print(
        f"Total Findings: "
        f"{len(investigation_card.payload.findings)}"
    )

    print(
        f"Overall Confidence: "
        f"{investigation_card.payload.overall_confidence}"
    )

    print("Investigation completed.")

    return investigation_card