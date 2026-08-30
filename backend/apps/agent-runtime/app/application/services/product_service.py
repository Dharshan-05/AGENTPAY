"""Product Application Domain Service for AGENTPAY (Phase 164)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select

from app.domain.exceptions.agent_exceptions import (
    MerchantNotFoundError,
    ProductAlreadyExistsError,
    ProductNotFoundError,
    ProductValidationError,
)
from app.infrastructure.database.models.merchant import Merchant
from app.infrastructure.database.models.product import Product
from app.infrastructure.database.repositories.product_repository import ProductRepository
from app.schemas.products import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductStatusEnum,
    ProductUpdateRequest,
)

logger = logging.getLogger("agentpay.product.service")

# ISO 4217 Currency Codes (subset of common supported currencies)
SUPPORTED_CURRENCIES: frozenset[str] = frozenset(
    {"USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "CNY", "INR", "BRL"}
)


class ProductService:
    """Production service orchestrating Product lifecycle and business rules (Phase 164)."""

    def __init__(self, repository: ProductRepository | None = None) -> None:
        self.repository = repository or ProductRepository()

    async def create_product(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        request: ProductCreateRequest,
    ) -> ProductResponse:
        """Create a new Product enforcing SKU uniqueness and merchant tenant ownership (Phase 164)."""  # noqa: E501
        # 1. Validate Merchant existence and tenant isolation
        merchant = await self._get_merchant(db, tenant_id, request.merchant_id)
        if not merchant:
            raise MerchantNotFoundError(
                f"Merchant '{request.merchant_id}' not found for tenant '{tenant_id}'."
            )

        # 2. Validate Price and Currency
        if request.price <= Decimal("0.00"):
            raise ProductValidationError("Product price must be greater than zero.")

        curr_code = request.currency_code.upper().strip()
        if curr_code not in SUPPORTED_CURRENCIES:
            raise ProductValidationError(f"Currency code '{curr_code}' is not supported.")

        # 3. Check SKU uniqueness within tenant & merchant scope
        sku_clean = request.sku.strip()
        exists = await self.repository.exists(db, tenant_id, request.merchant_id, sku_clean)
        if exists:
            raise ProductAlreadyExistsError(
                f"Product with SKU '{sku_clean}' already exists for merchant '{request.merchant_id}'."  # noqa: E501
            )

        # 4. Construct Product ORM entity
        product = Product(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            merchant_id=request.merchant_id,
            name=request.name.strip(),
            sku=sku_clean,
            description=request.description.strip() if request.description else None,
            status=request.status.value,
            price=request.price,
            currency_code=curr_code,
            metadata_payload=request.metadata_payload or {},
        )

        saved = await self.repository.create(db, product)
        logger.info(
            "Created product %s (SKU: %s, merchant: %s, tenant: %s)",
            saved.id,
            saved.sku,
            saved.merchant_id,
            tenant_id,
        )
        return self._to_response(saved)

    async def get_product(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> ProductResponse:
        """Lookup a single product by ID within tenant isolation boundary (Phase 164)."""
        product = await self.repository.get_by_id(db, tenant_id, product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found.")
        return self._to_response(product)

    async def update_product(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
        request: ProductUpdateRequest,
    ) -> ProductResponse:
        """Update an existing Product's attributes (Phase 164)."""
        product = await self.repository.get_by_id(db, tenant_id, product_id)
        if not product:
            raise ProductNotFoundError(f"Product '{product_id}' not found.")

        if request.name is not None:
            name_clean = request.name.strip()
            if not name_clean:
                raise ProductValidationError("Product name cannot be empty.")
            product.name = name_clean

        if request.description is not None:
            product.description = request.description.strip() if request.description else None

        if request.price is not None:
            if request.price <= Decimal("0.00"):
                raise ProductValidationError("Product price must be greater than zero.")
            product.price = request.price

        if request.currency_code is not None:
            curr_clean = request.currency_code.upper().strip()
            if curr_clean not in SUPPORTED_CURRENCIES:
                raise ProductValidationError(f"Currency code '{curr_clean}' is not supported.")
            product.currency_code = curr_clean

        if request.status is not None:
            product.status = request.status.value

        if request.metadata_payload is not None:
            product.metadata_payload = request.metadata_payload

        product.updated_at = datetime.now(UTC)
        updated = await self.repository.update(db, product)
        return self._to_response(updated)

    async def archive_product(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> ProductResponse:
        """Archive (soft-delete) a product (Phase 164)."""
        archived = await self.repository.archive(db, tenant_id, product_id)
        if not archived:
            raise ProductNotFoundError(f"Product '{product_id}' not found.")
        return self._to_response(archived)

    async def restore_product(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> ProductResponse:
        """Restore an archived product (Phase 164)."""
        restored = await self.repository.restore(db, tenant_id, product_id)
        if not restored:
            raise ProductNotFoundError(f"Product '{product_id}' not found.")
        return self._to_response(restored)

    async def activate_product(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> ProductResponse:
        """Activate a product (Phase 164)."""
        return await self.update_product(
            db, tenant_id, product_id, ProductUpdateRequest(status=ProductStatusEnum.ACTIVE)
        )

    async def deactivate_product(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> ProductResponse:
        """Deactivate a product (Phase 164)."""
        return await self.update_product(
            db, tenant_id, product_id, ProductUpdateRequest(status=ProductStatusEnum.INACTIVE)
        )

    async def list_products(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        *,
        merchant_id: uuid.UUID | None = None,
        status: str | None = None,
        currency: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = 20,
    ) -> ProductListResponse:
        """List tenant-scoped products supporting filtering, sorting, and keyset pagination (Phase 164/170/171)."""  # noqa: E501
        if min_price is not None and min_price < Decimal("0.00"):
            raise ProductValidationError("min_price cannot be negative.")
        if max_price is not None and max_price < Decimal("0.00"):
            raise ProductValidationError("max_price cannot be negative.")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ProductValidationError("min_price cannot exceed max_price.")

        rows, has_more = await self.repository.list(
            db,
            tenant_id,
            merchant_id=merchant_id,
            status=status,
            currency=currency,
            min_price=min_price,
            max_price=max_price,
            created_after=created_after,
            created_before=created_before,
            sort_by=sort_by,
            sort_dir=sort_dir,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
            limit=limit,
        )
        responses = [self._to_response(p) for p in rows]
        return ProductListResponse(
            tenant_id=tenant_id,
            total_count=len(responses),
            has_more=has_more,
            products=responses,
        )

    async def _get_merchant(
        self,
        db: Any,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
    ) -> Merchant | None:
        """Helper looking up merchant with tenant isolation."""
        stmt = select(Merchant).where(
            Merchant.id == merchant_id,
            Merchant.tenant_id == tenant_id,
            Merchant.deleted_at.is_(None),
        )
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        m: Merchant | None = res.scalars().first()
        return m

    def _to_response(self, product: Product) -> ProductResponse:
        """Map ORM entity to ProductResponse schema."""
        return ProductResponse(
            id=product.id,
            tenant_id=product.tenant_id,
            merchant_id=product.merchant_id,
            name=product.name,
            sku=product.sku,
            description=product.description,
            status=ProductStatusEnum(product.status),
            price=product.price,
            currency_code=product.currency_code,
            metadata_payload=product.metadata_payload or {},
            created_at=product.created_at,
            updated_at=product.updated_at,
            deleted_at=product.deleted_at,
        )
