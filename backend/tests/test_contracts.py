"""
Architecture / contract tests for Phase 1.

These tests do not exercise business logic. They prove that the contract
models can be constructed, that unavailable data is explicit, and that
critical invariants are encoded in the type system.
"""

from datetime import date, datetime

import pytest

from app.contracts.ai_context import AIProductContext, AIBusinessBriefContext
from app.contracts.analytics import (
    DemandMetrics,
    DemandTrend,
    InventoryMetrics,
    ProductAnalytics,
    ShipmentProjection,
    FinancialMetrics,
)
from app.contracts.api import (
    AIExplanationResponse,
    AnalyticsResponse,
    ApiError,
    DashboardResponse,
    ProductDetailResponse,
    ProductListItem,
    SettingsResponse,
)
from app.contracts.data import InventorySnapshot, Product, Sale, Shipment
from app.contracts.recommendation import (
    RecommendationAction,
    RecommendationPriority,
    RecommendationResult,
)


class TestSourceDataContracts:
    def test_product_contract(self):
        product = Product(
            product_id="coke-330",
            product_name="Coca-Cola 330ml",
            category="Beverages",
            unit="can",
            unit_cost="0.50",
            selling_price="0.75",
            supplier="Coke Distributor",
            lead_time_days=3,
            target_stock_days=14,
        )
        assert product.product_id == "coke-330"
        assert product.lead_time_days == 3

    def test_missing_optional_product_fields_are_none(self):
        product = Product(product_id="x", product_name="Unknown")
        assert product.category is None
        assert product.lead_time_days is None

    def test_inventory_is_not_automatically_zero(self):
        """An absent snapshot must not be represented as quantity 0."""
        snap = InventorySnapshot(date=date(2026, 9, 1), product_id="coke-330", quantity_on_hand=10)
        assert snap.quantity_on_hand == 10

    def test_shipment_is_separate_from_inventory(self):
        shipment = Shipment(
            shipment_id="sh-1",
            product_id="coke-330",
            quantity=50,
            expected_arrival=date(2026, 9, 10),
        )
        assert shipment.quantity == 50


class TestAnalyticsContracts:
    def test_unavailable_metrics_are_explicit(self):
        metrics = InventoryMetrics()
        assert metrics.current_stock is None
        assert metrics.days_of_stock_remaining is None

    def test_demand_trend_default_is_unavailable(self):
        demand = DemandMetrics()
        assert demand.trend == DemandTrend.UNAVAILABLE

    def test_shipment_projection_keeps_current_and_incoming_separate(self):
        projection = ShipmentProjection(
            incoming_quantity=50,
            expected_future_inventory=65,
        )
        assert projection.incoming_quantity == 50
        assert projection.expected_future_inventory == 65

    def test_product_analytics_can_be_built(self):
        analytics = ProductAnalytics(
            product_id="coke-330",
            product_name="Coca-Cola 330ml",
            demand=DemandMetrics(),
            inventory=InventoryMetrics(current_stock=15),
            shipment=ShipmentProjection(incoming_quantity=50),
            financial=FinancialMetrics(),
        )
        assert analytics.inventory.current_stock == 15
        assert analytics.shipment.incoming_quantity == 50
        assert analytics.financial.profit is None


class TestRecommendationContract:
    def test_all_supported_actions_exist(self):
        assert RecommendationAction.REORDER == "REORDER"
        assert RecommendationAction.REDUCE_EXCESS == "REDUCE EXCESS"
        assert RecommendationAction.MONITOR_PREPARE == "MONITOR / PREPARE"
        assert RecommendationAction.NO_ACTION == "NO ACTION"
        assert RecommendationAction.UNAVAILABLE == "UNAVAILABLE"

    def test_priority_order_is_stockout_first(self):
        """REORDER must outrank EXCESS and MONITOR."""
        assert RecommendationPriority.REORDER < RecommendationPriority.REDUCE_EXCESS
        assert RecommendationPriority.REDUCE_EXCESS < RecommendationPriority.MONITOR_PREPARE
        assert RecommendationPriority.MONITOR_PREPARE < RecommendationPriority.NO_ACTION

    def test_unavailable_is_lowest_priority(self):
        assert RecommendationPriority.UNAVAILABLE.value == 0

    def test_recommendation_result_with_evidence(self):
        rec = RecommendationResult(
            product_id="coke-330",
            product_name="Coca-Cola 330ml",
            action=RecommendationAction.REORDER,
            priority=RecommendationPriority.REORDER,
            reorder_quantity=24,
            reorder_timing="within 2 days",
            evidence=["Stock runs out before next shipment arrives."],
        )
        assert rec.reorder_quantity == 24
        assert rec.is_actionable() is True


class TestAIContextContract:
    def test_ai_context_mirrors_verified_values(self):
        context = AIProductContext(
            product_id="coke-330",
            product_name="Coca-Cola 330ml",
            current_stock=15,
            recommendation_action=RecommendationAction.REORDER,
            recommended_reorder_quantity=24,
            evidence=["Low stock."],
        )
        assert context.recommended_reorder_quantity == 24
        assert context.current_stock == 15

    def test_business_brief_context_can_be_constructed(self):
        ctx = AIBusinessBriefContext(
            generated_at=datetime.now(),
            items_needing_attention=3,
            healthy_items=10,
        )
        assert ctx.items_needing_attention == 3


class TestAPIResponseContracts:
    def test_dashboard_response(self):
        response = DashboardResponse(
            generated_at=datetime.now(),
            summary={
                "items_needing_attention": 2,
                "healthy_items": 5,
                "top_priorities": [],
            },
            ai_brief_context=AIBusinessBriefContext(generated_at=datetime.now()),
        )
        assert response.summary.items_needing_attention == 2

    def test_product_list_item_status(self):
        item = ProductListItem(
            product_id="coke-330",
            product_name="Coca-Cola 330ml",
            current_stock=None,
            status=RecommendationAction.UNAVAILABLE,
        )
        assert item.days_remaining is None
        assert item.status == RecommendationAction.UNAVAILABLE

    def test_product_detail_response(self):
        response = ProductDetailResponse(
            product_id="coke-330",
            analytics=ProductAnalytics(
                product_id="coke-330",
                product_name="Coca-Cola 330ml",
                demand=DemandMetrics(),
                inventory=InventoryMetrics(),
                shipment=ShipmentProjection(),
                financial=FinancialMetrics(),
            ),
            recommendation=RecommendationResult(
                product_id="coke-330",
                product_name="Coca-Cola 330ml",
            ),
            ai_context={
                "generated_at": datetime.now(),
                "product": {
                    "product_id": "coke-330",
                    "product_name": "Coca-Cola 330ml",
                },
            },
        )
        assert response.recommendation.action == RecommendationAction.UNAVAILABLE

    def test_api_error_envelope(self):
        error = ApiError(error="validation_error", message="Missing required column")
        assert error.error == "validation_error"

    def test_settings_response_defaults(self):
        settings = SettingsResponse()
        assert settings.sheets_connected is False
        assert settings.business_name is None
        assert settings.business_type is None
        assert settings.currency is None
        assert settings.timezone is None

    def test_ai_unavailable_fallback(self):
        ai = AIExplanationResponse(
            summary="AI is currently unavailable.",
            ai_available=False,
        )
        assert ai.ai_available is False
