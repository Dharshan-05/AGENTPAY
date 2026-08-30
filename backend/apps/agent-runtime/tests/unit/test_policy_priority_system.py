"""Unit and Security Tests for Policy Priority System (Phase 196)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from app.application.services.policy_priority_service import PolicyPriorityService
from app.schemas.policy_priority import PolicyPriorityValidationRequest


@pytest.fixture
def service() -> PolicyPriorityService:
    return PolicyPriorityService()


def test_01_valid_priority_within_bounds(service: PolicyPriorityService) -> None:
    """1. Test priority within [0, 10000] passes validation."""
    tenant_id = uuid.uuid4()
    policy_id = uuid.uuid4()

    req = PolicyPriorityValidationRequest(
        tenant_id=tenant_id,
        policy_id=policy_id,
        priority=500,
    )

    res = service.validate_priority(req)
    assert res.is_valid is True
    assert res.reason_code == "PRIORITY_VALID"


def test_02_negative_priority_rejected(service: PolicyPriorityService) -> None:
    """2. Test negative priority rejected."""
    tenant_id = uuid.uuid4()
    policy_id = uuid.uuid4()

    req = PolicyPriorityValidationRequest(
        tenant_id=tenant_id,
        policy_id=policy_id,
        priority=-10,
    )

    res = service.validate_priority(req)
    assert res.is_valid is False
    assert res.reason_code == "PRIORITY_BELOW_MINIMUM"


def test_03_excessive_priority_rejected(service: PolicyPriorityService) -> None:
    """3. Test priority > 10000 rejected."""
    tenant_id = uuid.uuid4()
    policy_id = uuid.uuid4()

    req = PolicyPriorityValidationRequest(
        tenant_id=tenant_id,
        policy_id=policy_id,
        priority=99999,
    )

    res = service.validate_priority(req)
    assert res.is_valid is False
    assert res.reason_code == "PRIORITY_EXCEEDS_MAXIMUM"


def test_04_deterministic_policy_sorting(service: PolicyPriorityService) -> None:
    """4. Test policies sorted by priority DESC, then ID ASC."""
    id1 = uuid.UUID("00000000-0000-0000-0000-000000000001")
    id2 = uuid.UUID("00000000-0000-0000-0000-000000000002")

    p_low = SimpleNamespace(id=id1, priority=10)
    p_high = SimpleNamespace(id=id2, priority=500)

    sorted_list = service.sort_policies_by_priority([p_low, p_high])
    assert sorted_list[0].id == id2
    assert sorted_list[1].id == id1
