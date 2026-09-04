from TASK3.tools.metrics_reader import read_metrics
from TASK2.models.schemas import Finding, Evidence, AgentResult


def investigate_metrics(incident):
    """
    Investigate service performance metrics.
    """

    service = incident.service["name"]

    try:
        tool_result = read_metrics(service)

        if tool_result.status != "SUCCESS":
            return AgentResult(
                agent="metrics",
                status="FAILED",
                findings=[],
                confidence=0.0
            )

        metrics = tool_result.data

        baseline = metrics["latency"]["baseline_ms"]
        current = metrics["latency"]["current_ms"]

        increase_percent = ((current - baseline) / baseline) * 100

        if increase_percent > 0:
            finding = Finding(
                finding_id="F-002",
                agent="metrics",
                category="METRICS",
                finding="API latency increased",
                value=f"{current} ms",
                expected_value=f"{baseline} ms",
                evidence=[
                    Evidence(
                        source="metrics",
                        reference="metric-order-api-latency",
                        details=f"Latency increased by {increase_percent:.0f}%"
                    )
                ],
                confidence=0.96,
                severity=incident.severity
            )

            return AgentResult(
                agent="metrics",
                status="SUCCESS",
                findings=[finding],
                confidence=0.96
            )

        return AgentResult(
            agent="metrics",
            status="SUCCESS",
            findings=[],
            confidence=0.90
        )

    except Exception:
        return AgentResult(
            agent="metrics",
            status="FAILED",
            findings=[],
            confidence=0.0
        )