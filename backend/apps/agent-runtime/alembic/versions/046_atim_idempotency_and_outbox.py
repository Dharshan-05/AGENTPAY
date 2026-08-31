"""Alembic migration 046: ATIM Idempotency Records & Transactional Outbox Tables (Group 11)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "046"
down_revision: Union[str, None] = "045"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table: atim_idempotency_records
    op.create_table(
        "atim_idempotency_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("operation", sa.String(length=64), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("state", sa.String(length=32), nullable=False, server_default="PROCESSING"),
        sa.Column("response_code", sa.Integer(), nullable=True),
        sa.Column("response_body", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_atim_idempotency_records"),
    )
    op.create_index(
        "ix_atim_idempotency_scoped_key",
        "atim_idempotency_records",
        ["tenant_id", "agent_id", "operation", "idempotency_key"],
        unique=True,
    )
    op.create_index(
        "ix_atim_idempotency_expires_at",
        "atim_idempotency_records",
        ["expires_at"],
    )

    # 2. Table: atim_transactional_outbox
    op.create_table(
        "atim_transactional_outbox",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_atim_transactional_outbox"),
    )
    op.create_index(
        "ix_atim_outbox_tenant_processed",
        "atim_transactional_outbox",
        ["tenant_id", "processed"],
    )
    op.create_index(
        "ix_atim_outbox_created_at",
        "atim_transactional_outbox",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_atim_outbox_created_at", table_name="atim_transactional_outbox")
    op.drop_index("ix_atim_outbox_tenant_processed", table_name="atim_transactional_outbox")
    op.drop_table("atim_transactional_outbox")

    op.drop_index("ix_atim_idempotency_expires_at", table_name="atim_idempotency_records")
    op.drop_index("ix_atim_idempotency_scoped_key", table_name="atim_idempotency_records")
    op.drop_table("atim_idempotency_records")
