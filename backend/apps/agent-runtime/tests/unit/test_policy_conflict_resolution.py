"""Unit and Security Tests for Policy Conflict Resolution Engine (Phase 195)."""

from __future__ import annotations

import uuid

import pytest

from app.application.services.policy_conflict_resolution_service import (
    PolicyConflictResolutionService,
)
from app.schemas.policy_conflict_resolution import PolicyCandidate


@pytest.fixture
def service() -> PolicyConflictResolutionService:
    return PolicyConflictResolutionService()


def test_01_deny_overrides_allow(service: PolicyConflictResolutionService) -> None:
    """1. Test DENY policy overrides ALLOW policy regardless of priority order."""
    p1 = uuid.uuid4()
    p2 = uuid.uuid4()

    candidates = [
        PolicyCandidate(
            policy_id=p1,
            decision="ALLOW",
            priority=200,
            reason_code="POLICY_ALLOWED",
        ),
        PolicyCandidate(
            policy_id=p2,
            decision="DENIED",
            priority=100,
            reason_code="BLOCKED_BY_POLICY",
        ),
    ]

    res = service.resolve_conflicts(candidates)
    assert res.decision == "DENIED"
    assert res.winning_policy_id == p2
    assert res.conflict_detected is True


def test_02_require_approval_overrides_allow(
    service: PolicyConflictResolutionService,
) -> None:
    """2. Test REQUIRE_APPROVAL policy overrides ALLOW policy."""
    p1 = uuid.uuid4()
    p2 = uuid.uuid4()

    candidates = [
        PolicyCandidate(
            policy_id=p1,
            decision="ALLOW",
            priority=100,
            reason_code="POLICY_ALLOWED",
        ),
        PolicyCandidate(
            policy_id=p2,
            decision="REQUIRE_APPROVAL",
            priority=100,
            reason_code="APPROVAL_REQUIRED",
        ),
    ]

    res = service.resolve_conflicts(candidates)
    assert res.decision == "REQUIRE_APPROVAL"
    assert res.winning_policy_id == p2


def test_03_no_candidates_returns_no_applicable(
    service: PolicyConflictResolutionService,
) -> None:
    """3. Test empty candidates returns NO_APPLICABLE_POLICY."""
    res = service.resolve_conflicts([])
    assert res.decision == "NO_APPLICABLE_POLICY"
    assert res.conflict_detected is False
