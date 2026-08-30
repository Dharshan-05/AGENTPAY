"""Unit tests for Phase 121 — Agent Identity Service.

Tests:
- Retrieve agent identity (same-tenant success)
- Retrieve agent identity cross-tenant raises AgentIdentityNotFoundError (IDOR 404)
- Create agent identity (success)
- Create duplicate identity raises AgentIdentityAlreadyExistsError (1-to-1 invariant)
- AgentIdentityResponse schema has zero credentials/secret material
- Separation of concerns: identity contains no tokens, keys, or passwords
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_service import AgentIdentityService
from app.domain.exceptions.agent_exceptions import (
    AgentIdentityAlreadyExistsError,
    AgentIdentityNotFoundError,
)
from app.infrastructure.database.models.agent_identity import AgentIdentity
from app.schemas.agents import AgentIdentityResponse

_identity_service = AgentIdentityService()


def _make_identity(
    tenant_id: uuid.UUID | None = None,
    agent_id: uuid.UUID | None = None,
) -> AgentIdentity:
    return AgentIdentity(
        id=uuid.uuid4(),
        tenant_id=tenant_id or uuid.uuid4(),
        agent_id=agent_id or uuid.uuid4(),
        display_name="Test Agent Identity",
        identity_type="standard",
        external_reference=None,
        description=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_01_get_agent_identity_success() -> None:
    """Verify get_agent_identity retrieves identity for agent in tenant."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    identity = _make_identity(tenant_id, agent_id)

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = identity
    db.execute.return_value = result

    fetched = await _identity_service.get_agent_identity(db, tenant_id, agent_id)
    assert fetched.agent_id == agent_id
    assert fetched.tenant_id == tenant_id


@pytest.mark.asyncio
async def test_02_get_agent_identity_cross_tenant_raises_not_found() -> None:
    """Verify get_agent_identity raises AgentIdentityNotFoundError for cross-tenant access."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(AgentIdentityNotFoundError):
        await _identity_service.get_agent_identity(db, tenant_a, agent_id)


@pytest.mark.asyncio
async def test_03_create_agent_identity_success() -> None:
    """Verify create_agent_identity creates identity bound to tenant and agent."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None  # No existing identity
    db.execute.return_value = result
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    identity = await _identity_service.create_agent_identity(
        db,
        tenant_id,
        agent_id,
        display_name="Custom Identity",
    )
    assert identity.agent_id == agent_id
    assert identity.tenant_id == tenant_id
    assert identity.display_name == "Custom Identity"


@pytest.mark.asyncio
async def test_04_create_duplicate_agent_identity_raises_conflict() -> None:
    """Verify creating duplicate identity for an agent raises AgentIdentityAlreadyExistsError."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    existing = _make_identity(tenant_id, agent_id)

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing
    db.execute.return_value = result

    with pytest.raises(AgentIdentityAlreadyExistsError):
        await _identity_service.create_agent_identity(db, tenant_id, agent_id)


def test_05_agent_identity_response_zero_credentials() -> None:
    """Verify AgentIdentityResponse contains no credential or secret key fields."""
    fields = set(AgentIdentityResponse.model_fields.keys())
    forbidden = {"password", "secret", "api_key", "credentials", "token", "private_key"}
    assert forbidden.isdisjoint(fields)
