from TASK4.tests.test_task4 import run_scenario
from TASK5.approval.approval import ApprovalDecision
from TASK5.orchestrator.remediation import run_remediation
from TASK5.orchestrator.task4_adapter import convert_task4_output


def test_task4_to_task5_end_to_end():
    """
    Verify the real Task 4 RCA output can flow into Task 5
    and reach controlled remediation after approval.
    """

    # Task 4 generates the RCA from its existing scenario.
    task4_output = run_scenario("database")

    # Convert Task 4 output at the Task 4 -> Task 5 boundary.
    rca_card = convert_task4_output(task4_output)

    # Task 5 receives human approval and executes the
    # approved remediation in its controlled simulator.
    result = run_remediation(
        rca_card=rca_card,
        decision=ApprovalDecision.APPROVED,
    )

    output = result.to_dict()

    assert output["schema_version"] == "1.0"

    assert output["incident_id"] == task4_output.incident_id

    assert (
        output["correlation_id"]
        == task4_output.correlation_id
    )

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

    # The recommendation must come from Task 4,
    # not from a hard-coded Task 5 assumption.
    assert (
        output["payload"]["remediation"]["action"]
        == task4_output.payload["recommended_action"]["action"]
    )

    assert (
        output["payload"]["remediation"]["action_type"]
        == task4_output.payload["recommended_action"]["action_type"]
    )

    assert (
        output["payload"]["remediation"]["target"]
        == task4_output.payload["recommended_action"]["target"]
    )

    assert (
        output["payload"]["remediation"]["risk"]
        == task4_output.payload["recommended_action"]["risk"]
    )

    assert (
        output["payload"]["rollback_plan"]["description"]
        == task4_output.payload["rollback_plan"]["description"]
    )