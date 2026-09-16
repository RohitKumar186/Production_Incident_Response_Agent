from typing import List, Optional
from pydantic import BaseModel, Field


class RAGContext(BaseModel):
    source_id: str
    source_type: str
    title: str
    relevant_information: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class RootCause(BaseModel):
    description: str
    category: str
    confidence: float = Field(ge=0.0, le=1.0)


class SupportingEvidence(BaseModel):
    finding_id: str
    source: str
    evidence: str
    expected_value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class RecommendedAction(BaseModel):
    action: str
    action_type: str
    target: str
    risk: str
    requires_human_approval: bool = True


class RollbackPlan(BaseModel):
    description: str


class RCAResult(BaseModel):
    root_cause: RootCause
    supporting_evidence: List[SupportingEvidence]
    rag_context: List[RAGContext]
    recommended_action: RecommendedAction
    target_version: str
    rollback_plan: RollbackPlan


class RCAOutput(BaseModel):
    schema_version: str = "1.0"
    incident_id: str
    correlation_id: str
    timestamp: str
    producer: str = "rca"
    consumer: str = "remediation"
    status: str
    payload: dict