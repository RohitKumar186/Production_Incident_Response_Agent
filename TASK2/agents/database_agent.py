from TASK3.tools.database_reader import read_database
from TASK2.models.schemas import Finding, Evidence, AgentResult


def investigate_database(incident):
    """
    Investigate database query performance.
    """

    try:
        tool_result = read_database()

        if tool_result.status != "SUCCESS":
            return AgentResult(
                agent="database",
                status="FAILED",
                findings=[],
                confidence=0.0
            )

        database = tool_result.data

        slow_queries = [
            query
            for query in database.get("queries", [])
            if query["execution_time_ms"] > query["expected_time_ms"]
        ]

        if slow_queries:
            slow_query = max(
                slow_queries,
                key=lambda query: query["execution_time_ms"]
            )

            execution_time = slow_query["execution_time_ms"]
            expected_time = slow_query["expected_time_ms"]

            finding = Finding(
                finding_id="F-003",
                agent="database",
                category="DATABASE",
                finding="Orders query is executing slowly",
                value=f"{execution_time / 1000:.1f} seconds",
                expected_value=f"< {expected_time} ms",
                evidence=[
                    Evidence(
                        source="database",
                        reference=slow_query["query_id"],
                        details="Query execution time is above the expected threshold"
                    )
                ],
                confidence=0.91,
                severity=incident.severity
            )

            return AgentResult(
                agent="database",
                status="SUCCESS",
                findings=[finding],
                confidence=0.91
            )

        return AgentResult(
            agent="database",
            status="SUCCESS",
            findings=[],
            confidence=0.90
        )

    except Exception:
        return AgentResult(
            agent="database",
            status="FAILED",
            findings=[],
            confidence=0.0
        )