from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from models.schemas import (
    Evidence,
    Finding,
    Incident,
    InvestigationStatus,
    KnowledgeCard,
    Severity,
)
from orchestration.investigation import run_investigation
from simulation.incident_generator import generate_simulation_data


def test_incident_model_validation() -> None:
    incident = generate_simulation_data(seed=42)

    assert incident.incident_id == "INC-001"
    assert incident.service_name == "order-api"
    assert incident.service_version == "v1.8"
    assert incident.environment == "production"
    assert incident.current_latency_ms > incident.baseline_latency_ms
    assert incident.increase_percent > 300


def test_confidence_cannot_be_greater_than_one() -> None:
    with pytest.raises(ValidationError):
        Finding(
            finding_id="F-1",
            agent="metrics",
            category="METRICS",
            finding="Bad confidence",
            value="x",
            expected_value="y",
            evidence=[],
            confidence=1.1,
            severity=Severity.HIGH,
        )


def test_confidence_cannot_be_negative() -> None:
    with pytest.raises(ValidationError):
        Finding(
            finding_id="F-1",
            agent="metrics",
            category="METRICS",
            finding="Bad confidence",
            value="x",
            expected_value="y",
            evidence=[],
            confidence=-0.1,
            severity=Severity.HIGH,
        )


def test_invalid_severity_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Incident(
            incident_id="INC-X",
            service_name="api",
            service_version="v1",
            severity="URGENT",
            detected_at=datetime.now(timezone.utc),
            symptom="slow",
            baseline_latency_ms=100,
            current_latency_ms=500,
            increase_percent=400,
            environment="production",
        )


def test_finding_structure_is_valid() -> None:
    finding = Finding(
        finding_id="F-1",
        agent="database",
        category="DATABASE",
        finding="Query latency increased",
        value="4.2 seconds",
        expected_value="< 0.5 seconds",
        evidence=[
            Evidence(
                source="database",
                reference="query-1",
                details="simulated",
            )
        ],
        confidence=0.91,
        severity=Severity.HIGH,
    )

    assert finding.finding_id == "F-1"
    assert finding.agent == "database"
    assert finding.evidence[0].reference == "query-1"
    assert finding.confidence == 0.91


def test_knowledge_card_can_be_created() -> None:
    incident = generate_simulation_data(seed=42)

    card = run_investigation(incident)

    assert isinstance(card, KnowledgeCard)
    assert card.status == InvestigationStatus.SUCCESS
    assert card.incident_id == incident.incident_id
    assert card.consumer == "rca"
    assert card.producer == "investigation"
    assert card.payload.findings

    assert any(
        finding.agent == "database"
        for finding in card.payload.findings
    )


def test_knowledge_card_can_be_serialized_to_json() -> None:
    incident = generate_simulation_data(seed=42)

    serialized = run_investigation(incident).model_dump_json()

    assert '"schema_version":"1.0"' in serialized
    assert '"consumer":"rca"' in serialized
    assert '"producer":"investigation"' in serialized
    assert '"incident_id":"INC-001"' in serialized