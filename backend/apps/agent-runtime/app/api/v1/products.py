"""Product Management, Search, Comparison, Ranking, Recommendation, Inventory & Offers REST controller router for AGENTPAY (Phase 164 & 168-178)."""  # noqa: E501

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import AuthenticatedUser, get_current_user
from app.api.dependencies.authorization import require_permission
from app.application.services.inventory_check_service import InventoryCheckService
from app.application.services.inventory_validation_service import InventoryValidationService
from app.application.services.offer_optimization_service import OfferOptimizationService
from app.application.services.offer_service import OfferService
from app.application.services.personalization_service import PersonalizationService
from app.application.services.product_comparison_service import ProductComparisonService
from app.application.services.product_ranking_service import ProductRankingService
from app.application.services.product_search_service import ProductSearchService
from app.application.services.product_service import ProductService
from app.application.services.recommendation_service import RecommendationService
from app.domain.authorization.permissions_registry import (
    PRODUCTS_ARCHIVE,
    PRODUCTS_CREATE,
    PRODUCTS_READ,
    PRODUCTS_UPDATE,
)
from app.domain.exceptions.agent_exceptions import (
    MerchantNotFoundError,
    ProductAlreadyExistsError,
    ProductNotFoundError,
    ProductValidationError,
)
from app.infrastructure.database.session import get_db_session
from app.schemas.inventory import (
    InventoryCheckResult,
    InventoryValidationItem,
    InventoryValidationResponse,
)
from app.schemas.offer_optimization import OfferOptimizationResponse
from app.schemas.offers import OfferListResponse
from app.schemas.product_comparison import ProductComparisonResponse
from app.schemas.product_personalization import PersonalizedRecommendationResponse
from app.schemas.product_ranking import ProductRankingResponse
from app.schemas.product_recommendations import RecommendationResponse
from app.schemas.product_search import ProductSearchResponse, SemanticProductSearchResponse
from app.schemas.products import (
    ProductCreateRequest,
    ProductListResponse,
    ProductResponse,
    ProductUpdateRequest,
)

logger = logging.getLogger("agentpay.api.products")

products_router = APIRouter(prefix="/products", tags=["Commerce Engine - Products"])


def get_product_service() -> ProductService:
    """Dependency factory for ProductService."""
    return ProductService()


def get_product_search_service() -> ProductSearchService:
    """Dependency factory for ProductSearchService."""
    return ProductSearchService()


def get_product_comparison_service() -> ProductComparisonService:
    """Dependency factory for ProductComparisonService."""
    return ProductComparisonService()


def get_product_ranking_service() -> ProductRankingService:
    """Dependency factory for ProductRankingService."""
    return ProductRankingService()


def get_recommendation_service() -> RecommendationService:
    """Dependency factory for RecommendationService."""
    return RecommendationService()


def get_personalization_service() -> PersonalizationService:
    """Dependency factory for PersonalizationService."""
    return PersonalizationService()


def get_inventory_check_service() -> InventoryCheckService:
    """Dependency factory for InventoryCheckService."""
    return InventoryCheckService()


def get_inventory_validation_service() -> InventoryValidationService:
    """Dependency factory for InventoryValidationService."""
    return InventoryValidationService()


def get_offer_service() -> OfferService:
    """Dependency factory for OfferService."""
    return OfferService()


def get_offer_optimization_service() -> OfferOptimizationService:
    """Dependency factory for OfferOptimizationService."""
    return OfferOptimizationService()


