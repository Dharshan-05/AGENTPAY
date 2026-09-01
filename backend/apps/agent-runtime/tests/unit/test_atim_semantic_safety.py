"""ATIM LLM Semantic Intent Safety Verification Unit Tests."""

import pytest
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

from app.application.services.atim_facade_service import ATIMFacadeService
from app.application.services.intent_extraction_service import RuleBasedIntentExtractorProvider
from app.domain.atim.telemetry_models import ATIMAnalyzeRequest


@pytest.mark.asyncio
async def test_semantic_safety_greeting_hi():
    """Verify 'HI' is classified as GREETING with zero financial execution."""
    facade = ATIMFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = ATIMAnalyzeRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        prompt="HI",
    )
    mock_db = AsyncMock()

    res = await facade.analyze_transaction_intelligence(mock_db, req)

    assert res.prompt_security_blocked is False
    assert res.proposed_intent["action"] == "GREETING"
    assert Decimal(str(res.proposed_intent["amount"])) == Decimal("0.00")
    assert res.final_execution_decision in ("NOT_REQUESTED", "NONE")
    assert res.agentguard_decision in ("NOT_REQUIRED", "ALLOWED")


@pytest.mark.asyncio
async def test_semantic_safety_greeting_hello():
    """Verify 'HELLO' is classified as GREETING with zero financial execution."""
    facade = ATIMFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = ATIMAnalyzeRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        prompt="HELLO",
    )
    mock_db = AsyncMock()

    res = await facade.analyze_transaction_intelligence(mock_db, req)

    assert res.proposed_intent["action"] == "GREETING"
    assert Decimal(str(res.proposed_intent["amount"])) == Decimal("0.00")
    assert res.final_execution_decision in ("NOT_REQUESTED", "NONE")


@pytest.mark.asyncio
async def test_semantic_safety_general_query():
    """Verify 'WHAT CAN YOU DO?' is classified as GENERAL_QUERY with zero financial execution."""
    facade = ATIMFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = ATIMAnalyzeRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        prompt="WHAT CAN YOU DO?",
    )
    mock_db = AsyncMock()

    res = await facade.analyze_transaction_intelligence(mock_db, req)

    assert res.proposed_intent["action"] == "GENERAL_QUERY"
    assert Decimal(str(res.proposed_intent["amount"])) == Decimal("0.00")
    assert res.final_execution_decision in ("NOT_REQUESTED", "NONE")


@pytest.mark.asyncio
async def test_semantic_safety_transaction_query():
    """Verify 'SHOW MY TRANSACTIONS' is classified as TRANSACTION_QUERY with zero financial execution."""
    facade = ATIMFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = ATIMAnalyzeRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        prompt="SHOW MY TRANSACTIONS",
    )
    mock_db = AsyncMock()

    res = await facade.analyze_transaction_intelligence(mock_db, req)

    assert res.proposed_intent["action"] == "TRANSACTION_QUERY"
    assert Decimal(str(res.proposed_intent["amount"])) == Decimal("0.00")
    assert res.final_execution_decision in ("NOT_REQUESTED", "NONE")


@pytest.mark.asyncio
async def test_semantic_safety_explicit_purchase_request():
    """Verify explicit purchase request extracts details but LLM has zero execution authority."""
    facade = ATIMFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = ATIMAnalyzeRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        prompt="BUY A LAPTOP FOR ₹50000",
    )
    mock_db = AsyncMock()

    res = await facade.analyze_transaction_intelligence(mock_db, req)

    assert res.proposed_intent["action"] in ("PURCHASE", "PAYMENT")
    assert Decimal(str(res.proposed_intent["amount"])) == Decimal("50000.00")
    assert res.proposed_intent["currency"] == "INR"
    assert res.final_execution_decision in ("DENY", "REVIEW", "ALLOW")


@pytest.mark.asyncio
async def test_semantic_safety_rule_provider_greetings():
    """Verify RuleBasedIntentExtractorProvider extracts greeting actions."""
    provider = RuleBasedIntentExtractorProvider()

    for word in ["HI", "HELLO", "HEY", "GOOD MORNING", "THANK YOU", "PING"]:
        intent = await provider.extract(word, {})
        assert intent.action == "greeting"
        assert intent.confidence == Decimal("1.00")
