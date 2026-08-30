"""Unit tests for Phase 118 — User Preferences.

Tests:
- Preferences retrieval creates defaults when none exist
- Preferences retrieval returns existing record
- Preferences update merges patch into existing
- Default preferences contain all expected keys
- Partial update: only provided keys change
- Validation: locale format enforced
- Validation: empty timezone rejected
- Validation: unknown keys rejected (extra='forbid')
- Security: security-sensitive fields rejected from preferences update
- Security: preferences update verifies user exists in tenant (IDOR protection)
- Preferences response includes merged effective preferences
- UserPreferencesUpdateRequest to_patch_dict excludes None fields
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.application.services.user_service import UserService
from app.domain.exceptions.auth_exceptions import ResourceNotFoundOrForbiddenError
from app.infrastructure.database.models.user_preferences import (
    DEFAULT_PREFERENCES,
    UserPreferences,
)
from app.schemas.users import UserPreferencesUpdateRequest

_service = UserService()


def _make_prefs(
    tenant_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    preferences: dict[str, object] | None = None,
) -> UserPreferences:

    prefs = UserPreferences(
        id=uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        tenant_id=tenant_id or uuid.uuid4(),
        preferences=preferences or dict(DEFAULT_PREFERENCES),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return prefs


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


def test_01_default_preferences_contain_required_keys() -> None:
    """Verify DEFAULT_PREFERENCES contains all expected preference keys."""
    required_keys = {
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
    assert required_keys.issubset(DEFAULT_PREFERENCES.keys())


def test_02_effective_preferences_merges_with_defaults() -> None:
    """Verify effective_preferences() fills missing keys with defaults."""
    prefs = _make_prefs(preferences={"locale": "fr"})
    effective = prefs.effective_preferences()
    assert effective["locale"] == "fr"
    # Other keys come from defaults
    assert effective["ui_theme"] == DEFAULT_PREFERENCES["ui_theme"]
    assert effective["notification_email"] == DEFAULT_PREFERENCES["notification_email"]


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_03_get_preferences_returns_existing_record() -> None:
    """Verify get_user_preferences returns an existing preferences record."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    existing = _make_prefs(tenant_id, user_id)

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing
    db.execute.return_value = result

    prefs = await _service.get_user_preferences(db, tenant_id, user_id)
    assert prefs.user_id == user_id
    assert prefs.tenant_id == tenant_id


@pytest.mark.asyncio
async def test_04_get_preferences_creates_defaults_when_missing() -> None:
    """Verify get_user_preferences creates default record when none exists."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()

    new_prefs = _make_prefs(tenant_id, user_id)

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock(side_effect=lambda obj: None)

    with patch.object(
        _service, "_create_default_preferences", new=AsyncMock(return_value=new_prefs)
    ):
        prefs = await _service.get_user_preferences(db, tenant_id, user_id)
        assert prefs.user_id == user_id


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_05_update_preferences_merges_patch() -> None:
    """Verify update_user_preferences merges provided keys into existing preferences."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()

    existing = _make_prefs(tenant_id, user_id, preferences={"locale": "en", "ui_theme": "light"})

    from app.infrastructure.database.models.user import User

    mock_user = MagicMock(spec=User)
    mock_user.id = user_id

    db = AsyncMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    request = UserPreferencesUpdateRequest(locale="fr", ui_theme="dark")

    with (
        patch.object(_service, "get_user", new=AsyncMock(return_value=mock_user)),
        patch.object(_service, "get_user_preferences", new=AsyncMock(return_value=existing)),
    ):
        result = await _service.update_user_preferences(db, tenant_id, user_id, request)
        assert result.preferences["locale"] == "fr"
        assert result.preferences["ui_theme"] == "dark"


@pytest.mark.asyncio
async def test_06_update_preferences_idor_protection() -> None:
    """Verify update_user_preferences raises if user not in tenant."""
    tenant_id = uuid.uuid4()
    user_id = uuid.uuid4()
    request = UserPreferencesUpdateRequest(locale="fr")

    err = ResourceNotFoundOrForbiddenError("Not found")
    with patch.object(_service, "get_user", new=AsyncMock(side_effect=err)):
        db = AsyncMock()
        with pytest.raises(ResourceNotFoundOrForbiddenError):
            await _service.update_user_preferences(db, tenant_id, user_id, request)


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_07_preferences_update_rejects_invalid_locale() -> None:
    """Verify locale must match BCP-47 pattern."""
    with pytest.raises(ValidationError):
        UserPreferencesUpdateRequest.model_validate({"locale": "INVALID"})

    with pytest.raises(ValidationError):
        UserPreferencesUpdateRequest.model_validate({"locale": "en_US"})  # underscore not allowed


def test_08_preferences_update_rejects_empty_timezone() -> None:
    """Verify empty timezone is rejected."""
    with pytest.raises(ValidationError):
        UserPreferencesUpdateRequest.model_validate({"timezone": "   "})


def test_09_preferences_update_rejects_unknown_fields() -> None:
    """Verify extra fields are rejected (prevents mass assignment)."""
    with pytest.raises(ValidationError):
        UserPreferencesUpdateRequest.model_validate({"role": "admin"})

    with pytest.raises(ValidationError):
        UserPreferencesUpdateRequest.model_validate({"password": "hack"})

    with pytest.raises(ValidationError):
        UserPreferencesUpdateRequest.model_validate({"tenant_id": str(uuid.uuid4())})


def test_10_preferences_update_rejects_invalid_ui_theme() -> None:
    """Verify ui_theme must be one of light/dark/system."""
    with pytest.raises(ValidationError):
        UserPreferencesUpdateRequest.model_validate({"ui_theme": "pink"})


def test_11_to_patch_dict_excludes_none_fields() -> None:
    """Verify to_patch_dict only returns explicitly set (non-None) fields."""
    request = UserPreferencesUpdateRequest(locale="en-US", timezone="UTC")
    patch_dict = request.to_patch_dict()
    assert set(patch_dict.keys()) == {"locale", "timezone"}
    assert "notification_email" not in patch_dict


def test_12_valid_locale_formats_accepted() -> None:
    """Verify valid BCP-47 locale formats are accepted."""
    req = UserPreferencesUpdateRequest.model_validate({"locale": "en"})
    assert req.locale == "en"

    req2 = UserPreferencesUpdateRequest.model_validate({"locale": "en-US"})
    assert req2.locale == "en-US"
