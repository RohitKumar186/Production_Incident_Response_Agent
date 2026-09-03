from models.schemas import AgentResult, Evidence, Finding, Incident, InvestigationStatus
from tools.log_tool import search_logs


def investigate_logs(incident: Incident) -> AgentResult:
    """
    Investigate application logs for the given incident.
    """

    logs = search_logs(
        incident_id=incident.incident_id,
        service=incident.service_name,
    )

    if not logs:
        return AgentResult(
            agent="logs",
            status=InvestigationStatus.FAILED,
            error={
                "code": "NO_LOG_DATA",
                "message": "No logs were found for the incident.",
                "retryable": False,
            },
        )

    error_logs = [
        log for log in logs
        if log.get("level") == "ERROR"
    ]

    database_logs = [
        log for log in logs
        if "database" in log.get("message", "").lower()
    ]

    findings = []

    if error_logs:
        findings.append(
            Finding(
                finding_id="LOG-F-001",
                agent="logs",
                category="LOGS",
                finding="Database-related errors increased during the incident.",
                value=f"{len(error_logs)} error logs found",
                expected_value="No significant database errors",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs.json",
                        details=log["message"],
                    )
                    for log in database_logs
                ],
                confidence=0.88,
                severity="HIGH",
            )
        )

    if database_logs:
        findings.append(
            Finding(
                finding_id="LOG-F-002",
                agent="logs",
                category="DATABASE",
                finding="Database timeout and slow-query messages are present.",
                value=f"{len(database_logs)} database-related log entries",
                expected_value="No database timeout errors",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs.json",
                        details=log["message"],
                    )
                    for log in database_logs
                ],
                confidence=0.91,
                severity="HIGH",
            )
        )

    return AgentResult(
        agent="logs",
        status=InvestigationStatus.SUCCESS,
        findings=findings,
        confidence=max(
            (finding.confidence for finding in findings),
            default=0.0,
        ),
    )