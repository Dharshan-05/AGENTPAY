"""Dataset Ingestion & Integration Service (Phase 217)."""

from __future__ import annotations

import inspect
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.payment_order import PaymentOrder
from app.ml.config.ml_config import (  # noqa: E501
    MLPipelineConfig,
    compute_dataset_fingerprint,
    get_default_ml_config,
)
from app.schemas.ml_foundation import DatasetContract, DatasetMetadata, DatasetSnapshot

logger = logging.getLogger("fraudguard.ml.integration")


class DatasetLoader:
    """Production Dataset Integration Layer (Phase 217)."""

    def __init__(self, config: MLPipelineConfig | None = None) -> None:
        self.config = config or get_default_ml_config()
        self.snapshots: dict[str, DatasetSnapshot] = {}

    async def load_payment_orders(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        agent_id: uuid.UUID | None = None,
        limit: int = 1000,
    ) -> tuple[list[dict[str, Any]], DatasetMetadata]:
        """Load payment orders from database with tenant isolation (Phase 217)."""
        logger.info(
            "Loading payment orders dataset for tenant %s (agent=%s, limit=%d)",
            tenant_id,
            agent_id,
            limit,
        )

        query = (
            select(PaymentOrder)
            .where(PaymentOrder.tenant_id == tenant_id)
            .order_by(PaymentOrder.created_at.desc())
            .limit(limit)
        )
        if agent_id:
            query = query.where(PaymentOrder.agent_id == agent_id)

        res = db.execute(query)
        if inspect.isawaitable(res):
            res = await res
        orders: list[PaymentOrder] = list(res.scalars().all()) if hasattr(res, "scalars") else []

        records: list[dict[str, Any]] = []
        for order in orders:
            records.append(
                {
                    "transaction_id": str(order.id),
                    "tenant_id": str(order.tenant_id),
                    "agent_id": str(order.agent_id) if order.agent_id else None,
                    "merchant_id": str(order.merchant_id)
                    if getattr(order, "merchant_id", None)
                    else None,  # noqa: E501
                    "amount": getattr(order, "amount", None),
                    "currency": getattr(order, "currency", "USD"),
                    "status": getattr(order, "status", "UNKNOWN"),
                    "created_at": (
                        order.created_at.isoformat()
                        if getattr(order, "created_at", None)
                        else datetime.now(UTC).isoformat()
                    ),
                }
            )

        fingerprint = compute_dataset_fingerprint(records)
        metadata = DatasetMetadata(
            tenant_id=tenant_id,
            dataset_name="payment_orders",
            source="POSTGRESQL_PAYMENT_ORDER",
            version=self.config.dataset_version,
            record_count=len(records),
            schema_version=self.config.schema_version,
            fingerprint=fingerprint,
            attributes={"agent_filter": str(agent_id) if agent_id else "ALL"},
        )

        return records, metadata

    def load_raw_batch_records(
        self,
        tenant_id: uuid.UUID,
        records: list[dict[str, Any]],
        dataset_name: str = "batch_records",
    ) -> tuple[list[dict[str, Any]], DatasetMetadata]:
        """Ingest raw batch records with tenant isolation verification (Phase 217)."""
        tenant_str = str(tenant_id)
        filtered_records: list[dict[str, Any]] = []

        for rec in records:
            rec_tenant = rec.get("tenant_id")
            if rec_tenant is not None and str(rec_tenant) != tenant_str:
                logger.warning(
                    "Skipping cross-tenant record with tenant_id=%s (expected %s)",
                    rec_tenant,
                    tenant_str,
                )
                continue
            cleaned_rec = dict(rec)
            cleaned_rec["tenant_id"] = tenant_str
            filtered_records.append(cleaned_rec)

        fingerprint = compute_dataset_fingerprint(filtered_records)
        metadata = DatasetMetadata(
            tenant_id=tenant_id,
            dataset_name=dataset_name,
            source="BATCH_INGESTION",
            version=self.config.dataset_version,
            record_count=len(filtered_records),
            schema_version=self.config.schema_version,
            fingerprint=fingerprint,
        )

        return filtered_records, metadata

    def create_snapshot(
        self, dataset_name: str, records: list[dict[str, Any]], version_tag: str = "v1"
    ) -> DatasetSnapshot:
        """Create an immutable snapshot record of a dataset version (Phase 217)."""
        fingerprint = compute_dataset_fingerprint(records)
        snapshot = DatasetSnapshot(
            dataset_name=dataset_name,
            dataset_version=version_tag,
            fingerprint=fingerprint,
            record_count=len(records),
            captured_at=datetime.now(UTC),
        )
        self.snapshots[f"{dataset_name}:{version_tag}"] = snapshot
        logger.info(
            "Captured immutable dataset snapshot %s:%s (Fingerprint: %s)",
            dataset_name,
            version_tag,
            fingerprint,
        )
        return snapshot

    def create_dataset_contract(
        self, dataset_name: str, source: str, description: str = ""
    ) -> DatasetContract:
        """Create a formal dataset contract specification (Phase 217)."""
        return DatasetContract(
            dataset_version=self.config.dataset_version,
            schema_version=self.config.schema_version,
            source=source,
            description=description,
            created_at=datetime.now(UTC),
            effective_from=datetime.now(UTC),
        )
