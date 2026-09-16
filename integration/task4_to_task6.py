from typing import Any

from TASK5.approval.approval import ApprovalDecision
from TASK5.execution.simulator import SimulatedEnvironment
from TASK5.orchestrator.remediation import run_remediation
from TASK5.orchestrator.task4_adapter import convert_task4_output

from TASK6.orchestrator.verification import run_verification


def run_task4_to_task6(
    task4_output: Any,
    decision: ApprovalDecision,
    feedback: str | None = None,
) -> dict:

    rca_card = convert_task4_output(task4_output)

    environment = SimulatedEnvironment()

    task5_result = run_remediation(
        rca_card=rca_card,
        decision=decision,
        feedback=feedback,
        environment=environment,
    )

    task5_output = task5_result.to_dict()

    task6_result = run_verification(
        task5_output=task5_output,
        environment=environment,
    )

    return task6_result.to_dict()