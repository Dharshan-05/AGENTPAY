"""payment_idempotency_keys

Revision ID: 027_payment_idempotency_keys
Revises: 026_cancellations
Create Date: 2026-08-26 08:23:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "027_payment_idempotency_keys"
down_revision: str | None = "026_cancellations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "payment_idempotency_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", sa.String(length=100), nullable=False),
        sa.Column("operation_type", sa.String(length=50), nullable=False),
        sa.Column("request_id", sa.String(length=100), nullable=True),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("request_hash", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("response_code", sa.Integer(), nullable=True),
        sa.Column(
            "response_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="{}",
        ),
        sa.Column(
            "first_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
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
            "operation_type IN ('create_order', 'authorize', 'capture', 'refund', 'cancel', 'payment', 'retry', 'webhook')",  # noqa: E501
            name="ck_payment_idempotency_keys_operation_type",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed', 'expired', 'conflict')",
            name="ck_payment_idempotency_keys_status",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_payment_idempotency_keys"),
        sa.UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_payment_idempotency_keys_tenant_key",
        ),
    )
    op.create_index(
        "ix_payment_idempotency_keys_tenant_id",
        "payment_idempotency_keys",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_idempotency_keys_idempotency_key",
        "payment_idempotency_keys",
        ["idempotency_key"],
        unique=False,
    )
    op.create_index(
        "ix_payment_idempotency_keys_operation_type",
        "payment_idempotency_keys",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        "ix_payment_idempotency_keys_request_id",
        "payment_idempotency_keys",
        ["request_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_idempotency_keys_status", "payment_idempotency_keys", ["status"], unique=False
    )
    op.create_index(
        "ix_payment_idempotency_keys_resource_id",
        "payment_idempotency_keys",
        ["resource_id"],
        unique=False,
    )
    op.create_index(
        "ix_payment_idempotency_keys_expires_at",
        "payment_idempotency_keys",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_payment_idempotency_keys_expires_at", table_name="payment_idempotency_keys")
    op.drop_index("ix_payment_idempotency_keys_resource_id", table_name="payment_idempotency_keys")
    op.drop_index("ix_payment_idempotency_keys_status", table_name="payment_idempotency_keys")
    op.drop_index("ix_payment_idempotency_keys_request_id", table_name="payment_idempotency_keys")
    op.drop_index(
        "ix_payment_idempotency_keys_operation_type", table_name="payment_idempotency_keys"
    )
    op.drop_index(
        "ix_payment_idempotency_keys_idempotency_key", table_name="payment_idempotency_keys"
    )
    op.drop_index("ix_payment_idempotency_keys_tenant_id", table_name="payment_idempotency_keys")
    op.drop_table("payment_idempotency_keys")
