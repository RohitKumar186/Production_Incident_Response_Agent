from datetime import datetime, timezone


class LogsTool:
    """
    Generates diagnostic log evidence from the current
    simulated infrastructure state.

    Logs describe observable consequences of the current
    state.

    They do not expose the simulator's hidden root cause.
    """

    def __init__(self, infrastructure) -> None:
        self.infrastructure = infrastructure

    def _log(
        self,
        component: str,
        level: str,
        message: str,
    ) -> dict:

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": component,
            "level": level,
            "message": message,
        }

    def search(self, component: str) -> list[dict]:

        logs = []

        # ========================================================
        # SERVICES
        # ========================================================

        services = self.infrastructure.state.services

        if component in services:

            state = services[component]

            if state["status"] != "healthy":

                if state["error_rate"] > 5:

                    logs.append(
                        self._log(
                            component,
                            "ERROR",
                            (
                                "Elevated request failures detected; "
                                f"error_rate={state['error_rate']}%"
                            ),
                        )
                    )

                if state["latency_ms"] > 200:

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Request processing latency exceeded "
                                f"baseline; latency={state['latency_ms']}ms"
                            ),
                        )
                    )

                if state.get("request_queue", 0) > 25:

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Application request queue is growing; "
                                f"queue_depth={state['request_queue']}"
                            ),
                        )
                    )

                if state["cpu_percent"] > 75:

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Application CPU utilization is elevated; "
                                f"cpu={state['cpu_percent']}%"
                            ),
                        )
                    )

                if state["memory_percent"] > 80:

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Application memory utilization is elevated; "
                                f"memory={state['memory_percent']}%"
                            ),
                        )
                    )

        # ========================================================
        # DATABASES
        # ========================================================

        databases = self.infrastructure.state.databases

        if component in databases:

            state = databases[component]

            if state["status"] != "healthy":

                query_plan = state.get("query_plan")

                if query_plan not in (
                    None,
                    "indexed",
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Database query planner is using "
                                f"an inefficient plan: {query_plan}"
                            ),
                        )
                    )

                index_status = state.get("index_status")

                if index_status not in (
                    None,
                    "valid",
                ):

                    logs.append(
                        self._log(
                            component,
                            "ERROR",
                            (
                                "Database index health is abnormal; "
                                f"index_status={index_status}"
                            ),
                        )
                    )

                if state.get("lock_waits", 0) > 0:

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Database lock contention detected; "
                                f"lock_waits={state['lock_waits']}"
                            ),
                        )
                    )

                pool_used = state.get(
                    "connection_pool_used"
                )

                pool_size = state.get(
                    "connection_pool_size"
                )

                if (
                    pool_used is not None
                    and pool_size is not None
                    and pool_used >= pool_size
                ):

                    logs.append(
                        self._log(
                            component,
                            "ERROR",
                            (
                                "Database connection pool is exhausted; "
                                f"used={pool_used}, "
                                f"capacity={pool_size}"
                            ),
                        )
                    )

                replication_lag = state.get(
                    "replication_lag_ms"
                )

                if (
                    replication_lag is not None
                    and replication_lag > 100
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Database replication lag is elevated; "
                                f"lag={replication_lag}ms"
                            ),
                        )
                    )

                query_latency = state.get(
                    "query_latency_ms"
                )

                if (
                    query_latency is not None
                    and query_latency > 200
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Database query latency is elevated; "
                                f"query_latency={query_latency}ms"
                            ),
                        )
                    )

        # ========================================================
        # NETWORK
        # ========================================================

        network = self.infrastructure.state.network

        if component in network:

            state = network[component]

            if state["status"] != "healthy":

                packet_loss = state.get(
                    "packet_loss_percent"
                )

                if (
                    packet_loss is not None
                    and packet_loss > 0
                ):

                    logs.append(
                        self._log(
                            component,
                            "ERROR",
                            (
                                "Network packet loss detected; "
                                f"packet_loss={packet_loss}%"
                            ),
                        )
                    )

                dns_latency = state.get(
                    "dns_latency_ms"
                )

                if (
                    dns_latency is not None
                    and dns_latency > 50
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "DNS resolution latency increased; "
                                f"dns_latency={dns_latency}ms"
                            ),
                        )
                    )

                resets = state.get(
                    "connection_resets"
                )

                if (
                    resets is not None
                    and resets > 0
                ):

                    logs.append(
                        self._log(
                            component,
                            "ERROR",
                            (
                                "Network connection resets detected; "
                                f"resets={resets}"
                            ),
                        )
                    )

                latency = state.get(
                    "latency_ms"
                )

                if (
                    latency is not None
                    and latency > 50
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Network path latency increased; "
                                f"latency={latency}ms"
                            ),
                        )
                    )

        # ========================================================
        # INFRASTRUCTURE
        # ========================================================

        infrastructure = (
            self.infrastructure.state.infrastructure
        )

        if component in infrastructure:

            state = infrastructure[component]

            if state["status"] != "healthy":

                cpu = state.get("cpu_percent")

                if cpu is not None and cpu > 80:

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Infrastructure CPU utilization "
                                f"is high; cpu={cpu}%"
                            ),
                        )
                    )

                memory = state.get(
                    "memory_percent"
                )

                if (
                    memory is not None
                    and memory > 80
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Infrastructure memory utilization "
                                f"is high; memory={memory}%"
                            ),
                        )
                    )

                disk = state.get(
                    "disk_percent"
                )

                if (
                    disk is not None
                    and disk > 80
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Infrastructure disk utilization "
                                f"is high; disk={disk}%"
                            ),
                        )
                    )

                restarts = state.get(
                    "pods_restarting"
                )

                if (
                    restarts is not None
                    and restarts > 0
                ):

                    logs.append(
                        self._log(
                            component,
                            "ERROR",
                            (
                                "Workloads are restarting repeatedly; "
                                f"pod_restarts={restarts}"
                            ),
                        )
                    )

                queue_depth = state.get(
                    "queue_depth"
                )

                if (
                    queue_depth is not None
                    and queue_depth > 50
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Work queue depth is elevated; "
                                f"queue_depth={queue_depth}"
                            ),
                        )
                    )

                available_workers = state.get(
                    "available_workers"
                )

                total_workers = state.get(
                    "total_workers"
                )

                if (
                    available_workers is not None
                    and total_workers is not None
                    and available_workers < total_workers
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Worker capacity is reduced; "
                                f"available={available_workers}, "
                                f"total={total_workers}"
                            ),
                        )
                    )

        # ========================================================
        # DEPENDENCIES
        # ========================================================

        dependencies = (
            self.infrastructure.state.dependencies
        )

        if component in dependencies:

            state = dependencies[component]

            if state["status"] != "healthy":

                error_rate = state.get(
                    "error_rate"
                )

                if (
                    error_rate is not None
                    and error_rate > 5
                ):

                    logs.append(
                        self._log(
                            component,
                            "ERROR",
                            (
                                "Dependency request failures detected; "
                                f"error_rate={error_rate}%"
                            ),
                        )
                    )

                latency = state.get(
                    "latency_ms"
                )

                if (
                    latency is not None
                    and latency > 100
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Dependency response latency increased; "
                                f"latency={latency}ms"
                            ),
                        )
                    )

                queue_depth = state.get(
                    "queue_depth"
                )

                if (
                    queue_depth is not None
                    and queue_depth > 50
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Dependency queue depth increased; "
                                f"queue_depth={queue_depth}"
                            ),
                        )
                    )

                consumer_lag = state.get(
                    "consumer_lag"
                )

                if (
                    consumer_lag is not None
                    and consumer_lag > 0
                ):

                    logs.append(
                        self._log(
                            component,
                            "WARN",
                            (
                                "Dependency consumer lag detected; "
                                f"consumer_lag={consumer_lag}"
                            ),
                        )
                    )

        return logs