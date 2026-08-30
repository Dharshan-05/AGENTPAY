"""FastAPI application entry point for AGENTPAY backend service."""

from fastapi import FastAPI

from app.bootstrap import bootstrap_app


def create_app() -> FastAPI:
    """Application factory for AGENTPAY FastAPI application.

    Delegates to the service bootstrap coordinator for idempotent and deterministic setup.
    """
    return bootstrap_app()


app = create_app()
