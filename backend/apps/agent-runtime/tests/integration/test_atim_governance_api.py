"""Integration tests for ATIM Governance & Rate Limit APIs (Group 9)."""

import pytest


def test_01_governance_policy_model_import():
    from app.domain.governance.policy_models import GovernancePolicyStatus, GovernancePolicyType
    assert GovernancePolicyStatus.ACTIVE.value == "ACTIVE"
    assert GovernancePolicyType.ATIM_SECURITY_POLICY.value == "ATIM_SECURITY_POLICY"
