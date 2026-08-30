"""merchants_and_products

Revision ID: 011_merchants_and_products
Revises: 010_agent_trust_and_audit
Create Date: 2026-08-25 22:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "011_merchants_and_products"
down_revision: str | None = "010_agent_trust_and_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create merchants table
    op.create_table(
        "merchants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("description", sa.String(length=500), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name="pk_merchants"),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_merchants_tenant_id_slug"),
    )
    op.create_index("ix_merchants_tenant_id", "merchants", ["tenant_id"], unique=False)
    op.create_index("ix_merchants_status", "merchants", ["status"], unique=False)

    # 2. Create products table
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column(
            "price", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0.00"
        ),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
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
        sa.CheckConstraint("price >= 0", name="ck_products_price_nonnegative"),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_products_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_products"),
        sa.UniqueConstraint("merchant_id", "sku", name="uq_products_merchant_id_sku"),
    )
    op.create_index("ix_products_tenant_id", "products", ["tenant_id"], unique=False)
    op.create_index("ix_products_merchant_id", "products", ["merchant_id"], unique=False)
    op.create_index("ix_products_status", "products", ["status"], unique=False)


def downgrade() -> None:
    # 1. Drop products table
    op.drop_index("ix_products_status", table_name="products")
    op.drop_index("ix_products_merchant_id", table_name="products")
    op.drop_index("ix_products_tenant_id", table_name="products")
    op.drop_table("products")

    # 2. Drop merchants table
    op.drop_index("ix_merchants_status", table_name="merchants")
    op.drop_index("ix_merchants_tenant_id", table_name="merchants")
    op.drop_table("merchants")
