from pprint import pprint

from TASK4.tests.test_task4 import run_scenario

from TASK5.approval.approval import ApprovalDecision
from TASK5.execution.simulator import SimulatedEnvironment
from TASK5.orchestrator.remediation import run_remediation
from TASK5.orchestrator.task4_adapter import convert_task4_output

from TASK6.orchestrator.verification import run_verification


def main():
    print("=" * 70)
    print("PRODUCTION INCIDENT RESPONSE AGENT")
    print("TASK 1 -> TASK 2 -> TASK 4 -> TASK 5 -> TASK 6")
    print("=" * 70)

    # ---------------------------------------------------------
    # TASK 4 - ROOT CAUSE ANALYSIS
    # ---------------------------------------------------------
    print("\n[1] Running Task 4 RCA...")

    task4_output = run_scenario("database")

    print(f"Incident: {task4_output.incident_id}")
    print(f"RCA Status: {task4_output.status}")

    payload = task4_output.payload

    # Task 4 payload is dictionary-based.
    root_cause = payload["root_cause"]
    recommended_action = payload["recommended_action"]

    # Support the actual Task 4 field while keeping the demo
    # tolerant of an alternate descriptive field name.
    root_cause_text = (
        root_cause.get("cause")
        or root_cause.get("summary")
        or root_cause.get("description")
        or str(root_cause)
    )

    print(f"Root Cause: {root_cause_text}")

    print(
        f"Recommended Action: "
        f"{recommended_action['action']}"
    )

    # ---------------------------------------------------------
    # TASK 5 - RCA -> REMEDIATION
    # ---------------------------------------------------------
    print("\n[2] Converting Task 4 RCA -> Task 5 Knowledge Card...")

    rca_card = convert_task4_output(task4_output)

    task5_action = rca_card.payload.recommended_action

    print(
        f"Action Type: "
        f"{task5_action.action_type}"
    )

    print(
        f"Target: "
        f"{task5_action.target}"
    )

    print(
        f"Risk: "
        f"{task5_action.risk}"
    )

    # ---------------------------------------------------------
    # SHARED SIMULATED ENVIRONMENT
    # ---------------------------------------------------------
    print("\n[3] Creating shared simulated environment...")

    environment = SimulatedEnvironment()

    print("\nBefore remediation:")
    pprint(environment.snapshot())

    # ---------------------------------------------------------
    # HUMAN APPROVAL
    # ---------------------------------------------------------
    print("\n[4] Human approval required.")
    print("For this demo, approval = APPROVED")

    # ---------------------------------------------------------
    # TASK 5 - CONTROLLED REMEDIATION
    # ---------------------------------------------------------
    task5_result = run_remediation(
        rca_card=rca_card,
        decision=ApprovalDecision.APPROVED,
        environment=environment,
    )

    task5_output = task5_result.to_dict()

    print("\n[5] Task 5 Remediation Result:")

    print(
        f"Status: "
        f"{task5_output['status']}"
    )

    print(
        f"Execution: "
        f"{task5_output['payload']['execution']['status']}"
    )

    print(
        f"Message: "
        f"{task5_output['payload']['execution']['message']}"
    )

    print("\nAfter remediation:")
    pprint(environment.snapshot())

    # ---------------------------------------------------------
    # TASK 6 - POST REMEDIATION VERIFICATION
    # ---------------------------------------------------------
    print("\n[6] Task 6 Post-Remediation Verification...")

    task6_result = run_verification(
        task5_output=task5_output,
        environment=environment,
    )

    output = task6_result.to_dict()

    verification = output["payload"]["verification"]

    print("\nTask 6 Verification:")

    print(
        f"Status: "
        f"{output['status']}"
    )

    print(
        f"Service Recovered: "
        f"{verification['service_recovered']}"
    )

    print(
        f"Next Step: "
        f"{verification['recommended_next_step']}"
    )

    print(
        f"Message: "
        f"{verification['message']}"
    )

    print("\nVerification checks:")
    pprint(verification["checks"])

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------
    print("\n" + "=" * 70)
    print("FINAL PIPELINE RESULT")
    print("=" * 70)

    if output["status"] == "SUCCESS":
        print("INCIDENT RESOLVED -> CLOSE")
    else:
        print("RECOVERY FAILED -> RE-INVESTIGATE")

    print("=" * 70)


if __name__ == "__main__":
    main()