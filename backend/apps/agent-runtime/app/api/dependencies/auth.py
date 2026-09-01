"""FastAPI authentication dependencies for Bearer token extraction and session validation."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.jwt import JWTAuthenticationError, decode_access_token
from app.domain.exceptions.auth_exceptions import AccountDisabledError, AuthenticationFailedError
from app.infrastructure.database.models.session import Session as SessionModel
from app.infrastructure.database.models.user import User
from app.infrastructure.database.session import get_db_session

http_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    """Authenticated principal context container."""

    user: User
    session: SessionModel
    tenant_id: uuid.UUID


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer_scheme)],
) -> AuthenticatedUser:
    """Extract Bearer token, verify JWT signature & claims, validate session & user status."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationFailedError("Missing authorization header or Bearer token.")

    token = credentials.credentials.strip()
    payload = decode_access_token(token)

    try:
        user_id = uuid.UUID(str(payload["sub"]))
        tenant_id = uuid.UUID(str(payload["tenant_id"]))
        session_id = uuid.UUID(str(payload["session_id"]))
    except (KeyError, ValueError) as exc:
        raise JWTAuthenticationError("Malformed token claims.") from exc

    now = datetime.now(UTC)

    # 1. Validate Session state in database
    session_stmt = select(SessionModel).where(
        SessionModel.id == session_id,
        SessionModel.tenant_id == tenant_id,
        SessionModel.user_id == user_id,
    )
    session_res = await db.execute(session_stmt)
    session_obj = session_res.scalar_one_or_none()

    if session_obj is None or session_obj.status.lower() != "active":
        raise AuthenticationFailedError("Session is revoked, expired, or invalid.")

    if session_obj.expires_at is not None and now > session_obj.expires_at:
        raise AuthenticationFailedError("Session expired.")

    # 2. Validate User account state in database
    user_stmt = (
        select(User)
        .where(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.deleted_at.is_(None),
        )
        .options(selectinload(User.profile))
    )
    user_res = await db.execute(user_stmt)
    user_obj = user_res.scalar_one_or_none()

    if user_obj is None:
        raise AuthenticationFailedError("User account not found.")

    if user_obj.status.lower() in ("suspended", "disabled", "inactive", "locked"):
        raise AccountDisabledError("User account is disabled or suspended.")

    # 3. Store request context state
    request.state.request_id = getattr(request.state, "request_id", "")
    request.state.tenant_id = str(tenant_id)
    request.state.user_id = str(user_id)

    return AuthenticatedUser(
        user=user_obj,
        session=session_obj,
        tenant_id=tenant_id,
    )


async def get_current_user_optional(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer_scheme)],
) -> AuthenticatedUser | None:
    """Extract Bearer token if present, otherwise return None without raising error."""
    if credentials is None or not credentials.credentials:
        return None
    try:
        return await get_current_user(request=request, db=db, credentials=credentials)
    except Exception:
        return None

