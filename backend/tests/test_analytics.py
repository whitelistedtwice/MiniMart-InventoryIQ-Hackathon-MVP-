"""
Phase 4 analytics tests.

Exact-value tests for every metric, plus the full
raw -> validation -> processing -> analytics integration path.
"""

from datetime import date
from decimal import Decimal

import pytest

from app.analytics.engine import compute_product_analytics
from app.contracts.analytics import DemandTrend
from app.processing.pipeline import build_analysis_ready
from tests.fixtures import (
    ALL_SCENARIOS,
    excess_slow_moving,
    healthy,
    immediate_stockout,
    increasing_demand,
    shipment_after_stockout,
    shipment_before_stockout,
)

AS_OF = date(2026, 9, 14)  # last inventory date in the canonical fixtures


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


def analyze(raw, as_of=AS_OF):
    """Full pipeline: raw -> validate -> process -> analytics."""
    return compute_product_analytics(build_analysis_ready(raw)[0], as_of=as_of)


# ------------------------------------------------------------------- demand

def test_demand_exact_values():
    result = analyze(make_raw(
        sales=[("2026-09-01", 5), ("2026-09-02", 7)],
        inventory=[("2026-09-02", 10)],
    ))
    assert result.demand.total_sold == 12
    assert result.demand.average_daily_sales == 6.0  # 12 / 2 days


def test_trend_stable_exact():
    sales = [("2026-09-%02d" % d, 5) for d in range(1, 15)]
    result = analyze(make_raw(sales=sales, inventory=[("2026-09-14", 70)]))
    assert result.demand.trend == DemandTrend.STABLE
    assert result.demand.recent_daily_sales == 5.0


def test_trend_increasing_and_decreasing_exact():
    up = analyze(make_raw(
        sales=[("2026-09-%02d" % d, 2 if d <= 7 else 8) for d in range(1, 15)],
        inventory=[("2026-09-14", 40)],
    ))
    assert up.demand.recent_daily_sales == 8.0
    assert up.demand.trend == DemandTrend.INCREASING

    down = analyze(make_raw(
        sales=[("2026-09-%02d" % d, 8 if d <= 7 else 2) for d in range(1, 15)],
        inventory=[("2026-09-14", 40)],
    ))
    assert down.demand.recent_daily_sales == 2.0
    assert down.demand.trend == DemandTrend.DECREASING


def test_one_day_history_trend_unavailable():
    result = analyze(make_raw(sales=[("2026-09-14", 10)], inventory=[("2026-09-14", 5)]))
    assert result.demand.total_sold == 10
    assert result.demand.average_daily_sales == 10.0
    assert result.demand.recent_daily_sales is None
    assert result.demand.trend == DemandTrend.UNAVAILABLE


def test_insufficient_history_trend_unavailable():
    sales = [("2026-09-01", 2), ("2026-09-02", 4), ("2026-09-03", 6)]  # span 3 < 4
    result = analyze(make_raw(sales=sales, inventory=[("2026-09-03", 5)]))
    assert result.demand.total_sold == 12
    assert result.demand.recent_daily_sales is None
    assert result.demand.trend == DemandTrend.UNAVAILABLE


def test_zero_sales_is_valid_zero_demand():
    sales = [("2026-09-%02d" % d, 0) for d in range(1, 15)]
    result = analyze(make_raw(sales=sales, inventory=[("2026-09-14", 30)]))
    assert result.demand.total_sold == 0
    assert result.demand.average_daily_sales == 0.0
    assert result.demand.trend == DemandTrend.STABLE
    # Zero demand -> no finite days estimate, and no crash.
    assert result.inventory.days_of_stock_remaining is None
    assert result.inventory.stockout_risk is None
    # With zero demand, all 30 units exceed the zero target stock.
    assert result.inventory.excess_units == 30.0


def test_no_sales_is_missing_not_zero():
    result = analyze(make_raw(sales=[], inventory=[("2026-09-14", 30)]))
    assert result.demand.total_sold is None
    assert result.demand.average_daily_sales is None
    assert result.demand.trend == DemandTrend.UNAVAILABLE
    assert result.inventory.days_of_stock_remaining is None
    assert result.inventory.excess_units is None  # needs demand
    assert result.financial.revenue is None  # no sales -> missing, not $0


