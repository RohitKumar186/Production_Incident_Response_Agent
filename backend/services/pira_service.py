# backend/services/pira_service.py

from typing import Any

from TASK1.models.schemas import Incident as Task1Incident
from TASK1.models.schemas import Severity as Task1Severity
from TASK4.orchestrator.investigation import run_rca

from integration.task1_to_task2 import investigate_task1_incident


# =========================================================
# HELPER
# =========================================================

def get_value(obj: Any, key: str, default=None):
    """
    Safely read a value from:
    - dictionary
    - RealDictRow
    - Pydantic model
    - normal Python object
    """

    if isinstance(obj, dict):
        return obj.get(key, default)

    if hasattr(obj, key):
        return getattr(obj, key)

    return default


# =========================================================
# BACKEND INCIDENT → TASK 1 INCIDENT
# =========================================================

def convert_backend_incident_to_task1(
    incident: Any,
) -> Task1Incident:

    incident_id = get_value(
        incident,
        "incident_id",
    )

    severity_value = get_value(
        incident,
        "severity",
        "MEDIUM",
    )

    affected_service = get_value(
        incident,
        "affected_service",
        "unknown-service",
    )

    detected_at = get_value(
        incident,
        "detected_at",
    )

    description = get_value(
        incident,
        "description",
    )

    title = get_value(
        incident,
        "title",
        "",
    )

    metadata = get_value(
        incident,
        "metadata",
        {},
    )

    if metadata is None:
        metadata = {}

    # PostgreSQL JSONB may already be a dict,
    # but handle string safely as well.
    if isinstance(metadata, str):
        import json

        try:
            metadata = json.loads(metadata)
        except json.JSONDecodeError:
            metadata = {}

    # -----------------------------------------------------
    # SEVERITY
    # -----------------------------------------------------

    try:

        severity = Task1Severity(
            str(severity_value).upper()
        )

    except ValueError:

        raise ValueError(
            f"Invalid severity: {severity_value}"
        )

    # -----------------------------------------------------
    # METADATA
    # -----------------------------------------------------

    service_version = metadata.get(
        "service_version",
        "1.0.0",
    )

    environment = metadata.get(
        "environment",
        "production",
    )

    baseline_latency_ms = float(
        metadata.get(
            "baseline_latency_ms",
            100.0,
        )
    )

    current_latency_ms = float(
        metadata.get(
            "current_latency_ms",
            baseline_latency_ms,
        )
    )

    increase_percent = float(
        metadata.get(
            "increase_percent",
            0.0,
        )
    )

    symptom = (
        description
        or title
        or "Unknown incident symptom"
    )

    # -----------------------------------------------------
    # CREATE TASK 1 INCIDENT
    # -----------------------------------------------------

    return Task1Incident(
        incident_id=incident_id,
        service_name=affected_service,
        service_version=service_version,
        severity=severity,
        detected_at=detected_at,
        symptom=symptom,
        baseline_latency_ms=baseline_latency_ms,
        current_latency_ms=current_latency_ms,
        increase_percent=increase_percent,
        environment=environment,
    )


# =========================================================
# RUN INVESTIGATION
# =========================================================

def run_investigation(
    incident: Any,
):

    task1_incident = (
        convert_backend_incident_to_task1(
            incident
        )
    )

    return investigate_task1_incident(
        task1_incident
    )


# =========================================================
# RUN ROOT CAUSE ANALYSIS
# =========================================================

def run_root_cause_analysis(
    investigation_card: Any,
):

    return run_rca(
        investigation_card
    )


# =========================================================
# FULL INVESTIGATION → RCA PIPELINE
# =========================================================

def run_investigation_and_rca(
    incident: Any,
) -> dict:

    investigation_card = run_investigation(
        incident
    )

    rca_output = run_root_cause_analysis(
        investigation_card
    )

    return {
        "investigation": investigation_card,
        "rca": rca_output,
    }