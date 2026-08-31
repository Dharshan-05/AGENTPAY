"""Failure Injection Test Suite for ATIM Group 3 verifying fail-closed invariants (Phase 7)."""

from decimal import Decimal
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.services.atim_execution_decision_service import ATIMExecutionDecisionService
from app.schemas.atim import ATIMPlanProposal, ATIMProposedIntent
from tests.e2e.test_atim_end_to_end import create_test_plan


@pytest.fixture
def mock_proposal():
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    intent = ATIMProposedIntent(action="purchase", amount=Decimal("200.00"), currency="USD")
    plan = create_test_plan(tenant_id, agent_id, action="prepare_payment", amount=200.0)
    return tenant_id, agent_id, ATIMPlanProposal(proposed_intent=intent, plan=plan)


@pytest.mark.asyncio
async def test_01_agentguard_failure_fails_closed(mock_proposal):
    tenant_id, agent_id, proposal = mock_proposal
    db = AsyncMock()

    mock_ag = MagicMock()
    mock_ag.evaluate_proposal = AsyncMock(side_effect=Exception("AGENTGUARD DB Connection Timeout"))

    decision_service = ATIMExecutionDecisionService(agentguard_integration=mock_ag)

    with pytest.raises(Exception):
        await decision_service.evaluate_proposal_execution(db, tenant_id, agent_id, proposal)


@pytest.mark.asyncio
async def test_02_fraudguard_failure_fails_closed(mock_proposal):
    tenant_id, agent_id, proposal = mock_proposal
    db = AsyncMock()

    mock_ag = MagicMock()
    mock_ag.evaluate_proposal = AsyncMock(
        return_value=MagicMock(
            allowed=True,
            requires_human_approval=False,
            decision_code="ALLOWED",
            reason_code="ALLOWED",
            evaluated_amount=Decimal("200.00"),
            evaluated_currency="USD",
        )
    )

    mock_fg = MagicMock()
    mock_fg.evaluate_fraud_risk = AsyncMock(
        side_effect=Exception("FraudGuard ML Model Inference Error")
    )

    decision_service = ATIMExecutionDecisionService(
        agentguard_integration=mock_ag, fraudguard_integration=mock_fg
    )

    with pytest.raises(Exception):
        await decision_service.evaluate_proposal_execution(db, tenant_id, agent_id, proposal)


@pytest.mark.asyncio
async def test_03_hitl_failure_fails_closed(mock_proposal):
    tenant_id, agent_id, proposal = mock_proposal
    db = AsyncMock()

    mock_hitl = MagicMock()
    mock_hitl.evaluate_approval_policy = AsyncMock(side_effect=Exception("HITL Policy DB Error"))

    decision_service = ATIMExecutionDecisionService(human_approval_service=mock_hitl)

    with pytest.raises(Exception):
        await decision_service.evaluate_proposal_execution(db, tenant_id, agent_id, proposal)
