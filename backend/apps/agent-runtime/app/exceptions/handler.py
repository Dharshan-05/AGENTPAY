"""Global exception handlers foundation."""

from json import JSONDecodeError

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.exceptions.base import AgentPayError
from app.middleware.exception import (
    agentpay_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers on the application.

    Serves as the central extension point for domain exceptions,
    validation errors, and security exception handling.
    """
    app.add_exception_handler(AgentPayError, agentpay_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    app.add_exception_handler(JSONDecodeError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
