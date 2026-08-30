"""Agent Audit Events application service for AGENTPAY (Phase 132).

Responsibilities:
    - Transactional creation of immutable append-only `AgentAudit` log entries
    - Keyset-paginated audit log retrieval within tenant scope (`occurred_at DESC, id DESC`)
    - Context sanitization (zero secrets, passwords, or raw tokens in metadata)
    - IDOR protection: Cross-tenant attempts return `AgentNotFoundError` (404)
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_audit import AgentAudit

logger = logging.getLogger("agentpay.agent.audit.service")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100

SENSITIVE_AUDIT_KEYS: frozenset[str] = frozenset(
    {
        "password",
        "raw_secret",
        "secret",
        "secret_hash",
        "access_token",
        "refresh_token",
        "jwt",
        "private_key",
        "authorization",
    }
)


def _sanitize_metadata(data: dict[str, Any] | None) -> dict[str, Any]:
    """Recursively strip sensitive keys from audit event metadata dict."""
    if not data:
        return {}
    clean: dict[str, Any] = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_AUDIT_KEYS:
            clean[k] = "[REDACTED]"
        elif isinstance(v, dict):
            clean[k] = _sanitize_metadata(v)
        else:
            clean[k] = v
    return clean


class AgentAuditService:
    """Application service for managing immutable Agent audit events (Phase 132)."""

    async def record_audit_event(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        actor_id: uuid.UUID,
        event_type: str,
        event_action: str,
        *,
        actor_type: str = "user",
        event_result: str = "success",
        request_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        event_metadata: dict[str, Any] | None = None,
    ) -> AgentAudit:
        """Create and persist an immutable append-only `AgentAudit` record.

        No UPDATE or DELETE endpoints are provided by design.
        """
        clean_metadata = _sanitize_metadata(event_metadata)

        audit_entry = AgentAudit(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_type=actor_type,
            actor_id=actor_id,
            event_type=event_type,
            event_action=event_action,
            event_result=event_result,
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
            event_metadata=clean_metadata,
        )
        db.add(audit_entry)
        await db.flush()
        await db.refresh(audit_entry)

        logger.info(
            "Agent audit event recorded",
            extra={
                "audit_id": str(audit_entry.id),
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "event_type": event_type,
                "event_action": event_action,
                "event_result": event_result,
            },
        )

        return audit_entry

    async def list_agent_audit_events(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        cursor_occurred_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
        event_type: str | None = None,
    ) -> tuple[list[AgentAudit], bool]:
        """List tenant-scoped audit logs for an agent using keyset pagination.

        Raises:
            AgentNotFoundError: if agent is missing or belongs to another tenant.
        """
        # 1. IDOR Check
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        if agent_res.scalar_one_or_none() is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        limit = min(max(1, limit), _LIMIT_MAX)
        fetch_limit = limit + 1

        stmt = select(AgentAudit).where(
            AgentAudit.agent_id == agent_id,
            AgentAudit.tenant_id == tenant_id,
        )

        if event_type and event_type.strip():
            stmt = stmt.where(AgentAudit.event_type == event_type.strip())

        # Keyset pagination ordering: occurred_at DESC, id DESC
        if cursor_occurred_at is not None and cursor_id is not None:
            stmt = stmt.where(
                or_(
                    AgentAudit.occurred_at < cursor_occurred_at,
                    and_(
                        AgentAudit.occurred_at == cursor_occurred_at,
                        AgentAudit.id < cursor_id,
                    ),
                )
            )

        stmt = stmt.order_by(AgentAudit.occurred_at.desc(), AgentAudit.id.desc()).limit(fetch_limit)
        result = await db.execute(stmt)
        rows = list(result.scalars().all())

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        return rows, has_more
