from pathlib import Path
import json
import importlib

from TASK1.models.schemas import Incident as Task1Incident
from TASK2.models.schemas import Incident as Task2Incident
from TASK2.orchestrator.investigation import investigate_incident

import TASK3.config.settings as task3_settings


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TASK1_DATA_DIR = PROJECT_ROOT / "TASK1" / "data"
RUNTIME_DATA_DIR = PROJECT_ROOT / "integration" / "runtime_data"


# =========================================================
# HELPERS
# =========================================================

def load_json(filename):
    path = TASK1_DATA_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Task 1 data file not found: {path}"
        )

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(filename, data):
    RUNTIME_DATA_DIR.mkdir(parents=True, exist_ok=True)

    path = RUNTIME_DATA_DIR / filename

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


# =========================================================
# NORMALIZE LOG DATA
# =========================================================

def normalize_logs():
    """
    Task1 logs are already compatible with Task3.
    """

    logs = load_json("logs.json")

    if isinstance(logs, list):
        return logs

    return []


# =========================================================
# NORMALIZE METRICS
# =========================================================

def normalize_metrics():
    """
    Convert Task1 metrics list into the format expected
    by TASK3.metrics_reader and TASK2.metrics_agent.

    Task3 expects:

    {
        "service": "order-api",
        "latency": {
            "baseline_ms": ...,
            "current_ms": ...
        }
    }
    """

    metrics = load_json("metrics.json")

    if not isinstance(metrics, list) or not metrics:
        raise ValueError("Invalid Task1 metrics format")

    service = metrics[-1].get(
        "service",
        "order-api"
    )

    normal_metrics = [
        item
        for item in metrics
        if item.get("incident_id") is None
    ]

    incident_metrics = [
        item
        for item in metrics
        if item.get("incident_id") is not None
    ]

    if not normal_metrics:
        normal_metrics = metrics[:1]

    if not incident_metrics:
        incident_metrics = metrics[-1:]

    baseline = normal_metrics[0].get(
        "latency_ms",
        100
    )

    current = incident_metrics[-1].get(
        "latency_ms",
        baseline
    )

    return {
        "service": service,
        "latency": {
            "baseline_ms": baseline,
            "current_ms": current
        },
        "cpu_percent": incident_metrics[-1].get(
            "cpu_percent",
            0
        ),
        "error_rate_percent": incident_metrics[-1].get(
            "error_rate_percent",
            0
        )
    }


# =========================================================
# NORMALIZE DATABASE DATA
# =========================================================

def normalize_database():
    """
    Convert Task1 database list into the format expected
    by TASK2.database_agent.

    Task2 expects:

    {
        "database": "...",
        "status": "...",
        "queries": [...]
    }
    """

    database = load_json("database.json")

    if isinstance(database, dict):
        # Already in Task3 format.
        return database

    if not isinstance(database, list):
        raise ValueError("Invalid Task1 database format")

    queries = []

    for item in database:
        queries.append(
            {
                "query_id": item.get(
                    "query_id",
                    "unknown"
                ),
                "query": item.get(
                    "query",
                    ""
                ),
                "execution_time_ms": item.get(
                    "execution_time_ms",
                    0
                ),
                "expected_time_ms": item.get(
                    "expected_execution_time_ms",
                    item.get(
                        "expected_time_ms",
                        500
                    )
                )
            }
        )

    has_slow_query = any(
        query["execution_time_ms"] >
        query["expected_time_ms"]
        for query in queries
    )

    return {
        "database": "orders-db",
        "status": "DEGRADED" if has_slow_query else "HEALTHY",
        "queries": queries
    }


# =========================================================
# NORMALIZE NETWORK DATA
# =========================================================

