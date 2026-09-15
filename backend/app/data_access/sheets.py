"""
Google Sheets data-access layer (Phase 2, deployment Phase 16).

Reads the four MVP sheets and returns their raw, header-mapped rows.

Deployment notes:
- GOOGLE_SERVICE_ACCOUNT_JSON (raw JSON string) is preferred on PaaS hosts
  because they provide secrets as env vars, not files.
- GOOGLE_SERVICE_ACCOUNT_FILE still works for local development.
- DEMO_MODE=true loads the canonical demo dataset from
  backend/demo/cambodian_mini_mart.json instead of Google Sheets.
- Connection state is probed lazily and cached for a short TTL.

This layer does NO validation, typing, cleaning, or business interpretation:
- blank cells stay as empty strings (never coerced to 0)
- inventory and shipments stay in separate sheets/keys
- Phase 3 decides what is valid and how to coerce values
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from pathlib import Path
from typing import Any, Optional

import gspread

from app.core.errors import DataAccessError

REQUIRED_SHEETS = ("Products", "Sales", "Inventory", "Shipments")
_DEMO_PATH = Path(__file__).resolve().parents[2] / "demo" / "cambodian_mini_mart.json"
_SHEETS_PROBE_TIMEOUT_SECONDS = float(
    os.environ.get("SHEETS_PROBE_TIMEOUT_SECONDS", "3")
)
_CONNECTION_CACHE_TTL_SECONDS = int(
    os.environ.get("SHEETS_CONNECTION_CACHE_TTL_SECONDS", "60")
)

_connection_cache: dict[str, Any] = {}


def _is_demo_mode() -> bool:
    return os.environ.get("DEMO_MODE", "").strip().lower() in ("1", "true", "yes")


def _load_demo_sheets() -> dict[str, list[dict[str, Any]]]:
    if not _DEMO_PATH.exists():
        raise DataAccessError(f"Demo data file not found: {_DEMO_PATH}")
    try:
        with _DEMO_PATH.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:
        raise DataAccessError(f"Could not load demo data: {exc}") from exc
    for name in REQUIRED_SHEETS:
        if name not in data:
            raise DataAccessError(f"Demo data is missing required sheet: {name}")
    return data


def _service_account_credentials() -> tuple[
    Optional[str], Optional[str], Optional[dict[str, Any]]
]:
    sheet_id = os.environ.get("GOOGLE_SHEET_ID")
    credentials_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    credentials_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    credentials_info: Optional[dict[str, Any]] = None
    if credentials_json:
        try:
            credentials_info = json.loads(credentials_json)
        except json.JSONDecodeError as exc:
            raise DataAccessError(
                f"GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON: {exc}"
            ) from exc
    return sheet_id, credentials_file, credentials_info


def _open_spreadsheet() -> gspread.Spreadsheet:
    """Authenticate and open the spreadsheet configured via environment."""
    if _is_demo_mode():
        raise DataAccessError("Demo mode does not use Google Sheets")

    sheet_id, credentials_file, credentials_info = _service_account_credentials()
    if not sheet_id:
        raise DataAccessError("GOOGLE_SHEET_ID is not set")
    if not credentials_file and not credentials_info:
        raise DataAccessError(
            "Neither GOOGLE_SERVICE_ACCOUNT_JSON nor GOOGLE_SERVICE_ACCOUNT_FILE is set"
        )

    try:
        if credentials_info:
            client = gspread.service_account_from_dict(credentials_info)
        else:
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
    if _is_demo_mode():
        return _load_demo_sheets()

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


def _probe_connection(
    timeout_seconds: float = _SHEETS_PROBE_TIMEOUT_SECONDS,
) -> tuple[bool, Optional[str]]:
    """Attempt to open the spreadsheet and return (ok, error_message)."""
    if _is_demo_mode():
        return False, "Demo mode is active; Google Sheets is not used"
    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(_open_spreadsheet)
            future.result(timeout=timeout_seconds)
        return True, None
    except FutureTimeoutError:
        return False, f"Connection probe timed out after {timeout_seconds}s"
    except DataAccessError as exc:
        return False, str(exc)
    except Exception as exc:
        return False, f"Unexpected error during connection probe: {exc}"


def get_sheets_connection_state(*, force: bool = False) -> dict[str, Any]:
    """
    Return the current Google Sheets connection state with short-lived cache.

    States:
      - not_configured: spreadsheet id or credentials missing
      - configured:    credentials present but probe timed out / not verified
      - connected:     probe succeeded
      - error:         probe failed with a definite error
    """
    sheet_id, credentials_file, credentials_info = _service_account_credentials()
    if not sheet_id or (not credentials_file and not credentials_info):
        return {"state": "not_configured", "error": None, "last_checked": None}

    cache_key = "sheets_connection"
    now = time.time()
    if not force:
        cached = _connection_cache.get(cache_key)
        if cached and now - cached["checked_at"] < _CONNECTION_CACHE_TTL_SECONDS:
            return {
                "state": cached["state"],
                "error": cached["error"],
                "last_checked": cached["checked_at"],
            }

    ok, error = _probe_connection()
    if ok:
        state = "connected"
    elif error and "timed out" in error.lower():
        state = "configured"
    else:
        state = "error"

    _connection_cache[cache_key] = {
        "state": state,
        "error": error,
        "checked_at": now,
    }
    return {"state": state, "error": error, "last_checked": now}
