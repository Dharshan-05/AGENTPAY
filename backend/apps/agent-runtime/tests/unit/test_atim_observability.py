"""Unit tests for ATIM Observability, Telemetry Sanitization & Metrics (Phase 13 / Group 7)."""

from decimal import Decimal
import uuid

import pytest

from app.infrastructure.observability import (
    ATIMHealthChecker,
    ATIMMetricsCollector,
    ATIMStructuredLogger,
    ATIMTracer,
    CorrelationContext,
    TelemetrySanitizer,
    get_correlation_context,
    set_correlation_context,
)


def test_01_correlation_context_propagation():
    ctx = CorrelationContext(tenant_id=uuid.uuid4(), agent_id=uuid.uuid4())
    set_correlation_context(ctx)

    retrieved = get_correlation_context()
    assert retrieved.correlation_id.startswith("corr_")
    assert len(retrieved.trace_id) == 32
    assert retrieved.tenant_id == ctx.tenant_id


def test_02_telemetry_sanitizer_redacts_secrets_and_pii():
    text_with_secrets = "Authorization: Bearer secret_token_12345, password=MySecretPassword, card 4111-1111-1111-1111, email user@agentpay.io"
    clean = TelemetrySanitizer.sanitize_text(text_with_secrets)

    assert "secret_token_12345" not in clean
    assert "MySecretPassword" not in clean
    assert "4111-1111-1111-1111" not in clean
    assert "user@agentpay.io" not in clean
    assert "[REDACTED_BEARER_TOKEN]" in clean
    assert "[REDACTED_SECRET]" in clean
    assert "[REDACTED_CARD_NUMBER]" in clean
    assert "[REDACTED_EMAIL]" in clean


def test_03_structured_logger_json_format():
    log_event = ATIMStructuredLogger.log_event(
        event_name="test.llm.completion",
        payload={"model": "openai/gpt-4o", "password": "SuperSecretPassword123"},
    )

    assert log_event["service"] == "agent-runtime"
    assert log_event["component"] == "atim"
    assert log_event["event"] == "test.llm.completion"
    assert log_event["payload"]["password"] == "[REDACTED_SECRET]"


def test_04_metrics_collector_aggregation():
    metrics = ATIMMetricsCollector()
    metrics.record_request(task_type="PAYMENT", status="SUCCESS")
    metrics.record_security_block(block_type="PROMPT_INJECTION")
    metrics.record_llm_telemetry(latency_ms=120.0, cost_usd=Decimal("0.001500"))

    summary = metrics.get_summary()
    assert summary["total_requests"] == 1
    assert summary["total_security_blocks"] == 1
    assert summary["avg_latency_ms"] == 120.0
    assert summary["total_cost_usd"] == "0.001500"


def test_05_tracer_span_creation():
    tracer = ATIMTracer()
    with tracer.start_span("atim.security", {"bearer": "Bearer secret123"}) as span:
        assert span["name"] == "atim.security"
        assert span["status"] == "OK"
        assert span["attributes"]["bearer"] == "[REDACTED_BEARER_TOKEN]"


def test_06_health_checker():
    health = ATIMHealthChecker()
    assert health.check_liveness()["status"] == "UP"
    assert health.check_readiness()["status"] == "READY"

    health.set_dependency_health("database", False)
    assert health.check_readiness()["status"] == "NOT_READY"