# ----------------------------------------------------------------- inventory

def test_missing_inventory_stays_unavailable():
    result = analyze(make_raw(sales=[("2026-09-01", 5)], inventory=[]))
    assert result.inventory.current_stock is None
    assert result.inventory.inventory_value is None
    assert result.inventory.days_of_stock_remaining is None
    assert result.inventory.stockout_risk is None
    assert result.inventory.stock_status is None
    assert result.inventory.excess_units is None


def test_observed_zero_stock_stays_zero():
    result = analyze(make_raw(
        sales=[("2026-09-01", 5), ("2026-09-02", 5)],
        inventory=[("2026-09-02", 0)],
    ))
    assert result.inventory.current_stock == 0
    assert result.inventory.current_stock is not None  # zero is a real value
    assert result.inventory.days_of_stock_remaining == 0.0
    assert result.inventory.stockout_risk is True  # 0 < 3 day lead time
    assert result.inventory.stock_status == "low"


def test_days_of_stock_remaining_exact():
    result = analyze(make_raw(
        sales=[("2026-09-01", 4), ("2026-09-02", 4), ("2026-09-03", 4), ("2026-09-04", 4)],
        inventory=[("2026-09-04", 20)],
    ))
    assert result.inventory.days_of_stock_remaining == 5.0


def test_current_stock_uses_latest_snapshot():
    result = analyze(make_raw(
        sales=[("2026-09-01", 1)],
        inventory=[("2026-09-01", 50), ("2026-09-05", 12), ("2026-09-03", 30)],
    ))
    assert result.inventory.current_stock == 12


def test_stockout_risk_exact_boundaries():
    # days 3.0, lead 3 -> NOT risk (strict <)
    result = analyze(make_raw(
        sales=[("2026-09-01", 5), ("2026-09-02", 5)],
        inventory=[("2026-09-02", 15)],
    ))
    assert result.inventory.days_of_stock_remaining == 3.0
    assert result.inventory.stockout_risk is False
        # days 2.4, lead 3 -> risk
    result = analyze(make_raw(
        sales=[("2026-09-01", 5), ("2026-09-02", 5)],
        inventory=[("2026-09-02", 12)],
    ))
    assert result.inventory.days_of_stock_remaining == 2.4
    assert result.inventory.stockout_risk is True


def test_missing_lead_time_risk_unavailable():
    product = {
        "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
        "unit_cost": "0.50", "selling_price": "0.75", "supplier": "",
        "lead_time_days": "", "target_stock_days": "14",
    }
    result = analyze(make_raw(product=product, sales=[("2026-09-01", 5)], inventory=[("2026-09-01", 10)]))
    assert result.inventory.stockout_risk is None
    assert result.inventory.days_of_stock_remaining == 2.0


def test_missing_target_days_excess_unavailable():
    product = {
        "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
        "unit_cost": "0.50", "selling_price": "0.75", "supplier": "",
        "lead_time_days": "3", "target_stock_days": "",
    }
    result = analyze(make_raw(product=product, sales=[("2026-09-01", 5)], inventory=[("2026-09-01", 100)]))
    assert result.inventory.excess_units is None
    assert result.inventory.excess_value is None


def test_excess_exact_units_and_value():
    sales = [("2026-09-%02d" % d, 1) for d in range(1, 15)]  # avg 1/day
    result = analyze(make_raw(sales=sales, inventory=[("2026-09-14", 100)]))
    # target stock = 1 * 14 = 14 -> excess = 86, value = 86 * 0.50
    assert result.inventory.excess_units == 86.0
    assert result.inventory.excess_value == Decimal("43.0")
    assert result.inventory.stock_status == "excess"


# ----------------------------------------------------------------- shipments

