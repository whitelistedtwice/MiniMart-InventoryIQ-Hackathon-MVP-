"""Settings / connection API route (Phase 8)."""

import os

from fastapi import APIRouter

from app.contracts.api import SettingsResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings() -> SettingsResponse:
    """Return Google Sheets connection state (no secrets)."""
    connected = bool(
        os.environ.get("GOOGLE_SHEET_ID")
        and os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )
    return SettingsResponse(sheets_connected=connected)
