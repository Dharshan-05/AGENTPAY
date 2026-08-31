"""ATIM Group 13 / Phase 24 Multi-Agent Consensus Domain Models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ConsensusSessionStatus(StrEnum):
    """Execution status for multi-agent consensus sessions."""

    INITIATED = "INITIATED"
    VOTING = "VOTING"
    QUORUM_REACHED = "QUORUM_REACHED"
    QUORUM_FAILED = "QUORUM_FAILED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class VoteType(StrEnum):
    """Vote classification for consensus participant agents."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"


class ConsensusSessionRecord(BaseModel):
    """Domain model representing a multi-agent consensus session."""

    model_config = ConfigDict(frozen=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    proposer_agent_id: uuid.UUID
    workflow_id: Optional[uuid.UUID] = None
    action: str = Field(min_length=1, max_length=64)
    required_quorum: int = Field(ge=2, default=2)
    status: ConsensusSessionStatus = ConsensusSessionStatus.INITIATED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime


class ConsensusVoteRecord(BaseModel):
    """Domain model representing an individual agent's vote in a consensus session."""

    model_config = ConfigDict(frozen=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    session_id: uuid.UUID
    tenant_id: uuid.UUID
    voter_agent_id: uuid.UUID
    vote: VoteType
    reason: Optional[str] = Field(default=None, max_length=512)
    vote_signature: str = Field(min_length=16, max_length=256)
    voted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
