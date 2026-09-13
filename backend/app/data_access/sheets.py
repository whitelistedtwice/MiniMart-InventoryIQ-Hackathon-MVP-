"""
Google Sheets data-access layer (Phase 2).

Reads the four MVP sheets and returns their raw, header-mapped rows.

This layer does NO validation, typing, cleaning, or business interpretation:
- blank cells stay as empty strings (never coerced to 0)
- inventory and shipments stay in separate sheets/keys
- Phase 3 decides what is valid and how to coerce values
"""

import os
from typing import Any

import gspread

from app.core.errors import DataAccessError

REQUIRED_SHEETS = ("Products", "Sales", "Inventory", "Shipments")


def _open_spreadsheet() -> gspread.Spreadsheet:
    """Authenticate and open the spreadsheet configured via environment."""
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise DataAccessError("GOOGLE_SHEET_ID is not set")

    credentials_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not credentials_file:
        raise DataAccessError("GOOGLE_SERVICE_ACCOUNT_FILE is not set")

    try:
        client = gspread.service_account(filename=credentials_file)
        return client.open_by_key(sheet_id)
    except Exception as exc:  # auth, network, or bad spreadsheet id
        raise DataAccessError(f"Could not open Google Sheet: {exc}") from exc


def read_sheets() -> dict[str, list[dict[str, Any]]]:
    """
    Read the four required sheets.

    Returns a dict keyed by sheet name, each value a list of row dicts
    (header -> raw cell value). Blank cells remain empty strings.
    """
    # ponytail: no retry/caching; re-reads all four sheets every call.
    # Add a retry/cache when Sheets rate-limits or flakiness appear.
    spreadsheet = _open_spreadsheet()

    raw: dict[str, list[dict[str, Any]]] = {}
    for name in REQUIRED_SHEETS:
        try:
            worksheet = spreadsheet.worksheet(name)
            raw[name] = worksheet.get_all_records()
        except gspread.WorksheetNotFound as exc:
            raise DataAccessError(f"Missing required sheet: {name}") from exc
        except Exception as exc:
            raise DataAccessError(f"Could not read sheet '{name}': {exc}") from exc
    return raw