def normalize_network():
    """
    Convert Task1 network data into the exact structure
    expected by TASK3.network_checker.
    """

    network = load_json("network.json")

    # If already Task3-compatible
    if (
        isinstance(network, dict)
        and "service" in network
        and "latency_ms" in network
    ):
        return network

    if not isinstance(network, list):
        raise ValueError("Invalid Task1 network format")

    service = "order-api"

    if network:
        service = network[-1].get(
            "service",
            service
        )

    normal_entries = [
        item
        for item in network
        if item.get("incident_id") is None
    ]

    incident_entries = [
        item
        for item in network
        if item.get("incident_id") is not None
    ]

    # Fallbacks
    if not normal_entries:
        normal_entries = network[:1]

    if not incident_entries:
        incident_entries = network[-1:]

    normal = normal_entries[0]
    current = incident_entries[-1]

    latency = current.get(
        "latency_ms",
        20
    )

    expected_latency = normal.get(
        "latency_ms",
        25
    )

    packet_loss = current.get(
        "packet_loss_percent",
        0
    )

    expected_packet_loss = normal.get(
        "packet_loss_percent",
        0
    )

    return {
        "service": service,
        "latency_ms": latency,
        "expected_latency_ms": expected_latency,
        "packet_loss_percent": packet_loss,
        "expected_packet_loss_percent": expected_packet_loss
    }


# =========================================================
# PREPARE TASK3 RUNTIME DATA
# =========================================================

def prepare_runtime_data():
    """
    Convert Task1 generated data into Task3-compatible
    runtime data.

    IMPORTANT:
    TASK3/data is NEVER modified.
    """

    RUNTIME_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    logs = normalize_logs()
    metrics = normalize_metrics()
    database = normalize_database()
    network = normalize_network()

    save_json("logs.json", logs)
    save_json("metrics.json", metrics)
    save_json("database.json", database)
    save_json("network.json", network)

    print(
        "[Integration] Task 1 data normalized "
        "for Task 3"
    )


# =========================================================
# REDIRECT TASK3
# =========================================================

def redirect_task3_to_runtime_data():
    """
    Point Task3 settings to integration runtime data.
    """

    task3_settings.DATA_DIR = RUNTIME_DATA_DIR

    task3_settings.LOGS_FILE = (
        RUNTIME_DATA_DIR / "logs.json"
    )

    task3_settings.METRICS_FILE = (
        RUNTIME_DATA_DIR / "metrics.json"
    )

    task3_settings.DATABASE_FILE = (
        RUNTIME_DATA_DIR / "database.json"
    )

    task3_settings.NETWORK_FILE = (
        RUNTIME_DATA_DIR / "network.json"
    )

    print(
        "[Integration] Task 3 redirected "
        "to runtime_data"
    )


# =========================================================
# RELOAD TASK3 TOOLS
# =========================================================

def reload_task3_tools():
    """
    Reload Task3 tools after changing settings.

    This is required because the tools import file paths
    directly from TASK3.config.settings.
    """

    import TASK3.tools.log_search as log_search
    import TASK3.tools.metrics_reader as metrics_reader
    import TASK3.tools.database_reader as database_reader
    import TASK3.tools.network_checker as network_checker

    importlib.reload(log_search)
    importlib.reload(metrics_reader)
    importlib.reload(database_reader)
    importlib.reload(network_checker)

    print(
        "[Integration] Task 3 tools reloaded"
    )


# =========================================================
# INCIDENT CONVERSION
# =========================================================

def convert_incident(
    task1_incident: Task1Incident
) -> Task2Incident:

    return Task2Incident(
        incident_id=task1_incident.incident_id,

        service={
            "name": task1_incident.service_name,
            "version": task1_incident.service_version,
        },

        severity=task1_incident.severity.value,

        detected_at=(
            task1_incident.detected_at.isoformat()
        ),

        symptom={
            "description": task1_incident.symptom,
            "baseline_latency_ms": (
                task1_incident.baseline_latency_ms
            ),
            "current_latency_ms": (
                task1_incident.current_latency_ms
            ),
            "increase_percent": (
                task1_incident.increase_percent
            ),
        },

        environment=task1_incident.environment,
    )


# =========================================================
# TASK1 → TASK2
# =========================================================

def investigate_task1_incident(
    task1_incident: Task1Incident
):
    """
    Complete integration:

        TASK1
          ↓
        Normalize data
          ↓
        TASK3
          ↓
        TASK2
    """

    # 1. Prepare Task3-compatible runtime data
    prepare_runtime_data()

    # 2. Redirect Task3
    redirect_task3_to_runtime_data()

    # 3. Reload Task3 tools
    reload_task3_tools()

    # 4. Convert incident contract
    task2_incident = convert_incident(
        task1_incident
    )

    # 5. Existing Task2 investigation
    return investigate_incident(
        task2_incident
    )