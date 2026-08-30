"""razorpay_webhook_events

Revision ID: 024_razorpay_webhook_events
Revises: 023_payment_events
Create Date: 2026-08-26 00:22:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "024_razorpay_webhook_events"
down_revision: str | None = "023_payment_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "razorpay_webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("provider_event_id", sa.String(length=100), nullable=False),
        sa.Column("event_reference", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column(
            "processing_status", sa.String(length=50), nullable=False, server_default="received"
        ),
        sa.Column(
            "verification_status", sa.String(length=50), nullable=False, server_default="pending"
        ),
        sa.Column(
            "signature_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column(
            "event_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("processing_error", sa.String(length=1000), nullable=True),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
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
            "processing_status IN ('received', 'processing', 'processed', 'failed', 'ignored')",
            name="ck_razorpay_webhook_events_status",
        ),
        sa.CheckConstraint(
            "verification_status IN ('pending', 'verified', 'failed', 'skipped')",
            name="ck_razorpay_webhook_events_verification_status",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_razorpay_webhook_events_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_order_id"],
            ["payment_orders.id"],
            name="fk_razorpay_webhook_events_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_transaction_id"],
            ["payment_transactions.id"],
            name="fk_razorpay_wh_events_pay_tx_id_pay_tx",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_razorpay_webhook_events"),
        sa.UniqueConstraint(
            "tenant_id",
            "provider_event_id",
            name="uq_razorpay_webhook_events_tenant_provider_event",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "event_reference",
            name="uq_razorpay_webhook_events_tenant_event_reference",
        ),
    )
    op.create_index(
        "ix_razorpay_webhook_events_tenant_id",
        "razorpay_webhook_events",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_provider_event_id",
        "razorpay_webhook_events",
        ["provider_event_id"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_event_reference",
        "razorpay_webhook_events",
        ["event_reference"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_event_type",
        "razorpay_webhook_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_processing_status",
        "razorpay_webhook_events",
        ["processing_status"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_verification_status",
        "razorpay_webhook_events",
        ["verification_status"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_payment_order_id",
        "razorpay_webhook_events",
        ["payment_order_id"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_payment_transaction_id",
        "razorpay_webhook_events",
        ["payment_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_merchant_id",
        "razorpay_webhook_events",
        ["merchant_id"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_request_id",
        "razorpay_webhook_events",
        ["request_id"],
        unique=False,
    )
    op.create_index(
        "ix_razorpay_webhook_events_received_at",
        "razorpay_webhook_events",
        ["received_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_razorpay_webhook_events_received_at", table_name="razorpay_webhook_events")
    op.drop_index("ix_razorpay_webhook_events_request_id", table_name="razorpay_webhook_events")
    op.drop_index("ix_razorpay_webhook_events_merchant_id", table_name="razorpay_webhook_events")
    op.drop_index(
        "ix_razorpay_webhook_events_payment_transaction_id", table_name="razorpay_webhook_events"
    )
    op.drop_index(
        "ix_razorpay_webhook_events_payment_order_id", table_name="razorpay_webhook_events"
    )
    op.drop_index(
        "ix_razorpay_webhook_events_verification_status", table_name="razorpay_webhook_events"
    )
    op.drop_index(
        "ix_razorpay_webhook_events_processing_status", table_name="razorpay_webhook_events"
    )
    op.drop_index("ix_razorpay_webhook_events_event_type", table_name="razorpay_webhook_events")
    op.drop_index(
        "ix_razorpay_webhook_events_event_reference", table_name="razorpay_webhook_events"
    )
    op.drop_index(
        "ix_razorpay_webhook_events_provider_event_id", table_name="razorpay_webhook_events"
    )
    op.drop_index("ix_razorpay_webhook_events_tenant_id", table_name="razorpay_webhook_events")
    op.drop_table("razorpay_webhook_events")
