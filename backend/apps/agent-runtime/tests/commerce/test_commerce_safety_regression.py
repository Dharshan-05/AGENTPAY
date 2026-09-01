"""Semantic Safety Regression Tests (Buildathon Track 01 Baseline Requirement)."""

import uuid
from decimal import Decimal
import pytest
from unittest.mock import AsyncMock

from app.application.services.atim_facade_service import ATIMFacadeService
from app.domain.atim.telemetry_models import ATIMAnalyzeRequest


@pytest.mark.asyncio
async def test_semantic_safety_baseline_greetings_and_queries():
    """Verify greetings and queries map to non-financial intents with $0.00 allocation and NOT_REQUESTED decision."""
    facade = ATIMFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    test_prompts = [
        ("HI", "GREETING"),
        ("HELLO", "GREETING"),
        ("What can you do?", "GENERAL_QUERY"),
        ("SHOW MY TRANSACTIONS", "TRANSACTION_QUERY"),
    ]

    for prompt, expected_action in test_prompts:
        req = ATIMAnalyzeRequest(tenant_id=tenant_id, agent_id=agent_id, prompt=prompt)
        res = await facade.analyze_transaction_intelligence(mock_db, req)

        assert res.proposed_intent["action"] == expected_action
        assert Decimal(str(res.proposed_intent["amount"])) == Decimal("0.00")
        assert res.final_execution_decision == "NOT_REQUESTED"
        assert res.agentguard_decision == "NOT_REQUIRED"
