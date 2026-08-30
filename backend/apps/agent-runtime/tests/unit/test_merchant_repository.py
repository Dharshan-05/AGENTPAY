"""Unit and Data Access Tests for Merchant Repository (Phase 167)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.infrastructure.database.models.merchant import Merchant
from app.infrastructure.database.repositories.merchant_repository import MerchantRepository


@pytest.fixture
def repo() -> MerchantRepository:
    return MerchantRepository()


@pytest.mark.asyncio
async def test_01_create_and_get_merchant_repository(repo: MerchantRepository) -> None:
    """1. Test creating and retrieving a merchant entity in repository."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    merchant = Merchant(
        id=merchant_id,
        tenant_id=tenant_id,
        name="Apex Store",
        slug="apex-store",
        status="active",
        created_at=datetime.now(UTC),
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = merchant

    saved = await repo.create(mock_db, merchant)
    assert saved.id == merchant_id
    assert saved.slug == "apex-store"

    retrieved = await repo.get_by_id(mock_db, tenant_id, merchant_id)
    assert retrieved is not None
    assert retrieved.name == "Apex Store"


@pytest.mark.asyncio
async def test_02_get_by_slug_and_exists_check(repo: MerchantRepository) -> None:
    """2. Test slug lookup and existence check in repository."""
    tenant_id = uuid.uuid4()

    merchant = MagicMock(spec=Merchant)
    merchant.slug = "electronics-hub"

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = merchant

    res = await repo.get_by_slug(mock_db, tenant_id, "electronics-hub")
    assert res is not None
    assert res.slug == "electronics-hub"

    exists = await repo.exists(mock_db, tenant_id, "electronics-hub")
    assert exists is True


@pytest.mark.asyncio
async def test_03_archive_and_restore_merchant_repository(repo: MerchantRepository) -> None:
    """3. Test archival (soft delete) and restoration of a merchant."""
    tenant_id = uuid.uuid4()
    merchant_id = uuid.uuid4()

    merchant = Merchant(
        id=merchant_id,
        tenant_id=tenant_id,
        name="Archivable Merchant",
        slug="archivable-merchant",
        status="active",
        deleted_at=None,
    )

    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = merchant

    archived = await repo.archive(mock_db, tenant_id, merchant_id)
    assert archived is not None
    assert archived.deleted_at is not None
    assert archived.status == "archived"
