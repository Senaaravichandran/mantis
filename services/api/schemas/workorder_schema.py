"""Pydantic schemas for Work Order API endpoints."""

from datetime import date, datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel, Field


class WorkOrderCreate(BaseModel):
    alert_id: UUID | None = None
    asset_id: UUID
    municipality_id: UUID
    priority: int = Field(3, ge=1, le=5)
    title: str = Field(..., max_length=255)
    scope_of_work: str
    estimated_cost: float | None = None
    scheduled_date: date | None = None
    generated_by: str = "human"


class WorkOrderUpdate(BaseModel):
    status: str | None = None
    priority: int | None = Field(None, ge=1, le=5)
    title: str | None = None
    scope_of_work: str | None = None
    estimated_cost: float | None = None
    actual_cost: float | None = None
    contractor_id: UUID | None = None
    scheduled_date: date | None = None
    completed_date: date | None = None


class WorkOrderApprove(BaseModel):
    approved_by: UUID


class WorkOrderResponse(BaseModel):
    id: UUID
    alert_id: UUID | None = None
    asset_id: UUID
    municipality_id: UUID
    status: str
    priority: int | None = None
    title: str
    scope_of_work: str
    estimated_cost: float | None = None
    actual_cost: float | None = None
    generated_by: str
    agent_run_id: UUID | None = None
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    contractor_id: UUID | None = None
    scheduled_date: date | None = None
    completed_date: date | None = None
    regulatory_refs: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkOrderListResponse(BaseModel):
    items: list[WorkOrderResponse]
    total: int
    page: int
    page_size: int
