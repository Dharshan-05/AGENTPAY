"""UserPreferences ORM model module for AGENTPAY (Phase 118)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.user import User

# ---------------------------------------------------------------------------
# Default preference values — applied when a preference record is first created
# ---------------------------------------------------------------------------
DEFAULT_PREFERENCES: dict[str, Any] = {
    "locale": "en",
    "timezone": "UTC",
    "notification_email": True,
    "notification_push": True,
    "notification_sms": False,
    "ui_theme": "system",
    "ui_language": "en",
    "accessibility_high_contrast": False,
    "accessibility_reduce_motion": False,
}


class UserPreferences(Base):
    """UserPreferences ORM entity storing tenant-scoped user preference configuration."""

    __tablename__ = "user_preferences"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_user_preferences_user_id"),
        Index("ix_user_preferences_user_id", "user_id"),
        Index("ix_user_preferences_tenant_id", "tenant_id"),
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
        ForeignKey(
            "users.id",
            name="fk_user_preferences_user_id_users",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Multi-tenancy isolation key
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    # JSONB preferences bag — merged with DEFAULT_PREFERENCES on read
    preferences: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'"),
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

    # Relationship back to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="preferences",
        foreign_keys=[user_id],
    )

    def effective_preferences(self) -> dict[str, Any]:
        """Return preferences merged with defaults — new keys are always safely defaulted."""
        return {**DEFAULT_PREFERENCES, **(self.preferences or {})}

    def __repr__(self) -> str:
        """Return safe string representation."""
        return f"<UserPreferences id={self.id} user_id={self.user_id} tenant_id={self.tenant_id}>"
