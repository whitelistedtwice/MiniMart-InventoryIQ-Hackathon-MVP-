"""Phase 9: business clock tests (Asia/Phnom_Penh semantics)."""

from datetime import datetime, timezone

from app.analytics.engine import compute_product_analytics
from app.core import clock
from app.core.clock import business_today
from app.processing.pipeline import build_analysis_ready
from tests.fixtures import shipment_after_stockout


def test_business_timezone_is_phnom_penh():
    assert str(clock.BUSINESS_TIMEZONE) == "Asia/Phnom_Penh"


def test_business_today_reflects_business_timezone(monkeypatch):
    # A moment that is still "yesterday" in UTC but already today in UTC+7:
    # 2026-09-13 18:00 UTC == 2026-09-14 01:00 Phnom Penh.
    monkeypatch.setattr(
        clock, "_now",
        lambda: datetime(2026, 9, 13, 18, 0, tzinfo=timezone.utc)
        .astimezone(clock.BUSINESS_TIMEZONE),
    )
    assert business_today().isoformat() == "2026-09-14"


def test_analytics_default_as_of_uses_business_clock():
    processed = build_analysis_ready(shipment_after_stockout())[0]
    explicit = compute_product_analytics(processed, as_of=business_today())
    default = compute_product_analytics(processed)
    assert default == explicit
