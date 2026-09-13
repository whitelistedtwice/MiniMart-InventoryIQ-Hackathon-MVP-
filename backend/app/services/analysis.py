"""Phase 8 orchestration service.

Wires the existing deterministic layers together and presents their
outputs. It contains NO business logic: analytics and recommendations are
computed only by their engines, and AI context only by its builders.

	raw (data access) -> build_analysis_ready -> compute_product_analytics
	-> recommend -> verified AI context
"""

from dataclasses import dataclass
from datetime import date
from typing import Any, Optional

from app.ai_context.builder import build_product_context
from app.analytics.engine import compute_product_analytics
from app.contracts.ai_context import AIProductContext
from app.contracts.analytics import ProductAnalytics
from app.contracts.api import ProductListItem
from app.contracts.data import Product
from app.contracts.recommendation import RecommendationResult
from app.core.errors import NotFoundError
from app.processing.pipeline import build_analysis_ready
from app.recommendations.engine import recommend


@dataclass(frozen=True)
class ProductAnalysis:
    """One product's processed source, analytics, and recommendation."""

    product: Product
    analytics: ProductAnalytics
    recommendation: RecommendationResult

    def context(self) -> AIProductContext:
        """Verified AI context for this product."""
        return build_product_context(self.product, self.analytics, self.recommendation)

    def list_item(self) -> ProductListItem:
        """Inventory-list row built only from verified values."""
        return ProductListItem(
            product_id=self.analytics.product_id,
            product_name=self.analytics.product_name,
            category=self.product.category,
            current_stock=self.analytics.inventory.current_stock,
            status=self.recommendation.action,
            days_remaining=self.analytics.inventory.days_of_stock_remaining,
        )


def analyze(
    raw: dict[str, list[dict[str, Any]]],
    as_of: Optional[date] = None,
) -> list[ProductAnalysis]:
    """Run the full deterministic pipeline over raw sheet rows."""
    results: list[ProductAnalysis] = []
    for processed in build_analysis_ready(raw):
        analytics = compute_product_analytics(processed, as_of=as_of)
        results.append(
            ProductAnalysis(
                product=processed.product,
                analytics=analytics,
                recommendation=recommend(processed.product, analytics),
            )
        )
    return results


def find(analyses: list[ProductAnalysis], product_id: str) -> ProductAnalysis:
    """Return the analysis for one product or raise NotFoundError."""
    for item in analyses:
        if item.product.product_id == product_id:
            return item
    raise NotFoundError(f"Unknown product: {product_id}")
