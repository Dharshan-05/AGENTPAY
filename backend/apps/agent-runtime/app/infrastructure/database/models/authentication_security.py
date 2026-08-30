"""AuthenticationSecurity ORM model module for AGENTPAY (Phase 029)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.user import User


class AuthenticationSecurity(Base):
    """AuthenticationSecurity ORM entity representing user authentication security state."""

    __tablename__ = "authentication_security"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_authentication_security_user_id"),
        CheckConstraint(
            "failed_login_attempts >= 0",
            name="failed_login_attempts_nonnegative",
        ),
        Index("ix_authentication_security_tenant_id", "tenant_id"),
        Index("ix_authentication_security_user_id", "user_id"),
        Index("ix_authentication_security_status", "status"),
        Index("ix_authentication_security_locked_until", "locked_until"),
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

    # Foreign key referencing users.id (1-to-1 relationship per user)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_authentication_security_user_id_users",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Login failure & lockout tracking
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    locked_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    disabled_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Password security metadata (non-credential)
    password_changed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    password_expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Summary login activity timestamps
    last_successful_login_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    last_failed_login_at: Mapped[datetime | None] = mapped_column(
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
        """Return safe string representation without exposing sensitive details."""
        return (
            f"<AuthenticationSecurity id={self.id} tenant_id={self.tenant_id} "
            f"user_id={self.user_id} status='{self.status}' "
            f"failed_attempts={self.failed_login_attempts}>"
        )
