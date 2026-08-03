"""Document model for RAG corpus."""
from __future__ import annotations

import uuid as _uuid
from datetime import date, datetime
from sqlalchemy import String, Integer, Text, Date, DateTime, Boolean, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
    asset_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("assets.id")
    )
    municipality_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("municipalities.id")
    )
    doc_type: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str | None] = mapped_column(String(255))
    source_path: Mapped[str | None] = mapped_column(String(500))
    content_text: Mapped[str | None] = mapped_column(Text)
    qdrant_point_id: Mapped[str | None] = mapped_column(String(100))
    page_count: Mapped[int | None] = mapped_column(Integer)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    inspection_date: Mapped[date | None] = mapped_column(Date)
    inspector_name: Mapped[str | None] = mapped_column(String(255))
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, nullable=False
    )
