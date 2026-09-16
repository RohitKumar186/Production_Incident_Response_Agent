from typing import Any

from TASK5.execution.simulator import SimulatedEnvironment
from TASK6.models.schemas import Task5RemediationOutput
from TASK6.verification.verifier import verify_remediation


class VerificationOutput:
    def __init__(self, remediation_output, verification):
        self.remediation_output = remediation_output
        self.verification = verification

    @property
    def status(self):
        return self.verification.status

    def to_dict(self):
        output = self.remediation_output.model_dump()

        output["consumer"] = "verification"

        output["payload"]["verification"] = {
            "status": self.verification.status,
            "service_recovered": self.verification.service_recovered,
            "checks": self.verification.checks,
            "message": self.verification.message,
            "recommended_next_step": (
                self.verification.recommended_next_step
            ),
        }

        output["status"] = self.verification.status

        return output


def run_verification(
    task5_output: Any,
    environment: SimulatedEnvironment,
) -> VerificationOutput:

    if hasattr(task5_output, "model_dump"):
        data = task5_output.model_dump()

    elif isinstance(task5_output, dict):
        data = task5_output

    else:
        raise TypeError(
            "Task 5 output must be a Pydantic model or dictionary"
        )

    remediation_output = Task5RemediationOutput.model_validate(data)

    verification = verify_remediation(
        remediation_output=remediation_output,
        environment=environment,
    )

    return VerificationOutput(
        remediation_output=remediation_output,
        verification=verification,
    )