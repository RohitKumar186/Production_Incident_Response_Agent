from pathlib import Path
import json

from orchestration.investigation import (
    run_investigation,
    save_knowledge_card,
)
from simulation.incident_generator import generate_simulation_data
from models.schemas import InvestigationStatus, KnowledgeCard


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_orchestrator_returns_knowledge_card() -> None:
    incident = generate_simulation_data(seed=42)

    card = run_investigation(incident)

    assert isinstance(card, KnowledgeCard)
    assert card.incident_id == "INC-001"
    assert card.schema_version == "1.0"


def test_orchestrator_completes_successfully() -> None:
    incident = generate_simulation_data(seed=42)

    card = run_investigation(incident)

    assert card.status == InvestigationStatus.SUCCESS


def test_orchestrator_collects_all_findings() -> None:
    incident = generate_simulation_data(seed=42)

    card = run_investigation(incident)

    assert len(card.payload.findings) == 8


def test_orchestrator_contains_all_agents() -> None:
    incident = generate_simulation_data(seed=42)

    card = run_investigation(incident)

    agents = {
        finding.agent
        for finding in card.payload.findings
    }

    assert agents == {
        "logs",
        "metrics",
        "database",
        "network",
    }


def test_overall_confidence_is_valid() -> None:
    incident = generate_simulation_data(seed=42)

    card = run_investigation(incident)

    assert 0.0 <= card.payload.overall_confidence <= 1.0


def test_knowledge_card_can_be_saved() -> None:
    incident = generate_simulation_data(seed=42)

    card = run_investigation(incident)
    output_file = save_knowledge_card(card)

    assert output_file.exists()
    assert output_file.name == "knowledge_card.json"


def test_saved_knowledge_card_is_valid_json() -> None:
    incident = generate_simulation_data(seed=42)

    card = run_investigation(incident)
    output_file = save_knowledge_card(card)

    with output_file.open("r", encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data["schema_version"] == "1.0"
    assert saved_data["incident_id"] == "INC-001"
    assert saved_data["producer"] == "investigation"
    assert saved_data["consumer"] == "rca"
    assert saved_data["status"] == "SUCCESS"


def test_saved_knowledge_card_contains_findings() -> None:
    incident = generate_simulation_data(seed=42)

    card = run_investigation(incident)
    output_file = save_knowledge_card(card)

    with output_file.open("r", encoding="utf-8") as file:
        saved_data = json.load(file)

    findings = saved_data["payload"]["findings"]

    assert len(findings) == 8
    assert any(
        finding["agent"] == "database"
        for finding in findings
    )