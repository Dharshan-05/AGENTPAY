"""Exception translation middleware for AGENTPAY backend services."""

import logging
from json import JSONDecodeError
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.logging import sanitize_structured_data
from app.exceptions.base import AgentPayError
from app.exceptions.codes import ErrorCode

logger = logging.getLogger("agentpay.middleware.exception")

REQUEST_ID_HEADER = "X-Request-ID"

SENSITIVE_KEY_SUBSTRINGS: tuple[str, ...] = (
    "password",
    "token",
    "secret",
    "api_key",
    "apikey",
    "authorization",
    "cookie",
    "private_key",
    "credentials",
)

# Mapping ErrorCode enum values to HTTP status codes
ERROR_CODE_STATUS_MAP: dict[ErrorCode, int] = {
    ErrorCode.RESOURCE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCode.RESOURCE_CONFLICT: status.HTTP_409_CONFLICT,
    ErrorCode.VALIDATION_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.DOMAIN_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.APPLICATION_ERROR: status.HTTP_400_BAD_REQUEST,
    ErrorCode.INVALID_CONFIGURATION: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.INFRASTRUCTURE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.SERVICE_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    ErrorCode.INTERNAL_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCode.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
    ErrorCode.FORBIDDEN: status.HTTP_403_FORBIDDEN,
}

# Inverse mapping HTTP status codes to default ErrorCode
STATUS_CODE_TO_ERROR_CODE: dict[int, ErrorCode] = {
    status.HTTP_400_BAD_REQUEST: ErrorCode.VALIDATION_ERROR,
    status.HTTP_401_UNAUTHORIZED: ErrorCode.UNAUTHORIZED,
    status.HTTP_403_FORBIDDEN: ErrorCode.FORBIDDEN,
    status.HTTP_404_NOT_FOUND: ErrorCode.RESOURCE_NOT_FOUND,
    status.HTTP_409_CONFLICT: ErrorCode.RESOURCE_CONFLICT,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorCode.INTERNAL_ERROR,
    status.HTTP_503_SERVICE_UNAVAILABLE: ErrorCode.SERVICE_UNAVAILABLE,
}


def _is_sensitive_location(loc_parts: tuple[Any, ...] | list[Any]) -> bool:
    """Check if any path element in location is a sensitive parameter name."""
    for part in loc_parts:
        part_str = str(part).lower()
        if any(sens in part_str for sens in SENSITIVE_KEY_SUBSTRINGS):
            return True
    return False


def build_error_response(
    code: ErrorCode | str,
    message: str,
    details: dict[str, Any] | list[Any] | None = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    request_id: str | None = None,
) -> JSONResponse:
    """Construct a canonical standardized safe JSON error response."""
    code_str = code.value if isinstance(code, ErrorCode) else str(code)
    sanitized_details: Any = None
    if isinstance(details, (dict, list)):
        sanitized_details = sanitize_structured_data(details)

    payload = {
        "success": False,
        "error": {
            "code": code_str,
            "message": message,
            "details": sanitized_details,
        },
        "meta": {
            "request_id": request_id or "",
        },
    }
    resp = JSONResponse(status_code=status_code, content=payload)
    if request_id:
        resp.headers[REQUEST_ID_HEADER] = request_id
    return resp


