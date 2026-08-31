"""Unit tests for SecureMemoryRetriever isolation and scoring."""

from datetime import UTC, datetime
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.secure_memory_retriever import (
    MemoryTrustLevel,
    SecureMemoryItem,
    SecureMemoryRetriever,
)
from app.schemas.memory import AgentMemoryRecallResponse, AgentMemoryRecallItem, AgentMemoryResponse


@pytest.mark.asyncio
async def test_01_retrieve_secure_memories_success():
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_mem = AgentMemoryResponse(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        memory_type="short_term",
        namespace="preferences",
        key="brand",
        value={"brand": "Logitech", "trust_level": "VERIFIED"},
        importance=0.8,
        confidence=1.0,
        version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    mock_recall_resp = AgentMemoryRecallResponse(
        query="Logitech",
        total_recalled=1,
        results=[AgentMemoryRecallItem(memory=mock_mem, relevance_score=0.9)],
    )

    mock_mem_service = MagicMock()
    mock_mem_service.recall_memories = AsyncMock(return_value=mock_recall_resp)

    retriever = SecureMemoryRetriever(memory_service=mock_mem_service)
    db = AsyncMock()

    res = await retriever.retrieve_secure_memories(db, tenant_id, agent_id, query="Logitech")

    assert res.total_retrieved == 1
    assert res.quarantined_count == 0
    assert len(res.memories) == 1
    assert res.memories[0].key == "brand"
    assert res.memories[0].trust_level == MemoryTrustLevel.VERIFIED
