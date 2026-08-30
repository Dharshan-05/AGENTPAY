"""product_categories_and_inventory

Revision ID: 012_product_categories_and_inventory
Revises: 011_merchants_and_products
Create Date: 2026-08-25 22:25:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "012_product_categories_and_inventory"
down_revision: str | None = "011_merchants_and_products"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create product_categories table
    op.create_table(
        "product_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
        sa.Column("parent_category_id", postgresql.UUID(as_uuid=True), nullable=True),
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
            "parent_category_id IS NULL OR parent_category_id <> id",
            name="ck_product_categories_parent_not_self",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'archived')",
            name="ck_product_categories_status",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_product_categories_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parent_category_id"],
            ["product_categories.id"],
            name="fk_product_categories_parent_category_id_product_categories",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_product_categories"),
        sa.UniqueConstraint(
            "tenant_id",
            "slug",
            name="uq_product_categories_tenant_id_slug",
        ),
    )
    op.create_index(
        "ix_product_categories_tenant_id", "product_categories", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_product_categories_merchant_id", "product_categories", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_product_categories_parent_category_id",
        "product_categories",
        ["parent_category_id"],
        unique=False,
    )
    op.create_index("ix_product_categories_status", "product_categories", ["status"], unique=False)

    # 2. Create inventory table
    op.create_table(
        "inventory",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "quantity", sa.Numeric(precision=18, scale=3), nullable=False, server_default="0.000"
        ),
        sa.Column(
            "reserved_quantity",
            sa.Numeric(precision=18, scale=3),
            nullable=False,
            server_default="0.000",
        ),
        sa.Column(
            "available_quantity",
            sa.Numeric(precision=18, scale=3),
            nullable=False,
            server_default="0.000",
        ),
        sa.Column(
            "reorder_level",
            sa.Numeric(precision=18, scale=3),
            nullable=False,
            server_default="0.000",
        ),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="active"),
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
        sa.CheckConstraint("quantity >= 0", name="ck_inventory_quantity_nonnegative"),
        sa.CheckConstraint(
            "reserved_quantity >= 0", name="ck_inventory_reserved_quantity_nonnegative"
        ),
        sa.CheckConstraint(
            "available_quantity >= 0", name="ck_inventory_available_quantity_nonnegative"
        ),
        sa.CheckConstraint("reorder_level >= 0", name="ck_inventory_reorder_level_nonnegative"),
        sa.CheckConstraint(
            "reserved_quantity <= quantity AND available_quantity <= quantity AND available_quantity + reserved_quantity <= quantity",  # noqa: E501
            name="ck_inventory_quantity_consistency",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'inactive', 'discontinued')",
            name="ck_inventory_status",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_inventory_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            name="fk_inventory_product_id_products",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_inventory"),
        sa.UniqueConstraint("tenant_id", "product_id", name="uq_inventory_tenant_id_product_id"),
    )
    op.create_index("ix_inventory_tenant_id", "inventory", ["tenant_id"], unique=False)
    op.create_index("ix_inventory_merchant_id", "inventory", ["merchant_id"], unique=False)
    op.create_index("ix_inventory_product_id", "inventory", ["product_id"], unique=False)
    op.create_index("ix_inventory_status", "inventory", ["status"], unique=False)


def downgrade() -> None:
    # 1. Drop inventory table
    op.drop_index("ix_inventory_status", table_name="inventory")
    op.drop_index("ix_inventory_product_id", table_name="inventory")
    op.drop_index("ix_inventory_merchant_id", table_name="inventory")
    op.drop_index("ix_inventory_tenant_id", table_name="inventory")
    op.drop_table("inventory")

    # 2. Drop product_categories table
    op.drop_index("ix_product_categories_status", table_name="product_categories")
    op.drop_index("ix_product_categories_parent_category_id", table_name="product_categories")
    op.drop_index("ix_product_categories_merchant_id", table_name="product_categories")
    op.drop_index("ix_product_categories_tenant_id", table_name="product_categories")
    op.drop_table("product_categories")
