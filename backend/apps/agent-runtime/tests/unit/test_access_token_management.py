"""Unit tests for Phase 105 Access Token Management, Bearer authentication, and /auth/me."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.dependencies.auth import get_current_user
from app.application.services.auth import AuthenticationService
from app.core.jwt import create_access_token
from app.core.security import hash_password
from app.domain.exceptions.auth_exceptions import AccountDisabledError, AuthenticationFailedError
from app.infrastructure.database.models.authentication_security import AuthenticationSecurity
from app.infrastructure.database.models.session import Session as SessionModel
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.user_profile import UserProfile
from app.schemas.auth import UserLoginRequest

_auth_service = AuthenticationService()


def _create_mock_db_session(
    user: User | None = None,
    auth_sec: AuthenticationSecurity | None = None,
    session_obj: SessionModel | None = None,
) -> AsyncMock:
    """Construct mock AsyncSession for access token service testing."""
    db = AsyncMock()
    db.add = MagicMock()
    db.add_all = MagicMock()

    res_user = MagicMock()
    res_user.scalar_one_or_none.return_value = user

    res_sec = MagicMock()
    res_sec.scalar_one_or_none.return_value = auth_sec

    res_sess = MagicMock()
    res_sess.scalar_one_or_none.return_value = session_obj

    db.execute.side_effect = [res_user, res_sec, res_sess, res_user, MagicMock()]
    db.get.return_value = user
    return db


@pytest.mark.asyncio
async def test_01_login_issues_access_and_refresh_tokens() -> None:
    """Verify login issues valid signed JWT access token and opaque refresh token."""
    tenant_id = uuid.uuid4()
    pwd_hash = hash_password("SecureP@ssw0rd123!")

    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="token_user@example.com",
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
        email="token_user@example.com",
        password="SecureP@ssw0rd123!",
    )

    res = await _auth_service.authenticate_user(db, login_req)

    assert res.access_token is not None
    assert len(res.access_token) > 20
    assert res.refresh_token is not None
    assert len(res.refresh_token) > 30
    assert res.token_type == "Bearer"


@pytest.mark.asyncio
async def test_02_get_current_user_success() -> None:
    """Verify get_current_user dependency resolves authenticated user from Bearer token."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    user = User(
        id=user_id,
        tenant_id=tenant_id,
        email="bearer_user@example.com",
        status="active",
    )
    user.profile = UserProfile(
        id=uuid.uuid4(), user_id=user_id, tenant_id=tenant_id, first_name="Bearer"
    )

    session_obj = SessionModel(
        id=session_id,
        tenant_id=tenant_id,
        user_id=user_id,
        status="active",
    )

    token = create_access_token(tenant_id=tenant_id, user_id=user_id, session_id=session_id)

    db = AsyncMock()
    res_sess = MagicMock()
    res_sess.scalar_one_or_none.return_value = session_obj
    res_user = MagicMock()
    res_user.scalar_one_or_none.return_value = user
    db.execute.side_effect = [res_sess, res_user]

    request = MagicMock()
    request.state = MagicMock()

    credentials = MagicMock()
    credentials.credentials = token

    principal = await get_current_user(request=request, db=db, credentials=credentials)

    assert principal.user.id == user_id
    assert principal.tenant_id == tenant_id
    assert principal.session.id == session_id


@pytest.mark.asyncio
async def test_03_get_current_user_revoked_session_rejection() -> None:
    """Verify get_current_user rejects token if session is revoked."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    token = create_access_token(tenant_id=tenant_id, user_id=user_id, session_id=session_id)

    db = AsyncMock()
    res_sess = MagicMock()
    res_sess.scalar_one_or_none.return_value = None  # Session revoked or absent
    db.execute.return_value = res_sess

    request = MagicMock()
    credentials = MagicMock()
    credentials.credentials = token

    with pytest.raises(AuthenticationFailedError, match="Session is revoked, expired, or invalid"):
        await get_current_user(request=request, db=db, credentials=credentials)


@pytest.mark.asyncio
async def test_04_get_current_user_disabled_account_rejection() -> None:
    """Verify get_current_user rejects token if user account is suspended."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    suspended_user = User(
        id=user_id,
        tenant_id=tenant_id,
        email="suspended@example.com",
        status="suspended",
    )
    session_obj = SessionModel(
        id=session_id,
        tenant_id=tenant_id,
        user_id=user_id,
        status="active",
    )

    token = create_access_token(tenant_id=tenant_id, user_id=user_id, session_id=session_id)

    db = AsyncMock()
    res_sess = MagicMock()
    res_sess.scalar_one_or_none.return_value = session_obj
    res_user = MagicMock()
    res_user.scalar_one_or_none.return_value = suspended_user
    db.execute.side_effect = [res_sess, res_user]

    request = MagicMock()
    credentials = MagicMock()
    credentials.credentials = token

    with pytest.raises(AccountDisabledError):
        await get_current_user(request=request, db=db, credentials=credentials)
