"""Integration tests for ATIM -> PlanValidation -> AGENTGUARD Policy Engine boundary."""

from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
import uuid
import pytest

from app.application.services.agentguard_decision_service import AgentGuardDecisionService
from app.application.services.atim_planning_service import ATIMPlanningService
from app.application.services.plan_validation_service import PlanValidationService
from app.schemas.agentguard_decision import AgentGuardDecisionRequest
from app.schemas.atim import ATIMProposedIntent


@pytest.mark.asyncio
async def test_atim_agentguard_security_boundary_enforces_policy():
    """Test that AGENTGUARD decision engine remains authoritative over LLM proposals."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    # 1. ATIM proposes intent
    llm_proposed_intent = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PAYMENT",
        amount=Decimal("1000000.00"),  # $1,000,000 purchase attempt
        currency="USD",
        merchant="super_luxury_store",
    )

    # 2. ATIM generates proposed plan & validates DAG
    planner = ATIMPlanningService()
    plan_validator = PlanValidationService()

    proposal = planner.propose_plan(tenant_id, agent_id, llm_proposed_intent)
    agent_plan = planner.to_agent_plan(proposal, llm_proposed_intent)
    val_res = plan_validator.validate_plan(agent_plan, target_tenant_id=tenant_id, target_agent_id=agent_id)
    assert val_res.is_valid is True

    # 3. Mock DB Session for AGENTGUARD Policy Evaluation
    db_mock = AsyncMock()
    mock_agent = MagicMock()
    mock_agent.id = agent_id
    mock_agent.tenant_id = tenant_id
    mock_agent.status = "active"
    mock_agent.deleted_at = None

    mock_merchant = MagicMock()
    mock_merchant.id = uuid.uuid4()
    mock_merchant.tenant_id = tenant_id
    mock_merchant.slug = "super_luxury_store"
    mock_merchant.deleted_at = None

    mock_rule = MagicMock()
    mock_rule.id = uuid.uuid4()
    mock_rule.rule_type = "max_amount"
    mock_rule.rule_name = "Max Amount Rule"
    mock_rule.config = {"max_amount": "50000.00", "currency": "USD"}
    mock_rule.action = "DENY"
    mock_rule.is_active = True

    mock_policy = MagicMock()
    mock_policy.id = uuid.uuid4()
    mock_policy.tenant_id = tenant_id
    mock_policy.slug = "max_limit_policy"
    mock_policy.status = "active"
    mock_policy.priority = 100
    mock_policy.enforcement_mode = "block"
    mock_policy.deleted_at = None
    mock_policy.starts_at = None
    mock_policy.ends_at = None
    mock_policy.configuration = {"maximum_transaction_amount": "50000.00"}
    mock_policy.rules = [mock_rule]

    def mock_execute(stmt, *args, **kwargs):
        stmt_str = str(stmt).lower()
        res = MagicMock()
        sc = MagicMock()
        if "security_policies" in stmt_str:
            sc.all.return_value = [mock_policy]
            sc.first.return_value = mock_policy
            res.scalar_one_or_none.return_value = mock_policy
        elif "merchants" in stmt_str:
            sc.all.return_value = [mock_merchant]
            sc.first.return_value = mock_merchant
            res.scalar_one_or_none.return_value = mock_merchant
        elif "from agents" in stmt_str or "agents." in stmt_str:
            sc.all.return_value = [mock_agent]
            sc.first.return_value = mock_agent
            res.scalar_one_or_none.return_value = mock_agent
        else:
            sc.all.return_value = []
            sc.first.return_value = None
            res.scalar_one_or_none.return_value = None
        res.scalars.return_value = sc
        return res

    db_mock.execute.side_effect = mock_execute







    agentguard = AgentGuardDecisionService()
    decision_req = AgentGuardDecisionRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        requested_action="payment_initiation",
        amount=Decimal("1000000.00"),
        currency="USD",
        merchant_id=uuid.uuid4(),
        category="luxury",
    )

    decision_res = await agentguard.evaluate_agentguard_decision(
        db=db_mock,
        request=decision_req,
    )

    # 4. Verify AGENTGUARD decision is DENIED or REQUIRE_APPROVAL (NOT blindly allowed)
    assert decision_res.decision in ("DENIED", "REQUIRE_APPROVAL")
    assert decision_res.can_proceed is False or decision_res.requires_approval is True

