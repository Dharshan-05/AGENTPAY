"""Unit and Security Tests for Merchant Domain Service (Phase 165/167)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.services.merchant_service import MerchantService, _slugify
from app.domain.exceptions.agent_exceptions import MerchantAlreadyExistsError
from app.infrastructure.database.models.merchant import Merchant
from app.schemas.merchants import MerchantCreateRequest, MerchantStatusEnum


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service() -> MerchantService:
    service = MerchantService()
    service.repository.create = AsyncMock()  # type: ignore[method-assign]
    service.repository.get_by_id = AsyncMock()  # type: ignore[method-assign]
    service.repository.get_by_slug = AsyncMock()  # type: ignore[method-assign]
    service.repository.update = AsyncMock()  # type: ignore[method-assign]
    service.repository.archive = AsyncMock()  # type: ignore[method-assign]
    service.repository.restore = AsyncMock()  # type: ignore[method-assign]
    service.repository.exists = AsyncMock()  # type: ignore[method-assign]
    service.repository.list = AsyncMock()  # type: ignore[method-assign]
    return service


@pytest.mark.asyncio
async def test_01_slugify_helper() -> None:
    """1. Test string slugification helper function."""
    assert _slugify("Acme Commerce Inc.") == "acme-commerce-inc"
    assert _slugify("  Special @ Merchant $ Name!  ") == "special-merchant-name"


@pytest.mark.asyncio
async def test_02_create_merchant_success(mock_db: MagicMock, service: MerchantService) -> None:
    """2. Test creating a merchant entity successfully."""
    tenant_id = uuid.uuid4()

    service.repository.get_by_slug.return_value = None  # type: ignore[attr-defined]
    now = datetime.now(UTC)
    mock_m = Merchant(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name="Global Retailers",
        slug="global-retailers",
        status="active",
        created_at=now,
        updated_at=now,
    )
    service.repository.create.return_value = mock_m  # type: ignore[attr-defined]

    req = MerchantCreateRequest(
        name="Global Retailers",
        description="International retail merchant",
    )

    res = await service.create_merchant(mock_db, tenant_id, req)
    assert res.name == "Global Retailers"
    assert res.slug == "global-retailers"
    assert res.status == MerchantStatusEnum.ACTIVE


@pytest.mark.asyncio
async def test_03_create_merchant_duplicate_slug_rejected(
    mock_db: MagicMock, service: MerchantService
) -> None:
    """3. Test duplicate merchant slug creation raises MerchantAlreadyExistsError."""
    tenant_id = uuid.uuid4()

    existing_merchant = MagicMock(spec=Merchant)
    service.repository.get_by_slug.return_value = existing_merchant  # type: ignore[attr-defined]

    req = MerchantCreateRequest(
        name="Existing Shop",
        slug="existing-shop",
    )

    with pytest.raises(MerchantAlreadyExistsError):
        await service.create_merchant(mock_db, tenant_id, req)


@pytest.mark.asyncio
async def test_04_merchant_status_transitions(mock_db: MagicMock, service: MerchantService) -> None:
    """4. Test merchant lifecycle status transitions (activate, suspend, archive)."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    merchant = Merchant(
        id=merchant_id,
        tenant_id=tenant_id,
        name="Tech Store",
        slug="tech-store",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    service.repository.get_by_id.return_value = merchant  # type: ignore[attr-defined]
    service.repository.update.return_value = merchant  # type: ignore[attr-defined]

    res_suspended = await service.suspend_merchant(mock_db, tenant_id, merchant_id)
    assert res_suspended.status == MerchantStatusEnum.SUSPENDED

    res_active = await service.activate_merchant(mock_db, tenant_id, merchant_id)
    assert res_active.status == MerchantStatusEnum.ACTIVE
