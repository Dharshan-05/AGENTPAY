"""payment_orders

Revision ID: 021_payment_orders
Revises: 020_xai_explanations
Create Date: 2026-08-26 00:01:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "021_payment_orders"
down_revision: str | None = "020_xai_explanations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "payment_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_intent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("purchase_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("order_reference", sa.String(length=100), nullable=False),
        sa.Column("external_reference", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="created"),
        sa.Column("amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column(
            "subtotal", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0.0000"
        ),
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
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column(
            "quantity", sa.Numeric(precision=18, scale=3), nullable=True, server_default="1.000"
        ),
        sa.Column(
            "order_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
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
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("authorized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('created', 'pending', 'processing', 'authorized', "
            "'completed', 'failed', 'cancelled', 'expired')",
            name="ck_payment_orders_status",
        ),
        sa.CheckConstraint("amount >= 0", name="ck_payment_orders_amount_nonnegative"),
        sa.CheckConstraint("subtotal >= 0", name="ck_payment_orders_subtotal_nonnegative"),
        sa.CheckConstraint("tax_amount >= 0", name="ck_payment_orders_tax_nonnegative"),
        sa.CheckConstraint("discount_amount >= 0", name="ck_payment_orders_discount_nonnegative"),
        sa.CheckConstraint("fee_amount >= 0", name="ck_payment_orders_fee_nonnegative"),
        sa.CheckConstraint("total_amount >= 0", name="ck_payment_orders_total_nonnegative"),
        sa.CheckConstraint(
            "quantity IS NULL OR quantity >= 0", name="ck_payment_orders_quantity_nonnegative"
        ),
        sa.CheckConstraint(
            "(authorized_at IS NULL OR authorized_at >= created_at) AND "
            "(completed_at IS NULL OR completed_at >= created_at)",
            name="ck_payment_orders_date_bounds",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_payment_orders_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_payment_orders_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_payment_orders_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_payment_orders_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_intent_id"],
            ["purchase_intents.id"],
            name="fk_payment_orders_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_plan_id"],
            ["purchase_plans.id"],
            name="fk_payment_orders_purchase_plan_id_purchase_plans",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_payment_orders"),
        sa.UniqueConstraint(
            "tenant_id",
            "order_reference",
            name="uq_payment_orders_tenant_id_order_reference",
        ),
    )
    op.create_index("ix_payment_orders_tenant_id", "payment_orders", ["tenant_id"], unique=False)
    op.create_index(
        "ix_payment_orders_merchant_id", "payment_orders", ["merchant_id"], unique=False
    )
    op.create_index("ix_payment_orders_agent_id", "payment_orders", ["agent_id"], unique=False)
    op.create_index("ix_payment_orders_product_id", "payment_orders", ["product_id"], unique=False)
    op.create_index("ix_payment_orders_offer_id", "payment_orders", ["offer_id"], unique=False)
    op.create_index(
        "ix_payment_orders_purchase_intent_id",
        "payment_orders",
        ["purchase_intent_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_orders_purchase_plan_id", "payment_orders", ["purchase_plan_id"], unique=False
    )
    op.create_index(
        "ix_payment_orders_order_reference", "payment_orders", ["order_reference"], unique=False
    )
    op.create_index(
        "ix_payment_orders_external_reference",
        "payment_orders",
        ["external_reference"],
        unique=False,
    )
    op.create_index("ix_payment_orders_status", "payment_orders", ["status"], unique=False)
    op.create_index("ix_payment_orders_created_at", "payment_orders", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_payment_orders_created_at", table_name="payment_orders")
    op.drop_index("ix_payment_orders_status", table_name="payment_orders")
    op.drop_index("ix_payment_orders_external_reference", table_name="payment_orders")
    op.drop_index("ix_payment_orders_order_reference", table_name="payment_orders")
    op.drop_index("ix_payment_orders_purchase_plan_id", table_name="payment_orders")
    op.drop_index("ix_payment_orders_purchase_intent_id", table_name="payment_orders")
    op.drop_index("ix_payment_orders_offer_id", table_name="payment_orders")
    op.drop_index("ix_payment_orders_product_id", table_name="payment_orders")
    op.drop_index("ix_payment_orders_agent_id", table_name="payment_orders")
    op.drop_index("ix_payment_orders_merchant_id", table_name="payment_orders")
    op.drop_index("ix_payment_orders_tenant_id", table_name="payment_orders")
    op.drop_table("payment_orders")
