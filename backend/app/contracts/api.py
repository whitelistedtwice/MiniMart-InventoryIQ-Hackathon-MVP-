"""
API response contracts.

These define the shape of every response the frontend will receive.
The frontend consumes these directly and does not recompute business
metrics.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from .ai_context import (
    AIBusinessBriefContext,
    AIInsightContext,
    AIRecommendationContext,
)
from .analytics import ProductAnalytics
from .recommendation import RecommendationAction, RecommendationResult


class ProductListItem(BaseModel):
    """One row in the inventory product list."""

    product_id: str
    product_name: str
    category: Optional[str] = None
    current_stock: Optional[int] = None
    status: RecommendationAction = RecommendationAction.UNAVAILABLE
    days_remaining: Optional[float] = None


class DashboardSummary(BaseModel):
    """Deterministic dashboard numbers."""

    items_needing_attention: int = 0
    healthy_items: int = 0
    total_inventory_value: Optional[float] = None
    top_priorities: list[ProductListItem] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    """Complete dashboard payload."""

    generated_at: datetime
    summary: DashboardSummary
    ai_brief_context: AIBusinessBriefContext


class ProductDetailResponse(BaseModel):
    """Complete product detail payload."""

    product_id: str
    analytics: ProductAnalytics
    recommendation: RecommendationResult
    ai_context: AIRecommendationContext
    historical_inventory: list[tuple[date, int]] = Field(
        default_factory=list,
        description="Date + quantity pairs for the historical trend chart",
    )


class AnalyticsResponse(BaseModel):
    """Complete analytics page payload."""

    generated_at: datetime
    products: list[ProductAnalytics]
    ai_insight_context: AIInsightContext


class SettingsResponse(BaseModel):
    """Settings page state."""

    business_name: Optional[str] = None
    business_type: Optional[str] = None
    sheets_connected: bool = False
    last_sync_at: Optional[datetime] = None


class AIExplanationResponse(BaseModel):
    """Plain-language explanation produced by Gemini from verified context."""

    summary: str
    reason: Optional[str] = None
    action_explanation: Optional[str] = None
    future_note: Optional[str] = None
    ai_available: bool = True


class ApiError(BaseModel):
    """Standard error envelope returned by the API."""

    error: str = Field(..., description="Short error code")
    message: str = Field(..., description="Human-readable description")
    details: Optional[dict] = None
