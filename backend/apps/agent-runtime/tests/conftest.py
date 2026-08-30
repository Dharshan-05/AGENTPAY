"""Pytest configuration and shared test fixtures."""

from collections.abc import AsyncGenerator, Generator
from typing import Any, cast

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

import app.infrastructure.database.models as _models  # noqa: F401
from app.infrastructure.database.base import Base
from app.main import create_app


@compiles(UUID, "sqlite")  # type: ignore[no-untyped-call,untyped-decorator]
def compile_uuid_sqlite(type_: Any, compiler: Any, **kw: Any) -> str:
    return "CHAR(36)"


@compiles(JSONB, "sqlite")  # type: ignore[no-untyped-call,untyped-decorator]
def compile_jsonb_sqlite(type_: Any, compiler: Any, **kw: Any) -> str:
    return "TEXT"


@pytest.fixture
def app() -> FastAPI:
    """Fixture providing a fresh FastAPI application instance."""
    return create_app()


@pytest.fixture
def client(app: FastAPI) -> Generator[TestClient, None, None]:
    """Fixture providing a synchronous TestClient."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Fixture providing an asynchronous AsyncClient."""
    transport = ASGITransport(app=cast(Any, app))
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture providing an in-memory AsyncSession for database unit testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()
