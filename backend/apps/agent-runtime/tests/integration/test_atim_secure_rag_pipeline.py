"""Integration tests for ATIM secure RAG pipeline flow."""

import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.atim_context_assembler import ATIMContextAssembler
from app.application.services.atim_security.security_classifier import SecuritySeverity
from app.application.services.secure_memory_retriever import (
    MemoryTrustLevel,
    SecureMemoryItem,
    SecureMemoryRecallResult,
)


@pytest.mark.asyncio
async def test_01_secure_rag_pipeline_end_to_end():
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_memory_item = SecureMemoryItem(
        memory_id=uuid.uuid4(),
        tenant_id=tenant_id,
        agent_id=agent_id,
        namespace="preferences",
        key="brand_preference",
        value={"brand": "Logitech"},
        memory_type="short_term",
        trust_level=MemoryTrustLevel.USER_PROVIDED,
        relevance_score=0.9,
        created_at=pytest.importorskip("datetime").datetime.now(pytest.importorskip("datetime").UTC),
    )

    mock_sec_res = SecureMemoryRecallResult(
        tenant_id=tenant_id,
        agent_id=agent_id,
        total_retrieved=1,
        memories=[mock_memory_item],
    )

    mock_retriever = MagicMock()
    mock_retriever.retrieve_secure_memories = AsyncMock(return_value=mock_sec_res)

    assembler = ATIMContextAssembler(memory_retriever=mock_retriever)
    db = AsyncMock()

    payload = await assembler.assemble_context(
        db,
        tenant_id=tenant_id,
        agent_id=agent_id,
        user_prompt="Buy Logitech keyboard for 4500 INR",
    )

    assert payload.security_decision.allowed is True
    assert payload.security_decision.severity == SecuritySeverity.NONE
    assert len(payload.recalled_memories) == 1
    assert "Logitech" in payload.recalled_memories[0]
