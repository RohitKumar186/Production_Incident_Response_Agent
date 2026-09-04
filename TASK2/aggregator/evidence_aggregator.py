from datetime import datetime, timezone

from TASK2.models.schemas import (
    Incident,
    AgentResult,
    InvestigationPayload,
    InvestigationOutput,
)


def aggregate_findings(
    incident: Incident,
    agent_results: list[AgentResult],
) -> InvestigationOutput:
    """
    Combine findings from all investigation agents
    into the Investigation Knowledge Card.
    """

    all_findings = []

    for result in agent_results:
        all_findings.extend(result.findings)

    successful_results = [
        result for result in agent_results
        if result.status == "SUCCESS"
    ]

    if successful_results:
        overall_confidence = sum(
            result.confidence for result in successful_results
        ) / len(successful_results)
    else:
        overall_confidence = 0.0

    if len(successful_results) == len(agent_results):
        status = "SUCCESS"
    elif successful_results:
        status = "PARTIAL"
    else:
        status = "FAILED"

    payload = InvestigationPayload(
        incident=incident,
        findings=all_findings,
        overall_confidence=round(overall_confidence, 2),
    )

    return InvestigationOutput(
        schema_version="1.0",
        incident_id=incident.incident_id,
        correlation_id=incident.incident_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        producer="investigation",
        consumer="rca",
        status=status,
        payload=payload,
    )