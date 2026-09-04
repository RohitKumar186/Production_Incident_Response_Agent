from TASK3.tools.log_search import search_logs
from TASK2.models.schemas import Finding, Evidence, AgentResult


def investigate_logs(incident):
    """
    Investigate application logs for the given incident.
    """

    service = incident.service["name"]

    try:
        tool_result = search_logs(service)

        if tool_result.status != "SUCCESS":
            return AgentResult(
                agent="logs",
                status="FAILED",
                findings=[],
                confidence=0.0
            )

        logs = tool_result.data

        timeout_logs = [
            log
            for log in logs
            if "timeout" in log.get("message", "").lower()
        ]

        if timeout_logs:
            finding = Finding(
                finding_id="F-001",
                agent="logs",
                category="LOGS",
                finding="Database timeout errors increased",
                value=f"{len(timeout_logs)} timeout errors found",
                expected_value="No significant database timeout errors",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs-001",
                        details="Database timeout errors detected in application logs"
                    )
                ],
                confidence=0.88,
                severity=incident.severity
            )

            return AgentResult(
                agent="logs",
                status="SUCCESS",
                findings=[finding],
                confidence=0.88
            )

        return AgentResult(
            agent="logs",
            status="SUCCESS",
            findings=[],
            confidence=0.90
        )

    except Exception:
        return AgentResult(
            agent="logs",
            status="FAILED",
            findings=[],
            confidence=0.0
        )