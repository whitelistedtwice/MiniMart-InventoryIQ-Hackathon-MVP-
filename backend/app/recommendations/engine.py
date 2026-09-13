"""
Deterministic recommendation engine (Phase 5).

Consumes verified analytics facts (Phase 4) plus the product's planning
parameters, and produces one deterministic action per product. It never
recomputes analytics and never invents missing values.

EXACT FORMULAS (documented, tested)
-----------------------------------
Inputs:
- avg        = analytics.demand.average_daily_sales (None = no sales history)
- stock      = analytics.inventory.current_stock
- incoming   = analytics.shipment.incoming_quantity (0 when none)
- days_left  = analytics.inventory.days_of_stock_remaining
- days_until = analytics.shipment.days_until_arrival
- target     = product.target_stock_days
- lead       = product.lead_time_days

desired_stock           = avg * target
expected_available      = stock + incoming
bridge_to_arrival       = max(0, ceil(avg * days_until - stock))   # only when
                          stockout_before_arrival is True
reorder_quantity        = max(0, ceil(desired_stock - expected_available),
                              bridge_to_arrival)
immediate_risk          = (stockout_before_arrival is True) or
                          (expected_available < desired_stock and
                           stockout_risk is True)
below_target            = expected_available < desired_stock

DECISION PRIORITY (first match wins; matches Source of Truth §13)
1. UNAVAILABLE   - a required input is missing/insufficient.
                   Required: current stock, sales history, target stock days,
                   and (when avg > 0) supplier lead time.
2. REORDER       - immediate_risk is True.
                    Triggered when we will stock out before the next shipment
                    arrives, OR when target coverage is not met and current
                    coverage is inside the supplier lead time.
3. REDUCE EXCESS - analytics.inventory.stock_status == "excess" and
                    excess_units > 0 (reuses Phase 4's excess detection;
                    no second excess formula).
4. MONITOR/PREPARE - below_target OR demand trend is increasing.
5. NO ACTION     - covered and stable.

Zero demand (avg == 0.0) is valid: desired_stock = 0, no stockout is
possible, and any remaining stock is treated as excess by Phase 4.
"""

import math
from typing import Optional

from app.contracts.analytics import DemandTrend, ProductAnalytics
from app.contracts.data import Product
from app.contracts.recommendation import (
    RecommendationAction,
    RecommendationPriority,
    RecommendationResult,
)


def recommend(product: Product, analytics: ProductAnalytics) -> RecommendationResult:
    """Return the deterministic recommendation for one product."""
    stock = analytics.inventory.current_stock
    avg = analytics.demand.average_daily_sales
    target = product.target_stock_days
    lead = product.lead_time_days
    incoming = analytics.shipment.incoming_quantity or 0

    missing = []
    if stock is None:
        missing.append("current inventory")
    if avg is None:
        missing.append("sales history")
    if target is None:
        missing.append("target stock days")
    if avg is not None and avg > 0 and lead is None:
        missing.append("supplier lead time")
    if missing:
        return _result(
            product,
            analytics,
            RecommendationAction.UNAVAILABLE,
            RecommendationPriority.UNAVAILABLE,
            evidence=[f"Missing required information: {', '.join(missing)}."],
        )

    desired = avg * target
    expected = stock + incoming
    days_left = analytics.inventory.days_of_stock_remaining
    # Reorder immediately only when there is a real near-term shortfall:
    #   - no shipment prevents it, target is not met, and current coverage is
    #     inside the supplier lead time; OR
    #   - we will run out before the incoming shipment arrives.
    immediate_risk = (
        analytics.shipment.stockout_before_arrival is True
        or (
            expected < desired
            and analytics.inventory.stockout_risk is True
        )
    )
    incoming_sufficient = _incoming_sufficient(analytics)

    if immediate_risk:
        quantity = max(0, math.ceil(desired - expected))
        if (
            analytics.shipment.stockout_before_arrival is True
            and analytics.shipment.days_until_arrival is not None
        ):
            bridge = math.ceil(avg * analytics.shipment.days_until_arrival - stock)
            quantity = max(quantity, bridge)
        return _result(
            product,
            analytics,
            RecommendationAction.REORDER,
            RecommendationPriority.REORDER,
            reorder_quantity=max(0, quantity),
            reorder_timing=_reorder_timing(analytics, days_left, lead),
            incoming_stock_sufficient=incoming_sufficient,
            evidence=_reorder_evidence(analytics, product, desired, quantity, days_left),
        )

    if analytics.inventory.stock_status == "excess" and (analytics.inventory.excess_units or 0) > 0:
        return _result(
            product,
            analytics,
            RecommendationAction.REDUCE_EXCESS,
            RecommendationPriority.REDUCE_EXCESS,
            incoming_stock_sufficient=incoming_sufficient,
            evidence=_excess_evidence(analytics, product),
        )

    below_target = expected < desired
    if below_target or analytics.demand.trend == DemandTrend.INCREASING:
        return _result(
            product,
            analytics,
            RecommendationAction.MONITOR_PREPARE,
            RecommendationPriority.MONITOR_PREPARE,
            incoming_stock_sufficient=incoming_sufficient,
            evidence=_monitor_evidence(analytics, product, desired, expected),
        )

    return _result(
        product,
        analytics,
        RecommendationAction.NO_ACTION,
        RecommendationPriority.NO_ACTION,
        incoming_stock_sufficient=incoming_sufficient,
        evidence=_no_action_evidence(analytics, product, days_left),
    )


