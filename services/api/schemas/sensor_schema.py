"""Pydantic schemas for Sensor API endpoints."""

from datetime import datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel, Field


class SensorReadingCreate(BaseModel):
    asset_id: UUID
    sensor_id: str
    sensor_type: str
    value: float
    unit: str | None = None
    quality_flag: str = "good"
    raw_payload: dict[str, Any] | None = None
    time: datetime | None = None


class SensorReadingResponse(BaseModel):
    time: datetime
    asset_id: UUID
    sensor_id: str
    sensor_type: str
    value: float
    unit: str | None = None
    quality_flag: str

    model_config = {"from_attributes": True}


class SensorHourlyResponse(BaseModel):
    bucket: datetime
    asset_id: UUID
    sensor_type: str
    avg_val: float
    max_val: float
    min_val: float
    reading_count: int


class SensorTimeSeriesRequest(BaseModel):
    asset_id: UUID
    sensor_type: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    resolution: str = "raw"  # raw | hourly | daily
