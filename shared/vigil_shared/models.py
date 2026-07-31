"""Shared Pydantic models used across MANTIS services."""

from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class SensorEvent(BaseModel):
    """Kafka message schema for raw sensor readings."""
    asset_id: UUID
    sensor_id: str
    sensor_type: str
    value: float
    unit: str | None = None
    quality_flag: str = "good"
    raw_payload: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class AnomalyAlert(BaseModel):
    """Internal message when an anomaly is detected."""
    asset_id: UUID
    sensor_id: str
    anomaly_score: float
    confidence: float
    deviation_pct: float
    affected_sensors: list[str] = Field(default_factory=list)
    weather_factor: float | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class AgentTaskMessage(BaseModel):
    """Kafka message to trigger an agent run."""
    task_id: UUID
    trigger_type: str
    asset_id: UUID | None = None
    sensor_data: dict[str, Any] | None = None
    municipality_id: UUID
    priority: int = 3
    metadata: dict[str, Any] = Field(default_factory=dict)


class WeatherData(BaseModel):
    """Weather conditions for a location."""
    temperature_c: float
    humidity_pct: float
    wind_speed_kmh: float
    precipitation_mm: float
    pressure_hpa: float
    conditions: str
    freeze_thaw_risk: bool = False
    extreme_heat: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    service: str
    version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
