"""Unit tests for token and item budget enforcement in SecureMemoryRetriever."""

from datetime import UTC, datetime
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.secure_memory_retriever import SecureMemoryRetriever
from app.schemas.memory import AgentMemoryRecallResponse, AgentMemoryRecallItem, AgentMemoryResponse


@pytest.mark.asyncio
async def test_01_context_budget_truncation():
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    items = []
    for i in range(20):
        mem = AgentMemoryResponse(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            agent_id=agent_id,
            memory_type="short_term",
            namespace="pref",
            key=f"item_{i}",
            value={"desc": f"This is memory item {i} with a reasonable amount of descriptive content."},
            importance=0.5 + (i * 0.01),
            confidence=1.0,
            version=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        items.append(AgentMemoryRecallItem(memory=mem, relevance_score=0.5 + (i * 0.02)))

    mock_recall_resp = AgentMemoryRecallResponse(
        query="item",
        total_recalled=20,
        results=items,
    )

    mock_mem_service = MagicMock()
    mock_mem_service.recall_memories = AsyncMock(return_value=mock_recall_resp)

    # Max memory items = 5
    retriever = SecureMemoryRetriever(memory_service=mock_mem_service, max_memory_items=5)
    db = AsyncMock()

    res = await retriever.retrieve_secure_memories(db, tenant_id, agent_id, query="item", top_k=10)

    assert len(res.memories) <= 5
    assert res.budget_truncated is True
