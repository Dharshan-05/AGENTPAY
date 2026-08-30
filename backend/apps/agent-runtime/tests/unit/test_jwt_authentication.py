"""Unit tests for Phase 104 JWT Authentication layer, token creation, claims, and verification."""

import uuid

import pytest

from app.core.config import get_settings
from app.core.jwt import JWTAuthenticationError, create_access_token, decode_access_token


def test_01_create_and_decode_valid_access_token() -> None:
    """Verify signed JWT access token creation and decoding with claims validation."""
    settings = get_settings()
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    token = create_access_token(
        tenant_id=tenant_id,
        user_id=user_id,
        session_id=session_id,
        settings=settings,
    )

    assert isinstance(token, str)
    assert len(token) > 20

    payload = decode_access_token(token, settings=settings)
    assert payload["sub"] == str(user_id)
    assert payload["tenant_id"] == str(tenant_id)
    assert payload["session_id"] == str(session_id)
    assert payload["type"] == "access"
    assert payload["iss"] == settings.jwt_issuer
    assert payload["aud"] == settings.jwt_audience
    assert "jti" in payload
    assert "exp" in payload
    assert "iat" in payload


def test_02_tampered_token_rejection() -> None:
    """Verify decode_access_token rejects tampered or signature-mismatched JWTs."""
    settings = get_settings()
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    valid_token = create_access_token(
        tenant_id=tenant_id,
        user_id=user_id,
        session_id=session_id,
        settings=settings,
    )

    # Tamper with signature
    parts = valid_token.split(".")
    tampered_token = f"{parts[0]}.{parts[1]}.tampered_signature"

    with pytest.raises(JWTAuthenticationError, match="Invalid or expired authentication token"):
        decode_access_token(tampered_token, settings=settings)


def test_03_invalid_token_type_rejection() -> None:
    """Verify decode_access_token rejects tokens where type != 'access'."""
    from jose import jwt

    settings = get_settings()
    secret = settings.jwt_secret.get_secret_value()

    # Create token with type="refresh"
    payload = {
        "sub": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4()),
        "type": "refresh",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    wrong_type_token = jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)

    with pytest.raises(JWTAuthenticationError, match="not a valid access token"):
        decode_access_token(wrong_type_token, settings=settings)
