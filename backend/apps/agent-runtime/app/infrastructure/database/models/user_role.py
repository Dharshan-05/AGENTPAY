"""UserRole ORM model module for AGENTPAY (Phase 026)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.role import Role
    from app.infrastructure.database.models.user import User


class UserRole(Base):
    """UserRole ORM entity mapping relationships between users and roles."""

    __tablename__ = "user_roles"

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_id_role_id"),
        Index("ix_user_roles_tenant_id", "tenant_id"),
        Index("ix_user_roles_user_id", "user_id"),
        Index("ix_user_roles_role_id", "role_id"),
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
        ForeignKey("users.id", name="fk_user_roles_user_id_users", ondelete="RESTRICT"),
        nullable=False,
    )

    # Foreign key referencing roles.id
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", name="fk_user_roles_role_id_roles", ondelete="RESTRICT"),
        nullable=False,
    )

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    user: Mapped["User"] = relationship("User")
    role: Mapped["Role"] = relationship("Role")

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<UserRole id={self.id} tenant_id={self.tenant_id} "
            f"user_id={self.user_id} role_id={self.role_id}>"
        )
