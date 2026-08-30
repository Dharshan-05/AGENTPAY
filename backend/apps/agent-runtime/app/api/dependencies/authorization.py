"""AGENTPAY Authorization Middleware Dependencies (Phase 114).

Provides reusable FastAPI authorization dependencies.

Usage in endpoints:

    @router.get("/payments")
    async def list_payments(
        _: None = Depends(require_permission("payments:read")),
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> ...:

Authorization semantics:
    - 401: Unauthenticated (handled by get_current_user)
    - 403: Authenticated but lacks required permission
    - Default-deny: missing permission → 403 (never 200)
    - Tenant context always enforced from authenticated session
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.application.services.authorization import AuthorizationService
from app.domain.authorization.context import AuthorizationContext
from app.infrastructure.database.session import get_db_session

_authorization_service = AuthorizationService()


def get_authorization_service() -> AuthorizationService:
    """Dependency provider for AuthorizationService."""
    return _authorization_service


def require_permission(permission: str) -> Callable[..., Any]:
    """Factory that returns a FastAPI dependency enforcing the given permission.

    Fail-closed: raises PermissionDeniedError (→ HTTP 403) if:
    - The principal has no roles
    - The principal's roles do not include the permission
    - The permission string is empty or invalid

    Authentication (identity + session validity) is always enforced first
    via get_current_user. Authorization is a separate, subsequent check.

    Args:
        permission: Canonical permission name (e.g., "payments:read").

    Returns:
        A FastAPI dependency callable.
    """

    async def _check(
        current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db_session)],
        authz_service: Annotated[AuthorizationService, Depends(get_authorization_service)],
    ) -> AuthenticatedUser:
        """Check that current_user holds the required permission."""
        context = AuthorizationContext(
            user_id=current_user.user.id,
            tenant_id=current_user.tenant_id,
            session_id=current_user.session.id,
        )
        await authz_service.require_permission(db, context, permission)
        return current_user

    return _check
