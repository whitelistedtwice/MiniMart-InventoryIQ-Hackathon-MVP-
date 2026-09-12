"""
Settings API routes.

Phase 15 will wire this to real data. Phase 1 defines the contract only.
"""

from fastapi import APIRouter

from app.contracts.api import SettingsResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings() -> SettingsResponse:
    """Return current settings state."""
    return SettingsResponse()
