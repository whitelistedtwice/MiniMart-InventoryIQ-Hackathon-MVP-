"""Settings / connection API route (Phase 8, profile Phase 15).

The business profile comes from environment configuration (single business,
no database). ``sheets_connected`` remains environment-presence only: it
proves the credentials are configured, not that Google Sheets is reachable
(C-002 is intentionally deferred until deployment has real credentials).
"""

import os

from fastapi import APIRouter

from app.contracts.api import SettingsResponse
from app.core import business
from app.core.clock import BUSINESS_TIMEZONE

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings() -> SettingsResponse:
    """Return the configured business profile + Sheets connection state."""
    connected = bool(
        os.environ.get("GOOGLE_SHEET_ID")
        and os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    )
    return SettingsResponse(
        business_name=business.business_name(),
        business_type=business.business_type(),
        currency=business.business_currency(),
        timezone=str(BUSINESS_TIMEZONE),
        sheets_connected=connected,
    )
