"""XAIExplanation ORM model module for AGENTPAY (Phase 058)."""

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
    Text,
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
    from app.infrastructure.database.models.offer import Offer
    from app.infrastructure.database.models.policy_evaluation import PolicyEvaluation
    from app.infrastructure.database.models.product import Product
    from app.infrastructure.database.models.purchase_intent import PurchaseIntent
    from app.infrastructure.database.models.purchase_plan import PurchasePlan
    from app.infrastructure.database.models.risk_signal import RiskSignal
    from app.infrastructure.database.models.security_violation import SecurityViolation


class XAIExplanation(Base):
    """XAIExplanation ORM entity representing explainable-AI output in AGENTPAY."""

    __tablename__ = "xai_explanations"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "explanation_reference",
            name="uq_xai_explanations_tenant_id_explanation_reference",
        ),
        CheckConstraint(
            "explanation_type IN ('shap', 'feature_importance', 'counterfactual', "
            "'local', 'global', 'hybrid', 'custom')",
            name="explanation_type",
        ),
        CheckConstraint(
            "explanation_status IN ('pending', 'completed', 'failed', 'expired', 'cancelled')",
            name="explanation_status",
        ),
        CheckConstraint(
            "explainer_type IN ('tree_shap', 'kernel_shap', 'linear_shap', "
            "'deep_shap', 'generic_feature_importance', 'custom')",
            name="explainer_type",
        ),
        CheckConstraint(
            "top_feature_count >= 0",
            name="top_feature_count_nonnegative",
        ),
        Index("ix_xai_explanations_tenant_id", "tenant_id"),
        Index("ix_xai_explanations_fraud_prediction_id", "fraud_prediction_id"),
        Index("ix_xai_explanations_risk_signal_id", "risk_signal_id"),
        Index("ix_xai_explanations_security_violation_id", "security_violation_id"),
        Index("ix_xai_explanations_policy_evaluation_id", "policy_evaluation_id"),
        Index("ix_xai_explanations_agent_id", "agent_id"),
        Index("ix_xai_explanations_merchant_id", "merchant_id"),
        Index("ix_xai_explanations_product_id", "product_id"),
        Index("ix_xai_explanations_offer_id", "offer_id"),
        Index("ix_xai_explanations_purchase_intent_id", "purchase_intent_id"),
        Index("ix_xai_explanations_purchase_plan_id", "purchase_plan_id"),
        Index("ix_xai_explanations_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_xai_explanations_explanation_type", "explanation_type"),
        Index("ix_xai_explanations_explanation_status", "explanation_status"),
        Index("ix_xai_explanations_model_reference", "model_reference"),
        Index("ix_xai_explanations_request_id", "request_id"),
        Index("ix_xai_explanations_generated_at", "generated_at"),
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
    fraud_prediction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "fraud_predictions.id",
            name="fk_xai_explanations_fraud_prediction_id_fraud_predictions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    risk_signal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "risk_signals.id",
            name="fk_xai_explanations_risk_signal_id_risk_signals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    security_violation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_violations.id",
            name="fk_xai_explanations_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_evaluations.id",
            name="fk_xai_explanations_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_xai_explanations_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_xai_explanations_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_xai_explanations_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "offers.id",
            name="fk_xai_explanations_offer_id_offers",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_intent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_intents.id",
            name="fk_xai_explanations_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_plans.id",
            name="fk_xai_explanations_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_xai_explanations_commerce_transaction_id_commerce_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Explanation Identity & Classification
    explanation_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    explanation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    explanation_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="completed",
    )
    model_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    explainer_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Numerical Values (Signed NUMERIC 18,8 Decimal)
    base_value: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 8),
        nullable=True,
    )
    prediction_value: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 8),
        nullable=True,
    )

    # Feature Counts & JSONB Structured Payloads (Non-secret)
    top_feature_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    feature_importance: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    shap_values: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    feature_snapshot: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    explanation_context: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    explanation_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Summaries
    summary: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    reasoning_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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
    generated_at: Mapped[datetime] = mapped_column(
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
    fraud_prediction: Mapped[Optional["FraudPrediction"]] = relationship(
        "FraudPrediction",
        back_populates="xai_explanations",
    )
    risk_signal: Mapped[Optional["RiskSignal"]] = relationship("RiskSignal")
    security_violation: Mapped[Optional["SecurityViolation"]] = relationship("SecurityViolation")
    policy_evaluation: Mapped[Optional["PolicyEvaluation"]] = relationship("PolicyEvaluation")
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    product: Mapped[Optional["Product"]] = relationship("Product")
    offer: Mapped[Optional["Offer"]] = relationship("Offer")
    purchase_intent: Mapped[Optional["PurchaseIntent"]] = relationship("PurchaseIntent")
    purchase_plan: Mapped[Optional["PurchasePlan"]] = relationship("PurchasePlan")
    commerce_transaction: Mapped[Optional["CommerceTransaction"]] = relationship(
        "CommerceTransaction"
    )

    def __repr__(self) -> str:
        """Return safe string representation excluding JSONB payloads."""
        return (
            f"<XAIExplanation id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.explanation_reference}' type='{self.explanation_type}' "
            f"explainer='{self.explainer_type}' status='{self.explanation_status}'>"
        )
