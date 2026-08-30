"""Request ID / Correlation ID middleware for AGENTPAY backend services."""

import re
import uuid

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.exceptions.codes import ErrorCode
from app.middleware.exception import build_error_response

REQUEST_ID_HEADER = "X-Request-ID"
MAX_REQUEST_ID_LENGTH = 128
VALID_REQUEST_ID_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """ASGI HTTP middleware for establishing request correlation identity."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request, validate or generate request ID, and attach response header."""
        incoming_id = request.headers.get(REQUEST_ID_HEADER)

        if incoming_id is None or not incoming_id.strip():
            request_id = str(uuid.uuid4())
        else:
            clean_id = incoming_id.strip()
            if len(clean_id) > MAX_REQUEST_ID_LENGTH or not VALID_REQUEST_ID_PATTERN.match(
                clean_id
            ):
                return build_error_response(
                    code=ErrorCode.VALIDATION_ERROR,
                    message="Invalid request ID.",
                    details=None,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            request_id = clean_id

        # Store in request state for downstream handlers and logging
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
