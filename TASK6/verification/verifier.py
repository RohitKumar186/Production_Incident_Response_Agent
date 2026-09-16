from TASK5.execution.simulator import SimulatedEnvironment
from TASK6.models.schemas import Task5RemediationOutput, VerificationResult


def verify_remediation(
    remediation_output: Task5RemediationOutput,
    environment: SimulatedEnvironment,
) -> VerificationResult:

    if remediation_output.producer != "remediation":
        raise ValueError("Invalid producer: expected 'remediation'")

    if remediation_output.consumer != "verification":
        raise ValueError("Invalid consumer: expected 'verification'")

    if remediation_output.status != "SUCCESS":
        return VerificationResult(
            status="NOT_VERIFIED",
            service_recovered=False,
            checks={},
            message=(
                "Task 5 did not report a successful remediation. "
                "Verification cannot mark the incident as recovered."
            ),
            recommended_next_step="RE-INVESTIGATE",
        )

    approval_status = remediation_output.payload.approval.status
    execution_status = remediation_output.payload.execution.status

    if approval_status != "APPROVED":
        return VerificationResult(
            status="NOT_VERIFIED",
            service_recovered=False,
            checks={
                "approval_status": approval_status,
                "execution_status": execution_status,
            },
            message="Remediation was not approved. The incident remains unresolved.",
            recommended_next_step="RE-INVESTIGATE",
        )

    if execution_status != "SUCCESS":
        return VerificationResult(
            status="FAILED",
            service_recovered=False,
            checks={
                "approval_status": approval_status,
                "execution_status": execution_status,
            },
            message="Remediation execution did not succeed.",
            recommended_next_step="RE-INVESTIGATE",
        )

    state = environment.state
    action_type = remediation_output.payload.remediation.action_type

    checks = {
        "action_type": action_type,
        "db_query_latency_ms": state["db_query_latency_ms"],
        "api_latency_ms": state["api_latency_ms"],
        "error_rate": state["error_rate"],
        "service_status": state["service_status"],
    }

    # Common recovery checks.
    api_recovered = state["api_latency_ms"] <= 200
    errors_recovered = state["error_rate"] <= 2
    service_healthy = state["service_status"] == "HEALTHY"

    # Database latency is only relevant when the remediation
    # specifically targeted the database.
    database_recovered = True

    if action_type == "DATABASE_REMEDIATION":
        database_recovered = state["db_query_latency_ms"] <= 500

    recovered = (
        database_recovered
        and api_recovered
        and errors_recovered
        and service_healthy
    )

    if recovered:
        return VerificationResult(
            status="SUCCESS",
            service_recovered=True,
            checks=checks,
            message=(
                "Post-remediation verification passed. "
                "The simulated service has recovered."
            ),
            recommended_next_step="CLOSE",
        )

    return VerificationResult(
        status="FAILED",
        service_recovered=False,
        checks=checks,
        message=(
            "Post-remediation verification failed. "
            "The simulated service has not fully recovered."
        ),
        recommended_next_step="RE-INVESTIGATE",
    )