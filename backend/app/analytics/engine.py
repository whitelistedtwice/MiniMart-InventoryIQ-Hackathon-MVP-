"""
Analytics engine placeholder.

Phase 4 will implement demand, inventory, shipment, and financial
analytics.
"""

from app.contracts.analytics import ProductAnalytics
from app.processing.pipeline import ProcessedProduct


def compute_product_analytics(processed: ProcessedProduct) -> ProductAnalytics:
    """Return deterministic analytics for a single product."""
    raise NotImplementedError("Analytics calculations belong to Phase 4")
