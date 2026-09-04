from TASK3.tools.network_checker import check_network
from TASK2.models.schemas import Finding, Evidence, AgentResult


def investigate_network(incident):
    """
    Investigate network health for the affected service.
    """

    service = incident.service["name"]

    try:
        tool_result = check_network(service)

        if tool_result.status != "SUCCESS":
            return AgentResult(
                agent="network",
                status="FAILED",
                findings=[],
                confidence=0.0
            )

        network = tool_result.data

        latency = network["latency_ms"]
        expected_latency = network["expected_latency_ms"]
        packet_loss = network["packet_loss_percent"]
        expected_packet_loss = network["expected_packet_loss_percent"]

        if (
            latency <= expected_latency
            and packet_loss <= expected_packet_loss
        ):
            finding = Finding(
                finding_id="F-004",
                agent="network",
                category="NETWORK",
                finding="Network latency is within normal range",
                value=f"{latency} ms",
                expected_value=f"< {expected_latency} ms",
                evidence=[
                    Evidence(
                        source="network_metrics",
                        reference="network-001",
                        details="Network latency and packet loss are within normal limits"
                    )
                ],
                confidence=0.94,
                severity="LOW"
            )

            return AgentResult(
                agent="network",
                status="SUCCESS",
                findings=[finding],
                confidence=0.94
            )

        finding = Finding(
            finding_id="F-004",
            agent="network",
            category="NETWORK",
            finding="Network performance is abnormal",
            value=f"Latency: {latency} ms, Packet loss: {packet_loss}%",
            expected_value=f"Latency < {expected_latency} ms",
            evidence=[
                Evidence(
                    source="network_metrics",
                    reference="network-001",
                    details="Network performance exceeded expected limits"
                )
            ],
            confidence=0.94,
            severity=incident.severity
        )

        return AgentResult(
            agent="network",
            status="SUCCESS",
            findings=[finding],
            confidence=0.94
        )

    except Exception:
        return AgentResult(
            agent="network",
            status="FAILED",
            findings=[],
            confidence=0.0
        )