def test_no_shipments():
    result = analyze(make_raw(sales=[("2026-09-01", 5)], inventory=[("2026-09-01", 15)]))
    assert result.shipment.incoming_quantity == 0  # genuinely zero, not missing
    assert result.shipment.expected_arrival is None
    assert result.shipment.days_until_arrival is None
    assert result.shipment.expected_future_inventory is None
    assert result.shipment.stockout_before_arrival is None


def test_shipment_arriving_today():
    result = analyze(make_raw(
        sales=[("2026-09-01", 5)],
        inventory=[("2026-09-14", 15)],
        shipments=[("2026-09-14", 50)],
    ))
    assert result.shipment.days_until_arrival == 0
    assert result.shipment.incoming_quantity == 50
    assert result.shipment.expected_future_inventory == 65
    assert result.inventory.current_stock == 15  # shipment does not inflate current stock


def test_shipment_before_vs_after_stockout():
    base = dict(
        sales=[("2026-09-%02d" % d, 8) for d in range(1, 15)],  # avg 8/day
        inventory=[("2026-09-14", 24)],  # 3.0 days
    )
    before = analyze(make_raw(shipments=[("2026-09-16", 50)], **base))
    assert before.shipment.days_until_arrival == 2
    assert before.shipment.stockout_before_arrival is False  # 3.0 !< 2

    after = analyze(make_raw(shipments=[("2026-09-19", 50)], **base))
    assert after.shipment.days_until_arrival == 5
    assert after.shipment.stockout_before_arrival is True  # 3.0 < 5


def test_multiple_shipments_sum_and_earliest_arrival():
    result = analyze(make_raw(
        sales=[("2026-09-01", 5)],
        inventory=[("2026-09-14", 10)],
        shipments=[("2026-09-20", 20), ("2026-09-16", 30), ("2026-09-25", 10)],
    ))
    assert result.shipment.incoming_quantity == 60
    assert result.shipment.expected_arrival == date(2026, 9, 16)
    assert result.shipment.days_until_arrival == 2
    assert result.shipment.expected_future_inventory == 70


def test_past_shipment_is_ignored():
    result = analyze(make_raw(
        sales=[("2026-09-01", 5)],
        inventory=[("2026-09-14", 10)],
        shipments=[("2026-09-10", 50)],  # already past as of 2026-09-14
    ))
    assert result.shipment.incoming_quantity == 0
    assert result.shipment.expected_arrival is None
    assert result.shipment.expected_future_inventory is None


def test_current_stock_never_includes_shipments():
    result = analyze(make_raw(
        sales=[("2026-09-01", 5)],
        inventory=[("2026-09-14", 15)],
        shipments=[("2026-09-16", 50)],
    ))
    assert result.inventory.current_stock == 15
    assert result.shipment.incoming_quantity == 50
    assert result.shipment.expected_future_inventory == 65  # projection only
    assert result.inventory.current_stock != result.shipment.expected_future_inventory


# ----------------------------------------------------------------- financial

def test_financial_exact_values():
    result = analyze(healthy())
    # healthy: 70 units sold, price 0.75, cost 0.50, stock 70
    assert result.financial.revenue == Decimal("52.50")
    assert result.financial.estimated_cost == Decimal("35.00")
    assert result.financial.profit == Decimal("17.50")
    assert abs(result.financial.profit_margin - (17.5 / 52.5)) < 1e-9
    assert result.inventory.inventory_value == Decimal("35.00")
    assert result.financial.financial_exposure == Decimal("35.00")


def test_missing_selling_price():
    product = {
        "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
        "unit_cost": "0.50", "selling_price": "", "supplier": "",
        "lead_time_days": "3", "target_stock_days": "14",
    }
    result = analyze(make_raw(product=product, sales=[("2026-09-01", 4)], inventory=[("2026-09-01", 10)]))
    assert result.financial.revenue is None
    assert result.financial.estimated_cost == Decimal("2.00")
    assert result.financial.profit is None
    assert result.financial.profit_margin is None
    assert result.inventory.inventory_value == Decimal("5.00")  # cost-side still works


