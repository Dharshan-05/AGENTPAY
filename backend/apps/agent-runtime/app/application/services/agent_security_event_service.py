"""Agent Security Events application service for AGENTPAY (Phase 133).

Responsibilities:
    - Transactional creation of append-only `SecurityEvent` log records
    - Integration with agent credentials, sessions, suspension, revocation, and roles/permissions
    - Keyset-paginated security event retrieval within tenant scope (`occurred_at DESC, id DESC`)
    - Payload sanitization (zero raw secrets, password hashes, or bearer tokens)
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
from app.infrastructure.database.models.security_event import SecurityEvent

logger = logging.getLogger("agentpay.agent.security_event.service")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100

SENSITIVE_SECURITY_KEYS: frozenset[str] = frozenset(
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
        "bearer",
    }
)


def _sanitize_payload(data: dict[str, Any] | None) -> dict[str, Any]:
    """Recursively strip sensitive keys from security event payload dict."""
    if not data:
        return {}
    clean: dict[str, Any] = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_SECURITY_KEYS:
            clean[k] = "[REDACTED]"
        elif isinstance(v, dict):
            clean[k] = _sanitize_payload(v)
        else:
            clean[k] = v
    return clean


class AgentSecurityEventService:
    """Application service for managing Agent security events (Phase 133)."""

    async def record_security_event(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        *,
        agent_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        actor_type: str = "user",
        event_type: str = "credential",
        event_action: str = "credential_used",
        event_result: str = "success",
        severity: str = "medium",
        source: str = "agent",
        request_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        event_payload: dict[str, Any] | None = None,
    ) -> SecurityEvent:
        """Create and persist an append-only `SecurityEvent` record."""
        clean_payload = _sanitize_payload(event_payload)
        ref_id = f"sec-{uuid.uuid4().hex[:12]}"

        sec_event = SecurityEvent(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            user_id=user_id,
            actor_id=actor_id,
            actor_type=actor_type,
            event_reference=ref_id,
            event_type=event_type,
            event_action=event_action,
            event_result=event_result,
            severity=severity,
            source=source,
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
            event_payload=clean_payload,
        )
        db.add(sec_event)
        await db.flush()
        await db.refresh(sec_event)

        logger.info(
            "Agent security event recorded",
            extra={
                "security_event_id": str(sec_event.id),
                "agent_id": str(agent_id) if agent_id else None,
                "tenant_id": str(tenant_id),
                "event_type": event_type,
                "event_action": event_action,
                "severity": severity,
                "event_result": event_result,
            },
        )

        return sec_event

    async def list_agent_security_events(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        cursor_occurred_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
        severity: str | None = None,
        event_type: str | None = None,
    ) -> tuple[list[SecurityEvent], bool]:
        """List tenant-scoped security events for an agent using keyset pagination.

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

        stmt = select(SecurityEvent).where(
            SecurityEvent.agent_id == agent_id,
            SecurityEvent.tenant_id == tenant_id,
        )

        if severity and severity.strip():
            stmt = stmt.where(SecurityEvent.severity == severity.strip().lower())

        if event_type and event_type.strip():
            stmt = stmt.where(SecurityEvent.event_type == event_type.strip().lower())

        # Keyset pagination ordering: occurred_at DESC, id DESC
        if cursor_occurred_at is not None and cursor_id is not None:
            stmt = stmt.where(
                or_(
                    SecurityEvent.occurred_at < cursor_occurred_at,
                    and_(
                        SecurityEvent.occurred_at == cursor_occurred_at,
                        SecurityEvent.id < cursor_id,
                    ),
                )
            )

        stmt = stmt.order_by(SecurityEvent.occurred_at.desc(), SecurityEvent.id.desc()).limit(
            fetch_limit
        )
        result = await db.execute(stmt)
        rows = list(result.scalars().all())

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        return rows, has_more
