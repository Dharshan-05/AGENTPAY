"""Alembic migration 045: ATIM Compliance Evidence Table (Group 10)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "045"
down_revision: Union[str, None] = "044"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Table: atim_compliance_evidence
    op.create_table(
        "atim_compliance_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=False),
        sa.Column("decision_precedence", sa.String(length=128), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("signature", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_atim_compliance_evidence"),
    )
    op.create_index(
        "ix_atim_comp_evidence_tenant_cat",
        "atim_compliance_evidence",
        ["tenant_id", "category"],
    )
    op.create_index(
        "ix_atim_comp_evidence_created_at",
        "atim_compliance_evidence",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_atim_comp_evidence_created_at", table_name="atim_compliance_evidence")
    op.drop_index("ix_atim_comp_evidence_tenant_cat", table_name="atim_compliance_evidence")
    op.drop_table("atim_compliance_evidence")
