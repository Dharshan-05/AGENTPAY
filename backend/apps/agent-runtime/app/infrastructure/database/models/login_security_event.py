"""LoginSecurityEvent ORM model module for AGENTPAY (Phase 030)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.refresh_token import RefreshToken
    from app.infrastructure.database.models.session import Session
    from app.infrastructure.database.models.user import User


class LoginSecurityEvent(Base):
    """LoginSecurityEvent ORM entity representing immutable security events."""

    __tablename__ = "login_security_events"

    __table_args__ = (
        Index("ix_login_security_events_tenant_id", "tenant_id"),
        Index("ix_login_security_events_user_id", "user_id"),
        Index("ix_login_security_events_session_id", "session_id"),
        Index("ix_login_security_events_refresh_token_id", "refresh_token_id"),
        Index("ix_login_security_events_event_type", "event_type"),
        Index("ix_login_security_events_occurred_at", "occurred_at"),
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

    # Foreign key referencing users.id (nullable for pre-auth or unknown user attempts)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_login_security_events_user_id_users",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Foreign key referencing sessions.id (nullable if pre-session)
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sessions.id",
            name="fk_login_security_events_session_id_sessions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Foreign key referencing refresh_tokens.id (nullable if not token event)
    refresh_token_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "refresh_tokens.id",
            name="fk_login_security_events_refresh_token_id_refresh_tokens",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Event identification & result
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success",
    )

    # Request context (non-sensitive)
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    request_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Event metadata (controlled JSONB payload with ZERO secrets/passwords/tokens)
    event_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )

    # Immutable event occurrence timestamp (no updated_at / no deleted_at)
    occurred_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    user: Mapped[Optional["User"]] = relationship("User")
    session: Mapped[Optional["Session"]] = relationship("Session")
    refresh_token: Mapped[Optional["RefreshToken"]] = relationship("RefreshToken")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING sensitive event_metadata."""
        return (
            f"<LoginSecurityEvent id={self.id} tenant_id={self.tenant_id} "
            f"user_id={self.user_id} event_type='{self.event_type}' "
            f"result='{self.event_result}'>"
        )
