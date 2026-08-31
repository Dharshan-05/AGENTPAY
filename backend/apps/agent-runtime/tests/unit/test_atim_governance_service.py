"""Unit tests for ATIM Governance Service (Phase 11 / Group 6)."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
import uuid

import pytest

from app.application.services.atim_governance_service import ATIMGovernanceService
from app.domain.governance.models import GovernanceStatus


@pytest.fixture
def governance_service():
    return ATIMGovernanceService()


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_01_promote_model_admin_success(governance_service, mock_db):
    res = await governance_service.promote_model(
        db=mock_db,
        model_id="anthropic/claude-3-5-sonnet-20241022",
        target_status=GovernanceStatus.APPROVED,
        security_score=Decimal("0.9800"),
        decision_reason="Passed all security and evaluation benchmarks",
        actor_id=uuid.uuid4(),
        actor_type="ADMIN",
    )

    assert res.model_id == "anthropic/claude-3-5-sonnet-20241022"
    assert res.new_status == GovernanceStatus.APPROVED
    assert res.security_score == Decimal("0.9800")
    assert mock_db.add.called


@pytest.mark.asyncio
async def test_02_promote_model_security_floor_violation_forces_rejection(governance_service, mock_db):
    res = await governance_service.promote_model(
        db=mock_db,
        model_id="unsafe_model",
        target_status=GovernanceStatus.APPROVED,
        security_score=Decimal("0.9000"),  # Below 0.95 floor!
        decision_reason="Attempting promotion of low security score model",
        actor_id=uuid.uuid4(),
        actor_type="ADMIN",
    )

    assert res.model_id == "unsafe_model"
    assert res.new_status == GovernanceStatus.REJECTED
    assert "HARD SECURITY FLOOR VIOLATION" in res.decision_reason


@pytest.mark.asyncio
async def test_03_non_admin_promotion_rejected(governance_service, mock_db):
    with pytest.raises(PermissionError) as exc_info:
        await governance_service.promote_model(
            db=mock_db,
            model_id="openai/gpt-4o",
            target_status=GovernanceStatus.CHAMPION,
            security_score=Decimal("0.9800"),
            decision_reason="Agent attempting self-promotion",
            actor_id=uuid.uuid4(),
            actor_type="AGENT",  # Non-admin!
        )

    assert "admin authorization required" in str(exc_info.value)


@pytest.mark.asyncio
async def test_04_rollback_model_success(governance_service, mock_db):
    res = await governance_service.rollback_model(
        db=mock_db,
        model_id="degraded_model",
        fallback_model_id="openai/gpt-4o",
        reason="P95 latency spike",
    )

    assert res.model_id == "degraded_model"
    assert res.new_status == GovernanceStatus.ROLLED_BACK
    assert governance_service.get_champion_model() == "openai/gpt-4o"
