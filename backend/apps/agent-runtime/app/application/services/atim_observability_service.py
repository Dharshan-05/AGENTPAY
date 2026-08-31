"""ATIM Real-Time Observability & Telemetry Service for AGENTPAY (Phase 10 / Group 5)."""

import logging
import math
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.atim.telemetry_models import (
    ATIMTelemetryAggregate,
    ATIMTelemetryRecord,
    LatencyDistribution,
    ProviderCostAggregate,
)
from app.infrastructure.database.models.atim_telemetry import ATIMExecutionTelemetry

logger = logging.getLogger("agentpay.atim.observability")


class ATIMObservabilityService:
    """Application service for ATIM execution logging, latency/cost aggregations, and real-time telemetry."""

    async def record_telemetry(
        self,
        db: AsyncSession | Any,
        record: ATIMTelemetryRecord,
    ) -> ATIMExecutionTelemetry:
        """Persist execution telemetry record to PostgreSQL in tenant scope."""
        telemetry_entry = ATIMExecutionTelemetry(
            id=record.id,
            tenant_id=record.tenant_id,
            agent_id=record.agent_id,
            request_id=record.request_id,
            prompt_text=record.prompt_text[:2000] if record.prompt_text else None,
            action=record.action,
            amount=record.amount,
            currency=record.currency or "USD",
            is_security_blocked=record.is_security_blocked,
            security_score=record.security_score,
            security_reason=record.security_reason,
            selected_model=record.selected_model,
            provider=record.provider,
            fallback_used=record.fallback_used,
            task_type=record.task_type,
            complexity=record.complexity,
            risk_level=record.risk_level,
            latency_ms=record.latency_ms,
            prompt_tokens=record.prompt_tokens,
            completion_tokens=record.completion_tokens,
            total_tokens=record.total_tokens,
            estimated_cost_usd=record.estimated_cost_usd,
            agentguard_decision=record.agentguard_decision,
            fraudguard_score=record.fraudguard_score,
            hitl_required=record.hitl_required,
            execution_decision=record.execution_decision,
            created_at=record.created_at,
        )

        try:
            if hasattr(db, "add"):
                db.add(telemetry_entry)
                if hasattr(db, "commit") and callable(getattr(db, "commit", None)):
                    commit_res = db.commit()
                    import inspect
                    if inspect.isawaitable(commit_res):
                        await commit_res
        except Exception as err:
            logger.warning("Failed to persist ATIM telemetry record to DB: %s", err)

        logger.info(
            "Recorded ATIM Telemetry [Tenant=%s Agent=%s Model=%s Latency=%.2fms Cost=$%.6f Blocked=%s]",
            record.tenant_id,
            record.agent_id,
            record.selected_model,
            record.latency_ms or 0.0,
            record.estimated_cost_usd,
            record.is_security_blocked,
        )

        return telemetry_entry

    async def get_tenant_telemetry_aggregate(
        self,
        db: AsyncSession | Any,
        tenant_id: uuid.UUID,
        window_minutes: int = 1440,
    ) -> ATIMTelemetryAggregate:
        """Compute aggregated latency, token expenditure, and security block metrics for a tenant."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=window_minutes)

        stmt = select(ATIMExecutionTelemetry).where(
            and_(
                ATIMExecutionTelemetry.tenant_id == tenant_id,
                ATIMExecutionTelemetry.created_at >= start_time,
            )
        )

        import inspect
        res = db.execute(stmt)
        if inspect.isawaitable(res):
            res = await res

        records: list[ATIMExecutionTelemetry] = []
        if hasattr(res, "scalars") and callable(getattr(res, "scalars", None)):
            try:
                sc = res.scalars()
                if inspect.isawaitable(sc):
                    sc = await sc
                if hasattr(sc, "all") and callable(getattr(sc, "all", None)):
                    all_rec = sc.all()
                    if inspect.isawaitable(all_rec):
                        all_rec = await all_rec
                    if isinstance(all_rec, (list, tuple, set)):
                        records = list(all_rec)
            except Exception:
                records = []

        total_requests = len(records)
        if total_requests == 0:
            return ATIMTelemetryAggregate(
                tenant_id=tenant_id,
                total_requests=0,
                security_blocked_requests=0,
                security_block_rate=0.0,
                fallback_requests=0,
                total_prompt_tokens=0,
                total_completion_tokens=0,
                total_tokens=0,
                total_cost_usd=Decimal("0.000000"),
                latency_distribution=LatencyDistribution(),
                provider_breakdown=[],
            )

        blocked_count = sum(1 for r in records if getattr(r, "is_security_blocked", False))
        fallback_count = sum(1 for r in records if getattr(r, "fallback_used", False))
        prompt_tokens = sum(getattr(r, "prompt_tokens", 0) or 0 for r in records)
        completion_tokens = sum(getattr(r, "completion_tokens", 0) or 0 for r in records)
        total_tokens = sum(getattr(r, "total_tokens", 0) or 0 for r in records)
        total_cost = sum(
            (Decimal(str(r.estimated_cost_usd)) for r in records if getattr(r, "estimated_cost_usd", None) is not None),
            Decimal("0.000000"),
        )

        # Compute Latency Percentiles
        latencies = sorted([float(r.latency_ms) for r in records if getattr(r, "latency_ms", None) is not None])
        if latencies:
            n = len(latencies)
            avg_lat = sum(latencies) / n
            p50 = latencies[int(n * 0.50)]
            p75 = latencies[int(n * 0.75)]
            p90 = latencies[int(n * 0.90)]
            p95 = latencies[min(int(n * 0.95), n - 1)]
            p99 = latencies[min(int(n * 0.99), n - 1)]
            latency_dist = LatencyDistribution(
                avg_ms=round(avg_lat, 2),
                p50_ms=round(p50, 2),
                p75_ms=round(p75, 2),
                p90_ms=round(p90, 2),
                p95_ms=round(p95, 2),
                p99_ms=round(p99, 2),
            )
        else:
            latency_dist = LatencyDistribution()

        # Provider Breakdown Aggregation
        provider_map: dict[str, dict[str, Any]] = {}
        for r in records:
            provider = getattr(r, "provider", "unknown") or "unknown"
            model = getattr(r, "selected_model", "unknown") or "unknown"
            key = f"{provider}:{model}"
            if key not in provider_map:
                provider_map[key] = {
                    "provider": provider,
                    "model": model,
                    "count": 0,
                    "tokens": 0,
                    "cost": Decimal("0.000000"),
                }
            provider_map[key]["count"] += 1
            provider_map[key]["tokens"] += getattr(r, "total_tokens", 0) or 0
            if getattr(r, "estimated_cost_usd", None) is not None:
                provider_map[key]["cost"] += Decimal(str(r.estimated_cost_usd))

        provider_breakdown = [
            ProviderCostAggregate(
                provider=item["provider"],
                model=item["model"],
                request_count=item["count"],
                total_tokens=item["tokens"],
                total_cost_usd=item["cost"],
            )
            for item in provider_map.values()
        ]

        return ATIMTelemetryAggregate(
            tenant_id=tenant_id,
            total_requests=total_requests,
            security_blocked_requests=blocked_count,
            security_block_rate=round(blocked_count / total_requests, 4),
            fallback_requests=fallback_count,
            total_prompt_tokens=prompt_tokens,
            total_completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            latency_distribution=latency_dist,
            provider_breakdown=provider_breakdown,
        )
