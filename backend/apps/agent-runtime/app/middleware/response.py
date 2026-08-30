"""Response standardization middleware for AGENTPAY backend services."""

import json
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.exceptions.codes import ErrorCode

UNWRAPPED_PATH_PREFIXES: tuple[str, ...] = (
    "/openapi.json",
    "/docs",
    "/redoc",
)

STATUS_CODE_TO_ERROR_CODE: dict[int, ErrorCode] = {
    status.HTTP_400_BAD_REQUEST: ErrorCode.VALIDATION_ERROR,
    status.HTTP_401_UNAUTHORIZED: ErrorCode.UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN: ErrorCode.FORBIDDEN,
    status.HTTP_404_NOT_FOUND: ErrorCode.RESOURCE_NOT_FOUND,
    status.HTTP_405_METHOD_NOT_ALLOWED: ErrorCode.APPLICATION_ERROR,
    status.HTTP_409_CONFLICT: ErrorCode.RESOURCE_CONFLICT,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorCode.INTERNAL_ERROR,
    status.HTTP_503_SERVICE_UNAVAILABLE: ErrorCode.SERVICE_UNAVAILABLE,
}


class ResponseStandardizationMiddleware(BaseHTTPMiddleware):
    """ASGI HTTP middleware for standardizing API JSON payloads into canonical envelopes."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Intercept responses and wrap into canonical SuccessResponse or ErrorResponse envelope."""
        response = await call_next(request)

        # 1. Skip HEAD requests (HEAD responses must not contain body)
        if request.method == "HEAD":
            return response

        # 2. Skip 204 No Content (HTTP 204 responses MUST remain bodyless)
        if response.status_code == 204:
            return response

        # 3. Skip OpenAPI, Swagger, ReDoc documentation routes
        path = request.url.path
        if any(path == p or path.startswith(p) for p in UNWRAPPED_PATH_PREFIXES):
            return response

        # 4. Inspect content-type header
        content_type = response.headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            return response

        # 5. Read response body
        body_bytes = b""
        async for chunk in response.body_iterator:  # type: ignore[attr-defined]
            body_bytes += chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")

        if not body_bytes:
            return response

        try:
            payload = json.loads(body_bytes.decode("utf-8"))
        except Exception:
            # If body is not valid JSON, return original response
            headers = dict(response.headers)
            headers.pop("content-length", None)
            headers.pop("Content-Length", None)
            return Response(
                content=body_bytes,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )

        # 6. Prevent double-wrapping: check if payload is already a standardized envelope
        if isinstance(payload, dict) and "success" in payload:
            headers = dict(response.headers)
            headers.pop("content-length", None)
            headers.pop("Content-Length", None)
            return Response(
                content=body_bytes,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )

        request_id = getattr(request.state, "request_id", "")
        headers = dict(response.headers)
        headers.pop("content-length", None)
        headers.pop("Content-Length", None)

        # 7. Standardize error responses >= 400 that were not handled by exception handlers
        if response.status_code >= 400:
            code = STATUS_CODE_TO_ERROR_CODE.get(response.status_code, ErrorCode.INTERNAL_ERROR)
            msg = (
                payload.get("detail", "An error occurred.")
                if isinstance(payload, dict)
                else str(payload)
            )
            wrapped_error: dict[str, Any] = {
                "success": False,
                "error": {
                    "code": code.value,
                    "message": msg,
                    "details": None,
                },
                "meta": {
                    "request_id": request_id,
                },
            }
            return JSONResponse(
                status_code=response.status_code,
                content=wrapped_error,
                headers=headers,
            )

        # 8. Standardize successful payload < 400
        wrapped_success: dict[str, Any] = {
            "success": True,
            "data": payload,
            "meta": {
                "request_id": request_id,
            },
        }

        return JSONResponse(
            status_code=response.status_code,
            content=wrapped_success,
            headers=headers,
        )
