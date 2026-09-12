"""
Gemini integration placeholder.

Phase 7 will implement the Gemini API client.
"""

from app.contracts.ai_context import (
    AIBusinessBriefContext,
    AIInsightContext,
    AIRecommendationContext,
)
from app.contracts.api import AIExplanationResponse


def explain_recommendation(
    context: AIRecommendationContext,
) -> AIExplanationResponse:
    """Ask Gemini to explain a product recommendation from verified context."""
    raise NotImplementedError("Gemini integration belongs to Phase 7")


def generate_business_brief(
    context: AIBusinessBriefContext,
) -> AIExplanationResponse:
    """Ask Gemini for a dashboard-level business summary."""
    raise NotImplementedError("Gemini integration belongs to Phase 7")


def generate_insight(
    context: AIInsightContext,
) -> AIExplanationResponse:
    """Ask Gemini for an analytics-page insight."""
    raise NotImplementedError("Gemini integration belongs to Phase 7")
