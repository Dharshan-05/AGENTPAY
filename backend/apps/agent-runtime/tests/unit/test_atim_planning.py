"""Unit tests for ATIMPlanningService and PlanValidationService integration."""

from __future__ import annotations

from decimal import Decimal
import uuid

from app.application.services.atim_planning_service import ATIMPlanningService
from app.application.services.plan_validation_service import PlanValidationService
from app.schemas.atim import ATIMProposedIntent, ToolRiskLevel


def test_atim_planning_propose_payment_plan():
    """Test generating dynamic tool sequence for PAYMENT intent."""
    planner = ATIMPlanningService()
    validator = PlanValidationService()

    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    intent = ATIMProposedIntent(
        intent_id=uuid.uuid4(),
        action="PAYMENT",
        amount=Decimal("65000.00"),
        currency="INR",
        merchant="amazon",
    )

    proposal = planner.propose_plan(tenant_id, agent_id, intent)

    assert proposal.is_executable_proposal is True
    assert len(proposal.proposed_tools) == 5
    assert proposal.proposed_tools[4].risk_level == ToolRiskLevel.PROPOSAL_ONLY
    assert proposal.proposed_tools[4].requires_server_validation is True

    # Convert to domain AgentPlan and validate against PlanValidationService
    agent_plan = planner.to_agent_plan(proposal, intent)
    val_res = validator.validate_plan(agent_plan, target_tenant_id=tenant_id, target_agent_id=agent_id)

    assert val_res.is_valid is True
    assert val_res.execution_eligible is True
    assert len(val_res.errors) == 0
