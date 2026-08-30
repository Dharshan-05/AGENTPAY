"""Generic API HTTP lifecycle middleware for AGENTPAY backend services."""

import logging
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("agentpay.middleware.api")


class APIMiddleware(BaseHTTPMiddleware):
    """ASGI HTTP Middleware for observing request lifecycle duration and status."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process HTTP request, measure duration, and emit structured lifecycle logs."""
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            # Let downstream exception middleware handle exception translation
            raise
        else:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            request_id = getattr(request.state, "request_id", None)

            log_extra = {
                "event": "http.request",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }

            logger.info("HTTP request completed", extra=log_extra)
            return response
