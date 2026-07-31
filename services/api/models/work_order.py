"""Work order model."""
from __future__ import annotations

import uuid as _uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Text, Date, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
    alert_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alerts.id")
    )
    asset_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False
    )
    municipality_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("municipalities.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "draft", "pending_approval", "approved", "in_progress",
            "completed", "cancelled", "on_hold",
            name="work_order_status", create_type=False,
        ),
        default="draft",
        nullable=False,
    )
    priority: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    scope_of_work: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))
    actual_cost: Mapped[float | None] = mapped_column(Numeric(12, 2))
    generated_by: Mapped[str] = mapped_column(String(20), default="agent")
    agent_run_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_runs.id")
    )
    approved_by: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    contractor_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contractors.id")
    )
    scheduled_date: Mapped[date | None] = mapped_column(Date)
    completed_date: Mapped[date | None] = mapped_column(Date)
    regulatory_refs: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, nullable=False
    )

    # Relationships
    asset = relationship("Asset", back_populates="work_orders")
