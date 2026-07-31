"""Pydantic schemas for Agent API endpoints."""

from datetime import datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel


class AgentTriggerRequest(BaseModel):
    trigger_type: str = "manual"
    asset_id: UUID | None = None
    municipality_id: UUID
    sensor_data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class AgentRunResponse(BaseModel):
    id: UUID
    municipality_id: UUID
    agent_type: str
    trigger_type: str | None = None
    status: str
    input_context: dict[str, Any] | None = None
    thought_chain: list[dict[str, Any]] | None = None
    output: dict[str, Any] | None = None
    model_used: str | None = None
    tokens_used: int | None = None
    cost_estimate: float | None = None
    error_message: str | None = None
    started_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class AgentRunListResponse(BaseModel):
    items: list[AgentRunResponse]
    total: int
    page: int
    page_size: int
