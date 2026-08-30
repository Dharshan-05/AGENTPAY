"""commerce_transactions_and_events

Revision ID: 015_commerce_transactions_and_events
Revises: 014_purchase_intents_and_plans
Create Date: 2026-08-25 23:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "015_commerce_transactions_and_events"
down_revision: str | None = "014_purchase_intents_and_plans"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create commerce_transactions table
    op.create_table(
        "commerce_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_intent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("transaction_reference", sa.String(length=100), nullable=False),
        sa.Column("external_reference", sa.String(length=100), nullable=True),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column(
            "quantity", sa.Numeric(precision=18, scale=3), nullable=False, server_default="1.000"
        ),
        sa.Column("amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column(
            "tax_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0.0000"
        ),
        sa.Column(
            "discount_amount",
            sa.Numeric(precision=18, scale=4),
            nullable=False,
            server_default="0.0000",
        ),
        sa.Column(
            "fee_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0.0000"
        ),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column(
            "refunded_amount",
            sa.Numeric(precision=18, scale=4),
            nullable=False,
            server_default="0.0000",
        ),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("payment_provider", sa.String(length=100), nullable=True),
        sa.Column("provider_transaction_reference", sa.String(length=100), nullable=True),
        sa.Column("provider_authorization_reference", sa.String(length=100), nullable=True),
        sa.Column(
            "metadata_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("authorized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("refunded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "transaction_type IN ('purchase', 'authorization', 'capture', 'refund', 'void', 'adjustment')",  # noqa: E501
            name="ck_commerce_transactions_transaction_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'authorized', 'completed', 'failed', 'cancelled', 'refunded', 'partially_refunded')",  # noqa: E501
            name="ck_commerce_transactions_status",
        ),
        sa.CheckConstraint("quantity > 0", name="ck_commerce_transactions_quantity_positive"),
        sa.CheckConstraint("amount >= 0", name="ck_commerce_transactions_amount_nonnegative"),
        sa.CheckConstraint("subtotal >= 0", name="ck_commerce_transactions_subtotal_nonnegative"),
        sa.CheckConstraint("tax_amount >= 0", name="ck_commerce_transactions_tax_nonnegative"),
        sa.CheckConstraint(
            "discount_amount >= 0", name="ck_commerce_transactions_discount_nonnegative"
        ),
        sa.CheckConstraint("fee_amount >= 0", name="ck_commerce_transactions_fee_nonnegative"),
        sa.CheckConstraint("total_amount >= 0", name="ck_commerce_transactions_total_nonnegative"),
        sa.CheckConstraint(
            "refunded_amount >= 0", name="ck_commerce_transactions_refunded_nonnegative"
        ),
        sa.CheckConstraint(
            "refunded_amount <= total_amount", name="ck_commerce_transactions_refund_bounds"
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_commerce_transactions_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_commerce_transactions_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_commerce_transactions_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_commerce_transactions_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_intent_id"],
            ["purchase_intents.id"],
            name="fk_commerce_transactions_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_plan_id"],
            ["purchase_plans.id"],
            name="fk_commerce_transactions_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_commerce_transactions"),
        sa.UniqueConstraint(
            "tenant_id",
            "transaction_reference",
            name="uq_commerce_transactions_tenant_id_transaction_reference",
        ),
    )
    op.create_index(
        "ix_commerce_transactions_tenant_id", "commerce_transactions", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_commerce_transactions_merchant_id",
        "commerce_transactions",
        ["merchant_id"],
        unique=False,
    )
    op.create_index(
        "ix_commerce_transactions_agent_id", "commerce_transactions", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_commerce_transactions_product_id", "commerce_transactions", ["product_id"], unique=False
    )
    op.create_index(
        "ix_commerce_transactions_offer_id", "commerce_transactions", ["offer_id"], unique=False
    )
    op.create_index(
        "ix_commerce_transactions_purchase_intent_id",
        "commerce_transactions",
        ["purchase_intent_id"],
        unique=False,
    )
    op.create_index(
        "ix_commerce_transactions_purchase_plan_id",
        "commerce_transactions",
        ["purchase_plan_id"],
        unique=False,
    )
    op.create_index(
        "ix_commerce_transactions_external_reference",
        "commerce_transactions",
        ["external_reference"],
        unique=False,
    )
    op.create_index(
        "ix_commerce_transactions_transaction_type",
        "commerce_transactions",
        ["transaction_type"],
        unique=False,
    )
    op.create_index(
        "ix_commerce_transactions_status", "commerce_transactions", ["status"], unique=False
    )

    # 2. Create commerce_events table
    op.create_table(
        "commerce_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_reference", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("event_action", sa.String(length=100), nullable=False),
        sa.Column("event_result", sa.String(length=50), nullable=True),
        sa.Column("sequence_number", sa.BigInteger(), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("actor_type", sa.String(length=100), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "event_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "event_type IN ('transaction', 'authorization', 'capture', 'refund', 'adjustment', 'lifecycle')",  # noqa: E501
            name="ck_commerce_events_event_type",
        ),
        sa.CheckConstraint(
            "event_action IN ('created', 'requested', 'approved', 'completed', 'failed', 'cancelled', 'refunded')",  # noqa: E501
            name="ck_commerce_events_event_action",
        ),
        sa.CheckConstraint(
            "event_result IS NULL OR event_result IN ('success', 'failure', 'pending')",
            name="ck_commerce_events_event_result",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_commerce_events_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_commerce_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["transaction_id"],
            ["commerce_transactions.id"],
            name="fk_commerce_events_transaction_id_commerce_transactions",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_commerce_events"),
        sa.UniqueConstraint(
            "tenant_id", "event_reference", name="uq_commerce_events_tenant_id_event_reference"
        ),
        sa.UniqueConstraint(
            "transaction_id",
            "sequence_number",
            name="uq_commerce_events_transaction_id_sequence_number",
        ),
    )
    op.create_index("ix_commerce_events_tenant_id", "commerce_events", ["tenant_id"], unique=False)
    op.create_index(
        "ix_commerce_events_transaction_id", "commerce_events", ["transaction_id"], unique=False
    )
    op.create_index(
        "ix_commerce_events_merchant_id", "commerce_events", ["merchant_id"], unique=False
    )
    op.create_index("ix_commerce_events_agent_id", "commerce_events", ["agent_id"], unique=False)
    op.create_index(
        "ix_commerce_events_event_type", "commerce_events", ["event_type"], unique=False
    )
    op.create_index(
        "ix_commerce_events_occurred_at", "commerce_events", ["occurred_at"], unique=False
    )


def downgrade() -> None:
    # 1. Drop commerce_events table
    op.drop_index("ix_commerce_events_occurred_at", table_name="commerce_events")
    op.drop_index("ix_commerce_events_event_type", table_name="commerce_events")
    op.drop_index("ix_commerce_events_agent_id", table_name="commerce_events")
    op.drop_index("ix_commerce_events_merchant_id", table_name="commerce_events")
    op.drop_index("ix_commerce_events_transaction_id", table_name="commerce_events")
    op.drop_index("ix_commerce_events_tenant_id", table_name="commerce_events")
    op.drop_table("commerce_events")

    # 2. Drop commerce_transactions table
    op.drop_index("ix_commerce_transactions_status", table_name="commerce_transactions")
    op.drop_index("ix_commerce_transactions_transaction_type", table_name="commerce_transactions")
    op.drop_index("ix_commerce_transactions_external_reference", table_name="commerce_transactions")
    op.drop_index("ix_commerce_transactions_purchase_plan_id", table_name="commerce_transactions")
    op.drop_index("ix_commerce_transactions_purchase_intent_id", table_name="commerce_transactions")
    op.drop_index("ix_commerce_transactions_offer_id", table_name="commerce_transactions")
    op.drop_index("ix_commerce_transactions_product_id", table_name="commerce_transactions")
    op.drop_index("ix_commerce_transactions_agent_id", table_name="commerce_transactions")
    op.drop_index("ix_commerce_transactions_merchant_id", table_name="commerce_transactions")
    op.drop_index("ix_commerce_transactions_tenant_id", table_name="commerce_transactions")
    op.drop_table("commerce_transactions")
