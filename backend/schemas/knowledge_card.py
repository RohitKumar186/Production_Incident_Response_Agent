from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field


class KnowledgeCard(BaseModel):
    schema_version: str = "1.0"

    incident_id: str
    correlation_id: str

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    producer: str
    consumer: str

    status: str

    payload: Dict[str, Any] = Field(default_factory=dict)