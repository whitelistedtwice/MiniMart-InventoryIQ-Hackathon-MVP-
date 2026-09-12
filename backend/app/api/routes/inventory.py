"""
Inventory / product API routes.

Phase 12 will wire this to real data. Phase 1 defines the contract only.
"""

from datetime import date, datetime

from fastapi import APIRouter

from app.contracts.ai_context import AIProductContext, AIRecommendationContext
from app.contracts.analytics import (
    DemandMetrics,
    DemandTrend,
    FinancialMetrics,
    InventoryMetrics,
    ProductAnalytics,
    ShipmentProjection,
)
from app.contracts.api import ProductDetailResponse, ProductListItem
from app.contracts.recommendation import RecommendationAction, RecommendationResult

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=list[ProductListItem])
def list_products() -> list[ProductListItem]:
    """Return the inventory product list."""
    return []


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(product_id: str) -> ProductDetailResponse:
    """Return full product detail for one product."""
    analytics = ProductAnalytics(
        product_id=product_id,
        product_name="Sample Product",
        demand=DemandMetrics(trend=DemandTrend.UNAVAILABLE),
        inventory=InventoryMetrics(current_stock=None),
        shipment=ShipmentProjection(),
        financial=FinancialMetrics(),
    )
    recommendation = RecommendationResult(
        product_id=product_id,
        product_name=analytics.product_name,
        action=RecommendationAction.UNAVAILABLE,
    )
    ai_context = AIRecommendationContext(
        generated_at=datetime.now(),
        product=AIProductContext(
            product_id=product_id,
            product_name=analytics.product_name,
            current_stock=None,
            recommendation_action=RecommendationAction.UNAVAILABLE,
        ),
    )
    return ProductDetailResponse(
        product_id=product_id,
        analytics=analytics,
        recommendation=recommendation,
        ai_context=ai_context,
        historical_inventory=[],
    )
