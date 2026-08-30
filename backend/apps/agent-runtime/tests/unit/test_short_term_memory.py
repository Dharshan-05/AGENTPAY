"""Unit & Security Tests for Short-Term Working Memory (Phase 154)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_memory_service import AgentMemoryService
from app.application.services.short_term_memory_service import (
    MAX_SESSION_WORKING_MEMORY_VARIABLES,
    ShortTermMemoryService,
)
from app.domain.exceptions.agent_exceptions import MemoryQuotaExceededError
from app.schemas.memory import (
    AgentMemoryResponse,
    ShortTermMemorySetRequest,
)


@pytest.mark.asyncio
async def test_01_set_and_get_working_memory_variable() -> None:
    """Test setting and getting a short-term session working memory variable."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    mock_mem_service = AsyncMock(spec=AgentMemoryService)
    mock_mem_service.list_memories.return_value = []

    expected_resp = AgentMemoryResponse(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        session_id=session_id,
        task_id=None,
        memory_type="short_term",
        namespace="short_term_working_memory",
        key="temp_cart_total",
        value={"amount": 49.99, "currency": "USD"},
        importance=0.8,
        confidence=1.0,
        version=1,
        expires_at=None,
        created_at=MagicMock(),
        updated_at=MagicMock(),
    )
    mock_mem_service.create_memory.return_value = expected_resp

    service = ShortTermMemoryService(memory_service=mock_mem_service)

    req = ShortTermMemorySetRequest(
        key="temp_cart_total",
        value={"amount": 49.99, "currency": "USD"},
        ttl_seconds=3600,
    )

    mock_db = AsyncMock()
    result = await service.set_variable(mock_db, tenant_id, agent_id, user_id, session_id, req)

    assert result.key == "temp_cart_total"
    assert result.value == {"amount": 49.99, "currency": "USD"}
    assert mock_mem_service.create_memory.called


@pytest.mark.asyncio
async def test_02_working_memory_quota_exceeded() -> None:
    """Test that setting variables beyond MAX_SESSION_WORKING_MEMORY_VARIABLES raises error."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    mock_memories = [
        MagicMock(key=f"var_{i}", spec=[f for f in dir(AgentMemoryResponse) if f != "__fields__"])
        for i in range(MAX_SESSION_WORKING_MEMORY_VARIABLES)
    ]

    mock_mem_service = AsyncMock(spec=AgentMemoryService)
    mock_mem_service.list_memories.return_value = mock_memories

    service = ShortTermMemoryService(memory_service=mock_mem_service)

    req = ShortTermMemorySetRequest(
        key="new_overflow_variable",
        value={"test": True},
    )

    mock_db = AsyncMock()
    with pytest.raises(MemoryQuotaExceededError):
        await service.set_variable(mock_db, tenant_id, agent_id, user_id, session_id, req)


@pytest.mark.asyncio
async def test_03_clear_working_memory() -> None:
    """Test clearing all working memory variables for a session."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_id = uuid.uuid4()

    mem1 = MagicMock(id=uuid.uuid4(), key="var1")
    mem2 = MagicMock(id=uuid.uuid4(), key="var2")

    mock_mem_service = AsyncMock(spec=AgentMemoryService)
    mock_mem_service.list_memories.return_value = [mem1, mem2]

    service = ShortTermMemoryService(memory_service=mock_mem_service)

    mock_db = AsyncMock()
    cleared = await service.clear_working_memory(
        mock_db, tenant_id, agent_id, user_id, session_id=session_id
    )

    assert cleared == 2
    assert mock_mem_service.delete_memory.call_count == 2
