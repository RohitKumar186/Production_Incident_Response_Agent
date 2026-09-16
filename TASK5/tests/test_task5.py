import pytest

from TASK5.approval.approval import ApprovalDecision
from TASK5.execution.simulator import SimulatedEnvironment
from TASK5.models.schemas import (
    RCAInputIncident,
    RCAInputPayload,
    RCARootCause,
    RCASupportingEvidence,
    RCARecommendedAction,
    RCARollbackPlan,
    Task4RCAKnowledgeCard,
)
from TASK5.orchestrator.remediation import run_remediation
from TASK5.orchestrator.task4_adapter import convert_task4_output
from TASK5.planner.planner import create_remediation_plan


def create_rca(
    action: str = "Optimize the orders database query",
    action_type: str = "DATABASE_REMEDIATION",
    target: str = "orders-db",
    risk: str = "MEDIUM",
) -> Task4RCAKnowledgeCard:
    """Create a representative valid Task 4 RCA Knowledge Card."""

    return Task4RCAKnowledgeCard(
        schema_version="1.0",
        incident_id="INC-001",
        correlation_id="INC-001-RCA-001",
        timestamp="2026-09-15T10:30:00Z",
        producer="rca",
        consumer="remediation",
        status="SUCCESS",
        payload=RCAInputPayload(
            incident=RCAInputIncident(
                incident_id="INC-001",
                service={
                    "name": "order-api",
                    "version": "v1.2.3",
                },
                severity="HIGH",
                detected_at="2026-09-15T10:20:00Z",
                symptom={
                    "description": (
                        "Order API latency increased significantly"
                    ),
                    "baseline_latency_ms": 100,
                    "current_latency_ms": 500,
                    "increase_percent": 400,
                },
                environment="production",
            ),
            root_cause=RCARootCause(
                description="Database query performance degradation",
                category="DATABASE",
                confidence=0.91,
            ),
            supporting_evidence=[
                RCASupportingEvidence(
                    finding_id="F-003",
                    source="database_agent",
                    evidence=(
                        "Query execution time is 4200 ms"
                    ),
                    expected_value="500 ms",
                    confidence=0.91,
                ),
                RCASupportingEvidence(
                    finding_id="F-001",
                    source="logs_agent",
                    evidence=(
                        "Multiple database timeout errors detected"
                    ),
                    confidence=0.88,
                ),
            ],
            rag_context=[
                {
                    "source_id": "INC-017",
                    "source_type": "previous_incident",
                    "title": (
                        "Previous Order API Database Incident"
                    ),
                    "relevant_information": (
                        "A similar database query performance "
                        "issue was resolved by optimizing the "
                        "affected query."
                    ),
                    "relevance_score": 0.94,
                }
            ],
            recommended_action=RCARecommendedAction(
                action=action,
                action_type=action_type,
                target=target,
                risk=risk,
                requires_human_approval=True,
            ),
            target_version="v1.2.4",
            rollback_plan=RCARollbackPlan(
                description=(
                    "Rollback the database change if "
                    "verification fails"
                )
            ),
        ),
    )


def test_valid_rca_creates_remediation_plan():
    """A valid Task 4 RCA should produce a Task 5 plan."""

    rca = create_rca()

    plan = create_remediation_plan(rca)

    assert plan.incident_id == "INC-001"
    assert plan.correlation_id == "INC-001-RCA-001"
    assert plan.action == "Optimize the orders database query"
    assert plan.action_type == "DATABASE_REMEDIATION"
    assert plan.target == "orders-db"
    assert plan.risk == "MEDIUM"
    assert plan.target_version == "v1.2.4"
    assert plan.requires_human_approval is True


def test_approved_remediation_executes():
    """APPROVED must allow controlled execution."""

    rca = create_rca()

    result = run_remediation(
        rca_card=rca,
        decision=ApprovalDecision.APPROVED,
    )

    output = result.to_dict()

    assert output["schema_version"] == "1.0"
    assert output["incident_id"] == "INC-001"
    assert output["producer"] == "remediation"
    assert output["consumer"] == "verification"
    assert output["status"] == "SUCCESS"

    assert (
        output["payload"]["approval"]["status"]
        == "APPROVED"
    )

    assert (
        output["payload"]["execution"]["status"]
        == "SUCCESS"
    )


def test_rejected_remediation_does_not_execute():
    """REJECTED must block execution."""

    rca = create_rca()

    result = run_remediation(
        rca_card=rca,
        decision=ApprovalDecision.REJECTED,
    )

    output = result.to_dict()

    assert output["status"] == "PARTIAL"

    assert (
        output["payload"]["approval"]["status"]
        == "REJECTED"
    )

    assert (
        output["payload"]["execution"]["status"]
        == "NOT_EXECUTED"
    )


def test_stopped_remediation_does_not_execute():
    """STOPPED must block execution."""

    rca = create_rca()

    result = run_remediation(
        rca_card=rca,
        decision=ApprovalDecision.STOPPED,
    )

    output = result.to_dict()

    assert output["status"] == "PARTIAL"

    assert (
        output["payload"]["approval"]["status"]
        == "STOPPED"
    )

    assert (
        output["payload"]["execution"]["status"]
        == "NOT_EXECUTED"
    )


