"""payment_events

Revision ID: 023_payment_events
Revises: 022_payment_transactions
Create Date: 2026-08-26 00:03:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "023_payment_events"
down_revision: str | None = "022_payment_transactions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "payment_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_reference", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_action", sa.String(length=50), nullable=False),
        sa.Column("event_result", sa.String(length=50), nullable=False),
        sa.Column("sequence_number", sa.BigInteger(), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("actor_type", sa.String(length=100), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "event_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
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
            "event_type IN ('payment', 'authorization', 'capture', "
            "'failure', 'cancellation', 'lifecycle')",
            name="ck_payment_events_event_type",
        ),
        sa.CheckConstraint(
            "event_action IN ('created', 'requested', 'processing', "
            "'authorized', 'completed', 'failed', 'cancelled')",
            name="ck_payment_events_event_action",
        ),
        sa.CheckConstraint(
            "event_result IN ('success', 'failure', 'pending')",
            name="ck_payment_events_event_result",
        ),
        sa.CheckConstraint(
            "sequence_number > 0", name="ck_payment_events_sequence_number_positive"
        ),
        sa.ForeignKeyConstraint(
            ["payment_order_id"],
            ["payment_orders.id"],
            name="fk_payment_events_payment_order_id_payment_orders",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["payment_transaction_id"],
            ["payment_transactions.id"],
            name="fk_payment_events_payment_transaction_id_payment_transactions",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_payment_events"),
        sa.UniqueConstraint(
            "tenant_id",
            "event_reference",
            name="uq_payment_events_tenant_id_event_reference",
        ),
        sa.UniqueConstraint(
            "payment_transaction_id",
            "sequence_number",
            name="uq_payment_events_transaction_sequence",
        ),
    )
    op.create_index("ix_payment_events_tenant_id", "payment_events", ["tenant_id"], unique=False)
    op.create_index(
        "ix_payment_events_payment_transaction_id",
        "payment_events",
        ["payment_transaction_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_events_payment_order_id", "payment_events", ["payment_order_id"], unique=False
    )
    op.create_index("ix_payment_events_event_type", "payment_events", ["event_type"], unique=False)
    op.create_index(
        "ix_payment_events_event_action", "payment_events", ["event_action"], unique=False
    )
    op.create_index(
        "ix_payment_events_event_result", "payment_events", ["event_result"], unique=False
    )
    op.create_index("ix_payment_events_request_id", "payment_events", ["request_id"], unique=False)
    op.create_index(
        "ix_payment_events_occurred_at", "payment_events", ["occurred_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_payment_events_occurred_at", table_name="payment_events")
    op.drop_index("ix_payment_events_request_id", table_name="payment_events")
    op.drop_index("ix_payment_events_event_result", table_name="payment_events")
    op.drop_index("ix_payment_events_event_action", table_name="payment_events")
    op.drop_index("ix_payment_events_event_type", table_name="payment_events")
    op.drop_index("ix_payment_events_payment_order_id", table_name="payment_events")
    op.drop_index("ix_payment_events_payment_transaction_id", table_name="payment_events")
    op.drop_index("ix_payment_events_tenant_id", table_name="payment_events")
    op.drop_table("payment_events")
