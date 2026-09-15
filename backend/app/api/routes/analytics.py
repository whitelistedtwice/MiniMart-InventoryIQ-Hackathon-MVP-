"""Analytics API routes (Phase 8)."""

from datetime import date, datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends

from app.ai_context.builder import build_insight_context
from app.api.dependencies import get_as_of, get_raw_sheets
from app.contracts.api import AnalyticsResponse
from app.core.business import business_currency
from app.services.analysis import analyze

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    raw: dict[str, list[dict[str, Any]]] = Depends(get_raw_sheets),
    as_of: Optional[date] = Depends(get_as_of),
) -> AnalyticsResponse:
    """Return per-product analytics + AI insight context."""
    now = datetime.now()
    analyses = analyze(raw, as_of)
    contexts = [item.context() for item in analyses]
    return AnalyticsResponse(
        generated_at=now,
        products=[item.analytics for item in analyses],
        ai_insight_context=build_insight_context(
            contexts, generated_at=now, currency=business_currency()
        ),
    )
