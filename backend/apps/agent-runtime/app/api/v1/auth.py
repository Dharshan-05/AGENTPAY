"""API v1 Authentication & Token Management Controller for AGENTPAY (Phase 101–106)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.application.services.auth import AuthenticationService
from app.infrastructure.database.session import get_db_session
from app.schemas.auth import (
    TokenRefreshRequest,
    TokenRefreshResponseData,
    UserLoginRequest,
    UserLoginResponseData,
    UserMeResponseData,
    UserProfileResponse,
    UserRegisterRequest,
    UserRegisterResponseData,
)

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

_auth_service = AuthenticationService()


def get_auth_service() -> AuthenticationService:
    """Dependency provider for AuthenticationService."""
    return _auth_service


@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRegisterResponseData,
    summary="User Registration",
    description="Registers a new user within the specified tenant scope with password hashing.",
    operation_id="register_user",
)
async def register(
    request: Request,
    body: UserRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> UserRegisterResponseData:
    """Execute user registration flow."""
    request_id = getattr(request.state, "request_id", None)
    return await service.register_user(db, body, request_id=request_id)


@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponseData,
    summary="User Login",
    description=(
        "Authenticates user credentials and issues signed JWT access token and refresh token."
    ),
    operation_id="login_user",
)
async def login(
    request: Request,
    body: UserLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> UserLoginResponseData:
    """Execute user login authentication flow."""
    request_id = getattr(request.state, "request_id", None)
    return await service.authenticate_user(db, body, request_id=request_id)


@auth_router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenRefreshResponseData,
    summary="Token Refresh & Rotation",
    description="Rotates opaque refresh token and issues a new signed JWT access token.",
    operation_id="refresh_tokens",
)
async def refresh_tokens(
    request: Request,
    body: TokenRefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> TokenRefreshResponseData:
    """Execute refresh token rotation flow."""
    request_id = getattr(request.state, "request_id", None)
    user_agent = request.headers.get("user-agent")
    client_host = request.client.host if request.client else None

    return await service.refresh_tokens(
        db=db,
        request_data=body,
        request_id=request_id,
        ip_address=client_host,
        user_agent=user_agent,
    )


@auth_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserMeResponseData,
    summary="Current User Context",
    description="Returns safe identity and profile metadata for the authenticated user.",
    operation_id="get_current_user_me",
)
async def get_me(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> UserMeResponseData:
    """Return authenticated principal user details."""
    u = current_user.user
    p = u.profile
    profile_resp = (
        UserProfileResponse(
            id=p.id,
            first_name=p.first_name,
            last_name=p.last_name,
            display_name=p.display_name,
        )
        if p
        else None
    )

    return UserMeResponseData(
        user_id=u.id,
        tenant_id=u.tenant_id,
        session_id=current_user.session.id,
        email=u.email,
        status=u.status,
        created_at=u.created_at,
        profile=profile_resp,
    )


@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Revokes current authenticated session and all associated refresh tokens.",
    operation_id="logout_user",
)
async def logout(
    request: Request,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[AuthenticationService, Depends(get_auth_service)],
) -> dict[str, str]:
    """Execute user logout flow."""
    request_id = getattr(request.state, "request_id", None)
    await service.logout_user(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user.id,
        session_id=current_user.session.id,
        request_id=request_id,
    )
    return {"message": "Successfully logged out."}