def test_missing_unit_cost():
    product = {
        "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
        "unit_cost": "", "selling_price": "0.75", "supplier": "",
        "lead_time_days": "3", "target_stock_days": "14",
    }
    result = analyze(make_raw(product=product, sales=[("2026-09-01", 4)], inventory=[("2026-09-01", 10)]))
    assert result.financial.revenue == Decimal("3.00")
    assert result.financial.estimated_cost is None
    assert result.financial.profit is None
    assert result.inventory.inventory_value is None
    assert result.financial.financial_exposure is None
    assert result.inventory.excess_value is None  # cost-dependent


def test_zero_revenue_no_division_by_zero():
    sales = [("2026-09-01", 0), ("2026-09-02", 0)]
    result = analyze(make_raw(sales=sales, inventory=[("2026-09-02", 10)]))
    assert result.financial.revenue == Decimal("0.00")
    assert result.financial.estimated_cost == Decimal("0.00")
    assert result.financial.profit == Decimal("0.00")
    assert result.financial.profit_margin is None  # revenue == 0 -> unavailable


def test_decimal_prices_stay_exact():
    product = {
        "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
        "unit_cost": "0.33", "selling_price": "0.99", "supplier": "",
        "lead_time_days": "3", "target_stock_days": "14",
    }
    result = analyze(make_raw(product=product, sales=[("2026-09-01", 3)], inventory=[("2026-09-01", 7)]))
    assert result.financial.revenue == Decimal("2.97")
    assert result.inventory.inventory_value == Decimal("2.31")


def test_large_quantities():
    result = analyze(make_raw(
        sales=[("2026-09-01", 1_000_000)],
        inventory=[("2026-09-01", 2_000_000)],
    ))
    assert result.demand.total_sold == 1_000_000
    assert result.financial.revenue == Decimal("750000.00")


# ----------------------------------------------------------------- history

def test_history_is_chronological_and_exact():
    result = analyze(make_raw(
        sales=[("2026-09-03", 3), ("2026-09-01", 1), ("2026-09-02", 2)],
        inventory=[("2026-09-02", 20), ("2026-09-01", 25)],
    ))
    assert result.sales_history == [
        (date(2026, 9, 1), 1), (date(2026, 9, 2), 2), (date(2026, 9, 3), 3),
    ]
    assert result.inventory_history == [(date(2026, 9, 1), 25), (date(2026, 9, 2), 20)]


# ----------------------------------------------------------- canonical runs

@pytest.mark.parametrize("scenario", list(ALL_SCENARIOS))
def test_canonical_scenarios_produce_sensible_metrics(scenario):
    result = compute_product_analytics(
        build_analysis_ready(ALL_SCENARIOS[scenario]())[0], as_of=AS_OF
    )
    assert result.demand.total_sold is not None and result.demand.total_sold > 0
    assert result.inventory.current_stock is not None


def test_canonical_exact_outcomes():
    healthy_r = compute_product_analytics(build_analysis_ready(healthy())[0], as_of=AS_OF)
    assert healthy_r.demand.average_daily_sales == 5.0
    assert healthy_r.demand.trend == DemandTrend.STABLE
    assert healthy_r.inventory.days_of_stock_remaining == 14.0
    assert healthy_r.inventory.stockout_risk is False
    assert healthy_r.inventory.stock_status == "healthy"
    assert healthy_r.inventory.excess_units == 0.0

    stockout = compute_product_analytics(build_analysis_ready(immediate_stockout())[0], as_of=AS_OF)
    assert stockout.inventory.days_of_stock_remaining == 0.5
    assert stockout.inventory.stockout_risk is True
    assert stockout.inventory.stock_status == "low"
    assert stockout.shipment.incoming_quantity == 0
    assert stockout.shipment.stockout_before_arrival is None

    before = compute_product_analytics(build_analysis_ready(shipment_before_stockout())[0], as_of=AS_OF)
    assert before.shipment.incoming_quantity == 50
    assert before.shipment.days_until_arrival == 2
    assert before.shipment.expected_future_inventory == 74
    assert before.shipment.stockout_before_arrival is False

    after = compute_product_analytics(build_analysis_ready(shipment_after_stockout())[0], as_of=AS_OF)
    assert after.shipment.days_until_arrival == 5
    assert after.shipment.stockout_before_arrival is True

    excess = compute_product_analytics(build_analysis_ready(excess_slow_moving())[0], as_of=AS_OF)
    assert excess.inventory.stock_status == "excess"
    assert excess.inventory.excess_units == 86.0
    assert excess.inventory.excess_value == Decimal("43.0")
    assert excess.inventory.stockout_risk is False

    trend = compute_product_analytics(build_analysis_ready(increasing_demand())[0], as_of=AS_OF)
    assert trend.demand.trend == DemandTrend.INCREASING
    assert trend.demand.average_daily_sales == 5.0
    assert trend.demand.recent_daily_sales == 8.0
    assert trend.inventory.days_of_stock_remaining == 8.0


