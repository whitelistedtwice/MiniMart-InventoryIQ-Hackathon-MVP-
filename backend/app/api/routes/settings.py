"""Settings / connection API route (Phase 8, profile Phase 15, probe Phase 16).

The business profile comes from environment configuration (single business,
no database). ``sheets_connection_state`` is the result of a cached live
connectivity probe (C-002).
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.contracts.api import SettingsResponse
from app.core import business
from app.core.clock import BUSINESS_TIMEZONE
from app.data_access.sheets import get_sheets_connection_state

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
def get_settings(force: bool = False) -> SettingsResponse:
    """Return the configured business profile + Sheets connection state."""
    conn = get_sheets_connection_state(force=force)
    connected = conn["state"] == "connected"
    last_checked = conn["last_checked"]
    return SettingsResponse(
        business_name=business.business_name(),
        business_type=business.business_type(),
        currency=business.business_currency(),
        timezone=str(BUSINESS_TIMEZONE),
        sheets_connected=connected,
        sheets_connection_state=conn["state"],
        sheets_connection_error=conn["error"],
        sheets_last_checked_at=(
            datetime.fromtimestamp(last_checked, tz=timezone.utc)
            if last_checked
            else None
        ),
        last_sync_at=None,
    )
