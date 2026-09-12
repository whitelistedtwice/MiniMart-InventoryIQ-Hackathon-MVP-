"""
Analytics API routes.

Phase 14 will wire this to real data. Phase 1 defines the contract only.
"""

from datetime import datetime

from fastapi import APIRouter

from app.contracts.ai_context import AIInsightContext
from app.contracts.api import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics() -> AnalyticsResponse:
    """Return analytics data + AI insight context."""
    return AnalyticsResponse(
        generated_at=datetime.now(),
        products=[],
        ai_insight_context=AIInsightContext(
            generated_at=datetime.now(),
            focus_area="demand",
        ),
    )
