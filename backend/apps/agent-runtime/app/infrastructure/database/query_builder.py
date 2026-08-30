"""Query Optimization & Builder Module for AGENTPAY (Phase 077)."""

import uuid
from collections.abc import Sequence
from typing import Any, TypeVar

from sqlalchemy import Select, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

T = TypeVar("T", bound=Any)


def enforce_tenant_filter(
    query: Select[tuple[T]],
    model_tenant_col: Any,
    tenant_id: uuid.UUID,
) -> Select[tuple[T]]:
    """Enforce mandatory tenant isolation filter on a SQLAlchemy Select query."""
    return query.where(model_tenant_col == tenant_id)


def build_exists_query(
    model_tenant_col: Any,
    tenant_id: uuid.UUID,
    *where_clauses: Any,
) -> Select[tuple[bool]]:
    """Construct an optimized SQL EXISTS query returning bool without loading entity rows."""
    stmt = select(1).where(model_tenant_col == tenant_id)
    for clause in where_clauses:
        stmt = stmt.where(clause)
    return select(exists(stmt))


async def check_exists(
    session: AsyncSession,
    model_tenant_col: Any,
    tenant_id: uuid.UUID,
    *where_clauses: Any,
) -> bool:
    """Execute optimized SELECT EXISTS(...) probe returning boolean."""
    stmt = build_exists_query(model_tenant_col, tenant_id, *where_clauses)
    result = await session.execute(stmt)
    return bool(result.scalar())


def paginate_keyset(
    query: Select[tuple[T]],
    id_col: InstrumentedAttribute[uuid.UUID],
    created_at_col: InstrumentedAttribute[Any],
    tenant_id: uuid.UUID,
    tenant_col: InstrumentedAttribute[uuid.UUID],
    limit: int = 50,
    cursor_created_at: Any | None = None,
    cursor_id: uuid.UUID | None = None,
) -> Select[tuple[T]]:
    """Construct deterministic keyset (cursor) pagination query for high-volume datasets."""
    stmt = query.where(tenant_col == tenant_id)

    if cursor_created_at is not None and cursor_id is not None:
        # Keyset tuple comparison: (created_at, id) < (cursor_created_at, cursor_id)
        stmt = stmt.where(
            (created_at_col < cursor_created_at)
            | ((created_at_col == cursor_created_at) & (id_col < cursor_id))
        )

    stmt = stmt.order_by(created_at_col.desc(), id_col.desc()).limit(limit)
    return stmt


async def fetch_keyset_page(
    session: AsyncSession,
    query: Select[tuple[T]],
    id_col: InstrumentedAttribute[uuid.UUID],
    created_at_col: InstrumentedAttribute[Any],
    tenant_id: uuid.UUID,
    tenant_col: InstrumentedAttribute[uuid.UUID],
    limit: int = 50,
    cursor_created_at: Any | None = None,
    cursor_id: uuid.UUID | None = None,
) -> tuple[Sequence[T], Any | None, uuid.UUID | None]:
    """Execute keyset pagination query and return items plus next cursor tuple."""
    stmt = paginate_keyset(
        query=query,
        id_col=id_col,
        created_at_col=created_at_col,
        tenant_id=tenant_id,
        tenant_col=tenant_col,
        limit=limit,
        cursor_created_at=cursor_created_at,
        cursor_id=cursor_id,
    )
    result = await session.execute(stmt)
    items = list(result.scalars().all())

    if items:
        last_item = items[-1]
        next_created_at = getattr(last_item, created_at_col.key)
        next_id = getattr(last_item, id_col.key)
        return items, next_created_at, next_id

    return [], None, None
