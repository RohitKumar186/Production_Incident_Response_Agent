import json

from TASK3.config.settings import NETWORK_FILE
from TASK3.models.tool_schemas import ToolResponse, ToolError


def check_network(service: str) -> ToolResponse:

    try:
        with open(NETWORK_FILE, "r", encoding="utf-8") as file:
            network = json.load(file)

        if network.get("service") != service:
            return ToolResponse(
                status="FAILED",
                error=ToolError(
                    code="SERVICE_NOT_FOUND",
                    message=f"No network data found for service: {service}"
                )
            )

        return ToolResponse(
            status="SUCCESS",
            data=network
        )

    except FileNotFoundError:
        return ToolResponse(
            status="FAILED",
            error=ToolError(
                code="DATA_NOT_FOUND",
                message="Network data file was not found."
            )
        )

    except json.JSONDecodeError:
        return ToolResponse(
            status="FAILED",
            error=ToolError(
                code="INVALID_DATA",
                message="Network data contains invalid JSON."
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