async def validation_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """FastAPI exception handler for RequestValidationError and malformed JSON payloads."""
    request_id = getattr(request.state, "request_id", None)
    log_extra = {
        "event": "application.error",
        "request_id": request_id,
        "error_code": ErrorCode.VALIDATION_ERROR.value,
        "error_type": exc.__class__.__name__,
        "path": request.url.path,
    }
    logger.info("Request validation failed: %s", request.url.path, extra=log_extra)

    formatted_details: list[dict[str, Any]] = []
    raw_errors: list[dict[str, Any]] = getattr(exc, "errors", list)()

    is_json_syntax_error = isinstance(exc, JSONDecodeError)
    if not is_json_syntax_error:
        for err in raw_errors:
            err_type = str(err.get("type", "")).lower()
            err_msg = str(err.get("msg", "")).lower()
            if "json" in err_type or "json" in err_msg or "decode" in err_type:
                is_json_syntax_error = True
                break

    if is_json_syntax_error:
        return build_error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="Invalid JSON payload syntax.",
            details=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            request_id=request_id,
        )

    for err in raw_errors:
        loc = err.get("loc", ())
        loc_str = ".".join(str(p) for p in loc) if loc else "body"

        if _is_sensitive_location(loc):
            err_msg = "Invalid sensitive parameter value."
        else:
            err_msg = str(err.get("msg", "Validation error."))
            for sens in SENSITIVE_KEY_SUBSTRINGS:
                if sens in err_msg.lower():
                    err_msg = "Validation failed for specified parameter."
                    break

        formatted_details.append(
            {
                "location": loc_str,
                "message": err_msg,
                "type": str(err.get("type", "validation_error")),
            }
        )

    return build_error_response(
        code=ErrorCode.VALIDATION_ERROR,
        message="Request validation failed.",
        details=formatted_details if formatted_details else None,
        status_code=status.HTTP_400_BAD_REQUEST,
        request_id=request_id,
    )


async def agentpay_exception_handler(request: Request, exc: AgentPayError) -> JSONResponse:
    """FastAPI exception handler for AgentPayError instances."""
    http_status = ERROR_CODE_STATUS_MAP.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    request_id = getattr(request.state, "request_id", None)

    log_extra = {
        "event": "application.error",
        "request_id": request_id,
        "error_code": exc.code.value,
        "error_type": exc.__class__.__name__,
        "path": request.url.path,
    }

    if http_status >= 500:
        logger.error("Internal application error: %s", exc.message, extra=log_extra)
    else:
        logger.info("Application exception occurred: %s", exc.message, extra=log_extra)

    return build_error_response(
        code=exc.code,
        message=exc.message,
        details=exc.details,
        status_code=http_status,
        request_id=request_id,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """FastAPI exception handler for HTTPException instances."""
    request_id = getattr(request.state, "request_id", None)
    code = STATUS_CODE_TO_ERROR_CODE.get(exc.status_code, ErrorCode.INTERNAL_ERROR)
    message = str(exc.detail) if exc.detail else "An error occurred."

    log_extra = {
        "event": "application.error",
        "request_id": request_id,
        "error_code": code.value,
        "error_type": exc.__class__.__name__,
        "path": request.url.path,
    }

    if exc.status_code >= 500:
        logger.error("HTTP Exception %d: %s", exc.status_code, message, extra=log_extra)
    else:
        logger.info("HTTP Exception %d: %s", exc.status_code, message, extra=log_extra)

    return build_error_response(
        code=code,
        message=message,
        details=None,
        status_code=exc.status_code,
        request_id=request_id,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """FastAPI exception handler for unhandled generic exceptions."""
    request_id = getattr(request.state, "request_id", None)
    log_extra = {
        "event": "application.error",
        "request_id": request_id,
        "error_code": ErrorCode.INTERNAL_ERROR.value,
        "error_type": exc.__class__.__name__,
        "path": request.url.path,
    }
    logger.exception("Unhandled application exception: %s", str(exc), extra=log_extra)

    return build_error_response(
        code=ErrorCode.INTERNAL_ERROR,
        message="An internal error occurred.",
        details=None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        request_id=request_id,
    )


class ExceptionMiddleware(BaseHTTPMiddleware):
    """ASGI HTTP Middleware for intercepting exceptions across the request stack."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process HTTP request and catch unhandled exceptions."""
        try:
            return await call_next(request)
        except AgentPayError as exc:
            return await agentpay_exception_handler(request, exc)
        except HTTPException as exc:
            return await http_exception_handler(request, exc)
        except Exception as exc:
            return await unhandled_exception_handler(request, exc)
