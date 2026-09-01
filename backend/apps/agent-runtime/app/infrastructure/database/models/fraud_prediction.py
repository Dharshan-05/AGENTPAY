"""FraudPrediction ORM model module for AGENTPAY (Phase 057)."""

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
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.offer import Offer
    from app.infrastructure.database.models.policy_evaluation import PolicyEvaluation
    from app.infrastructure.database.models.policy_rule import PolicyRule
    from app.infrastructure.database.models.product import Product
    from app.infrastructure.database.models.purchase_intent import PurchaseIntent
    from app.infrastructure.database.models.purchase_plan import PurchasePlan
    from app.infrastructure.database.models.risk_signal import RiskSignal
    from app.infrastructure.database.models.security_policy import SecurityPolicy
    from app.infrastructure.database.models.security_violation import SecurityViolation
    from app.infrastructure.database.models.xai_explanation import XAIExplanation


class FraudPrediction(Base):
    """FraudPrediction ORM entity representing fraud-model predictions in AGENTPAY."""

    __tablename__ = "fraud_predictions"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "prediction_reference",
            name="uq_fraud_predictions_tenant_id_prediction_reference",
        ),
        CheckConstraint(
            "prediction_type IN ('transaction', 'payment', 'purchase', 'account', "
            "'agent', 'merchant', 'identity', 'behaviour', 'commerce', 'custom')",
            name="prediction_type",
        ),
        CheckConstraint(
            "prediction_status IN ('pending', 'completed', 'failed', 'expired', 'cancelled')",
            name="prediction_status",
        ),
        CheckConstraint(
            "prediction_label IN ('legitimate', 'suspicious', 'fraud', 'unknown')",
            name="prediction_label",
        ),
        CheckConstraint(
            "fraud_probability IS NULL OR (fraud_probability >= 0 AND fraud_probability <= 1)",
            name="fraud_probability_bounds",
        ),
        CheckConstraint(
            "legitimate_probability IS NULL OR "
            "(legitimate_probability >= 0 AND legitimate_probability <= 1)",
            name="legitimate_probability_bounds",
        ),
        CheckConstraint(
            "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)",
            name="risk_score_bounds",
        ),
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
            name="confidence_score_bounds",
        ),
        CheckConstraint(
            "feature_count >= 0",
            name="feature_count_nonnegative",
        ),
        CheckConstraint(
            "fraud_probability IS NULL OR legitimate_probability IS NULL OR "
            "(fraud_probability + legitimate_probability BETWEEN 0.99 AND 1.01)",
            name="probability_consistency",
        ),
        Index("ix_fraud_predictions_tenant_id", "tenant_id"),
        Index("ix_fraud_predictions_security_policy_id", "security_policy_id"),
        Index("ix_fraud_predictions_policy_rule_id", "policy_rule_id"),
        Index("ix_fraud_predictions_policy_evaluation_id", "policy_evaluation_id"),
        Index("ix_fraud_predictions_security_violation_id", "security_violation_id"),
        Index("ix_fraud_predictions_risk_signal_id", "risk_signal_id"),
        Index("ix_fraud_predictions_agent_id", "agent_id"),
        Index("ix_fraud_predictions_merchant_id", "merchant_id"),
        Index("ix_fraud_predictions_product_id", "product_id"),
        Index("ix_fraud_predictions_offer_id", "offer_id"),
        Index("ix_fraud_predictions_purchase_intent_id", "purchase_intent_id"),
        Index("ix_fraud_predictions_purchase_plan_id", "purchase_plan_id"),
        Index("ix_fraud_predictions_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_fraud_predictions_prediction_type", "prediction_type"),
        Index("ix_fraud_predictions_prediction_status", "prediction_status"),
        Index("ix_fraud_predictions_prediction_label", "prediction_label"),
        Index("ix_fraud_predictions_model_reference", "model_reference"),
        Index("ix_fraud_predictions_request_id", "request_id"),
        Index("ix_fraud_predictions_predicted_at", "predicted_at"),
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

    # Foreign Keys (All ON DELETE RESTRICT)
    security_policy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_policies.id",
            name="fk_fraud_preds_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_rules.id",
            name="fk_fraud_predictions_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_evaluations.id",
            name="fk_fraud_preds_pol_eval_id_pol_evals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    security_violation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_violations.id",
            name="fk_fraud_preds_sec_viol_id_sec_viols",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    risk_signal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "risk_signals.id",
            name="fk_fraud_predictions_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_fraud_predictions_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_fraud_predictions_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_fraud_predictions_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "offers.id",
            name="fk_fraud_predictions_offer_id_offers",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_intent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_intents.id",
            name="fk_fraud_preds_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_plans.id",
            name="fk_fraud_predictions_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_fraud_preds_ctxn_id_ctxns",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Prediction Identity & Model Metadata
    prediction_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    model_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    prediction_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    prediction_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="completed",
    )
    prediction_label: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Probabilities & Scores (NUMERIC 8,4 Decimal)
    fraud_probability: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )
    legitimate_probability: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )
    risk_score: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )
    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )

    # Model Features
    feature_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # JSONB Structured Payloads (Non-secret)
    feature_snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    prediction_context: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    prediction_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Correlation & Actor Context
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    actor_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # Timestamps & Soft Delete
    predicted_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
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
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    product: Mapped[Optional["Product"]] = relationship("Product")
    offer: Mapped[Optional["Offer"]] = relationship("Offer")
    purchase_intent: Mapped[Optional["PurchaseIntent"]] = relationship("PurchaseIntent")
    purchase_plan: Mapped[Optional["PurchasePlan"]] = relationship("PurchasePlan")
    commerce_transaction: Mapped[Optional["CommerceTransaction"]] = relationship(
        "CommerceTransaction"
    )
    xai_explanations: Mapped[list["XAIExplanation"]] = relationship(
        "XAIExplanation",
        back_populates="fraud_prediction",
    )

    def __repr__(self) -> str:
        """Return safe string representation excluding JSONB payloads."""
        return (
            f"<FraudPrediction id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.prediction_reference}' model='{self.model_reference}' "
            f"label='{self.prediction_label}' status='{self.prediction_status}'>"
        )
