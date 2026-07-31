"""Agent run audit trail model."""
from __future__ import annotations

import uuid as _uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
    municipality_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("municipalities.id"), nullable=False
    )
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_type: Mapped[str | None] = mapped_column(String(50))
    trigger_ref: Mapped[_uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    input_context: Mapped[dict | None] = mapped_column(JSONB)
    thought_chain: Mapped[dict | None] = mapped_column(JSONB, default=[])
    output: Mapped[dict | None] = mapped_column(JSONB)
    model_used: Mapped[str | None] = mapped_column(String(100))
    tokens_used: Mapped[int | None] = mapped_column(Integer)
    cost_estimate: Mapped[float | None] = mapped_column(Numeric(8, 4))
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
