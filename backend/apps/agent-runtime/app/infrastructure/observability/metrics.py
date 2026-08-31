"""Prometheus metrics collector module for ATIM (Phase 13 / Group 7)."""

from decimal import Decimal
from typing import Any


class ATIMMetricsCollector:
    """Metrics collector for ATIM requests, latencies, tokens, costs, and security events."""

    def __init__(self) -> None:
        self.requests_total: dict[tuple[str, str], int] = {}
        self.security_blocks_total: dict[str, int] = {}
        self.dependency_failures_total: dict[str, int] = {}
        self.llm_cost_total_usd: Decimal = Decimal("0.000000")
        self.llm_latency_sum_ms: float = 0.0
        self.llm_latency_count: int = 0

    def record_request(self, task_type: str = "INTENT_EXTRACTION", status: str = "SUCCESS") -> None:
        """Increment request total metric with controlled label cardinality."""
        key = (task_type, status)
        self.requests_total[key] = self.requests_total.get(key, 0) + 1

    def record_security_block(self, block_type: str = "PROMPT_INJECTION") -> None:
        """Increment security block counter metric."""
        self.security_blocks_total[block_type] = self.security_blocks_total.get(block_type, 0) + 1

    def record_dependency_failure(self, dependency_name: str) -> None:
        """Increment dependency failure counter metric."""
        self.dependency_failures_total[dependency_name] = self.dependency_failures_total.get(dependency_name, 0) + 1

    def record_llm_telemetry(self, latency_ms: float, cost_usd: Decimal) -> None:
        """Record LLM latency and cost expenditure metrics."""
        self.llm_latency_sum_ms += latency_ms
        self.llm_latency_count += 1
        self.llm_cost_total_usd += cost_usd

    def get_summary(self) -> dict[str, Any]:
        """Return Prometheus metric summary dictionary."""
        avg_latency = self.llm_latency_sum_ms / self.llm_latency_count if self.llm_latency_count > 0 else 0.0
        return {
            "total_requests": sum(self.requests_total.values()),
            "total_security_blocks": sum(self.security_blocks_total.values()),
            "total_dependency_failures": sum(self.dependency_failures_total.values()),
            "avg_latency_ms": round(avg_latency, 2),
            "total_cost_usd": str(self.llm_cost_total_usd),
        }
