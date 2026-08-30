"""Unit tests for Phase 103 User Login flow, lockout, and session creation."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.auth import AuthenticationService
from app.core.security import hash_password
from app.domain.exceptions.auth_exceptions import (
    AccountDisabledError,
    AuthenticationFailedError,
)
from app.infrastructure.database.models.authentication_security import AuthenticationSecurity
from app.infrastructure.database.models.user import User
from app.schemas.auth import UserLoginRequest

_auth_service = AuthenticationService()


def _create_mock_db_session(
    user: User | None = None,
    auth_sec: AuthenticationSecurity | None = None,
) -> AsyncMock:
    """Construct mock AsyncSession for login service testing."""
    db = AsyncMock()
    db.add = MagicMock()
    db.add_all = MagicMock()

    user_result = MagicMock()
    user_result.scalar_one_or_none.return_value = user

    sec_result = MagicMock()
    sec_result.scalar_one_or_none.return_value = auth_sec

    db.execute.side_effect = [user_result, sec_result, MagicMock(), MagicMock(), MagicMock()]
    db.get.return_value = user
    return db


@pytest.mark.asyncio
async def test_01_login_success() -> None:
    """Verify valid login creates session and returns login response."""
    tenant_id = uuid.uuid4()
    pwd_hash = hash_password("SecureP@ssw0rd123!")

    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="dave@example.com",
        password_hash=pwd_hash,
        status="active",
    )
    auth_sec = AuthenticationSecurity(
        id=uuid.uuid4(),
        user_id=user.id,
        tenant_id=tenant_id,
        failed_login_attempts=0,
        status="active",
    )

    db = _create_mock_db_session(user=user, auth_sec=auth_sec)

    login_req = UserLoginRequest(
        tenant_id=tenant_id,
        email="dave@example.com",
        password="SecureP@ssw0rd123!",
        device_id="dev-123",
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1",
    )

    login_res = await _auth_service.authenticate_user(db, login_req, request_id="req-login-001")

    assert login_res.user_id == user.id
    assert login_res.tenant_id == tenant_id
    assert login_res.session_id is not None
    assert login_res.email == "dave@example.com"
    assert login_res.status == "active"
    assert login_res.expires_at is not None
    assert db.commit.called is True


@pytest.mark.asyncio
async def test_02_login_invalid_password_and_lockout() -> None:
    """Verify failed login attempts trigger account lockout after threshold."""
    tenant_id = uuid.uuid4()
    pwd_hash = hash_password("SecureP@ssw0rd123!")

    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="eve@example.com",
        password_hash=pwd_hash,
        status="active",
    )
    auth_sec = AuthenticationSecurity(
        id=uuid.uuid4(),
        user_id=user.id,
        tenant_id=tenant_id,
        failed_login_attempts=4,  # Already at 4 failures
        status="active",
    )

    db = _create_mock_db_session(user=user, auth_sec=auth_sec)

    bad_login_req = UserLoginRequest(
        tenant_id=tenant_id,
        email="eve@example.com",
        password="WrongP@ssw0rd!",
    )

    # 5th failed attempt triggers lockout and raises AuthenticationFailedError
    with pytest.raises(AuthenticationFailedError):
        await _auth_service.authenticate_user(db, bad_login_req)

    assert auth_sec.failed_login_attempts == 5
    assert auth_sec.status == "locked"
    assert auth_sec.locked_until is not None


@pytest.mark.asyncio
async def test_03_login_disabled_account_rejection() -> None:
    """Verify disabled or suspended user cannot authenticate."""
    tenant_id = uuid.uuid4()
    pwd_hash = hash_password("SecureP@ssw0rd123!")

    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="frank@example.com",
        password_hash=pwd_hash,
        status="suspended",
    )
    auth_sec = AuthenticationSecurity(
        id=uuid.uuid4(),
        user_id=user.id,
        tenant_id=tenant_id,
        failed_login_attempts=0,
        status="suspended",
    )

    db = _create_mock_db_session(user=user, auth_sec=auth_sec)

    login_req = UserLoginRequest(
        tenant_id=tenant_id,
        email="frank@example.com",
        password="SecureP@ssw0rd123!",
    )

    with pytest.raises(AccountDisabledError):
        await _auth_service.authenticate_user(db, login_req)


@pytest.mark.asyncio
async def test_04_cross_tenant_login_isolation() -> None:
    """Verify user registered in tenant A cannot authenticate in tenant B."""
    tenant_b = uuid.uuid4()

    # Searching in tenant_b returns None
    db = _create_mock_db_session(user=None, auth_sec=None)

    login_wrong_tenant = UserLoginRequest(
        tenant_id=tenant_b,
        email="grace@example.com",
        password="SecureP@ssw0rd123!",
    )

    with pytest.raises(AuthenticationFailedError):
        await _auth_service.authenticate_user(db, login_wrong_tenant)
