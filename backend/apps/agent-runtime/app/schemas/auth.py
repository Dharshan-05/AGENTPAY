"""Authentication request and response Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Pydantic request schema for user registration."""

    tenant_id: uuid.UUID = Field(
        ...,
        description="Multi-tenancy isolation UUID.",
    )
    email: EmailStr = Field(
        ...,
        description="User email address.",
        max_length=255,
    )
    password: str = Field(
        ...,
        description="Plaintext password to be validated and hashed.",
        min_length=8,
        max_length=128,
    )
    first_name: str | None = Field(
        default=None,
        max_length=100,
        description="Optional user first name.",
    )
    last_name: str | None = Field(
        default=None,
        max_length=100,
        description="Optional user last name.",
    )
    display_name: str | None = Field(
        default=None,
        max_length=150,
        description="Optional user display name.",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class UserLoginRequest(BaseModel):
    """Pydantic request schema for user login authentication."""

    tenant_id: uuid.UUID = Field(
        ...,
        description="Multi-tenancy isolation UUID.",
    )
    email: EmailStr = Field(
        ...,
        description="User email address.",
        max_length=255,
    )
    password: str = Field(
        ...,
        description="Plaintext password for verification.",
        min_length=1,
        max_length=128,
    )
    device_id: str | None = Field(
        default=None,
        max_length=255,
        description="Optional client device identifier.",
    )
    user_agent: str | None = Field(
        default=None,
        description="Optional HTTP User-Agent header string.",
    )
    ip_address: str | None = Field(
        default=None,
        max_length=45,
        description="Optional client IP address.",
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class TokenRefreshRequest(BaseModel):
    """Pydantic request schema for refreshing JWT access tokens using opaque refresh token."""

    tenant_id: uuid.UUID = Field(
        ...,
        description="Multi-tenancy isolation UUID.",
    )
    refresh_token: str = Field(
        ...,
        description="Raw opaque refresh token string.",
        min_length=1,
    )

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class UserProfileResponse(BaseModel):
    """Pydantic response schema for user profile data."""

    id: uuid.UUID
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserRegisterResponseData(BaseModel):
    """Pydantic response schema for successful user registration."""

    user_id: uuid.UUID = Field(..., description="Registered user UUIDv7.")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID.")
    email: str = Field(..., description="Normalized user email address.")
    status: str = Field(..., description="Account lifecycle status.")
    created_at: datetime = Field(..., description="Account creation timestamp.")
    profile: UserProfileResponse | None = Field(
        default=None, description="Associated user profile metadata."
    )

    model_config = ConfigDict(from_attributes=True)


class UserLoginResponseData(BaseModel):
    """Pydantic response schema for successful user login."""

    user_id: uuid.UUID = Field(..., description="Authenticated user UUIDv7.")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID.")
    session_id: uuid.UUID = Field(..., description="Created session UUIDv7.")
    email: str = Field(..., description="User email address.")
    status: str = Field(..., description="Account status.")
    expires_at: datetime = Field(..., description="Session expiration timestamp.")
    access_token: str | None = Field(default=None, description="Signed JWT access token.")
    refresh_token: str | None = Field(
        default=None, description="Opaque refresh token for token renewal."
    )
    token_type: str = Field(default="Bearer", description="HTTP authorization scheme type.")

    model_config = ConfigDict(from_attributes=True)


class TokenRefreshResponseData(BaseModel):
    """Pydantic response schema for successful token rotation and refresh."""

    access_token: str = Field(..., description="New signed JWT access token.")
    refresh_token: str = Field(..., description="New rotated opaque refresh token.")
    token_type: str = Field(default="Bearer", description="HTTP authorization scheme type.")
    expires_at: datetime = Field(..., description="New refresh token expiration timestamp.")

    model_config = ConfigDict(from_attributes=True)


class UserMeResponseData(BaseModel):
    """Pydantic response schema for current authenticated user details (/auth/me)."""

    user_id: uuid.UUID = Field(..., description="Authenticated user UUIDv7.")
    tenant_id: uuid.UUID = Field(..., description="Tenant isolation UUID.")
    session_id: uuid.UUID = Field(..., description="Active session UUIDv7.")
    email: str = Field(..., description="User email address.")
    status: str = Field(..., description="Account lifecycle status.")
    created_at: datetime = Field(..., description="Account creation timestamp.")
    profile: UserProfileResponse | None = Field(
        default=None, description="Associated profile metadata."
    )

    model_config = ConfigDict(from_attributes=True)
