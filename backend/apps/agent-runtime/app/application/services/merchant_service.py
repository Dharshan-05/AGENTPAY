"""Merchant Application Domain Service for AGENTPAY (Phase 165/167)."""

from __future__ import annotations

import logging
import re
import uuid
from datetime import UTC, datetime
from typing import Any

from app.domain.exceptions.agent_exceptions import (
    MerchantAlreadyExistsError,
    MerchantNotFoundError,
    MerchantValidationError,
)
from app.infrastructure.database.models.merchant import Merchant
from app.infrastructure.database.repositories.merchant_repository import MerchantRepository
from app.schemas.merchants import (
    MerchantCreateRequest,
    MerchantListResponse,
    MerchantResponse,
    MerchantStatusEnum,
    MerchantUpdateRequest,
)

logger = logging.getLogger("agentpay.merchant.service")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100


def _slugify(name: str) -> str:
    """Generate a clean slug string from a merchant name."""
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s.strip("-") or "merchant"


class MerchantService:
    """Production service orchestrating Merchant lifecycle and business rules (Phase 165/167)."""

    def __init__(self, repository: MerchantRepository | None = None) -> None:
        self.repository = repository or MerchantRepository()

    async def create_merchant(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        request: MerchantCreateRequest,
    ) -> MerchantResponse:
        """Create a new Merchant enforcing tenant isolation and slug uniqueness (Phase 165/167)."""
        name_clean = request.name.strip()
        if not name_clean:
            raise MerchantValidationError("Merchant name cannot be empty.")

        slug_clean = _slugify(request.slug or name_clean)

        # Check slug uniqueness within tenant scope
        existing = await self.repository.get_by_slug(db, tenant_id, slug_clean)
        if existing:
            raise MerchantAlreadyExistsError(
                f"Merchant with slug '{slug_clean}' already exists for tenant '{tenant_id}'."
            )

        now = datetime.now(UTC)
        merchant = Merchant(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=name_clean,
            slug=slug_clean,
            status=request.status.value,
            description=request.description.strip() if request.description else None,
            created_at=now,
            updated_at=now,
        )

        saved = await self.repository.create(db, merchant)

        logger.info(
            "Created merchant %s (name: %s, slug: %s, tenant: %s)",
            saved.id,
            saved.name,
            saved.slug,
            tenant_id,
        )
        return self._to_response(saved)

    async def get_merchant(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
    ) -> MerchantResponse:
        """Lookup a merchant by ID within tenant isolation boundary (Phase 165/167)."""
        merchant = await self.repository.get_by_id(db, tenant_id, merchant_id)
        if not merchant:
            raise MerchantNotFoundError(f"Merchant '{merchant_id}' not found.")
        return self._to_response(merchant)

    async def update_merchant(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
        request: MerchantUpdateRequest,
    ) -> MerchantResponse:
        """Update merchant details (Phase 165/167)."""
        merchant = await self.repository.get_by_id(db, tenant_id, merchant_id)
        if not merchant:
            raise MerchantNotFoundError(f"Merchant '{merchant_id}' not found.")

        if request.name is not None:
            name_clean = request.name.strip()
            if not name_clean:
                raise MerchantValidationError("Merchant name cannot be empty.")
            merchant.name = name_clean

        if request.description is not None:
            merchant.description = request.description.strip() if request.description else None

        if request.status is not None:
            merchant.status = request.status.value

        merchant.updated_at = datetime.now(UTC)
        updated = await self.repository.update(db, merchant)
        return self._to_response(updated)

    async def activate_merchant(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
    ) -> MerchantResponse:
        """Activate a merchant (Phase 165/167)."""
        return await self.update_merchant(
            db, tenant_id, merchant_id, MerchantUpdateRequest(status=MerchantStatusEnum.ACTIVE)
        )

    async def deactivate_merchant(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
    ) -> MerchantResponse:
        """Deactivate a merchant (Phase 165/167)."""
        return await self.update_merchant(
            db, tenant_id, merchant_id, MerchantUpdateRequest(status=MerchantStatusEnum.INACTIVE)
        )

    async def suspend_merchant(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
    ) -> MerchantResponse:
        """Suspend a merchant (Phase 165/167)."""
        return await self.update_merchant(
            db, tenant_id, merchant_id, MerchantUpdateRequest(status=MerchantStatusEnum.SUSPENDED)
        )

    async def archive_merchant(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
    ) -> MerchantResponse:
        """Archive (soft delete) a merchant (Phase 165/167)."""
        archived = await self.repository.archive(db, tenant_id, merchant_id)
        if not archived:
            raise MerchantNotFoundError(f"Merchant '{merchant_id}' not found.")
        return self._to_response(archived)

    async def restore_merchant(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
    ) -> MerchantResponse:
        """Restore an archived merchant (Phase 165/167)."""
        restored = await self.repository.restore(db, tenant_id, merchant_id)
        if not restored:
            raise MerchantNotFoundError(f"Merchant '{merchant_id}' not found.")
        return self._to_response(restored)

    async def list_merchants(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        *,
        status: str | None = None,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
    ) -> MerchantListResponse:
        """List tenant-scoped merchants using keyset pagination (Phase 165/167)."""
        rows, has_more = await self.repository.list(
            db,
            tenant_id,
            status=status,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
            limit=limit,
        )
        responses = [self._to_response(m) for m in rows]
        return MerchantListResponse(
            tenant_id=tenant_id,
            total_count=len(responses),
            has_more=has_more,
            merchants=responses,
        )

    def _to_response(self, merchant: Merchant) -> MerchantResponse:
        """Map ORM entity to MerchantResponse schema."""
        return MerchantResponse(
            id=merchant.id,
            tenant_id=merchant.tenant_id,
            name=merchant.name,
            slug=merchant.slug,
            status=MerchantStatusEnum(merchant.status),
            description=merchant.description,
            created_at=merchant.created_at,
            updated_at=merchant.updated_at,
            deleted_at=merchant.deleted_at,
        )
