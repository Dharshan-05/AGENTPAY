"""Unit tests for ATIM Group 13 / Phase 24 Multi-Agent Distributed Consensus Service."""

from __future__ import annotations

import uuid
import pytest
from app.application.services.atim_consensus_service import (
    ATIMConsensusService,
    ConsensusError,
    QuorumError,
    SeparationOfDutiesError,
)
from app.domain.governance.consensus_models import ConsensusSessionStatus, VoteType


@pytest.fixture
def consensus_service() -> ATIMConsensusService:
    return ATIMConsensusService()


@pytest.mark.asyncio
async def test_consensus_session_creation(db_session, consensus_service):
    """Test creating a valid multi-agent consensus session."""
    tenant_id = uuid.uuid4()
    proposer_id = uuid.uuid4()

    session = await consensus_service.create_session(
        db=db_session,
        tenant_id=tenant_id,
        proposer_agent_id=proposer_id,
        action="PURCHASE_APPROVAL",
        required_quorum=2,
        timeout_seconds=300,
    )

    assert session.tenant_id == tenant_id
    assert session.proposer_agent_id == proposer_id
    assert session.action == "PURCHASE_APPROVAL"
    assert session.required_quorum == 2
    assert session.status == ConsensusSessionStatus.VOTING


@pytest.mark.asyncio
async def test_consensus_sod_enforcement(db_session, consensus_service):
    """Test that proposing agent cannot vote in its own consensus session (SoD Violation)."""
    tenant_id = uuid.uuid4()
    proposer_id = uuid.uuid4()

    session = await consensus_service.create_session(
        db=db_session,
        tenant_id=tenant_id,
        proposer_agent_id=proposer_id,
        action="PURCHASE_APPROVAL",
        required_quorum=2,
    )

    with pytest.raises(SeparationOfDutiesError):
        await consensus_service.record_vote(
            db=db_session,
            tenant_id=tenant_id,
            session_id=session.id,
            voter_agent_id=proposer_id,  # Same as proposer
            vote=VoteType.APPROVE,
        )


@pytest.mark.asyncio
async def test_consensus_quorum_reached(db_session, consensus_service):
    """Test multi-agent voting reaching quorum threshold."""
    tenant_id = uuid.uuid4()
    proposer_id = uuid.uuid4()
    voter1_id = uuid.uuid4()
    voter2_id = uuid.uuid4()

    session = await consensus_service.create_session(
        db=db_session,
        tenant_id=tenant_id,
        proposer_agent_id=proposer_id,
        action="TREASURY_TRANSFER",
        required_quorum=2,
    )

    # Vote 1
    session = await consensus_service.record_vote(
        db=db_session,
        tenant_id=tenant_id,
        session_id=session.id,
        voter_agent_id=voter1_id,
        vote=VoteType.APPROVE,
        reason="Risk metrics compliant",
    )
    assert session.status == ConsensusSessionStatus.VOTING

    # Vote 2 -> Quorum Reached
    session = await consensus_service.record_vote(
        db=db_session,
        tenant_id=tenant_id,
        session_id=session.id,
        voter_agent_id=voter2_id,
        vote=VoteType.APPROVE,
        reason="Compliance checks passed",
    )
    assert session.status == ConsensusSessionStatus.QUORUM_REACHED


@pytest.mark.asyncio
async def test_consensus_duplicate_vote_prevention(db_session, consensus_service):
    """Test that duplicate votes from the same agent identity are rejected."""
    tenant_id = uuid.uuid4()
    proposer_id = uuid.uuid4()
    voter_id = uuid.uuid4()

    session = await consensus_service.create_session(
        db=db_session,
        tenant_id=tenant_id,
        proposer_agent_id=proposer_id,
        action="LARGE_PURCHASE",
        required_quorum=2,
    )

    await consensus_service.record_vote(
        db=db_session,
        tenant_id=tenant_id,
        session_id=session.id,
        voter_agent_id=voter_id,
        vote=VoteType.APPROVE,
    )

    with pytest.raises(QuorumError):
        await consensus_service.record_vote(
            db=db_session,
            tenant_id=tenant_id,
            session_id=session.id,
            voter_agent_id=voter_id,  # Duplicate
            vote=VoteType.APPROVE,
        )
