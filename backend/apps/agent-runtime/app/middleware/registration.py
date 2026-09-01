"""Middleware foundation registration point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.middleware.api import APIMiddleware
from app.middleware.exception import ExceptionMiddleware
from app.middleware.request_id import REQUEST_ID_HEADER, RequestIDMiddleware
from app.middleware.response import ResponseStandardizationMiddleware


def register_middleware(app: FastAPI) -> None:
    """Register application middleware pipeline in deterministic order.

    Serves as the central extension point for middleware layers
    such as CORS, request tracing, rate limiting, and security headers.
    """
    settings = get_settings()

    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    app.add_middleware(APIMiddleware)
    app.add_middleware(ResponseStandardizationMiddleware)
    app.add_middleware(RequestIDMiddleware)
