"""Unit and Security Tests for Agent Security History Engine (Phase 210)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from app.application.services.agent_security_history_service import (
    AgentSecurityHistoryService,
)
from app.schemas.agent_violations import AgentViolationQueryResponse


@pytest.fixture
def service() -> AgentSecurityHistoryService:
    mock_v_service = AsyncMock()
    return AgentSecurityHistoryService(violation_service=mock_v_service)


@pytest.mark.asyncio
async def test_01_get_security_history_summary(
    service: AgentSecurityHistoryService,
) -> None:
    """1. Test retrieving security history summary."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    service.violation_service.get_agent_violations.return_value = (  # type: ignore[attr-defined]
        AgentViolationQueryResponse(
            tenant_id=tenant_id,
            agent_id=agent_id,
            violations=[],
            total_count=0,
        )
    )

    mock_db = AsyncMock()
    res = await service.get_security_history_summary(mock_db, tenant_id, agent_id)
    assert res.total_events == 0
    assert res.violation_count == 0
