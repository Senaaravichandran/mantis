"""Pydantic schema for weather events."""

from datetime import datetime
from pydantic import BaseModel, Field


class WeatherEvent(BaseModel):
    latitude: float
    longitude: float
    temperature_c: float
    conditions: str
    wind_speed: str = ""
    freeze_thaw_risk: bool = False
    extreme_heat: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
