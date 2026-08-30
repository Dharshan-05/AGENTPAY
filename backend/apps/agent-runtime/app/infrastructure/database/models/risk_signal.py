"""RiskSignal ORM model module for AGENTPAY (Phase 056)."""

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
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.offer import Offer
    from app.infrastructure.database.models.policy_evaluation import PolicyEvaluation
    from app.infrastructure.database.models.policy_rule import PolicyRule
    from app.infrastructure.database.models.product import Product
    from app.infrastructure.database.models.purchase_intent import PurchaseIntent
    from app.infrastructure.database.models.purchase_plan import PurchasePlan
    from app.infrastructure.database.models.security_policy import SecurityPolicy
    from app.infrastructure.database.models.security_violation import SecurityViolation


class RiskSignal(Base):
    """RiskSignal ORM entity representing normalized risk indicators in AGENTPAY."""

    __tablename__ = "risk_signals"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "signal_reference",
            name="uq_risk_signals_tenant_id_signal_reference",
        ),
        CheckConstraint(
            "signal_type IN ('velocity', 'amount', 'frequency', 'authentication', "
            "'authorization', 'behaviour', 'fraud', 'device', 'identity', "
            "'agent_trust', 'merchant', 'product', 'inventory', 'transaction', "
            "'policy', 'compliance', 'geography', 'anomaly', 'spending', 'custom')",
            name="signal_type",
        ),
        CheckConstraint(
            "signal_source IN ('policy_engine', 'rule_engine', 'risk_engine', "
            "'fraud_engine', 'behaviour_engine', 'authentication', 'authorization', "
            "'agent_runtime', 'system', 'manual')",
            name="signal_source",
        ),
        CheckConstraint(
            "status IN ('active', 'inactive', 'expired', 'suppressed', 'resolved')",
            name="status",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="severity",
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
            "expires_at IS NULL OR observed_at <= expires_at",
            name="date_bounds",
        ),
        Index("ix_risk_signals_tenant_id", "tenant_id"),
        Index("ix_risk_signals_security_policy_id", "security_policy_id"),
        Index("ix_risk_signals_policy_rule_id", "policy_rule_id"),
        Index("ix_risk_signals_policy_evaluation_id", "policy_evaluation_id"),
        Index("ix_risk_signals_security_violation_id", "security_violation_id"),
        Index("ix_risk_signals_agent_id", "agent_id"),
        Index("ix_risk_signals_merchant_id", "merchant_id"),
        Index("ix_risk_signals_product_id", "product_id"),
        Index("ix_risk_signals_offer_id", "offer_id"),
        Index("ix_risk_signals_purchase_intent_id", "purchase_intent_id"),
        Index("ix_risk_signals_purchase_plan_id", "purchase_plan_id"),
        Index("ix_risk_signals_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_risk_signals_signal_code", "signal_code"),
        Index("ix_risk_signals_request_id", "request_id"),
        Index("ix_risk_signals_source_reference", "source_reference"),
        Index("ix_risk_signals_status", "status"),
        Index("ix_risk_signals_severity", "severity"),
        Index("ix_risk_signals_signal_type", "signal_type"),
        Index("ix_risk_signals_observed_at", "observed_at"),
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
            name="fk_risk_signals_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_rules.id",
            name="fk_risk_signals_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_evaluations.id",
            name="fk_risk_signals_policy_evaluation_id_policy_evaluations",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    security_violation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_violations.id",
            name="fk_risk_signals_security_violation_id_security_violations",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_risk_signals_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_risk_signals_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_risk_signals_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "offers.id",
            name="fk_risk_signals_offer_id_offers",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_intent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_intents.id",
            name="fk_risk_signals_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_plans.id",
            name="fk_risk_signals_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_risk_signals_commerce_transaction_id_commerce_transactions",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Signal Identity & Classification
    signal_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    signal_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    signal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    signal_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="low",
    )

    # Risk & Numeric Values (NUMERIC Decimal precision)
    risk_score: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )
    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )
    signal_value: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 6),
        nullable=True,
    )

    # JSONB Context (Non-secret structured context)
    signal_context: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    evidence_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )
    metadata_payload: Mapped[dict[str, Any] | None] = mapped_column(
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
    source_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Timestamps & Soft Delete
    observed_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(
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
    security_violation: Mapped[Optional["SecurityViolation"]] = relationship(
        "SecurityViolation",
        back_populates="risk_signals",
    )
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
            f"<RiskSignal id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.signal_reference}' code='{self.signal_code}' "
            f"type='{self.signal_type}' severity='{self.severity}' status='{self.status}'>"
        )
