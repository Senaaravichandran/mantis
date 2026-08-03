"""Alert model."""
from __future__ import annotations

import uuid as _uuid
from datetime import datetime
from sqlalchemy import String, Float, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
    asset_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False
    )
    municipality_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("municipalities.id"), nullable=False
    )
    severity: Mapped[str] = mapped_column(
        Enum("info", "warning", "critical", "emergency", name="alert_severity", create_type=False),
        nullable=False,
    )
    anomaly_type: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    agent_reasoning: Mapped[str | None] = mapped_column(Text)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    risk_score: Mapped[float | None] = mapped_column(Float)
    affected_sensors: Mapped[dict | None] = mapped_column(JSONB)
    weather_context: Mapped[dict | None] = mapped_column(JSONB)
    agent_run_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_runs.id")
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, nullable=False
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    acknowledged_by: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_false_positive: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    asset = relationship("Asset", back_populates="alerts")
