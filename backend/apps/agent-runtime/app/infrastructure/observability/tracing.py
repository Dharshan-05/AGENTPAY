"""OpenTelemetry-compatible distributed tracing span manager for ATIM (Phase 13 / Group 7)."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, Optional

from app.infrastructure.observability.context import get_correlation_context
from app.infrastructure.observability.sanitization import TelemetrySanitizer


class ATIMTracer:
    """Tracer creating OpenTelemetry-compatible spans for ATIM pipeline stages."""

    def __init__(self) -> None:
        self.active_spans: list[dict[str, Any]] = []

    @contextmanager
    def start_span(
        self,
        span_name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Generator[dict[str, Any], None, None]:
        """Context manager creating a trace span with sanitized attributes."""
        ctx = get_correlation_context()
        attr = attributes or {}
        sanitized_attr = TelemetrySanitizer.sanitize_dict(attr)

        span = {
            "name": span_name,
            "correlation_id": ctx.correlation_id,
            "trace_id": ctx.trace_id,
            "attributes": sanitized_attr,
            "status": "OK",
        }
        self.active_spans.append(span)

        try:
            yield span
        except Exception as exc:
            span["status"] = "ERROR"
            span["attributes"]["error.message"] = str(exc)[:256]
            raise exc
