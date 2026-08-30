"""refunds

Revision ID: 025_refunds
Revises: 024_razorpay_webhook_events
Create Date: 2026-08-26 00:23:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "025_refunds"
down_revision: str | None = "024_razorpay_webhook_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "refunds",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("refund_reference", sa.String(length=100), nullable=False),
        sa.Column("external_reference", sa.String(length=100), nullable=True),
        sa.Column("provider_refund_reference", sa.String(length=100), nullable=True),
        sa.Column("refund_type", sa.String(length=50), nullable=False, server_default="full"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column(
            "refund_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
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
            "refund_type IN ('full', 'partial')",
            name="ck_refunds_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')",
            name="ck_refunds_status",
        ),
        sa.CheckConstraint("amount > 0", name="ck_refunds_amount_positive"),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_refunds_commerce_transaction_id_commerce_transactions",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_refunds_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_order_id"],
            ["payment_orders.id"],
            name="fk_refunds_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_transaction_id"],
            ["payment_transactions.id"],
            name="fk_refunds_payment_transaction_id_payment_transactions",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_refunds"),
        sa.UniqueConstraint(
            "tenant_id",
            "refund_reference",
            name="uq_refunds_tenant_id_refund_reference",
        ),
    )
    op.create_index("ix_refunds_tenant_id", "refunds", ["tenant_id"], unique=False)
    op.create_index(
        "ix_refunds_payment_transaction_id", "refunds", ["payment_transaction_id"], unique=False
    )
    op.create_index("ix_refunds_payment_order_id", "refunds", ["payment_order_id"], unique=False)
    op.create_index(
        "ix_refunds_commerce_transaction_id", "refunds", ["commerce_transaction_id"], unique=False
    )
    op.create_index("ix_refunds_merchant_id", "refunds", ["merchant_id"], unique=False)
    op.create_index("ix_refunds_refund_reference", "refunds", ["refund_reference"], unique=False)
    op.create_index(
        "ix_refunds_external_reference", "refunds", ["external_reference"], unique=False
    )
    op.create_index(
        "ix_refunds_provider_refund_reference",
        "refunds",
        ["provider_refund_reference"],
        unique=False,
    )
    op.create_index("ix_refunds_refund_type", "refunds", ["refund_type"], unique=False)
    op.create_index("ix_refunds_status", "refunds", ["status"], unique=False)
    op.create_index("ix_refunds_requested_at", "refunds", ["requested_at"], unique=False)
    op.create_index("ix_refunds_created_at", "refunds", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_refunds_created_at", table_name="refunds")
    op.drop_index("ix_refunds_requested_at", table_name="refunds")
    op.drop_index("ix_refunds_status", table_name="refunds")
    op.drop_index("ix_refunds_refund_type", table_name="refunds")
    op.drop_index("ix_refunds_provider_refund_reference", table_name="refunds")
    op.drop_index("ix_refunds_external_reference", table_name="refunds")
    op.drop_index("ix_refunds_refund_reference", table_name="refunds")
    op.drop_index("ix_refunds_merchant_id", table_name="refunds")
    op.drop_index("ix_refunds_commerce_transaction_id", table_name="refunds")
    op.drop_index("ix_refunds_payment_order_id", table_name="refunds")
    op.drop_index("ix_refunds_payment_transaction_id", table_name="refunds")
    op.drop_index("ix_refunds_tenant_id", table_name="refunds")
    op.drop_table("refunds")
