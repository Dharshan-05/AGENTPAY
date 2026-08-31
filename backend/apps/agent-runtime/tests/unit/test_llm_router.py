"""Unit tests for LLMRouter failover, retries, and error handling."""

from __future__ import annotations

from unittest.mock import AsyncMock
import pytest
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.infrastructure.llm.base import ILLMProvider
from app.infrastructure.llm.exceptions import LLMProviderError
from app.infrastructure.llm.router import LLMRouter
from app.infrastructure.llm.schemas import (
    LLMRequest,
    LLMResponse,
    StructuredLLMResponse,
)


class SampleSchema(BaseModel):
    query: str = Field(description="Sample query")


@pytest.mark.asyncio
async def test_llm_router_primary_success():
    """Test router successfully executes using primary provider."""
    primary_mock = AsyncMock(spec=ILLMProvider)
    primary_mock.provider_name = "mock_primary"
    primary_mock.default_model = "mock-model-1"

    expected_resp = StructuredLLMResponse[SampleSchema](
        correlation_id=pytest.importorskip("uuid").uuid4(),
        provider="mock_primary",
        model="mock-model-1",
        data=SampleSchema(query="test"),
        raw_content='{"query": "test"}',
        latency_ms=10.0,
    )
    primary_mock.generate_structured.return_value = expected_resp

    router = LLMRouter(
        settings=Settings(llm_enabled=True),
        primary_provider=primary_mock,
        secondary_provider=AsyncMock(spec=ILLMProvider),
    )

    req = LLMRequest(prompt="Hello")
    res = await router.generate_structured(SampleSchema, req)

    assert res.provider == "mock_primary"
    assert res.data.query == "test"
    primary_mock.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_llm_router_primary_fail_secondary_success():
    """Test router fails over to secondary provider when primary raises exception."""
    primary_mock = AsyncMock(spec=ILLMProvider)
    primary_mock.provider_name = "mock_primary"
    primary_mock.default_model = "mock-model-1"
    primary_mock.generate_structured.side_effect = LLMProviderError("Primary API Timeout")

    secondary_mock = AsyncMock(spec=ILLMProvider)
    secondary_mock.provider_name = "mock_secondary"
    secondary_mock.default_model = "mock-model-2"

    expected_resp = StructuredLLMResponse[SampleSchema](
        correlation_id=pytest.importorskip("uuid").uuid4(),
        provider="mock_secondary",
        model="mock-model-2",
        data=SampleSchema(query="fallback_success"),
        raw_content='{"query": "fallback_success"}',
        latency_ms=15.0,
    )
    secondary_mock.generate_structured.return_value = expected_resp

    router = LLMRouter(
        settings=Settings(llm_enabled=True),
        primary_provider=primary_mock,
        secondary_provider=secondary_mock,
    )

    req = LLMRequest(prompt="Hello")
    res = await router.generate_structured(SampleSchema, req)

    assert res.provider == "mock_secondary"
    assert res.data.query == "fallback_success"
    primary_mock.generate_structured.assert_called_once()
    secondary_mock.generate_structured.assert_called_once()


@pytest.mark.asyncio
async def test_llm_router_both_fail_raises_provider_error():
    """Test router raises LLMProviderError when both primary and secondary fail."""
    primary_mock = AsyncMock(spec=ILLMProvider)
    primary_mock.provider_name = "mock_primary"
    primary_mock.default_model = "mock-model-1"
    primary_mock.generate_structured.side_effect = LLMProviderError("Primary Error")

    secondary_mock = AsyncMock(spec=ILLMProvider)
    secondary_mock.provider_name = "mock_secondary"
    secondary_mock.default_model = "mock-model-2"
    secondary_mock.generate_structured.side_effect = LLMProviderError("Secondary Error")

    router = LLMRouter(
        settings=Settings(llm_enabled=True),
        primary_provider=primary_mock,
        secondary_provider=secondary_mock,
    )

    req = LLMRequest(prompt="Hello")
    with pytest.raises(LLMProviderError):
        await router.generate_structured(SampleSchema, req)


@pytest.mark.asyncio
async def test_llm_router_disabled_raises_provider_error():
    """Test router raises LLMProviderError immediately when LLM_ENABLED=False."""
    router = LLMRouter(
        settings=Settings(llm_enabled=False),
        primary_provider=AsyncMock(spec=ILLMProvider),
        secondary_provider=AsyncMock(spec=ILLMProvider),
    )

    req = LLMRequest(prompt="Hello")
    with pytest.raises(LLMProviderError):
        await router.generate_structured(SampleSchema, req)
