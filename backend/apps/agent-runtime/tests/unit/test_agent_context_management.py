"""Unit & Security Tests for Agent Context Management (Phase 152)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.agent_context_service import AgentContextService
from app.domain.exceptions.agent_exceptions import AgentNotFoundError
from app.infrastructure.database.models.agent import Agent
from app.schemas.context import (
    ContextAssemblyRequest,
    ContextBudget,
    ContextItem,
    ContextScope,
)


@pytest.mark.asyncio
async def test_01_assemble_context_success() -> None:
    """Test successful context assembly with priority ordering and secret sanitization."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    mock_agent.id = agent_id
    mock_agent.tenant_id = tenant_id
    mock_agent.name = "PaymentAgent"
    mock_agent.agent_type = "autonomous"
    mock_agent.status = "active"

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_agent

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_res

    mock_trust = AsyncMock()
    mock_trust.get_agent_trust.return_value = MagicMock(trust_score=85.0)
    mock_audit = AsyncMock()

    service = AgentContextService(trust_service=mock_trust, audit_service=mock_audit)

    req = ContextAssemblyRequest(
        user_prompt="Execute payment with Bearer secret_token_12345",
        budget=ContextBudget(max_tokens=4096),
    )

    response = await service.assemble_agent_context(mock_db, tenant_id, agent_id, req)

    assert response.agent_id == agent_id
    assert response.tenant_id == tenant_id
    assert response.total_tokens > 0
    assert response.total_items >= 3
    assert response.truncated_items_count == 0

    # Verify secret sanitization in prompt item
    user_item = next(i for i in response.items if i.scope == ContextScope.USER)
    assert "secret_token_12345" not in user_item.content
    assert "[REDACTED_SECRET]" in user_item.content


@pytest.mark.asyncio
async def test_02_context_truncation_on_budget_exceeded() -> None:
    """Test that context assembly truncates lower priority items when budget is tight."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_agent = MagicMock(spec=Agent)
    mock_agent.id = agent_id
    mock_agent.tenant_id = tenant_id
    mock_agent.name = "PaymentAgent"
    mock_agent.agent_type = "autonomous"
    mock_agent.status = "active"

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = mock_agent

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_res

    service = AgentContextService(trust_service=AsyncMock(), audit_service=AsyncMock())

    custom_items = [
        ContextItem(
            item_id="item-low-1",
            scope=ContextScope.TOOL,
            priority=10,
            content="Tool documentation item " * 50,
            estimated_tokens=500,
        ),
        ContextItem(
            item_id="item-low-2",
            scope=ContextScope.RUNTIME,
            priority=5,
            content="Runtime metrics item " * 50,
            estimated_tokens=500,
        ),
    ]

    # Strict low token budget
    req = ContextAssemblyRequest(
        custom_items=custom_items,
        budget=ContextBudget(max_tokens=256, max_items=10),
    )

    response = await service.assemble_agent_context(mock_db, tenant_id, agent_id, req)

    # SYSTEM and AGENT_IDENTITY should be preserved, lower priority truncated
    scopes = [i.scope for i in response.items]
    assert ContextScope.SYSTEM in scopes
    assert ContextScope.AGENT_IDENTITY in scopes
    assert response.truncated_items_count >= 1


@pytest.mark.asyncio
async def test_03_context_assembly_cross_tenant_idor() -> None:
    """Test that cross-tenant context assembly raises AgentNotFoundError."""
    tenant_b = uuid.uuid4()
    agent_id = uuid.uuid4()

    mock_res = MagicMock()
    mock_res.scalar_one_or_none.return_value = None

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_res

    service = AgentContextService(trust_service=AsyncMock(), audit_service=AsyncMock())

    req = ContextAssemblyRequest()

    with pytest.raises(AgentNotFoundError):
        await service.assemble_agent_context(mock_db, tenant_b, agent_id, req)
