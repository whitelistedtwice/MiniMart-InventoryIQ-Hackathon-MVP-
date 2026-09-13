"""
Phase 5 recommendation tests.

Deterministic exact-value tests plus the full
raw -> validation -> processing -> analytics -> recommendation integration.
"""

from datetime import date

import pytest

from app.analytics.engine import compute_product_analytics
from app.contracts.analytics import DemandTrend
from app.contracts.recommendation import RecommendationAction, RecommendationPriority
from app.processing.pipeline import build_analysis_ready
from app.recommendations.engine import recommend
from tests.fixtures import (
    ALL_SCENARIOS,
    excess_slow_moving,
    healthy,
    immediate_stockout,
    increasing_demand,
    shipment_after_stockout,
    shipment_before_stockout,
)

AS_OF = date(2026, 9, 14)


def make_raw(product=None, sales=(), inventory=(), shipments=()):
    product = product or {
        "product_id": "p1", "product_name": "Test Product", "category": "Cat", "unit": "u",
        "unit_cost": "0.50", "selling_price": "0.75", "supplier": "S",
        "lead_time_days": "3", "target_stock_days": "14",
    }
    return {
        "Products": [product],
        "Sales": [
            {"date": d, "product_id": product["product_id"], "quantity_sold": str(q)}
            for d, q in sales
        ],
        "Inventory": [
            {"date": d, "product_id": product["product_id"], "quantity_on_hand": str(q)}
            for d, q in inventory
        ],
        "Shipments": [
            {
                "shipment_id": f"sh-{i}", "product_id": product["product_id"],
                "quantity": str(q), "expected_arrival": a,
            }
            for i, (a, q) in enumerate(shipments)
        ],
    }


def run(raw, as_of=AS_OF):
    """Full production pipeline through to a recommendation."""
    processed = build_analysis_ready(raw)[0]
    analytics = compute_product_analytics(processed, as_of=as_of)
    return recommend(processed.product, analytics)


def five_per_day():
    return [("2026-09-%02d" % d, 5) for d in range(1, 15)]


# ------------------------------------------------------------ canonical runs

def test_healthy_no_action():
    result = run(healthy())
    assert result.action == RecommendationAction.NO_ACTION
    assert result.priority == RecommendationPriority.NO_ACTION
    assert result.reorder_quantity is None
    assert result.current_stock == 70
    assert result.excess_units == 0.0


def test_immediate_stockout_reorders_exact():
    result = run(immediate_stockout())
    assert result.action == RecommendationAction.REORDER
    assert result.priority == RecommendationPriority.REORDER
    # desired = 10/day * 14 days = 140; current 5; incoming 0 -> 135
    assert result.reorder_quantity == 135
    assert result.incoming_stock_sufficient is None  # no shipment
    assert result.reorder_timing is not None
    assert any("135" in reason for reason in result.evidence)


def test_shipment_before_stockout_is_monitored_not_reordered():
    result = run(shipment_before_stockout())
    assert result.action == RecommendationAction.MONITOR_PREPARE
    assert result.priority == RecommendationPriority.MONITOR_PREPARE
    assert result.reorder_quantity is None
    assert result.incoming_stock_sufficient is True  # arrives before stockout
    assert result.days_until_arrival == 2


def test_shipment_after_stockout_reorders_exact():
    result = run(shipment_after_stockout())
    assert result.action == RecommendationAction.REORDER
    # desired 8*14=112; expected 24+50=74 -> 38; bridge ceil(8*5-24)=16 -> 38
    assert result.reorder_quantity == 38
    assert result.incoming_stock_sufficient is False  # runs out before it arrives
    assert result.reorder_timing.startswith("Order immediately")


def test_excess_slow_moving_reduces_excess():
    result = run(excess_slow_moving())
    assert result.action == RecommendationAction.REDUCE_EXCESS
    assert result.priority == RecommendationPriority.REDUCE_EXCESS
    assert result.reorder_quantity is None
    assert result.excess_units == 86.0
    assert any("above the" in reason for reason in result.evidence)


def test_increasing_demand_monitors():
    result = run(increasing_demand())
    assert result.action == RecommendationAction.MONITOR_PREPARE
    assert result.reorder_quantity is None
    assert result.demand_trend == DemandTrend.INCREASING
    assert any("increasing" in reason.lower() for reason in result.evidence)


@pytest.mark.parametrize(
    "scenario,expected_action",
    [
        ("healthy", RecommendationAction.NO_ACTION),
        ("immediate_stockout", RecommendationAction.REORDER),
        ("shipment_before_stockout", RecommendationAction.MONITOR_PREPARE),
        ("shipment_after_stockout", RecommendationAction.REORDER),
        ("excess_slow_moving", RecommendationAction.REDUCE_EXCESS),
        ("increasing_demand", RecommendationAction.MONITOR_PREPARE),
    ],
)
def test_all_canonical_scenarios(scenario, expected_action):
    result = run(ALL_SCENARIOS[scenario]())
    assert result.action == expected_action
    assert result.priority.value <= 4
    assert result.evidence


