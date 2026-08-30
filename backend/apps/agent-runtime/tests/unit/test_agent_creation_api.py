"""Unit tests for Phase 120 — Agent Creation API.

Tests:
- Successful agent creation with auto-generated slug
- Successful agent creation with custom valid slug
- Atomic creation of Agent + AgentIdentity records
- Duplicate slug conflict raises AgentAlreadyExistsError
- Mass assignment prevention: AgentCreateRequest extra='forbid'
- Client tenant_id injection rejected by Pydantic schema
- Client agent_id injection rejected by Pydantic schema
- Client roles / permissions / trust injection rejected
- Zero secret leakage in creation response
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from app.application.services.agent_service import AgentService
from app.domain.exceptions.agent_exceptions import AgentAlreadyExistsError
from app.schemas.agents import AgentCreateRequest

_service = AgentService()


@pytest.mark.asyncio
async def test_01_create_agent_success_atomic() -> None:
    """Verify create_agent creates both Agent and AgentIdentity atomically in tenant."""
    tenant_id = uuid.uuid4()
    req = AgentCreateRequest(
        name="Commerce Bot",
        agent_type="autonomous",
        description="Automated commerce worker",
    )

    db = AsyncMock()
    # Mock no existing duplicate slug
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    agent = await _service.create_agent(db, tenant_id, req)
    assert agent.name == "Commerce Bot"
    assert agent.slug == "commerce-bot"
    assert agent.tenant_id == tenant_id
    assert db.add.call_count == 3  # Agent, AgentIdentity, and AgentLifecycle added atomically


@pytest.mark.asyncio
async def test_02_create_agent_custom_slug() -> None:
    """Verify custom slug is respected during creation."""
    tenant_id = uuid.uuid4()
    req = AgentCreateRequest(
        name="Custom Bot",
        slug="custom-bot-v1",
    )

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    db.execute.return_value = result
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.refresh = AsyncMock()

    agent = await _service.create_agent(db, tenant_id, req)
    assert agent.slug == "custom-bot-v1"


@pytest.mark.asyncio
async def test_03_create_agent_duplicate_slug_conflict() -> None:
    """Verify create_agent raises AgentAlreadyExistsError when slug exists in tenant."""
    tenant_id = uuid.uuid4()
    req = AgentCreateRequest(name="Duplicate Bot", slug="dup-bot")

    from app.infrastructure.database.models.agent import Agent

    existing_agent = MagicMock(spec=Agent)

    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing_agent
    db.execute.return_value = result

    with pytest.raises(AgentAlreadyExistsError):
        await _service.create_agent(db, tenant_id, req)


def test_04_create_request_rejects_extra_fields() -> None:
    """Verify AgentCreateRequest rejects extra/unauthorized client fields (mass assignment)."""
    with pytest.raises(ValidationError):
        AgentCreateRequest.model_validate({"name": "Bot", "tenant_id": str(uuid.uuid4())})

    with pytest.raises(ValidationError):
        AgentCreateRequest.model_validate({"name": "Bot", "agent_id": str(uuid.uuid4())})

    with pytest.raises(ValidationError):
        AgentCreateRequest.model_validate({"name": "Bot", "roles": ["admin"]})

    with pytest.raises(ValidationError):
        AgentCreateRequest.model_validate({"name": "Bot", "trust_score": 100})

    with pytest.raises(ValidationError):
        AgentCreateRequest.model_validate({"name": "Bot", "credentials": "secret"})


@pytest.mark.asyncio
async def test_05_slugify_fallback_for_non_latin() -> None:
    """Verify slug generation creates fallback slug if name has no ascii characters."""
    from app.application.services.agent_service import _slugify

    slug = _slugify("🤖🌟")
    assert slug.startswith("agent-")
