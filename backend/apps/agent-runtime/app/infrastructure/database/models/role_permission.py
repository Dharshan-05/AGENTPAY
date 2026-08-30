"""RolePermission ORM model module for AGENTPAY (Phase 025)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.permission import Permission
    from app.infrastructure.database.models.role import Role


class RolePermission(Base):
    """RolePermission ORM entity mapping relationships between roles and permissions."""

    __tablename__ = "role_permissions"

    __table_args__ = (
        UniqueConstraint(
            "role_id", "permission_id", name="uq_role_permissions_role_id_permission_id"
        ),
        Index("ix_role_permissions_role_id", "role_id"),
        Index("ix_role_permissions_permission_id", "permission_id"),
    )

    # Primary key: UUID (UUIDv7)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign key referencing roles.id
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", name="fk_role_permissions_role_id_roles", ondelete="RESTRICT"),
        nullable=False,
    )

    # Foreign key referencing permissions.id
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "permissions.id",
            name="fk_role_permissions_permission_id_permissions",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    # Audit timestamp
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    role: Mapped["Role"] = relationship("Role")
    permission: Mapped["Permission"] = relationship("Permission")

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<RolePermission id={self.id} role_id={self.role_id} "
            f"permission_id={self.permission_id}>"
        )
