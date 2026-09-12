"""
Verified AI context builder placeholder.

Phase 6 will implement assembling the verified context passed to Gemini.
"""

from app.contracts.ai_context import (
    AIBusinessBriefContext,
    AIInsightContext,
    AIProductContext,
    AIRecommendationContext,
)
from app.contracts.analytics import ProductAnalytics
from app.contracts.recommendation import RecommendationResult


def build_product_context(
    analytics: ProductAnalytics,
    recommendation: RecommendationResult,
) -> AIProductContext:
    """Build verified context for a single product."""
    raise NotImplementedError("AI context building belongs to Phase 6")


def build_business_brief_context(
    product_contexts: list[AIProductContext],
) -> AIBusinessBriefContext:
    """Build verified context for the dashboard AI Business Brief."""
    raise NotImplementedError("AI context building belongs to Phase 6")


def build_recommendation_context(
    product_context: AIProductContext,
) -> AIRecommendationContext:
    """Build verified context for the product-detail AI explanation."""
    raise NotImplementedError("AI context building belongs to Phase 6")


def build_insight_context(
    product_contexts: list[AIProductContext],
    focus_area: str = "demand",
) -> AIInsightContext:
    """Build verified context for the analytics-page AI insight."""
    raise NotImplementedError("AI context building belongs to Phase 6")
