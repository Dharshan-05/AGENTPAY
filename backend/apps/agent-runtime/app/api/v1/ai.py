"""FastAPI Router for AI Model Catalog & Neural Routing Endpoints."""

from __future__ import annotations

import logging
from typing import Any
from fastapi import APIRouter, status

from app.core.config import Settings

logger = logging.getLogger("agentpay.api.v1.ai")

router = APIRouter(prefix="/ai", tags=["AI Models & Neural Router"])


@router.get("/models", status_code=status.HTTP_200_OK)
async def list_available_ai_models() -> dict[str, Any]:
    """Retrieve normalized AI model catalog and active routing status for frontend model selector.

    INVARIANT: API keys are NEVER exposed in this response.
    """
    settings = Settings()
    has_openrouter = bool(settings.openrouter_api_key)

    configured_models = [
        {
            "id": "auto",
            "name": "Auto (Neural Router)",
            "provider": "AGENTPAY Router",
            "badge": "AUTO-ROUTE",
            "description": "Automatically selects the best model for intent performance and latency",
            "available": True,
        },
        {
            "id": "google/gemini-2.5-flash",
            "name": "Gemini 2.5 Flash",
            "provider": "Google",
            "badge": "FAST & ACCURATE",
            "description": "High-speed multimodal intelligence optimized for commerce search",
            "available": has_openrouter or bool(settings.gemini_api_key),
        },
        {
            "id": "anthropic/claude-3.5-haiku",
            "name": "Claude 3.5 Haiku",
            "provider": "Anthropic",
            "badge": "EXCELLENT REASONING",
            "description": "Precision intent classification and complex comparative reasoning",
            "available": has_openrouter or bool(settings.anthropic_api_key),
        },
        {
            "id": "openai/gpt-4o-mini",
            "name": "GPT-4o Mini",
            "provider": "OpenAI",
            "badge": "PRODUCTION DEFAULT",
            "description": "Proven balanced model for structured intent extraction and product ranking",
            "available": has_openrouter or bool(settings.openai_api_key),
        },
        {
            "id": "deepseek/deepseek-r1-distill-llama-70b",
            "name": "DeepSeek R1 70B",
            "provider": "DeepSeek",
            "badge": "DEEP REASONING",
            "description": "Advanced open-weight reasoning model for detailed product comparison",
            "available": has_openrouter,
        },
        {
            "id": "qwen/qwen-2.5-72b-instruct",
            "name": "Qwen 2.5 72B",
            "provider": "Alibaba Cloud",
            "badge": "COMMERCE LEADER",
            "description": "High-performance multilingual model for global product specifications",
            "available": has_openrouter,
        },
    ]

    return {
        "status": "LIVE",
        "provider": "OpenRouter & Native Providers" if has_openrouter else "Native Multi-Provider",
        "openrouter_enabled": has_openrouter,
        "default_model": "auto",
        "models": configured_models,
    }
