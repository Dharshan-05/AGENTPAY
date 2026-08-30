"""Agent Trust Data application service for AGENTPAY (Phase 134).

Responsibilities:
    - Controlled, tenant-isolated trust posture resolution and administrative updates
    - Score validation (numerical range 0.00 to 100.00)
    - Prevention of client-controlled trust mutation (server/admin controlled only)
    - Integration with Audit and Security Events
    - IDOR protection: Cross-tenant attempts raise `AgentNotFoundError` (404)
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    InvalidAgentTrustScoreError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_trust import AgentTrust

logger = logging.getLogger("agentpay.agent.trust.service")

VALID_TRUST_STATUSES: frozenset[str] = frozenset({"unknown", "low", "medium", "high", "restricted"})


class AgentTrustService:
    """Application service for managing Agent trust data posture (Phase 134)."""

    async def get_agent_trust(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> AgentTrust:
        """Retrieve AgentTrust posture for an agent within tenant scope.

        Raises:
            AgentNotFoundError: if agent or trust record is missing or cross-tenant.
        """
        stmt = select(AgentTrust).where(
            AgentTrust.agent_id == agent_id,
            AgentTrust.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        trust = res.scalar_one_or_none()

        if trust is None:
            # Check if agent exists in tenant
            agent_stmt = select(Agent).where(
                Agent.id == agent_id,
                Agent.tenant_id == tenant_id,
                Agent.deleted_at.is_(None),
            )
            agent_res = await db.execute(agent_stmt)
            if agent_res.scalar_one_or_none() is None:
                raise AgentNotFoundError(f"Agent {agent_id} not found.")

            # Create default 'unknown' trust record if missing
            trust = AgentTrust(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                agent_id=agent_id,
                trust_status="unknown",
                trust_score=None,
                trust_reason="Initial trust posture",
                trust_metadata={},
            )
            db.add(trust)
            await db.flush()
            await db.refresh(trust)

        return trust

    async def update_agent_trust(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        trust_status: str | None = None,
        trust_score: Decimal | None = None,
        trust_reason: str | None = None,
        trust_metadata: dict[str, Any] | None = None,
    ) -> AgentTrust:
        """Execute controlled administrative update of agent trust posture.

        Validations:
            - Agent ownership in authenticated tenant
            - Score range: 0.00 <= score <= 100.00
            - Status in VALID_TRUST_STATUSES

        Raises:
            AgentNotFoundError: if agent not found in tenant.
            InvalidAgentTrustScoreError: if score is out of range or status invalid.
        """
        trust = await self.get_agent_trust(db, tenant_id, agent_id)

        if trust_score is not None:
            if trust_score < Decimal("0.00") or trust_score > Decimal("100.00"):
                raise InvalidAgentTrustScoreError(
                    f"Trust score {trust_score} must be between 0.00 and 100.00."
                )
            trust.trust_score = trust_score

        if trust_status is not None and trust_status.strip():
            st = trust_status.strip().lower()
            if st not in VALID_TRUST_STATUSES:
                raise InvalidAgentTrustScoreError(f"Unknown trust status '{trust_status}'.")
            trust.trust_status = st

        if trust_reason is not None:
            trust.trust_reason = trust_reason.strip()

        if trust_metadata is not None:
            curr_meta = dict(trust.trust_metadata or {})
            curr_meta.update(trust_metadata)
            trust.trust_metadata = curr_meta

        trust.evaluated_at = datetime.now(UTC)

        await db.flush()
        await db.refresh(trust)

        logger.info(
            "Agent trust posture updated",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "trust_status": trust.trust_status,
                "trust_score": str(trust.trust_score) if trust.trust_score else None,
            },
        )

        return trust
