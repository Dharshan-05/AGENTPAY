"""User Management application service for AGENTPAY (Phase 116–118).

Responsibilities:
    - Tenant-scoped user listing with keyset pagination
    - Tenant-scoped user retrieval (IDOR-safe)
    - User status administration
    - User profile retrieval and update
    - User preferences retrieval and upsert

Security invariants:
    - ALL queries include tenant_id in WHERE clause
    - Never fetch globally then filter in Python
    - Password hash and security internals are never returned
    - Profile updates cannot modify security-sensitive fields
    - Preferences updates cannot modify security-sensitive fields
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.exceptions.auth_exceptions import ResourceNotFoundOrForbiddenError
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.user_preferences import (
    DEFAULT_PREFERENCES,
    UserPreferences,
)
from app.infrastructure.database.models.user_profile import UserProfile
from app.schemas.users import (
    UserPreferencesUpdateRequest,
    UserProfileUpdateRequest,
    UserStatusUpdateRequest,
)

logger = logging.getLogger("agentpay.user.service")

_PAGE_SIZE_DEFAULT = 20
_PAGE_SIZE_MAX = 100


class UserService:
    """Application service for user management, profiles, and preferences."""

    # ------------------------------------------------------------------
    # Phase 116 — User Management
    # ------------------------------------------------------------------

    async def list_users(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        *,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        page_size: int = _PAGE_SIZE_DEFAULT,
    ) -> tuple[list[User], bool]:
        """List users within tenant using keyset pagination.

        Returns:
            (users, has_more) — users is a page of at most page_size records;
            has_more indicates whether another page exists.
        """
        page_size = min(max(1, page_size), _PAGE_SIZE_MAX)
        limit = page_size + 1  # fetch one extra to detect has_more

        stmt = (
            select(User)
            .where(
                User.tenant_id == tenant_id,
                User.deleted_at.is_(None),
            )
            .options(selectinload(User.profile))
        )

        # Keyset pagination: cursor is (created_at DESC, id DESC)
        if cursor_created_at is not None and cursor_id is not None:
            stmt = stmt.where(
                or_(
                    User.created_at < cursor_created_at,
                    and_(
                        User.created_at == cursor_created_at,
                        User.id < cursor_id,
                    ),
                )
            )

        stmt = stmt.order_by(User.created_at.desc(), User.id.desc()).limit(limit)
        result = await db.execute(stmt)
        rows = list(result.scalars().all())

        has_more = len(rows) > page_size
        if has_more:
            rows = rows[:page_size]

        return rows, has_more

    async def get_user(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> User:
        """Retrieve a user by ID within the authenticated tenant.

        Raises:
            ResourceNotFoundOrForbiddenError: if not found or cross-tenant.
        """
        stmt = (
            select(User)
            .where(
                User.id == user_id,
                User.tenant_id == tenant_id,
                User.deleted_at.is_(None),
            )
            .options(selectinload(User.profile))
        )
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise ResourceNotFoundOrForbiddenError(f"User {user_id} not found.")
        return user

    async def update_user_status(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        request: UserStatusUpdateRequest,
    ) -> User:
        """Update a user's account status within the authenticated tenant.

        Raises:
            ResourceNotFoundOrForbiddenError: if user not found.
            ValueError: if status unchanged.
        """
        user = await self.get_user(db, tenant_id, user_id)

        if user.status == request.status:
            raise ValueError(f"User is already in status '{request.status}'.")

        user.status = request.status
        await db.flush()
        await db.refresh(user)
        logger.info(
            "User status updated",
            extra={
                "user_id": str(user_id),
                "tenant_id": str(tenant_id),
                "new_status": request.status,
            },
        )
        return user

    # ------------------------------------------------------------------
    # Phase 117 — User Profile
    # ------------------------------------------------------------------

    async def get_user_profile(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> UserProfile:
        """Retrieve user profile within tenant scope.

        Raises:
            ResourceNotFoundOrForbiddenError: if not found or cross-tenant.
        """
        stmt = select(UserProfile).where(
            UserProfile.user_id == user_id,
            UserProfile.tenant_id == tenant_id,
            UserProfile.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()
        if profile is None:
            raise ResourceNotFoundOrForbiddenError(f"Profile for user {user_id} not found.")
        return profile

    async def update_user_profile(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        request: UserProfileUpdateRequest,
    ) -> UserProfile:
        """Update user profile (display fields only).

        Security: only first_name, last_name, display_name, avatar_url,
        phone_number can be updated. tenant_id, user_id, authentication
        fields are immutable here.

        Raises:
            ResourceNotFoundOrForbiddenError: if profile not found.
        """
        profile = await self.get_user_profile(db, tenant_id, user_id)

        updates = request.model_dump(exclude_none=True)
        for field, value in updates.items():
            setattr(profile, field, value)

        await db.flush()
        await db.refresh(profile)
        logger.info(
            "User profile updated",
            extra={"user_id": str(user_id), "tenant_id": str(tenant_id)},
        )
        return profile

    # ------------------------------------------------------------------
    # Phase 118 — User Preferences
    # ------------------------------------------------------------------

    async def get_user_preferences(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> UserPreferences:
        """Retrieve user preferences, creating default record if none exists.

        Preferences are never missing — a record is created on first access.
        """
        stmt = select(UserPreferences).where(
            UserPreferences.user_id == user_id,
            UserPreferences.tenant_id == tenant_id,
        )
        result = await db.execute(stmt)
        prefs = result.scalar_one_or_none()

        if prefs is None:
            prefs = await self._create_default_preferences(db, tenant_id, user_id)

        return prefs

    async def update_user_preferences(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        request: UserPreferencesUpdateRequest,
    ) -> UserPreferences:
        """Partial-update user preferences.

        Merges the provided patch into existing preferences.
        Validates that no security-sensitive fields are modified.

        Raises:
            ResourceNotFoundOrForbiddenError: if user not in this tenant.
        """
        # Verify user exists in this tenant first (IDOR protection)
        await self.get_user(db, tenant_id, user_id)

        prefs = await self.get_user_preferences(db, tenant_id, user_id)

        patch = request.to_patch_dict()
        if patch:
            # Merge patch into current JSONB preferences
            merged = {**(prefs.preferences or {}), **patch}
            prefs.preferences = merged
            await db.flush()
            await db.refresh(prefs)
            logger.info(
                "User preferences updated",
                extra={
                    "user_id": str(user_id),
                    "tenant_id": str(tenant_id),
                    "keys_updated": sorted(patch.keys()),
                },
            )

        return prefs

    async def _create_default_preferences(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> UserPreferences:
        """Create a new UserPreferences record with system defaults."""
        prefs = UserPreferences(
            id=uuid.uuid4(),
            user_id=user_id,
            tenant_id=tenant_id,
            preferences=dict(DEFAULT_PREFERENCES),
        )
        db.add(prefs)
        await db.flush()
        await db.refresh(prefs)
        return prefs
