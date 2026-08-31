"""Alembic migration 048: ATIM Multi-Agent Distributed Consensus & Transactional Multi-Party Governance (Phase 24 / Group 13)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "048"
down_revision: Union[str, None] = "047"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table: atim_consensus_sessions
    op.create_table(
        "atim_consensus_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("proposer_agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("required_quorum", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="INITIATED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_atim_consensus_sessions"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["proposer_agent_id"], ["agents.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["workflow_id"], ["atim_workflow_instances.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_atim_consensus_sessions_tenant_id",
        "atim_consensus_sessions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_atim_consensus_sessions_proposer_agent_id",
        "atim_consensus_sessions",
        ["proposer_agent_id"],
    )
    op.create_index(
        "ix_atim_consensus_sessions_workflow_id",
        "atim_consensus_sessions",
        ["workflow_id"],
    )
    op.create_index(
        "ix_atim_consensus_sessions_status",
        "atim_consensus_sessions",
        ["status"],
    )

    # 2. Table: atim_consensus_votes
    op.create_table(
        "atim_consensus_votes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("voter_agent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vote", sa.String(length=16), nullable=False),
        sa.Column("reason", sa.String(length=512), nullable=True),
        sa.Column("vote_signature", sa.String(length=256), nullable=False),
        sa.Column("voted_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_atim_consensus_votes"),
        sa.ForeignKeyConstraint(["session_id"], ["atim_consensus_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["voter_agent_id"], ["agents.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("session_id", "voter_agent_id", name="uq_session_voter"),
    )
    op.create_index(
        "ix_atim_consensus_votes_session_id",
        "atim_consensus_votes",
        ["session_id"],
    )
    op.create_index(
        "ix_atim_consensus_votes_tenant_id",
        "atim_consensus_votes",
        ["tenant_id"],
    )
    op.create_index(
        "ix_atim_consensus_votes_voter_agent_id",
        "atim_consensus_votes",
        ["voter_agent_id"],
    )


def downgrade() -> None:
    op.drop_table("atim_consensus_votes")
    op.drop_table("atim_consensus_sessions")
