import json

from TASK3.config.settings import LOGS_FILE
from TASK3.models.tool_schemas import ToolResponse, ToolError


def search_logs(service: str) -> ToolResponse:

    try:
        with open(LOGS_FILE, "r", encoding="utf-8") as file:
            logs = json.load(file)

        matching_logs = [
            log for log in logs
            if log.get("service") == service
        ]

        return ToolResponse(
            status="SUCCESS",
            data=matching_logs
        )

    except FileNotFoundError:
        return ToolResponse(
            status="FAILED",
            error=ToolError(
                code="DATA_NOT_FOUND",
                message="Logs data file was not found."
            )
        )

    except json.JSONDecodeError:
        return ToolResponse(
            status="FAILED",
            error=ToolError(
                code="INVALID_DATA",
                message="Logs data contains invalid JSON."
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