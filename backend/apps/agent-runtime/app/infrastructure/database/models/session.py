"""Session ORM model module for AGENTPAY (Phase 027)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.user import User


class Session(Base):
    """Session ORM entity representing an authenticated user/device session context."""

    __tablename__ = "sessions"

    __table_args__ = (
        Index("ix_sessions_tenant_id", "tenant_id"),
        Index("ix_sessions_user_id", "user_id"),
        Index("ix_sessions_status", "status"),
        Index("ix_sessions_expires_at", "expires_at"),
    )

    # Primary key: UUID (UUIDv7)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Multi-tenancy isolation key
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Foreign key referencing users.id
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="fk_sessions_user_id_users", ondelete="RESTRICT"),
        nullable=False,
    )

    # Session lifecycle status (e.g. "active", "revoked", "expired")
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    # Device & client metadata (non-sensitive)
    device_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    # Activity & expiration boundaries
    last_activity_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    revocation_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ORM Relationship back to User
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        """Return safe string representation without exposing user agent or sensitive metadata."""
        return (
            f"<Session id={self.id} tenant_id={self.tenant_id} "
            f"user_id={self.user_id} status='{self.status}'>"
        )
