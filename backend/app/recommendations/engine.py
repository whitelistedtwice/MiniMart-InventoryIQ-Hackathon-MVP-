"""
Recommendation engine placeholder.

Phase 5 will implement the deterministic recommendation logic.
"""

from app.contracts.analytics import ProductAnalytics
from app.contracts.recommendation import RecommendationResult


def recommend(analytics: ProductAnalytics) -> RecommendationResult:
    """Return the deterministic recommendation for a product."""
    raise NotImplementedError("Recommendation logic belongs to Phase 5")
