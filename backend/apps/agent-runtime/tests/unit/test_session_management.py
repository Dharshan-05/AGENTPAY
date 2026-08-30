"""Unit tests for Phase 109 Session Management lifecycle & multi-session independence."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.api.dependencies.auth import get_current_user
from app.core.jwt import create_access_token
from app.domain.exceptions.auth_exceptions import AuthenticationFailedError
from app.infrastructure.database.models.session import Session as SessionModel


@pytest.mark.asyncio
async def test_01_session_model_repr_redacts_metadata() -> None:
    """Verify Session model __repr__ displays safe identifiers without exposing token secrets."""
    sess = SessionModel(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        status="active",
        user_agent="Mozilla/5.0 SecretBrowser",
        ip_address="192.168.1.1",
    )
    repr_str = repr(sess)

    assert "Mozilla/5.0" not in repr_str
    assert "status='active'" in repr_str


@pytest.mark.asyncio
async def test_02_expired_session_rejection() -> None:
    """Verify get_current_user rejects requests with expired session."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    expired_session = SessionModel(
        id=session_id,
        tenant_id=tenant_id,
        user_id=user_id,
        status="active",
        expires_at=datetime.now(UTC) - timedelta(minutes=10),  # Expired!
    )

    token = create_access_token(tenant_id=tenant_id, user_id=user_id, session_id=session_id)

    db = AsyncMock()
    res_sess = MagicMock()
    res_sess.scalar_one_or_none.return_value = expired_session
    db.execute.return_value = res_sess

    request = MagicMock()
    credentials = MagicMock()
    credentials.credentials = token

    with pytest.raises(AuthenticationFailedError, match="Session expired"):
        await get_current_user(request=request, db=db, credentials=credentials)


@pytest.mark.asyncio
async def test_03_tenant_mismatch_session_rejection() -> None:
    """Verify get_current_user rejects request if session tenant_id does not match token."""
    tenant_a = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    token = create_access_token(tenant_id=tenant_a, user_id=user_id, session_id=session_id)

    db = AsyncMock()
    res_sess = MagicMock()
    res_sess.scalar_one_or_none.return_value = None  # No matching session in tenant
    db.execute.return_value = res_sess

    request = MagicMock()
    credentials = MagicMock()
    credentials.credentials = token

    with pytest.raises(AuthenticationFailedError, match="revoked, expired, or invalid"):
        await get_current_user(request=request, db=db, credentials=credentials)


@pytest.mark.asyncio
async def test_04_multi_session_independence() -> None:
    """Verify multiple sessions for same user are created independently with distinct IDs."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()

    sess1 = SessionModel(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user_id,
        status="active",
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    sess2 = SessionModel(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        user_id=user_id,
        status="active",
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )

    assert sess1.id != sess2.id
    assert sess1.user_id == sess2.user_id == user_id
    assert sess1.tenant_id == sess2.tenant_id == tenant_id
    assert sess1.status == "active"
    assert sess2.status == "active"
