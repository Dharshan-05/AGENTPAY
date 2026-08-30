"""Agent Authorization Application Service for AGENTPAY (Phase 183)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_identity_verification_service import (
    AgentIdentityVerificationService,
)
from app.application.services.authorization import AuthorizationService
from app.domain.authorization.context import AuthorizationContext
from app.domain.exceptions.auth_exceptions import PermissionDeniedError
from app.schemas.agent_authorization import AgentAuthorizationResponse

logger = logging.getLogger("agentguard.security.authorization")


class AgentAuthorizationService:
    """Production authorization service for AI agent actions reusing AuthorizationService (Phase 183)."""  # noqa: E501

    def __init__(
        self,
        identity_service: AgentIdentityVerificationService | None = None,
        authz_service: AuthorizationService | None = None,
    ) -> None:
        self.identity_service = identity_service or AgentIdentityVerificationService()
        self.authz_service = authz_service or AuthorizationService()

    async def authorize_agent_action(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        principal_id: uuid.UUID,
        action: str,
        required_permissions: list[str] | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
    ) -> AgentAuthorizationResponse:
        """Determine whether principal is authorized to perform action on behalf of verified agent (Phase 183)."""  # noqa: E501
        now = datetime.now(UTC)
        req_perms = required_permissions or [action]

        # 1. Identity Verification Step
        id_res = await self.identity_service.verify_agent_identity(
            db, tenant_id=tenant_id, agent_id=agent_id, principal_id=principal_id
        )
        if not id_res.verified:
            logger.info("Agent authorization DENIED for %s: identity not verified", agent_id)
            return AgentAuthorizationResponse(
                allowed=False,
                agent_id=agent_id,
                tenant_id=tenant_id,
                principal_id=principal_id,
                action=action,
                decision_reason=f"Identity verification failed: {id_res.verification_reason}",
                evaluated_at=now,
            )

        # 2. Resolve Agent Effective Permissions via AuthorizationService
        agent_perms = await self.authz_service.resolve_agent_permissions(
            db, tenant_id=tenant_id, agent_id=agent_id
        )

        # 3. Resolve Principal User Permissions via AuthorizationService
        ctx = AuthorizationContext(
            user_id=principal_id, tenant_id=tenant_id, session_id=uuid.uuid4()
        )
        user_perms = await self.authz_service.resolve_permissions(db, ctx)

        combined_perms = agent_perms | user_perms

        # 4. Evaluate Required Permissions (Fail-Closed)
        missing_perms = [p for p in req_perms if p not in combined_perms]
        if missing_perms:
            reason = f"Required permissions missing: {', '.join(missing_perms)}"
            logger.info("Agent authorization DENIED for %s: %s", agent_id, reason)
            return AgentAuthorizationResponse(
                allowed=False,
                agent_id=agent_id,
                tenant_id=tenant_id,
                principal_id=principal_id,
                action=action,
                decision_reason=reason,
                evaluated_at=now,
            )

        logger.info("Agent authorization ALLOWED for agent %s action '%s'", agent_id, action)
        return AgentAuthorizationResponse(
            allowed=True,
            agent_id=agent_id,
            tenant_id=tenant_id,
            principal_id=principal_id,
            action=action,
            decision_reason="Action authorized successfully.",
            evaluated_at=now,
        )

    async def require_agent_permission(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        principal_id: uuid.UUID,
        permission_name: str,
    ) -> None:
        """Enforce agent permission, raising PermissionDeniedError if not authorized (Phase 183)."""  # noqa: E501
        res = await self.authorize_agent_action(
            db,
            tenant_id=tenant_id,
            agent_id=agent_id,
            principal_id=principal_id,
            action=permission_name,
            required_permissions=[permission_name],
        )
        if not res.allowed:
            raise PermissionDeniedError(res.decision_reason)
