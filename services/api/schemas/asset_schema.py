"""Pydantic schemas for Asset API endpoints."""

from datetime import date, datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    name: str = Field(..., max_length=255)
    asset_type: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    installation_date: date | None = None
    design_life_years: int | None = None
    material: str | None = None
    manufacturer: str | None = None
    diameter_mm: int | None = None
    span_m: float | None = None
    fhwa_id: str | None = None
    epa_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssetCreate(AssetBase):
    municipality_id: UUID


class AssetUpdate(BaseModel):
    name: str | None = None
    material: str | None = None
    current_health_score: float | None = Field(None, ge=0, le=100)
    risk_level: str | None = None
    last_inspection_date: date | None = None
    next_inspection_date: date | None = None
    metadata: dict[str, Any] | None = None


class AssetResponse(BaseModel):
    id: UUID
    municipality_id: UUID
    name: str
    asset_type: str
    latitude: float | None = None
    longitude: float | None = None
    installation_date: date | None = None
    design_life_years: int | None = None
    material: str | None = None
    manufacturer: str | None = None
    diameter_mm: int | None = None
    span_m: float | None = None
    last_inspection_date: date | None = None
    next_inspection_date: date | None = None
    current_health_score: float | None = None
    risk_level: str
    fhwa_id: str | None = None
    epa_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    page: int
    page_size: int
