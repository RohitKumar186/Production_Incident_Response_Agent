import random
import uuid
from datetime import datetime, timezone
from typing import Any

from models.fault import SimulatedFault
from models.incident import Incident
from simulator.infrastructure import SimulatedInfrastructure


INCIDENT_TYPES = (
    "DATABASE",
    "APPLICATION",
    "NETWORK",
    "INFRASTRUCTURE",
    "API_LATENCY",
    "HIGH_ERROR_RATE",
)


class IncidentGenerator:
    """
    Generates varied incidents by combining randomized dimensions
    and applying actual faults to the simulated infrastructure.

    The generator does not select from a fixed list of complete
    scenarios.

    Instead it independently randomizes:
        - incident type
        - affected component
        - fault mechanism
        - fault parameters
        - severity/magnitude

    The resulting state becomes the source of investigation evidence.
    """

    def __init__(
        self,
        infrastructure: SimulatedInfrastructure,
        seed: int | None = None,
    ) -> None:
        self.infrastructure = infrastructure
        self.random = random.Random(seed)

    def generate(self) -> Incident:
        """
        Generate one random incident and apply its underlying
        fault to the simulated infrastructure.
        """

        incident_type = self.random.choice(INCIDENT_TYPES)

        if incident_type == "DATABASE":
            return self._generate_database_incident()

        if incident_type == "APPLICATION":
            return self._generate_application_incident()

        if incident_type == "NETWORK":
            return self._generate_network_incident()

        if incident_type == "INFRASTRUCTURE":
            return self._generate_infrastructure_incident()

        if incident_type == "API_LATENCY":
            return self._generate_api_latency_incident()

        return self._generate_error_rate_incident()

    def _set_fault(
        self,
        fault_domain: str,
        mechanism: str,
        component: str,
        parameters: dict[str, Any],
        description: str,
    ) -> None:
        """
        Store simulator-only fault information.
        """

        self.infrastructure.state.active_fault = SimulatedFault(
            fault_id=f"FAULT-{uuid.uuid4().hex[:8].upper()}",
            fault_domain=fault_domain,
            mechanism=mechanism,
            component=component,
            parameters=parameters,
            description=description,
        )

    def _base_incident(
        self,
        incident_type: str,
        title: str,
        description: str,
        component: str,
        stack: list[str],
        symptoms: list[str],
        abnormal_state: dict[str, Any],
        root_cause: str,
        fault_domain: str,
        fault_mechanism: str,
    ) -> Incident:

        return Incident(
            incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now(timezone.utc),
            incident_type=incident_type,
            title=title,
            description=description,
            affected_component=component,
            technology_stack=stack,
            symptoms=symptoms,
            abnormal_state=abnormal_state,
            root_cause=root_cause,
            fault_domain=fault_domain,
            fault_mechanism=fault_mechanism,
        )

    # ============================================================
    # DATABASE
    # ============================================================

    def _generate_database_incident(self) -> Incident:

        database = self.random.choice(
            list(self.infrastructure.state.databases.keys())
        )

        db = self.infrastructure.state.databases[database]

        mechanism = self.random.choice(
            [
                "query_plan",
                "index",
                "locks",
                "connection_pool",
                "replication",
            ]
        )

        if mechanism == "query_plan":

            plan = self.random.choice(
                [
                    "full_scan",
                    "nested_loop",
                    "inefficient_join",
                ]
            )

            db["query_plan"] = plan
            db["query_latency_ms"] = self.random.randint(300, 1200)
            db["status"] = "degraded"

            self._set_fault(
                "DATABASE",
                "query_plan",
                database,
                {
                    "query_plan": plan,
                    "query_latency_ms": db["query_latency_ms"],
                },
                f"An inefficient {plan} query plan is being used.",
            )

            return self._base_incident(
                "DATABASE",
                f"Database query performance degradation on {database}",
                "Database queries are taking significantly longer than baseline.",
                database,
                [
                    "PostgreSQL",
                    "SQL",
                    "query planner",
                ],
                [
                    "query latency increased",
                    "slow queries detected",
                    "database query plan changed",
                ],
                {
                    "query_plan": db["query_plan"],
                    "query_latency_ms": db["query_latency_ms"],
                    "status": db["status"],
                },
                f"An inefficient {plan} query plan is being used.",
                "DATABASE",
                "query_plan",
            )

        if mechanism == "index":

            index_status = self.random.choice(
                [
                    "missing",
                    "invalid",
                    "unused",
                ]
            )

            db["index_status"] = index_status
            db["query_plan"] = "full_scan"
            db["query_latency_ms"] = self.random.randint(250, 1000)
            db["status"] = "degraded"

            self._set_fault(
                "DATABASE",
                "index",
                database,
                {
                    "index_status": index_status,
                    "query_plan": db["query_plan"],
                },
                f"The required database index is {index_status}.",
            )

            return self._base_incident(
                "DATABASE",
                f"Database index issue on {database}",
                "A frequently accessed query is no longer using an effective index.",
                database,
                [
                    "PostgreSQL",
                    "SQL",
                    "B-tree indexes",
                ],
                [
                    "query latency increased",
                    "sequential scans detected",
                    "database load increased",
                ],
                {
                    "index_status": db["index_status"],
                    "query_plan": db["query_plan"],
                    "query_latency_ms": db["query_latency_ms"],
                    "status": db["status"],
                },
                f"The required database index is {index_status}.",
                "DATABASE",
                "index",
            )

        if mechanism == "locks":

            lock_waits = self.random.randint(20, 150)

            db["lock_waits"] = lock_waits
            db["query_latency_ms"] = self.random.randint(200, 900)
            db["status"] = "degraded"

            self._set_fault(
                "DATABASE",
                "lock_contention",
                database,
                {
                    "lock_waits": lock_waits,
                },
                "Concurrent transactions are causing excessive lock contention.",
            )

            return self._base_incident(
                "DATABASE",
                f"Database lock contention on {database}",
                "Concurrent transactions are waiting on database locks.",
                database,
                [
                    "PostgreSQL",
                    "SQL",
                    "transactions",
                ],
                [
                    "lock wait time increased",
                    "transaction latency increased",
                    "queries are waiting",
                ],
                {
                    "lock_waits": db["lock_waits"],
                    "query_latency_ms": db["query_latency_ms"],
                    "status": db["status"],
                },
                "Concurrent transactions are causing excessive lock contention.",
                "DATABASE",
                "lock_contention",
            )

        if mechanism == "connection_pool":

            db["connection_pool_used"] = db["connection_pool_size"]
            db["query_latency_ms"] = self.random.randint(150, 800)
            db["status"] = "degraded"

            self._set_fault(
                "DATABASE",
                "connection_pool_exhaustion",
                database,
                {
                    "connection_pool_used": db["connection_pool_used"],
                    "connection_pool_size": db["connection_pool_size"],
                },
                "The database connection pool has reached its configured capacity.",
            )

            return self._base_incident(
                "DATABASE",
                f"Database connection pool exhaustion on {database}",
                "Application requests are unable to obtain database connections quickly.",
                database,
                [
                    "PostgreSQL",
                    "connection pooling",
                    "TCP",
                ],
                [
                    "connection acquisition delays",
                    "database requests timing out",
                    "pool utilization at capacity",
                ],
                {
                    "connection_pool_used": db["connection_pool_used"],
                    "connection_pool_size": db["connection_pool_size"],
                    "query_latency_ms": db["query_latency_ms"],
                    "status": db["status"],
                },
                "The database connection pool has reached its configured capacity.",
                "DATABASE",
                "connection_pool_exhaustion",
            )

        lag = self.random.randint(500, 5000)

        db["replication_lag_ms"] = lag
        db["status"] = "degraded"

        self._set_fault(
            "DATABASE",
            "replication_lag",
            database,
            {
                "replication_lag_ms": lag,
            },
            "Database replication is experiencing sustained lag.",
        )

        return self._base_incident(
            "DATABASE",
            f"Database replication lag on {database}",
            "The database replica is falling behind the primary.",
            database,
            [
                "PostgreSQL",
                "streaming replication",
            ],
            [
                "replication lag increased",
                "replica freshness degraded",
                "read consistency affected",
            ],
            {
                "replication_lag_ms": db["replication_lag_ms"],
                "status": db["status"],
            },
            "Database replication is experiencing sustained lag.",
            "DATABASE",
            "replication_lag",
        )

    # ============================================================
    # APPLICATION
    # ============================================================

    def _generate_application_incident(self) -> Incident:

        service = self.random.choice(
            list(self.infrastructure.state.services.keys())
        )

        state = self.infrastructure.state.services[service]

        mechanism = self.random.choice(
            [
                "configuration",
                "thread_pool",
                "memory_pressure",
                "dependency_timeout",
            ]
        )

        state["status"] = "degraded"

        if mechanism == "configuration":

            config = self.random.choice(
                [
                    "feature_flag",
                    "timeout",
                    "connection_limit",
                ]
            )

            state["error_rate"] = round(
                self.random.uniform(3, 15),
                2,
            )

            self._set_fault(
                "APPLICATION",
                "configuration",
                service,
                {
                    "configuration": config,
                },
                f"An abnormal {config} configuration was applied.",
            )

            return self._base_incident(
                "APPLICATION",
                f"Application configuration failure on {service}",
                f"{service} is operating with an abnormal runtime configuration.",
                service,
                [
                    "Python",
                    "REST",
                    "configuration management",
                ],
                [
                    "application behavior changed",
                    "request failures increased",
                    "runtime configuration differs from baseline",
                ],
                {
                    "configuration": config,
                    "error_rate": state["error_rate"],
                    "status": state["status"],
                },
                f"An abnormal {config} configuration was applied.",
                "APPLICATION",
                "configuration",
            )

        if mechanism == "thread_pool":

            state["cpu_percent"] = self.random.randint(75, 95)
            state["latency_ms"] = self.random.randint(250, 800)
            state["request_queue"] = self.random.randint(50, 500)

            self._set_fault(
                "APPLICATION",
                "thread_pool_saturation",
                service,
                {
                    "cpu_percent": state["cpu_percent"],
                    "request_queue": state["request_queue"],
                },
                "The application request-processing pool is saturated.",
            )

            return self._base_incident(
                "APPLICATION",
                f"Application thread saturation on {service}",
                f"{service} is experiencing request-processing contention.",
                service,
                [
                    "Python",
                    "REST",
                    "thread pool",
                ],
                [
                    "request queue increased",
                    "application latency increased",
                    "CPU utilization increased",
                ],
                {
                    "cpu_percent": state["cpu_percent"],
                    "latency_ms": state["latency_ms"],
                    "request_queue": state["request_queue"],
                    "status": state["status"],
                },
                "The application request-processing pool is saturated.",
                "APPLICATION",
                "thread_pool_saturation",
            )

        if mechanism == "memory_pressure":

            state["memory_percent"] = self.random.randint(85, 98)
            state["latency_ms"] = self.random.randint(180, 700)

            self._set_fault(
                "APPLICATION",
                "memory_pressure",
                service,
                {
                    "memory_percent": state["memory_percent"],
                },
                "The application process is under sustained memory pressure.",
            )

            return self._base_incident(
                "APPLICATION",
                f"Application memory pressure on {service}",
                f"{service} is approaching its memory limit.",
                service,
                [
                    "Python",
                    "REST",
                    "process memory",
                ],
                [
                    "memory utilization increased",
                    "garbage collection pressure increased",
                    "application response time increased",
                ],
                {
                    "memory_percent": state["memory_percent"],
                    "latency_ms": state["latency_ms"],
                    "status": state["status"],
                },
                "The application process is under sustained memory pressure.",
                "APPLICATION",
                "memory_pressure",
            )

        state["latency_ms"] = self.random.randint(300, 900)

        self._set_fault(
            "APPLICATION",
            "dependency_timeout",
            service,
            {
                "latency_ms": state["latency_ms"],
            },
            "A downstream dependency is exceeding the application's timeout budget.",
        )

        return self._base_incident(
            "APPLICATION",
            f"Application dependency timeout on {service}",
            f"{service} is experiencing slow responses from a dependency.",
            service,
            [
                "Python",
                "REST",
                "HTTP",
            ],
            [
                "dependency response time increased",
                "application latency increased",
                "requests approaching timeout",
            ],
            {
                "latency_ms": state["latency_ms"],
                "status": state["status"],
            },
            "A downstream dependency is exceeding the application's timeout budget.",
            "APPLICATION",
            "dependency_timeout",
        )

    # ============================================================
    # NETWORK
    # ============================================================

    def _generate_network_incident(self) -> Incident:

        network = self.random.choice(
            list(self.infrastructure.state.network.keys())
        )

        state = self.infrastructure.state.network[network]

        mechanism = self.random.choice(
            [
                "packet_loss",
                "dns",
                "connection_reset",
                "latency",
            ]
        )

        state["status"] = "degraded"

        if mechanism == "packet_loss":

            loss = round(
                self.random.uniform(3, 25),
                2,
            )

            state["packet_loss_percent"] = loss
            state["latency_ms"] = self.random.randint(80, 500)

            root = (
                "Network packet loss is affecting communication "
                "between components."
            )

            parameters = {
                "packet_loss_percent": loss,
            }

        elif mechanism == "dns":

            dns_latency = self.random.randint(100, 1000)

            state["dns_latency_ms"] = dns_latency
            state["latency_ms"] = self.random.randint(100, 600)

            root = (
                "DNS resolution latency is delaying "
                "service communication."
            )

            parameters = {
                "dns_latency_ms": dns_latency,
            }

        elif mechanism == "connection_reset":

            resets = self.random.randint(10, 100)

            state["connection_resets"] = resets
            state["latency_ms"] = self.random.randint(100, 700)

            root = (
                "Network connections are being reset unexpectedly."
            )

            parameters = {
                "connection_resets": resets,
            }

        else:

            latency = self.random.randint(100, 500)

            state["latency_ms"] = latency

            root = (
                "Network path latency has increased significantly."
            )

            parameters = {
                "latency_ms": latency,
            }

        self._set_fault(
            "NETWORK",
            mechanism,
            network,
            parameters,
            root,
        )

        return self._base_incident(
            "NETWORK",
            f"Network degradation on {network}",
            "Network communication between system components is degraded.",
            network,
            [
                "TCP/IP",
                "DNS",
                "service mesh",
            ],
            [
                "network health degraded",
                "request communication slowed",
                "service-to-service communication affected",
            ],
            dict(state),
            root,
            "NETWORK",
            mechanism,
        )

    # ============================================================
    # INFRASTRUCTURE
    # ============================================================

    def _generate_infrastructure_incident(self) -> Incident:

        component = self.random.choice(
            list(self.infrastructure.state.infrastructure.keys())
        )

        state = self.infrastructure.state.infrastructure[component]

        if component == "worker-pool":
            mechanisms = [
                "cpu",
                "memory",
                "disk",
                "pod_restarts",
                "worker_capacity",
            ]
        else:
            mechanisms = [
                "cpu",
                "memory",
                "disk",
                "pod_restarts",
            ]

        mechanism = self.random.choice(mechanisms)

        state["status"] = "degraded"

        if mechanism == "cpu":

            state["cpu_percent"] = self.random.randint(85, 99)

            root = "Compute resources are CPU constrained."
            parameters = {
                "cpu_percent": state["cpu_percent"],
            }

        elif mechanism == "memory":

            state["memory_percent"] = self.random.randint(85, 99)

            root = (
                "Compute resources are experiencing memory pressure."
            )

            parameters = {
                "memory_percent": state["memory_percent"],
            }

        elif mechanism == "disk":

            state["disk_percent"] = self.random.randint(85, 98)

            root = (
                "Disk capacity has reached a critical utilization level."
            )

            parameters = {
                "disk_percent": state["disk_percent"],
            }

        elif mechanism == "pod_restarts":

            state["pods_restarting"] = self.random.randint(3, 15)

            root = "Workloads are repeatedly restarting."

            parameters = {
                "pods_restarting": state["pods_restarting"],
            }

        else:

            state["available_workers"] = self.random.randint(
                0,
                state["total_workers"] - 1,
            )

            state["queue_depth"] = self.random.randint(
                100,
                1000,
            )

            root = (
                "Insufficient worker capacity is causing "
                "request backlog."
            )

            parameters = {
                "available_workers": state["available_workers"],
                "total_workers": state["total_workers"],
                "queue_depth": state["queue_depth"],
            }

        self._set_fault(
            "INFRASTRUCTURE",
            mechanism,
            component,
            parameters,
            root,
        )

        return self._base_incident(
            "INFRASTRUCTURE",
            f"Infrastructure degradation on {component}",
            "Underlying compute capacity is operating outside healthy limits.",
            component,
            [
                "Linux",
                "containers",
                "Kubernetes",
            ],
            [
                "resource utilization increased",
                "system capacity degraded",
                "service processing affected",
            ],
            dict(state),
            root,
            "INFRASTRUCTURE",
            mechanism,
        )

    # ============================================================
    # API LATENCY
    # ============================================================

    def _generate_api_latency_incident(self) -> Incident:

        service = self.random.choice(
            list(self.infrastructure.state.services.keys())
        )

        state = self.infrastructure.state.services[service]

        cause = self.random.choice(
            [
                "dependency",
                "database",
                "network",
                "application",
            ]
        )

        if cause == "dependency":

            dependency = self.random.choice(
                list(self.infrastructure.state.dependencies.keys())
            )

            dependency_state = (
                self.infrastructure.state.dependencies[dependency]
            )

            dependency_state["latency_ms"] = self.random.randint(
                300,
                1500,
            )

            dependency_state["status"] = "degraded"

            state["latency_ms"] = (
                dependency_state["latency_ms"]
                + self.random.randint(50, 200)
            )

            root = (
                f"Downstream dependency {dependency} is responding slowly."
            )

            parameters = {
                "dependency": dependency,
                "dependency_latency_ms": dependency_state["latency_ms"],
            }

            mechanism = "slow_dependency"

        elif cause == "database":

            database = self.random.choice(
                list(self.infrastructure.state.databases.keys())
            )

            db = self.infrastructure.state.databases[database]

            db["query_plan"] = self.random.choice(
                [
                    "full_scan",
                    "inefficient_join",
                ]
            )

            db["query_latency_ms"] = self.random.randint(
                250,
                1000,
            )

            db["status"] = "degraded"

            state["latency_ms"] = (
                db["query_latency_ms"]
                + self.random.randint(50, 250)
            )

            root = (
                f"Database response time on {database} "
                "is causing API request delays."
            )

            parameters = {
                "database": database,
                "query_plan": db["query_plan"],
                "query_latency_ms": db["query_latency_ms"],
            }

            mechanism = "slow_database_query"

        elif cause == "network":

            network = self.random.choice(
                list(self.infrastructure.state.network.keys())
            )

            network_state = self.infrastructure.state.network[network]

            network_state["latency_ms"] = self.random.randint(
                100,
                500,
            )

            network_state["status"] = "degraded"

            state["latency_ms"] = (
                network_state["latency_ms"]
                + self.random.randint(40, 200)
            )

            root = (
                f"Network latency on {network} "
                "is delaying API communication."
            )

            parameters = {
                "network": network,
                "network_latency_ms": network_state["latency_ms"],
            }

            mechanism = "network_latency"

        else:

            state["request_queue"] = self.random.randint(
                50,
                500,
            )

            state["cpu_percent"] = self.random.randint(
                70,
                95,
            )

            state["latency_ms"] = self.random.randint(
                300,
                1200,
            )

            root = (
                "Application-side request processing "
                "time has increased."
            )

            parameters = {
                "request_queue": state["request_queue"],
                "cpu_percent": state["cpu_percent"],
            }

            mechanism = "application_processing"

        state["status"] = "degraded"

        self._set_fault(
            "API_LATENCY",
            mechanism,
            service,
            parameters,
            root,
        )

        return self._base_incident(
            "API_LATENCY",
            f"Elevated API latency on {service}",
            f"{service} API response times are significantly above baseline.",
            service,
            [
                "REST",
                "HTTP",
                "API gateway",
            ],
            [
                "API latency increased",
                "request duration exceeded baseline",
                "slow requests detected",
            ],
            {
                "latency_ms": state["latency_ms"],
                "status": state["status"],
                "causal_layer": cause,
            },
            root,
            "API_LATENCY",
            mechanism,
        )

    # ============================================================
    # HIGH ERROR RATE
    # ============================================================

    def _generate_error_rate_incident(self) -> Incident:

        service = self.random.choice(
            list(self.infrastructure.state.services.keys())
        )

        state = self.infrastructure.state.services[service]

        cause = self.random.choice(
            [
                "dependency",
                "database",
                "configuration",
                "resource_exhaustion",
            ]
        )

        if cause == "dependency":

            dependency = self.random.choice(
                list(self.infrastructure.state.dependencies.keys())
            )

            dependency_state = (
                self.infrastructure.state.dependencies[dependency]
            )

            dependency_state["error_rate"] = round(
                self.random.uniform(10, 60),
                2,
            )

            dependency_state["status"] = "degraded"

            state["error_rate"] = round(
                min(
                    90,
                    dependency_state["error_rate"]
                    + self.random.uniform(2, 15),
                ),
                2,
            )

            root = (
                f"Downstream dependency {dependency} "
                "is returning failed requests."
            )

            parameters = {
                "dependency": dependency,
                "dependency_error_rate": dependency_state["error_rate"],
            }

            mechanism = "dependency_failure"

        elif cause == "database":

            database = self.random.choice(
                list(self.infrastructure.state.databases.keys())
            )

            db = self.infrastructure.state.databases[database]

            db["status"] = "degraded"
            db["connection_pool_used"] = db["connection_pool_size"]

            state["error_rate"] = round(
                self.random.uniform(10, 50),
                2,
            )

            root = (
                f"Database operations on {database} "
                "are failing because connections are exhausted."
            )

            parameters = {
                "database": database,
                "connection_pool_used": db["connection_pool_used"],
                "connection_pool_size": db["connection_pool_size"],
            }

            mechanism = "database_connection_failure"

        elif cause == "configuration":

            state["error_rate"] = round(
                self.random.uniform(5, 40),
                2,
            )

            root = (
                "An invalid application configuration "
                "is causing requests to fail."
            )

            parameters = {
                "configuration": self.random.choice(
                    [
                        "endpoint",
                        "authentication",
                        "timeout",
                        "connection_limit",
                    ]
                ),
            }

            mechanism = "invalid_configuration"

        else:

            state["cpu_percent"] = self.random.randint(
                85,
                99,
            )

            state["memory_percent"] = self.random.randint(
                85,
                99,
            )

            state["error_rate"] = round(
                self.random.uniform(8, 45),
                2,
            )

            root = (
                "Resource exhaustion is causing "
                "request processing failures."
            )

            parameters = {
                "cpu_percent": state["cpu_percent"],
                "memory_percent": state["memory_percent"],
            }

            mechanism = "resource_exhaustion"

        state["status"] = "degraded"

        self._set_fault(
            "HIGH_ERROR_RATE",
            mechanism,
            service,
            parameters,
            root,
        )

        return self._base_incident(
            "HIGH_ERROR_RATE",
            f"Elevated error rate on {service}",
            f"{service} is returning errors above the normal operating range.",
            service,
            [
                "REST",
                "HTTP",
                "application runtime",
            ],
            [
                "HTTP error rate increased",
                "failed requests detected",
                "service health degraded",
            ],
            {
                "error_rate": state["error_rate"],
                "status": state["status"],
                "causal_layer": cause,
            },
            root,
            "HIGH_ERROR_RATE",
            mechanism,
        )