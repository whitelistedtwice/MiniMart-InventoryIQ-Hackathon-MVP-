"""
Phase 6 verified AI context tests.

Full production path: raw -> validation -> processing -> analytics ->
recommendation -> verified AI context, with exact-value assertions,
None/0 preservation, determinism, and trust-boundary checks.
"""

from datetime import date, datetime

from app.ai_context.builder import (
    build_business_brief_context,
    build_insight_context,
    build_product_context,
    build_recommendation_context,
)
from app.analytics.engine import compute_product_analytics
from app.contracts.ai_context import AIProductContext
from app.contracts.analytics import DemandTrend
from app.contracts.recommendation import RecommendationAction
from app.processing.pipeline import build_analysis_ready
from app.recommendations.engine import recommend
from tests.fixtures import (
    ALL_SCENARIOS,
    excess_slow_moving,
    healthy,
    immediate_stockout,
    shipment_after_stockout,
)

AS_OF = date(2026, 9, 14)
GENERATED_AT = datetime(2026, 9, 14, 12, 0)


def run_pipeline(raw, as_of=AS_OF):
    """raw -> validation -> processing -> analytics -> recommendation -> context."""
    processed = build_analysis_ready(raw)[0]
    analytics = compute_product_analytics(processed, as_of=as_of)
    recommendation = recommend(processed.product, analytics)
    context = build_product_context(processed.product, analytics, recommendation)
    return processed, analytics, recommendation, context


# ------------------------------------------------------- canonical scenarios

def test_healthy_context():
    processed, analytics, rec, ctx = run_pipeline(healthy())
    assert ctx.product_id == "healthy-1"
    assert ctx.product_name == "Coca-Cola 330ml / កូកា"  # Khmer preserved
    assert ctx.category == "Beverages"
    assert ctx.current_stock == 70  # 0 preserved as 0 when it is 0; here 70
    assert ctx.average_daily_sales == 5.0
    assert ctx.demand_trend == DemandTrend.STABLE
    assert ctx.days_of_stock_remaining == 14.0
    assert ctx.incoming_quantity == 0
    assert ctx.incoming_arrival_days is None  # no shipment -> None, not 0
    assert ctx.recommendation_action == RecommendationAction.NO_ACTION
    assert ctx.priority == 4
    assert ctx.recommended_reorder_quantity is None
    assert ctx.reorder_timing is None
    assert ctx.target_stock_days == 14
    assert ctx.excess_units == 0.0
    # Decimal(70 * 0.50) -> float exact
    assert ctx.inventory_value == 35.0
    assert ctx.financial_exposure == 35.0
    assert not ctx.is_actionable()


def test_immediate_stockout_context():
    _, _, rec, ctx = run_pipeline(immediate_stockout())
    assert ctx.current_stock == 5
    assert ctx.average_daily_sales == 10.0
    assert ctx.days_of_stock_remaining == 0.5
    assert ctx.recommendation_action == RecommendationAction.REORDER
    assert ctx.recommended_reorder_quantity == 135
    assert ctx.priority == 1
    assert ctx.reorder_timing is not None
    assert ctx.evidence == rec.evidence  # verbatim
    assert ctx.is_actionable()


def test_shipment_before_stockout_context():
    ctx = run_pipeline(ALL_SCENARIOS["shipment_before_stockout"]())[3]
    assert ctx.current_stock == 24
    assert ctx.incoming_quantity == 50
    assert ctx.incoming_arrival_days == 2
    assert ctx.recommendation_action == RecommendationAction.MONITOR_PREPARE
    assert ctx.priority == 3
    assert ctx.recommended_reorder_quantity is None


def test_shipment_after_stockout_context():
    ctx = run_pipeline(shipment_after_stockout())[3]
    assert ctx.current_stock == 24
    assert ctx.incoming_quantity == 50
    assert ctx.incoming_arrival_days == 5
    assert ctx.recommendation_action == RecommendationAction.REORDER
    assert ctx.recommended_reorder_quantity == 38
    assert ctx.reorder_timing.startswith("Order immediately")
    assert ctx.is_actionable()


def test_excess_slow_moving_context():
    ctx = run_pipeline(excess_slow_moving())[3]
    assert ctx.current_stock == 100
    assert ctx.excess_units == 86.0
    assert ctx.recommendation_action == RecommendationAction.REDUCE_EXCESS
    assert ctx.priority == 2
    assert ctx.recommended_reorder_quantity is None
    assert ctx.inventory_value == 50.0  # 100 * 0.50
    assert ctx.is_actionable()


