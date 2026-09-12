"""
Verified AI context contract.

Gemini receives ONLY what the backend has already validated and computed.
These structures make it difficult for Gemini to become the source of truth:
- All numeric fields are the exact values produced by analytics/recommendations.
- Missing data is explicit (Optional/None), so Gemini cannot assume values.
- No raw spreadsheet rows are included.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from .analytics import DemandTrend
from .recommendation import RecommendationAction


class AIProductContext(BaseModel):
    """Verified context for a single product, safe to hand to Gemini."""

    product_id: str
    product_name: str
    category: Optional[str] = None
    current_stock: Optional[int] = Field(
        None,
        description="Verified latest stock. None means unavailable.",
    )
    demand_trend: DemandTrend = DemandTrend.UNAVAILABLE
    days_of_stock_remaining: Optional[float] = None
    incoming_quantity: Optional[int] = None
    incoming_arrival_days: Optional[int] = None
    recommendation_action: RecommendationAction = RecommendationAction.UNAVAILABLE
    recommended_reorder_quantity: Optional[int] = None
    inventory_value: Optional[float] = None
    financial_exposure: Optional[float] = None
    evidence: list[str] = Field(default_factory=list)


class AIBusinessBriefContext(BaseModel):
    """Verified context for the dashboard AI Business Brief."""

    generated_at: datetime
    total_inventory_value: Optional[float] = None
    items_needing_attention: int = 0
    healthy_items: int = 0
    top_priorities: list[AIProductContext] = Field(
        default_factory=list,
        description="Products with the highest-priority recommendations",
    )


class AIRecommendationContext(BaseModel):
    """Verified context for the product-detail AI explanation."""

    generated_at: datetime
    product: AIProductContext


class AIInsightContext(BaseModel):
    """Verified context for the analytics-page AI insight card."""

    generated_at: datetime
    focus_area: str = Field(
        default="demand",
        description="Which analytics area the insight addresses",
    )
    verified_trends: list[str] = Field(default_factory=list)
    product_highlights: list[AIProductContext] = Field(default_factory=list)
