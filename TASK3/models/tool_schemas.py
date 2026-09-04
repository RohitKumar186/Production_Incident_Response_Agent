from pydantic import BaseModel, Field
from typing import Any, Optional


class ToolError(BaseModel):
    code: str
    message: str


class ToolResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[ToolError] = None