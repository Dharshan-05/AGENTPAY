"""Integration tests for ATIM tenant memory isolation security invariant."""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.secure_memory_retriever import SecureMemoryRetriever
from app.schemas.memory import AgentMemoryRecallResponse, AgentMemoryRecallItem, AgentMemoryResponse


@pytest.mark.asyncio
async def test_01_tenant_isolation_enforced():
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    agent_a = uuid.uuid4()
    agent_b = uuid.uuid4()

    mock_mem_service = MagicMock()
    # Mock recall_memories verifies that querying for tenant_a only receives tenant_a params
    async def fake_recall(db, tenant_id, agent_id, request):
        assert tenant_id == tenant_a
        assert agent_id == agent_a
        return AgentMemoryRecallResponse(
            query=request.query,
            total_recalled=0,
            results=[],
        )

    mock_mem_service.recall_memories = AsyncMock(side_effect=fake_recall)

    retriever = SecureMemoryRetriever(memory_service=mock_mem_service)
    db = AsyncMock()

    res = await retriever.retrieve_secure_memories(db, tenant_id=tenant_a, agent_id=agent_a, query="Logitech")
    assert res.tenant_id == tenant_a
    assert res.agent_id == agent_a
    assert res.total_retrieved == 0
