from TASK4.tests.test_task4 import run_scenario

from TASK5.approval.approval import ApprovalDecision
from TASK5.execution.simulator import SimulatedEnvironment
from TASK5.orchestrator.remediation import run_remediation
from TASK5.orchestrator.task4_adapter import convert_task4_output

from TASK6.orchestrator.verification import run_verification
from integration.task5_to_task6 import run_task5_to_task6
from integration.task4_to_task6 import run_task4_to_task6


def create_successful_task5_output():
    task4_output = run_scenario("database")

    rca_card = convert_task4_output(task4_output)

    environment = SimulatedEnvironment()

    result = run_remediation(
        rca_card=rca_card,
        decision=ApprovalDecision.APPROVED,
        environment=environment,
    )

    return result.to_dict(), environment


def test_successful_remediation_is_verified():
    task5_output, environment = create_successful_task5_output()

    result = run_verification(
        task5_output=task5_output,
        environment=environment,
    )

    assert result.status == "SUCCESS"
    assert result.verification.service_recovered is True
    assert result.verification.recommended_next_step == "CLOSE"


def test_verification_checks_actual_environment_state():
    task5_output, environment = create_successful_task5_output()

    environment.state["service_status"] = "DEGRADED"

    result = run_verification(
        task5_output=task5_output,
        environment=environment,
    )

    assert result.status == "FAILED"
    assert result.verification.service_recovered is False
    assert result.verification.recommended_next_step == "RE-INVESTIGATE"


def test_high_latency_causes_verification_failure():
    task5_output, environment = create_successful_task5_output()

    environment.state["api_latency_ms"] = 900.0

    result = run_verification(
        task5_output=task5_output,
        environment=environment,
    )

    assert result.status == "FAILED"
    assert result.verification.service_recovered is False


def test_high_error_rate_causes_verification_failure():
    task5_output, environment = create_successful_task5_output()

    environment.state["error_rate"] = 10.0

    result = run_verification(
        task5_output=task5_output,
        environment=environment,
    )

    assert result.status == "FAILED"
    assert result.verification.service_recovered is False


def test_rejected_remediation_is_not_verified_as_success():
    task4_output = run_scenario("database")

    rca_card = convert_task4_output(task4_output)

    environment = SimulatedEnvironment()

    result = run_remediation(
        rca_card=rca_card,
        decision=ApprovalDecision.REJECTED,
        environment=environment,
    )

    task5_output = result.to_dict()

    verification = run_verification(
        task5_output=task5_output,
        environment=environment,
    )

    assert verification.status == "NOT_VERIFIED"
    assert verification.verification.service_recovered is False
    assert (
        verification.verification.recommended_next_step
        == "RE-INVESTIGATE"
    )


def test_stopped_remediation_is_not_verified_as_success():
    task4_output = run_scenario("database")

    rca_card = convert_task4_output(task4_output)

    environment = SimulatedEnvironment()

    result = run_remediation(
        rca_card=rca_card,
        decision=ApprovalDecision.STOPPED,
        environment=environment,
    )

    task5_output = result.to_dict()

    verification = run_verification(
        task5_output=task5_output,
        environment=environment,
    )

    assert verification.status == "NOT_VERIFIED"
    assert verification.verification.service_recovered is False
    assert (
        verification.verification.recommended_next_step
        == "RE-INVESTIGATE"
    )


def test_task5_to_task6_integration():
    task5_output, environment = create_successful_task5_output()

    output = run_task5_to_task6(
        task5_output=task5_output,
        environment=environment,
    )

    assert output["schema_version"] == "1.0"
    assert output["incident_id"] == "INC-001"
    assert output["producer"] == "remediation"
    assert output["consumer"] == "verification"
    assert output["status"] == "SUCCESS"

    assert "verification" in output["payload"]

    assert output["payload"]["verification"]["status"] == "SUCCESS"
    assert (
        output["payload"]["verification"]["service_recovered"]
        is True
    )
    assert (
        output["payload"]["verification"]["recommended_next_step"]
        == "CLOSE"
    )


def test_failed_verification_requests_reinvestigation():
    task5_output, environment = create_successful_task5_output()

    environment.state["db_query_latency_ms"] = 3000.0

    output = run_task5_to_task6(
        task5_output=task5_output,
        environment=environment,
    )

    assert output["status"] == "FAILED"

    assert (
        output["payload"]["verification"]["recommended_next_step"]
        == "RE-INVESTIGATE"
    )


def test_all_remediation_types_can_reach_successful_verification():
    for scenario in [
        "database",
        "network",
        "application",
        "infrastructure",
    ]:
        task4_output = run_scenario(scenario)

        output = run_task4_to_task6(
            task4_output=task4_output,
            decision=ApprovalDecision.APPROVED,
        )

        assert output["schema_version"] == "1.0"
        assert output["producer"] == "remediation"
        assert output["consumer"] == "verification"
        assert output["status"] == "SUCCESS"

        assert (
            output["payload"]["verification"]["status"]
            == "SUCCESS"
        )

        assert (
            output["payload"]["verification"]["service_recovered"]
            is True
        )

        assert (
            output["payload"]["verification"]["recommended_next_step"]
            == "CLOSE"
        )


def test_full_pipeline_rejected_remediation_does_not_execute():
    task4_output = run_scenario("database")

    output = run_task4_to_task6(
        task4_output=task4_output,
        decision=ApprovalDecision.REJECTED,
    )

    assert output["status"] == "NOT_VERIFIED"

    assert (
        output["payload"]["verification"]["service_recovered"]
        is False
    )

    assert (
        output["payload"]["verification"]["recommended_next_step"]
        == "RE-INVESTIGATE"
    )


def test_full_pipeline_stopped_remediation_does_not_execute():
    task4_output = run_scenario("database")

    output = run_task4_to_task6(
        task4_output=task4_output,
        decision=ApprovalDecision.STOPPED,
    )

    assert output["status"] == "NOT_VERIFIED"

    assert (
        output["payload"]["verification"]["service_recovered"]
        is False
    )

    assert (
        output["payload"]["verification"]["recommended_next_step"]
        == "RE-INVESTIGATE"
    )