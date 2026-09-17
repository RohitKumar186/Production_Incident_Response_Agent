from .state import SimulatedState


class SimulatedInfrastructure:
    """
    Fixed generic production-like infrastructure used by the simulator.

    Every incident starts from this healthy baseline.

    Incidents modify this state.
    Metrics and logs are observations of the modified state.
    """

    def __init__(self) -> None:
        self.state = SimulatedState()
        self.reset()

    def reset(self) -> None:
        """
        Restore the entire simulated environment to a healthy state.

        Any previous incident fault is removed.
        """

        self.state.active_fault = None

        self.state.services = {
            "identity-service": {
                "status": "healthy",
                "replicas": 3,
                "cpu_percent": 35,
                "memory_percent": 48,
                "error_rate": 0.2,
                "latency_ms": 85,
                "request_queue": 4,
                "dependency_timeout_ms": 2000,
            },
            "profile-service": {
                "status": "healthy",
                "replicas": 3,
                "cpu_percent": 32,
                "memory_percent": 45,
                "error_rate": 0.1,
                "latency_ms": 78,
                "request_queue": 3,
                "dependency_timeout_ms": 2000,
            },
            "search-service": {
                "status": "healthy",
                "replicas": 4,
                "cpu_percent": 40,
                "memory_percent": 52,
                "error_rate": 0.2,
                "latency_ms": 95,
                "request_queue": 5,
                "dependency_timeout_ms": 2000,
            },
            "workflow-service": {
                "status": "healthy",
                "replicas": 3,
                "cpu_percent": 38,
                "memory_percent": 50,
                "error_rate": 0.1,
                "latency_ms": 90,
                "request_queue": 4,
                "dependency_timeout_ms": 2000,
            },
            "notification-service": {
                "status": "healthy",
                "replicas": 3,
                "cpu_percent": 30,
                "memory_percent": 42,
                "error_rate": 0.1,
                "latency_ms": 82,
                "request_queue": 2,
                "dependency_timeout_ms": 2000,
            },
        }

        self.state.databases = {
            "postgres-primary": {
                "status": "healthy",
                "query_plan": "indexed",
                "index_status": "valid",
                "lock_waits": 0,
                "connection_pool_used": 35,
                "connection_pool_size": 100,
                "replication_lag_ms": 5,
                "query_latency_ms": 40,
            },
            "redis-cache": {
                "status": "healthy",
                "eviction_rate": 0,
                "memory_percent": 55,
                "connection_pool_used": 30,
                "connection_pool_size": 100,
                "query_latency_ms": 8,
            },
        }

        self.state.network = {
            "service-mesh": {
                "status": "healthy",
                "packet_loss_percent": 0,
                "latency_ms": 8,
                "dns_latency_ms": 4,
                "connection_resets": 0,
            },
            "api-gateway": {
                "status": "healthy",
                "packet_loss_percent": 0,
                "latency_ms": 12,
                "timeout_ms": 5000,
                "connection_resets": 0,
            },
        }

        self.state.infrastructure = {
            "compute-cluster": {
                "status": "healthy",
                "cpu_percent": 45,
                "memory_percent": 52,
                "disk_percent": 48,
                "pods_restarting": 0,
            },
            "worker-pool": {
                "status": "healthy",
                "queue_depth": 12,
                "cpu_percent": 42,
                "memory_percent": 50,
                "available_workers": 8,
                "total_workers": 8,
            },
        }

        self.state.dependencies = {
            "identity-provider": {
                "status": "healthy",
                "latency_ms": 40,
                "error_rate": 0.1,
            },
            "message-broker": {
                "status": "healthy",
                "queue_depth": 10,
                "consumer_lag": 0,
            },
        }

    def snapshot(self) -> dict:
        """Return a complete snapshot of the current simulated state."""
        return self.state.snapshot()