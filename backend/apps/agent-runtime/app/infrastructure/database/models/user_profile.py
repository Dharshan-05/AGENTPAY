"""UserProfile ORM model module for AGENTPAY (Phase 022)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.user import User


class UserProfile(Base):
    """UserProfile ORM entity representing non-authentication user profile metadata."""

    __tablename__ = "user_profiles"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
        Index("ix_user_profiles_user_id", "user_id"),
        Index("ix_user_profiles_tenant_id", "tenant_id"),
    )

    # Primary key: UUID (UUIDv7)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign key referencing users.id
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", name="fk_user_profiles_user_id_users", ondelete="RESTRICT"),
        nullable=False,
    )

    # Multi-tenancy isolation key
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # Profile attributes
    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    display_name: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    timezone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    locale: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # Audit & Soft deletion timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationship back to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile",
    )

    def __repr__(self) -> str:
        """Return safe string representation without exposing PII in plain logs."""
        return f"<UserProfile id={self.id} user_id={self.user_id} tenant_id={self.tenant_id}>"
