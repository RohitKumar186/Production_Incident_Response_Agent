from typing import Any


class MetricsTool:
    """
    Read-only metrics tool for the simulated infrastructure.

    Metrics are observations of the current simulated state.
    This tool does not modify the infrastructure.
    """

    def __init__(self, infrastructure) -> None:
        self.infrastructure = infrastructure

    def service_metrics(self, service: str) -> dict[str, Any]:
        state = self.infrastructure.state.services.get(service)

        if state is None:
            return {"error": f"Unknown service: {service}"}

        return {
            "component": service,
            "status": state["status"],
            "replicas": state["replicas"],
            "cpu_percent": state["cpu_percent"],
            "memory_percent": state["memory_percent"],
            "error_rate": state["error_rate"],
            "latency_ms": state["latency_ms"],
            "request_queue": state.get("request_queue"),
            "dependency_timeout_ms": state.get(
                "dependency_timeout_ms"
            ),
        }

    def database_metrics(self, database: str) -> dict[str, Any]:
        state = self.infrastructure.state.databases.get(database)

        if state is None:
            return {"error": f"Unknown database: {database}"}

        return {
            "component": database,
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
            "eviction_rate": state.get("eviction_rate"),
            "memory_percent": state.get("memory_percent"),
        }

    def network_metrics(self, component: str) -> dict[str, Any]:
        state = self.infrastructure.state.network.get(component)

        if state is None:
            return {"error": f"Unknown network component: {component}"}

        return {
            "component": component,
            "status": state["status"],
            "packet_loss_percent": state.get(
                "packet_loss_percent"
            ),
            "latency_ms": state.get("latency_ms"),
            "dns_latency_ms": state.get("dns_latency_ms"),
            "connection_resets": state.get(
                "connection_resets"
            ),
        }

    def infrastructure_metrics(
        self,
        component: str,
    ) -> dict[str, Any]:

        state = self.infrastructure.state.infrastructure.get(
            component
        )

        if state is None:
            return {
                "error": (
                    f"Unknown infrastructure component: {component}"
                )
            }

        return {
            "component": component,
            "status": state["status"],
            "cpu_percent": state.get("cpu_percent"),
            "memory_percent": state.get("memory_percent"),
            "disk_percent": state.get("disk_percent"),
            "pods_restarting": state.get(
                "pods_restarting"
            ),
            "queue_depth": state.get("queue_depth"),
            "available_workers": state.get(
                "available_workers"
            ),
            "total_workers": state.get("total_workers"),
        }

    def dependency_metrics(
        self,
        dependency: str,
    ) -> dict[str, Any]:

        state = self.infrastructure.state.dependencies.get(
            dependency
        )

        if state is None:
            return {
                "error": (
                    f"Unknown dependency: {dependency}"
                )
            }

        return {
            "component": dependency,
            "status": state["status"],
            "latency_ms": state.get("latency_ms"),
            "error_rate": state.get("error_rate"),
            "queue_depth": state.get("queue_depth"),
            "consumer_lag": state.get(
                "consumer_lag"
            ),
        }