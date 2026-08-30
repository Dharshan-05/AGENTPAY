"""Unit and Security Tests for Category Restriction Engine (Phase 192)."""

from __future__ import annotations

import uuid

import pytest

from app.application.services.category_restriction_service import CategoryRestrictionService
from app.schemas.category_restrictions import CategoryRestrictionEvaluationRequest


@pytest.fixture
def service() -> CategoryRestrictionService:
    return CategoryRestrictionService()


def test_01_allowed_category_passes(service: CategoryRestrictionService) -> None:
    """1. Test category in allowlist returns ALLOW."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = CategoryRestrictionEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        category="electronics",
        allowed_categories=["electronics", "groceries"],
    )

    res = service.evaluate_category_restriction(req)
    assert res.decision == "ALLOW"
    assert res.reason_code == "CATEGORY_ALLOWED"


def test_02_blocked_category_denied(service: CategoryRestrictionService) -> None:
    """2. Test category in denylist returns DENIED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = CategoryRestrictionEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        category="gambling",
        blocked_categories=["gambling", "weapons"],
    )

    res = service.evaluate_category_restriction(req)
    assert res.decision == "DENIED"
    assert res.reason_code == "CATEGORY_DENIED"


def test_03_category_case_normalization(service: CategoryRestrictionService) -> None:
    """3. Test category string case & whitespace normalization."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = CategoryRestrictionEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        category="  Electronics  ",
        allowed_categories=["electronics"],
    )

    res = service.evaluate_category_restriction(req)
    assert res.decision == "ALLOW"


def test_04_hierarchical_sub_category_matching(
    service: CategoryRestrictionService,
) -> None:
    """4. Test sub-category matching (e.g., electronics.mobile matching electronics)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = CategoryRestrictionEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        category="electronics.mobile.smartphones",
        blocked_categories=["electronics.mobile"],
    )

    res = service.evaluate_category_restriction(req)
    assert res.decision == "DENIED"
    assert res.reason_code == "CATEGORY_DENIED"
