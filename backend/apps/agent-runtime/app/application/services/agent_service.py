"""Agent Registry, Creation & Identity application service for AGENTPAY (Phase 119–121).

Responsibilities:
    - Agent Registry Discovery (Phase 119): Tenant-isolated listing with keyset pagination & search
    - Agent Creation (Phase 120): Production-grade atomic agent + identity provision
    - Agent Identity Management (Phase 121): Safe agent identity resolution & ownership validation

Security Invariants:
    - ALL database queries enforce tenant_id isolation
    - Zero secret credential generation or exposure (credentials belong to Phase 122)
    - Keyset pagination (created_at DESC, id DESC) prevents N+1 and OFFSET performance degradation
    - IDOR protection: Cross-tenant attempts return AgentNotFoundError (HTTP 404 anti-enumeration)
    - Atomic transaction boundary: Agent + AgentIdentity are committed together or rolled back
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.exceptions.agent_exceptions import (
    AgentAlreadyExistsError,
    AgentIdentityAlreadyExistsError,
    AgentIdentityNotFoundError,
    AgentNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_identity import AgentIdentity
from app.infrastructure.database.models.agent_lifecycle import AgentLifecycle
from app.schemas.agents import AgentCreateRequest

logger = logging.getLogger("agentpay.agent.service")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100


def _slugify(text: str) -> str:
    """Generate a clean URL-safe slug from input text."""
    cleaned = text.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")
    return slug or f"agent-{uuid.uuid4().hex[:8]}"


class AgentIdentityService:
    """Application service for managing non-secret AgentIdentity domain entities (Phase 121)."""

    async def get_agent_identity(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> AgentIdentity:
        """Retrieve agent identity for an authorized agent within the authenticated tenant.

        Raises:
            AgentIdentityNotFoundError: if identity or agent does not exist in tenant scope.
        """
        stmt = select(AgentIdentity).where(
            AgentIdentity.agent_id == agent_id,
            AgentIdentity.tenant_id == tenant_id,
            AgentIdentity.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        identity = result.scalar_one_or_none()
        if identity is None:
            raise AgentIdentityNotFoundError(f"Identity for agent {agent_id} not found.")
        return identity

    async def create_agent_identity(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        display_name: str | None = None,
        identity_type: str = "standard",
        external_reference: str | None = None,
        description: str | None = None,
    ) -> AgentIdentity:
        """Create a new AgentIdentity record bound to an existing Agent within tenant scope.

        Raises:
            AgentIdentityAlreadyExistsError: if an identity already exists for this agent.
        """
        existing_stmt = select(AgentIdentity).where(
            AgentIdentity.agent_id == agent_id,
            AgentIdentity.tenant_id == tenant_id,
            AgentIdentity.deleted_at.is_(None),
        )
        res = await db.execute(existing_stmt)
        if res.scalar_one_or_none() is not None:
            raise AgentIdentityAlreadyExistsError(f"Identity already exists for agent {agent_id}.")

        identity = AgentIdentity(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            display_name=display_name,
            identity_type=identity_type,
            external_reference=external_reference,
            description=description,
        )
        db.add(identity)
        await db.flush()
        await db.refresh(identity)
        logger.info(
            "Agent identity created",
            extra={
                "identity_id": str(identity.id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
            },
        )
        return identity


class AgentService:
    """Application service for Agent Registry (Phase 119) and Creation (Phase 120)."""

    def __init__(self, identity_service: AgentIdentityService | None = None) -> None:
        self.identity_service = identity_service or AgentIdentityService()

    async def list_agents(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        *,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
        search: str | None = None,
        agent_type: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Agent], bool]:
        """List agents belonging to the authenticated tenant using keyset pagination.

        Returns:
            (agents, has_more) — page of agents (max size limit) and flag indicating if more exist.
        """
        limit = min(max(1, limit), _LIMIT_MAX)
        fetch_limit = limit + 1

        stmt = (
            select(Agent)
            .where(
                Agent.tenant_id == tenant_id,
                Agent.deleted_at.is_(None),
            )
            .options(selectinload(Agent.identity))
        )

        # Filters
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Agent.name.ilike(term),
                    Agent.slug.ilike(term),
                )
            )

        if agent_type and agent_type.strip():
            stmt = stmt.where(Agent.agent_type == agent_type.strip())

        if status and status.strip():
            stmt = stmt.where(Agent.status == status.strip())

        # Keyset pagination ordering: created_at DESC, id DESC
        if cursor_created_at is not None and cursor_id is not None:
            stmt = stmt.where(
                or_(
                    Agent.created_at < cursor_created_at,
                    and_(
                        Agent.created_at == cursor_created_at,
                        Agent.id < cursor_id,
                    ),
                )
            )

        stmt = stmt.order_by(Agent.created_at.desc(), Agent.id.desc()).limit(fetch_limit)
        result = await db.execute(stmt)
        rows = list(result.scalars().all())

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        return rows, has_more

    async def get_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> Agent:
        """Retrieve an individual agent by ID within authenticated tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or belongs to another tenant (IDOR-safe 404).
        """
        stmt = (
            select(Agent)
            .where(
                Agent.id == agent_id,
                Agent.tenant_id == tenant_id,
                Agent.deleted_at.is_(None),
            )
            .options(selectinload(Agent.identity))
        )
        result = await db.execute(stmt)
        agent = result.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")
        return agent

    async def create_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        request_data: AgentCreateRequest,
    ) -> Agent:
        """Execute atomic creation of a new Agent and its default AgentIdentity.

        Behavior:
            - Validates slug or generates a URL-safe slug from `name`
            - Checks tenant-scoped slug uniqueness
            - Creates `Agent` entity and `AgentIdentity` entity in the SAME transaction
            - Flushes and returns the fully populated `Agent` instance

        Raises:
            AgentAlreadyExistsError: if an agent with the target slug already exists in tenant.
        """
        target_slug = request_data.slug or _slugify(request_data.name)

        # 1. Tenant-scoped uniqueness check
        existing_stmt = select(Agent).where(
            Agent.tenant_id == tenant_id,
            Agent.slug == target_slug,
            Agent.deleted_at.is_(None),
        )
        res = await db.execute(existing_stmt)
        if res.scalar_one_or_none() is not None:
            raise AgentAlreadyExistsError(
                f"An agent with slug '{target_slug}' already exists in this tenant."
            )

        # 2. Instantiate Agent
        agent_id = uuid.uuid4()
        agent = Agent(
            id=agent_id,
            tenant_id=tenant_id,
            name=request_data.name.strip(),
            slug=target_slug,
            agent_type=request_data.agent_type.strip(),
            status="provisioning",
            description=request_data.description.strip() if request_data.description else None,
        )
        db.add(agent)

        # 3. Instantiate AgentIdentity in SAME transaction
        identity = AgentIdentity(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            display_name=request_data.display_name or request_data.name.strip(),
            identity_type=request_data.identity_type.strip(),
            external_reference=request_data.external_reference.strip()
            if request_data.external_reference
            else None,
            description=request_data.description.strip() if request_data.description else None,
        )
        db.add(identity)

        # 4. Instantiate AgentLifecycle in SAME transaction
        lifecycle = AgentLifecycle(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            status="provisioning",
            status_reason="Agent provisioned",
        )
        db.add(lifecycle)

        # 4. Flush and refresh atomically
        await db.flush()
        await db.refresh(agent, ["identity"])

        logger.info(
            "Agent and identity created atomically",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "slug": target_slug,
            },
        )
        return agent
