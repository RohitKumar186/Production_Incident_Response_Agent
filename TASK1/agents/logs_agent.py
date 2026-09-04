from models.schemas import (
    AgentResult,
    Evidence,
    Finding,
    Incident,
    InvestigationStatus,
)
from tools.log_tool import search_logs
from tools.ecommerce_log_tool import search_ecommerce_logs


def _investigate_simulation_logs(incident: Incident) -> AgentResult:
    """Investigate logs from the existing simulation data."""

    logs = search_logs(
        service=incident.service_name,
        incident_id=incident.incident_id,
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

    findings = []

    error_logs = [
        log for log in logs
        if log.get("level") == "ERROR"
    ]

    if error_logs:
        findings.append(
            Finding(
                finding_id="LOG-F-001",
                agent="logs",
                category="APPLICATION",
                finding="Application errors detected.",
                value=f"{len(error_logs)} error logs",
                expected_value="No application errors",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs.json",
                        details=(
                            error_logs[0].get(
                                "message",
                                "Application error detected.",
                            )
                        ),
                    )
                ],
                confidence=0.94,
                severity="HIGH",
            )
        )

    database_errors = [
        log
        for log in error_logs
        if "database" in log.get("message", "").lower()
        or "db" in log.get("message", "").lower()
        or "query" in log.get("message", "").lower()
    ]

    if database_errors:
        findings.append(
            Finding(
                finding_id="LOG-F-002",
                agent="logs",
                category="DATABASE",
                finding="Database-related errors detected in logs.",
                value=f"{len(database_errors)} database errors",
                expected_value="No database errors",
                evidence=[
                    Evidence(
                        source="application_logs",
                        reference="logs.json",
                        details=(
                            database_errors[0].get(
                                "message",
                                "Database-related error detected.",
                            )
                        ),
                    )
                ],
                confidence=0.92,
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
        agent="logs",
        status=InvestigationStatus.SUCCESS,
        findings=findings,
        confidence=confidence,
    )


def _investigate_ecommerce_logs(
    incident: Incident,
) -> AgentResult:
    """Investigate logs from the real e-commerce application."""

    logs = search_ecommerce_logs(
        service=incident.service_name,
    )

    if not logs:
        return AgentResult(
            agent="logs",
            status=InvestigationStatus.FAILED,
            error={
                "code": "NO_ECOMMERCE_LOG_DATA",
                "message": (
                    "No logs were found in the real e-commerce "
                    "application log."
                ),
                "retryable": True,
            },
        )

    findings = []

    # Look for HTTP request activity for the affected endpoint.
    request_logs = [
        log
        for log in logs
        if 'POST "/order"' in log["message"]
    ]

    if request_logs:
        findings.append(
            Finding(
                finding_id="LOG-F-REAL-001",
                agent="logs",
                category="APPLICATION",
                finding=(
                    "Real e-commerce Order API request "
                    "activity detected."
                ),
                value=f"{len(request_logs)} request log entries",
                expected_value="Normal request processing",
                evidence=[
                    Evidence(
                        source="ecommerce_application",
                        reference="ecommerce-application.log",
                        details=request_logs[-1]["message"],
                    )
                ],
                confidence=0.95,
                severity="HIGH",
            )
        )

    # Look for the controller mapping entry. This is useful because
    # the latency fault occurs before normal order processing.
    controller_logs = [
        log
        for log in logs
        if "OrderController#place" in log["message"]
    ]

    if controller_logs:
        findings.append(
            Finding(
                finding_id="LOG-F-REAL-002",
                agent="logs",
                category="APPLICATION",
                finding=(
                    "Order API request reached the "
                    "OrderController."
                ),
                value="OrderController#place",
                expected_value="Normal request processing",
                evidence=[
                    Evidence(
                        source="ecommerce_application",
                        reference="ecommerce-application.log",
                        details=controller_logs[-1]["message"],
                    )
                ],
                confidence=0.94,
                severity="MEDIUM",
            )
        )

    # The real log does not currently contain our internal incident ID,
    # so we do not pretend that it does.
    return AgentResult(
        agent="logs",
        status=InvestigationStatus.SUCCESS,
        findings=findings,
        confidence=(
            round(
                sum(finding.confidence for finding in findings)
                / len(findings),
                2,
            )
            if findings
            else 0.0
        ),
    )


def investigate_logs(incident: Incident) -> AgentResult:
    """
    Investigate logs using the appropriate data source.

    Simulation incidents use the existing simulated log tool.
    Real e-commerce incidents use the real application log adapter.
    """

    # Real e-commerce incidents currently use a 320 ms baseline.
    if incident.baseline_latency_ms == 320.0:
        return _investigate_ecommerce_logs(incident)

    return _investigate_simulation_logs(incident)