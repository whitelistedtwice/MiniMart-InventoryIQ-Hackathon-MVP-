"""
Analytics result contracts.

All values are backend-owned. Optional fields mean "unavailable".
A value of None does NOT mean zero.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DemandTrend(str, Enum):
    INCREASING = "increasing"
    STABLE = "stable"
    DECREASING = "decreasing"
    UNAVAILABLE = "unavailable"


class DemandMetrics(BaseModel):
    """Sales/demand analytics for one product."""

    total_sold: Optional[int] = Field(None, description="Total units sold over the analysis window")
    average_daily_sales: Optional[float] = Field(None, description="Average units sold per day")
    recent_daily_sales: Optional[float] = Field(None, description="Average over the most recent short window")
    trend: DemandTrend = DemandTrend.UNAVAILABLE


class InventoryMetrics(BaseModel):
    """Current inventory state for one product."""

    current_stock: Optional[int] = Field(
        None,
        description="Latest observed physical stock. None means unavailable, not zero.",
    )
    inventory_value: Optional[Decimal] = Field(None, description="current_stock * unit_cost when both available")
    days_of_stock_remaining: Optional[float] = Field(None, description="Estimated days current stock will last")
    stock_status: Optional[str] = Field(None, description="Human-readable status label")
    stockout_risk: bool = Field(False, description="True when a stockout is projected before safe coverage")


class ShipmentProjection(BaseModel):
    """Projection of incoming supplier stock.

    Current stock and incoming shipment quantities remain separate.
    expected_future_inventory is a derived convenience, not a replacement
    for current_stock.
    """

    incoming_quantity: Optional[int] = Field(None, description="Sum of outstanding shipment quantities")
    expected_arrival: Optional[date] = Field(None, description="Next incoming shipment arrival date")
    days_until_arrival: Optional[int] = Field(None, description="Days until expected_arrival")
    expected_future_inventory: Optional[int] = Field(
        None,
        description="current_stock + incoming_quantity when both available",
    )
    stockout_before_arrival: Optional[bool] = Field(
        None,
        description="True if stock is projected to run out before the shipment arrives",
    )


class FinancialMetrics(BaseModel):
    """Financial analytics for one product."""

    revenue: Optional[Decimal] = Field(None, description="Sold quantity * selling_price")
    estimated_cost: Optional[Decimal] = Field(None, description="Sold quantity * unit_cost")
    profit: Optional[Decimal] = Field(None, description="revenue - estimated_cost")
    profit_margin: Optional[float] = Field(None, description="profit / revenue when revenue > 0")
    financial_exposure: Optional[Decimal] = Field(
        None,
        description="Value tied up in current inventory (current_stock * unit_cost)",
    )


class ProductAnalytics(BaseModel):
    """Complete deterministic analytics for a single product."""

    product_id: str
    product_name: str
    demand: DemandMetrics
    inventory: InventoryMetrics
    shipment: ShipmentProjection
    financial: FinancialMetrics
