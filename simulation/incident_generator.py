"""
Incident generator.

Creates a simulated production incident and automatically
generates the production data associated with that incident.
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from random import Random

from models.schemas import Incident
from simulation.environment import generate_environment


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def format_timestamp(timestamp: datetime) -> str:
    """Convert a datetime to UTC ISO format."""
    return timestamp.astimezone(timezone.utc).isoformat().replace(
        "+00:00",
        "Z",
    )


def create_incident(
    seed: int | None = None,
    detected_at: datetime | None = None,
) -> Incident:
    """
    Create a simulated production incident.

    Environment values are generated automatically.
    """

    environment = generate_environment(seed)

    normal = environment["normal"]
    incident = environment["incident"]

    if detected_at is None:
        detected_at = datetime.now(timezone.utc)

    increase_percent = (
        (incident["latency_ms"] - normal["latency_ms"])
        / normal["latency_ms"]
    ) * 100

    return Incident(
        incident_id="INC-001",
        service_name=incident["service"],
        service_version=incident["version"],
        severity="HIGH",
        detected_at=detected_at,
        symptom=(
            f"API latency increased by approximately "
            f"{increase_percent:.0f}%"
        ),
        baseline_latency_ms=normal["latency_ms"],
        current_latency_ms=incident["latency_ms"],
        increase_percent=round(increase_percent, 2),
        environment=incident["environment"],
    )


def generate_logs(
    incident: Incident,
    environment: dict,
    rng: Random,
) -> list[dict]:
    """Generate simulated application logs."""

    normal = environment["normal"]
    incident_state = environment["incident"]
    incident_time = incident.detected_at

    logs = [
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=5)
            ),
            "service": incident.service_name,
            "level": "INFO",
            "message": "Order API request completed successfully",
            "latency_ms": normal["latency_ms"],
            "incident_id": None,
        },
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=4)
            ),
            "service": incident.service_name,
            "level": "INFO",
            "message": "Order API request completed successfully",
            "latency_ms": normal["latency_ms"] + rng.randint(-2, 2),
            "incident_id": None,
        },
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=3)
            ),
            "service": incident.service_name,
            "level": "INFO",
            "message": "Order API request completed successfully",
            "latency_ms": normal["latency_ms"] + rng.randint(-2, 2),
            "incident_id": None,
        },
    ]

    incident_messages = [
        "Database query execution time exceeded expected threshold",
        "Database query timeout while fetching order details",
        "Database connection request timed out",
        "Order request failed because database operation exceeded timeout",
        "Slow database query detected for order lookup",
    ]

    for index, message in enumerate(incident_messages):
        logs.append(
            {
                "timestamp": format_timestamp(
                    incident_time + timedelta(seconds=index * 5)
                ),
                "service": incident.service_name,
                "level": "WARN" if index == 0 else "ERROR",
                "message": message,
                "latency_ms": (
                    incident_state["database_query_latency_ms"]
                    + rng.randint(-150, 150)
                ),
                "incident_id": incident.incident_id,
            }
        )

    return logs


def generate_metrics(
    incident: Incident,
    environment: dict,
    rng: Random,
) -> list[dict]:
    """Generate simulated service metrics."""

    normal = environment["normal"]
    incident_state = environment["incident"]
    incident_time = incident.detected_at

    return [
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=5)
            ),
            "service": incident.service_name,
            "incident_id": None,
            "latency_ms": normal["latency_ms"],
            "cpu_percent": normal["cpu_percent"],
            "error_rate_percent": normal["error_rate_percent"],
        },
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=4)
            ),
            "service": incident.service_name,
            "incident_id": None,
            "latency_ms": normal["latency_ms"] + rng.randint(-2, 2),
            "cpu_percent": normal["cpu_percent"] + rng.randint(-2, 2),
            "error_rate_percent": normal["error_rate_percent"],
        },
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=1)
            ),
            "service": incident.service_name,
            "incident_id": incident.incident_id,
            "latency_ms": incident_state["latency_ms"] - rng.randint(
                10,
                30,
            ),
            "cpu_percent": incident_state["cpu_percent"] - rng.randint(
                1,
                4,
            ),
            "error_rate_percent": round(
                incident_state["error_rate_percent"]
                - rng.uniform(0.3, 0.8),
                2,
            ),
        },
        {
            "timestamp": format_timestamp(incident_time),
            "service": incident.service_name,
            "incident_id": incident.incident_id,
            "latency_ms": incident_state["latency_ms"],
            "cpu_percent": incident_state["cpu_percent"],
            "error_rate_percent": incident_state["error_rate_percent"],
        },
    ]


def generate_database_data(
    incident: Incident,
    environment: dict,
    rng: Random,
) -> list[dict]:
    """Generate simulated database query data."""

    normal = environment["normal"]
    incident_state = environment["incident"]
    incident_time = incident.detected_at

    return [
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=5)
            ),
            "query_id": "Q-101",
            "query": "SELECT * FROM orders WHERE customer_id = 101",
            "execution_time_ms": normal["database_query_latency_ms"],
            "expected_execution_time_ms": 500,
            "status": "SUCCESS",
            "incident_id": None,
        },
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=4)
            ),
            "query_id": "Q-102",
            "query": "SELECT * FROM orders WHERE customer_id = 102",
            "execution_time_ms": (
                normal["database_query_latency_ms"]
                + rng.randint(-20, 20)
            ),
            "expected_execution_time_ms": 500,
            "status": "SUCCESS",
            "incident_id": None,
        },
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=1)
            ),
            "query_id": "Q-103",
            "query": "SELECT * FROM orders WHERE customer_id = 103",
            "execution_time_ms": (
                incident_state["database_query_latency_ms"]
                - rng.randint(100, 300)
            ),
            "expected_execution_time_ms": 500,
            "status": "SLOW",
            "incident_id": incident.incident_id,
        },
        {
            "timestamp": format_timestamp(incident_time),
            "query_id": "Q-104",
            "query": "SELECT * FROM orders WHERE customer_id = 104",
            "execution_time_ms": incident_state["database_query_latency_ms"],
            "expected_execution_time_ms": 500,
            "status": "TIMEOUT_RISK",
            "incident_id": incident.incident_id,
        },
        {
            "timestamp": format_timestamp(
                incident_time + timedelta(minutes=1)
            ),
            "query_id": "Q-105",
            "query": "SELECT * FROM orders WHERE customer_id = 105",
            "execution_time_ms": (
                incident_state["database_query_latency_ms"]
                + rng.randint(50, 200)
            ),
            "expected_execution_time_ms": 500,
            "status": "TIMEOUT_RISK",
            "incident_id": incident.incident_id,
        },
    ]


def generate_network_data(
    incident: Incident,
    environment: dict,
    rng: Random,
) -> list[dict]:
    """Generate simulated network data."""

    normal = environment["normal"]
    incident_state = environment["incident"]
    incident_time = incident.detected_at

    return [
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=5)
            ),
            "service": incident.service_name,
            "source": incident.service_name,
            "destination": "database",
            "latency_ms": normal["network_latency_ms"],
            "packet_loss_percent": 0,
            "status": "HEALTHY",
            "incident_id": None,
        },
        {
            "timestamp": format_timestamp(
                incident_time - timedelta(minutes=3)
            ),
            "service": incident.service_name,
            "source": incident.service_name,
            "destination": "database",
            "latency_ms": normal["network_latency_ms"] + 1,
            "packet_loss_percent": 0,
            "status": "HEALTHY",
            "incident_id": None,
        },
        {
            "timestamp": format_timestamp(incident_time),
            "service": incident.service_name,
            "source": incident.service_name,
            "destination": "database",
            "latency_ms": incident_state["network_latency_ms"],
            "packet_loss_percent": 0,
            "status": "HEALTHY",
            "incident_id": incident.incident_id,
        },
        {
            "timestamp": format_timestamp(
                incident_time + timedelta(minutes=1)
            ),
            "service": incident.service_name,
            "source": incident.service_name,
            "destination": "database",
            "latency_ms": (
                incident_state["network_latency_ms"]
                + rng.randint(0, 2)
            ),
            "packet_loss_percent": 0,
            "status": "HEALTHY",
            "incident_id": incident.incident_id,
        },
    ]


def generate_deployment_data(incident: Incident) -> list[dict]:
    """Generate simulated deployment history."""

    deployment_time = incident.detected_at - timedelta(minutes=35)

    return [
        {
            "deployment_id": "DEP-001",
            "service": incident.service_name,
            "version": "v1.7",
            "deployed_at": format_timestamp(
                deployment_time - timedelta(days=2)
            ),
            "status": "SUCCESS",
        },
        {
            "deployment_id": "DEP-002",
            "service": incident.service_name,
            "version": incident.service_version,
            "deployed_at": format_timestamp(deployment_time),
            "status": "SUCCESS",
        },
    ]


def generate_kubernetes_data(
    incident: Incident,
    environment: dict,
) -> dict:
    """Generate simulated Kubernetes state."""

    incident_state = environment["incident"]

    return {
        "cluster": "simulated-production-cluster",
        "namespace": "production",
        "deployment": {
            "name": incident.service_name,
            "service": incident.service_name,
            "version": incident.service_version,
            "replicas": 3,
            "available_replicas": 3,
            "status": "Running",
            "cpu_percent": incident_state["cpu_percent"],
        },
    }


def save_json(filename: str, data: object) -> None:
    """Save generated simulation data to the data directory."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIR / filename

    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def generate_simulation_data(
    seed: int | None = None,
) -> Incident:
    """
    Generate the complete simulated production environment.

    All data sources are generated from the same incident
    timeline and environment.
    """

    rng = Random(seed)

    # Use one timestamp for the entire simulation.
    incident_time = datetime.now(timezone.utc)

    environment = generate_environment(seed)

    incident = create_incident(
        seed=seed,
        detected_at=incident_time,
    )

    logs = generate_logs(incident, environment, rng)
    metrics = generate_metrics(incident, environment, rng)
    database = generate_database_data(incident, environment, rng)
    network = generate_network_data(incident, environment, rng)
    deployments = generate_deployment_data(incident)
    kubernetes = generate_kubernetes_data(incident, environment)

    save_json("logs.json", logs)
    save_json("metrics.json", metrics)
    save_json("database.json", database)
    save_json("network.json", network)
    save_json("deployments.json", deployments)
    save_json("kubernetes.json", kubernetes)

    return incident


if __name__ == "__main__":
    incident = generate_simulation_data()

    print("\n" + "=" * 60)
    print("SIMULATION DATA GENERATED")
    print("=" * 60)

    print(f"Incident ID     : {incident.incident_id}")
    print(f"Service         : {incident.service_name}")
    print(f"Version         : {incident.service_version}")
    print(f"Severity        : {incident.severity.value}")
    print(f"Baseline        : {incident.baseline_latency_ms} ms")
    print(f"Current Latency : {incident.current_latency_ms} ms")
    print(f"Increase        : {incident.increase_percent}%")
    print(f"Detected At     : {format_timestamp(incident.detected_at)}")

    print("\nGenerated files:")
    print("  ✓ logs.json")
    print("  ✓ metrics.json")
    print("  ✓ database.json")
    print("  ✓ network.json")
    print("  ✓ deployments.json")
    print("  ✓ kubernetes.json")