# ------------------------------------------------------------- unavailable

def test_missing_inventory_is_unavailable():
    result = run(make_raw(sales=[("2026-09-01", 5)], inventory=[]))
    assert result.action == RecommendationAction.UNAVAILABLE
    assert result.priority == RecommendationPriority.UNAVAILABLE
    assert result.reorder_quantity is None
    assert any("current inventory" in reason for reason in result.evidence)


def test_missing_sales_is_unavailable_not_zero():
    result = run(make_raw(sales=[], inventory=[("2026-09-14", 30)]))
    assert result.action == RecommendationAction.UNAVAILABLE
    assert result.current_stock == 30  # known, but demand unknown
    assert any("sales history" in reason for reason in result.evidence)


def test_missing_lead_time_is_unavailable():
    product = {
        "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
        "unit_cost": "0.50", "selling_price": "0.75", "supplier": "",
        "lead_time_days": "", "target_stock_days": "14",
    }
    result = run(make_raw(product=product, sales=five_per_day(), inventory=[("2026-09-14", 10)]))
    assert result.action == RecommendationAction.UNAVAILABLE
    assert any("lead time" in reason for reason in result.evidence)


def test_missing_target_stock_days_is_unavailable():
    product = {
        "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
        "unit_cost": "0.50", "selling_price": "0.75", "supplier": "",
        "lead_time_days": "3", "target_stock_days": "",
    }
    result = run(make_raw(product=product, sales=five_per_day(), inventory=[("2026-09-14", 10)]))
    assert result.action == RecommendationAction.UNAVAILABLE
    assert any("target stock days" in reason for reason in result.evidence)


# --------------------------------------------------------------- zero cases

def test_zero_inventory_reorders_exact():
    result = run(make_raw(sales=five_per_day(), inventory=[("2026-09-14", 0)]))
    assert result.current_stock == 0
    assert result.action == RecommendationAction.REORDER
    assert result.reorder_quantity == 70  # desired 5*14=70, expected 0


def test_zero_sales_is_valid_and_excess():
    sales = [("2026-09-%02d" % d, 0) for d in range(1, 15)]
    result = run(make_raw(sales=sales, inventory=[("2026-09-14", 30)]))
    assert result.action == RecommendationAction.REDUCE_EXCESS
    assert result.excess_units == 30.0


def test_zero_demand_and_zero_stock_no_action():
    sales = [("2026-09-%02d" % d, 0) for d in range(1, 15)]
    result = run(make_raw(sales=sales, inventory=[("2026-09-14", 0)]))
    assert result.action == RecommendationAction.NO_ACTION


# ---------------------------------------------------------------- reorder/edge

def test_lead_time_risk_without_target_shortfall_is_not_reorder():
    # Stock already exceeds target coverage, even though coverage is inside the
    # long lead time. Should not alarm the owner with a REORDER 0.
    result = run(make_raw(
        sales=[("2026-09-01", 2), ("2026-09-02", 2)],  # avg 2
        inventory=[("2026-09-02", 200)],
        product={
            "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
            "unit_cost": "0.50", "selling_price": "0.75", "supplier": "",
            "lead_time_days": "200", "target_stock_days": "14",
        },
    ))
    assert result.action == RecommendationAction.REDUCE_EXCESS
    assert result.reorder_quantity is None


def test_fractional_demand_reorder_rounds_up():
    result = run(make_raw(
        sales=[("2026-09-01", 2), ("2026-09-02", 3)],  # avg 2.5
        inventory=[("2026-09-02", 8)],
        product={
            "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
            "unit_cost": "0.50", "selling_price": "0.75", "supplier": "",
            "lead_time_days": "5", "target_stock_days": "7",
        },
    ))
    assert result.action == RecommendationAction.REORDER
    assert result.reorder_quantity == 10  # ceil(2.5*7 - 8) = ceil(9.5)


def test_exactly_at_excess_threshold_is_no_action():
    # days = 28 == 2x target 14 -> Phase 4 does not mark it 'excess'.
    sales = [("2026-09-%02d" % d, 1) for d in range(1, 15)]
    result = run(make_raw(sales=sales, inventory=[("2026-09-14", 28)]))
    assert result.action == RecommendationAction.NO_ACTION


