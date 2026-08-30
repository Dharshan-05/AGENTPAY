"""Unit & Security tests for Phase 131 — Agent Metadata."""

import uuid
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.agent_metadata_service import AgentMetadataService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent


@pytest.mark.asyncio
async def test_get_agent_metadata_success(db_session: AsyncSession) -> None:
    """Test successful retrieval/initialization of AgentMetadata."""
    service = AgentMetadataService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Meta Agent",
        slug="meta-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    meta = await service.get_agent_metadata(db_session, tenant_id, agent_id)
    assert meta is not None
    assert meta.agent_id == agent_id
    assert meta.tenant_id == tenant_id
    assert isinstance(meta.metadata_payload, dict)


@pytest.mark.asyncio
async def test_update_agent_metadata_success(db_session: AsyncSession) -> None:
    """Test updating agent metadata payload."""
    service = AgentMetadataService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Meta Agent 2",
        slug="meta-agent-2",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    updates = {"environment": "production", "version": "1.4.0", "region": "us-east-1"}
    updated_meta = await service.update_agent_metadata(db_session, tenant_id, agent_id, updates)
    assert updated_meta.metadata_payload.get("environment") == "production"
    assert updated_meta.metadata_payload.get("version") == "1.4.0"
    assert updated_meta.metadata_payload.get("region") == "us-east-1"


@pytest.mark.asyncio
async def test_update_agent_metadata_strips_protected_fields(db_session: AsyncSession) -> None:
    """Test that updating metadata strips protected/forbidden system keys."""
    service = AgentMetadataService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_id,
        name="Protected Meta Agent",
        slug="protected-meta-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    updates: dict[str, Any] = {
        "status": "deactivated",
        "tenant_id": str(uuid.uuid4()),
        "raw_secret": "hacked_secret",
        "allowed_key": "valid_value",
    }
    updated_meta = await service.update_agent_metadata(db_session, tenant_id, agent_id, updates)
    assert "status" not in updated_meta.metadata_payload
    assert "tenant_id" not in updated_meta.metadata_payload
    assert "raw_secret" not in updated_meta.metadata_payload
    assert updated_meta.metadata_payload.get("allowed_key") == "valid_value"


@pytest.mark.asyncio
async def test_agent_metadata_cross_tenant_idor_rejected(db_session: AsyncSession) -> None:
    """Test cross-tenant metadata access fails closed with AgentNotFoundError (404)."""
    service = AgentMetadataService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent = Agent(
        id=agent_id,
        tenant_id=tenant_a,
        name="Tenant A Agent",
        slug="tenant-a-agent",
        agent_type="autonomous",
        status="active",
    )
    db_session.add(agent)
    await db_session.flush()

    with pytest.raises(AgentNotFoundError):
        await service.get_agent_metadata(db_session, tenant_b, agent_id)
