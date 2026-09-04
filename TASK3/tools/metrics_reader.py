import json

from TASK3.config.settings import METRICS_FILE
from TASK3.models.tool_schemas import ToolResponse, ToolError


def read_metrics(service: str) -> ToolResponse:

    try:
        with open(METRICS_FILE, "r", encoding="utf-8") as file:
            metrics = json.load(file)

        if metrics.get("service") != service:
            return ToolResponse(
                status="FAILED",
                error=ToolError(
                    code="SERVICE_NOT_FOUND",
                    message=f"No metrics found for service: {service}"
                )
            )

        return ToolResponse(
            status="SUCCESS",
            data=metrics
        )

    except FileNotFoundError:
        return ToolResponse(
            status="FAILED",
            error=ToolError(
                code="DATA_NOT_FOUND",
                message="Metrics data file was not found."
            )
        )

    except json.JSONDecodeError:
        return ToolResponse(
            status="FAILED",
            error=ToolError(
                code="INVALID_DATA",
                message="Metrics data contains invalid JSON."
            )
        )

    except Exception as error:
        return ToolResponse(
            status="FAILED",
            error=ToolError(
                code="TOOL_ERROR",
                message=str(error)
            )
        )