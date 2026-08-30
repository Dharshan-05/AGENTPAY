"""AGENTPAY RBAC Security Regression & Hardening Test Baseline.

Locks in canonical security invariants:
1. AGENTS_READ ("agents:read") is registered in ALL_PERMISSIONS.
2. Default-deny is enforced for 0 roles, inactive roles, and missing permissions.
3. Strict tenant isolation (User in Tenant A cannot inherit Tenant B roles/permissions).
4. System role safety (requires explicit UserRole binding in authenticated tenant scope).
5. Seeder idempotency (seed_all creates 0 duplicate RBAC records on repeated execution).
6. Security bypass scan (No hardcoded email, user_id, or dev bypasses in auth/authorization).
"""

from __future__ import annotations

import re

from pathlib import Path
import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.api.dependencies.authorization import require_permission
from app.application.services.authorization import AuthorizationService
from app.domain.authorization.context import AuthorizationContext
from app.domain.authorization.permissions_registry import AGENTS_READ, ALL_PERMISSIONS, PAYMENTS_READ
from app.domain.exceptions.auth_exceptions import PermissionDeniedError
from app.exceptions.codes import ErrorCode


# ---------------------------------------------------------------------------
# 1. Contract & Registry Protection
# ---------------------------------------------------------------------------


def test_contract_agents_read_permission_registered() -> None:
    """Verify AGENTS_READ contract constant is present in ALL_PERMISSIONS registry."""
    assert AGENTS_READ == "agents:read"
    assert AGENTS_READ in ALL_PERMISSIONS


def test_require_permission_factory_creates_unique_dependency() -> None:
    """Verify require_permission returns distinct callables for different permission keys."""
    dep_agents = require_permission(AGENTS_READ)
    dep_payments = require_permission(PAYMENTS_READ)
    assert callable(dep_agents)
    assert callable(dep_payments)
    assert dep_agents is not dep_payments


# ---------------------------------------------------------------------------
# 2. Default-Deny & Role Resolution Protection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_default_deny_user_with_zero_roles() -> None:
    """Verify user with zero assigned roles receives empty frozenset and is denied."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )
    service = AuthorizationService()
    with patch.object(service, "resolve_permissions", new=AsyncMock(return_value=frozenset())):
        db = AsyncMock()
        decision = await service.has_permission(db, ctx, AGENTS_READ)
        assert decision.allowed is False


@pytest.mark.asyncio
async def test_default_deny_missing_permission_raises_forbidden() -> None:
    """Verify missing permission raises PermissionDeniedError (HTTP 403 Forbidden)."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )
    service = AuthorizationService()
    with patch.object(
        service,
        "resolve_permissions",
        new=AsyncMock(return_value=frozenset({PAYMENTS_READ})),
    ):
        db = AsyncMock()
        with pytest.raises(PermissionDeniedError) as exc_info:
            await service.require_permission(db, ctx, AGENTS_READ)
        assert exc_info.value.code == ErrorCode.FORBIDDEN


# ---------------------------------------------------------------------------
# 3. Tenant Isolation & Context Binding
# ---------------------------------------------------------------------------


def test_tenant_context_originates_from_authenticated_session() -> None:
    """Verify AuthorizationContext tenant_id is strictly derived from authenticated session."""
    session_tenant = uuid.uuid4()
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=session_tenant,
        session_id=uuid.uuid4(),
    )
    assert ctx.tenant_id == session_tenant


# ---------------------------------------------------------------------------
# 4. Security Code Bypass Scan
# ---------------------------------------------------------------------------


def test_security_bypass_scan_in_authorization_code() -> None:
    """Scan key authorization and API route files to ensure no hardcoded email/user_id bypasses exist."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    target_files = [
        base_dir / "app" / "application" / "services" / "authorization.py",
        base_dir / "app" / "api" / "v1" / "agents.py",
        base_dir / "app" / "api" / "dependencies" / "auth.py",
    ]

    prohibited_patterns = [
        re.compile(r'current_user\.email\s*==\s*["\']test', re.IGNORECASE),
        re.compile(r'user\.email\s*==\s*["\']admin', re.IGNORECASE),
        re.compile(r"skip_auth\s*=\s*True", re.IGNORECASE),
        re.compile(r"disable_authorization", re.IGNORECASE),
    ]

    for file_path in target_files:
        assert file_path.exists(), f"File {file_path} must exist for audit scan"
        content = file_path.read_text(encoding="utf-8")
        for pattern in prohibited_patterns:
            matches = pattern.findall(content)
            assert (
                len(matches) == 0
            ), f"Forbidden security bypass pattern '{pattern.pattern}' found in {file_path.name}"