# -------------------------------------------------------------- integration

def test_full_pipeline_integration_exact():
    """raw sheet-shaped strings -> validate -> process -> analytics, exact values."""
    raw = {
        "Products": [{
            "product_id": "p-42", "product_name": "Fish Sauce 500ml", "category": "Condiments",
            "unit": "bottle", "unit_cost": "1.20", "selling_price": "2.00",
            "supplier": "  Mekong Co ", "lead_time_days": "4", "target_stock_days": "7",
        }],
        "Sales": [
            {"date": "2026-09-12", "product_id": "p-42", "quantity_sold": "6"},
            {"date": "2026-09-10", "product_id": "p-42", "quantity_sold": "4"},
            {"date": "2026-09-11", "product_id": "p-42", "quantity_sold": "5"},
            {"date": "2026-09-13", "product_id": "p-42", "quantity_sold": "7"},
        ],
        "Inventory": [{"date": "2026-09-13", "product_id": "p-42", "quantity_on_hand": " 22 "}],
        "Shipments": [{
            "shipment_id": "sh-9", "product_id": "p-42",
            "quantity": "30", "expected_arrival": "2026-09-17",
        }],
    }
    result = compute_product_analytics(build_analysis_ready(raw)[0], as_of=date(2026, 9, 13))

    assert result.demand.total_sold == 22
    assert result.demand.average_daily_sales == 5.5
    assert result.inventory.current_stock == 22  # whitespace-trimmed " 22 "
    assert result.inventory.days_of_stock_remaining == 4.0
    assert result.inventory.stockout_risk is False  # 4.0 !< 4
    assert result.shipment.days_until_arrival == 4
    assert result.shipment.stockout_before_arrival is False  # 4.0 !< 4
    assert result.shipment.expected_future_inventory == 52
    assert result.financial.revenue == Decimal("44.00")
    assert result.financial.estimated_cost == Decimal("26.40")
    assert result.financial.profit == Decimal("17.60")


def test_empty_valid_dataset_produces_no_analytics():
    assert build_analysis_ready({"Products": [], "Sales": [], "Inventory": [], "Shipments": []}) == []


def test_multiple_products_are_independent():
    raw = make_raw(sales=[("2026-09-01", 5)], inventory=[("2026-09-01", 10)])
    raw["Products"].append({
        "product_id": "p2", "product_name": "Second", "category": "Other", "unit": "u",
        "unit_cost": "1.00", "selling_price": "2.00", "supplier": "", "lead_time_days": "1",
        "target_stock_days": "7",
    })
    raw["Sales"].append({"date": "2026-09-01", "product_id": "p2", "quantity_sold": "20"})
    raw["Inventory"].append({"date": "2026-09-01", "product_id": "p2", "quantity_on_hand": "3"})

    processed = build_analysis_ready(raw)
    first = compute_product_analytics(processed[0], as_of=AS_OF)
    second = compute_product_analytics(processed[1], as_of=AS_OF)
    assert first.demand.total_sold == 5
    assert second.demand.total_sold == 20
    assert first.inventory.stockout_risk is True  # 2.0 days < 3 lead
    assert second.inventory.stockout_risk is True  # 0.15 days < 1 lead
    assert first.financial.revenue == Decimal("3.75")
    assert second.financial.revenue == Decimal("40.00")
