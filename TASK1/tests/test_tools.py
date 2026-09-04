from simulation.incident_generator import generate_simulation_data
from tools.database_tool import query_database
from tools.git_tool import get_deployment_history
from tools.kubernetes_tool import get_kubernetes_state
from tools.log_tool import search_logs
from tools.metrics_tool import get_metrics
from tools.network_tool import get_network_metrics


def setup_module() -> None:
    generate_simulation_data(seed=42)


def test_log_tool_finds_incident_logs() -> None:
    logs = search_logs(incident_id="INC-001")

    assert logs
    assert all(log["incident_id"] == "INC-001" for log in logs)
    assert any(log["level"] == "ERROR" for log in logs)


def test_metrics_tool_finds_incident_metrics() -> None:
    metrics = get_metrics(incident_id="INC-001")

    assert metrics
    assert all(metric["incident_id"] == "INC-001" for metric in metrics)
    assert any(metric["latency_ms"] > 400 for metric in metrics)


def test_database_tool_finds_slow_queries() -> None:
    records = query_database(incident_id="INC-001")

    assert records
    assert any(
        record["status"] == "SLOW"
        for record in records
    )
    assert any(
        record["status"] == "TIMEOUT_RISK"
        for record in records
    )


def test_network_tool_returns_incident_network_data() -> None:
    records = get_network_metrics(incident_id="INC-001")

    assert records
    assert all(
        record["incident_id"] == "INC-001"
        for record in records
    )


def test_network_is_healthy() -> None:
    records = get_network_metrics(incident_id="INC-001")

    assert all(
        record["status"] == "HEALTHY"
        for record in records
    )
    assert all(
        record["packet_loss_percent"] == 0
        for record in records
    )


def test_git_tool_finds_current_deployment() -> None:
    deployments = get_deployment_history(
        service="order-api",
        version="v1.8",
    )

    assert deployments
    assert any(
        deployment["version"] == "v1.8"
        for deployment in deployments
    )


def test_kubernetes_tool_returns_running_service() -> None:
    state = get_kubernetes_state(service="order-api")

    assert state
    assert state["deployment"]["service"] == "order-api"
    assert state["deployment"]["version"] == "v1.8"
    assert state["deployment"]["status"] == "Running"
    assert state["deployment"]["available_replicas"] == 3