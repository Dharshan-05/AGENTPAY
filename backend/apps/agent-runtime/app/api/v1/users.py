"""AGENTPAY User Management API Controller (Phase 116–118).

Endpoints:
    GET    /api/v1/users                     — List tenant users (paginated)
    GET    /api/v1/users/me                  — Get authenticated user
    GET    /api/v1/users/me/profile          — Get authenticated user's profile
    PATCH  /api/v1/users/me/profile          — Update authenticated user's profile
    GET    /api/v1/users/me/preferences      — Get authenticated user's preferences
    PATCH  /api/v1/users/me/preferences      — Update authenticated user's preferences
    GET    /api/v1/users/{user_id}           — Get user by ID (admin)
    PATCH  /api/v1/users/{user_id}/status    — Update user status (admin)
    GET    /api/v1/users/{user_id}/profile   — Get user profile by ID (admin)

Authorization:
    - /me/* endpoints: authenticated only (no additional permission required)
    - /users listing: users:read
    - /users/{id}: users:read
    - /users/{id}/status: users:update
    - /users/{id}/profile (admin): users:read

Note: /users/me must be registered BEFORE /users/{user_id} to avoid
      FastAPI matching "me" as a UUID path parameter.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.user_service import UserService
from app.domain.authorization.permissions_registry import (
    USERS_READ,
    USERS_UPDATE,
)
from app.domain.exceptions.auth_exceptions import ResourceNotFoundOrForbiddenError
from app.infrastructure.database.session import get_db_session
from app.schemas.users import (
    UserListCursor,
    UserListResponse,
    UserPreferencesResponse,
    UserPreferencesUpdateRequest,
    UserProfileFullResponse,
    UserProfileUpdateRequest,
    UserResponse,
    UserStatusUpdateRequest,
)

users_router = APIRouter(tags=["User Management"])


def get_user_service() -> UserService:
    """FastAPI dependency factory for UserService."""
    return UserService()


# ---------------------------------------------------------------------------
# /me routes — must be registered BEFORE /{user_id} routes
# ---------------------------------------------------------------------------


@users_router.get(
    "/users/me",
    status_code=status.HTTP_200_OK,
    summary="Get Authenticated User",
    description="Return the currently authenticated user's account details.",
    operation_id="get_me",
)
async def get_me(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> UserResponse:
    """Return the authenticated user's safe profile."""
    return UserResponse.model_validate(current_user.user)


@users_router.get(
    "/users/me/profile",
    status_code=status.HTTP_200_OK,
    summary="Get Authenticated User Profile",
    description="Return the currently authenticated user's full profile.",
    operation_id="get_me_profile",
)
async def get_me_profile(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileFullResponse:
    """Return the authenticated user's full profile."""
    try:
        profile = await service.get_user_profile(db, current_user.tenant_id, current_user.user.id)
    except ResourceNotFoundOrForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserProfileFullResponse.model_validate(profile)


@users_router.patch(
    "/users/me/profile",
    status_code=status.HTTP_200_OK,
    summary="Update Authenticated User Profile",
    description="Update the currently authenticated user's own profile.",
    operation_id="update_me_profile",
)
async def update_me_profile(
    body: UserProfileUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileFullResponse:
    """Update the authenticated user's own profile fields."""
    try:
        profile = await service.update_user_profile(
            db, current_user.tenant_id, current_user.user.id, body
        )
    except ResourceNotFoundOrForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserProfileFullResponse.model_validate(profile)


@users_router.get(
    "/users/me/preferences",
    status_code=status.HTTP_200_OK,
    summary="Get Authenticated User Preferences",
    description="Return the currently authenticated user's preferences.",
    operation_id="get_me_preferences",
)
async def get_me_preferences(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserPreferencesResponse:
    """Return the authenticated user's preferences (creates defaults if none exist)."""
    prefs = await service.get_user_preferences(db, current_user.tenant_id, current_user.user.id)
    return UserPreferencesResponse(
        user_id=prefs.user_id,
        tenant_id=prefs.tenant_id,
        preferences=prefs.effective_preferences(),
        updated_at=prefs.updated_at,
    )


@users_router.patch(
    "/users/me/preferences",
    status_code=status.HTTP_200_OK,
    summary="Update Authenticated User Preferences",
    description="Partially update the currently authenticated user's preferences.",
    operation_id="update_me_preferences",
)
async def update_me_preferences(
    body: UserPreferencesUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserPreferencesResponse:
    """Partially update the authenticated user's preference settings."""
    try:
        prefs = await service.update_user_preferences(
            db, current_user.tenant_id, current_user.user.id, body
        )
    except ResourceNotFoundOrForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserPreferencesResponse(
        user_id=prefs.user_id,
        tenant_id=prefs.tenant_id,
        preferences=prefs.effective_preferences(),
        updated_at=prefs.updated_at,
    )


# ---------------------------------------------------------------------------
# Admin user management routes — require explicit permissions
# ---------------------------------------------------------------------------


@users_router.get(
    "/users",
    status_code=status.HTTP_200_OK,
    summary="List Users",
    description="List users within the authenticated tenant with keyset pagination.",
    operation_id="list_users",
)
async def list_users(
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(USERS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[UserService, Depends(get_user_service)],
    page_size: Annotated[int, Query(ge=1, le=100, description="Page size")] = 20,
    cursor_created_at: Annotated[
        datetime | None,
        Query(description="Keyset cursor: created_at of last item"),
    ] = None,
    cursor_id: Annotated[
        uuid.UUID | None,
        Query(description="Keyset cursor: id of last item"),
    ] = None,
) -> UserListResponse:
    """List tenant users with keyset pagination (default-deny enforced)."""
    users, has_more = await service.list_users(
        db,
        current_user.tenant_id,
        cursor_created_at=cursor_created_at,
        cursor_id=cursor_id,
        page_size=page_size,
    )
    cursor = UserListCursor(
        next_created_at=users[-1].created_at if (has_more and users) else None,
        next_id=users[-1].id if (has_more and users) else None,
    )
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        count=len(users),
        cursor=cursor,
    )


@users_router.get(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Get User",
    description="Retrieve a specific user by ID within the authenticated tenant.",
    operation_id="get_user",
)
async def get_user(
    user_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(USERS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Retrieve user by ID (tenant-scoped, IDOR-protected)."""
    try:
        user = await service.get_user(db, current_user.tenant_id, user_id)
    except ResourceNotFoundOrForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserResponse.model_validate(user)


@users_router.patch(
    "/users/{user_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Update User Status",
    description="Update a user's account lifecycle status within the authenticated tenant.",
    operation_id="update_user_status",
)
async def update_user_status(
    user_id: uuid.UUID,
    body: UserStatusUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(USERS_UPDATE))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Update user's account status (admin action, requires users:update)."""
    try:
        user = await service.update_user_status(db, current_user.tenant_id, user_id, body)
    except ResourceNotFoundOrForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UserResponse.model_validate(user)


@users_router.get(
    "/users/{user_id}/profile",
    status_code=status.HTTP_200_OK,
    summary="Get User Profile (Admin)",
    description=(
        "Retrieve a specific user's profile within the authenticated tenant. "
        "Requires users:read permission."
    ),
    operation_id="get_user_profile",
)
async def get_user_profile(
    user_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(require_permission(USERS_READ))],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserProfileFullResponse:
    """Retrieve user profile by user ID (admin, tenant-scoped)."""
    try:
        profile = await service.get_user_profile(db, current_user.tenant_id, user_id)
    except ResourceNotFoundOrForbiddenError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserProfileFullResponse.model_validate(profile)
