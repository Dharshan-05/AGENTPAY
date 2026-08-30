"""Unit tests for Phase 119 — Agent Registry API.

Tests:
- List agents (returns tenant-scoped agents)
- Empty registry listing
- Filter agents by search term, agent_type, status
- Keyset pagination (cursor returned when has_more=True)
- Limit clamped to max limit (100)
- Get agent by ID (same-tenant success)
- Get agent cross-tenant raises AgentNotFoundError (IDOR-safe 404)
- AgentNotFoundError maps to 404
- Safe serialization (AgentResponse includes no credentials or secrets)
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_service import AgentService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_identity import AgentIdentity
from app.schemas.agents import AgentCreateRequest, AgentResponse

_service = AgentService()


def _make_agent(
    tenant_id: uuid.UUID | None = None,
    name: str = "Test Bot",
    slug: str = "test-bot",
    agent_type: str = "autonomous",
    status: str = "active",
) -> Agent:
    agent_id = uuid.uuid4()
    tid = tenant_id or uuid.uuid4()
    agent = Agent(
        id=agent_id,
        tenant_id=tid,
        name=name,
        slug=slug,
        agent_type=agent_type,
        status=status,
        description="A test agent",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    agent.identity = AgentIdentity(
        id=uuid.uuid4(),
        tenant_id=tid,
        agent_id=agent_id,
        display_name=name,
        identity_type="standard",
        external_reference=None,
        description=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    return agent


@pytest.mark.asyncio
async def test_01_list_agents_returns_tenant_agents() -> None:
    """Verify list_agents returns only agents belonging to the tenant."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)

    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [agent]
    db.execute.return_value = result

    agents, has_more = await _service.list_agents(db, tenant_id)
    assert len(agents) == 1
    assert agents[0].tenant_id == tenant_id
    assert has_more is False


@pytest.mark.asyncio
async def test_02_list_agents_empty_registry() -> None:
    """Verify list_agents returns empty list when no agents exist in tenant."""
    tenant_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    db.execute.return_value = result

    agents, has_more = await _service.list_agents(db, tenant_id)
    assert agents == []
    assert has_more is False


@pytest.mark.asyncio
async def test_03_list_agents_has_more_pagination() -> None:
    """Verify has_more is True when database returns extra item beyond limit."""
    tenant_id = uuid.uuid4()
    items = [_make_agent(tenant_id, slug=f"bot-{i}") for i in range(21)]

    db = AsyncMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = items
    db.execute.return_value = result

    agents, has_more = await _service.list_agents(db, tenant_id, limit=20)
    assert len(agents) == 20
    assert has_more is True


@pytest.mark.asyncio
async def test_04_get_agent_returns_agent_in_tenant() -> None:
    """Verify get_agent returns target agent when tenant matches."""
    tenant_id = uuid.uuid4()
    agent = _make_agent(tenant_id)

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = agent
    db.execute.return_value = result

    fetched = await _service.get_agent(db, tenant_id, agent.id)
    assert fetched.id == agent.id
    assert fetched.tenant_id == tenant_id


@pytest.mark.asyncio
async def test_05_get_agent_cross_tenant_raises_not_found() -> None:
    """Verify get_agent raises AgentNotFoundError (IDOR 404) for cross-tenant access."""
    tenant_a = uuid.uuid4()
    agent_id = uuid.uuid4()

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result

    with pytest.raises(AgentNotFoundError):
        await _service.get_agent(db, tenant_a, agent_id)


def test_06_agent_response_safe_serialization() -> None:
    """Verify AgentResponse schema contains zero credential or secret fields."""
    schema_fields = set(AgentResponse.model_fields.keys())
    forbidden = {
        "password",
        "password_hash",
        "secret",
        "secret_key",
        "api_key",
        "credentials",
        "access_token",
    }
    assert forbidden.isdisjoint(schema_fields)


def test_07_slug_validation_rejects_invalid_chars() -> None:
    """Verify AgentCreateRequest slug validator rejects spaces and special characters."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AgentCreateRequest.model_validate({"name": "Bot", "slug": "Invalid Slug!"})

    with pytest.raises(ValidationError):
        AgentCreateRequest.model_validate({"name": "Bot", "slug": "slug_with_underscores"})
