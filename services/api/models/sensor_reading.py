"""Sensor reading model (TimescaleDB hypertable)."""
from __future__ import annotations

import uuid as _uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    # TimescaleDB hypertables don't use a UUID PK — they use time + asset_id + sensor_id
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, nullable=False)
    asset_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), primary_key=True, nullable=False
    )
    sensor_id: Mapped[str] = mapped_column(String(100), primary_key=True, nullable=False)
    sensor_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50))
    quality_flag: Mapped[str] = mapped_column(String(20), default="good")
    raw_payload: Mapped[dict | None] = mapped_column(JSONB)
