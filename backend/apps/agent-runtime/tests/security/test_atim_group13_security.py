"""Security tests for ATIM Group 13 / Phase 24 Multi-Agent Consensus Security Invariants."""

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.application.services.atim_consensus_service import (
    ATIMConsensusService,
    SeparationOfDutiesError,
)
from app.domain.governance.consensus_models import VoteType
from app.infrastructure.database.models.session import Session as SessionModel
from app.infrastructure.database.models.user import User
from app.main import app


@pytest.mark.asyncio
async def test_cross_tenant_consensus_voting_forbidden(db_session):
    """Security Invariant: Cross-tenant voting attempts must be rejected with 403 / Forbidden error."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    proposer_agent = uuid.uuid4()
    voter_agent = uuid.uuid4()

    service = ATIMConsensusService()
    session = await service.create_session(
        db=db_session,
        tenant_id=tenant_a,
        proposer_agent_id=proposer_agent,
        action="SENSITIVE_PAYMENT",
        required_quorum=2,
    )

    # Tenant B tries to vote in Tenant A's session
    with pytest.raises(Exception):
        await service.record_vote(
            db=db_session,
            tenant_id=tenant_b,  # Tenant mismatch
            session_id=session.id,
            voter_agent_id=voter_agent,
            vote=VoteType.APPROVE,
        )


@pytest.mark.asyncio
async def test_proposer_self_voting_security_rejection(db_session):
    """Security Invariant: Proposer agent cannot vote in its own session (SoD Enforcement)."""
    tenant_id = uuid.uuid4()
    proposer_agent = uuid.uuid4()

    service = ATIMConsensusService()
    session = await service.create_session(
        db=db_session,
        tenant_id=tenant_id,
        proposer_agent_id=proposer_agent,
        action="POLICY_OVERRIDE",
        required_quorum=2,
    )

    with pytest.raises(SeparationOfDutiesError):
        await service.record_vote(
            db=db_session,
            tenant_id=tenant_id,
            session_id=session.id,
            voter_agent_id=proposer_agent,
            vote=VoteType.APPROVE,
        )
