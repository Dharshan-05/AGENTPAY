"""ApprovalRequest ORM model module for AGENTPAY (Phase 069)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
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


class ApprovalRequest(Base):
    """ApprovalRequest ORM entity representing multi-approval authorization requests in AGENTPAY."""

    __tablename__ = "approval_requests"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "approval_reference",
            name="uq_approval_requests_tenant_id_approval_reference",
        ),
        CheckConstraint(
            "approval_type IN ('payment', 'transaction', 'refund', 'cancellation', "
            "'security', 'risk', 'fraud', 'commerce', 'agent', 'policy', 'manual')",
            name="approval_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'in_review', 'partially_approved', 'approved', "
            "'rejected', 'expired', 'cancelled')",
            name="status",
        ),
        CheckConstraint(
            "requested_action IN ('authorize', 'capture', 'refund', 'cancel', "
            "'execute', 'allow', 'deny', 'override', 'escalate')",
            name="requested_action",
        ),
        CheckConstraint(
            "priority >= 0",
            name="priority_nonnegative",
        ),
        CheckConstraint(
            "requested_amount IS NULL OR requested_amount >= 0",
            name="requested_amount_nonnegative",
        ),
        CheckConstraint(
            "required_approvals > 0",
            name="required_approvals_positive",
        ),
        CheckConstraint(
            "received_approvals >= 0",
            name="received_approvals_nonnegative",
        ),
        CheckConstraint(
            "received_approvals <= required_approvals",
            name="received_le_required",
        ),
        Index("ix_approval_requests_tenant_id", "tenant_id"),
        Index("ix_approval_requests_approval_reference", "approval_reference"),
        Index("ix_approval_requests_approval_type", "approval_type"),
        Index("ix_approval_requests_status", "status"),
        Index("ix_approval_requests_tenant_status", "tenant_id", "status"),
        Index("ix_approval_requests_priority", "priority"),
        Index("ix_approval_requests_requester_id", "requester_id"),
        Index("ix_approval_requests_target_reviewer_id", "target_reviewer_id"),
        Index("ix_approval_requests_request_id", "request_id"),
        Index("ix_approval_requests_expires_at", "expires_at"),
        Index("ix_approval_requests_requested_at", "requested_at"),
        Index("ix_approval_requests_source_id", "source_id"),
        Index("ix_approval_requests_security_policy_id", "security_policy_id"),
        Index("ix_approval_requests_policy_rule_id", "policy_rule_id"),
        Index("ix_approval_requests_policy_evaluation_id", "policy_evaluation_id"),
        Index("ix_approval_requests_security_violation_id", "security_violation_id"),
        Index("ix_approval_requests_risk_signal_id", "risk_signal_id"),
        Index("ix_approval_requests_fraud_prediction_id", "fraud_prediction_id"),
        Index("ix_approval_requests_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_approval_requests_payment_order_id", "payment_order_id"),
        Index("ix_approval_requests_payment_transaction_id", "payment_transaction_id"),
        Index("ix_approval_requests_agent_id", "agent_id"),
        Index("ix_approval_requests_merchant_id", "merchant_id"),
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

    # Approval Identity & Classification
    approval_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    approval_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="payment",
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    requested_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="authorize",
    )

    # Monetary Amount & Currency (NUMERIC 18,4 Decimal ONLY)
    requested_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4),
        nullable=True,
    )
    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
    )

    # Requester & Target Reviewer Identity (FK -> users.id, ON DELETE RESTRICT)
    requester_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    requester_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_approval_requests_requester_id_users",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    target_reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            name="fk_approval_requests_target_reviewer_id_users",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Approval Counter Thresholds
    required_approvals: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    received_approvals: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Source Correlation
    source_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Optional Domain Foreign Keys (All ON DELETE RESTRICT)
    security_policy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_policies.id",
            name="fk_short_96242783",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_rules.id",
            name="fk_approval_requests_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_evaluations.id",
            name="fk_approval_requests_pol_eval_id_pol_evals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    security_violation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_violations.id",
            name="fk_approval_requests_sec_viol_id_sec_viols",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    risk_signal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "risk_signals.id",
            name="fk_approval_requests_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    fraud_prediction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "fraud_predictions.id",
            name="fk_approval_requests_fraud_pred_id_fraud_preds",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_approval_requests_ctxn_id_ctxns",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    payment_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_orders.id",
            name="fk_approval_requests_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    payment_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_transactions.id",
            name="fk_approval_requests_ptxn_id_ptxns",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_approval_requests_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_approval_requests_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Metadata & Context
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    approval_context: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Lifecycle Timestamps & Expiration
    expires_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )
    requested_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
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
    requester: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[requester_id],
    )
    target_reviewer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[target_reviewer_id],
    )
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

    def __repr__(self) -> str:
        """Return safe string representation REDACTING approval_context and secrets."""
        return (
            f"<ApprovalRequest id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.approval_reference}' type='{self.approval_type}' "
            f"action='{self.requested_action}' status='{self.status}' "
            f"approvals={self.received_approvals}/{self.required_approvals}>"
        )
