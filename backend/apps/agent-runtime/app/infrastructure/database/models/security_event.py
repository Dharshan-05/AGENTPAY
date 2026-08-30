"""SecurityEvent ORM model module for AGENTPAY (Phase 073)."""

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
    from app.infrastructure.database.models.policy_evaluation import PolicyEvaluation
    from app.infrastructure.database.models.risk_signal import RiskSignal
    from app.infrastructure.database.models.security_violation import SecurityViolation
    from app.infrastructure.database.models.user import User


class SecurityEvent(Base):
    """SecurityEvent ORM entity representing normalized security-event history in AGENTPAY."""

    __tablename__ = "security_events"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "event_reference",
            name="uq_security_events_tenant_id_event_reference",
        ),
        CheckConstraint(
            "event_type IN ('authentication', 'authorization', 'policy', 'credential', "
            "'tenant_isolation', 'suspicious_activity', 'security_control', 'attack', 'system')",
            name="event_type",
        ),
        CheckConstraint(
            "event_action IN ('login', 'logout', 'authentication_failed', 'authorization_denied', "
            "'permission_changed', 'credential_used', 'credential_failed', 'policy_blocked', "
            "'policy_violation', 'tenant_boundary_violation', 'suspicious_request', "
            "'attack_detected', 'security_control_triggered', 'security_alert', "
            "'security_reviewed')",
            name="event_action",
        ),
        CheckConstraint(
            "event_result IN ('success', 'failure', 'blocked', 'detected', "
            "'review_required', 'error')",
            name="event_result",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="severity",
        ),
        CheckConstraint(
            "source IN ('internal', 'external', 'agent', 'merchant', 'webhook', "
            "'policy_engine', 'risk_engine', 'siem', 'system')",
            name="source",
        ),
        Index("ix_security_events_tenant_id", "tenant_id"),
        Index("ix_security_events_tenant_occurred_at", "tenant_id", "occurred_at"),
        Index("ix_security_events_event_reference", "event_reference"),
        Index("ix_security_events_event_type", "event_type"),
        Index("ix_security_events_event_action", "event_action"),
        Index("ix_security_events_event_result", "event_result"),
        Index("ix_security_events_severity", "severity"),
        Index("ix_security_events_source", "source"),
        Index("ix_security_events_request_id", "request_id"),
        Index("ix_security_events_actor_id", "actor_id"),
        Index("ix_security_events_user_id", "user_id"),
        Index("ix_security_events_agent_id", "agent_id"),
        Index("ix_security_events_merchant_id", "merchant_id"),
        Index("ix_security_events_security_violation_id", "security_violation_id"),
        Index("ix_security_events_risk_signal_id", "risk_signal_id"),
        Index("ix_security_events_policy_evaluation_id", "policy_evaluation_id"),
        Index("ix_security_events_occurred_at", "occurred_at"),
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

    # Identity & Event References
    event_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Event Categorization & Classification
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="system",
    )
    event_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="security_alert",
    )
    event_result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success",
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
    )
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="internal",
    )

    # Correlation & Network Context
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
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

    # Foreign Keys (All ON DELETE RESTRICT)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_security_events_user_id_users",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_security_events_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_security_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    security_violation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_violations.id",
            name="fk_security_events_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    risk_signal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "risk_signals.id",
            name="fk_security_events_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_evaluations.id",
            name="fk_security_events_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Structured Non-secret Payload
    event_payload: Mapped[dict[str, Any] | None] = mapped_column(
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
    security_violation: Mapped[Optional["SecurityViolation"]] = relationship("SecurityViolation")
    risk_signal: Mapped[Optional["RiskSignal"]] = relationship("RiskSignal")
    policy_evaluation: Mapped[Optional["PolicyEvaluation"]] = relationship("PolicyEvaluation")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING event_payload and secrets."""
        return (
            f"<SecurityEvent id={self.id} tenant_id={self.tenant_id} "
            f"type='{self.event_type}' action='{self.event_action}' "
            f"severity='{self.severity}' result='{self.event_result}'>"
        )