def test_multiple_shipments_use_total_incoming():
    result = run(make_raw(
        sales=five_per_day(),
        inventory=[("2026-09-14", 10)],
        shipments=[("2026-09-16", 20), ("2026-09-18", 30)],
    ))
    assert result.incoming_quantity == 50
    assert result.action == RecommendationAction.REORDER
    assert result.reorder_quantity == 10  # desired 70 - (10 + 50)


def test_shipment_arriving_today():
    result = run(make_raw(
        sales=five_per_day(),
        inventory=[("2026-09-14", 15)],
        shipments=[("2026-09-14", 50)],
    ))
    assert result.days_until_arrival == 0
    assert result.action == RecommendationAction.MONITOR_PREPARE  # 65 < 70 but no risk
    assert result.incoming_stock_sufficient is True


def test_no_shipment_reports_none_sufficiency():
    result = run(healthy())
    assert result.incoming_quantity == 0
    assert result.incoming_stock_sufficient is None


def test_decreasing_trend_with_adequate_stock_no_action():
    sales = [("2026-09-%02d" % d, 8 if d <= 7 else 2) for d in range(1, 15)]
    result = run(make_raw(sales=sales, inventory=[("2026-09-14", 70)]))
    assert result.demand_trend == DemandTrend.DECREASING
    assert result.action == RecommendationAction.NO_ACTION


def test_insufficient_history_still_recommends():
    # One day of history: trend unavailable, but stockout logic still works.
    result = run(make_raw(
        sales=[("2026-09-14", 10)],
        inventory=[("2026-09-14", 5)],
    ))
    assert result.demand_trend == DemandTrend.UNAVAILABLE
    assert result.action == RecommendationAction.REORDER


def test_priority_order_values():
    assert RecommendationPriority.UNAVAILABLE.value == 0
    assert RecommendationPriority.REORDER.value == 1
    assert RecommendationPriority.REDUCE_EXCESS.value == 2
    assert RecommendationPriority.MONITOR_PREPARE.value == 3
    assert RecommendationPriority.NO_ACTION.value == 4
    assert RecommendationPriority.REORDER < RecommendationPriority.REDUCE_EXCESS


def test_results_are_deterministic():
    raw = shipment_after_stockout()
    first = run(raw)
    second = run(raw)
    assert first == second


# -------------------------------------------------------------- integration

def test_full_pipeline_recommendation_exact():
    """raw spreadsheet strings -> validate -> process -> analytics -> recommendation."""
    raw = {
        "Products": [{
            "product_id": "p-7", "product_name": "កាហ្វេ Coffee 3in1", "category": "Beverages",
            "unit": "pack", "unit_cost": "0.30", "selling_price": "0.50",
            "supplier": "  Phnom Penh Distributor ", "lead_time_days": "2",
            "target_stock_days": "10",
        }],
        "Sales": [
            {"date": "2026-09-12", "product_id": "p-7", "quantity_sold": "6"},
            {"date": "2026-09-13", "product_id": "p-7", "quantity_sold": "4"},
        ],
        "Inventory": [{"date": "2026-09-13", "product_id": "p-7", "quantity_on_hand": " 5 "}],
        "Shipments": [],
    }
    result = run(raw, as_of=date(2026, 9, 13))
    # avg 5/day, target 10 -> desired 50; stock 5 -> reorder 45
    assert result.action == RecommendationAction.REORDER
    assert result.reorder_quantity == 45
    assert result.current_stock == 5
    assert result.target_stock_days == 10
    assert result.product_name == "កាហ្វេ Coffee 3in1"


def test_empty_dataset_yields_no_recommendations():
    assert build_analysis_ready(
        {"Products": [], "Sales": [], "Inventory": [], "Shipments": []}
    ) == []


def test_multiple_products_recommend_independently():
    raw = make_raw(sales=five_per_day(), inventory=[("2026-09-14", 70)])
    raw["Products"].append({
        "product_id": "p2", "product_name": "Milk", "category": "Dairy", "unit": "u",
        "unit_cost": "1.00", "selling_price": "2.00", "supplier": "",
        "lead_time_days": "3", "target_stock_days": "14",
    })
    raw["Sales"] += [
        {"date": "2026-09-%02d" % d, "product_id": "p2", "quantity_sold": "8"}
        for d in range(1, 15)
    ]
    raw["Inventory"].append({"date": "2026-09-14", "product_id": "p2", "quantity_on_hand": "5"})

    processed = build_analysis_ready(raw)
    results = [
        recommend(item.product, compute_product_analytics(item, as_of=AS_OF))
        for item in processed
    ]
    assert results[0].action == RecommendationAction.NO_ACTION  # 70 stock vs 70 target
    assert results[1].action == RecommendationAction.REORDER  # 5 stock, sells 8/day
    assert results[1].reorder_quantity == 107  # 8*14=112 - 5
