"""RiskDecisionAudit ORM model module for AGENTPAY (Phase 075)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.commerce_transaction import CommerceTransaction
    from app.infrastructure.database.models.fraud_prediction import FraudPrediction
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.payment_transaction import PaymentTransaction
    from app.infrastructure.database.models.policy_evaluation import PolicyEvaluation
    from app.infrastructure.database.models.policy_rule import PolicyRule
    from app.infrastructure.database.models.risk_signal import RiskSignal
    from app.infrastructure.database.models.security_policy import SecurityPolicy
    from app.infrastructure.database.models.security_violation import SecurityViolation


class RiskDecisionAudit(Base):
    """RiskDecisionAudit ORM entity representing risk engine decision audits in AGENTPAY."""

    __tablename__ = "risk_decision_audits"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "decision_reference",
            name="uq_risk_decision_audits_tenant_id_decision_reference",
        ),
        CheckConstraint(
            "decision_type IN ('authorization', 'transaction', 'fraud', 'risk', "
            "'payment', 'commerce', 'spending', 'agent', 'security')",
            name="decision_type",
        ),
        CheckConstraint(
            "decision IN ('allow', 'deny', 'challenge', 'review', 'block', 'require_approval')",
            name="decision",
        ),
        CheckConstraint(
            "result IN ('success', 'failure', 'error', 'skipped')",
            name="result",
        ),
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 100",
            name="risk_score_bounds",
        ),
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name="confidence_score_bounds",
        ),
        Index("ix_risk_decision_audits_tenant_id", "tenant_id"),
        Index("ix_risk_decision_audits_tenant_occurred_at", "tenant_id", "occurred_at"),
        Index("ix_risk_decision_audits_decision_reference", "decision_reference"),
        Index("ix_risk_decision_audits_request_id", "request_id"),
        Index("ix_risk_decision_audits_decision_type", "decision_type"),
        Index("ix_risk_decision_audits_decision", "decision"),
        Index("ix_risk_decision_audits_result", "result"),
        Index("ix_risk_decision_audits_decision_source", "decision_source"),
        Index("ix_risk_decision_audits_model_name", "model_name"),
        Index("ix_risk_decision_audits_policy_evaluation_id", "policy_evaluation_id"),
        Index("ix_risk_decision_audits_security_policy_id", "security_policy_id"),
        Index("ix_risk_decision_audits_policy_rule_id", "policy_rule_id"),
        Index("ix_risk_decision_audits_risk_signal_id", "risk_signal_id"),
        Index("ix_risk_decision_audits_fraud_prediction_id", "fraud_prediction_id"),
        Index("ix_risk_decision_audits_security_violation_id", "security_violation_id"),
        Index("ix_risk_decision_audits_agent_id", "agent_id"),
        Index("ix_risk_decision_audits_merchant_id", "merchant_id"),
        Index("ix_risk_decision_audits_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_risk_decision_audits_payment_transaction_id", "payment_transaction_id"),
        Index("ix_risk_decision_audits_occurred_at", "occurred_at"),
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

    # Decision Identity & Correlation
    decision_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Decision Categorization & Classification
    decision_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="transaction",
    )
    decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="allow",
    )
    result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success",
    )
    decision_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="risk_engine",
    )

    # Scores (NUMERIC Decimal Precision)
    risk_score: Mapped[Decimal] = mapped_column(
        Numeric(8, 4),
        nullable=False,
    )
    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(8, 4),
        nullable=False,
    )

    # Model Traceability
    model_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    model_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # Foreign Keys (All ON DELETE RESTRICT)
    policy_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_evaluations.id",
            name="fk_risk_decision_audits_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    security_policy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_policies.id",
            name="fk_risk_decision_audits_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_rules.id",
            name="fk_risk_decision_audits_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    risk_signal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "risk_signals.id",
            name="fk_risk_decision_audits_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    fraud_prediction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "fraud_predictions.id",
            name="fk_risk_decision_audits_fraud_prediction_id_fraud_predictions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    security_violation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_violations.id",
            name="fk_risk_decision_audits_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_risk_decision_audits_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_risk_decision_audits_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_risk_decision_audits_commerce_transaction_id_commerce_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    payment_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "payment_transactions.id",
            name="fk_risk_decision_audits_payment_transaction_id_payment_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Rationale & Sanitized Context Summaries (NO SECRETS)
    decision_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    decision_context: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    input_summary: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    output_summary: Mapped[dict[str, Any] | None] = mapped_column(
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
    policy_evaluation: Mapped[Optional["PolicyEvaluation"]] = relationship("PolicyEvaluation")
    security_policy: Mapped[Optional["SecurityPolicy"]] = relationship("SecurityPolicy")
    policy_rule: Mapped[Optional["PolicyRule"]] = relationship("PolicyRule")
    risk_signal: Mapped[Optional["RiskSignal"]] = relationship("RiskSignal")
    fraud_prediction: Mapped[Optional["FraudPrediction"]] = relationship("FraudPrediction")
    security_violation: Mapped[Optional["SecurityViolation"]] = relationship("SecurityViolation")
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    commerce_transaction: Mapped[Optional["CommerceTransaction"]] = relationship(
        "CommerceTransaction"
    )

    payment_transaction: Mapped[Optional["PaymentTransaction"]] = relationship("PaymentTransaction")

    def __repr__(self) -> str:
        """Return safe string representation REDACTING JSONB summaries and secrets."""
        return (
            f"<RiskDecisionAudit id={self.id} tenant_id={self.tenant_id} "
            f"type='{self.decision_type}' decision='{self.decision}' "
            f"result='{self.result}'>"
        )
