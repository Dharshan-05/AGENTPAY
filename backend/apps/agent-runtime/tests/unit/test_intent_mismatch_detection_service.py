"""Unit and Security Tests for Intent Mismatch Detection Engine (Phase 199)."""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest

from app.application.services.intent_mismatch_detection_service import (
    IntentMismatchDetectionService,
)
from app.schemas.intent_matching import IntentMatchResult, IntentMatchSignal
from app.schemas.intent_mismatch import IntentMismatchDetectionRequest


@pytest.fixture
def service() -> IntentMismatchDetectionService:
    return IntentMismatchDetectionService()


def test_01_critical_mismatch_halts_execution(
    service: IntentMismatchDetectionService,
) -> None:
    """1. Test critical mismatch (AMOUNT_MISMATCH) sets can_proceed = False."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    match_res = IntentMatchResult(
        overall_match="MISMATCH",
        match_score=Decimal("0.00"),
        signals=[
            IntentMatchSignal(
                dimension="amount",
                status="MISMATCH",
                weight=Decimal("0.25"),
                score=Decimal("0.00"),
                detail="Amount mismatch detected",
            )
        ],
    )

    req = IntentMismatchDetectionRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        match_result=match_res,
    )

    res = service.detect_mismatches(req)
    assert res.mismatch_detected is True
    assert res.severity == "CRITICAL"
    assert "AMOUNT_MISMATCH" in res.reason_codes
    assert res.can_proceed is False


def test_02_no_mismatches_can_proceed(
    service: IntentMismatchDetectionService,
) -> None:
    """2. Test exact match signals allows operation to proceed (can_proceed = True)."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    match_res = IntentMatchResult(
        overall_match="EXACT_MATCH",
        match_score=Decimal("1.00"),
        signals=[
            IntentMatchSignal(
                dimension="action",
                status="EXACT_MATCH",
                weight=Decimal("0.25"),
                score=Decimal("1.00"),
                detail="Action match",
            )
        ],
    )

    req = IntentMismatchDetectionRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        match_result=match_res,
    )

    res = service.detect_mismatches(req)
    assert res.mismatch_detected is False
    assert res.severity == "NONE"
    assert res.can_proceed is True
