from typing import Any

from TASK5.execution.simulator import SimulatedEnvironment
from TASK6.orchestrator.verification import run_verification


def run_task5_to_task6(
    task5_output: Any,
    environment: SimulatedEnvironment,
) -> dict:
    result = run_verification(
        task5_output=task5_output,
        environment=environment,
    )

    return result.to_dict()