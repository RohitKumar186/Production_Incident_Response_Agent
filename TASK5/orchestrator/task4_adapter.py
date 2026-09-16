from typing import Any

from TASK5.models.schemas import Task4RCAKnowledgeCard


def convert_task4_output(
    task4_output: Any,
) -> Task4RCAKnowledgeCard:
    """
    Convert the Task 4 RCAOutput into the frozen
    Task 4 -> Task 5 Knowledge Card contract.

    Task 5 intentionally depends only on the fields
    defined by the integration contract.
    """

    if hasattr(task4_output, "model_dump"):
        data = task4_output.model_dump()
    elif isinstance(task4_output, dict):
        data = task4_output
    else:
        raise TypeError(
            "Task 4 output must be a Pydantic model or dictionary"
        )

    required_top_level_fields = [
        "schema_version",
        "incident_id",
        "correlation_id",
        "timestamp",
        "producer",
        "consumer",
        "status",
        "payload",
    ]

    for field in required_top_level_fields:
        if field not in data:
            raise ValueError(
                f"Task 4 output is missing required field: {field}"
            )

    payload = data["payload"]

    if not isinstance(payload, dict):
        raise ValueError("Task 4 payload must be a dictionary")

    required_payload_fields = [
        "incident",
        "root_cause",
        "supporting_evidence",
        "recommended_action",
        "target_version",
        "rollback_plan",
    ]

    for field in required_payload_fields:
        if field not in payload:
            raise ValueError(
                f"Task 4 payload is missing required field: {field}"
            )

    card = Task4RCAKnowledgeCard.model_validate(data)

    card.validate_for_remediation()

    return card