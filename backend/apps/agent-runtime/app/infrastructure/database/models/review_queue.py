"""ReviewQueue ORM model module for AGENTPAY (Phase 068)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.commerce_transaction import CommerceTransaction
    from app.infrastructure.database.models.fraud_prediction import FraudPrediction
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.payment_order import PaymentOrder
    from app.infrastructure.database.models.payment_transaction import PaymentTransaction
    from app.infrastructure.database.models.policy_evaluation import PolicyEvaluation
    from app.infrastructure.database.models.policy_rule import PolicyRule
    from app.infrastructure.database.models.risk_signal import RiskSignal
    from app.infrastructure.database.models.security_policy import SecurityPolicy
    from app.infrastructure.database.models.security_violation import SecurityViolation
    from app.infrastructure.database.models.user import User


class ReviewQueue(Base):
    """ReviewQueue ORM entity representing cases requiring human or automated review in AGENTPAY."""

    __tablename__ = "review_queue"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "review_reference",
            name="uq_review_queue_tenant_id_review_reference",
        ),
        CheckConstraint(
            "review_type IN ('security', 'risk', 'fraud', 'payment', 'transaction', "
            "'authorization', 'compliance', 'manual', 'agent', 'commerce')",
            name="review_type",
        ),
        CheckConstraint(
            "status IN ('queued', 'assigned', 'in_review', 'approved', 'rejected', "
            "'escalated', 'resolved', 'cancelled')",
            name="status",
        ),
        CheckConstraint(
            "priority >= 0",
            name="priority_nonnegative",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="severity",
        ),
        CheckConstraint(
            "decision IS NULL OR decision IN ('allow', 'deny', 'approve', 'reject', "
            "'escalate', 'cancel', 'review')",
            name="decision",
        ),
        Index("ix_review_queue_tenant_id", "tenant_id"),
        Index("ix_review_queue_review_reference", "review_reference"),
        Index("ix_review_queue_status", "status"),
        Index("ix_review_queue_priority", "priority"),
        Index("ix_review_queue_tenant_status_priority", "tenant_id", "status", "priority"),
        Index("ix_review_queue_severity", "severity"),
        Index("ix_review_queue_review_type", "review_type"),
        Index("ix_review_queue_assigned_reviewer_id", "assigned_reviewer_id"),
        Index("ix_review_queue_request_id", "request_id"),
        Index("ix_review_queue_queued_at", "queued_at"),
        Index("ix_review_queue_source_id", "source_id"),
        Index("ix_review_queue_security_policy_id", "security_policy_id"),
        Index("ix_review_queue_policy_rule_id", "policy_rule_id"),
        Index("ix_review_queue_policy_evaluation_id", "policy_evaluation_id"),
        Index("ix_review_queue_security_violation_id", "security_violation_id"),
        Index("ix_review_queue_risk_signal_id", "risk_signal_id"),
        Index("ix_review_queue_fraud_prediction_id", "fraud_prediction_id"),
        Index("ix_review_queue_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_review_queue_payment_order_id", "payment_order_id"),
        Index("ix_review_queue_payment_transaction_id", "payment_transaction_id"),
        Index("ix_review_queue_agent_id", "agent_id"),
        Index("ix_review_queue_merchant_id", "merchant_id"),
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

    # Review Identity & References
    review_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    review_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="security",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="queued",
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="medium",
    )

    # Generic Source Correlation
    source_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Optional Domain Foreign Keys (ON DELETE RESTRICT)
    security_policy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_policies.id",
            name="fk_review_queue_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_rules.id",
            name="fk_review_queue_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_evaluations.id",
            name="fk_review_queue_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    security_violation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_violations.id",
            name="fk_review_queue_sec_viol_id_sec_viols",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    risk_signal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "risk_signals.id",
            name="fk_review_queue_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    fraud_prediction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "fraud_predictions.id",
            name="fk_review_queue_fraud_prediction_id_fraud_predictions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_review_queue_ctxn_id_ctxns",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    payment_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_orders.id",
            name="fk_review_queue_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    payment_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_transactions.id",
            name="fk_review_queue_ptxn_id_ptxns",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_review_queue_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_review_queue_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Reviewer Identity (FK -> users.id, ON DELETE RESTRICT)
    assigned_reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_review_queue_assigned_reviewer_id_users",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Request & Description Metadata
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
    review_context: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Review Outcome & Decision Reason
    decision: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    decision_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Lifecycle Timestamps & Soft Delete
    queued_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    assigned_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
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
    security_policy: Mapped[Optional["SecurityPolicy"]] = relationship("SecurityPolicy")
    policy_rule: Mapped[Optional["PolicyRule"]] = relationship("PolicyRule")
    policy_evaluation: Mapped[Optional["PolicyEvaluation"]] = relationship("PolicyEvaluation")
    security_violation: Mapped[Optional["SecurityViolation"]] = relationship("SecurityViolation")
    risk_signal: Mapped[Optional["RiskSignal"]] = relationship("RiskSignal")
    fraud_prediction: Mapped[Optional["FraudPrediction"]] = relationship("FraudPrediction")
    commerce_transaction: Mapped[Optional["CommerceTransaction"]] = relationship(
        "CommerceTransaction"
    )

    payment_order: Mapped[Optional["PaymentOrder"]] = relationship("PaymentOrder")
    payment_transaction: Mapped[Optional["PaymentTransaction"]] = relationship("PaymentTransaction")
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    assigned_reviewer: Mapped[Optional["User"]] = relationship("User")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING review_context and secrets."""
        return (
            f"<ReviewQueue id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.review_reference}' type='{self.review_type}' "
            f"status='{self.status}' priority={self.priority}>"
        )
