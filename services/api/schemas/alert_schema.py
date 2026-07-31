"""Pydantic schemas for Alert API endpoints."""

from datetime import datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    asset_id: UUID
    municipality_id: UUID
    severity: str
    anomaly_type: str | None = None
    title: str = Field(..., max_length=255)
    description: str
    agent_reasoning: str | None = None
    confidence_score: float | None = Field(None, ge=0, le=1)
    risk_score: float | None = Field(None, ge=0, le=100)
    affected_sensors: dict[str, Any] | None = None
    weather_context: dict[str, Any] | None = None
    agent_run_id: UUID | None = None


class AlertUpdate(BaseModel):
    severity: str | None = None
    is_false_positive: bool | None = None


class AlertAcknowledge(BaseModel):
    acknowledged_by: UUID


class AlertResolve(BaseModel):
    resolved_by: UUID | None = None
    is_false_positive: bool = False


class AlertResponse(BaseModel):
    id: UUID
    asset_id: UUID
    municipality_id: UUID
    severity: str
    anomaly_type: str | None = None
    title: str
    description: str
    agent_reasoning: str | None = None
    confidence_score: float | None = None
    risk_score: float | None = None
    affected_sensors: dict[str, Any] | None = None
    weather_context: dict[str, Any] | None = None
    agent_run_id: UUID | None = None
    detected_at: datetime
    acknowledged_at: datetime | None = None
    acknowledged_by: UUID | None = None
    resolved_at: datetime | None = None
    is_false_positive: bool

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    total: int
    page: int
    page_size: int
