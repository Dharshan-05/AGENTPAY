"""payment_transactions

Revision ID: 022_payment_transactions
Revises: 021_payment_orders
Create Date: 2026-08-26 00:02:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "022_payment_transactions"
down_revision: str | None = "021_payment_orders"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "payment_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("commerce_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("transaction_reference", sa.String(length=100), nullable=False),
        sa.Column("external_reference", sa.String(length=100), nullable=True),
        sa.Column("payment_provider", sa.String(length=100), nullable=False),
        sa.Column("provider_transaction_reference", sa.String(length=100), nullable=True),
        sa.Column("provider_authorization_reference", sa.String(length=100), nullable=True),
        sa.Column("transaction_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("authorized_amount", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("captured_amount", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column(
            "fee_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0.0000"
        ),
        sa.Column(
            "tax_amount", sa.Numeric(precision=18, scale=4), nullable=False, server_default="0.0000"
        ),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("currency_code", sa.String(length=3), nullable=False, server_default="USD"),
        sa.Column(
            "transaction_metadata",
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
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("authorized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "transaction_type IN ('authorization', 'capture', 'payment', 'refund', 'void', 'adjustment')",  # noqa: E501
            name="ck_payment_transactions_transaction_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'authorized', 'completed', 'failed', 'cancelled')",
            name="ck_payment_transactions_status",
        ),
        sa.CheckConstraint("amount >= 0", name="ck_payment_transactions_amount_nonnegative"),
        sa.CheckConstraint(
            "authorized_amount IS NULL OR authorized_amount >= 0",
            name="ck_payment_transactions_authorized_amount_nonnegative",
        ),
        sa.CheckConstraint(
            "captured_amount IS NULL OR captured_amount >= 0",
            name="ck_payment_transactions_captured_amount_nonnegative",
        ),
        sa.CheckConstraint(
            "fee_amount >= 0", name="ck_payment_transactions_fee_amount_nonnegative"
        ),
        sa.CheckConstraint(
            "tax_amount >= 0", name="ck_payment_transactions_tax_amount_nonnegative"
        ),
        sa.CheckConstraint(
            "total_amount >= 0", name="ck_payment_transactions_total_amount_nonnegative"
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_payment_transactions_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["commerce_transaction_id"],
            ["commerce_transactions.id"],
            name="fk_pay_tx_commerce_tx_id_commerce_tx",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_payment_transactions_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_order_id"],
            ["payment_orders.id"],
            name="fk_payment_transactions_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_payment_transactions"),
        sa.UniqueConstraint(
            "tenant_id",
            "transaction_reference",
            name="uq_payment_transactions_tenant_id_transaction_reference",
        ),
    )
    op.create_index(
        "ix_payment_transactions_tenant_id", "payment_transactions", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_payment_transactions_payment_order_id",
        "payment_transactions",
        ["payment_order_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_transactions_merchant_id", "payment_transactions", ["merchant_id"], unique=False
    )
    op.create_index(
        "ix_payment_transactions_agent_id", "payment_transactions", ["agent_id"], unique=False
    )
    op.create_index(
        "ix_payment_transactions_commerce_transaction_id",
        "payment_transactions",
        ["commerce_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_transactions_transaction_reference",
        "payment_transactions",
        ["transaction_reference"],
        unique=False,
    )
    op.create_index(
        "ix_payment_transactions_external_reference",
        "payment_transactions",
        ["external_reference"],
        unique=False,
    )
    op.create_index(
        "ix_payment_transactions_payment_provider",
        "payment_transactions",
        ["payment_provider"],
        unique=False,
    )
    op.create_index(
        "ix_payment_transactions_provider_transaction_reference",
        "payment_transactions",
        ["provider_transaction_reference"],
        unique=False,
    )
    op.create_index(
        "ix_payment_transactions_transaction_type",
        "payment_transactions",
        ["transaction_type"],
        unique=False,
    )
    op.create_index(
        "ix_payment_transactions_status", "payment_transactions", ["status"], unique=False
    )
    op.create_index(
        "ix_payment_transactions_created_at", "payment_transactions", ["created_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_payment_transactions_created_at", table_name="payment_transactions")
    op.drop_index("ix_payment_transactions_status", table_name="payment_transactions")
    op.drop_index("ix_payment_transactions_transaction_type", table_name="payment_transactions")
    op.drop_index(
        "ix_payment_transactions_provider_transaction_reference", table_name="payment_transactions"
    )
    op.drop_index("ix_payment_transactions_payment_provider", table_name="payment_transactions")
    op.drop_index("ix_payment_transactions_external_reference", table_name="payment_transactions")
    op.drop_index(
        "ix_payment_transactions_transaction_reference", table_name="payment_transactions"
    )
    op.drop_index(
        "ix_payment_transactions_commerce_transaction_id", table_name="payment_transactions"
    )
    op.drop_index("ix_payment_transactions_agent_id", table_name="payment_transactions")
    op.drop_index("ix_payment_transactions_merchant_id", table_name="payment_transactions")
    op.drop_index("ix_payment_transactions_payment_order_id", table_name="payment_transactions")
    op.drop_index("ix_payment_transactions_tenant_id", table_name="payment_transactions")
    op.drop_table("payment_transactions")
