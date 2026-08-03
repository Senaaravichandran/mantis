"""User model."""
from __future__ import annotations

import uuid as _uuid
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[_uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4)
    municipality_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("municipalities.id")
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="engineer")
    keycloak_id: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    municipality = relationship("Municipality", back_populates="users")
