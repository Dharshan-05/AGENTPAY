"""Alembic migration 044: ATIM Governance Policies & Quota Usages Tables (Group 9)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "044"
down_revision: Union[str, None] = "043"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table: atim_governance_policies
    op.create_table(
        "atim_governance_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("policy_type", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="DRAFT"),
        sa.Column("configuration", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False, server_default="Initial draft creation"),
        sa.Column("previous_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("signature", sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_atim_governance_policies"),
    )
    op.create_index(
        "ix_atim_gov_policies_tenant_type_version",
        "atim_governance_policies",
        ["tenant_id", "policy_type", "version"],
        unique=True,
    )
    op.create_index(
        "ix_atim_gov_policies_status",
        "atim_governance_policies",
        ["status"],
    )
    op.create_index(
        "ix_atim_gov_policies_created_at",
        "atim_governance_policies",
        ["created_at"],
    )

    # 2. Table: atim_quota_usages
    op.create_table(
        "atim_quota_usages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("current_daily_requests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_daily_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_daily_cost_usd", sa.Numeric(precision=18, scale=6), nullable=False, server_default="0.0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_atim_quota_usages"),
    )
    op.create_index(
        "ix_atim_quota_usages_tenant_agent",
        "atim_quota_usages",
        ["tenant_id", "agent_id"],
    )
    op.create_index(
        "ix_atim_quota_usages_updated_at",
        "atim_quota_usages",
        ["updated_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_atim_quota_usages_updated_at", table_name="atim_quota_usages")
    op.drop_index("ix_atim_quota_usages_tenant_agent", table_name="atim_quota_usages")
    op.drop_table("atim_quota_usages")

    op.drop_index("ix_atim_gov_policies_created_at", table_name="atim_governance_policies")
    op.drop_index("ix_atim_gov_policies_status", table_name="atim_governance_policies")
    op.drop_index("ix_atim_gov_policies_tenant_type_version", table_name="atim_governance_policies")
    op.drop_table("atim_governance_policies")
