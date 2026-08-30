"""Role ORM model module for AGENTPAY (Phase 023)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class Role(Base):
    """Role ORM entity representing tenant-scoped or system authorization roles."""

    __tablename__ = "roles"

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_id_name"),
        Index("ix_roles_tenant_id", "tenant_id"),
        Index("ix_roles_name", "name"),
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

    # Role name (e.g. "admin", "operator", "viewer")
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Optional description of permissions granted by this role
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # System role flag (true for platform-predefined immutable roles)
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # Role lifecycle status (e.g. "active", "inactive")
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    # Audit & Soft deletion timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<Role id={self.id} tenant_id={self.tenant_id} "
            f"name='{self.name}' is_system={self.is_system}>"
        )
