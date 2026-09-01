"""SecurityViolation ORM model module for AGENTPAY (Phase 055)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
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
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.offer import Offer
    from app.infrastructure.database.models.policy_evaluation import PolicyEvaluation
    from app.infrastructure.database.models.policy_rule import PolicyRule
    from app.infrastructure.database.models.product import Product
    from app.infrastructure.database.models.purchase_intent import PurchaseIntent
    from app.infrastructure.database.models.purchase_plan import PurchasePlan
    from app.infrastructure.database.models.risk_signal import RiskSignal
    from app.infrastructure.database.models.security_policy import SecurityPolicy


class SecurityViolation(Base):
    """SecurityViolation ORM entity representing detected security violations in AGENTPAY."""

    __tablename__ = "security_violations"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "violation_reference",
            name="uq_security_violations_tenant_id_violation_reference",
        ),
        CheckConstraint(
            "violation_type IN ('authentication', 'authorization', 'policy', 'fraud', "
            "'risk', 'compliance', 'spending', 'access', 'agent', 'commerce', "
            "'transaction', 'inventory', 'credential', 'tenant_isolation', 'system')",
            name="violation_type",
        ),
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="severity",
        ),
        CheckConstraint(
            "status IN ('open', 'investigating', 'confirmed', 'resolved', "
            "'dismissed', 'false_positive')",
            name="status",
        ),
        CheckConstraint(
            "detection_source IN ('policy_engine', 'rule_engine', 'risk_engine', "
            "'fraud_engine', 'authentication', 'authorization', 'agent_runtime', "
            "'system', 'manual')",
            name="detection_source",
        ),
        CheckConstraint(
            "risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100)",
            name="risk_score_bounds",
        ),
        CheckConstraint(
            "impact_score IS NULL OR (impact_score >= 0 AND impact_score <= 100)",
            name="impact_score_bounds",
        ),
        CheckConstraint(
            "acknowledged_at IS NULL OR detected_at <= acknowledged_at",
            name="acknowledged_bounds",
        ),
        CheckConstraint(
            "resolved_at IS NULL OR detected_at <= resolved_at",
            name="resolved_bounds",
        ),
        Index("ix_security_violations_tenant_id", "tenant_id"),
        Index("ix_security_violations_security_policy_id", "security_policy_id"),
        Index("ix_security_violations_policy_rule_id", "policy_rule_id"),
        Index("ix_security_violations_policy_evaluation_id", "policy_evaluation_id"),
        Index("ix_security_violations_agent_id", "agent_id"),
        Index("ix_security_violations_merchant_id", "merchant_id"),
        Index("ix_security_violations_product_id", "product_id"),
        Index("ix_security_violations_offer_id", "offer_id"),
        Index("ix_security_violations_purchase_intent_id", "purchase_intent_id"),
        Index("ix_security_violations_purchase_plan_id", "purchase_plan_id"),
        Index("ix_security_violations_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_security_violations_violation_reference", "violation_reference"),
        Index("ix_security_violations_violation_code", "violation_code"),
        Index("ix_security_violations_request_id", "request_id"),
        Index("ix_security_violations_status", "status"),
        Index("ix_security_violations_severity", "severity"),
        Index("ix_security_violations_violation_type", "violation_type"),
        Index("ix_security_violations_detected_at", "detected_at"),
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
            name="fk_sec_viols_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_rules.id",
            name="fk_security_violations_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_evaluations.id",
            name="fk_sec_viols_pol_eval_id_pol_evals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_security_violations_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_security_violations_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_security_violations_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "offers.id",
            name="fk_security_violations_offer_id_offers",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_intent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_intents.id",
            name="fk_sec_viols_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_plans.id",
            name="fk_security_violations_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_sec_viols_ctxn_id_ctxns",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Violation Identity & Categorization
    violation_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    violation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
    )
    detection_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Details & Context
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    violation_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
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

    # Risk & Impact Scores (NUMERIC 8,4 Decimal)
    risk_score: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )
    impact_score: Mapped[Decimal | None] = mapped_column(
        Numeric(8, 4),
        nullable=True,
    )

    # JSONB Payloads (Non-secret structured context)
    violation_context: Mapped[dict[str, Any] | None] = mapped_column(
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
    resolution_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        server_default="{}",
    )

    # Timestamps & Soft Delete
    detected_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(
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
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    product: Mapped[Optional["Product"]] = relationship("Product")
    offer: Mapped[Optional["Offer"]] = relationship("Offer")
    purchase_intent: Mapped[Optional["PurchaseIntent"]] = relationship("PurchaseIntent")
    purchase_plan: Mapped[Optional["PurchasePlan"]] = relationship("PurchasePlan")
    commerce_transaction: Mapped[Optional["CommerceTransaction"]] = relationship(
        "CommerceTransaction"
    )
    risk_signals: Mapped[list["RiskSignal"]] = relationship(
        "RiskSignal",
        back_populates="security_violation",
    )

    def __repr__(self) -> str:
        """Return safe string representation excluding JSONB payloads."""

        return (
            f"<SecurityViolation id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.violation_reference}' type='{self.violation_type}' "
            f"code='{self.violation_code}' severity='{self.severity}' status='{self.status}'>"
        )
