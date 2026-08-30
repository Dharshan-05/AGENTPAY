"""inventory_events_and_offers

Revision ID: 013_inventory_events_and_offers
Revises: 012_product_categories_and_inventory
Create Date: 2026-08-25 23:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "013_inventory_events_and_offers"
down_revision: str | None = "012_product_categories_and_inventory"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create inventory_events table
    op.create_table(
        "inventory_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inventory_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("event_action", sa.String(length=100), nullable=False),
        sa.Column("event_result", sa.String(length=50), nullable=False, server_default="success"),
        sa.Column(
            "quantity_delta",
            sa.Numeric(precision=18, scale=3),
            nullable=False,
            server_default="0.000",
        ),
        sa.Column(
            "quantity_before",
            sa.Numeric(precision=18, scale=3),
            nullable=False,
            server_default="0.000",
        ),
        sa.Column(
            "quantity_after",
            sa.Numeric(precision=18, scale=3),
            nullable=False,
            server_default="0.000",
        ),
        sa.Column("reserved_quantity_delta", sa.Numeric(precision=18, scale=3), nullable=True),
        sa.Column("reserved_quantity_before", sa.Numeric(precision=18, scale=3), nullable=True),
        sa.Column("reserved_quantity_after", sa.Numeric(precision=18, scale=3), nullable=True),
        sa.Column("reference_type", sa.String(length=100), nullable=True),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
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
            "quantity_after = quantity_before + quantity_delta",
            name="ck_inventory_events_quantity_after_consistency",
        ),
        sa.CheckConstraint(
            "quantity_before >= 0", name="ck_inventory_events_quantity_before_nonnegative"
        ),
        sa.CheckConstraint(
            "quantity_after >= 0", name="ck_inventory_events_quantity_after_nonnegative"
        ),
        sa.ForeignKeyConstraint(
            ["inventory_id"],
            ["inventory.id"],
            name="fk_inventory_events_inventory_id_inventory",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_inventory_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_inventory_events_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_inventory_events"),
    )
    op.create_index(
        "ix_inventory_events_tenant_id", "inventory_events", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_inventory_events_inventory_id", "inventory_events", ["inventory_id"], unique=False
    )
    op.create_index(
        "ix_inventory_events_merchant_id", "inventory_events", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_inventory_events_product_id", "inventory_events", ["product_id"], unique=False
    )
    op.create_index(
        "ix_inventory_events_event_type", "inventory_events", ["event_type"], unique=False
    )
    op.create_index(
        "ix_inventory_events_occurred_at", "inventory_events", ["occurred_at"], unique=False
    )

    # 2. Create offers table
    op.create_table(
        "offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("price", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "min_quantity",
            sa.Numeric(precision=18, scale=3),
            nullable=False,
            server_default="1.000",
        ),
        sa.Column("max_quantity", sa.Numeric(precision=18, scale=3), nullable=True),
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("price >= 0", name="ck_offers_price_nonnegative"),
        sa.CheckConstraint("min_quantity >= 0", name="ck_offers_min_quantity_nonnegative"),
        sa.CheckConstraint(
            "max_quantity IS NULL OR max_quantity >= min_quantity",
            name="ck_offers_max_quantity_bounds",
        ),
        sa.CheckConstraint(
            "starts_at IS NULL OR ends_at IS NULL OR starts_at <= ends_at",
            name="ck_offers_date_bounds",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'expired', 'suspended')",
            name="ck_offers_status",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_offers_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_offers_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_offers"),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_offers_tenant_id_slug"),
    )
    op.create_index("ix_offers_tenant_id", "offers", ["tenant_id"], unique=False)
    op.create_index("ix_offers_merchant_id", "offers", ["merchant_id"], unique=False)
    op.create_index("ix_offers_product_id", "offers", ["product_id"], unique=False)
    op.create_index("ix_offers_status", "offers", ["status"], unique=False)


def downgrade() -> None:
    # 1. Drop offers table
    op.drop_index("ix_offers_status", table_name="offers")
    op.drop_index("ix_offers_product_id", table_name="offers")
    op.drop_index("ix_offers_merchant_id", table_name="offers")
    op.drop_index("ix_offers_tenant_id", table_name="offers")
    op.drop_table("offers")

    # 2. Drop inventory_events table
    op.drop_index("ix_inventory_events_occurred_at", table_name="inventory_events")
    op.drop_index("ix_inventory_events_event_type", table_name="inventory_events")
    op.drop_index("ix_inventory_events_product_id", table_name="inventory_events")
    op.drop_index("ix_inventory_events_merchant_id", table_name="inventory_events")
    op.drop_index("ix_inventory_events_inventory_id", table_name="inventory_events")
    op.drop_index("ix_inventory_events_tenant_id", table_name="inventory_events")
    op.drop_table("inventory_events")
