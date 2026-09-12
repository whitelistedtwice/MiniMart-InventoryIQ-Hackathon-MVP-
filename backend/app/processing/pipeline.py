"""
Processing placeholder.

Phase 3 will normalize and combine validated source data into
analysis-ready structures.
"""

from collections import defaultdict
from datetime import date
from typing import Optional

from app.contracts.data import InventorySnapshot, Product, Sale, Shipment


class ProcessedProduct:
    """Analysis-ready view of one product and its related records."""

    def __init__(
        self,
        product: Product,
        sales: list[Sale],
        inventory: list[InventorySnapshot],
        shipments: list[Shipment],
    ):
        self.product = product
        self.sales = sales
        self.inventory = inventory
        self.shipments = shipments

    def latest_inventory(self, as_of: Optional[date] = None) -> Optional[InventorySnapshot]:
        """Return the most recent inventory snapshot up to as_of."""
        if not self.inventory:
            return None
        cutoff = as_of or max(s.date for s in self.inventory)
        candidates = [s for s in self.inventory if s.date <= cutoff]
        return max(candidates, key=lambda s: s.date) if candidates else None


def process(
    products: list[Product],
    sales: list[Sale],
    inventory: list[InventorySnapshot],
    shipments: list[Shipment],
) -> list[ProcessedProduct]:
    """Group and normalize validated source data by product."""
    sales_by_product: dict[str, list[Sale]] = defaultdict(list)
    inventory_by_product: dict[str, list[InventorySnapshot]] = defaultdict(list)
    shipments_by_product: dict[str, list[Shipment]] = defaultdict(list)

    for sale in sales:
        sales_by_product[sale.product_id].append(sale)
    for snap in inventory:
        inventory_by_product[snap.product_id].append(snap)
    for shipment in shipments:
        shipments_by_product[shipment.product_id].append(shipment)

    return [
        ProcessedProduct(
            product=p,
            sales=sales_by_product.get(p.product_id, []),
            inventory=inventory_by_product.get(p.product_id, []),
            shipments=shipments_by_product.get(p.product_id, []),
        )
        for p in products
    ]
