"""Merchant Repository infrastructure data access module for AGENTPAY (Phase 167)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.merchant import Merchant

logger = logging.getLogger("agentpay.merchant.repository")

_LIMIT_DEFAULT = 20
_LIMIT_MAX = 100


class MerchantRepository:
    """Infrastructure repository managing persistent Merchant entities with tenant isolation (Phase 167)."""  # noqa: E501

    async def create(self, db: AsyncSession, merchant: Merchant) -> Merchant:
        """Persist a new Merchant entity."""
        db.add(merchant)
        await self._flush(db)
        await self._refresh(db, merchant)
        return merchant

    async def get_by_id(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
        include_deleted: bool = False,
    ) -> Merchant | None:
        """Lookup a Merchant entity by merchant_id within tenant isolation scope."""
        stmt = select(Merchant).where(
            Merchant.id == merchant_id,
            Merchant.tenant_id == tenant_id,
        )
        if not include_deleted:
            stmt = stmt.where(Merchant.deleted_at.is_(None))

        res = await self._exec(db, stmt)
        m: Merchant | None = res.scalars().first()
        return m

    async def get_by_slug(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        slug: str,
    ) -> Merchant | None:
        """Lookup a Merchant entity by unique slug within tenant isolation scope."""
        stmt = select(Merchant).where(
            Merchant.tenant_id == tenant_id,
            Merchant.slug == slug.strip(),
            Merchant.deleted_at.is_(None),
        )
        res = await self._exec(db, stmt)
        m: Merchant | None = res.scalars().first()
        return m

    async def list(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        *,
        status: str | None = None,
        cursor_created_at: datetime | None = None,
        cursor_id: uuid.UUID | None = None,
        limit: int = _LIMIT_DEFAULT,
    ) -> tuple[list[Merchant], bool]:
        """List tenant-scoped merchants using keyset pagination (created_at DESC, id DESC)."""
        fetch_limit = min(max(1, limit), _LIMIT_MAX) + 1

        stmt = select(Merchant).where(
            Merchant.tenant_id == tenant_id,
            Merchant.deleted_at.is_(None),
        )

        if status and status.strip():
            stmt = stmt.where(Merchant.status == status.strip().lower())

        if cursor_created_at is not None and cursor_id is not None:
            stmt = stmt.where(
                or_(
                    Merchant.created_at < cursor_created_at,
                    and_(
                        Merchant.created_at == cursor_created_at,
                        Merchant.id < cursor_id,
                    ),
                )
            )

        stmt = stmt.order_by(Merchant.created_at.desc(), Merchant.id.desc()).limit(fetch_limit)
        res = await self._exec(db, stmt)
        rows = list(res.scalars().all())

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        return rows, has_more

    async def update(self, db: AsyncSession, merchant: Merchant) -> Merchant:
        """Update an existing Merchant entity."""
        await self._flush(db)
        await self._refresh(db, merchant)
        return merchant

    async def archive(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
    ) -> Merchant | None:
        """Soft delete / archive a Merchant by setting deleted_at timestamp and status='archived'."""  # noqa: E501
        merchant = await self.get_by_id(db, tenant_id, merchant_id, include_deleted=False)
        if not merchant:
            return None

        now = datetime.now(UTC)
        merchant.deleted_at = now
        merchant.status = "archived"
        merchant.updated_at = now
        await self._flush(db)
        return merchant

    async def restore(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        merchant_id: uuid.UUID,
    ) -> Merchant | None:
        """Restore an archived Merchant by clearing deleted_at timestamp and setting status='active'."""  # noqa: E501
        merchant = await self.get_by_id(db, tenant_id, merchant_id, include_deleted=True)
        if not merchant or merchant.deleted_at is None:
            return merchant

        merchant.deleted_at = None
        merchant.status = "active"
        merchant.updated_at = datetime.now(UTC)
        await self._flush(db)
        return merchant

    async def exists(
        self,
        db: AsyncSession,
        tenant_id: uuid.UUID,
        slug: str,
    ) -> bool:
        """Check if a Merchant with slug exists within tenant scope."""
        merchant = await self.get_by_slug(db, tenant_id, slug)
        return merchant is not None

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
