"""FastAPI dependencies.

Injectable seams so routes stay thin and tests can supply deterministic
sources without touching the real Google Sheets layer.
"""

from datetime import date
from typing import Any, Optional

from app.data_access.sheets import read_sheets


def get_raw_sheets() -> dict[str, list[dict[str, Any]]]:
    """Return raw sheet rows from the Google Sheets data-access layer."""
    return read_sheets()


def get_as_of() -> Optional[date]:
    """Reference 'today' for shipment timing.

    Production returns None, letting the analytics engine use its default.
    Tests override this to a fixed date for reproducibility.
    """
    return None
