"""
Deterministic analytics engine (Phase 4).

All metrics are computed only from validated, processed source data.
No Gemini, no frontend, no Google Sheets, no forecasting.

Exact definitions (simple, explainable; constants below):

DEMAND
- total_sold = sum(quantity_sold) over the full history.
  No sales records at all -> None (missing demand, not zero demand).
- average_daily_sales = total_sold / span_days, where
  span_days = (last_sale_date - first_sale_date).days + 1.
  Zero sales rows present -> 0.0 (genuine zero demand).
- recent_daily_sales = average daily sales in the recent half of the span.
  The span is split at its midpoint: earlier half vs recent half.
  Computed only when span >= MIN_TREND_SPAN_DAYS and >= 2 records,
  otherwise None (insufficient history).
- trend = increasing when recent_daily > earlier_daily * (1 + TREND_THRESHOLD),
          decreasing when recent_daily < earlier_daily * (1 - TREND_THRESHOLD),
          otherwise stable. UNAVAILABLE when insufficient history.

INVENTORY
- current_stock = latest inventory snapshot's quantity_on_hand.
  No snapshot -> None (missing inventory, never zero). An observed 0 stays 0.
- inventory_value = current_stock * unit_cost (None when either missing).
- days_of_stock_remaining = current_stock / average_daily_sales.
  None when either is unavailable or average_daily_sales == 0
  (zero demand = no finite estimate; never divide by zero).
- stockout_risk = days_of_stock_remaining < lead_time_days.
  None when either input is unavailable.
- excess_units = max(0, current_stock - average_daily_sales * target_stock_days).
  None unless current_stock, average_daily_sales AND target_stock_days exist.
- excess_value = excess_units * unit_cost (None when either missing).
- stock_status = 'excess' when days > target_stock_days * EXCESS_COVERAGE_FACTOR,
                 'low' when days < lead_time_days,
                 'healthy' when a threshold exists and neither triggers,
                 None otherwise.

SHIPMENTS (current stock and incoming shipments stay separate)
- Only shipments with expected_arrival >= as_of count as incoming.
  Past-dated shipments are ignored.
- incoming_quantity = sum of incoming shipment quantities (0 when none).
- expected_arrival = earliest incoming arrival (None when none).
- days_until_arrival = (expected_arrival - as_of).days (None when none).
- expected_future_inventory = current_stock + incoming_quantity, computed
  only when current_stock is known AND incoming shipments exist; else None.
  It is a projection at arrival, NOT a replacement for current_stock.
- stockout_before_arrival = days_of_stock_remaining < days_until_arrival.
  None when either input is unavailable.

FINANCIAL (sales vs inventory financials are distinct)
- revenue = total_sold * selling_price (None when either missing).
- estimated_cost = total_sold * unit_cost (None when either missing).
- profit = revenue - estimated_cost (None when either missing).
- profit_margin = profit / revenue (None when profit or revenue missing or
  revenue == 0; never divide by zero).
- financial_exposure = inventory_value (cash tied up in current stock).
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from app.contracts.analytics import (
    DemandMetrics,
    DemandTrend,
    FinancialMetrics,
    InventoryMetrics,
    ProductAnalytics,
    ShipmentProjection,
)
from app.processing.pipeline import ProcessedProduct

TREND_THRESHOLD = 0.20        # 20% change between earlier/recent half = trend
MIN_TREND_SPAN_DAYS = 4       # fewer days of history -> trend unavailable
EXCESS_COVERAGE_FACTOR = 2.0  # days_remaining > 2x target days -> 'excess'


def compute_product_analytics(
    processed: ProcessedProduct, as_of: Optional[date] = None
) -> ProductAnalytics:
    """Deterministic analytics for one processed product.

    `as_of` is the reference "today" for shipment timing; defaults to
    date.today(). Tests pass it explicitly for reproducibility.
    """
    as_of = as_of or date.today()
    demand = _demand(processed)
    inventory = _inventory(processed, demand)
    shipment = _shipment(processed, inventory, as_of)
    financial = _financial(processed, demand, inventory)
    return ProductAnalytics(
        product_id=processed.product.product_id,
        product_name=processed.product.product_name,
        demand=demand,
        inventory=inventory,
        shipment=shipment,
        financial=financial,
        sales_history=[(s.date, s.quantity_sold) for s in processed.sales],
        inventory_history=[(s.date, s.quantity_on_hand) for s in processed.inventory],
    )


def _demand(processed: ProcessedProduct) -> DemandMetrics:
    sales = processed.sales
    if not sales:
        return DemandMetrics()  # missing demand: all None / UNAVAILABLE

    total = sum(s.quantity_sold for s in sales)
    first, last = sales[0].date, sales[-1].date
    span = (last - first).days + 1
    average = total / span

    recent = None
    trend = DemandTrend.UNAVAILABLE
    if len(sales) >= 2 and span >= MIN_TREND_SPAN_DAYS:
        midpoint = first + timedelta(days=span // 2)
        earlier_days = span // 2
        recent_days = span - earlier_days
        earlier_daily = sum(s.quantity_sold for s in sales if s.date < midpoint) / earlier_days
        recent = sum(s.quantity_sold for s in sales if s.date >= midpoint) / recent_days
        if recent > earlier_daily * (1 + TREND_THRESHOLD):
            trend = DemandTrend.INCREASING
        elif recent < earlier_daily * (1 - TREND_THRESHOLD):
            trend = DemandTrend.DECREASING
        else:
            trend = DemandTrend.STABLE

    return DemandMetrics(
        total_sold=total,
        average_daily_sales=average,
        recent_daily_sales=recent,
        trend=trend,
    )


def _inventory(processed: ProcessedProduct, demand: DemandMetrics) -> InventoryMetrics:
    snapshot = processed.latest_inventory()
    current = snapshot.quantity_on_hand if snapshot is not None else None
    unit_cost = processed.product.unit_cost
    average = demand.average_daily_sales
    lead_days = processed.product.lead_time_days
    target_days = processed.product.target_stock_days

    value = Decimal(current) * unit_cost if current is not None and unit_cost is not None else None
    days = current / average if current is not None and average is not None and average > 0 else None
    risk = (days < lead_days) if days is not None and lead_days is not None else None

    excess_units = None
    excess_value = None
    if current is not None and average is not None and target_days is not None:
        excess_units = max(0.0, current - average * target_days)
        if unit_cost is not None:
            excess_value = Decimal(str(excess_units)) * unit_cost

    status = None
    if current is not None and days is not None:
        if target_days is not None and days > target_days * EXCESS_COVERAGE_FACTOR:
            status = "excess"
        elif lead_days is not None and days < lead_days:
            status = "low"
        elif target_days is not None or lead_days is not None:
            status = "healthy"
    elif current is not None and excess_units:
        status = "excess"  # zero demand with stock: everything is above target

    return InventoryMetrics(
        current_stock=current,
        inventory_value=value,
        days_of_stock_remaining=days,
        stock_status=status,
        stockout_risk=risk,
        excess_units=excess_units,
        excess_value=excess_value,
    )


def _shipment(
    processed: ProcessedProduct, inventory: InventoryMetrics, as_of: date
) -> ShipmentProjection:
    incoming = [s for s in processed.shipments if s.expected_arrival >= as_of]
    quantity = sum(s.quantity for s in incoming)  # 0 when nothing incoming
    arrival = min((s.expected_arrival for s in incoming), default=None)
    days_until = (arrival - as_of).days if arrival is not None else None

    current = inventory.current_stock
    expected_future = current + quantity if current is not None and incoming else None

    days = inventory.days_of_stock_remaining
    stockout_before = (
        days < days_until if days is not None and days_until is not None else None
    )

    return ShipmentProjection(
        incoming_quantity=quantity,
        expected_arrival=arrival,
        days_until_arrival=days_until,
        expected_future_inventory=expected_future,
        stockout_before_arrival=stockout_before,
    )


def _financial(
    processed: ProcessedProduct, demand: DemandMetrics, inventory: InventoryMetrics
) -> FinancialMetrics:
    price = processed.product.selling_price
    cost = processed.product.unit_cost
    total = demand.total_sold

    revenue = Decimal(total) * price if total is not None and price is not None else None
    estimated = Decimal(total) * cost if total is not None and cost is not None else None
    profit = revenue - estimated if revenue is not None and estimated is not None else None
    margin = (
        float(profit) / float(revenue)
        if profit is not None and revenue is not None and revenue != 0
        else None
    )

    return FinancialMetrics(
        revenue=revenue,
        estimated_cost=estimated,
        profit=profit,
        profit_margin=margin,
        financial_exposure=inventory.inventory_value,
    )
