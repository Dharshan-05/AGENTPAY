"""Unit and Security Tests for Trust Score Calculation Engine (Phase 207)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.trust_score_calculation_service import (
    TrustScoreCalculationService,
)
from app.schemas.trust_score_calculation import TrustScoreCalculationRequest


@pytest.fixture
def service() -> TrustScoreCalculationService:
    return TrustScoreCalculationService()


def test_01_perfect_trust_score(service: TrustScoreCalculationService) -> None:
    """1. Test zero risk signals produces 1.00 trust score."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = TrustScoreCalculationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = service.calculate_trust_score(req)
    assert res.trust_score == Decimal("1.00")
    assert res.trust_state == "TRUSTED"
    assert len(res.deductions) == 0


def test_02_cold_start_neutral_score(service: TrustScoreCalculationService) -> None:
    """2. Test baseline_available = False produces neutral COLD_START trust score."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    req = TrustScoreCalculationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        baseline_available=False,
    )

    res = service.calculate_trust_score(req)
    assert res.trust_score == Decimal("0.50")
    assert res.trust_state == "COLD_START"
