from models.schemas import AgentResult, Evidence, Finding, Incident, InvestigationStatus
from tools.database_tool import query_database


def investigate_database(incident: Incident) -> AgentResult:
    """
    Investigate database query performance for the given incident.
    """

    records = query_database(
        incident_id=incident.incident_id,
    )

    if not records:
        return AgentResult(
            agent="database",
            status=InvestigationStatus.FAILED,
            error={
                "code": "NO_DATABASE_DATA",
                "message": "No database records were found for the incident.",
                "retryable": False,
            },
        )

    slow_queries = [
        record
        for record in records
        if record.get("execution_time_ms", 0)
        > record.get("expected_execution_time_ms", 0)
    ]

    findings = []

    if slow_queries:
        max_query = max(
            slow_queries,
            key=lambda record: record["execution_time_ms"],
        )

        findings.append(
            Finding(
                finding_id="DB-F-001",
                agent="database",
                category="DATABASE",
                finding="Database query execution time increased significantly.",
                value=f"{max_query['execution_time_ms']} ms",
                expected_value=(
                    f"< {max_query['expected_execution_time_ms']} ms"
                ),
                evidence=[
                    Evidence(
                        source="database_query_data",
                        reference=record["query_id"],
                        details=(
                            f"Query execution time: "
                            f"{record['execution_time_ms']} ms; "
                            f"status: {record['status']}"
                        ),
                    )
                    for record in slow_queries
                ],
                confidence=0.91,
                severity="HIGH",
            )
        )

    timeout_risk_queries = [
        record
        for record in records
        if record.get("status") == "TIMEOUT_RISK"
    ]

    if timeout_risk_queries:
        findings.append(
            Finding(
                finding_id="DB-F-002",
                agent="database",
                category="DATABASE",
                finding="Multiple database queries are at risk of timing out.",
                value=f"{len(timeout_risk_queries)} queries",
                expected_value="No timeout-risk queries",
                evidence=[
                    Evidence(
                        source="database_query_data",
                        reference=record["query_id"],
                        details=(
                            f"Query status is {record['status']} "
                            f"with execution time "
                            f"{record['execution_time_ms']} ms."
                        ),
                    )
                    for record in timeout_risk_queries
                ],
                confidence=0.94,
                severity="HIGH",
            )
        )

    return AgentResult(
        agent="database",
        status=InvestigationStatus.SUCCESS,
        findings=findings,
        confidence=max(
            (finding.confidence for finding in findings),
            default=0.0,
        ),
    )