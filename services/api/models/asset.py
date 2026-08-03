"""Infrastructure asset model."""
from __future__ import annotations

import uuid as _uuid
from datetime import date
from sqlalchemy import String, Integer, Float, Date, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from models.base import Base, TimestampMixin


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
    municipality_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("municipalities.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(
        Enum(
            "bridge", "water_main", "road", "power_line",
            "tunnel", "pump_station", "culvert", "retention_basin",
            name="asset_type", create_type=False,
        ),
        nullable=False,
    )
    geom = mapped_column(Geometry("GEOMETRY", srid=4326), nullable=False)
    installation_date: Mapped[date | None] = mapped_column(Date)
    design_life_years: Mapped[int | None] = mapped_column(Integer)
    material: Mapped[str | None] = mapped_column(String(100))
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    diameter_mm: Mapped[int | None] = mapped_column(Integer)
    span_m: Mapped[float | None] = mapped_column(Float)
    last_inspection_date: Mapped[date | None] = mapped_column(Date)
    next_inspection_date: Mapped[date | None] = mapped_column(Date)
    current_health_score: Mapped[float | None] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(
        Enum("low", "medium", "high", "critical", name="risk_level", create_type=False),
        default="low",
        nullable=False,
    )
    fhwa_id: Mapped[str | None] = mapped_column(String(50))
    epa_id: Mapped[str | None] = mapped_column(String(50))
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSONB, default={})

    # Relationships
    municipality = relationship("Municipality", back_populates="assets")
    alerts = relationship("Alert", back_populates="asset", lazy="selectin")
    work_orders = relationship("WorkOrder", back_populates="asset", lazy="selectin")
