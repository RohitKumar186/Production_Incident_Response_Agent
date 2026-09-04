from models.schemas import (
    AgentResult,
    Evidence,
    Finding,
    Incident,
    InvestigationStatus,
)
from tools.metrics_tool import get_metrics
from tools.ecommerce_metrics_tool import get_ecommerce_metrics


def _investigate_simulation_metrics(incident: Incident) -> AgentResult:
    """Investigate metrics from the existing simulation data."""

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
                expected_value=(
                    f"Approximately "
                    f"{incident.baseline_latency_ms} ms"
                ),
                evidence=[
                    Evidence(
                        source="service_metrics",
                        reference="metrics.json",
                        details=(
                            f"Latest latency is {latency} ms compared "
                            f"with baseline "
                            f"{incident.baseline_latency_ms} ms."
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
                category="METRICS",
                finding="CPU utilization is high.",
                value=f"{cpu}%",
                expected_value="< 80%",
                evidence=[
                    Evidence(
                        source="service_metrics",
                        reference="metrics.json",
                        details=(
                            f"Latest CPU utilization is {cpu}%."
                        ),
                    )
                ],
                confidence=0.91,
                severity="HIGH",
            )
        )

    if error_rate > 1:
        findings.append(
            Finding(
                finding_id="METRIC-F-003",
                agent="metrics",
                category="METRICS",
                finding="API error rate increased.",
                value=f"{error_rate}%",
                expected_value="< 1%",
                evidence=[
                    Evidence(
                        source="service_metrics",
                        reference="metrics.json",
                        details=(
                            f"Latest API error rate is "
                            f"{error_rate}%."
                        ),
                    )
                ],
                confidence=0.93,
                severity="HIGH",
            )
        )

    confidence = (
        round(
            sum(finding.confidence for finding in findings)
            / len(findings),
            2,
        )
        if findings
        else 0.0
    )

    return AgentResult(
        agent="metrics",
        status=InvestigationStatus.SUCCESS,
        findings=findings,
        confidence=confidence,
    )


def _investigate_ecommerce_metrics(
    incident: Incident,
) -> AgentResult:
    """Investigate metrics from the real e-commerce application."""

    metrics = get_ecommerce_metrics(
        order_id=f"{incident.incident_id}-METRICS"
    )

    if not metrics:
        return AgentResult(
            agent="metrics",
            status=InvestigationStatus.FAILED,
            error={
                "code": "NO_ECOMMERCE_METRIC_DATA",
                "message": (
                    "No metrics were collected from the "
                    "e-commerce application."
                ),
                "retryable": True,
            },
        )

    latest = metrics[-1]

    latency = latest["latency_ms"]
    baseline = latest["baseline_latency_ms"]
    status_code = latest["status_code"]

    findings = []

    if latency > baseline:
        increase_percent = round(
            ((latency - baseline) / baseline) * 100,
            2,
        )

        findings.append(
            Finding(
                finding_id="METRIC-F-REAL-001",
                agent="metrics",
                category="METRICS",
                finding=(
                    "Real e-commerce API latency "
                    "increased significantly."
                ),
                value=f"{latency} ms",
                expected_value=f"Approximately {baseline} ms",
                evidence=[
                    Evidence(
                        source="ecommerce_api",
                        reference="order-api",
                        details=(
                            f"Real Order API latency was {latency} ms "
                            f"compared with the healthy baseline of "
                            f"{baseline} ms, an increase of "
                            f"{increase_percent}%."
                        ),
                    )
                ],
                confidence=0.98,
                severity="HIGH",
            )
        )

    if status_code is not None and status_code >= 500:
        findings.append(
            Finding(
                finding_id="METRIC-F-REAL-002",
                agent="metrics",
                category="METRICS",
                finding=(
                    "Real e-commerce Order API returned "
                    "a server error."
                ),
                value=f"HTTP {status_code}",
                expected_value="HTTP 2xx",
                evidence=[
                    Evidence(
                        source="ecommerce_api",
                        reference="order-api",
                        details=(
                            f"The real Order API returned HTTP "
                            f"{status_code} during the investigation."
                        ),
                    )
                ],
                confidence=0.97,
                severity="HIGH",
            )
        )

    confidence = (
        round(
            sum(finding.confidence for finding in findings)
            / len(findings),
            2,
        )
        if findings
        else 1.0
    )

    return AgentResult(
        agent="metrics",
        status=InvestigationStatus.SUCCESS,
        findings=findings,
        confidence=confidence,
    )


def investigate_metrics(incident: Incident) -> AgentResult:
    """
    Investigate metrics using the appropriate data source.

    Simulation incidents continue using the existing simulated
    metrics tool. Real e-commerce incidents use the live API
    metrics adapter.
    """

    # Real e-commerce incidents created by ecommerce_monitor.py
    # currently use this service/version/environment combination.
    #
    # The simulation path remains the default for incidents
    # generated by simulation.incident_generator.
    if incident.baseline_latency_ms == 320.0:
        return _investigate_ecommerce_metrics(incident)

    return _investigate_simulation_metrics(incident)