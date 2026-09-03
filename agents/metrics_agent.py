from models.schemas import AgentResult, Evidence, Finding, Incident, InvestigationStatus
from tools.metrics_tool import get_metrics


def investigate_metrics(incident: Incident) -> AgentResult:
    """
    Investigate service metrics for the given incident.
    """

    metrics = get_metrics(
        service=incident.service_name,
        incident_id=incident.incident_id,
    )

    if not metrics:
        return AgentResult(
            agent="metrics",
            status=InvestigationStatus.FAILED,
            error={
                "code": "NO_METRIC_DATA",
                "message": "No metrics were found for the incident.",
                "retryable": False,
            },
        )

    findings = []

    latest = metrics[-1]

    latency = latest["latency_ms"]
    cpu = latest["cpu_percent"]
    error_rate = latest["error_rate_percent"]

    if latency > incident.baseline_latency_ms:
        findings.append(
            Finding(
                finding_id="METRIC-F-001",
                agent="metrics",
                category="METRICS",
                finding="API latency increased significantly.",
                value=f"{latency} ms",
                expected_value=f"Approximately {incident.baseline_latency_ms} ms",
                evidence=[
                    Evidence(
                        source="service_metrics",
                        reference="metrics.json",
                        details=(
                            f"Latest latency is {latency} ms compared "
                            f"with baseline {incident.baseline_latency_ms} ms."
                        ),
                    )
                ],
                confidence=0.96,
                severity="HIGH",
            )
        )

    if cpu >= 80:
        findings.append(
            Finding(
                finding_id="METRIC-F-002",
                agent="metrics",
                category="INFRASTRUCTURE",
                finding="CPU utilization is elevated.",
                value=f"{cpu}%",
                expected_value="< 80%",
                evidence=[
                    Evidence(
                        source="service_metrics",
                        reference="metrics.json",
                        details=f"CPU utilization reached {cpu}%.",
                    )
                ],
                confidence=0.89,
                severity="HIGH",
            )
        )

    if error_rate > 1:
        findings.append(
            Finding(
                finding_id="METRIC-F-003",
                agent="metrics",
                category="APPLICATION",
                finding="API error rate increased.",
                value=f"{error_rate}%",
                expected_value="< 1%",
                evidence=[
                    Evidence(
                        source="service_metrics",
                        reference="metrics.json",
                        details=f"Error rate reached {error_rate}%.",
                    )
                ],
                confidence=0.94,
                severity="HIGH",
            )
        )

    return AgentResult(
        agent="metrics",
        status=InvestigationStatus.SUCCESS,
        findings=findings,
        confidence=max(
            (finding.confidence for finding in findings),
            default=0.0,
        ),
    )