"""
Dashboard API routes.

Phase 11 will wire this to real data. Phase 1 defines the contract only.
"""

from datetime import datetime

from fastapi import APIRouter

from app.contracts.ai_context import AIBusinessBriefContext
from app.contracts.api import DashboardResponse, DashboardSummary, ProductListItem
from app.contracts.recommendation import RecommendationAction

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    """Return dashboard summary + AI business brief context."""
    return DashboardResponse(
        generated_at=datetime.now(),
        summary=DashboardSummary(
            items_needing_attention=0,
            healthy_items=0,
            total_inventory_value=None,
            top_priorities=[],
        ),
        ai_brief_context=AIBusinessBriefContext(
            generated_at=datetime.now(),
            total_inventory_value=None,
            items_needing_attention=0,
            healthy_items=0,
            top_priorities=[],
        ),
    )
