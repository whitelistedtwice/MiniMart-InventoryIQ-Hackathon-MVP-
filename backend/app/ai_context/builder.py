"""
Verified AI context builder (Phase 6).

Pure mapping layer: Product + Analytics + Recommendation -> context.
No clock reads, no recomputation, no business decisions, no prose.
Every field is copied from a verified deterministic source; None is
preserved exactly. The only transformation is Decimal -> float where the
AI contract requires it (inventory_value, financial_exposure).
"""

from datetime import datetime
from typing import Optional

from app.contracts.ai_context import (
    AIBusinessBriefContext,
    AIInsightContext,
    AIProductContext,
    AIRecommendationContext,
)
from app.contracts.analytics import DemandTrend, ProductAnalytics
from app.contracts.data import Product
from app.contracts.recommendation import RecommendationAction, RecommendationResult


def build_product_context(
    product: Product,
    analytics: ProductAnalytics,
    recommendation: RecommendationResult,
) -> AIProductContext:
    """Build verified context for a single product."""
    return AIProductContext(
        product_id=analytics.product_id,
        product_name=analytics.product_name,
        category=product.category,
        current_stock=analytics.inventory.current_stock,
        demand_trend=analytics.demand.trend,
        average_daily_sales=analytics.demand.average_daily_sales,
        days_of_stock_remaining=analytics.inventory.days_of_stock_remaining,
        incoming_quantity=analytics.shipment.incoming_quantity,
        incoming_arrival_days=analytics.shipment.days_until_arrival,
        recommendation_action=recommendation.action,
        priority=recommendation.priority.value,
        recommended_reorder_quantity=recommendation.reorder_quantity,
        reorder_timing=recommendation.reorder_timing,
        target_stock_days=recommendation.target_stock_days,
        excess_units=recommendation.excess_units,
        inventory_value=(
            float(analytics.inventory.inventory_value)
            if analytics.inventory.inventory_value is not None
            else None
        ),
        financial_exposure=(
            float(analytics.financial.financial_exposure)
            if analytics.financial.financial_exposure is not None
            else None
        ),
        evidence=list(recommendation.evidence),
    )


def build_business_brief_context(
    product_contexts: list[AIProductContext],
    *,
    generated_at: datetime,
    currency: Optional[str] = None,
) -> AIBusinessBriefContext:
    """Build verified context for the dashboard AI Business Brief.

    ``currency`` comes from business configuration (not from Gemini), so the
    explanation can only use a currency the business actually configured.
    """
    values = [c.inventory_value for c in product_contexts if c.inventory_value is not None]
    return AIBusinessBriefContext(
        generated_at=generated_at,
        currency=currency,
        total_inventory_value=sum(values) if values else None,
        items_needing_attention=sum(1 for c in product_contexts if c.is_actionable()),
        healthy_items=sum(
            1
            for c in product_contexts
            if c.recommendation_action == RecommendationAction.NO_ACTION
        ),
        unavailable_items=sum(
            1
            for c in product_contexts
            if c.recommendation_action == RecommendationAction.UNAVAILABLE
        ),
        top_priorities=sorted(
            (c for c in product_contexts if c.is_actionable()),
            key=lambda c: (c.priority, c.product_id),
        ),
    )


def build_recommendation_context(
    product_context: AIProductContext,
    *,
    generated_at: datetime,
    currency: Optional[str] = None,
) -> AIRecommendationContext:
    """Build verified context for the product-detail AI explanation."""
    return AIRecommendationContext(
        generated_at=generated_at, currency=currency, product=product_context
    )


def build_insight_context(
    product_contexts: list[AIProductContext],
    *,
    focus_area: str = "demand",
    generated_at: datetime,
    currency: Optional[str] = None,
) -> AIInsightContext:
    """Build verified context for the analytics-page AI insight."""
    highlights = sorted(
        product_contexts,
        key=lambda c: (c.priority, c.product_id),
    )
    trends: list[str] = []
    for trend in (DemandTrend.INCREASING, DemandTrend.DECREASING, DemandTrend.STABLE):
        count = sum(1 for c in product_contexts if c.demand_trend == trend)
        if count:
            trends.append(f"{count} product(s) with {trend.value} demand")
    unavailable = sum(1 for c in product_contexts if c.demand_trend == DemandTrend.UNAVAILABLE)
    if unavailable:
        trends.append(f"{unavailable} product(s) with unavailable demand trend")

    return AIInsightContext(
        generated_at=generated_at,
        currency=currency,
        focus_area=focus_area,
        verified_trends=trends,
        product_highlights=highlights,
    )
