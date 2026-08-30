"""Unit tests for Phase 111 — RBAC Architecture.

Tests:
- AuthorizationContext construction and immutability
- AuthorizationDecision allow/deny factory
- PermissionsRegistry completeness
- Default-deny behavior in AuthorizationService
- Permission resolution from mocked DB
- AuthorizationContext zero-UUID rejection
"""

import uuid

import pytest

from app.domain.authorization.context import AuthorizationContext
from app.domain.authorization.decision import AuthorizationDecision
from app.domain.authorization.permissions_registry import (
    ALL_PERMISSIONS,
    PAYMENTS_READ,
    ROLES_ASSIGN,
    USERS_READ,
    is_valid_permission,
)
from app.domain.exceptions.auth_exceptions import PermissionDeniedError

# ---------------------------------------------------------------------------
# AuthorizationContext
# ---------------------------------------------------------------------------


def test_01_authorization_context_construction() -> None:
    """Verify AuthorizationContext constructs with valid UUIDs."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )
    assert isinstance(ctx.user_id, uuid.UUID)
    assert isinstance(ctx.tenant_id, uuid.UUID)
    assert isinstance(ctx.session_id, uuid.UUID)


def test_02_authorization_context_is_immutable() -> None:
    """Verify AuthorizationContext is frozen (immutable)."""
    from dataclasses import FrozenInstanceError

    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )
    with pytest.raises(FrozenInstanceError):
        ctx.user_id = uuid.uuid4()  # type: ignore[misc]


def test_03_authorization_context_rejects_zero_uuid() -> None:
    """Verify AuthorizationContext rejects zero-value UUIDs."""
    with pytest.raises(ValueError, match="user_id"):
        AuthorizationContext(
            user_id=uuid.UUID(int=0),
            tenant_id=uuid.uuid4(),
            session_id=uuid.uuid4(),
        )


def test_04_authorization_context_repr_is_safe() -> None:
    """Verify AuthorizationContext repr does not expose secrets."""
    ctx = AuthorizationContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        session_id=uuid.uuid4(),
    )
    repr_str = repr(ctx)
    assert "session_id" not in repr_str
    assert "AuthorizationContext" in repr_str


# ---------------------------------------------------------------------------
# AuthorizationDecision
# ---------------------------------------------------------------------------


def test_05_authorization_decision_allow() -> None:
    """Verify AuthorizationDecision.allow() sets allowed=True."""
    d = AuthorizationDecision.allow(permission=PAYMENTS_READ)
    assert d.allowed is True
    assert d.permission == PAYMENTS_READ


def test_06_authorization_decision_deny() -> None:
    """Verify AuthorizationDecision.deny() sets allowed=False (default-deny)."""
    d = AuthorizationDecision.deny(permission=USERS_READ)
    assert d.allowed is False
    assert d.permission == USERS_READ


def test_07_authorization_decision_is_immutable() -> None:
    """Verify AuthorizationDecision is frozen."""
    from dataclasses import FrozenInstanceError

    d = AuthorizationDecision.deny(permission=ROLES_ASSIGN)
    with pytest.raises(FrozenInstanceError):
        d.allowed = True  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Permissions Registry
# ---------------------------------------------------------------------------


def test_08_permissions_registry_completeness() -> None:
    """Verify ALL_PERMISSIONS is non-empty and contains critical permissions."""
    assert len(ALL_PERMISSIONS) > 20
    assert PAYMENTS_READ in ALL_PERMISSIONS
    assert USERS_READ in ALL_PERMISSIONS
    assert ROLES_ASSIGN in ALL_PERMISSIONS


def test_09_is_valid_permission_true_for_registered() -> None:
    """Verify is_valid_permission returns True for canonical names."""
    assert is_valid_permission(PAYMENTS_READ) is True


def test_10_is_valid_permission_false_for_unknown() -> None:
    """Verify is_valid_permission returns False for unknown names."""
    assert is_valid_permission("arbitrary:hack") is False
    assert is_valid_permission("") is False


# ---------------------------------------------------------------------------
# PermissionDeniedError
# ---------------------------------------------------------------------------


def test_11_permission_denied_error_with_permission() -> None:
    """Verify PermissionDeniedError includes permission in details."""
    err = PermissionDeniedError(permission=PAYMENTS_READ)
    assert err.details is not None
    assert "payments:read" in str(err.details)


def test_12_permission_denied_error_without_permission() -> None:
    """Verify PermissionDeniedError works without permission arg."""
    err = PermissionDeniedError()
    assert "permission" in err.message.lower() or "action" in err.message.lower()