def test_increasing_demand_context():
    ctx = run_pipeline(ALL_SCENARIOS["increasing_demand"]())[3]
    assert ctx.demand_trend == DemandTrend.INCREASING
    assert ctx.current_stock == 40
    assert ctx.recommendation_action == RecommendationAction.MONITOR_PREPARE
    assert ctx.is_actionable()


def test_all_canonical_contexts_mirror_pipeline():
    """Context must exactly mirror analytics + recommendation for all six."""
    for fn in ALL_SCENARIOS.values():
        processed, analytics, rec, ctx = run_pipeline(fn())
        assert ctx.product_id == analytics.product_id == processed.product.product_id
        assert ctx.product_name == analytics.product_name
        assert ctx.current_stock == analytics.inventory.current_stock
        assert ctx.demand_trend == analytics.demand.trend
        assert ctx.average_daily_sales == analytics.demand.average_daily_sales
        assert ctx.days_of_stock_remaining == analytics.inventory.days_of_stock_remaining
        assert ctx.incoming_quantity == analytics.shipment.incoming_quantity
        assert ctx.incoming_arrival_days == analytics.shipment.days_until_arrival
        assert ctx.recommendation_action == rec.action
        assert ctx.priority == rec.priority.value
        assert ctx.recommended_reorder_quantity == rec.reorder_quantity
        assert ctx.reorder_timing == rec.reorder_timing
        assert ctx.target_stock_days == rec.target_stock_days
        assert ctx.excess_units == rec.excess_units
        assert ctx.evidence == rec.evidence


# ------------------------------------------------- None vs 0 / missing data

def test_missing_inventory_preserved_as_none():
    raw = ALL_SCENARIOS["healthy"]()
    raw["Inventory"] = []
    _, _, _, ctx = run_pipeline(raw)
    assert ctx.current_stock is None
    assert ctx.days_of_stock_remaining is None
    assert ctx.recommendation_action == RecommendationAction.UNAVAILABLE
    assert ctx.recommended_reorder_quantity is None


def test_missing_sales_preserved_as_none():
    raw = ALL_SCENARIOS["healthy"]()
    raw["Sales"] = []
    _, _, _, ctx = run_pipeline(raw)
    assert ctx.current_stock == 70  # known
    assert ctx.average_daily_sales is None  # unknown, not 0
    assert ctx.recommendation_action == RecommendationAction.UNAVAILABLE


def test_missing_target_and_lead_time_preserved():
    raw = ALL_SCENARIOS["healthy"]()
    raw["Products"][0]["target_stock_days"] = ""
    _, _, _, ctx = run_pipeline(raw)
    assert ctx.target_stock_days is None
    assert ctx.recommendation_action == RecommendationAction.UNAVAILABLE


def test_zero_inventory_preserved_as_zero_not_none():
    raw = ALL_SCENARIOS["immediate_stockout"]()
    raw["Inventory"][0]["quantity_on_hand"] = 0
    _, _, _, ctx = run_pipeline(raw)
    assert ctx.current_stock == 0
    assert ctx.days_of_stock_remaining == 0.0
    assert ctx.recommendation_action == RecommendationAction.REORDER


def test_zero_demand_valid_not_missing():
    raw = ALL_SCENARIOS["healthy"]()
    for row in raw["Sales"]:
        row["quantity_sold"] = 0
    _, _, _, ctx = run_pipeline(raw)
    assert ctx.average_daily_sales == 0.0
    assert ctx.demand_trend == DemandTrend.STABLE


def test_zero_demand_and_zero_stock_is_no_action():
    raw = ALL_SCENARIOS["immediate_stockout"]()
    for row in raw["Sales"]:
        row["quantity_sold"] = 0
    raw["Inventory"][0]["quantity_on_hand"] = 0
    _, _, _, ctx = run_pipeline(raw)
    assert ctx.average_daily_sales == 0.0
    assert ctx.current_stock == 0
    assert ctx.recommendation_action == RecommendationAction.NO_ACTION


