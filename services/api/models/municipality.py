"""Municipality model."""
from __future__ import annotations

import uuid as _uuid
from sqlalchemy import String, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from .base import Base, TimestampMixin


class Municipality(Base, TimestampMixin):
    __tablename__ = "municipalities"

    id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100), default="US")
    population: Mapped[int | None] = mapped_column(Integer)
    area_sq_km: Mapped[float | None] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(50), default="America/New_York")
    geom = mapped_column(Geometry("POINT", srid=4326), nullable=True)

    # Relationships
    assets = relationship("Asset", back_populates="municipality", lazy="selectin")
    users = relationship("User", back_populates="municipality", lazy="selectin")
