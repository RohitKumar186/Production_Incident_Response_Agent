from TASK3.tools.log_search import search_logs
from TASK2.models.schemas import Finding, Evidence, AgentResult


def investigate_logs(incident):
    """
    Investigate application logs for the given incident.

    Logs always return one diagnostic finding.
    The category is based on the actual incident type.
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

        messages = [
            log.get("message", "").lower()
            for log in logs
        ]

        all_text = " ".join(messages)

        # ---------------------------------------------
        # DATABASE
        # ---------------------------------------------

        if any(
            word in all_text
            for word in [
                "database",
                "query timeout",
                "slow database",
            ]
        ):
            finding = Finding(
                finding_id="F-001",
                agent="logs",
                category="LOGS",
                finding="Database timeout errors increased",
                value="Database timeout errors detected",
                expected_value="No significant database timeout errors",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs-001",
                        details=(
                            "Database timeout and slow query "
                            "messages detected in application logs"
                        )
                    )
                ],
                confidence=0.88,
                severity=incident.severity
            )

        # ---------------------------------------------
        # NETWORK
        # ---------------------------------------------

        elif any(
            word in all_text
            for word in [
                "network latency",
                "packet loss",
                "network connectivity",
            ]
        ):
            finding = Finding(
                finding_id="F-001",
                agent="logs",
                category="NETWORK",
                finding="Network degradation detected in logs",
                value="Network latency or packet loss messages detected",
                expected_value="No network degradation",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs-001",
                        details=(
                            "Network latency and connectivity "
                            "degradation detected in application logs"
                        )
                    )
                ],
                confidence=0.86,
                severity=incident.severity
            )

        # ---------------------------------------------
        # APPLICATION
        # ---------------------------------------------

        elif any(
            word in all_text
            for word in [
                "http 500",
                "application exception",
                "application errors",
                "application layer",
            ]
        ):
            finding = Finding(
                finding_id="F-001",
                agent="logs",
                category="APPLICATION",
                finding="Application errors detected in logs",
                value="Application errors or exceptions detected",
                expected_value="No application errors",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs-001",
                        details=(
                            "Application errors and exceptions "
                            "detected in application logs"
                        )
                    )
                ],
                confidence=0.87,
                severity=incident.severity
            )

        # ---------------------------------------------
        # INFRASTRUCTURE
        # ---------------------------------------------

        elif any(
            word in all_text
            for word in [
                "infrastructure cpu",
                "system resources",
                "resource pressure",
                "resource utilization",
                "high resource usage",
            ]
        ):
            finding = Finding(
                finding_id="F-001",
                agent="logs",
                category="INFRASTRUCTURE",
                finding="Infrastructure resource pressure detected",
                value="High infrastructure resource utilization",
                expected_value="Normal resource utilization",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs-001",
                        details=(
                            "Infrastructure resource pressure "
                            "detected in application logs"
                        )
                    )
                ],
                confidence=0.87,
                severity=incident.severity
            )

        # ---------------------------------------------
        # FALLBACK
        # ---------------------------------------------

        else:
            finding = Finding(
                finding_id="F-001",
                agent="logs",
                category="LOGS",
                finding="No abnormal log pattern detected",
                value="Logs inspected successfully",
                expected_value="No critical errors",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs-001",
                        details="No critical abnormal log pattern detected"
                    )
                ],
                confidence=0.90,
                severity="LOW"
            )

        return AgentResult(
            agent="logs",
            status="SUCCESS",
            findings=[finding],
            confidence=finding.confidence
        )

    except Exception:
        return AgentResult(
            agent="logs",
            status="FAILED",
            findings=[],
            confidence=0.0
        )