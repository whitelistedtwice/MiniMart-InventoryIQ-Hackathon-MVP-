"""
AI explanation API routes.

Phase 7 will call Gemini. Phase 1 defines the contract only.
"""

from fastapi import APIRouter

from app.contracts.api import AIExplanationResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/business-brief", response_model=AIExplanationResponse)
def business_brief() -> AIExplanationResponse:
    """Return Gemini-generated business brief or unavailable fallback."""
    return AIExplanationResponse(
        summary="AI explanation is not yet available.",
        ai_available=False,
    )


@router.get("/recommendation/{product_id}", response_model=AIExplanationResponse)
def recommendation_explanation(product_id: str) -> AIExplanationResponse:
    """Return Gemini-generated explanation for a product recommendation."""
    return AIExplanationResponse(
        summary=f"AI explanation for {product_id} is not yet available.",
        ai_available=False,
    )


@router.get("/insight", response_model=AIExplanationResponse)
def analytics_insight() -> AIExplanationResponse:
    """Return Gemini-generated analytics insight."""
    return AIExplanationResponse(
        summary="AI insight is not yet available.",
        ai_available=False,
    )
