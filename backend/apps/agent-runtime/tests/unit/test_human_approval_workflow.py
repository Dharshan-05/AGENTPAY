"""Unit and security tests for Phase 162 Human Approval & Agent Authorization Workflow."""

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from app.application.services.human_approval_workflow_service import (
    HumanApprovalWorkflowService,
)
from app.domain.exceptions.agent_exceptions import SelfApprovalForbiddenError
from app.infrastructure.database.models.approval_request import ApprovalRequest
from app.schemas.human_approval import (
    ApprovalDecisionRequest,
    ApprovalRiskLevel,
    ApprovalStatus,
)


@pytest.fixture
def mock_db() -> MagicMock:
    """Fixture for SQLAlchemy session mock."""
    return MagicMock()


@pytest.fixture
def service() -> HumanApprovalWorkflowService:
    """Fixture for HumanApprovalWorkflowService."""
    return HumanApprovalWorkflowService()


@pytest.mark.asyncio
async def test_01_evaluate_approval_policy_thresholds(
    service: HumanApprovalWorkflowService,
) -> None:
    """1. Verify approval policy evaluation risk classification and threshold rules."""
    tenant_id = uuid.uuid4()

    # Low risk (Amount <= 50.00)
    low_res = await service.evaluate_approval_policy(tenant_id, "balance_inquiry", 20.00)
    assert low_res.risk_level == ApprovalRiskLevel.LOW
    assert low_res.requires_approval is False
    assert low_res.auto_approved is True

    # Medium risk (50.00 < Amount <= 500.00)
    med_res = await service.evaluate_approval_policy(tenant_id, "standard_payment", 150.00)
    assert med_res.risk_level == ApprovalRiskLevel.MEDIUM
    assert med_res.requires_approval is True
    assert med_res.required_approvals_count == 1

    # High risk (Amount > 500.00 or sensitive action)
    high_res = await service.evaluate_approval_policy(tenant_id, "large_transfer", 1000.00)
    assert high_res.risk_level == ApprovalRiskLevel.HIGH
    assert high_res.requires_approval is True
    assert high_res.required_approvals_count == 2


@pytest.mark.asyncio
async def test_02_self_approval_security_prevention(
    mock_db: MagicMock, service: HumanApprovalWorkflowService
) -> None:
    """2. STRICT SECURITY TEST: Verify self-approval prevention blocks requesting user from approving own transaction."""  # noqa: E501
    tenant_id = uuid.uuid4()
    approval_id = uuid.uuid4()
    user_id = uuid.uuid4()

    mock_appr = MagicMock(spec=ApprovalRequest)
    mock_appr.id = approval_id
    mock_appr.tenant_id = tenant_id
    mock_appr.requester_id = user_id
    mock_appr.agent_id = uuid.uuid4()
    mock_appr.expires_at = datetime.now(UTC) + timedelta(hours=1)
    mock_appr.status = "pending_approval"
    mock_appr.required_approvals = 1
    mock_appr.received_approvals = 0

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_appr

    decision_req = ApprovalDecisionRequest(decision="APPROVED", reason="I approve my own request.")

    with pytest.raises(SelfApprovalForbiddenError, match="Self-approval security violation"):
        await service.record_approval_decision(
            mock_db, tenant_id, approval_id, decision_req, reviewer_id=user_id
        )


@pytest.mark.asyncio
async def test_03_record_valid_approval_decision(
    mock_db: MagicMock, service: HumanApprovalWorkflowService
) -> None:
    """3. Test successful approval decision by an independent authorized reviewer."""
    tenant_id = uuid.uuid4()
    approval_id = uuid.uuid4()
    requesting_user_id = uuid.uuid4()
    reviewer_id = uuid.uuid4()

    mock_appr = MagicMock(spec=ApprovalRequest)
    mock_appr.id = approval_id
    mock_appr.tenant_id = tenant_id
    mock_appr.requesting_user_id = requesting_user_id
    mock_appr.agent_id = uuid.uuid4()
    mock_appr.expires_at = datetime.now(UTC) + timedelta(hours=1)
    mock_appr.status = "pending_approval"
    mock_appr.required_approvals = 1
    mock_appr.received_approvals = 0

    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_appr

    decision_req = ApprovalDecisionRequest(
        decision="APPROVED", reason="Independent manager approval granted."
    )

    res = await service.record_approval_decision(
        mock_db, tenant_id, approval_id, decision_req, reviewer_id=reviewer_id
    )

    assert res.decision == "APPROVED"
    assert res.reviewer_id == reviewer_id
    assert mock_appr.status == ApprovalStatus.APPROVED.value.lower()
