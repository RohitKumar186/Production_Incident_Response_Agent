from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import json

from models.schemas import (
    AgentResult,
    Evidence,
    Finding,
    Incident,
    InvestigationStatus,
)
from tools.database_tool import query_database


ECOMMERCE_DB_URL = "http://localhost:8080/incident/database"


def _investigate_simulation_database(incident: Incident) -> AgentResult:
    """Investigate database data from the existing simulation."""

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


def _investigate_ecommerce_database(incident: Incident) -> AgentResult:
    """Investigate the real e-commerce application's database."""

    try:
        with urlopen(ECOMMERCE_DB_URL, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

    except HTTPError as error:
        return AgentResult(
            agent="database",
            status=InvestigationStatus.FAILED,
            error={
                "code": "ECOMMERCE_DB_HTTP_ERROR",
                "message": f"E-commerce DB endpoint returned HTTP {error.code}.",
                "retryable": True,
            },
        )

    except URLError as error:
        return AgentResult(
            agent="database",
            status=InvestigationStatus.FAILED,
            error={
                "code": "ECOMMERCE_DB_UNAVAILABLE",
                "message": f"Could not connect to e-commerce DB endpoint: {error}",
                "retryable": True,
            },
        )

    except Exception as error:
        return AgentResult(
            agent="database",
            status=InvestigationStatus.FAILED,
            error={
                "code": "ECOMMERCE_DB_ERROR",
                "message": str(error),
                "retryable": True,
            },
        )

    findings = []

    status = data.get("status")
    query_latency = data.get("query_latency_ms")

    if status == "HEALTHY":
        findings.append(
            Finding(
                finding_id="DB-F-REAL-001",
                agent="database",
                category="DATABASE",
                finding="Real e-commerce database is healthy.",
                value=(
                    f"H2 database healthy; query latency "
                    f"{query_latency} ms"
                ),
                expected_value="Healthy database connectivity",
                evidence=[
                    Evidence(
                        source="ecommerce_database",
                        reference="/incident/database",
                        details=(
                            f"Database status: {status}; "
                            f"orders: {data.get('orders_count', 0)}; "
                            f"order items: {data.get('order_items_count', 0)}; "
                            f"diagnostic query latency: "
                            f"{query_latency} ms."
                        ),
                    )
                ],
                confidence=0.98,
                severity="LOW",
            )
        )

    else:
        findings.append(
            Finding(
                finding_id="DB-F-REAL-002",
                agent="database",
                category="DATABASE",
                finding="Real e-commerce database health check failed.",
                value=str(status),
                expected_value="HEALTHY",
                evidence=[
                    Evidence(
                        source="ecommerce_database",
                        reference="/incident/database",
                        details=json.dumps(data),
                    )
                ],
                confidence=0.98,
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


def investigate_database(incident: Incident) -> AgentResult:
    """
    Investigate database using the appropriate data source.

    Simulation incidents use simulated database data.
    Real e-commerce incidents use the live database diagnostics endpoint.
    """

    if incident.baseline_latency_ms == 320.0:
        return _investigate_ecommerce_database(incident)

    return _investigate_simulation_database(incident)