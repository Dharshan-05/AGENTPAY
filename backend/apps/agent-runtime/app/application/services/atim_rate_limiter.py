"""ATIM Atomic Sliding-Window Rate Limiter Engine (Phase 18 / Group 9)."""

from datetime import datetime, timedelta
import logging
from typing import Optional
import uuid

from app.domain.governance.policy_models import RateLimitAlgorithm, RateLimitRecord

logger = logging.getLogger("agentpay.atim.rate_limiter")


class ATIMRateLimiter:
    """Sliding-window rate limiter evaluated by tenant_id, agent_id, and endpoint dimensions."""

    def __init__(self, default_limit: int = 100, window_seconds: int = 60) -> None:
        self.default_limit = default_limit
        self.window_seconds = window_seconds
        # Atomic sliding window request timestamps store
        self._sliding_windows: dict[tuple[str, str], list[datetime]] = {}

    def check_rate_limit(
        self,
        tenant_id: uuid.UUID,
        endpoint: str = "/api/v1/atim/analyze",
        agent_id: Optional[uuid.UUID] = None,
        limit_override: Optional[int] = None,
    ) -> RateLimitRecord:
        """Check if request exceeds sliding-window rate limit.

        Returns:
            RateLimitRecord (allowed: bool, limit: int, remaining: int, retry_after_seconds: int)
        """
        now = datetime.utcnow()
        limit = limit_override if limit_override is not None else self.default_limit
        cutoff = now - timedelta(seconds=self.window_seconds)

        key = (f"tenant:{tenant_id}", f"endpoint:{endpoint}")
        if agent_id:
            key = (f"tenant:{tenant_id}:agent:{agent_id}", f"endpoint:{endpoint}")

        timestamps = self._sliding_windows.get(key, [])
        # Prune expired timestamps
        valid_timestamps = [t for t in timestamps if t > cutoff]

        if len(valid_timestamps) >= limit:
            oldest = valid_timestamps[0]
            retry_after = max(1, int((oldest + timedelta(seconds=self.window_seconds) - now).total_seconds()))
            logger.warning(
                "Rate limit EXCEEDED for Tenant %s (Endpoint %s): %d/%d requests in %ds. Retry after %ds",
                tenant_id,
                endpoint,
                len(valid_timestamps),
                limit,
                self.window_seconds,
                retry_after,
            )
            return RateLimitRecord(
                allowed=False,
                tenant_id=tenant_id,
                agent_id=agent_id,
                limit=limit,
                remaining=0,
                retry_after_seconds=retry_after,
                algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
            )

        valid_timestamps.append(now)
        self._sliding_windows[key] = valid_timestamps
        remaining = limit - len(valid_timestamps)

        return RateLimitRecord(
            allowed=True,
            tenant_id=tenant_id,
            agent_id=agent_id,
            limit=limit,
            remaining=remaining,
            retry_after_seconds=0,
            algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        )
