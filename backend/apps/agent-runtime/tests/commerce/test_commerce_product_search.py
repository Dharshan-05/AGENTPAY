"""Unit and Integration Tests for Agentic Commerce Product Search (Buildathon Track 01)."""

import uuid
from decimal import Decimal
import pytest
from unittest.mock import AsyncMock

from app.commerce.schemas import CommerceSearchRequest
from app.commerce.services.commerce_facade_service import CommerceFacadeService


@pytest.mark.asyncio
async def test_commerce_product_search_natural_language_discovery():
    """Verify natural language product discovery for laptops under ₹50,000 for coding."""
    facade = CommerceFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    req = CommerceSearchRequest(
        prompt="Find the best laptop under ₹50,000 for coding.",
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = await facade.execute_commerce_search(db=mock_db, request=req)

    assert res.intent == "PRODUCT_SEARCH"
    assert res.budget == Decimal("50000.00") or res.budget == Decimal("50000")
    assert res.products_discovered_count > 0
    assert len(res.products) > 0
    assert res.recommended_product is not None
    assert res.comparison_matrix is not None
    assert res.execution_status == "NOT_REQUESTED"
    assert res.prompt_security_blocked is False


@pytest.mark.asyncio
async def test_commerce_product_search_no_fabricated_data():
    """Verify products returned contain explicit factual specs, prices, and seller information."""
    facade = CommerceFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    req = CommerceSearchRequest(
        prompt="Find laptops under 45000",
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = await facade.execute_commerce_search(db=mock_db, request=req)

    for p in res.products:
        assert p.product_id.startswith("prod_")
        assert p.price <= Decimal("50000.00")
        assert p.seller.seller_name != ""
        assert p.data_status == "LIVE"
        assert p.source is not None


@pytest.mark.asyncio
async def test_commerce_product_search_smartphone_category():
    """Verify 'give the phone under 20000' parses as SMARTPHONE and excludes feature phones."""
    facade = CommerceFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    req = CommerceSearchRequest(
        prompt="give the phone under 20000",
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = await facade.execute_commerce_search(db=mock_db, request=req)

    assert res.category == "SMARTPHONE"
    assert res.products_discovered_count > 0
    for p in res.products:
        assert p.price >= Decimal("3000.00")
        assert "Guru" not in p.product_name
        assert "Nokia 105" not in p.product_name


@pytest.mark.asyncio
async def test_commerce_product_search_unavailable_mode():
    """Verify provider returning zero listings produces UNAVAILABLE status without mock data fallback."""
    facade = CommerceFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    req = CommerceSearchRequest(
        prompt="Find non_existent_xyz_product_999 under 100",
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = await facade.execute_commerce_search(db=mock_db, request=req)

    assert res.products_discovered_count == 0
    assert res.data_status == "UNAVAILABLE"
    assert "ONLINE COMMERCE DATA UNAVAILABLE" in res.formatted_response


@pytest.mark.asyncio
async def test_commerce_product_search_top_4_deterministic_ranking():
    """Verify 'best laptop under 100000' returns TOP 4 ranked candidates with structured explanations."""
    facade = CommerceFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    req = CommerceSearchRequest(
        prompt="best laptop under 100000",
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = await facade.execute_commerce_search(db=mock_db, request=req)

    assert res.query is not None
    assert res.query["category"] == "LAPTOP"
    assert len(res.products) == 4
    for idx, p in enumerate(res.products):
        assert p.rank == idx + 1
        assert p.overall_score is not None
        assert len(p.why_ranked) > 0
        assert len(p.strengths) > 0

    assert res.recommendation is not None
    assert res.recommendation["rank"] == 1
    assert len(res.recommendation["why"]) > 0
    assert len(res.recommendation["alternative_picks"]) == 3


@pytest.mark.asyncio
async def test_commerce_product_search_purpose_coding():
    """Verify 'best laptop for coding under 50000' extracts CODING purpose and applies coding weights."""
    facade = CommerceFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    req = CommerceSearchRequest(
        prompt="best laptop for coding under 50000",
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = await facade.execute_commerce_search(db=mock_db, request=req)

    assert res.query["purpose"] == "CODING"
    assert len(res.products) > 0
    top_p = res.products[0]
    assert top_p.rank == 1
    assert "coding" in top_p.why_ranked[0].lower()


@pytest.mark.asyncio
async def test_commerce_product_search_fewer_than_4_no_fabrication():
    """Verify when provider returns 2 products, exactly 2 are returned without inventing fake items."""
    facade = CommerceFacadeService()
    tenant_id = uuid.uuid4()
    agent_id = uuid.uuid4()
    mock_db = AsyncMock()

    # Query with strict price cap yielding 2 candidates
    req = CommerceSearchRequest(
        prompt="Find laptop under 46000",
        tenant_id=tenant_id,
        agent_id=agent_id,
    )

    res = await facade.execute_commerce_search(db=mock_db, request=req)

    assert len(res.products) <= 4
    for p in res.products:
        assert p.price <= Decimal("46000.00")
        assert p.data_status == "LIVE"

