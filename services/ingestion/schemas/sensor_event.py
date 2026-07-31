"""Pydantic schema for raw sensor events on Kafka."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class SensorEvent(BaseModel):
    asset_id: str
    sensor_id: str
    sensor_type: str
    value: float
    unit: str | None = None
    quality_flag: str = "good"
    raw_payload: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_simulated: bool = False
