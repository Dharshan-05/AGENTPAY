"""Unit tests for Phase 102 User Registration flow and tenant isolation."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.auth import AuthenticationService
from app.domain.exceptions.auth_exceptions import UserAlreadyExistsError
from app.infrastructure.database.models.user import User
from app.schemas.auth import UserRegisterRequest

_auth_service = AuthenticationService()


def _create_mock_db_session(existing_user: User | None = None) -> AsyncMock:
    """Construct mock AsyncSession for testing AuthenticationService without external DB."""
    db = AsyncMock()
    db.add = MagicMock()
    db.add_all = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    db.execute.return_value = mock_result
    return db


@pytest.mark.asyncio
async def test_01_user_registration_success() -> None:
    """Verify successful user registration creates User, UserProfile, and security state."""
    tenant_id = uuid.uuid4()
    req = UserRegisterRequest(
        tenant_id=tenant_id,
        email="alice@example.com",
        password="SecureP@ssw0rd123!",
        first_name="Alice",
        last_name="Smith",
        display_name="Alice S.",
    )

    db = _create_mock_db_session(existing_user=None)
    res = await _auth_service.register_user(db, req, request_id="req-reg-001")

    assert res.user_id is not None
    assert res.tenant_id == tenant_id
    assert res.email == "alice@example.com"
    assert res.status == "active"
    assert res.profile is not None
    assert res.profile.first_name == "Alice"
    assert res.profile.display_name == "Alice S."
    assert db.commit.called is True
    assert db.add_all.called is True


@pytest.mark.asyncio
async def test_02_duplicate_user_registration_rejection() -> None:
    """Verify registration rejects duplicate email within same tenant scope."""
    tenant_id = uuid.uuid4()
    existing_user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email="bob@example.com",
        status="active",
    )

    db = _create_mock_db_session(existing_user=existing_user)

    req = UserRegisterRequest(
        tenant_id=tenant_id,
        email="bob@example.com",
        password="AnotherP@ssw0rd123!",
    )

    with pytest.raises(UserAlreadyExistsError):
        await _auth_service.register_user(db, req)


@pytest.mark.asyncio
async def test_03_tenant_isolation_in_registration() -> None:
    """Verify same email can register independently in different tenant scopes."""
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    req_a = UserRegisterRequest(
        tenant_id=tenant_a,
        email="charlie@example.com",
        password="SecureP@ssw0rd123!",
    )
    db_a = _create_mock_db_session(existing_user=None)
    res_a = await _auth_service.register_user(db_a, req_a)

    req_b = UserRegisterRequest(
        tenant_id=tenant_b,
        email="charlie@example.com",
        password="SecureP@ssw0rd123!",
    )
    db_b = _create_mock_db_session(existing_user=None)
    res_b = await _auth_service.register_user(db_b, req_b)

    assert res_a.tenant_id == tenant_a
    assert res_b.tenant_id == tenant_b
    assert res_a.user_id != res_b.user_id
