"""Unit tests for Phase 117 — User Profile API.

Tests:
- Profile retrieval (same-tenant)
- Profile retrieval cross-tenant rejected
- Profile update success (allowed fields)
- Profile update rejects forbidden fields (tenant_id, user_id, role)
- Profile update validator: invalid avatar_url
- Profile update: only set fields are applied (partial update)
- UserProfileFullResponse never exposes authentication data
- Secret redaction: no password/token fields in profile response
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.application.services.user_service import UserService
from app.domain.exceptions.auth_exceptions import ResourceNotFoundOrForbiddenError
from app.infrastructure.database.models.user_profile import UserProfile
from app.schemas.users import UserProfileFullResponse, UserProfileUpdateRequest

_service = UserService()


def _make_profile(
    tenant_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
) -> UserProfile:
    return UserProfile(
        id=uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        tenant_id=tenant_id or uuid.uuid4(),
        first_name="Alice",
        last_name="Smith",
        display_name="alice",
        avatar_url=None,
        phone_number=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


# ---------------------------------------------------------------------------
# Profile retrieval
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_01_get_user_profile_returns_profile() -> None:
    """Verify get_user_profile returns the correct profile for the tenant."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    profile = _make_profile(tenant_id, user_id)

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = profile
    db.execute.return_value = result

    fetched = await _service.get_user_profile(db, tenant_id, user_id)
    assert fetched.user_id == user_id
    assert fetched.tenant_id == tenant_id


@pytest.mark.asyncio
async def test_02_get_user_profile_cross_tenant_raises_not_found() -> None:
    """Verify cross-tenant profile access raises ResourceNotFoundOrForbiddenError."""
    tenant_b = uuid.uuid4()
    user_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(ResourceNotFoundOrForbiddenError):
        await _service.get_user_profile(db, tenant_b, user_id)


@pytest.mark.asyncio
async def test_03_get_user_profile_not_found_raises_not_found() -> None:
    """Verify profile not found raises ResourceNotFoundOrForbiddenError."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(ResourceNotFoundOrForbiddenError):
        await _service.get_user_profile(db, uuid.uuid4(), uuid.uuid4())


# ---------------------------------------------------------------------------
# Profile update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_04_update_user_profile_success() -> None:
    """Verify update_user_profile applies allowed field changes."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    profile = _make_profile(tenant_id, user_id)

    db = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    request = UserProfileUpdateRequest(display_name="alice-updated")

    with patch.object(_service, "get_user_profile", new=AsyncMock(return_value=profile)):
        result = await _service.update_user_profile(db, tenant_id, user_id, request)
        assert result.display_name == "alice-updated"


@pytest.mark.asyncio
async def test_05_update_user_profile_partial_only_updates_set_fields() -> None:
    """Verify update_user_profile only updates provided fields, leaving others unchanged."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    profile = _make_profile(tenant_id, user_id)
    original_first_name = profile.first_name

    db = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    # Only update last_name, leave first_name unchanged
    request = UserProfileUpdateRequest(last_name="Jones")

    with patch.object(_service, "get_user_profile", new=AsyncMock(return_value=profile)):
        result = await _service.update_user_profile(db, tenant_id, user_id, request)
        assert result.last_name == "Jones"
        assert result.first_name == original_first_name


# ---------------------------------------------------------------------------
# Schema validation / security
# ---------------------------------------------------------------------------


def test_06_profile_update_rejects_extra_fields() -> None:
    """Verify UserProfileUpdateRequest rejects unauthorized fields."""
    with pytest.raises(ValidationError):
        UserProfileUpdateRequest.model_validate({"tenant_id": str(uuid.uuid4())})

    with pytest.raises(ValidationError):
        UserProfileUpdateRequest.model_validate({"role": "admin"})

    with pytest.raises(ValidationError):
        UserProfileUpdateRequest.model_validate({"password": "hack"})


def test_07_profile_update_rejects_invalid_avatar_url() -> None:
    """Verify avatar_url must be a valid http/https URL."""
    with pytest.raises(ValidationError):
        UserProfileUpdateRequest.model_validate({"avatar_url": "ftp://invalid-scheme.com/pic.jpg"})


def test_08_user_profile_response_never_exposes_auth_fields() -> None:
    """Verify UserProfileFullResponse schema excludes authentication internals."""
    schema_fields = UserProfileFullResponse.model_fields
    forbidden = {"password_hash", "status", "failed_login_attempts", "locked_until"}
    for field in forbidden:
        assert field not in schema_fields, f"Field '{field}' must not appear in profile response"