def test_shipment_timing_preserved_exactly():
    ctx = run_pipeline(shipment_after_stockout())[3]
    # Current stock (24) and incoming (50) stay separate concepts:
    # current_stock is the physical stock; incoming_quantity is not merged in.
    assert ctx.current_stock == 24
    assert ctx.incoming_quantity == 50
    assert ctx.incoming_arrival_days == 5


# ------------------------------------------------------- Decimal -> float

def test_decimal_to_float_conversion_exact():
    raw = ALL_SCENARIOS["excess_slow_moving"]()
    raw["Products"][0]["unit_cost"] = "1.25"
    raw["Inventory"][0]["quantity_on_hand"] = 40
    ctx = run_pipeline(raw)[3]
    # Analytics keeps Decimal; context exposes float per contract.
    assert ctx.inventory_value == 50.0
    assert ctx.financial_exposure == 50.0
    assert isinstance(ctx.inventory_value, float)


def test_decimal_none_stays_none():
    raw = ALL_SCENARIOS["healthy"]()
    raw["Products"][0]["unit_cost"] = ""  # unknown cost
    ctx = run_pipeline(raw)[3]
    assert ctx.inventory_value is None
    assert ctx.financial_exposure is None


# ------------------------------------------------------- business brief

def _contexts(*fns):
    out = []
    for fn in fns:
        processed = build_analysis_ready(fn())[0]
        analytics = compute_product_analytics(processed, as_of=AS_OF)
        rec = recommend(processed.product, analytics)
        out.append(build_product_context(processed.product, analytics, rec))
    return out


def test_business_brief_counts_and_ordering():
    contexts = _contexts(
        healthy,                 # NO ACTION (4)
        immediate_stockout,      # REORDER (1)
        excess_slow_moving,      # REDUCE EXCESS (2)
        ALL_SCENARIOS["increasing_demand"],  # MONITOR (3)
        ALL_SCENARIOS["shipment_after_stockout"],  # REORDER (1)
    )
    brief = build_business_brief_context(contexts, generated_at=GENERATED_AT)
    assert brief.generated_at == GENERATED_AT
    assert brief.items_needing_attention == 4  # actionable ones
    assert brief.healthy_items == 1
    assert [c.product_id for c in brief.top_priorities] == [
        "arrival-late-1",  # REORDER
        "stockout-1",      # REORDER
        "excess-1",        # REDUCE EXCESS
        "trend-up-1",      # MONITOR
    ]
    # 35 + 2.5 + 50 + 20 + 12 = 119.5 (all values available)
    assert brief.total_inventory_value == 119.5


def test_business_brief_total_none_when_no_values():
    raw = ALL_SCENARIOS["healthy"]()
    raw["Products"][0]["unit_cost"] = ""
    contexts = _contexts(lambda: raw)
    brief = build_business_brief_context(contexts, generated_at=GENERATED_AT)
    assert brief.total_inventory_value is None


def test_business_brief_unavailable_items_are_healthy_side():
    raw = ALL_SCENARIOS["healthy"]()
    raw["Inventory"] = []  # UNAVAILABLE
    contexts = _contexts(lambda: raw)
    brief = build_business_brief_context(contexts, generated_at=GENERATED_AT)
    assert brief.items_needing_attention == 0
    assert brief.healthy_items == 1
    assert brief.top_priorities == []


# --------------------------------------------------------- insight context

def test_insight_context_trends_and_highlights():
    contexts = _contexts(
        healthy,
        immediate_stockout,
        ALL_SCENARIOS["increasing_demand"],
    )
    insight = build_insight_context(contexts, generated_at=GENERATED_AT)
    assert insight.generated_at == GENERATED_AT
    assert insight.focus_area == "demand"
    assert insight.verified_trends == [
        "1 product(s) with increasing demand",
        "2 product(s) with stable demand",
    ]
    # ordered by priority: REORDER(1) < MONITOR(3) < NO ACTION(4)
    assert [c.product_id for c in insight.product_highlights] == [
        "stockout-1", "trend-up-1", "healthy-1",
    ]


def test_insight_context_empty():
    insight = build_insight_context([], generated_at=GENERATED_AT)
    assert insight.verified_trends == []
    assert insight.product_highlights == []


# --------------------------------------------------- recommendation context

def test_recommendation_context_wraps_product_context():
    _, _, rec, ctx = run_pipeline(immediate_stockout())
    wrapped = build_recommendation_context(ctx, generated_at=GENERATED_AT)
    assert wrapped.generated_at == GENERATED_AT
    assert wrapped.product == ctx
    assert wrapped.product.recommendation_action == rec.action == RecommendationAction.REORDER


