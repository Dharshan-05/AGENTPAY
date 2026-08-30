"""Centralized Agent Lifecycle state machine application service for AGENTPAY (Phase 123–135).

State Machine:
    PROVISIONING ("provisioning")
         ↓ (Phase 124 Activation)
    ACTIVE ("active")
         ↓ (Phase 130 Pause / Phase 125 Suspension)
    PAUSED / SUSPENDED ("paused" / "suspended")
         ↓ (Phase 126 Revocation/Deactivation)
    DEACTIVATED ("deactivated") [TERMINAL STATE]

Transition Rules:
    - provisioning → active, suspended, deactivated
    - active       → paused, suspended, deactivated
    - paused       → active, suspended, deactivated
    - suspended    → active, deactivated
    - deactivated  → (terminal state — no outbound transitions allowed)

Security & Integrity Invariants:
    - All state transitions enforce tenant scope (`WHERE tenant_id = :tenant_id`)
    - Invalid state transitions fail closed with `InvalidAgentLifecycleTransitionError`
    - Cross-tenant requests return `AgentNotFoundError` (IDOR 404 anti-enumeration)
    - Agent status and lifecycle record are updated atomically in same transaction
    - Agent activation/resume requires an active credential to exist
    - Agent pause & suspension revoke active agent sessions
    - Agent revocation/deactivation revokes active sessions and invalidates active credentials
    - Generates integrated audit events and security events on state changes
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_audit_service import AgentAuditService
from app.application.services.agent_credential_service import AgentCredentialService
from app.application.services.agent_security_event_service import AgentSecurityEventService
from app.domain.exceptions.agent_exceptions import (
    AgentActivationError,
    AgentAlreadyActiveError,
    AgentAlreadyRevokedError,
    AgentAlreadySuspendedError,
    AgentNotFoundError,
    AgentStatusTransitionError,
    InvalidAgentLifecycleTransitionError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_credential import AgentCredential
from app.infrastructure.database.models.agent_lifecycle import AgentLifecycle
from app.infrastructure.database.models.agent_session import AgentSession

logger = logging.getLogger("agentpay.agent.lifecycle.service")

# ---------------------------------------------------------------------------
# State Machine Transition Definitions
# ---------------------------------------------------------------------------

VALID_LIFECYCLE_STATES: frozenset[str] = frozenset(
    {"provisioning", "active", "paused", "suspended", "deactivated"}
)

ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "provisioning": frozenset({"active", "suspended", "deactivated"}),
    "active": frozenset({"paused", "suspended", "deactivated"}),
    "paused": frozenset({"active", "suspended", "deactivated"}),
    "suspended": frozenset({"active", "deactivated"}),
    "deactivated": frozenset(),
}


def validate_transition(current_state: str, target_state: str) -> bool:
    """Validate whether transitioning from `current_state` to `target_state` is allowed.

    Returns:
        True if transition is legal under the state machine rules; False otherwise.
    """
    curr = current_state.strip().lower()
    targ = target_state.strip().lower()
    if curr not in VALID_LIFECYCLE_STATES or targ not in VALID_LIFECYCLE_STATES:
        return False
    allowed = ALLOWED_TRANSITIONS.get(curr, frozenset())
    return targ in allowed


class AgentLifecycleService:
    """Centralized domain application service for Agent Lifecycle transitions."""

    def __init__(
        self,
        credential_service: AgentCredentialService | None = None,
        audit_service: AgentAuditService | None = None,
        security_event_service: AgentSecurityEventService | None = None,
    ) -> None:
        self.credential_service = credential_service or AgentCredentialService()
        self.audit_service = audit_service or AgentAuditService()
        self.security_event_service = security_event_service or AgentSecurityEventService()

    async def get_agent_lifecycle(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> AgentLifecycle:
        """Retrieve operational lifecycle state for an agent within tenant scope.

        Raises:
            AgentNotFoundError: if agent or lifecycle is missing or belongs to another tenant.
        """
        stmt = select(AgentLifecycle).where(
            AgentLifecycle.agent_id == agent_id,
            AgentLifecycle.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        lifecycle = res.scalar_one_or_none()

        if lifecycle is None:
            # Check if agent exists in tenant
            agent_stmt = select(Agent).where(
                Agent.id == agent_id,
                Agent.tenant_id == tenant_id,
                Agent.deleted_at.is_(None),
            )
            agent_res = await db.execute(agent_stmt)
            if agent_res.scalar_one_or_none() is None:
                raise AgentNotFoundError(f"Agent {agent_id} not found.")

            # Create initial provisioning lifecycle record if missing
            lifecycle = AgentLifecycle(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                agent_id=agent_id,
                status="provisioning",
                status_reason="Initialized lifecycle record",
            )
            db.add(lifecycle)
            await db.flush()
            await db.refresh(lifecycle)

        return lifecycle

    async def activate_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        reason: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> tuple[Agent, AgentLifecycle]:
        """Execute production-grade agent activation (Phase 124)."""
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()

        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        lifecycle = await self.get_agent_lifecycle(db, tenant_id, agent_id)
        current_status = lifecycle.status.strip().lower()

        if current_status == "active" or agent.status.strip().lower() == "active":
            raise AgentAlreadyActiveError(f"Agent {agent_id} is already active.")

        if not validate_transition(current_status, "active"):
            raise InvalidAgentLifecycleTransitionError(
                f"Cannot transition agent from lifecycle status '{current_status}' to 'active'."
            )

        cred_stmt = select(AgentCredential).where(
            AgentCredential.agent_id == agent_id,
            AgentCredential.tenant_id == tenant_id,
            AgentCredential.status == "active",
        )
        cred_res = await db.execute(cred_stmt)
        active_cred = cred_res.scalar_one_or_none()

        if active_cred is None:
            raise AgentActivationError(
                "Agent cannot be activated without an active credential. "
                "Issue an agent credential before activation."
            )

        now = datetime.now(UTC)
        status_reason = reason or "Agent activation executed successfully"

        agent.status = "active"
        lifecycle.status = "active"
        lifecycle.status_reason = status_reason
        lifecycle.activated_at = now
        lifecycle.last_transition_at = now

        await db.flush()
        await db.refresh(agent)
        await db.refresh(lifecycle)

        # Audit & Security Events
        act_id = actor_id or agent_id
        await self.audit_service.record_audit_event(
            db,
            tenant_id,
            agent_id,
            act_id,
            event_type="agent_activated",
            event_action="activate_agent",
            event_result="success",
            event_metadata={"previous_status": current_status, "reason": status_reason},
        )
        await self.security_event_service.record_security_event(
            db,
            tenant_id,
            agent_id=agent_id,
            actor_id=act_id,
            event_type="security_control",
            event_action="security_control_triggered",
            severity="medium",
            event_payload={"previous_status": current_status, "new_status": "active"},
        )

        logger.info(
            "Agent activated successfully",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "previous_status": current_status,
                "new_status": "active",
            },
        )

        return agent, lifecycle

    async def suspend_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        reason: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> tuple[Agent, AgentLifecycle, int]:
        """Execute production-grade agent suspension (Phase 125)."""
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()

        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        lifecycle = await self.get_agent_lifecycle(db, tenant_id, agent_id)
        current_status = lifecycle.status.strip().lower()

        if current_status == "suspended" or agent.status.strip().lower() == "suspended":
            raise AgentAlreadySuspendedError(f"Agent {agent_id} is already suspended.")

        if not validate_transition(current_status, "suspended"):
            raise InvalidAgentLifecycleTransitionError(
                f"Cannot transition agent from status '{current_status}' to 'suspended'."
            )

        now = datetime.now(UTC)
        status_reason = reason or "Agent suspended by administrator"

        agent.status = "suspended"
        lifecycle.status = "suspended"
        lifecycle.status_reason = status_reason
        lifecycle.suspended_at = now
        lifecycle.last_transition_at = now

        session_revoke_stmt = (
            update(AgentSession)
            .where(
                AgentSession.agent_id == agent_id,
                AgentSession.tenant_id == tenant_id,
                AgentSession.status == "active",
            )
            .values(
                status="revoked",
                revoked_at=now,
                revocation_reason=f"Agent suspended: {status_reason}",
            )
        )
        session_res = await db.execute(session_revoke_stmt)
        revoked_sessions_count = session_res.rowcount or 0

        await db.flush()
        await db.refresh(agent)
        await db.refresh(lifecycle)

        # Audit & Security Events
        act_id = actor_id or agent_id
        await self.audit_service.record_audit_event(
            db,
            tenant_id,
            agent_id,
            act_id,
            event_type="agent_suspended",
            event_action="suspend_agent",
            event_result="success",
            event_metadata={
                "previous_status": current_status,
                "revoked_sessions_count": revoked_sessions_count,
                "reason": status_reason,
            },
        )
        await self.security_event_service.record_security_event(
            db,
            tenant_id,
            agent_id=agent_id,
            actor_id=act_id,
            event_type="security_control",
            event_action="security_control_triggered",
            event_result="success",
            severity="high",
            event_payload={
                "previous_status": current_status,
                "new_status": "suspended",
                "revoked_sessions_count": revoked_sessions_count,
            },
        )

        logger.info(
            "Agent suspended successfully",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "previous_status": current_status,
                "new_status": "suspended",
                "revoked_sessions_count": revoked_sessions_count,
            },
        )

        return agent, lifecycle, revoked_sessions_count

    async def revoke_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        reason: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> tuple[Agent, AgentLifecycle, int, int]:
        """Execute production-grade agent revocation/deactivation (Phase 126)."""
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()

        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        lifecycle = await self.get_agent_lifecycle(db, tenant_id, agent_id)
        current_status = lifecycle.status.strip().lower()

        if current_status == "deactivated" or agent.status.strip().lower() == "deactivated":
            raise AgentAlreadyRevokedError(f"Agent {agent_id} is already deactivated/revoked.")

        if not validate_transition(current_status, "deactivated"):
            raise InvalidAgentLifecycleTransitionError(
                f"Cannot transition agent from status '{current_status}' to 'deactivated'."
            )

        now = datetime.now(UTC)
        status_reason = reason or "Agent permanently revoked/deactivated"

        agent.status = "deactivated"
        lifecycle.status = "deactivated"
        lifecycle.status_reason = status_reason
        lifecycle.deactivated_at = now
        lifecycle.last_transition_at = now

        session_revoke_stmt = (
            update(AgentSession)
            .where(
                AgentSession.agent_id == agent_id,
                AgentSession.tenant_id == tenant_id,
                AgentSession.status == "active",
            )
            .values(
                status="revoked",
                revoked_at=now,
                revocation_reason=f"Agent deactivated: {status_reason}",
            )
        )
        session_res = await db.execute(session_revoke_stmt)
        revoked_sessions_count = session_res.rowcount or 0

        cred_revoke_stmt = (
            update(AgentCredential)
            .where(
                AgentCredential.agent_id == agent_id,
                AgentCredential.tenant_id == tenant_id,
                AgentCredential.status == "active",
            )
            .values(
                status="revoked",
                revoked_at=now,
            )
        )
        cred_res = await db.execute(cred_revoke_stmt)
        revoked_credentials_count = cred_res.rowcount or 0

        await db.flush()
        await db.refresh(agent)
        await db.refresh(lifecycle)

        # Audit & Security Events
        act_id = actor_id or agent_id
        await self.audit_service.record_audit_event(
            db,
            tenant_id,
            agent_id,
            act_id,
            event_type="agent_revoked",
            event_action="revoke_agent",
            event_result="success",
            event_metadata={
                "previous_status": current_status,
                "revoked_sessions_count": revoked_sessions_count,
                "revoked_credentials_count": revoked_credentials_count,
                "reason": status_reason,
            },
        )
        await self.security_event_service.record_security_event(
            db,
            tenant_id,
            agent_id=agent_id,
            actor_id=act_id,
            event_type="security_control",
            event_action="security_control_triggered",
            event_result="success",
            severity="critical",
            event_payload={
                "previous_status": current_status,
                "new_status": "deactivated",
                "revoked_sessions_count": revoked_sessions_count,
                "revoked_credentials_count": revoked_credentials_count,
            },
        )

        logger.info(
            "Agent revoked/deactivated successfully",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "previous_status": current_status,
                "new_status": "deactivated",
                "revoked_sessions_count": revoked_sessions_count,
                "revoked_credentials_count": revoked_credentials_count,
            },
        )

        return agent, lifecycle, revoked_sessions_count, revoked_credentials_count

    # ------------------------------------------------------------------
    # Phase 130 — Agent Status Management
    # ------------------------------------------------------------------

    async def pause_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        reason: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> tuple[Agent, AgentLifecycle, int]:
        """Pause an active agent temporarily (Phase 130)."""
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()

        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        lifecycle = await self.get_agent_lifecycle(db, tenant_id, agent_id)
        current_status = lifecycle.status.strip().lower()

        if current_status == "paused" or agent.status.strip().lower() == "paused":
            raise AgentStatusTransitionError(f"Agent {agent_id} is already paused.")

        if not validate_transition(current_status, "paused"):
            raise InvalidAgentLifecycleTransitionError(
                f"Cannot transition agent from status '{current_status}' to 'paused'."
            )

        now = datetime.now(UTC)
        status_reason = reason or "Agent operational pause requested"

        agent.status = "paused"
        lifecycle.status = "paused"
        lifecycle.status_reason = status_reason
        lifecycle.last_transition_at = now

        session_revoke_stmt = (
            update(AgentSession)
            .where(
                AgentSession.agent_id == agent_id,
                AgentSession.tenant_id == tenant_id,
                AgentSession.status == "active",
            )
            .values(
                status="revoked",
                revoked_at=now,
                revocation_reason=f"Agent paused: {status_reason}",
            )
        )
        session_res = await db.execute(session_revoke_stmt)
        revoked_sessions_count = session_res.rowcount or 0

        await db.flush()
        await db.refresh(agent)
        await db.refresh(lifecycle)

        # Audit & Security Events
        act_id = actor_id or agent_id
        await self.audit_service.record_audit_event(
            db,
            tenant_id,
            agent_id,
            act_id,
            event_type="status_changed",
            event_action="pause_agent",
            event_result="success",
            event_metadata={
                "previous_status": current_status,
                "new_status": "paused",
                "revoked_sessions_count": revoked_sessions_count,
            },
        )
        await self.security_event_service.record_security_event(
            db,
            tenant_id,
            agent_id=agent_id,
            actor_id=act_id,
            event_type="security_control",
            event_action="security_control_triggered",
            event_result="success",
            severity="medium",
            event_payload={
                "previous_status": current_status,
                "new_status": "paused",
                "revoked_sessions_count": revoked_sessions_count,
            },
        )

        logger.info(
            "Agent paused successfully",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "previous_status": current_status,
                "new_status": "paused",
                "revoked_sessions_count": revoked_sessions_count,
            },
        )

        return agent, lifecycle, revoked_sessions_count

    async def resume_agent(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        *,
        reason: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> tuple[Agent, AgentLifecycle]:
        """Resume a paused agent back to active status (Phase 130)."""
        agent_stmt = select(Agent).where(
            Agent.id == agent_id,
            Agent.tenant_id == tenant_id,
            Agent.deleted_at.is_(None),
        )
        agent_res = await db.execute(agent_stmt)
        agent = agent_res.scalar_one_or_none()

        if agent is None:
            raise AgentNotFoundError(f"Agent {agent_id} not found.")

        lifecycle = await self.get_agent_lifecycle(db, tenant_id, agent_id)
        current_status = lifecycle.status.strip().lower()

        if current_status == "active" or agent.status.strip().lower() == "active":
            raise AgentAlreadyActiveError(f"Agent {agent_id} is already active.")

        if not validate_transition(current_status, "active"):
            raise InvalidAgentLifecycleTransitionError(
                f"Cannot transition agent from status '{current_status}' to 'active'."
            )

        cred_stmt = select(AgentCredential).where(
            AgentCredential.agent_id == agent_id,
            AgentCredential.tenant_id == tenant_id,
            AgentCredential.status == "active",
        )
        cred_res = await db.execute(cred_stmt)
        if cred_res.scalar_one_or_none() is None:
            raise AgentActivationError("Agent cannot be resumed without an active credential.")

        now = datetime.now(UTC)
        status_reason = reason or "Agent resumed to active operational state"

        agent.status = "active"
        lifecycle.status = "active"
        lifecycle.status_reason = status_reason
        if lifecycle.activated_at is None:
            lifecycle.activated_at = now
        lifecycle.last_transition_at = now

        await db.flush()
        await db.refresh(agent)
        await db.refresh(lifecycle)

        # Audit & Security Events
        act_id = actor_id or agent_id
        await self.audit_service.record_audit_event(
            db,
            tenant_id,
            agent_id,
            act_id,
            event_type="status_changed",
            event_action="resume_agent",
            event_result="success",
            event_metadata={"previous_status": current_status, "new_status": "active"},
        )
        await self.security_event_service.record_security_event(
            db,
            tenant_id,
            agent_id=agent_id,
            actor_id=act_id,
            event_type="security_control",
            event_action="security_control_triggered",
            event_result="success",
            severity="medium",
            event_payload={"previous_status": current_status, "new_status": "active"},
        )

        logger.info(
            "Agent resumed successfully",
            extra={
                "agent_id": str(agent_id),
                "tenant_id": str(tenant_id),
                "previous_status": current_status,
                "new_status": "active",
            },
        )

        return agent, lifecycle

    async def update_agent_status(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        target_status: str,
        *,
        reason: str | None = None,
        actor_id: uuid.UUID | None = None,
    ) -> tuple[Agent, AgentLifecycle, int]:
        """Controlled status transition dispatcher delegating strictly to lifecycle state
        machine.
        """
        st = target_status.strip().lower()
        if st not in VALID_LIFECYCLE_STATES:
            raise AgentStatusTransitionError(f"Unknown target status '{target_status}'.")

        if st == "active":
            agent, lc = await self.resume_agent(
                db, tenant_id, agent_id, reason=reason, actor_id=actor_id
            )
            return agent, lc, 0
        elif st == "paused":
            return await self.pause_agent(db, tenant_id, agent_id, reason=reason, actor_id=actor_id)
        elif st == "suspended":
            return await self.suspend_agent(
                db, tenant_id, agent_id, reason=reason, actor_id=actor_id
            )
        elif st == "deactivated":
            agent, lc, rev_sess, _ = await self.revoke_agent(
                db, tenant_id, agent_id, reason=reason, actor_id=actor_id
            )
            return agent, lc, rev_sess
        else:
            raise AgentStatusTransitionError(f"Transition to status '{st}' is not supported.")
