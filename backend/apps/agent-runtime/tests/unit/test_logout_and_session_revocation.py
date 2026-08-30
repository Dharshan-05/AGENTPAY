"""Unit tests for Phase 110 Logout & Session Revocation, idempotency, and logout_all_sessions."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.auth import AuthenticationService
from app.infrastructure.database.models.refresh_token import RefreshToken
from app.infrastructure.database.models.session import Session as SessionModel

_auth_service = AuthenticationService()


@pytest.mark.asyncio
async def test_01_logout_user_revokes_session_and_tokens() -> None:
    """Verify logout_user revokes session and associated refresh tokens in single transaction."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    session_obj = SessionModel(
        id=session_id,
        tenant_id=tenant_id,
        user_id=user_id,
        status="active",
    )
    refresh_tok = RefreshToken(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        session_id=session_id,
        token_hash="hash_123",
        status="active",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    db = AsyncMock()
    db.add = MagicMock()

    res_sess = MagicMock()
    res_sess.scalar_one_or_none.return_value = session_obj

    res_toks = MagicMock()
    res_toks.scalars.return_value = [refresh_tok]

    db.execute.side_effect = [res_sess, res_toks, MagicMock()]

    await _auth_service.logout_user(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        session_id=session_id,
        request_id="req-logout-01",
    )

    assert session_obj.status == "revoked"
    assert session_obj.revocation_reason == "user_logout"
    assert refresh_tok.status == "revoked"
    assert db.commit.called is True


@pytest.mark.asyncio
async def test_02_logout_idempotency_on_already_revoked_session() -> None:
    """Verify repeating logout on already-revoked session executes safely without error."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    already_revoked_session = SessionModel(
        id=session_id,
        tenant_id=tenant_id,
        user_id=user_id,
        status="revoked",
        revocation_reason="user_logout",
    )

    db = AsyncMock()
    db.add = MagicMock()

    res_sess = MagicMock()
    res_sess.scalar_one_or_none.return_value = already_revoked_session

    res_toks = MagicMock()
    res_toks.scalars.return_value = []

    db.execute.side_effect = [res_sess, res_toks, MagicMock()]

    # Should not raise exception
    await _auth_service.logout_user(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        session_id=session_id,
    )

    assert db.commit.called is True


@pytest.mark.asyncio
async def test_03_logout_all_sessions_revokes_all_user_sessions() -> None:
    """Verify logout_all_sessions revokes every session and token for user in tenant."""

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()

    sess1 = SessionModel(id=uuid.uuid4(), tenant_id=tenant_id, user_id=user_id, status="active")
    sess2 = SessionModel(id=uuid.uuid4(), tenant_id=tenant_id, user_id=user_id, status="active")

    tok1 = RefreshToken(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        session_id=sess1.id,
        token_hash="hash_a",
        status="active",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    tok2 = RefreshToken(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        session_id=sess2.id,
        token_hash="hash_b",
        status="active",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    db = AsyncMock()
    db.add = MagicMock()

    res_sess = MagicMock()
    res_sess.scalars.return_value = [sess1, sess2]

    res_toks = MagicMock()
    res_toks.scalars.return_value = [tok1, tok2]

    db.execute.side_effect = [res_sess, res_toks, MagicMock()]

    await _auth_service.logout_all_sessions(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        request_id="req-logout-all-01",
    )

    assert sess1.status == "revoked"
    assert sess1.revocation_reason == "user_logout_all"
    assert sess2.status == "revoked"
    assert sess2.revocation_reason == "user_logout_all"
    assert tok1.status == "revoked"
    assert tok2.status == "revoked"
    assert db.commit.called is True
