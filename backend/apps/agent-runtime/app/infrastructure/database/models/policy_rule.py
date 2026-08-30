"""PolicyRule ORM model module for AGENTPAY (Phase 052)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.security_policy import SecurityPolicy


class PolicyRule(Base):
    """PolicyRule ORM entity representing a deterministic rule for a SecurityPolicy in AGENTPAY."""

    __tablename__ = "policy_rules"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "security_policy_id",
            "slug",
            name="uq_policy_rules_tenant_id_security_policy_id_slug",
        ),
        CheckConstraint(
            "status IN ('draft', 'active', 'inactive', 'disabled', 'archived')",
            name="status",
        ),
        CheckConstraint(
            "rule_type IN ('threshold', 'allowlist', 'denylist', 'velocity', "
            "'amount', 'frequency', 'geography', 'identity', 'agent_trust', "
            "'merchant', 'product', 'custom')",
            name="rule_type",
        ),
        CheckConstraint("priority >= 0", name="priority_nonnegative"),
        CheckConstraint(
            "operator IN ('eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', "
            "'not_in', 'contains', 'not_contains', 'exists', 'not_exists')",
            name="operator",
        ),
        CheckConstraint(
            "action IN ('allow', 'deny', 'challenge', 'review', 'alert', "
            "'block', 'require_approval')",
            name="action",
        ),
        CheckConstraint(
            "failure_action IN ('deny', 'allow', 'alert', 'review')",
            name="failure_action",
        ),
        CheckConstraint(
            "ends_at IS NULL OR starts_at <= ends_at",
            name="date_bounds",
        ),
        Index("ix_policy_rules_tenant_id", "tenant_id"),
        Index("ix_policy_rules_security_policy_id", "security_policy_id"),
        Index("ix_policy_rules_merchant_id", "merchant_id"),
        Index("ix_policy_rules_status", "status"),
        Index("ix_policy_rules_rule_type", "rule_type"),
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
    security_policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_policies.id",
            name="fk_policy_rules_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_policy_rules_merchant_id_merchants",
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

    # Status & Rule Type
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
    )
    rule_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )

    # Operator & Evaluation Logic
    operator: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    condition_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Action & Failure Behavior
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    failure_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="deny",
    )

    # Activation Window
    starts_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    ends_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
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
    security_policy: Mapped["SecurityPolicy"] = relationship(
        "SecurityPolicy",
        back_populates="rules",
    )
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")

    def __repr__(self) -> str:
        """Return safe string representation."""
        return (
            f"<PolicyRule id={self.id} tenant_id={self.tenant_id} "
            f"name='{self.name}' slug='{self.slug}' status='{self.status}' "
            f"action='{self.action}'>"
        )