def test_currency_carried_into_all_ai_contexts():
    _, _, _, ctx = run_pipeline(healthy())
    brief = build_business_brief_context([ctx], generated_at=GENERATED_AT, currency="USD")
    assert brief.currency == "USD"
    wrapped = build_recommendation_context(ctx, generated_at=GENERATED_AT, currency="USD")
    assert wrapped.currency == "USD"
    insight = build_insight_context([ctx], generated_at=GENERATED_AT, currency="USD")
    assert insight.currency == "USD"


def test_currency_defaults_to_none_when_not_configured():
    _, _, _, ctx = run_pipeline(healthy())
    assert build_business_brief_context([ctx], generated_at=GENERATED_AT).currency is None
    assert build_recommendation_context(ctx, generated_at=GENERATED_AT).currency is None
    assert build_insight_context([ctx], generated_at=GENERATED_AT).currency is None


# -------------------------------------------------------------- determinism

def test_builders_deterministic_identical_generated_at():
    processed = build_analysis_ready(immediate_stockout())[0]
    analytics = compute_product_analytics(processed, as_of=AS_OF)
    rec = recommend(processed.product, analytics)
    ctx1 = build_product_context(processed.product, analytics, rec)
    ctx2 = build_product_context(processed.product, analytics, rec)
    assert ctx1 == ctx2

    b1 = build_business_brief_context([ctx1], generated_at=GENERATED_AT)
    b2 = build_business_brief_context([ctx1], generated_at=GENERATED_AT)
    assert b1 == b2
    assert b1.model_dump_json() == b2.model_dump_json()

    r1 = build_recommendation_context(ctx1, generated_at=GENERATED_AT)
    r2 = build_recommendation_context(ctx1, generated_at=GENERATED_AT)
    assert r1 == r2
    assert r1.model_dump_json() == r2.model_dump_json()

    i1 = build_insight_context([ctx1], generated_at=GENERATED_AT)
    i2 = build_insight_context([ctx1], generated_at=GENERATED_AT)
    assert i1 == i2
    assert i1.model_dump_json() == i2.model_dump_json()


def test_generated_at_is_preserved_not_clocked():
    # proves builders do not read the clock: a distinctive timestamp round-trips
    odd = datetime(1999, 12, 31, 23, 59, 59)
    processed = build_analysis_ready(healthy())[0]
    analytics = compute_product_analytics(processed, as_of=AS_OF)
    rec = recommend(processed.product, analytics)
    ctx = build_product_context(processed.product, analytics, rec)
    assert build_recommendation_context(ctx, generated_at=odd).generated_at == odd
    assert build_business_brief_context([ctx], generated_at=odd).generated_at == odd
    assert build_insight_context([ctx], generated_at=odd).generated_at == odd


# ------------------------------------------------------------ integration

def test_full_pipeline_khmer_name_exact():
    raw = {
        "Products": [{
            "product_id": "p-7", "product_name": "កាហ្វេ Coffee 3in1", "category": "Beverages",
            "unit": "pack", "unit_cost": "0.30", "selling_price": "0.50",
            "supplier": "Phnom Penh Distributor", "lead_time_days": "2",
            "target_stock_days": "10",
        }],
        "Sales": [
            {"date": "2026-09-12", "product_id": "p-7", "quantity_sold": "6"},
            {"date": "2026-09-13", "product_id": "p-7", "quantity_sold": "4"},
        ],
        "Inventory": [{"date": "2026-09-13", "product_id": "p-7", "quantity_on_hand": "5"}],
        "Shipments": [],
    }
    ctx = run_pipeline(raw, as_of=date(2026, 9, 13))[3]
    assert ctx.product_name == "កាហ្វេ Coffee 3in1"
    assert ctx.product_id == "p-7"
    assert ctx.current_stock == 5
    assert ctx.average_daily_sales == 5.0
    assert ctx.recommendation_action == RecommendationAction.REORDER
    assert ctx.recommended_reorder_quantity == 45
    assert ctx.target_stock_days == 10
    assert ctx.inventory_value == 1.5  # 5 * 0.30
    assert ctx.financial_exposure == 1.5
    assert ctx.evidence  # recommendation evidence carried over
