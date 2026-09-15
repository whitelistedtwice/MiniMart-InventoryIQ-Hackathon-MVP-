"""Inventory / product API routes (Phase 8)."""

from datetime import date, datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends

from app.ai_context.builder import build_recommendation_context
from app.api.dependencies import get_as_of, get_raw_sheets
from app.contracts.api import ProductDetailResponse, ProductListItem
from app.core.business import business_currency
from app.services.analysis import analyze, find

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=list[ProductListItem])
def list_products(
    raw: dict[str, list[dict[str, Any]]] = Depends(get_raw_sheets),
    as_of: Optional[date] = Depends(get_as_of),
) -> list[ProductListItem]:
    """Return the inventory product list, ordered by name."""
    analyses = analyze(raw, as_of)
    ordered = sorted(
        analyses,
        key=lambda item: (item.analytics.product_name.casefold(), item.analytics.product_id),
    )
    return [item.list_item() for item in ordered]


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product(
    product_id: str,
    raw: dict[str, list[dict[str, Any]]] = Depends(get_raw_sheets),
    as_of: Optional[date] = Depends(get_as_of),
) -> ProductDetailResponse:
    """Return full detail for exactly one product."""
    item = find(analyze(raw, as_of), product_id)
    return ProductDetailResponse(
        product_id=item.analytics.product_id,
        analytics=item.analytics,
        recommendation=item.recommendation,
        ai_context=build_recommendation_context(
            item.context(), generated_at=datetime.now(), currency=business_currency()
        ),
        historical_inventory=item.analytics.inventory_history,
    )
