from models.schemas import AgentResult, Evidence, Finding, Incident, InvestigationStatus
from tools.network_tool import get_network_metrics


def investigate_network(incident: Incident) -> AgentResult:
    """
    Investigate network health for the given incident.
    """

    records = get_network_metrics(
        service=incident.service_name,
        incident_id=incident.incident_id,
    )

    if not records:
        return AgentResult(
            agent="network",
            status=InvestigationStatus.FAILED,
            error={
                "code": "NO_NETWORK_DATA",
                "message": "No network data was found for the incident.",
                "retryable": False,
            },
        )

    latest = records[-1]

    latency = latest["latency_ms"]
    packet_loss = latest["packet_loss_percent"]
    status = latest["status"]

    findings = []

    if latency <= 50 and packet_loss == 0 and status == "HEALTHY":
        findings.append(
            Finding(
                finding_id="NET-F-001",
                agent="network",
                category="NETWORK",
                finding="Network conditions are within normal range.",
                value=f"{latency} ms latency, {packet_loss}% packet loss",
                expected_value="< 50 ms latency and 0% packet loss",
                evidence=[
                    Evidence(
                        source="network_metrics",
                        reference="network.json",
                        details=(
                            f"Network status: {status}; "
                            f"latency: {latency} ms; "
                            f"packet loss: {packet_loss}%."
                        ),
                    )
                ],
                confidence=0.94,
                severity="LOW",
            )
        )
    else:
        findings.append(
            Finding(
                finding_id="NET-F-002",
                agent="network",
                category="NETWORK",
                finding="Network conditions may be degraded.",
                value=(
                    f"{latency} ms latency, "
                    f"{packet_loss}% packet loss"
                ),
                expected_value="< 50 ms latency and 0% packet loss",
                evidence=[
                    Evidence(
                        source="network_metrics",
                        reference="network.json",
                        details=(
                            f"Network status: {status}; "
                            f"latency: {latency} ms; "
                            f"packet loss: {packet_loss}%."
                        ),
                    )
                ],
                confidence=0.85,
                severity="MEDIUM",
            )
        )

    return AgentResult(
        agent="network",
        status=InvestigationStatus.SUCCESS,
        findings=findings,
        confidence=max(
            (finding.confidence for finding in findings),
            default=0.0,
        ),
    )