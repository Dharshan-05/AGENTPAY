"""BehaviourEvent ORM model module for AGENTPAY (Phase 054)."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
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
    from app.infrastructure.database.models.product import Product
    from app.infrastructure.database.models.purchase_intent import PurchaseIntent
    from app.infrastructure.database.models.purchase_plan import PurchasePlan


class BehaviourEvent(Base):
    """BehaviourEvent ORM entity representing an append-only behavioral/audit event in AGENTPAY."""

    __tablename__ = "behaviour_events"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "event_reference",
            name="uq_behaviour_events_tenant_id_event_reference",
        ),
        UniqueConstraint(
            "tenant_id",
            "sequence_number",
            name="uq_behaviour_events_tenant_id_sequence_number",
        ),
        CheckConstraint(
            "event_type IN ('agent', 'authentication', 'authorization', 'policy', "
            "'commerce', 'purchase', 'inventory', 'merchant', 'product', "
            "'offer', 'transaction', 'system')",
            name="event_type",
        ),
        CheckConstraint(
            "event_action IN ('created', 'requested', 'approved', 'rejected', "
            "'executed', 'completed', 'failed', 'cancelled', 'viewed', "
            "'selected', 'initiated', 'updated', 'deleted', 'evaluated')",
            name="event_action",
        ),
        CheckConstraint(
            "event_result IN ('success', 'failure', 'pending', 'skipped')",
            name="event_result",
        ),
        CheckConstraint("sequence_number >= 0", name="sequence_nonnegative"),
        Index("ix_behaviour_events_tenant_id", "tenant_id"),
        Index("ix_behaviour_events_event_type", "event_type"),
        Index("ix_behaviour_events_event_action", "event_action"),
        Index("ix_behaviour_events_event_result", "event_result"),
        Index("ix_behaviour_events_agent_id", "agent_id"),
        Index("ix_behaviour_events_merchant_id", "merchant_id"),
        Index("ix_behaviour_events_product_id", "product_id"),
        Index("ix_behaviour_events_offer_id", "offer_id"),
        Index("ix_behaviour_events_purchase_intent_id", "purchase_intent_id"),
        Index("ix_behaviour_events_purchase_plan_id", "purchase_plan_id"),
        Index("ix_behaviour_events_commerce_transaction_id", "commerce_transaction_id"),
        Index("ix_behaviour_events_policy_evaluation_id", "policy_evaluation_id"),
        Index("ix_behaviour_events_request_id", "request_id"),
        Index("ix_behaviour_events_occurred_at", "occurred_at"),
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

    # Reference & Event Classification
    event_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    event_action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    event_result: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="success",
    )

    # Foreign Keys
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            name="fk_behaviour_events_agent_id_agents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    merchant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "merchants.id",
            name="fk_behaviour_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "products.id",
            name="fk_behaviour_events_product_id_products",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "offers.id",
            name="fk_behaviour_events_offer_id_offers",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_intent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_intents.id",
            name="fk_behaviour_events_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    purchase_plan_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "purchase_plans.id",
            name="fk_behaviour_events_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    commerce_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "commerce_transactions.id",
            name="fk_behaviour_events_ctxn_id_ctxns",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )
    policy_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "policy_evaluations.id",
            name="fk_behaviour_events_pol_eval_id_pol_evals",
            ondelete="RESTRICT",
        ),
        nullable=True,
    )

    # Context & Actor Attributes
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

    # Sequence Number & Payload (JSONB, zero secrets)
    sequence_number: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    event_payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Append-Only Timestamps (NO updated_at, NO deleted_at)
    occurred_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
    )

    # ORM Relationships
    agent: Mapped[Optional["Agent"]] = relationship("Agent")
    merchant: Mapped[Optional["Merchant"]] = relationship("Merchant")
    product: Mapped[Optional["Product"]] = relationship("Product")
    offer: Mapped[Optional["Offer"]] = relationship("Offer")
    purchase_intent: Mapped[Optional["PurchaseIntent"]] = relationship("PurchaseIntent")
    purchase_plan: Mapped[Optional["PurchasePlan"]] = relationship("PurchasePlan")
    commerce_transaction: Mapped[Optional["CommerceTransaction"]] = relationship(
        "CommerceTransaction"
    )

    policy_evaluation: Mapped[Optional["PolicyEvaluation"]] = relationship(
        "PolicyEvaluation",
        back_populates="behaviour_events",
    )

    def __repr__(self) -> str:
        """Return safe string representation excluding event payload and actor context."""
        return (
            f"<BehaviourEvent id={self.id} tenant_id={self.tenant_id} "
            f"reference='{self.event_reference}' type='{self.event_type}' "
            f"action='{self.event_action}' result='{self.event_result}' "
            f"seq={self.sequence_number}>"
        )
