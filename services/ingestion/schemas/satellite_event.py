"""Pydantic schema for satellite analysis events."""

from datetime import datetime
from pydantic import BaseModel, Field


class SatelliteEvent(BaseModel):
    asset_id: str | None = None
    latitude: float
    longitude: float
    image_source: str = "sentinel-1"
    subsidence_detected: bool = False
    subsidence_mm: float | None = None
    flood_risk: bool = False
    analysis_confidence: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
