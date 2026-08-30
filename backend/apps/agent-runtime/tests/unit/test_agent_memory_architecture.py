"""Unit & Security Tests for Unified Agent Memory Architecture (Phase 153)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_memory_service import AgentMemoryService
from app.domain.exceptions.agent_exceptions import (
    AgentNotFoundError,
)
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_memory import AgentMemory
from app.schemas.memory import (
    AgentMemoryCreateRequest,
    AgentMemoryUpdateRequest,
    MemoryType,
)


@pytest.mark.asyncio
async def test_01_create_memory_success() -> None:
    """Test successful creation of unified memory record."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    mock_agent.id = agent_id
    mock_agent.tenant_id = tenant_id

    mock_db = AsyncMock()

    # First call: agent exists; second call: memory does not exist yet
    mock_res_agent = MagicMock()
    mock_res_agent.scalar_one_or_none.return_value = mock_agent

    mock_res_mem = MagicMock()
    mock_res_mem.scalar_one_or_none.return_value = None

    mock_db.execute.side_effect = [mock_res_agent, mock_res_mem]

    audit_mock = AsyncMock()
    service = AgentMemoryService(audit_service=audit_mock)

    req = AgentMemoryCreateRequest(
        key="user_preference_currency",
        value={"currency": "USD", "auto_convert": True},
        namespace="preferences",
        memory_type=MemoryType.SHORT_TERM,
        importance=0.9,
    )

    response = await service.create_memory(mock_db, tenant_id, agent_id, user_id, req)

    assert response.agent_id == agent_id
    assert response.tenant_id == tenant_id
    assert response.key == "user_preference_currency"
    assert response.value == {"currency": "USD", "auto_convert": True}
    assert response.version == 1
    assert mock_db.add.called
    assert mock_db.commit.called


@pytest.mark.asyncio
async def test_02_update_memory_and_version_increment() -> None:
    """Test updating existing memory record increments version counter."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()
    memory_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    mock_memory = MagicMock(spec=AgentMemory)
    mock_memory.id = memory_id
    mock_memory.tenant_id = tenant_id
    mock_memory.agent_id = agent_id
    mock_memory.session_id = None
    mock_memory.task_id = None
    mock_memory.memory_type = "short_term"
    mock_memory.namespace = "default"
    mock_memory.key = "active_step"
    mock_memory.value = {"step": 1}
    mock_memory.importance = 0.5
    mock_memory.confidence = 1.0
    mock_memory.version = 1
    mock_memory.expires_at = None
    mock_memory.created_at = datetime.now(UTC)
    mock_memory.updated_at = datetime.now(UTC)

    mock_db = AsyncMock()
    mock_res_agent = MagicMock()
    mock_res_agent.scalar_one_or_none.return_value = mock_agent

    mock_res_mem = MagicMock()
    mock_res_mem.scalar_one_or_none.return_value = mock_memory

    mock_db.execute.side_effect = [mock_res_agent, mock_res_mem]

    service = AgentMemoryService(audit_service=AsyncMock())

    upd_req = AgentMemoryUpdateRequest(
        value={"step": 2},
        importance=0.8,
    )

    response = await service.update_memory(
        mock_db, tenant_id, agent_id, user_id, memory_id, upd_req
    )

    assert mock_memory.version == 2
    assert response.version == 2
    assert response.value == {"step": 2}


@pytest.mark.asyncio
async def test_03_memory_cross_tenant_idor() -> None:
    """Test cross-tenant memory access raises AgentNotFoundError or MemoryNotFoundError."""
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()
    memory_id = uuid.uuid4()

    mock_db = AsyncMock()
    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_res

    service = AgentMemoryService(audit_service=AsyncMock())

    with pytest.raises(AgentNotFoundError):
        await service.get_memory(mock_db, tenant_b, agent_id, memory_id)
