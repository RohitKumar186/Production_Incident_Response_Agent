from typing import Any


class DatabaseTool:
    """
    Read-only diagnostics for simulated databases.

    The tool exposes database evidence such as query plans,
    indexes, locks, connection pools, and replication state.
    """

    def __init__(self, infrastructure) -> None:
        self.infrastructure = infrastructure

    def inspect(self, database: str) -> dict[str, Any]:
        state = self.infrastructure.state.databases.get(database)

        if state is None:
            return {
                "error": f"Unknown database: {database}"
            }

        evidence = {
            "database": database,
            "status": state["status"],
            "query_plan": state.get("query_plan"),
            "index_status": state.get("index_status"),
            "lock_waits": state.get("lock_waits"),
            "connection_pool_used": state.get(
                "connection_pool_used"
            ),
            "connection_pool_size": state.get(
                "connection_pool_size"
            ),
            "replication_lag_ms": state.get(
                "replication_lag_ms"
            ),
            "query_latency_ms": state.get(
                "query_latency_ms"
            ),
        }

        return evidence