"""Agent State Management application service for AGENTPAY (Phase 150).

Responsibilities:
    - Canonical agent runtime state abstraction: IDLE, PREPARING, READY, BLOCKED, WAITING
    - Explicit state transition graph enforcement
    - Integration with authoritative agent lifecycle status (active, paused, suspended, deactivated)
    - Rejection of prohibited states (NO EXECUTING, TOOL_EXECUTING, or PAYMENT_EXECUTING)
    - Audit logging of runtime state changes
    - Tenant-isolated state updates and IDOR defense
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_lifecycle_service import AgentLifecycleService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
    InvalidAgentStateTransitionError,
)
from app.infrastructure.database.models.agent import Agent
from app.schemas.state import AgentStateResponse

logger = logging.getLogger("agentpay.agent.state.service")

# Canonical Runtime States (Phase 150)
VALID_RUNTIME_STATES: frozenset[str] = frozenset(
    {"IDLE", "PREPARING", "READY", "BLOCKED", "WAITING", "FAILED", "CANCELLED"}
)

# Explicit State Transition Graph (Phase 150)
ALLOWED_STATE_TRANSITIONS: dict[str, set[str]] = {
    "IDLE": {"PREPARING"},
    "PREPARING": {"READY", "BLOCKED", "FAILED"},
    "READY": {"WAITING", "CANCELLED"},
    "WAITING": {"READY", "BLOCKED"},
    "BLOCKED": {"READY"},
    "FAILED": {"IDLE"},
    "CANCELLED": {"IDLE"},
}


class AgentStateService:
    """Application service for managing Agent runtime states (Phase 150)."""

    def __init__(
        self,
        lifecycle_service: AgentLifecycleService | None = None,
        audit_service: AgentAuditService | None = None,
    ) -> None:
        self.lifecycle_service = lifecycle_service or AgentLifecycleService()
        self.audit_service = audit_service or AgentAuditService()

    async def get_agent_state(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> AgentStateResponse:
        """Retrieve current runtime state for an agent within verified tenant scope.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
        """
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # Extract runtime state from agent metadata or default to IDLE
        meta: dict[str, Any] = getattr(agent, "agent_metadata", None) or {}
        if not isinstance(meta, dict):
            meta = {}
        runtime_meta = meta.get("runtime_state", {})

        current_state = str(runtime_meta.get("current_state", "IDLE"))
        previous_state = runtime_meta.get("previous_state")
        reason = runtime_meta.get("reason")
        updated_at_str = runtime_meta.get("updated_at")

        updated_at = (
            datetime.fromisoformat(updated_at_str)
            if updated_at_str
            else (agent.updated_at or agent.created_at or datetime.now(UTC))
        )

        return AgentStateResponse(
            agent_id=agent.id,
            tenant_id=agent.tenant_id,
            current_state=current_state,
            previous_state=previous_state,
            lifecycle_status=agent.status,
            reason=reason,
            updated_at=updated_at,
        )

    async def update_agent_state(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        user_id: uuid.UUID,
        requested_transition: str,
        reason: str | None = None,
    ) -> AgentStateResponse:
        """Transition agent runtime state following explicit transition rules.

        Raises:
            AgentNotFoundError: if agent is missing or cross-tenant.
            InvalidAgentStateTransitionError: if transition is invalid or forbidden by lifecycle.
        """
        target_state = requested_transition.upper()

        if target_state not in VALID_RUNTIME_STATES:
            raise InvalidAgentStateTransitionError(
                f"Requested state '{requested_transition}' is not a valid runtime state."
            )

        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()
        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        # 1. Lifecycle Status Protection Rules
        if agent.status in ("deactivated", "revoked"):
            raise InvalidAgentStateTransitionError(
                f"Agent is '{agent.status}' and runtime state cannot be updated."
            )

        if agent.status == "suspended" and target_state != "BLOCKED":
            raise InvalidAgentStateTransitionError(
                "Suspended agent runtime state must remain 'BLOCKED'."
            )

        if agent.status == "provisioning" and target_state == "READY":
            raise InvalidAgentStateTransitionError(
                "Provisioning agent runtime state cannot become 'READY'."
            )

        # 2. Extract Current State & Validate Transition Matrix
        meta: dict[str, Any] = getattr(agent, "agent_metadata", None) or {}
        runtime_meta = meta.get("runtime_state", {})
        current_state = str(runtime_meta.get("current_state", "IDLE"))

        if target_state != current_state:
            allowed_next = ALLOWED_STATE_TRANSITIONS.get(current_state, set())
            if target_state not in allowed_next:
                raise InvalidAgentStateTransitionError(
                    f"Transition from '{current_state}' to '{target_state}' is not permitted."
                )

        # 3. Apply Transition
        now = datetime.now(UTC)
        new_runtime_meta = {
            "current_state": target_state,
            "previous_state": current_state,
            "reason": reason,
            "updated_at": now.isoformat(),
        }
        meta["runtime_state"] = new_runtime_meta
        agent.agent_metadata = meta  # type: ignore[attr-defined]

        # 4. Audit Event Registration
        await self.audit_service.record_audit_event(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            actor_id=user_id,
            event_type="agent_state_updated",
            event_action="update_agent_state",
            event_result="success",
            event_metadata={
                "previous_state": current_state,
                "current_state": target_state,
                "reason": reason,
            },
        )

        await db.commit()
        await db.refresh(agent)

        logger.info(
            "Agent runtime state updated successfully",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "previous_state": current_state,
                "current_state": target_state,
            },
        )

        return AgentStateResponse(
            agent_id=agent.id,
            tenant_id=agent.tenant_id,
            current_state=target_state,
            previous_state=current_state,
            lifecycle_status=agent.status,
            reason=reason,
            updated_at=now,
        )
