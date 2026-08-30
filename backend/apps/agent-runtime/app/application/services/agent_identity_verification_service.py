"""Agent Identity Verification Application Service for AGENTPAY (Phase 182)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.schemas.agent_identity_verification import AgentIdentityVerificationResult

logger = logging.getLogger("agentguard.security.identity_verification")


class AgentIdentityVerificationService:
    """Production identity verification service for AI agents in AGENTGUARD (Phase 182)."""

    async def verify_agent_identity(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        principal_id: uuid.UUID | None = None,
    ) -> AgentIdentityVerificationResult:
        """Verify agent identity, status, and tenant boundary fail-closed (Phase 182)."""
        now = datetime.now(UTC)

        # 1. Fetch Agent within strict tenant boundary
        stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
        )
        import inspect

        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res

        agent: Agent | None = None
        if hasattr(res, "scalar_one_or_none"):
            agent = res.scalar_one_or_none()
            if inspect.isawaitable(agent):
                agent = await agent
        elif hasattr(res, "scalars"):
            sc = res.scalars()
            if inspect.isawaitable(sc):
                sc = await sc
            agent = sc.first()
            if inspect.isawaitable(agent):
                agent = await agent

        # 2. Fail-closed anti-enumeration check
        if not agent:
            logger.warning(
                "Agent identity verification failed: agent %s not found in tenant %s",
                agent_id,
                tenant_id,
            )
            raise AgentNotFoundError(f"Agent {agent_id} not found in tenant {tenant_id}.")

        # 3. Check for deleted or archived status
        if getattr(agent, "deleted_at", None) is not None or agent.status in (
            "deleted",
            "archived",
        ):  # noqa: E501
            logger.info("Agent %s identity rejected: agent is deleted/archived", agent_id)
            return AgentIdentityVerificationResult(
                agent_id=agent_id,
                tenant_id=tenant_id,
                authenticated_principal_id=principal_id,
                verified=False,
                agent_status=agent.status or "deleted",
                verification_reason=f"Agent '{agent_id}' has been deleted/archived.",
                verified_at=now,
            )

        # 4. Check active operational status
        if agent.status != "active":
            logger.info(
                "Agent %s identity rejected: status '%s' is not active", agent_id, agent.status
            )
            return AgentIdentityVerificationResult(
                agent_id=agent_id,
                tenant_id=tenant_id,
                authenticated_principal_id=principal_id,
                verified=False,
                agent_status=agent.status,
                verification_reason=f"Agent status '{agent.status}' is not active.",
                verified_at=now,
            )

        # 5. Principal validation
        if principal_id is not None and principal_id == uuid.UUID(int=0):
            logger.info("Agent %s identity rejected: invalid principal ID", agent_id)
            return AgentIdentityVerificationResult(
                agent_id=agent_id,
                tenant_id=tenant_id,
                authenticated_principal_id=principal_id,
                verified=False,
                agent_status=agent.status,
                verification_reason="Invalid requesting principal identity.",
                verified_at=now,
            )

        logger.info("Agent %s identity verified successfully for tenant %s", agent_id, tenant_id)
        return AgentIdentityVerificationResult(
            agent_id=agent_id,
            tenant_id=tenant_id,
            authenticated_principal_id=principal_id,
            verified=True,
            agent_status=agent.status,
            verification_reason="Agent identity verified successfully.",
            verified_at=now,
        )
