"""SecurityPolicy ORM model module for AGENTPAY (Phase 051)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.policy_rule import PolicyRule


class SecurityPolicy(Base):
    """SecurityPolicy ORM entity representing security/risk policies in AGENTPAY."""

    __tablename__ = "security_policies"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "slug",
            name="uq_security_policies_tenant_id_slug",
        ),
        CheckConstraint(
            "status IN ('draft', 'active', 'inactive', 'suspended', 'archived')",
            name="status",
        ),
        CheckConstraint(
            "policy_type IN ('authorization', 'transaction', 'fraud', 'risk', "
            "'compliance', 'spending', 'access', 'agent', 'commerce')",
            name="policy_type",
        ),
        CheckConstraint("priority >= 0", name="priority_nonnegative"),
        CheckConstraint(
            "enforcement_mode IN ('enforce', 'monitor', 'warn', 'block')",
            name="enforcement_mode",
        ),
        CheckConstraint("version >= 1", name="version_positive"),
        CheckConstraint(
            "ends_at IS NULL OR starts_at <= ends_at",
            name="date_bounds",
        ),
        Index("ix_security_policies_tenant_id", "tenant_id"),
        Index("ix_security_policies_merchant_id", "merchant_id"),
        Index("ix_security_policies_status", "status"),
        Index("ix_security_policies_policy_type", "policy_type"),
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

    # Foreign keys
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_security_policies_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Identity
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Status & Type
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
    )
    policy_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Enforcement & Versioning
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )
    enforcement_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="enforce",
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    # Activation Window
    starts_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    # Configuration Payload (JSONB, zero secrets)
    configuration: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Lifecycle Timestamps & Soft Delete
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

    # ORM Relationships
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    rules: Mapped[list["PolicyRule"]] = relationship(
        "PolicyRule",
        back_populates="security_policy",
    )

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<SecurityPolicy id={self.id} tenant_id={self.tenant_id} "
            f"name='{self.name}' slug='{self.slug}' status='{self.status}' "
            f"type='{self.policy_type}'>"
        )
