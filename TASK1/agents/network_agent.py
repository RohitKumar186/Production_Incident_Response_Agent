import json

from models.schemas import (
    AgentResult,
    Evidence,
    Finding,
    Incident,
    InvestigationStatus,
)
from tools.network_tool import get_network_metrics
from tools.ecommerce_network_tool import get_ecommerce_network_metrics


def _investigate_simulation_network(incident: Incident) -> AgentResult:
    """Investigate network health from simulation data."""

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


def _investigate_ecommerce_network(incident: Incident) -> AgentResult:
    """Investigate network connectivity to the real e-commerce app."""

    result = get_ecommerce_network_metrics()

    if result.get("latency_ms") is None:
        return AgentResult(
            agent="network",
            status=InvestigationStatus.FAILED,
            error={
                "code": "ECOMMERCE_NETWORK_UNAVAILABLE",
                "message": result.get(
                    "error",
                    "E-commerce application is unreachable.",
                ),
                "retryable": True,
            },
        )

    latency = result["latency_ms"]
    packet_loss = result["packet_loss_percent"]
    status = result["status"]

    if status == "HEALTHY":
        finding = Finding(
            finding_id="NET-F-REAL-001",
            agent="network",
            category="NETWORK",
            finding="Real e-commerce application is reachable.",
            value=f"{latency} ms latency, {packet_loss}% packet loss",
            expected_value="Reachable with 0% packet loss",
            evidence=[
                Evidence(
                    source="ecommerce_application",
                    reference="/incident/database",
                    details=(
                        f"Connectivity probe returned HTTP "
                        f"{result['status_code']} with "
                        f"{latency} ms response latency and "
                        f"{packet_loss}% packet loss."
                    ),
                )
            ],
            confidence=0.97,
            severity="LOW",
        )
    else:
        finding = Finding(
            finding_id="NET-F-REAL-002",
            agent="network",
            category="NETWORK",
            finding="Real e-commerce application connectivity is degraded.",
            value=f"{latency} ms latency, {packet_loss}% packet loss",
            expected_value="Healthy connectivity",
            evidence=[
                Evidence(
                    source="ecommerce_application",
                    reference="/incident/database",
                    details=json.dumps(result),
                )
            ],
            confidence=0.90,
            severity="MEDIUM",
        )

    return AgentResult(
        agent="network",
        status=InvestigationStatus.SUCCESS,
        findings=[finding],
        confidence=finding.confidence,
    )


def investigate_network(incident: Incident) -> AgentResult:
    """
    Investigate network using the appropriate data source.

    Simulation incidents use simulated network data.
    Real e-commerce incidents use the live application probe.
    """

    if incident.baseline_latency_ms == 320.0:
        return _investigate_ecommerce_network(incident)

    return _investigate_simulation_network(incident)