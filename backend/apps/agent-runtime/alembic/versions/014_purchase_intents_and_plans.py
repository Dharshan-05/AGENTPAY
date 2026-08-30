"""purchase_intents_and_plans

Revision ID: 014_purchase_intents_and_plans
Revises: 013_inventory_events_and_offers
Create Date: 2026-08-25 23:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "014_purchase_intents_and_plans"
down_revision: str | None = "013_inventory_events_and_offers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create purchase_intents table
    op.create_table(
        "purchase_intents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("intent_reference", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column(
            "quantity", sa.Numeric(precision=18, scale=3), nullable=False, server_default="1.000"
        ),
        sa.Column("unit_price", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("actor_type", sa.String(length=100), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "intent_metadata",
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'expired', 'cancelled')",
            name="ck_purchase_intents_status",
        ),
        sa.CheckConstraint("quantity > 0", name="ck_purchase_intents_quantity_positive"),
        sa.CheckConstraint("unit_price >= 0", name="ck_purchase_intents_unit_price_nonnegative"),
        sa.CheckConstraint(
            "total_amount >= 0", name="ck_purchase_intents_total_amount_nonnegative"
        ),
        sa.CheckConstraint(
            "expires_at IS NULL OR requested_at <= expires_at",
            name="ck_purchase_intents_date_bounds",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_purchase_intents_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_purchase_intents_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_purchase_intents_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_purchase_intents_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_purchase_intents"),
        sa.UniqueConstraint(
            "tenant_id", "intent_reference", name="uq_purchase_intents_tenant_id_intent_reference"
        ),
    )
    op.create_index(
        "ix_purchase_intents_tenant_id", "purchase_intents", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_purchase_intents_merchant_id", "purchase_intents", ["merchant_id"], unique=False
    )
    op.create_index("ix_purchase_intents_agent_id", "purchase_intents", ["agent_id"], unique=False)
    op.create_index(
        "ix_purchase_intents_product_id", "purchase_intents", ["product_id"], unique=False
    )
    op.create_index("ix_purchase_intents_offer_id", "purchase_intents", ["offer_id"], unique=False)
    op.create_index("ix_purchase_intents_status", "purchase_intents", ["status"], unique=False)

    # 2. Create purchase_plans table
    op.create_table(
        "purchase_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_intent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("plan_reference", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column(
            "quantity", sa.Numeric(precision=18, scale=3), nullable=False, server_default="1.000"
        ),
        sa.Column("unit_price", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("subtotal", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column(
            "planned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "plan_metadata",
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('draft', 'ready', 'executing', 'completed', 'failed', 'cancelled', 'expired')",  # noqa: E501
            name="ck_purchase_plans_status",
        ),
        sa.CheckConstraint("quantity > 0", name="ck_purchase_plans_quantity_positive"),
        sa.CheckConstraint("unit_price >= 0", name="ck_purchase_plans_unit_price_nonnegative"),
        sa.CheckConstraint("subtotal >= 0", name="ck_purchase_plans_subtotal_nonnegative"),
        sa.CheckConstraint("total_amount >= 0", name="ck_purchase_plans_total_amount_nonnegative"),
        sa.CheckConstraint(
            "expires_at IS NULL OR planned_at <= expires_at",
            name="ck_purchase_plans_date_bounds",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_purchase_plans_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_purchase_plans_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["offer_id"],
            ["offers.id"],
            name="fk_purchase_plans_offer_id_offers",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_purchase_plans_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["purchase_intent_id"],
            ["purchase_intents.id"],
            name="fk_purchase_plans_purchase_intent_id_purchase_intents",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_purchase_plans"),
        sa.UniqueConstraint(
            "tenant_id", "plan_reference", name="uq_purchase_plans_tenant_id_plan_reference"
        ),
    )
    op.create_index("ix_purchase_plans_tenant_id", "purchase_plans", ["tenant_id"], unique=False)
    op.create_index(
        "ix_purchase_plans_purchase_intent_id",
        "purchase_plans",
        ["purchase_intent_id"],
        unique=False,
    )
    op.create_index(
        "ix_purchase_plans_merchant_id", "purchase_plans", ["merchant_id"], unique=False
    )
    op.create_index("ix_purchase_plans_agent_id", "purchase_plans", ["agent_id"], unique=False)
    op.create_index("ix_purchase_plans_product_id", "purchase_plans", ["product_id"], unique=False)
    op.create_index("ix_purchase_plans_offer_id", "purchase_plans", ["offer_id"], unique=False)
    op.create_index("ix_purchase_plans_status", "purchase_plans", ["status"], unique=False)


def downgrade() -> None:
    # 1. Drop purchase_plans table
    op.drop_index("ix_purchase_plans_status", table_name="purchase_plans")
    op.drop_index("ix_purchase_plans_offer_id", table_name="purchase_plans")
    op.drop_index("ix_purchase_plans_product_id", table_name="purchase_plans")
    op.drop_index("ix_purchase_plans_agent_id", table_name="purchase_plans")
    op.drop_index("ix_purchase_plans_merchant_id", table_name="purchase_plans")
    op.drop_index("ix_purchase_plans_purchase_intent_id", table_name="purchase_plans")
    op.drop_index("ix_purchase_plans_tenant_id", table_name="purchase_plans")
    op.drop_table("purchase_plans")

    # 2. Drop purchase_intents table
    op.drop_index("ix_purchase_intents_status", table_name="purchase_intents")
    op.drop_index("ix_purchase_intents_offer_id", table_name="purchase_intents")
    op.drop_index("ix_purchase_intents_product_id", table_name="purchase_intents")
    op.drop_index("ix_purchase_intents_agent_id", table_name="purchase_intents")
    op.drop_index("ix_purchase_intents_merchant_id", table_name="purchase_intents")
    op.drop_index("ix_purchase_intents_tenant_id", table_name="purchase_intents")
    op.drop_table("purchase_intents")
