from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AgentEvent(BaseModel):
    runId: str
    investigationId: str
    timestamp: str
    eventType: str
    status: Literal[
        "pending",
        "running",
        "success",
        "error",
        "interrupted",
    ]
    agent: Optional[str] = None
    tool: Optional[str] = None
    inputSummary: Optional[str] = None
    outputSummary: Optional[str] = None
    durationMs: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class Evidence(BaseModel):
    id: str
    source: str
    title: str
    metric: Optional[str] = None
    value: Optional[str] = None
    timestamp: Optional[str] = None
    interpretation: str
    relevance: Literal["low", "medium", "high", "critical"]


class Action(BaseModel):
    id: str
    description: str
    status: Literal[
        "pending",
        "approved",
        "rejected",
        "executing",
        "completed",
    ] = "pending"


class Recommendation(BaseModel):
    title: str
    description: str
    actions: List[Action] = Field(default_factory=list)


class InvestigationResult(BaseModel):
    investigationId: str
    status: Literal["completed", "failed", "interrupted"]
    query: str
    rootCause: Optional[str] = None
    confidence: float = 0.0
    evidence: List[Evidence] = Field(default_factory=list)
    recommendation: Optional[Recommendation] = None
    events: List[AgentEvent] = Field(default_factory=list)
