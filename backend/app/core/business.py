"""Business profile configuration (Phase 15).

InventoryIQ serves a single business, so the business profile is
configuration rather than persistent user data: it is read from environment
variables at request time. There is no database, no account system, and no
write path (C-014 decision locked).

Values are optional; missing/blank means "not configured" and the API
returns ``None`` rather than an empty string.
"""

import os
from typing import Optional


def _env_text(name: str) -> Optional[str]:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def business_name() -> Optional[str]:
    """Configured business name, or None when not configured."""
    return _env_text("BUSINESS_NAME")


def business_type() -> Optional[str]:
    """Configured business type, or None when not configured."""
    return _env_text("BUSINESS_TYPE")


def business_currency() -> Optional[str]:
    """Configured ISO 4217 currency code for money values.

    None means the currency is not configured: the UI shows plain amounts
    and Gemini is instructed not to invent a currency.
    """
    return _env_text("BUSINESS_CURRENCY")
