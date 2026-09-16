from TASK1.simulation.incident_generator import generate_simulation_data
from integration.task1_to_task2 import investigate_task1_incident
from TASK4.orchestrator.investigation import run_rca


def run_scenario(scenario):
    incident = generate_simulation_data(
        seed=42,
        scenario=scenario,
    )

    investigation_card = investigate_task1_incident(incident)

    assert investigation_card.status == "SUCCESS"
    assert len(investigation_card.payload.findings) == 4

    rca = run_rca(investigation_card)

    assert rca.status == "SUCCESS"
    assert rca.incident_id == "INC-001"

    return rca


def test_database_scenario():
    rca = run_scenario("database")

    assert rca.payload["root_cause"]["category"] == "DATABASE"


def test_network_scenario():
    rca = run_scenario("network")

    assert rca.payload["root_cause"]["category"] == "NETWORK"


def test_application_scenario():
    rca = run_scenario("application")

    assert rca.payload["root_cause"]["category"] == "APPLICATION"


def test_infrastructure_scenario():
    rca = run_scenario("infrastructure")

    assert rca.payload["root_cause"]["category"] == "INFRASTRUCTURE"


def test_rca_contains_required_fields():
    rca = run_scenario("database")

    payload = rca.payload

    assert "incident" in payload
    assert "root_cause" in payload
    assert "supporting_evidence" in payload
    assert "rag_context" in payload
    assert "recommended_action" in payload
    assert "target_version" in payload
    assert "rollback_plan" in payload

    assert len(payload["supporting_evidence"]) > 0
    assert len(payload["rag_context"]) > 0