@products_router.get(
    "/{product_id}/offers/optimize",
    response_model=OfferOptimizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Optimize Product Offers",
    description="Evaluate applicable commercial offers and select optimal customer savings (Phase 179).",  # noqa: E501
    operation_id="optimize_product_offers",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def optimize_product_offers(
    product_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    opt_service: Annotated[OfferOptimizationService, Depends(get_offer_optimization_service)],
    quantity: Annotated[Decimal, Query(gt=0, description="Evaluated purchase quantity")] = Decimal(
        "1.000"
    ),
) -> OfferOptimizationResponse:
    """Find optimal offer for product and quantity."""
    try:
        return await opt_service.optimize_offer(
            db, tenant_id=current_user.tenant_id, product_id=product_id, quantity=quantity
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Product",
    description="Create a new Product entity for a Merchant in AGENTPAY (Phase 164).",
    operation_id="create_product",
    dependencies=[Depends(require_permission(PRODUCTS_CREATE))],
)
async def create_product(
    request: ProductCreateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductResponse:
    """Create a new product with tenant & merchant isolation."""
    try:
        return await service.create_product(db, tenant_id=current_user.tenant_id, request=request)
    except MerchantNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.get(
    "",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Products",
    description="List tenant-scoped products supporting filtering, sorting, and keyset pagination (Phase 164/170/171).",  # noqa: E501
    operation_id="list_products",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def list_products(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ProductService, Depends(get_product_service)],
    merchant_id: Annotated[
        uuid.UUID | None, Query(description="Optional filter by merchant UUID")
    ] = None,
    status_filter: Annotated[
        str | None, Query(alias="status", description="Optional filter by product status")
    ] = None,
    currency: Annotated[
        str | None, Query(description="Optional filter by ISO currency code")
    ] = None,
    min_price: Annotated[Decimal | None, Query(description="Optional minimum price filter")] = None,
    max_price: Annotated[Decimal | None, Query(description="Optional maximum price filter")] = None,
    created_after: Annotated[
        datetime | None, Query(description="Filter created on or after datetime")
    ] = None,
    created_before: Annotated[
        datetime | None, Query(description="Filter created on or before datetime")
    ] = None,
    sort_by: Annotated[
        str, Query(description="Sort column (created_at, updated_at, name, price, sku)")
    ] = "created_at",
    sort_dir: Annotated[str, Query(description="Sort direction (asc, desc)")] = "desc",
    cursor_created_at: Annotated[
        datetime | None, Query(description="Keyset cursor datetime")
    ] = None,
    cursor_id: Annotated[uuid.UUID | None, Query(description="Keyset cursor UUID")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Page limit")] = 20,
) -> ProductListResponse:
    """List products for tenant with filtering and sorting."""
    try:
        return await service.list_products(
            db,
            tenant_id=current_user.tenant_id,
            merchant_id=merchant_id,
            status=status_filter,
            currency=currency,
            min_price=min_price,
            max_price=max_price,
            created_after=created_after,
            created_before=created_before,
            sort_by=sort_by,
            sort_dir=sort_dir,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
            limit=limit,
        )
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.get(
    "/search",
    response_model=ProductSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Products (Keyword)",
    description="Search tenant products by keyword/text over SKU, name, and description (Phase 168).",  # noqa: E501
    operation_id="search_products",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def search_products(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    search_service: Annotated[ProductSearchService, Depends(get_product_search_service)],
    q: Annotated[str, Query(description="Search query string")],
    merchant_id: Annotated[
        uuid.UUID | None, Query(description="Optional filter by merchant UUID")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Result limit")] = 20,
) -> ProductSearchResponse:
    """Keyword search for products."""
    try:
        return await search_service.search_products(
            db, tenant_id=current_user.tenant_id, query=q, merchant_id=merchant_id, limit=limit
        )
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.get(
    "/semantic-search",
    response_model=SemanticProductSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search Products (Semantic Vector)",
    description="Search tenant products using vector cosine similarity and hybrid scoring (Phase 169).",  # noqa: E501
    operation_id="semantic_search_products",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def semantic_search_products(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    search_service: Annotated[ProductSearchService, Depends(get_product_search_service)],
    q: Annotated[str, Query(description="Natural language query string")],
    merchant_id: Annotated[
        uuid.UUID | None, Query(description="Optional filter by merchant UUID")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Result limit")] = 20,
    hybrid: Annotated[bool, Query(description="Enable hybrid score weighting")] = True,
) -> SemanticProductSearchResponse:
    """Semantic vector search for products."""
    try:
        return await search_service.semantic_search_products(
            db,
            tenant_id=current_user.tenant_id,
            query=q,
            merchant_id=merchant_id,
            limit=limit,
            hybrid=hybrid,
        )
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.get(
    "/compare",
    response_model=ProductComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Products",
    description="Compare 2 to 5 products side-by-side with metrics (Phase 172).",
    operation_id="compare_products",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def compare_products(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    comparison_service: Annotated[
        ProductComparisonService, Depends(get_product_comparison_service)
    ],
    product_ids: Annotated[
        list[uuid.UUID], Query(description="List of 2 to 5 product UUIDs to compare")
    ],
) -> ProductComparisonResponse:
    """Compare multiple products."""
    try:
        return await comparison_service.compare_products(
            db, tenant_id=current_user.tenant_id, product_ids=product_ids
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.get(
    "/rank",
    response_model=ProductRankingResponse,
    status_code=status.HTTP_200_OK,
    summary="Rank Products",
    description="Rank candidate products using transparent multi-signal explainable scoring (Phase 173).",  # noqa: E501
    operation_id="rank_products",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def rank_products(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    ranking_service: Annotated[ProductRankingService, Depends(get_product_ranking_service)],
    q: Annotated[str, Query(description="Ranking query string")],
    merchant_id: Annotated[
        uuid.UUID | None, Query(description="Optional filter by merchant UUID")
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Result limit")] = 20,
) -> ProductRankingResponse:
    """Rank candidate products."""
    try:
        return await ranking_service.rank_products(
            db, tenant_id=current_user.tenant_id, query=q, merchant_id=merchant_id, limit=limit
        )
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.get(
    "/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Product Recommendations",
    description="Get deduplicated, bounded product recommendations (Phase 174).",
    operation_id="get_product_recommendations",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def get_product_recommendations(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    recommendation_service: Annotated[RecommendationService, Depends(get_recommendation_service)],
    recommendation_type: Annotated[
        str, Query(description="Type: similar_products, related_products")
    ] = "similar_products",
    target_product_id: Annotated[
        uuid.UUID | None, Query(description="Optional target product UUID to compare against")
    ] = None,
    q: Annotated[str | None, Query(alias="query", description="Optional search query")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Result limit")] = 10,
) -> RecommendationResponse:
    """Get product recommendations."""
    try:
        return await recommendation_service.get_recommendations(
            db,
            tenant_id=current_user.tenant_id,
            recommendation_type=recommendation_type,
            target_product_id=target_product_id,
            query=q,
            limit=limit,
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.get(
    "/personalized",
    response_model=PersonalizedRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Personalized Product Recommendations",
    description="Get memory-boosted personalized recommendations for agent/user (Phase 175).",
    operation_id="get_personalized_recommendations",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def get_personalized_recommendations(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    personalization_service: Annotated[
        PersonalizationService, Depends(get_personalization_service)
    ],
    agent_id: Annotated[
        uuid.UUID | None, Query(description="Optional agent UUID to extract preferences from")
    ] = None,
    q: Annotated[
        str, Query(alias="query", description="Query context string")
    ] = "catalog products",
    limit: Annotated[int, Query(ge=1, le=100, description="Result limit")] = 10,
) -> PersonalizedRecommendationResponse:
    """Get personalized recommendations."""
    return await personalization_service.get_personalized_recommendations(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.user.id,
        agent_id=agent_id,
        query=q,
        limit=limit,
    )


@products_router.post(
    "/inventory/validate",
    response_model=InventoryValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate Inventory Quantities (Advisory)",
    description="Validate requested purchase quantities against inventory stock in read-only advisory mode (Phase 177).",  # noqa: E501
    operation_id="validate_inventory",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def validate_inventory(
    items: list[InventoryValidationItem],
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    validation_service: Annotated[
        InventoryValidationService, Depends(get_inventory_validation_service)
    ],
) -> InventoryValidationResponse:
    """Read-only advisory validation for requested purchase quantities."""
    try:
        return await validation_service.validate_inventory(
            db, tenant_id=current_user.tenant_id, items=items
        )
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Product Detail",
    description="Lookup a product by product_id within tenant scope (Phase 164).",
    operation_id="get_product",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def get_product(
    product_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductResponse:
    """Lookup product detail."""
    try:
        return await service.get_product(
            db, tenant_id=current_user.tenant_id, product_id=product_id
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@products_router.get(
    "/{product_id}/inventory",
    response_model=InventoryCheckResult,
    status_code=status.HTTP_200_OK,
    summary="Check Product Inventory",
    description="Perform read-only stock availability check for a product (Phase 176).",
    operation_id="check_product_inventory",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def check_product_inventory(
    product_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    check_service: Annotated[InventoryCheckService, Depends(get_inventory_check_service)],
    quantity: Annotated[Decimal, Query(gt=0, description="Requested quantity check")] = Decimal(
        "1.000"
    ),
) -> InventoryCheckResult:
    """Check product inventory availability."""
    try:
        return await check_service.check_inventory(
            db, tenant_id=current_user.tenant_id, product_id=product_id, requested_quantity=quantity
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.get(
    "/{product_id}/offers",
    response_model=OfferListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Product Commercial Offers",
    description="Retrieve active commercial offers and discount calculations for a product (Phase 178).",  # noqa: E501
    operation_id="get_product_offers",
    dependencies=[Depends(require_permission(PRODUCTS_READ))],
)
async def get_product_offers(
    product_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    offer_service: Annotated[OfferService, Depends(get_offer_service)],
    quantity: Annotated[Decimal, Query(gt=0, description="Requested quantity")] = Decimal("1.000"),
) -> OfferListResponse:
    """Get active commercial offers for a product."""
    try:
        return await offer_service.get_product_offers(
            db, tenant_id=current_user.tenant_id, product_id=product_id, requested_quantity=quantity
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Product",
    description="Update an existing product's attributes (Phase 164).",
    operation_id="update_product",
    dependencies=[Depends(require_permission(PRODUCTS_UPDATE))],
)
async def update_product(
    product_id: uuid.UUID,
    request: ProductUpdateRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductResponse:
    """Update product attributes."""
    try:
        return await service.update_product(
            db, tenant_id=current_user.tenant_id, product_id=product_id, request=request
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@products_router.post(
    "/{product_id}/archive",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Archive Product",
    description="Archive (soft delete) a product (Phase 164).",
    operation_id="archive_product",
    dependencies=[Depends(require_permission(PRODUCTS_ARCHIVE))],
)
async def archive_product(
    product_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductResponse:
    """Archive a product."""
    try:
        return await service.archive_product(
            db, tenant_id=current_user.tenant_id, product_id=product_id
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@products_router.post(
    "/{product_id}/restore",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Restore Product",
    description="Restore an archived product (Phase 164).",
    operation_id="restore_product",
    dependencies=[Depends(require_permission(PRODUCTS_ARCHIVE))],
)
async def restore_product(
    product_id: uuid.UUID,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db_session)],
    service: Annotated[ProductService, Depends(get_product_service)],
) -> ProductResponse:
    """Restore an archived product."""
    try:
        return await service.restore_product(
            db, tenant_id=current_user.tenant_id, product_id=product_id
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
