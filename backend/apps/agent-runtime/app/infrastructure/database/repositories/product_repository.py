"""Product Repository infrastructure data access module for AGENTPAY (Phase 166/170/171)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.product import Product

logger = logging.getLogger("agentpay.product.repository")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100

SORT_COLUMN_MAP: dict[str, Any] = {
    "created_at": Product.created_at,
    "updated_at": Product.updated_at,
    "name": Product.name,
    "price": Product.price,
    "sku": Product.sku,
}


class ProductRepository:
    """Infrastructure repository managing persistent Product entities with tenant isolation (Phase 166/170/171)."""  # noqa: E501

    async def create(self, db: AsyncSession, product: Product) -> Product:
        """Persist a new Product entity."""
        db.add(product)
        await self._flush(db)
        await self._refresh(db, product)
        return product

    async def get_by_id(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
        include_deleted: bool = False,
    ) -> Product | None:
        """Lookup a Product entity by product_id within tenant isolation scope."""
        stmt = select(Product).where(
            Product.id == product_id,
            Product.tenant_id == tenant_id,
        )
        if not include_deleted:
            stmt = stmt.where(Product.deleted_at.is_(None))

        res = await self._exec(db, stmt)
        prod: Product | None = res.scalars().first()
        return prod

    async def get_by_sku(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
        sku: str,
    ) -> Product | None:
        """Lookup a Product by SKU within merchant and tenant scope."""
        stmt = select(Product).where(
            Product.tenant_id == tenant_id,
            Product.merchant_id == merchant_id,
            Product.sku == sku.strip(),
            Product.deleted_at.is_(None),
        )
        res = await self._exec(db, stmt)
        prod: Product | None = res.scalars().first()
        return prod

    async def list(
        self,
        db: AsyncSession,
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
        limit: int = _LIMIT_DEFAULT,
    ) -> tuple[list[Product], bool]:
        """List tenant-scoped products supporting filtering, sorting, and keyset pagination (Phase 170 & 171)."""  # noqa: E501
        fetch_limit = min(max(1, limit), _LIMIT_MAX) + 1

        stmt = select(Product).where(
            Product.tenant_id == tenant_id,
            Product.deleted_at.is_(None),
        )

        if merchant_id:
            stmt = stmt.where(Product.merchant_id == merchant_id)
        if status and status.strip():
            stmt = stmt.where(Product.status == status.strip().lower())
        if currency and currency.strip():
            stmt = stmt.where(Product.currency_code == currency.strip().upper())

        if min_price is not None:
            stmt = stmt.where(Product.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.price <= max_price)

        if created_after is not None:
            stmt = stmt.where(Product.created_at >= created_after)
        if created_before is not None:
            stmt = stmt.where(Product.created_at <= created_before)

        # Keyset pagination clause
        if cursor_created_at is not None and cursor_id is not None:
            stmt = stmt.where(
                or_(
                    Product.created_at < cursor_created_at,
                    and_(
                        Product.created_at == cursor_created_at,
                        Product.id < cursor_id,
                    ),
                )
            )

        # Whitelisted sorting column lookup
        clean_sort_by = sort_by.strip().lower() if sort_by else "created_at"
        sort_col = SORT_COLUMN_MAP.get(clean_sort_by, Product.created_at)

        clean_sort_dir = sort_dir.strip().lower() if sort_dir else "desc"
        if clean_sort_dir == "asc":
            stmt = stmt.order_by(sort_col.asc(), Product.id.asc())
        else:
            stmt = stmt.order_by(sort_col.desc(), Product.id.desc())

        stmt = stmt.limit(fetch_limit)
        res = await self._exec(db, stmt)
        rows = list(res.scalars().all())

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        return rows, has_more

    async def update(self, db: AsyncSession, product: Product) -> Product:
        """Update an existing Product entity."""
        await self._flush(db)
        await self._refresh(db, product)
        return product

    async def archive(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> Product | None:
        """Soft delete / archive a Product by setting deleted_at timestamp and status='archived'."""  # noqa: E501
        product = await self.get_by_id(db, tenant_id, product_id, include_deleted=False)
        if not product:
            return None

        now = datetime.now(UTC)
        product.deleted_at = now
        product.status = "archived"
        product.updated_at = now
        await self._flush(db)
        return product

    async def restore(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        product_id: uuid.UUID,
    ) -> Product | None:
        """Restore an archived Product by clearing deleted_at timestamp and setting status='active'."""  # noqa: E501
        product = await self.get_by_id(db, tenant_id, product_id, include_deleted=True)
        if not product or product.deleted_at is None:
            return product

        product.deleted_at = None
        product.status = "active"
        product.updated_at = datetime.now(UTC)
        await self._flush(db)
        return product

    async def exists(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
        sku: str,
    ) -> bool:
        """Check if a Product with SKU exists within merchant and tenant scope."""
        product = await self.get_by_sku(db, tenant_id, merchant_id, sku)
        return product is not None

    async def _exec(self, db: Any, stmt: Any) -> Any:
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res
        return res

    async def _flush(self, db: Any) -> None:
        res = db.flush()
        if inspect.isawaitable(res):
            await res

    async def _refresh(self, db: Any, obj: Any) -> None:
        res = db.refresh(obj)
        if inspect.isawaitable(res):
            await res
