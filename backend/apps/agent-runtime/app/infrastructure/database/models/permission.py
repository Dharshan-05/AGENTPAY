"""Permission ORM model module for AGENTPAY (Phase 024)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class Permission(Base):
    """Permission ORM entity representing atomic global authorization capabilities."""

    __tablename__ = "permissions"

    __table_args__ = (
        UniqueConstraint("name", name="uq_permissions_name"),
        Index("ix_permissions_name", "name"),
        Index("ix_permissions_resource", "resource"),
    )

    # Primary key: UUID (UUIDv7)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Permission canonical name (e.g. "users.read", "agents.execute")
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Resource domain (e.g. "users", "agents", "transactions")
    resource: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Action (e.g. "read", "create", "update", "delete", "execute")
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Optional description of capability
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # System permission flag
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<Permission id={self.id} name='{self.name}' "
            f"resource='{self.resource}' action='{self.action}'>"
        )
