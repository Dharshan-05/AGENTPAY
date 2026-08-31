"""Structured JSON logger module for ATIM (Phase 13 / Group 7)."""

import json
import logging
from typing import Any

from app.infrastructure.observability.context import get_correlation_context
from app.infrastructure.observability.sanitization import TelemetrySanitizer

logger = logging.getLogger("agentpay.atim.structured_logger")


class ATIMStructuredLogger:
    """Structured JSON logging component for ATIM pipeline events."""

    @staticmethod
    def log_event(
        event_name: str,
        level: str = "INFO",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Emit structured JSON telemetry log event."""
        ctx = get_correlation_context()
        raw_payload = payload or {}
        sanitized_payload = TelemetrySanitizer.sanitize_dict(raw_payload)

        log_data = {
            "service": "agent-runtime",
            "component": "atim",
            "event": event_name,
            "correlation_id": ctx.correlation_id,
            "trace_id": ctx.trace_id,
            "span_id": ctx.span_id,
            "tenant_id": str(ctx.tenant_id) if ctx.tenant_id else None,
            "agent_id": str(ctx.agent_id) if ctx.agent_id else None,
            "payload": sanitized_payload,
        }

        json_str = json.dumps(log_data)
        if level == "ERROR":
            logger.error(json_str)
        elif level == "WARNING":
            logger.warning(json_str)
        else:
            logger.info(json_str)

        return log_data
