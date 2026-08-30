"""Unit tests for Phase 106 Refresh Token Management, rotation, & replay protection."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.auth import AuthenticationService
from app.core.tokens import generate_opaque_token, hash_token
from app.domain.exceptions.auth_exceptions import AuthenticationFailedError
from app.infrastructure.database.models.refresh_token import RefreshToken
from app.infrastructure.database.models.session import Session as SessionModel
from app.infrastructure.database.models.user import User
from app.schemas.auth import TokenRefreshRequest

_auth_service = AuthenticationService()


def test_01_opaque_token_generation_and_hashing() -> None:
    """Verify opaque token generator and hash_token SHA-256 digest function."""

    raw_token = generate_opaque_token(64)
    assert isinstance(raw_token, str)
    assert len(raw_token) >= 64

    digest = hash_token(raw_token)
    assert isinstance(digest, str)
    assert len(digest) == 64
    assert hash_token(raw_token) == digest


@pytest.mark.asyncio
async def test_02_successful_refresh_token_rotation() -> None:
    """Verify refresh_tokens rotates old refresh token, generates new access and refresh tokens."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    token_id = uuid.uuid4()

    raw_token = generate_opaque_token()
    token_digest = hash_token(raw_token)
    expires_at = datetime.now(UTC) + timedelta(days=7)

    session_obj = SessionModel(
        id=session_id,
        tenant_id=tenant_id,
        user_id=user_id,
        status="active",
    )
    refresh_record = RefreshToken(
        id=token_id,
        tenant_id=tenant_id,
        session_id=session_id,
        token_hash=token_digest,
        family_id=uuid.uuid4(),
        status="active",
        expires_at=expires_at,
    )
    refresh_record.session = session_obj

    user_obj = User(
        id=user_id,
        tenant_id=tenant_id,
        email="rotate@example.com",
        status="active",
    )

    db = AsyncMock()
    db.add = MagicMock()
    db.add_all = MagicMock()

    res_tok = MagicMock()
    res_tok.scalar_one_or_none.return_value = refresh_record
    res_user = MagicMock()
    res_user.scalar_one_or_none.return_value = user_obj
    db.execute.side_effect = [res_tok, res_user, MagicMock()]

    req = TokenRefreshRequest(tenant_id=tenant_id, refresh_token=raw_token)
    res = await _auth_service.refresh_tokens(db, req)

    assert refresh_record.status == "rotated"
    assert refresh_record.rotated_at is not None
    assert res.access_token is not None
    assert res.refresh_token is not None
    assert res.refresh_token != raw_token
    assert db.commit.called is True


@pytest.mark.asyncio
async def test_03_refresh_token_replay_protection() -> None:
    """Verify presenting already-rotated refresh token triggers replay detection & revocation."""

    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    family_id = uuid.uuid4()

    raw_token = generate_opaque_token()
    token_digest = hash_token(raw_token)

    session_obj = SessionModel(
        id=session_id,
        tenant_id=tenant_id,
        user_id=user_id,
        status="active",
    )
    already_rotated_token = RefreshToken(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        session_id=session_id,
        token_hash=token_digest,
        family_id=family_id,
        status="rotated",  # Already rotated! Replay!
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    already_rotated_token.session = session_obj

    db = AsyncMock()
    db.add = MagicMock()
    db.add_all = MagicMock()

    res_tok = MagicMock()
    res_tok.scalar_one_or_none.return_value = already_rotated_token

    fam_tokens = MagicMock()
    fam_tokens.scalars.return_value = [already_rotated_token]

    db.execute.side_effect = [res_tok, fam_tokens, MagicMock()]

    req = TokenRefreshRequest(tenant_id=tenant_id, refresh_token=raw_token)

    with pytest.raises(AuthenticationFailedError, match="reuse detected"):
        await _auth_service.refresh_tokens(db, req)

    assert session_obj.status == "revoked"
    assert session_obj.revocation_reason == "refresh_token_reuse_detected"
    assert db.commit.called is True


@pytest.mark.asyncio
async def test_04_logout_user_revokes_session_and_refresh_tokens() -> None:
    """Verify logout_user revokes server-side session and all associated refresh tokens."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    session_obj = SessionModel(
        id=session_id,
        tenant_id=tenant_id,
        user_id=user_id,
        status="active",
    )
    tok1 = RefreshToken(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        session_id=session_id,
        token_hash="hash1",
        status="active",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )
    tok2 = RefreshToken(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        session_id=session_id,
        token_hash="hash2",
        status="active",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    db = AsyncMock()
    db.add = MagicMock()
    db.add_all = MagicMock()

    res_sess = MagicMock()
    res_sess.scalar_one_or_none.return_value = session_obj

    res_toks = MagicMock()
    res_toks.scalars.return_value = [tok1, tok2]

    db.execute.side_effect = [res_sess, res_toks, MagicMock()]

    await _auth_service.logout_user(db, tenant_id=tenant_id, user_id=user_id, session_id=session_id)

    assert session_obj.status == "revoked"
    assert session_obj.revocation_reason == "user_logout"
    assert tok1.status == "revoked"
    assert tok2.status == "revoked"
    assert db.commit.called is True
