"""PolicyEvaluation ORM model module for AGENTPAY (Phase 053)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base

if TYPE_CHECKING:
    from app.infrastructure.database.models.agent import Agent
    from app.infrastructure.database.models.behaviour_event import BehaviourEvent
    from app.infrastructure.database.models.commerce_transaction import CommerceTransaction
    from app.infrastructure.database.models.merchant import Merchant
    from app.infrastructure.database.models.offer import Offer
    from app.infrastructure.database.models.policy_rule import PolicyRule
    from app.infrastructure.database.models.product import Product
    from app.infrastructure.database.models.purchase_intent import PurchaseIntent
    from app.infrastructure.database.models.purchase_plan import PurchasePlan
    from app.infrastructure.database.models.security_policy import SecurityPolicy


class PolicyEvaluation(Base):
    """PolicyEvaluation ORM entity representing policy evaluation results in AGENTPAY."""

    __tablename__ = "policy_evaluations"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "evaluation_reference",
            name="uq_policy_evaluations_tenant_id_evaluation_reference",
        ),
        CheckConstraint(
            "evaluation_type IN ('authorization', 'transaction', 'fraud', 'risk', "
            "'compliance', 'spending', 'access', 'agent', 'commerce')",
            name="evaluation_type",
        ),
        CheckConstraint(
            "decision IN ('allow', 'deny', 'challenge', 'review', 'alert', "
            "'block', 'require_approval')",
            name="decision",
        ),
        CheckConstraint(
            "result IN ('success', 'failure', 'error', 'skipped')",
            name="result",
        ),
        CheckConstraint(
            "status IN ('pending', 'completed', 'failed', 'expired', 'cancelled')",
            name="status",
        ),
        CheckConstraint("priority >= 0", name="priority_nonnegative"),
        CheckConstraint("evaluation_version > 0", name="version_positive"),
        Index("ix_policy_evaluations_tenant_id", "tenant_id"),
        Index("ix_policy_evaluations_security_policy_id", "security_policy_id"),
        Index("ix_policy_evaluations_policy_rule_id", "policy_rule_id"),
        Index("ix_policy_evaluations_merchant_id", "merchant_id"),
        Index("ix_policy_evaluations_agent_id", "agent_id"),
        Index("ix_policy_evaluations_product_id", "product_id"),
        Index("ix_policy_evaluations_offer_id", "offer_id"),
        Index("ix_policy_evaluations_purchase_intent_id", "purchase_intent_id"),
        Index("ix_policy_evaluations_purchase_plan_id", "purchase_plan_id"),
        Index("ix_policy_evaluations_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_policy_evaluations_evaluation_type", "evaluation_type"),
        Index("ix_policy_evaluations_decision", "decision"),
        Index("ix_policy_evaluations_status", "status"),
        Index("ix_policy_evaluations_evaluated_at", "evaluated_at"),
        Index("ix_policy_evaluations_request_id", "request_id"),
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

    # Foreign Keys
    security_policy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "security_policies.id",
            name="fk_pol_evals_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_rules.id",
            name="fk_policy_evaluations_policy_rule_id_policy_rules",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_policy_evaluations_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_policy_evaluations_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_policy_evaluations_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "offers.id",
            name="fk_policy_evaluations_offer_id_offers",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_intent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_intents.id",
            name="fk_pol_evals_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_plans.id",
            name="fk_policy_evaluations_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_pol_evals_ctxn_id_ctxns",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Identifiers & Correlation
    evaluation_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Evaluation Categorization & Decision
    evaluation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    decision: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="completed",
    )

    # Versioning & Priority
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )
    evaluation_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    # Context & Payloads (JSONB, zero secrets)
    condition_result: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    evaluation_context: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Failure / Error Details
    failure_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    failure_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # Timestamps
    evaluated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    security_policy: Mapped[Optional["SecurityPolicy"]] = relationship("SecurityPolicy")
    policy_rule: Mapped[Optional["PolicyRule"]] = relationship("PolicyRule")
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    product: Mapped[Optional["Product"]] = relationship("Product")
    offer: Mapped[Optional["Offer"]] = relationship("Offer")
    purchase_intent: Mapped[Optional["PurchaseIntent"]] = relationship("PurchaseIntent")
    purchase_plan: Mapped[Optional["PurchasePlan"]] = relationship("PurchasePlan")
    commerce_transaction: Mapped[Optional["CommerceTransaction"]] = relationship(
        "CommerceTransaction"
    )

    behaviour_events: Mapped[list["BehaviourEvent"]] = relationship(
        "BehaviourEvent",
        back_populates="policy_evaluation",
    )

    def __repr__(self) -> str:
        """Return safe string representation excluding sensitive context/payloads."""
        return (
            f"<PolicyEvaluation id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.evaluation_reference}' type='{self.evaluation_type}' "
            f"decision='{self.decision}' result='{self.result}' status='{self.status}'>"
        )
