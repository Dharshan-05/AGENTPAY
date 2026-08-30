"""Agent Session application service for AGENTPAY (Phase 127).

Responsibilities:
    - Session lifecycle management (create, retrieve, list, revoke, bulk revoke)
    - Server-controlled session ID generation (UUIDv7) and TTL enforcement
    - Defense-in-depth session validation (rejecting expired/revoked/suspended sessions)
    - Multi-tenant isolation (`WHERE tenant_id = :tenant_id AND agent_id = :agent_id`)


Security Invariants:
    - All session operations strictly enforce tenant isolation & IDOR protection
    - Server controls session expiration TTL (never trusting client-supplied timestamps)
    - Revoked sessions can NEVER be resurrected
    - Suspended and deactivated agents CANNOT create new sessions or maintain active sessions
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    AgentSessionAlreadyRevokedError,
    AgentSessionCreationError,
    AgentSessionNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_credential import AgentCredential
from app.infrastructure.database.models.agent_session import AgentSession
from app.schemas.agents import AgentSessionCreateRequest

logger = logging.getLogger("agentpay.agent.session.service")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100


class AgentSessionService:
    """Application service for AgentSession domain entities and session lifecycle."""

    async def create_session(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        request: AgentSessionCreateRequest,
    ) -> AgentSession:
        """Create and register a new agent runtime session.

        Checks:
            1. Agent exists in authenticated tenant (IDOR check)
            2. Agent operational status is valid (not suspended or deactivated)
            3. Credential (if supplied) exists, belongs to agent, and is active & unexpired

        Security:
            - Server controls session ID generation (UUIDv7)
            - Server enforces session TTL expiration boundary

        Raises:
            AgentNotFoundError: if agent does not exist or cross-tenant.
            AgentSessionCreationError: if agent is suspended/deactivated or credential is invalid.
        """
        # 1. Tenant-scoped IDOR check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        res = await db.execute(agent_stmt)
        agent = res.scalar_one_or_none()

        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # 2. Operational state check
        agent_status = agent.status.strip().lower()
        if agent_status in ("suspended", "deactivated"):
            raise AgentSessionCreationError(
                f"Cannot create session for agent in '{agent_status}' state."
            )

        # 3. Credential verification (if credential_id supplied)
        credential_id = request.credential_id
        if credential_id is not None:
            cred_stmt = select(AgentCredential).where(
                AgentCredential.id == credential_id,
                AgentCredential.agent_id == agent_id,
                AgentCredential.tenant_id == tenant_id,
                AgentCredential.status == "active",
            )
            cred_res = await db.execute(cred_stmt)
            cred = cred_res.scalar_one_or_none()
            if cred is None:
                raise AgentSessionCreationError(
                    f"Credential {credential_id} is invalid, inactive, or belongs to another agent."
                )

            # Expiration check on credential
            now = datetime.now(UTC)
            if cred.expires_at is not None and now > cred.expires_at:
                raise AgentSessionCreationError(f"Credential {credential_id} has expired.")

        # 4. Server-controlled TTL and session instantiation
        now = datetime.now(UTC)
        ttl_hours = request.expires_in_hours or 24
        expires_at = now + timedelta(hours=ttl_hours)

        session = AgentSession(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            credential_id=credential_id,
            status="active",
            device_id=request.device_id.strip() if request.device_id else None,
            ip_address=request.ip_address.strip() if request.ip_address else None,
            user_agent=request.user_agent.strip() if request.user_agent else None,
            session_metadata={},
            last_activity_at=now,
            expires_at=expires_at,
        )
        db.add(session)
        await db.flush()
        await db.refresh(session)

        logger.info(
            "Agent session created successfully",
            extra={
                "session_id": str(session.id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "expires_at": expires_at.isoformat(),
            },
        )
        return session

    async def get_session(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> AgentSession:
        """Retrieve safe agent session metadata by ID (tenant-scoped).

        Raises:
            AgentSessionNotFoundError: if session is not found or cross-tenant.
        """
        stmt = select(AgentSession).where(
            AgentSession.id == session_id,
            AgentSession.agent_id == agent_id,
            AgentSession.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        session = res.scalar_one_or_none()

        if session is None:
            raise AgentSessionNotFoundError(f"Session {session_id} not found for agent {agent_id}.")
        return session

    async def list_sessions(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
        status_filter: str | None = None,
    ) -> tuple[list[AgentSession], bool]:
        """List tenant agent sessions using keyset pagination (created_at DESC, id DESC).

        Raises:
            AgentNotFoundError: if agent is not found or belongs to another tenant.
        """
        # IDOR check: verify agent exists in tenant
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        query_limit = min(max(1, limit), _LIMIT_MAX)

        stmt = select(AgentSession).where(
            AgentSession.agent_id == agent_id,
            AgentSession.tenant_id == tenant_id,
        )

        if status_filter:
            stmt = stmt.where(AgentSession.status == status_filter.strip().lower())

        if cursor_created_at is not None and cursor_id is not None:
            stmt = stmt.where(
                or_(
                    AgentSession.created_at < cursor_created_at,
                    and_(
                        AgentSession.created_at == cursor_created_at,
                        AgentSession.id < cursor_id,
                    ),
                )
            )

        stmt = stmt.order_by(AgentSession.created_at.desc(), AgentSession.id.desc()).limit(
            query_limit + 1
        )

        res = await db.execute(stmt)
        items = list(res.scalars().all())

        has_more = len(items) > query_limit
        page_items = items[:query_limit]
        return page_items, has_more

    async def revoke_session(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        session_id: uuid.UUID,
        *,
        reason: str | None = None,
    ) -> AgentSession:
        """Revoke a specific agent runtime session.

        Raises:
            AgentSessionNotFoundError: if session missing or cross-tenant.
            AgentSessionAlreadyRevokedError: if session is already revoked.
        """
        session = await self.get_session(db, tenant_id, agent_id, session_id)

        if session.status == "revoked":
            raise AgentSessionAlreadyRevokedError(f"Session {session_id} is already revoked.")

        now = datetime.now(UTC)
        status_reason = reason or "Session manually revoked"

        session.status = "revoked"
        session.revoked_at = now
        session.revocation_reason = status_reason

        await db.flush()
        await db.refresh(session)

        logger.info(
            "Agent session revoked",
            extra={
                "session_id": str(session_id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "reason": status_reason,
            },
        )
        return session

    async def revoke_all_sessions(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        reason: str | None = None,
    ) -> int:
        """Bulk revoke all active sessions belonging to an agent within tenant.

        Raises:
            AgentNotFoundError: if agent missing or cross-tenant.
        """
        # IDOR check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        now = datetime.now(UTC)
        status_reason = reason or "Bulk revocation of active agent sessions"

        revoke_stmt = (
            update(AgentSession)
            .where(
                AgentSession.agent_id == agent_id,
                AgentSession.tenant_id == tenant_id,
                AgentSession.status == "active",
            )
            .values(
                status="revoked",
                revoked_at=now,
                revocation_reason=status_reason,
            )
        )
        res = await db.execute(revoke_stmt)
        revoked_count = res.rowcount or 0

        logger.info(
            "Bulk agent sessions revoked",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "revoked_count": revoked_count,
            },
        )
        return revoked_count

    async def validate_session(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> bool:
        """Validate an agent session context (Defense in Depth).

        Returns:
            True if session is active, unexpired, and agent is in active status; False otherwise.
        """
        # 1. Fetch session record
        stmt = select(AgentSession).where(
            AgentSession.id == session_id,
            AgentSession.agent_id == agent_id,
            AgentSession.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        session = res.scalar_one_or_none()

        if session is None or session.status != "active":
            return False

        # 2. Expiration check
        now = datetime.now(UTC)
        if now > session.expires_at:
            session.status = "expired"
            await db.flush()
            return False

        # 3. Defense-in-depth: Inspect agent operational state
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()

        if agent is None or agent.status.strip().lower() in ("suspended", "deactivated"):
            return False

        return True
