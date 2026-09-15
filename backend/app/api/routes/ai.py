"""AI explanation API routes (Phase 8).

Gemini is an optional explanation layer. Deterministic endpoints never
depend on it, and these routes return a graceful ``ai_available=False``
result when Gemini is unavailable.
"""

from datetime import date, datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends

from app.ai_context.builder import (
    build_business_brief_context,
    build_insight_context,
    build_recommendation_context,
)
from app.api.dependencies import get_as_of, get_raw_sheets
from app.contracts.api import AIExplanationResponse
from app.core.business import business_currency
from app.gemini import client
from app.services.analysis import analyze, find

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/business-brief", response_model=AIExplanationResponse)
def business_brief(
    raw: dict[str, list[dict[str, Any]]] = Depends(get_raw_sheets),
    as_of: Optional[date] = Depends(get_as_of),
) -> AIExplanationResponse:
    """Gemini summary of the verified business condition."""
    contexts = [item.context() for item in analyze(raw, as_of)]
    context = build_business_brief_context(
        contexts, generated_at=datetime.now(), currency=business_currency()
    )
    return client.generate_business_brief(context)


@router.get("/recommendation/{product_id}", response_model=AIExplanationResponse)
def recommendation_explanation(
    product_id: str,
    raw: dict[str, list[dict[str, Any]]] = Depends(get_raw_sheets),
    as_of: Optional[date] = Depends(get_as_of),
) -> AIExplanationResponse:
    """Gemini explanation of one product's deterministic recommendation."""
    item = find(analyze(raw, as_of), product_id)
    context = build_recommendation_context(
        item.context(), generated_at=datetime.now(), currency=business_currency()
    )
    return client.explain_recommendation(context)


@router.get("/insight", response_model=AIExplanationResponse)
def analytics_insight(
    raw: dict[str, list[dict[str, Any]]] = Depends(get_raw_sheets),
    as_of: Optional[date] = Depends(get_as_of),
) -> AIExplanationResponse:
    """Gemini explanation of verified analytics trends."""
    contexts = [item.context() for item in analyze(raw, as_of)]
    context = build_insight_context(
        contexts, generated_at=datetime.now(), currency=business_currency()
    )
    return client.generate_insight(context)
