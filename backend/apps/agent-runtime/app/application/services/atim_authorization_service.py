"""ATIM Centralized RBAC Authorization & Tenant Isolation Boundary Service (Phase 19 / Group 10)."""

import logging
from typing import Optional
import uuid

from app.domain.governance.compliance_models import ATIMSecurityContext, SecurityPermission

logger = logging.getLogger("agentpay.atim.authorization")


class ATIMAuthorizationService:
    """Service enforcing centralized RBAC permissions, tenant boundaries, and agent isolation."""

    def authorize_permission(
        self,
        security_ctx: ATIMSecurityContext,
        required_permission: SecurityPermission,
    ) -> None:
        """Verify principal possesses required fine-grained SecurityPermission."""
        if required_permission not in security_ctx.permissions and SecurityPermission.ATIM_SYSTEM_ADMIN not in security_ctx.permissions:
            logger.warning(
                "RBAC DENIAL: User %s (Tenant %s) lacks required permission '%s'",
                security_ctx.user_id,
                security_ctx.tenant_id,
                required_permission.value,
            )
            raise PermissionError(f"Access Denied: Missing required permission '{required_permission.value}'.")

    def verify_tenant_boundary(
        self,
        security_ctx: ATIMSecurityContext,
        target_tenant_id: uuid.UUID,
    ) -> None:
        """Verify principal tenant identity matches requested resource tenant identity."""
        if security_ctx.tenant_id != target_tenant_id:
            logger.warning(
                "CROSS-TENANT VIOLATION ATTEMPT: Authenticated Tenant %s attempted access to Target Tenant %s (User %s)",
                security_ctx.tenant_id,
                target_tenant_id,
                security_ctx.user_id,
            )
            raise PermissionError("Cross-tenant operation is forbidden.")

    def verify_four_eyes_approval(
        self,
        creator_id: uuid.UUID,
        approver_id: uuid.UUID,
    ) -> None:
        """Enforce Four-Eyes Principle (creator_id != approver_id)."""
        if creator_id == approver_id:
            logger.warning("FOUR-EYES VIOLATION ATTEMPT: User %s attempted self-approval", creator_id)
            raise PermissionError("Four-Eyes Violation: Policy creator cannot approve their own submission.")
