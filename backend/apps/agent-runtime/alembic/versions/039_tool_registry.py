"""tool_registry_table

Revision ID: 039_tool_registry
Revises: 038_agent_memories
Create Date: 2026-08-26 14:00:00.000000

Creates the tool_definitions table for Phase 157.
Stores agent tool registration metadata, schemas, lifecycle status, and environment settings.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "039_tool_registry"
down_revision: str | None = "038_agent_memories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create tool_definitions table."""
    op.create_table(
        "tool_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False, server_default="1.0.0"),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="utility"),
        sa.Column("owner", sa.String(length=150), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="REGISTERED"),
        sa.Column("environment", sa.String(length=50), nullable=False, server_default="production"),
        sa.Column("risk_classification", sa.String(length=50), nullable=False, server_default="LOW"),  # noqa: E501
        sa.Column(
            "input_schema",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "output_schema",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "capabilities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "tool_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "name",
            "version",
            name="uq_tool_definitions_tenant_name_version",
        ),
    )

    op.create_index("ix_tool_definitions_tenant_id", "tool_definitions", ["tenant_id"])
    op.create_index("ix_tool_definitions_tool_id", "tool_definitions", ["tool_id"])
    op.create_index("ix_tool_definitions_name", "tool_definitions", ["name"])
    op.create_index("ix_tool_definitions_category", "tool_definitions", ["category"])
    op.create_index("ix_tool_definitions_status", "tool_definitions", ["status"])
    op.create_index("ix_tool_definitions_risk_classification", "tool_definitions", ["risk_classification"])  # noqa: E501


def downgrade() -> None:
    """Drop tool_definitions table."""
    op.drop_index("ix_tool_definitions_risk_classification", table_name="tool_definitions")
    op.drop_index("ix_tool_definitions_status", table_name="tool_definitions")
    op.drop_index("ix_tool_definitions_category", table_name="tool_definitions")
    op.drop_index("ix_tool_definitions_name", table_name="tool_definitions")
    op.drop_index("ix_tool_definitions_tool_id", table_name="tool_definitions")
    op.drop_index("ix_tool_definitions_tenant_id", table_name="tool_definitions")
    op.drop_table("tool_definitions")
