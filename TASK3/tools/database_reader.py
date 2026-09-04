import json

from TASK3.config.settings import DATABASE_FILE
from TASK3.models.tool_schemas import ToolResponse, ToolError


def read_database() -> ToolResponse:

    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as file:
            database = json.load(file)

        return ToolResponse(
            status="SUCCESS",
            data=database
        )

    except FileNotFoundError:
        return ToolResponse(
            status="FAILED",
            error=ToolError(
                code="DATA_NOT_FOUND",
                message="Database data file was not found."
            )
        )

    except json.JSONDecodeError:
        return ToolResponse(
            status="FAILED",
            error=ToolError(
                code="INVALID_DATA",
                message="Database data contains invalid JSON."
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