def _incoming_sufficient(analytics: ProductAnalytics) -> Optional[bool]:
    """True if incoming stock arrives before stock runs out; None if none."""
    if analytics.shipment.expected_arrival is None:
        return None
    return analytics.shipment.stockout_before_arrival is not True


def _reorder_timing(
    analytics: ProductAnalytics, days_left: Optional[float], lead: Optional[int]
) -> str:
    if analytics.shipment.stockout_before_arrival is True:
        return "Order immediately - current stock may run out before the shipment arrives."
    if days_left is not None:
        whole_days = math.floor(days_left)
        return f"Order within {whole_days} day(s)." if whole_days > 0 else "Order now."
    return "Order now."


def _reorder_evidence(
    analytics: ProductAnalytics,
    product: Product,
    desired: float,
    quantity: int,
    days_left: Optional[float],
) -> list[str]:
    evidence: list[str] = []
    until = analytics.shipment.days_until_arrival
    if analytics.shipment.stockout_before_arrival is True and until is not None:
        evidence.append(
            f"Stock covers about {days_left:.1f} days, but the next shipment arrives in {until} day(s)."
        )
    elif days_left is not None and product.lead_time_days is not None:
        evidence.append(
            f"Stock covers about {days_left:.1f} days, less than the {product.lead_time_days}-day supplier lead time."
        )
    if quantity > 0:
        evidence.append(
            f"Order {quantity} units to reach {product.target_stock_days} days of coverage (about {desired:.0f} units)."
        )
    else:
        evidence.append(
            "Current and incoming stock already meet target coverage; the risk is lead-time driven."
        )
    return evidence


def _excess_evidence(analytics: ProductAnalytics, product: Product) -> list[str]:
    evidence = [
        f"Stock is {(analytics.inventory.excess_units or 0):.0f} units above the {product.target_stock_days}-day target."
    ]
    if analytics.inventory.excess_value is not None:
        evidence.append(f"About {analytics.inventory.excess_value:.2f} in inventory value is tied up.")
    if analytics.demand.trend == DemandTrend.DECREASING:
        evidence.append("Sales are decreasing, so this stock may sit longer.")
    evidence.append("Consider reducing stock (discount, return, or pause reordering).")
    return evidence


def _monitor_evidence(
    analytics: ProductAnalytics, product: Product, desired: float, expected: int
) -> list[str]:
    evidence: list[str] = []
    if analytics.demand.trend == DemandTrend.INCREASING:
        evidence.append("Demand is increasing compared with earlier sales.")
    if expected < desired:
        evidence.append(
            f"Projected stock ({expected} units) is below the {product.target_stock_days}-day target ({desired:.0f} units)."
        )
    evidence.append("Monitor demand and prepare additional stock if the trend continues.")
    return evidence


def _no_action_evidence(
    analytics: ProductAnalytics, product: Product, days_left: Optional[float]
) -> list[str]:
    evidence: list[str] = []
    if days_left is not None:
        evidence.append(
            f"Stock covers about {days_left:.1f} days, within the {product.target_stock_days}-day target."
        )
    if analytics.demand.trend == DemandTrend.STABLE:
        evidence.append("Demand is stable.")
    evidence.append("No action needed.")
    return evidence


def _result(
    product: Product,
    analytics: ProductAnalytics,
    action: RecommendationAction,
    priority: RecommendationPriority,
    *,
    reorder_quantity: Optional[int] = None,
    reorder_timing: Optional[str] = None,
    incoming_stock_sufficient: Optional[bool] = None,
    evidence: Optional[list[str]] = None,
) -> RecommendationResult:
    return RecommendationResult(
        product_id=analytics.product_id,
        product_name=analytics.product_name,
        action=action,
        priority=priority,
        reorder_quantity=reorder_quantity,
        reorder_timing=reorder_timing,
        incoming_stock_sufficient=incoming_stock_sufficient,
        evidence=evidence or [],
        current_stock=analytics.inventory.current_stock,
        incoming_quantity=analytics.shipment.incoming_quantity,
        days_of_stock_remaining=analytics.inventory.days_of_stock_remaining,
        days_until_arrival=analytics.shipment.days_until_arrival,
        demand_trend=analytics.demand.trend,
        target_stock_days=product.target_stock_days,
        excess_units=analytics.inventory.excess_units,
    )
