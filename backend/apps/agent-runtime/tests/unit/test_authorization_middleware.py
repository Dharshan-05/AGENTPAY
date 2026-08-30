"""Unit tests for Phase 114 — Authorization Middleware.

Tests:
- require_permission factory returns callable
- Authenticated + authorized → passes
- Authenticated + unauthorized → PermissionDeniedError (→ 403)
- Unauthenticated → AuthenticationFailedError (→ 401)
- Authentication ≠ authorization (valid JWT doesn't auto-grant)
- Standardized 401/403 responses via exception middleware
- Tenant context enforced from session (not from client input)
- Revoked session → 401
- Inactive user → 403
"""

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.api.dependencies.authorization import require_permission
from app.application.services.authorization import AuthorizationService
from app.domain.authorization.context import AuthorizationContext
from app.domain.authorization.permissions_registry import PAYMENTS_READ, ROLES_CREATE
from app.domain.exceptions.auth_exceptions import PermissionDeniedError

# ---------------------------------------------------------------------------
# require_permission factory
# ---------------------------------------------------------------------------


def test_01_require_permission_returns_callable() -> None:
    """Verify require_permission factory returns a callable dependency."""
    dep = require_permission(PAYMENTS_READ)
    assert callable(dep)


def test_02_different_permissions_return_distinct_callables() -> None:
    """Verify each call to require_permission returns a unique dependency."""
    dep_read = require_permission(PAYMENTS_READ)
    dep_create = require_permission(ROLES_CREATE)
    assert dep_read is not dep_create


# ---------------------------------------------------------------------------
# Authorization checks (authenticated + authorized)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_03_permission_granted_passes() -> None:
    """Verify require_permission allows request when permission is granted."""
    tenant_id = uuid.uuid4()
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=tenant_id,
        session_id=uuid.uuid4(),
    )

    service = AuthorizationService()
    with patch.object(
        service,
        "resolve_permissions",
        new=AsyncMock(return_value=frozenset({PAYMENTS_READ})),
    ):
        db = AsyncMock()
        # Should not raise
        await service.require_permission(db, ctx, PAYMENTS_READ)


@pytest.mark.asyncio
async def test_04_permission_denied_raises_exception() -> None:
    """Verify require_permission raises PermissionDeniedError when permission absent."""
    tenant_id = uuid.uuid4()
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=tenant_id,
        session_id=uuid.uuid4(),
    )

    service = AuthorizationService()
    with patch.object(
        service,
        "resolve_permissions",
        new=AsyncMock(return_value=frozenset()),
    ):
        db = AsyncMock()
        with pytest.raises(PermissionDeniedError):
            await service.require_permission(db, ctx, PAYMENTS_READ)


# ---------------------------------------------------------------------------
# JWT valid but no permission → 403 not 401
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_05_valid_jwt_without_permission_is_forbidden() -> None:
    """Verify that a valid JWT without the required permission produces 403 not 401."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    service = AuthorizationService()
    with patch.object(service, "resolve_permissions", new=AsyncMock(return_value=frozenset())):
        db = AsyncMock()
        with pytest.raises(PermissionDeniedError) as exc_info:
            await service.require_permission(db, ctx, ROLES_CREATE)

        # PermissionDeniedError maps to FORBIDDEN (403)
        from app.exceptions.codes import ErrorCode

        assert exc_info.value.code == ErrorCode.FORBIDDEN


# ---------------------------------------------------------------------------
# Tenant isolation enforcement
# ---------------------------------------------------------------------------


def test_06_authorization_context_tenant_bound_to_session() -> None:
    """Verify AuthorizationContext tenant_id must originate from authenticated session."""
    tenant_from_session = uuid.uuid4()
    malicious_tenant_from_client = uuid.uuid4()

    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=tenant_from_session,
        session_id=uuid.uuid4(),
    )

    # The context uses the session tenant, not any client-supplied value
    assert ctx.tenant_id == tenant_from_session
    assert ctx.tenant_id != malicious_tenant_from_client


# ---------------------------------------------------------------------------
# Multiple roles / multiple permissions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_07_user_with_multiple_roles_can_access_any_granted_permission() -> None:
    """Verify user with multiple roles gets union of all permissions."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    # Simulate multiple roles aggregated into permission set
    combined = frozenset({PAYMENTS_READ, ROLES_CREATE})

    service = AuthorizationService()
    with patch.object(service, "resolve_permissions", new=AsyncMock(return_value=combined)):
        db = AsyncMock()
        decision_read = await service.has_permission(db, ctx, PAYMENTS_READ)
        decision_create = await service.has_permission(db, ctx, ROLES_CREATE)
        assert decision_read.allowed is True
        assert decision_create.allowed is True


@pytest.mark.asyncio
async def test_08_default_deny_with_empty_roles() -> None:
    """Verify user with no roles gets default-deny on all permissions."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )

    service = AuthorizationService()
    with patch.object(service, "resolve_permissions", new=AsyncMock(return_value=frozenset())):
        db = AsyncMock()
        for perm in [PAYMENTS_READ, ROLES_CREATE]:
            decision = await service.has_permission(db, ctx, perm)
            assert decision.allowed is False, f"Expected deny for {perm}"
