"""Unit tests for ATIM Administrative Policy Governance Service (Phase 17 / Group 9)."""

import uuid

import pytest

from app.application.services.atim_policy_governance_service import ATIMPolicyGovernanceService
from app.domain.governance.policy_models import GovernancePolicyStatus, GovernancePolicyType


@pytest.fixture
def governance_service():
    return ATIMPolicyGovernanceService()


def test_01_create_draft_policy(governance_service):
    tenant_id = uuid.uuid4()
    creator_id = uuid.uuid4()

    record = governance_service.create_draft_policy(
        tenant_id=tenant_id,
        policy_type=GovernancePolicyType.ATIM_SECURITY_POLICY,
        configuration={"min_security_score": "0.9500"},
        creator_id=creator_id,
    )

    assert record.tenant_id == tenant_id
    assert record.policy_type == GovernancePolicyType.ATIM_SECURITY_POLICY
    assert record.version == 1
    assert record.status == GovernancePolicyStatus.DRAFT
    assert record.signature is not None


def test_02_submit_and_approve_policy_four_eyes(governance_service):
    tenant_id = uuid.uuid4()
    creator_id = uuid.uuid4()
    approver_id = uuid.uuid4()

    draft = governance_service.create_draft_policy(
        tenant_id=tenant_id,
        policy_type=GovernancePolicyType.ATIM_SECURITY_POLICY,
        configuration={"min_security_score": "0.9500"},
        creator_id=creator_id,
    )

    submitted = governance_service.submit_policy(draft.id, actor_id=creator_id)
    assert submitted.status == GovernancePolicyStatus.PENDING_APPROVAL

    approved = governance_service.approve_policy(draft.id, approver_id=approver_id)
    assert approved.status == GovernancePolicyStatus.APPROVED
    assert approved.approved_by == approver_id


def test_03_four_eyes_violation_creator_cannot_approve(governance_service):
    tenant_id = uuid.uuid4()
    creator_id = uuid.uuid4()

    draft = governance_service.create_draft_policy(
        tenant_id=tenant_id,
        policy_type=GovernancePolicyType.ATIM_SECURITY_POLICY,
        configuration={"min_security_score": "0.9500"},
        creator_id=creator_id,
    )
    governance_service.submit_policy(draft.id, actor_id=creator_id)

    # Attempting to approve own submission must raise PermissionError
    with pytest.raises(PermissionError) as exc_info:
        governance_service.approve_policy(draft.id, approver_id=creator_id)

    assert "Four-Eyes Violation" in str(exc_info.value)


def test_04_activate_policy_retires_old_version(governance_service):
    tenant_id = uuid.uuid4()
    c1, a1 = uuid.uuid4(), uuid.uuid4()
    c2, a2 = uuid.uuid4(), uuid.uuid4()

    # Policy 1 -> Active
    p1 = governance_service.create_draft_policy(tenant_id, GovernancePolicyType.ATIM_RATE_LIMIT_POLICY, {"limit": 100}, c1)
    governance_service.submit_policy(p1.id, c1)
    governance_service.approve_policy(p1.id, a1)
    governance_service.activate_policy(p1.id, a1)
    assert governance_service.get_policy(p1.id).status == GovernancePolicyStatus.ACTIVE

    # Policy 2 -> Active (should retire Policy 1)
    p2 = governance_service.create_draft_policy(tenant_id, GovernancePolicyType.ATIM_RATE_LIMIT_POLICY, {"limit": 200}, c2)
    governance_service.submit_policy(p2.id, c2)
    governance_service.approve_policy(p2.id, a2)
    governance_service.activate_policy(p2.id, a2)

    assert governance_service.get_policy(p1.id).status == GovernancePolicyStatus.RETIRED
    assert governance_service.get_policy(p2.id).status == GovernancePolicyStatus.ACTIVE
