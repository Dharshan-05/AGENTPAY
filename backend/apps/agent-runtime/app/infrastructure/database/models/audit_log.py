"""AuditLog ORM model module for AGENTPAY (Phase 072)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.user import User


class AuditLog(Base):
    """AuditLog ORM entity representing platform-wide immutable audit trail in AGENTPAY."""

    __tablename__ = "audit_logs"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "audit_reference",
            name="uq_audit_logs_tenant_id_audit_reference",
        ),
        CheckConstraint(
            "category IN ('authentication', 'authorization', 'security', 'policy', "
            "'commerce', 'payment', 'approval', 'review', 'configuration', 'agent', "
            "'merchant', 'system')",
            name="category",
        ),
        CheckConstraint(
            "result IN ('success', 'failure', 'denied', 'error')",
            name="result",
        ),
        Index("ix_audit_logs_tenant_id", "tenant_id"),
        Index("ix_audit_logs_tenant_occurred_at", "tenant_id", "occurred_at"),
        Index("ix_audit_logs_audit_reference", "audit_reference"),
        Index("ix_audit_logs_actor_type", "actor_type"),
        Index("ix_audit_logs_actor_id", "actor_id"),
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_agent_id", "agent_id"),
        Index("ix_audit_logs_merchant_id", "merchant_id"),
        Index("ix_audit_logs_resource_type", "resource_type"),
        Index("ix_audit_logs_resource_id", "resource_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_category", "category"),
        Index("ix_audit_logs_result", "result"),
        Index("ix_audit_logs_request_id", "request_id"),
        Index("ix_audit_logs_correlation_id", "correlation_id"),
        Index("ix_audit_logs_occurred_at", "occurred_at"),
    )

    # Primary Key (UUIDv7)
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

    # Audit Identity & Reference
    audit_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Actor Tracking
    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_audit_logs_user_id_users",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_audit_logs_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_audit_logs_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Resource Identification
    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Action & Outcome Classification
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="system",
    )
    result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success",
    )

    # Correlation & Network Context
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # State Diffs & Metadata Payloads (NO SECRETS)
    before_state: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    after_state: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Timestamps (APPEND-ONLY: NO updated_at or deleted_at)
    occurred_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    user: Mapped[Optional["User"]] = relationship("User")
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING before/after/metadata JSONB and secrets."""
        return (
            f"<AuditLog id={self.id} tenant_id={self.tenant_id} "
            f"category='{self.category}' action='{self.action}' "
            f"result='{self.result}'>"
        )
