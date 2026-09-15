"""Dashboard API routes (Phase 8)."""

from datetime import date, datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends

from app.ai_context.builder import build_business_brief_context
from app.api.dependencies import get_as_of, get_raw_sheets
from app.contracts.api import DashboardResponse, DashboardSummary
from app.core.business import business_currency
from app.services.analysis import analyze

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

TOP_PRIORITIES_LIMIT = 5


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    raw: dict[str, list[dict[str, Any]]] = Depends(get_raw_sheets),
    as_of: Optional[date] = Depends(get_as_of),
) -> DashboardResponse:
    """Return the deterministic business health summary + AI brief context."""
    now = datetime.now()
    analyses = analyze(raw, as_of)
    contexts = [item.context() for item in analyses]
    brief = build_business_brief_context(
        contexts, generated_at=now, currency=business_currency()
    )
    actionable = sorted(
        (item for item in analyses if item.recommendation.is_actionable()),
        key=lambda item: (item.recommendation.priority.value, item.analytics.product_id),
    )
    return DashboardResponse(
        generated_at=now,
        summary=DashboardSummary(
            items_needing_attention=brief.items_needing_attention,
            healthy_items=brief.healthy_items,
            total_inventory_value=brief.total_inventory_value,
            top_priorities=[item.list_item() for item in actionable[:TOP_PRIORITIES_LIMIT]],
        ),
        ai_brief_context=brief,
    )
