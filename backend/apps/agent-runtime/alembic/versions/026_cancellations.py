"""cancellations

Revision ID: 026_cancellations
Revises: 025_refunds
Create Date: 2026-08-26 00:24:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "026_cancellations"
down_revision: str | None = "025_refunds"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cancellations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cancellation_reference", sa.String(length=100), nullable=False),
        sa.Column("provider_cancellation_reference", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="requested"),
        sa.Column(
            "reason_type", sa.String(length=50), nullable=False, server_default="customer_request"
        ),
        sa.Column("reason_detail", sa.String(length=500), nullable=True),
        sa.Column(
            "cancellation_metadata",
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
        sa.CheckConstraint(
            "status IN ('requested', 'processing', 'completed', 'failed', 'rejected')",
            name="ck_cancellations_status",
        ),
        sa.CheckConstraint(
            "reason_type IN ('customer_request', 'merchant_request', 'payment_timeout', "
            "'duplicate_order', 'system_error', 'risk_rejection', 'other')",
            name="ck_cancellations_reason_type",
        ),
        sa.ForeignKeyConstraint(
            ["agent_id"],
            ["agents.id"],
            name="fk_cancellations_agent_id_agents",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_cancellations_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_order_id"],
            ["payment_orders.id"],
            name="fk_cancellations_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_transaction_id"],
            ["payment_transactions.id"],
            name="fk_cancellations_payment_transaction_id_payment_transactions",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_cancellations"),
        sa.UniqueConstraint(
            "tenant_id",
            "cancellation_reference",
            name="uq_cancellations_tenant_id_cancellation_reference",
        ),
    )
    op.create_index("ix_cancellations_tenant_id", "cancellations", ["tenant_id"], unique=False)
    op.create_index(
        "ix_cancellations_payment_order_id", "cancellations", ["payment_order_id"], unique=False
    )
    op.create_index(
        "ix_cancellations_payment_transaction_id",
        "cancellations",
        ["payment_transaction_id"],
        unique=False,
    )
    op.create_index("ix_cancellations_merchant_id", "cancellations", ["merchant_id"], unique=False)
    op.create_index("ix_cancellations_agent_id", "cancellations", ["agent_id"], unique=False)
    op.create_index(
        "ix_cancellations_cancellation_reference",
        "cancellations",
        ["cancellation_reference"],
        unique=False,
    )
    op.create_index(
        "ix_cancellations_provider_cancellation_reference",
        "cancellations",
        ["provider_cancellation_reference"],
        unique=False,
    )
    op.create_index("ix_cancellations_status", "cancellations", ["status"], unique=False)
    op.create_index("ix_cancellations_reason_type", "cancellations", ["reason_type"], unique=False)
    op.create_index(
        "ix_cancellations_requested_at", "cancellations", ["requested_at"], unique=False
    )
    op.create_index("ix_cancellations_created_at", "cancellations", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_cancellations_created_at", table_name="cancellations")
    op.drop_index("ix_cancellations_requested_at", table_name="cancellations")
    op.drop_index("ix_cancellations_reason_type", table_name="cancellations")
    op.drop_index("ix_cancellations_status", table_name="cancellations")
    op.drop_index("ix_cancellations_provider_cancellation_reference", table_name="cancellations")
    op.drop_index("ix_cancellations_cancellation_reference", table_name="cancellations")
    op.drop_index("ix_cancellations_agent_id", table_name="cancellations")
    op.drop_index("ix_cancellations_merchant_id", table_name="cancellations")
    op.drop_index("ix_cancellations_payment_transaction_id", table_name="cancellations")
    op.drop_index("ix_cancellations_payment_order_id", table_name="cancellations")
    op.drop_index("ix_cancellations_tenant_id", table_name="cancellations")
    op.drop_table("cancellations")
