from pathlib import Path

from simulation.incident_generator import generate_simulation_data


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_simulation_generates_incident() -> None:
    incident = generate_simulation_data(seed=42)

    assert incident.incident_id == "INC-001"
    assert incident.service_name == "order-api"
    assert incident.service_version == "v1.8"
    assert incident.environment == "production"


def test_simulation_creates_expected_data_files() -> None:
    generate_simulation_data(seed=42)

    expected_files = [
        "logs.json",
        "metrics.json",
        "database.json",
        "network.json",
        "deployments.json",
        "kubernetes.json",
    ]

    for filename in expected_files:
        assert (DATA_DIR / filename).exists()


def test_simulated_incident_has_high_latency() -> None:
    incident = generate_simulation_data(seed=42)

    assert incident.current_latency_ms > incident.baseline_latency_ms
    assert incident.increase_percent > 300


def test_simulated_incident_is_high_severity() -> None:
    incident = generate_simulation_data(seed=42)

    assert incident.severity.value == "HIGH"


def test_simulation_is_deterministic_with_seed() -> None:
    first = generate_simulation_data(seed=42)
    second = generate_simulation_data(seed=42)

    assert first.baseline_latency_ms == second.baseline_latency_ms
    assert first.current_latency_ms == second.current_latency_ms
    assert first.increase_percent == second.increase_percent