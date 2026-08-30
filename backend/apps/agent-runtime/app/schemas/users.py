"""User Management Pydantic schemas for AGENTPAY (Phase 116–118).

Schemas:
    UserResponse              — Safe user representation (no secrets)
    UserListResponse          — Keyset-paginated user list
    UserStatusUpdateRequest   — Admin user status mutation
    UserProfileFullResponse   — Full profile response (Phase 117)
    UserProfileUpdateRequest  — Self-service profile mutation
    UserPreferencesResponse   — User preferences response (Phase 118)
    UserPreferencesUpdateRequest — User preferences mutation

Security:
    - password_hash is NEVER included in any response schema
    - failed_login_attempts is NEVER included
    - locked_until is NEVER included
    - All request schemas use extra='forbid' to prevent mass assignment
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# User Management (Phase 116)
# ---------------------------------------------------------------------------


class UserProfileEmbedded(BaseModel):
    """Minimal embedded profile for user list/get responses."""

    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    """Safe user representation — NEVER exposes security-sensitive fields."""

    id: uuid.UUID = Field(..., description="User UUIDv7")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    email: str = Field(..., description="User email address")
    status: str = Field(..., description="Account lifecycle status")
    email_verified_at: datetime | None = Field(default=None)
    last_login_at: datetime | None = Field(default=None)
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    profile: UserProfileEmbedded | None = Field(default=None)

    # Explicitly excluded: password_hash, failed_login_attempts, locked_until
    model_config = ConfigDict(from_attributes=True)


class UserListCursor(BaseModel):
    """Keyset pagination cursor for user listing."""

    next_created_at: datetime | None = Field(
        default=None, description="Cursor: created_at of last item"
    )
    next_id: uuid.UUID | None = Field(
        default=None, description="Cursor: id of last item for tie-breaking"
    )


class UserListResponse(BaseModel):
    """Paginated user list response with keyset cursor."""

    users: list[UserResponse] = Field(..., description="Page of users")
    count: int = Field(..., description="Number of users in this page")
    cursor: UserListCursor = Field(..., description="Pagination cursor for next page")

    model_config = ConfigDict(from_attributes=True)


class UserStatusUpdateRequest(BaseModel):
    """Admin request to change a user's account status."""

    status: Literal["active", "inactive", "suspended"] = Field(
        ...,
        description="New account lifecycle status",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


# ---------------------------------------------------------------------------
# User Profile (Phase 117)
# ---------------------------------------------------------------------------


class UserProfileFullResponse(BaseModel):
    """Full user profile response — safe, no authentication internals."""

    id: uuid.UUID = Field(..., description="Profile UUID")
    user_id: uuid.UUID = Field(..., description="Associated user UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    avatar_url: str | None = None
    phone_number: str | None = None
    created_at: datetime
    updated_at: datetime

    # Explicitly excluded: deleted_at (internal), timezone/locale go through preferences
    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdateRequest(BaseModel):
    """Self-service user profile mutation.

    Only allows updating display metadata.
    Cannot modify: tenant_id, user_id, id, role, permissions,
    authentication state, timezone, locale (those are in preferences).
    """

    first_name: str | None = Field(default=None, max_length=100, description="User first name")
    last_name: str | None = Field(default=None, max_length=100, description="User last name")
    display_name: str | None = Field(default=None, max_length=150, description="Display name")
    avatar_url: str | None = Field(default=None, max_length=500, description="Avatar image URL")
    phone_number: str | None = Field(default=None, max_length=50, description="Phone number")

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: str | None) -> str | None:
        """Ensure avatar URL uses https or is None."""
        if v is not None and v != "" and not v.startswith(("https://", "http://")):
            raise ValueError("avatar_url must be a valid http/https URL")
        return v


# ---------------------------------------------------------------------------
# User Preferences (Phase 118)
# ---------------------------------------------------------------------------

_ALLOWED_PREFERENCE_KEYS = frozenset(
    {
        "locale",
        "timezone",
        "notification_email",
        "notification_push",
        "notification_sms",
        "ui_theme",
        "ui_language",
        "accessibility_high_contrast",
        "accessibility_reduce_motion",
    }
)

_SECURITY_SENSITIVE_KEYS = frozenset(
    {
        "role",
        "roles",
        "permission",
        "permissions",
        "tenant_id",
        "status",
        "user_id",
        "password",
        "password_hash",
        "authentication",
        "is_admin",
        "is_system",
        "account_status",
    }
)


class UserPreferencesResponse(BaseModel):
    """User preferences response — contains merged effective preferences."""

    user_id: uuid.UUID = Field(..., description="User UUID")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID")
    preferences: dict[str, Any] = Field(..., description="Effective preference values")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class UserPreferencesUpdateRequest(BaseModel):
    """Partial update to user preferences.

    Validates each key-value pair. Rejects any security-sensitive fields.
    Unknown keys beyond the allowed set are rejected (extra='forbid').
    """

    locale: str | None = Field(default=None, max_length=20, description="BCP-47 locale code")
    timezone: str | None = Field(default=None, max_length=50, description="IANA timezone name")
    notification_email: bool | None = Field(default=None, description="Email notifications")
    notification_push: bool | None = Field(default=None, description="Push notifications")
    notification_sms: bool | None = Field(default=None, description="SMS notifications")
    ui_theme: Literal["light", "dark", "system"] | None = Field(
        default=None, description="UI color theme"
    )
    ui_language: str | None = Field(default=None, max_length=10, description="UI language code")
    accessibility_high_contrast: bool | None = Field(default=None, description="High contrast mode")
    accessibility_reduce_motion: bool | None = Field(default=None, description="Reduce motion")

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    @field_validator("locale")
    @classmethod
    def validate_locale(cls, v: str | None) -> str | None:
        """Validate locale format (e.g. 'en', 'en-US', 'zh-CN')."""
        if v is None:
            return v
        import re

        if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", v):
            raise ValueError("locale must be a BCP-47 format like 'en' or 'en-US'")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str | None) -> str | None:
        """Ensure timezone is non-empty string if provided."""
        if v is not None and v.strip() == "":
            raise ValueError("timezone must be a non-empty IANA timezone name")
        return v

    def to_patch_dict(self) -> dict[str, Any]:
        """Return only the explicitly set (non-None) preference fields."""
        return {k: v for k, v in self.model_dump().items() if v is not None}
