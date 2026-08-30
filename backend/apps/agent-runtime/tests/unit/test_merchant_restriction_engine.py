"""Unit and Security Tests for Merchant Restriction Engine (Phase 193)."""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest

from app.application.services.merchant_restriction_service import MerchantRestrictionService
from app.domain.exceptions.agent_exceptions import MerchantNotFoundError
from app.infrastructure.database.models.merchant import Merchant
from app.schemas.merchant_restrictions import MerchantRestrictionEvaluationRequest


@pytest.fixture
def service() -> MerchantRestrictionService:
    return MerchantRestrictionService()


@pytest.mark.asyncio
async def test_01_allowed_merchant_passes(service: MerchantRestrictionService) -> None:
    """1. Test merchant in allowlist returns ALLOW."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    merchant = Merchant(
        id=merchant_id,
        tenant_id=tenant_id,
        name="Acme Supplies",
        slug="acme-supplies",
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = merchant

    req = MerchantRestrictionEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        merchant_id=merchant_id,
        allowed_merchants=["acme-supplies"],
    )

    res = await service.evaluate_merchant_restriction(mock_db, req)
    assert res.decision == "ALLOW"
    assert res.reason_code == "MERCHANT_ALLOWED"


@pytest.mark.asyncio
async def test_02_blocked_merchant_denied(service: MerchantRestrictionService) -> None:
    """2. Test merchant in denylist returns DENIED."""
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    merchant = Merchant(
        id=merchant_id,
        tenant_id=tenant_id,
        name="Risky Merchant",
        slug="risky-merchant",
        status="active",
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = merchant

    req = MerchantRestrictionEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        merchant_id=merchant_id,
        blocked_merchants=["risky-merchant"],
    )

    res = await service.evaluate_merchant_restriction(mock_db, req)
    assert res.decision == "DENIED"
    assert res.reason_code == "MERCHANT_DENIED"


@pytest.mark.asyncio
async def test_03_merchant_not_found_raises_404(
    service: MerchantRestrictionService,
) -> None:
    """3. Test missing or cross-tenant merchant raises MerchantNotFoundError (404 anti-enumeration)."""  # noqa: E501
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    req = MerchantRestrictionEvaluationRequest(
        tenant_id=tenant_id,
        agent_id=agent_id,
        merchant_id=merchant_id,
    )

    with pytest.raises(MerchantNotFoundError):
        await service.evaluate_merchant_restriction(mock_db, req)
