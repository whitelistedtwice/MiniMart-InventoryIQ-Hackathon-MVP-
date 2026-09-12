"""
Validation placeholder.

Phase 3 will implement validation of sheets, columns, dates, numbers,
product IDs, duplicates, and shipment dates.
"""

from app.contracts.data import InventorySnapshot, Product, Sale, Shipment


def validate_data(
    products: list[Product],
    sales: list[Sale],
    inventory: list[InventorySnapshot],
    shipments: list[Shipment],
) -> None:
    """Validate source data and raise ValidationError on problems."""
    raise NotImplementedError("Validation logic belongs to Phase 3")
