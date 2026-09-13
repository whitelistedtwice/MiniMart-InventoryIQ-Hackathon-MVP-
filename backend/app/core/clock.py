"""Business clock.

All business-date semantics (as_of, shipment timing, stock adjustment)
use the MVP business timezone: Asia/Phnom_Penh. Request timestamps
(generated_at) remain ordinary server time — they are cosmetic, not
business decisions.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

BUSINESS_TIMEZONE = ZoneInfo("Asia/Phnom_Penh")


def _now() -> datetime:
    """Seam for tests."""
    return datetime.now(BUSINESS_TIMEZONE)


def business_today() -> date:
    """Today's date in the business timezone."""
    return _now().date()