def test_revision_request_does_not_execute():
    """REVISION_REQUESTED must block execution."""

    rca = create_rca()

    feedback = "Please consider another remediation approach."

    result = run_remediation(
        rca_card=rca,
        decision=ApprovalDecision.REVISION_REQUESTED,
        feedback=feedback,
    )

    output = result.to_dict()

    assert output["status"] == "PARTIAL"

    assert (
        output["payload"]["approval"]["status"]
        == "REVISION_REQUESTED"
    )

    assert (
        output["payload"]["approval"]["feedback"]
        == feedback
    )

    assert (
        output["payload"]["execution"]["status"]
        == "NOT_EXECUTED"
    )


def test_revision_requires_feedback():
    """A revision request without feedback must be rejected."""

    rca = create_rca()

    with pytest.raises(ValueError):
        run_remediation(
            rca_card=rca,
            decision=ApprovalDecision.REVISION_REQUESTED,
        )


def test_task4_recommendation_is_preserved():
    """
    Task 5 must use the exact recommendation supplied
    by Task 4 rather than inventing a different fix.
    """

    rca = create_rca(
        action="Optimize the orders database query",
        action_type="DATABASE_REMEDIATION",
        target="orders-db",
        risk="MEDIUM",
    )

    result = run_remediation(
        rca_card=rca,
        decision=ApprovalDecision.APPROVED,
    )

    output = result.to_dict()

    remediation = output["payload"]["remediation"]

    assert remediation["action"] == (
        "Optimize the orders database query"
    )
    assert remediation["action_type"] == (
        "DATABASE_REMEDIATION"
    )
    assert remediation["target"] == "orders-db"
    assert remediation["risk"] == "MEDIUM"


def test_unsupported_action_type_is_rejected():
    """Unsupported remediation types must not execute."""

    rca = create_rca(
        action="Do something unknown",
        action_type="UNKNOWN_REMEDIATION",
    )

    with pytest.raises(ValueError):
        run_remediation(
            rca_card=rca,
            decision=ApprovalDecision.APPROVED,
        )


def test_unsupported_database_action_is_rejected():
    """Unknown database recommendations must not execute."""

    rca = create_rca(
        action="Delete the entire production database",
        action_type="DATABASE_REMEDIATION",
    )

    with pytest.raises(ValueError):
        run_remediation(
            rca_card=rca,
            decision=ApprovalDecision.APPROVED,
        )


def test_database_remediation_changes_simulated_state():
    """Supported database remediation should improve state."""

    rca = create_rca()

    environment = SimulatedEnvironment()

    before = environment.snapshot()

    result = run_remediation(
        rca_card=rca,
        decision=ApprovalDecision.APPROVED,
        environment=environment,
    )

    after = result.execution["after"]

    assert result.status == "SUCCESS"
    assert after["db_query_latency_ms"] < (
        before["db_query_latency_ms"]
    )
    assert after["api_latency_ms"] < (
        before["api_latency_ms"]
    )
    assert after["error_rate"] < before["error_rate"]
    assert after["service_status"] == "HEALTHY"


def test_rollback_restores_previous_state():
    """Rollback must restore the pre-remediation state."""

    environment = SimulatedEnvironment()

    original_state = environment.snapshot()

    rca = create_rca()

    result = run_remediation(
        rca_card=rca,
        decision=ApprovalDecision.APPROVED,
        environment=environment,
    )

    assert result.status == "SUCCESS"

    changed_state = environment.snapshot()

    assert changed_state != original_state

    rollback_result = environment.rollback(
        original_state
    )

    assert rollback_result["status"] == "SUCCESS"
    assert rollback_result["state"] == original_state


def test_task4_output_can_be_converted_to_task5_card():
    """Task 4's structured output should cross the boundary."""

    task4_output = {
        "schema_version": "1.0",
        "incident_id": "INC-001",
        "correlation_id": "INC-001-RCA-001",
        "timestamp": "2026-09-15T10:30:00Z",
        "producer": "rca",
        "consumer": "remediation",
        "status": "SUCCESS",
        "payload": create_rca().payload.model_dump(),
    }

    card = convert_task4_output(task4_output)

    assert isinstance(card, Task4RCAKnowledgeCard)
    assert card.incident_id == "INC-001"
    assert (
        card.payload.recommended_action.action
        == "Optimize the orders database query"
    )


def test_invalid_task4_status_is_rejected():
    """Task 5 must not remediate a failed Task 4 RCA."""

    rca_data = create_rca().model_dump()
    rca_data["status"] = "FAILED"

    with pytest.raises(ValueError):
        convert_task4_output(rca_data)


def test_invalid_task4_producer_is_rejected():
    """Task 5 must only accept RCA-produced cards."""

    rca_data = create_rca().model_dump()
    rca_data["producer"] = "remediation"

    with pytest.raises(ValueError):
        convert_task4_output(rca_data)


def test_incident_id_mismatch_is_rejected():
    """Top-level and payload incident IDs must match."""

    rca_data = create_rca().model_dump()
    rca_data["incident_id"] = "INC-999"

    with pytest.raises(ValueError):
        convert_task4_output(rca_data)


def test_missing_supporting_evidence_is_rejected():
    """Task 5 requires supporting evidence from Task 4."""

    rca = create_rca()
    rca.payload.supporting_evidence = []

    with pytest.raises(ValueError):
        rca.validate_for_remediation()


def test_missing_rollback_plan_is_rejected():
    """Task 5 requires a rollback plan."""

    rca = create_rca()

    rca.payload.rollback_plan.description = ""

    with pytest.raises(ValueError):
        rca.validate_for_remediation()