from simulation.incident_generator import generate_simulation_data
from agents.database_agent import investigate_database
from agents.logs_agent import investigate_logs
from agents.metrics_agent import investigate_metrics
from agents.network_agent import investigate_network
from models.schemas import InvestigationStatus


def setup_module() -> None:
    generate_simulation_data(seed=42)


def test_logs_agent_detects_database_errors() -> None:
    incident = generate_simulation_data(seed=42)

    result = investigate_logs(incident)

    assert result.status == InvestigationStatus.SUCCESS
    assert result.findings
    assert any(
        finding.category == "DATABASE"
        for finding in result.findings
    )


def test_metrics_agent_detects_latency_spike() -> None:
    incident = generate_simulation_data(seed=42)

    result = investigate_metrics(incident)

    assert result.status == InvestigationStatus.SUCCESS
    assert result.findings
    assert any(
        finding.finding_id == "METRIC-F-001"
        for finding in result.findings
    )


def test_metrics_agent_detects_high_cpu() -> None:
    incident = generate_simulation_data(seed=42)

    result = investigate_metrics(incident)

    assert any(
        finding.finding_id == "METRIC-F-002"
        for finding in result.findings
    )


def test_database_agent_detects_slow_queries() -> None:
    incident = generate_simulation_data(seed=42)

    result = investigate_database(incident)

    assert result.status == InvestigationStatus.SUCCESS
    assert result.findings
    assert any(
        finding.finding_id == "DB-F-001"
        for finding in result.findings
    )


def test_database_agent_detects_timeout_risk() -> None:
    incident = generate_simulation_data(seed=42)

    result = investigate_database(incident)

    assert any(
        finding.finding_id == "DB-F-002"
        for finding in result.findings
    )


def test_network_agent_identifies_healthy_network() -> None:
    incident = generate_simulation_data(seed=42)

    result = investigate_network(incident)

    assert result.status == InvestigationStatus.SUCCESS
    assert result.findings
    assert any(
        finding.finding_id == "NET-F-001"
        for finding in result.findings
    )


def test_all_agents_produce_confidence_scores() -> None:
    incident = generate_simulation_data(seed=42)

    results = [
        investigate_logs(incident),
        investigate_metrics(incident),
        investigate_database(incident),
        investigate_network(incident),
    ]

    for result in results:
        assert 0.0 <= result.confidence <= 1.0
        assert result.status == InvestigationStatus.SUCCESS