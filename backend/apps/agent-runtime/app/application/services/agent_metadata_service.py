"""Agent Metadata application service for AGENTPAY (Phase 131).

Responsibilities:
    - Tenant-isolated AgentMetadata resolution and profile maintenance
    - Protection of internal server-controlled fields (`id`, `tenant_id`, `agent_id`, etc.)
    - Sanitization against secrets or raw credentials in JSONB metadata payload
    - IDOR protection: Cross-tenant attempts raise `AgentNotFoundError` (404)
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_metadata import AgentMetadata

logger = logging.getLogger("agentpay.agent.metadata.service")

# Forbidden fields that clients MUST NOT inject via metadata_payload
PROTECTED_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "id",
        "agent_id",
        "tenant_id",
        "created_at",
        "updated_at",
        "deleted_at",
        "status",
        "trust_score",
        "password",
        "secret",
        "raw_secret",
        "token",
        "access_token",
        "refresh_token",
        "jwt",
    }
)


class AgentMetadataService:
    """Application service for Agent Metadata management (Phase 131)."""

    async def get_agent_metadata(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> AgentMetadata:
        """Retrieve AgentMetadata within authenticated tenant scope.

        Raises:
            AgentNotFoundError: if agent or metadata is not found or belongs to another tenant.
        """
        stmt = select(AgentMetadata).where(
            AgentMetadata.agent_id == agent_id,
            AgentMetadata.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        metadata = res.scalar_one_or_none()

        if metadata is None:
            # Check if Agent exists in tenant
            agent_stmt = select(Agent).where(
                Agent.id == agent_id,
                Agent.tenant_id == tenant_id,
                Agent.deleted_at.is_(None),
            )
            agent_res = await db.execute(agent_stmt)
            if agent_res.scalar_one_or_none() is None:
                raise AgentNotFoundError(f"Agent {agent_id} not found.")

            # Create default empty metadata record if missing
            metadata = AgentMetadata(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                agent_id=agent_id,
                metadata_payload={},
            )
            db.add(metadata)
            await db.flush()
            await db.refresh(metadata)

        return metadata

    async def update_agent_metadata(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        updates: dict[str, Any],
    ) -> AgentMetadata:
        """Update/merge custom non-sensitive metadata for an Agent.

        Behavior:
            - Verifies Agent ownership within authenticated tenant
            - Strips protected fields and secret material
            - Merges new metadata into existing `metadata_payload` dictionary
            - Flushes database updates atomically

        Raises:
            AgentNotFoundError: if agent not found in tenant.
        """
        metadata = await self.get_agent_metadata(db, tenant_id, agent_id)

        # Sanitize incoming payload
        sanitized_payload = {
            k: v for k, v in updates.items() if k.lower() not in PROTECTED_METADATA_KEYS
        }

        current_payload = dict(metadata.metadata_payload or {})
        current_payload.update(sanitized_payload)
        metadata.metadata_payload = current_payload

        await db.flush()
        await db.refresh(metadata)

        logger.info(
            "Agent metadata updated",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "updated_keys": list(sanitized_payload.keys()),
            },
        )

        return metadata
