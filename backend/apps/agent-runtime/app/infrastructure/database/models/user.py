"""User ORM model module for AGENTPAY (Phase 021)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.user_preferences import UserPreferences
    from app.infrastructure.database.models.user_profile import UserProfile


class User(Base):
    """User ORM entity representing core identity, account status, and tenant ownership."""

    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_id_email"),
        Index("ix_users_tenant_id", "tenant_id"),
        Index("ix_users_email", "email"),
        CheckConstraint("failed_login_attempts >= 0", name="failed_login_attempts_nonnegative"),
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

    # Normalized email address
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Protected password hash (never stored in plaintext)
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Account lifecycle status (active, inactive, suspended, locked, pending)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    # Security state
    failed_login_attempts: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Verification and Authentication timestamps
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    # Relationship to UserProfile
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # Relationship to UserPreferences
    preferences: Mapped[Optional["UserPreferences"]] = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Return safe string representation without exposing password hashes."""
        return (
            f"<User id={self.id} tenant_id={self.tenant_id} "
            f"email='{self.email}' status='{self.status}'>"
        )
