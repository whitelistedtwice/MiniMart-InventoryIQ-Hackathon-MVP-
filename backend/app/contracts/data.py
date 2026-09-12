"""
Raw source-data contracts.

These structures mirror the four Google Sheets tabs described in the
InventoryIQ Source of Truth.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    """A single product in the mini-mart catalog."""

    product_id: str = Field(..., description="Stable product identifier")
    product_name: str = Field(..., description="Display name; may include Khmer, English, or mixed text")
    category: Optional[str] = Field(None, description="Product category")
    unit: Optional[str] = Field(None, description="Unit of sale, e.g. 'bottle', 'pack'")
    unit_cost: Optional[Decimal] = Field(None, description="Cost per unit in local currency")
    selling_price: Optional[Decimal] = Field(None, description="Selling price per unit")
    supplier: Optional[str] = Field(None, description="Supplier name")
    lead_time_days: Optional[int] = Field(None, description="Typical supplier lead time in days")
    target_stock_days: Optional[int] = Field(None, description="Desired stock coverage in days")


class Sale(BaseModel):
    """One daily sales record for a product."""

    date: date
    product_id: str
    quantity_sold: int = Field(..., ge=0)


class InventorySnapshot(BaseModel):
    """
    Observed physical inventory for a product on a given date.

    IMPORTANT: missing inventory must remain distinguishable from zero
    inventory. A missing snapshot is represented by absence of the record,
    not by quantity_on_hand = 0.
    """

    date: date
    product_id: str
    quantity_on_hand: int = Field(..., ge=0)


class Shipment(BaseModel):
    """A future incoming supplier shipment."""

    shipment_id: str = Field(..., description="Stable shipment identifier")
    product_id: str
    quantity: int = Field(..., gt=0)
    expected_arrival: date
