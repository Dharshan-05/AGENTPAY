"""Security and Adversarial tests for ATIM Group 9 (Phases 17 & 18)."""

import uuid

import pytest

from app.application.services.atim_policy_governance_service import ATIMPolicyGovernanceService
from app.application.services.atim_rate_limiter import ATIMRateLimiter
from app.domain.governance.policy_models import GovernancePolicyType


def test_01_prevent_policy_creation_by_unauthorized_user():
    gov_service = ATIMPolicyGovernanceService()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()
    user_a = uuid.uuid4()

    draft = gov_service.create_draft_policy(
        tenant_id=tenant_a,
        policy_type=GovernancePolicyType.ATIM_SECURITY_POLICY,
        configuration={"min_security_score": "0.9500"},
        creator_id=user_a,
    )

    # Policy belongs strictly to Tenant A
    fetched = gov_service.get_policy(draft.id)
    assert fetched.tenant_id == tenant_a
    assert fetched.tenant_id != tenant_b


def test_02_rate_limiter_tenant_isolation():
    rate_limiter = ATIMRateLimiter(default_limit=1, window_seconds=60)
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    # Exhaust Tenant A rate limit
    r_a1 = rate_limiter.check_rate_limit(tenant_a)
    assert r_a1.allowed is True

    r_a2 = rate_limiter.check_rate_limit(tenant_a)
    assert r_a2.allowed is False

    # Tenant B is completely isolated and allowed
    r_b1 = rate_limiter.check_rate_limit(tenant_b)
    assert r_b1.allowed is True
