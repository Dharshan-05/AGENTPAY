"""ATIM Group 13 / Phase 24 Multi-Agent Distributed Consensus Application Service."""

from __future__ import annotations

import hmac
import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.base import DomainError
from app.domain.governance.consensus_models import (
    ConsensusSessionRecord,
    ConsensusSessionStatus,
    ConsensusVoteRecord,
    VoteType,
)
from app.infrastructure.database.models.atim_consensus import (
    ATIMConsensusSession,
    ATIMConsensusVote,
)

logger = logging.getLogger("agentpay.atim.consensus")

HMAC_SECRET = b"agentpay_atim_consensus_hmac_secret_v1"


class ConsensusError(DomainError):
    """Base exception for consensus service failures."""


class SeparationOfDutiesError(ConsensusError):
    """Raised when an agent attempts to violate separation-of-duties rules."""


class QuorumError(ConsensusError):
    """Raised when consensus voting fails or is invalid."""


class ATIMConsensusService:
    """Application Service orchestrating Multi-Agent Distributed Consensus & Separation of Duties."""

    async def create_session(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        proposer_agent_id: uuid.UUID,
        action: str,
        required_quorum: int = 2,
        workflow_id: Optional[uuid.UUID] = None,
        timeout_seconds: int = 300,
    ) -> ConsensusSessionRecord:
        """Create a new multi-agent consensus session under tenant scope."""
        if required_quorum < 2:
            raise QuorumError("Required quorum must be at least 2 participant agents.")

        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=timeout_seconds)

        session_entity = ATIMConsensusSession(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            proposer_agent_id=proposer_agent_id,
            workflow_id=workflow_id,
            action=action,
            required_quorum=required_quorum,
            status=ConsensusSessionStatus.VOTING.value,
            created_at=now,
            expires_at=expires_at,
        )

        db.add(session_entity)
        await db.flush()

        logger.info(
            "Created ATIM consensus session %s for action '%s' (required quorum: %d)",
            session_entity.id,
            action,
            required_quorum,
        )

        return ConsensusSessionRecord(
            id=session_entity.id,
            tenant_id=session_entity.tenant_id,
            proposer_agent_id=session_entity.proposer_agent_id,
            workflow_id=session_entity.workflow_id,
            action=session_entity.action,
            required_quorum=session_entity.required_quorum,
            status=ConsensusSessionStatus(session_entity.status),
            created_at=session_entity.created_at,
            expires_at=session_entity.expires_at,
        )

    def _generate_vote_signature(
        self,
        session_id: uuid.UUID,
        voter_agent_id: uuid.UUID,
        vote: str,
        voted_at: datetime,
    ) -> str:
        """Generate HMAC-SHA256 signature for immutable vote audit verification."""
        msg = f"{session_id}:{voter_agent_id}:{vote}:{voted_at.isoformat()}".encode("utf-8")
        return hmac.new(HMAC_SECRET, msg, hashlib.sha256).hexdigest()

    async def record_vote(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        session_id: uuid.UUID,
        voter_agent_id: uuid.UUID,
        vote: VoteType,
        reason: Optional[str] = None,
    ) -> ConsensusSessionRecord:
        """Record an agent's vote in a consensus session, enforcing SoD and updating quorum status."""
        stmt = (
            select(ATIMConsensusSession)
            .where(
                ATIMConsensusSession.id == session_id,
                ATIMConsensusSession.tenant_id == tenant_id,
            )
            .with_for_update()
        )
        res = await db.execute(stmt)
        session = res.scalar_one_or_none()

        if not session:
            raise ConsensusError(f"Consensus session '{session_id}' not found under tenant '{tenant_id}'.")

        now = datetime.now(timezone.utc)
        if session.expires_at and now > session.expires_at:
            session.status = ConsensusSessionStatus.EXPIRED.value
            await db.flush()
            raise QuorumError(f"Consensus session '{session_id}' has expired.")

        if session.status != ConsensusSessionStatus.VOTING.value:
            raise QuorumError(f"Consensus session '{session_id}' is not in VOTING state (current: {session.status}).")

        # SoD Enforcement: Proposer agent cannot vote in its own session
        if voter_agent_id == session.proposer_agent_id:
            raise SeparationOfDutiesError("Proposing agent cannot vote in its own consensus session (SoD Violation).")

        # Check duplicate vote
        for existing_vote in session.votes:
            if existing_vote.voter_agent_id == voter_agent_id:
                raise QuorumError(f"Agent '{voter_agent_id}' has already voted in session '{session_id}'.")

        vote_signature = self._generate_vote_signature(session_id, voter_agent_id, vote.value, now)

        vote_entity = ATIMConsensusVote(
            id=uuid.uuid4(),
            session_id=session_id,
            tenant_id=tenant_id,
            voter_agent_id=voter_agent_id,
            vote=vote.value,
            reason=reason,
            vote_signature=vote_signature,
            voted_at=now,
        )

        db.add(vote_entity)
        session.votes.append(vote_entity)
        await db.flush()

        # Re-evaluate quorum
        approve_count = sum(1 for v in session.votes if v.vote == VoteType.APPROVE.value)
        reject_count = sum(1 for v in session.votes if v.vote == VoteType.REJECT.value)

        if approve_count >= session.required_quorum:
            session.status = ConsensusSessionStatus.QUORUM_REACHED.value
            logger.info("Consensus session %s REACHED QUORUM (%d approvals)", session_id, approve_count)
        elif reject_count >= session.required_quorum:
            session.status = ConsensusSessionStatus.QUORUM_FAILED.value
            logger.info("Consensus session %s FAILED QUORUM (%d rejections)", session_id, reject_count)

        await db.flush()

        return ConsensusSessionRecord(
            id=session.id,
            tenant_id=session.tenant_id,
            proposer_agent_id=session.proposer_agent_id,
            workflow_id=session.workflow_id,
            action=session.action,
            required_quorum=session.required_quorum,
            status=ConsensusSessionStatus(session.status),
            created_at=session.created_at,
            expires_at=session.expires_at,
        )

    async def get_session(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> Optional[ConsensusSessionRecord]:
        """Fetch a consensus session under tenant boundary."""
        stmt = select(ATIMConsensusSession).where(
            ATIMConsensusSession.id == session_id,
            ATIMConsensusSession.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        session = res.scalar_one_or_none()

        if not session:
            return None

        now = datetime.now(timezone.utc)
        if session.status == ConsensusSessionStatus.VOTING.value and session.expires_at and now > session.expires_at:
            session.status = ConsensusSessionStatus.EXPIRED.value
            await db.flush()

        return ConsensusSessionRecord(
            id=session.id,
            tenant_id=session.tenant_id,
            proposer_agent_id=session.proposer_agent_id,
            workflow_id=session.workflow_id,
            action=session.action,
            required_quorum=session.required_quorum,
            status=ConsensusSessionStatus(session.status),
            created_at=session.created_at,
            expires_at=session.expires_at,
        )
