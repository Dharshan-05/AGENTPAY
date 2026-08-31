"""Alembic migration 043: ATIM Cryptographic Audit Lock & Threat Intelligence Tables (Group 8)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "043"
down_revision: Union[str, None] = "042"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table: atim_audit_signatures
    op.create_table(
        "atim_audit_signatures",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("record_type", sa.String(length=64), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("signature", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_atim_audit_signatures"),
    )
    op.create_index(
        "ix_atim_audit_signatures_tenant_request",
        "atim_audit_signatures",
        ["tenant_id", "request_id"],
    )
    op.create_index(
        "ix_atim_audit_signatures_created_at",
        "atim_audit_signatures",
        ["created_at"],
    )

    # 2. Table: atim_threat_intel_logs
    op.create_table(
        "atim_threat_intel_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("threat_score", sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_atim_threat_intel_logs"),
    )
    op.create_index(
        "ix_atim_threat_intel_logs_tenant_id",
        "atim_threat_intel_logs",
        ["tenant_id"],
    )
    op.create_index(
        "ix_atim_threat_intel_logs_category",
        "atim_threat_intel_logs",
        ["category"],
    )
    op.create_index(
        "ix_atim_threat_intel_logs_created_at",
        "atim_threat_intel_logs",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_atim_threat_intel_logs_created_at", table_name="atim_threat_intel_logs")
    op.drop_index("ix_atim_threat_intel_logs_category", table_name="atim_threat_intel_logs")
    op.drop_index("ix_atim_threat_intel_logs_tenant_id", table_name="atim_threat_intel_logs")
    op.drop_table("atim_threat_intel_logs")

    op.drop_index("ix_atim_audit_signatures_created_at", table_name="atim_audit_signatures")
    op.drop_index("ix_atim_audit_signatures_tenant_request", table_name="atim_audit_signatures")
    op.drop_table("atim_audit_signatures")
