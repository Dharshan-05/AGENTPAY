"""Integration tests for ATIM Compliance Evidence REST APIs (Group 10)."""

import pytest


def test_01_compliance_model_imports():
    from app.domain.governance.compliance_models import ComplianceEventCategory, SecurityPermission
    assert SecurityPermission.ATIM_POLICY_READ.value == "ATIM_POLICY_READ"
    assert ComplianceEventCategory.AUTH_FAILURE.value == "AUTH_FAILURE"
