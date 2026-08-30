"""Centralized JWT authentication, token signing, and claim verification module."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import Settings, get_settings
from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode


class JWTAuthenticationError(AgentPayError):
    """Exception raised when JWT token verification, decoding, or claim validation fails."""

    def __init__(self, message: str = "Invalid or expired authentication token.") -> None:
        """Initialize JWTAuthenticationError with safe default message."""
        super().__init__(
            message=message,
            code=ErrorCode.UNAUTHORIZED,
        )


def create_access_token(
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    settings: Settings | None = None,
) -> str:
    """Issue signed JWT access token containing standardized non-sensitive claims.

    Claims included: sub (user_id), tenant_id, session_id, type="access", jti, iat, exp, iss, aud.
    """
    active_settings = settings or get_settings()
    now = datetime.now(UTC)
    expires = now + timedelta(minutes=active_settings.access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "session_id": str(session_id),
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "iss": active_settings.jwt_issuer,
        "aud": active_settings.jwt_audience,
    }

    secret = active_settings.jwt_secret.get_secret_value()
    encoded_token: str = jwt.encode(
        payload,
        secret,
        algorithm=active_settings.jwt_algorithm,
    )
    return encoded_token


def decode_access_token(
    token: str,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Decode, verify signature, validate expiration, issuer, audience, and token type.

    Raises JWTAuthenticationError on any signature mismatch, expiration, or claim invalidity.
    """
    active_settings = settings or get_settings()
    secret = active_settings.jwt_secret.get_secret_value()

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            secret,
            algorithms=[active_settings.jwt_algorithm],
            issuer=active_settings.jwt_issuer,
            audience=active_settings.jwt_audience,
            options={
                "verify_sub": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            },
        )
    except JWTError as exc:
        raise JWTAuthenticationError("Invalid or expired authentication token.") from exc
    except Exception as exc:
        raise JWTAuthenticationError("Token verification failed.") from exc

    # Enforce strict token type checking (access token cannot be a refresh token)
    if payload.get("type") != "access":
        raise JWTAuthenticationError("Token is not a valid access token.")

    # Validate required claim presence
    required_claims = ("sub", "tenant_id", "session_id")
    for claim in required_claims:
        if not payload.get(claim):
            raise JWTAuthenticationError(f"Missing required token claim: {claim}")

    return payload
