"""RefreshToken ORM model module for AGENTPAY (Phase 028)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.session import Session


class RefreshToken(Base):
    """RefreshToken ORM entity representing cryptographic refresh token registry records."""

    __tablename__ = "refresh_tokens"

    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
        Index("ix_refresh_tokens_tenant_id", "tenant_id"),
        Index("ix_refresh_tokens_session_id", "session_id"),
        Index("ix_refresh_tokens_token_hash", "token_hash"),
        Index("ix_refresh_tokens_family_id", "family_id"),
        Index("ix_refresh_tokens_parent_token_id", "parent_token_id"),
        Index("ix_refresh_tokens_status", "status"),
        Index("ix_refresh_tokens_expires_at", "expires_at"),
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

    # Foreign key referencing sessions.id
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "sessions.id",
            name="fk_refresh_tokens_session_id_sessions",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Cryptographic token digest (NEVER raw plaintext token)
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Rotation family & parent chain identifiers
    family_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    parent_token_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "refresh_tokens.id",
            name="fk_refresh_tokens_parent_token_id_refresh_tokens",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Token lifecycle status (e.g. "active", "rotated", "revoked", "expired")
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    # Rotation & security timestamps
    expires_at: Mapped[datetime] = mapped_column(
        nullable=False,
    )
    rotated_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    reuse_detected_at: Mapped[datetime | None] = mapped_column(
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

    # ORM Relationship back to Session
    session: Mapped["Session"] = relationship("Session")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING token_hash and secrets."""
        return (
            f"<RefreshToken id={self.id} tenant_id={self.tenant_id} "
            f"session_id={self.session_id} status='{self.status}'>"
        )
