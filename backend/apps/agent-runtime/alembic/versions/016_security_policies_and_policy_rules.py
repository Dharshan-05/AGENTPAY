"""security_policies_and_policy_rules

Revision ID: 016_security_policies_and_policy_rules
Revises: 015_commerce_transactions_and_events
Create Date: 2026-08-25 23:25:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "016_security_policies_and_policy_rules"
down_revision: str | None = "015_commerce_transactions_and_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create security_policies table
    op.create_table(
        "security_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("policy_type", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column(
            "enforcement_mode", sa.String(length=50), nullable=False, server_default="enforce"
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "configuration",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('draft', 'active', 'inactive', 'suspended', 'archived')",
            name="ck_security_policies_status",
        ),
        sa.CheckConstraint(
            "policy_type IN ('authorization', 'transaction', 'fraud', 'risk', "
            "'compliance', 'spending', 'access', 'agent', 'commerce')",
            name="ck_security_policies_policy_type",
        ),
        sa.CheckConstraint("priority >= 0", name="ck_security_policies_priority_nonnegative"),
        sa.CheckConstraint(
            "enforcement_mode IN ('enforce', 'monitor', 'warn', 'block')",
            name="ck_security_policies_enforcement_mode",
        ),
        sa.CheckConstraint("version >= 1", name="ck_security_policies_version_positive"),
        sa.CheckConstraint(
            "ends_at IS NULL OR starts_at <= ends_at",
            name="ck_security_policies_date_bounds",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_security_policies_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_security_policies"),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_security_policies_tenant_id_slug"),
    )
    op.create_index(
        "ix_security_policies_tenant_id", "security_policies", ["tenant_id"], unique=False
    )
    op.create_index(
        "ix_security_policies_merchant_id", "security_policies", ["merchant_id"], unique=False
    )
    op.create_index("ix_security_policies_status", "security_policies", ["status"], unique=False)
    op.create_index(
        "ix_security_policies_policy_type", "security_policies", ["policy_type"], unique=False
    )

    # 2. Create policy_rules table
    op.create_table(
        "policy_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("security_policy_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("rule_type", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("operator", sa.String(length=50), nullable=False),
        sa.Column(
            "condition_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("failure_action", sa.String(length=50), nullable=False, server_default="deny"),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
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
            "status IN ('draft', 'active', 'inactive', 'disabled', 'archived')",
            name="ck_policy_rules_status",
        ),
        sa.CheckConstraint(
            "rule_type IN ('threshold', 'allowlist', 'denylist', 'velocity', "
            "'amount', 'frequency', 'geography', 'identity', 'agent_trust', "
            "'merchant', 'product', 'custom')",
            name="ck_policy_rules_rule_type",
        ),
        sa.CheckConstraint("priority >= 0", name="ck_policy_rules_priority_nonnegative"),
        sa.CheckConstraint(
            "operator IN ('eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', "
            "'not_in', 'contains', 'not_contains', 'exists', 'not_exists')",
            name="ck_policy_rules_operator",
        ),
        sa.CheckConstraint(
            "action IN ('allow', 'deny', 'challenge', 'review', 'alert', "
            "'block', 'require_approval')",
            name="ck_policy_rules_action",
        ),
        sa.CheckConstraint(
            "failure_action IN ('deny', 'allow', 'alert', 'review')",
            name="ck_policy_rules_failure_action",
        ),
        sa.CheckConstraint(
            "ends_at IS NULL OR starts_at <= ends_at",
            name="ck_policy_rules_date_bounds",
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            name="fk_policy_rules_merchant_id_merchants",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["security_policy_id"],
            ["security_policies.id"],
            name="fk_policy_rules_security_policy_id_security_policies",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_policy_rules"),
        sa.UniqueConstraint(
            "tenant_id",
            "security_policy_id",
            "slug",
            name="uq_policy_rules_tenant_id_security_policy_id_slug",
        ),
    )
    op.create_index("ix_policy_rules_tenant_id", "policy_rules", ["tenant_id"], unique=False)
    op.create_index(
        "ix_policy_rules_security_policy_id", "policy_rules", ["security_policy_id"], unique=False
    )
    op.create_index("ix_policy_rules_merchant_id", "policy_rules", ["merchant_id"], unique=False)
    op.create_index("ix_policy_rules_status", "policy_rules", ["status"], unique=False)
    op.create_index("ix_policy_rules_rule_type", "policy_rules", ["rule_type"], unique=False)


def downgrade() -> None:
    # 1. Drop policy_rules table
    op.drop_index("ix_policy_rules_rule_type", table_name="policy_rules")
    op.drop_index("ix_policy_rules_status", table_name="policy_rules")
    op.drop_index("ix_policy_rules_merchant_id", table_name="policy_rules")
    op.drop_index("ix_policy_rules_security_policy_id", table_name="policy_rules")
    op.drop_index("ix_policy_rules_tenant_id", table_name="policy_rules")
    op.drop_table("policy_rules")

    # 2. Drop security_policies table
    op.drop_index("ix_security_policies_policy_type", table_name="security_policies")
    op.drop_index("ix_security_policies_status", table_name="security_policies")
    op.drop_index("ix_security_policies_merchant_id", table_name="security_policies")
    op.drop_index("ix_security_policies_tenant_id", table_name="security_policies")
    op.drop_table("security_policies")
