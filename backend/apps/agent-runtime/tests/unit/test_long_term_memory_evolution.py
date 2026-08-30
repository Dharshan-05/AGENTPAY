"""Unit and Security Tests for Long-Term Memory Evolution (Phase 155)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_memory_service import AgentMemoryService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.infrastructure.database.models.agent_memory import AgentMemory
from app.schemas.memory import (
    AgentMemoryRecallRequest,
    MemoryRecallWeights,
    MemoryStatus,
)


@pytest.fixture
def service() -> AgentMemoryService:
    audit_mock = AsyncMock()
    return AgentMemoryService(audit_service=audit_mock)


@pytest.mark.asyncio
async def test_01_archive_and_restore_memory_success(
    service: AgentMemoryService,
) -> None:
    """1. Test archiving and restoring long-term memory state."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()
    memory_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    mock_agent.id = agent_id
    mock_agent.tenant_id = tenant_id

    mock_memory = MagicMock(spec=AgentMemory)
    mock_memory.id = memory_id
    mock_memory.tenant_id = tenant_id
    mock_memory.agent_id = agent_id
    mock_memory.session_id = None
    mock_memory.task_id = None
    mock_memory.memory_type = "long_term"
    mock_memory.namespace = "default"
    mock_memory.key = "user_preference"
    mock_memory.value = {"preference": "dark_mode", "status": "active"}
    mock_memory.importance = 0.8
    mock_memory.confidence = 1.0
    mock_memory.version = 1
    mock_memory.expires_at = None
    mock_memory.created_at = datetime.now(UTC)
    mock_memory.updated_at = datetime.now(UTC)

    mock_res_agent = MagicMock()
    mock_res_agent.scalar_one_or_none.return_value = mock_agent

    mock_res_mem = MagicMock()
    mock_res_mem.scalar_one_or_none.return_value = mock_memory

    mock_db = AsyncMock()
    mock_db.execute.side_effect = [mock_res_agent, mock_res_mem]

    # Test Archive
    archived_resp = await service.archive_memory(mock_db, tenant_id, agent_id, user_id, memory_id)
    assert archived_resp.id == memory_id
    assert mock_memory.value["status"] == MemoryStatus.ARCHIVED.value

    # Reset side effect for restore test
    mock_db.execute.side_effect = [mock_res_agent, mock_res_mem]

    # Test Restore
    restored_resp = await service.restore_memory(mock_db, tenant_id, agent_id, user_id, memory_id)
    assert restored_resp.id == memory_id
    assert mock_memory.value["status"] == MemoryStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_02_weighted_memory_recall(
    service: AgentMemoryService,
) -> None:
    """2. Test multi-factor weighted memory recall and relevance ranking."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    mock_agent.id = agent_id
    mock_agent.tenant_id = tenant_id

    m1 = MagicMock(spec=AgentMemory)
    m1.id = uuid.uuid4()
    m1.tenant_id = tenant_id
    m1.agent_id = agent_id
    m1.session_id = None
    m1.task_id = None
    m1.memory_type = "declarative"
    m1.namespace = "default"
    m1.key = "preferred_currency"
    m1.value = {"currency": "USD", "status": "active"}
    m1.importance = 0.9
    m1.confidence = 1.0
    m1.version = 1
    m1.expires_at = None
    m1.created_at = datetime.now(UTC)
    m1.updated_at = datetime.now(UTC)

    m2 = MagicMock(spec=AgentMemory)
    m2.id = uuid.uuid4()
    m2.tenant_id = tenant_id
    m2.agent_id = agent_id
    m2.session_id = None
    m2.task_id = None
    m2.memory_type = "episodic"
    m2.namespace = "default"
    m2.key = "last_purchase"
    m2.value = {"item": "laptop", "status": "active"}
    m2.importance = 0.4
    m2.confidence = 0.8
    m2.version = 1
    m2.expires_at = None
    m2.created_at = datetime.now(UTC)
    m2.updated_at = datetime.now(UTC)

    mock_res_agent = MagicMock()
    mock_res_agent.scalar_one_or_none.return_value = mock_agent

    mock_res_memories = MagicMock()
    mock_res_memories.scalars.return_value.all.return_value = [m1, m2]

    mock_db = AsyncMock()
    mock_db.execute.side_effect = [mock_res_agent, mock_res_memories]

    req = AgentMemoryRecallRequest(
        query="currency",
        min_relevance=0.2,
        top_k=5,
        weights=MemoryRecallWeights(importance_weight=0.4, decay_weight=0.3),
    )

    res = await service.recall_memories(mock_db, tenant_id, agent_id, req)
    assert res.total_recalled >= 1
    assert res.results[0].memory.key == "preferred_currency"
    assert res.results[0].relevance_score > 0.5


@pytest.mark.asyncio
async def test_03_tenant_isolation_memory_security(
    service: AgentMemoryService,
) -> None:
    """3. SECURITY TEST: Verify cross-tenant memory access is strictly rejected."""
    tenant_id_a = uuid.uuid4()
    agent_id_a = uuid.uuid4()
    memory_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_res_agent = MagicMock()
    mock_res_agent.scalar_one_or_none.return_value = None

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_res_agent

    with pytest.raises(AgentNotFoundError):
        await service.archive_memory(mock_db, tenant_id_a, agent_id_a, user_id, memory_id)
