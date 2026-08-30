"""Agent Permission Evaluation Application Service for AGENTPAY (Phase 184)."""

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
from app.schemas.agent_permission_evaluation import PermissionEvaluationResult

logger = logging.getLogger("agentguard.security.permission_evaluation")


class AgentPermissionEvaluationService:
    """Production permission evaluation service resolving effective agent permissions (Phase 184)."""  # noqa: E501

    def __init__(
        self,
        identity_service: AgentIdentityVerificationService | None = None,
        authz_service: AuthorizationService | None = None,
    ) -> None:
        self.identity_service = identity_service or AgentIdentityVerificationService()
        self.authz_service = authz_service or AuthorizationService()

    async def evaluate_agent_permissions(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
        requested_permissions: list[str],
        principal_id: uuid.UUID | None = None,
    ) -> PermissionEvaluationResult:
        """Deterministically evaluate effective permissions for an agent (Phase 184)."""
        now = datetime.now(UTC)

        # 1. Identity Verification Step
        id_res = await self.identity_service.verify_agent_identity(
            db, tenant_id=tenant_id, agent_id=agent_id, principal_id=principal_id
        )
        if not id_res.verified:
            logger.info(
                "Permission evaluation DENIED for agent %s: identity not verified", agent_id
            )  # noqa: E501
            return PermissionEvaluationResult(
                agent_id=agent_id,
                tenant_id=tenant_id,
                principal_id=principal_id,
                requested_permissions=requested_permissions,
                granted_permissions=[],
                missing_permissions=requested_permissions,
                decision="DENIED",
                reason_code="IDENTITY_NOT_VERIFIED",
                evaluated_at=now,
            )

        # 2. Resolve Agent Effective Permissions via AuthorizationService
        agent_perms = await self.authz_service.resolve_agent_permissions(
            db, tenant_id=tenant_id, agent_id=agent_id
        )

        combined_perms = set(agent_perms)

        # 3. Include principal permissions if principal provided
        if principal_id is not None:
            ctx = AuthorizationContext(
                user_id=principal_id, tenant_id=tenant_id, session_id=uuid.uuid4()
            )
            user_perms = await self.authz_service.resolve_permissions(db, ctx)
            combined_perms |= set(user_perms)

        # 4. Evaluate requested permissions
        granted = [p for p in requested_permissions if p in combined_perms]
        missing = [p for p in requested_permissions if p not in combined_perms]

        if not missing:
            logger.info("Permission evaluation GRANTED for agent %s", agent_id)
            return PermissionEvaluationResult(
                agent_id=agent_id,
                tenant_id=tenant_id,
                principal_id=principal_id,
                requested_permissions=requested_permissions,
                granted_permissions=granted,
                missing_permissions=[],
                decision="GRANTED",
                reason_code="PERMISSION_GRANTED",
                evaluated_at=now,
            )
        else:
            logger.info(
                "Permission evaluation DENIED for agent %s (%s missing)", agent_id, len(missing)
            )  # noqa: E501
            return PermissionEvaluationResult(
                agent_id=agent_id,
                tenant_id=tenant_id,
                principal_id=principal_id,
                requested_permissions=requested_permissions,
                granted_permissions=granted,
                missing_permissions=missing,
                decision="DENIED",
                reason_code="PERMISSION_MISSING",
                evaluated_at=now,
            )

    async def get_effective_agent_permissions(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID,
    ) -> list[str]:
        """Resolve complete list of effective permission names for an agent (Phase 184)."""
        id_res = await self.identity_service.verify_agent_identity(
            db, tenant_id=tenant_id, agent_id=agent_id
        )
        if not id_res.verified:
            return []

        agent_perms = await self.authz_service.resolve_agent_permissions(
            db, tenant_id=tenant_id, agent_id=agent_id
        )
        return sorted(list(agent_perms))
