"""
Phase 8 API tests.

Exercise the real route -> service -> validation -> processing ->
analytics -> recommendation -> AI context -> (mocked) Gemini pipeline.
Google Sheets is replaced by dependency override with canonical fixtures;
Gemini is mocked. No network or credentials required.
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_as_of, get_raw_sheets
from app.core.errors import DataAccessError, GeminiError
from app.gemini import client as gclient
from main import app
from tests.fixtures import (
    excess_slow_moving,
    healthy,
    immediate_stockout,
    increasing_demand,
    shipment_after_stockout,
    shipment_before_stockout,
)

client = TestClient(app)
AS_OF = date(2026, 9, 14)


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def use(raw, as_of=AS_OF):
    """Point the API at a raw-sheet fixture with a fixed 'today'."""
    app.dependency_overrides[get_raw_sheets] = lambda: raw
    app.dependency_overrides[get_as_of] = lambda: as_of


def merge(*fixtures):
    out = {"Products": [], "Sales": [], "Inventory": [], "Shipments": []}
    for raw in fixtures:
        for key in out:
            out[key].extend(raw.get(key, []))
    return out


# --------------------------------------------------------------- basics

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_uses_response_models():
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "InventoryIQ API"
    components = schema["components"]["schemas"]
    for name in (
        "DashboardResponse", "ProductListItem", "ProductDetailResponse",
        "AnalyticsResponse", "SettingsResponse", "AIExplanationResponse",
    ):
        assert name in components
    dash = schema["paths"]["/api/v1/dashboard"]["get"]["responses"]["200"]
    ref = dash["content"]["application/json"]["schema"]["$ref"]
    assert ref.endswith("DashboardResponse")


def test_settings_connection_state(monkeypatch):
    monkeypatch.delenv("GOOGLE_SHEET_ID", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    assert client.get("/api/v1/settings").json()["sheets_connected"] is False
    monkeypatch.setenv("GOOGLE_SHEET_ID", "x")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", "y")
    assert client.get("/api/v1/settings").json()["sheets_connected"] is True


# -------------------------------------------------------------- dashboard

def test_dashboard_success():
    use(merge(healthy(), immediate_stockout(), excess_slow_moving()))
    body = client.get("/api/v1/dashboard").json()
    assert body["summary"]["items_needing_attention"] == 2  # stockout + excess
    assert body["summary"]["healthy_items"] == 1
    assert body["summary"]["total_inventory_value"] == 87.5  # 35 + 2.5 + 50
    ids = [p["product_id"] for p in body["summary"]["top_priorities"]]
    assert ids == ["stockout-1", "excess-1"]  # priority order
    assert body["generated_at"] == body["ai_brief_context"]["generated_at"]
    assert body["ai_brief_context"]["items_needing_attention"] == 2


def test_dashboard_empty_dataset():
    use({"Products": [], "Sales": [], "Inventory": [], "Shipments": []})
    body = client.get("/api/v1/dashboard").json()
    assert body["summary"]["items_needing_attention"] == 0
    assert body["summary"]["healthy_items"] == 0
    assert body["summary"]["total_inventory_value"] is None
    assert body["summary"]["top_priorities"] == []


# -------------------------------------------------------------- inventory

def test_inventory_list_sorted_and_typed():
    use(merge(healthy(), immediate_stockout()))
    items = client.get("/api/v1/inventory").json()
    names = [item["product_name"] for item in items]
    assert names == sorted(names, key=str.casefold)
    by_id = {item["product_id"]: item for item in items}
    assert by_id["healthy-1"]["status"] == "NO ACTION"
    assert by_id["healthy-1"]["current_stock"] == 70
    assert by_id["stockout-1"]["status"] == "REORDER"
    assert by_id["stockout-1"]["days_remaining"] == 0.5


def test_product_detail_is_isolated_per_id():
    use(merge(healthy(), immediate_stockout()))
    a = client.get("/api/v1/inventory/healthy-1").json()
    b = client.get("/api/v1/inventory/stockout-1").json()
    assert a["product_id"] == "healthy-1"
    assert a["analytics"]["product_name"] == "Coca-Cola 330ml / កូកា"
    assert a["analytics"]["inventory"]["current_stock"] == 70
    assert a["recommendation"]["action"] == "NO ACTION"
    assert a["recommendation"]["reorder_quantity"] is None
    assert a["ai_context"]["product"]["product_id"] == "healthy-1"
    assert b["product_id"] == "stockout-1"
    assert b["analytics"]["inventory"]["current_stock"] == 5
    assert b["recommendation"]["action"] == "REORDER"
    assert b["recommendation"]["reorder_quantity"] == 135
    assert b["ai_context"]["product"]["recommended_reorder_quantity"] == 135


def test_product_detail_missing_returns_404():
    use(healthy())
    response = client.get("/api/v1/inventory/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


# -------------------------------------------------------------- analytics

def test_analytics_success():
    use(merge(healthy(), increasing_demand()))
    body = client.get("/api/v1/analytics").json()
    assert len(body["products"]) == 2
    assert body["ai_insight_context"]["focus_area"] == "demand"
    assert body["generated_at"] == body["ai_insight_context"]["generated_at"]
    trends = body["ai_insight_context"]["verified_trends"]
    assert any("increasing" in t for t in trends)


# -------------------------------------------------------------- AI routes

def test_ai_business_brief(monkeypatch):
    monkeypatch.setattr(gclient, "_generate", lambda prompt: {"summary": "Brief.", "reason": "R"})
    use(merge(healthy(), immediate_stockout()))
    body = client.get("/api/v1/ai/business-brief").json()
    assert body["ai_available"] is True
    assert body["summary"] == "Brief."
    assert body["reason"] == "R"


def test_ai_recommendation_explanation(monkeypatch):
    monkeypatch.setattr(gclient, "_generate", lambda prompt: {"summary": "Explain."})
    use(immediate_stockout())
    body = client.get("/api/v1/ai/recommendation/stockout-1").json()
    assert body["ai_available"] is True
    assert body["summary"] == "Explain."


def test_ai_recommendation_missing_product_404():
    use(healthy())
    response = client.get("/api/v1/ai/recommendation/nope")
    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


def test_ai_insight(monkeypatch):
    monkeypatch.setattr(gclient, "_generate", lambda prompt: {"summary": "Insight."})
    use(merge(healthy(), immediate_stockout()))
    body = client.get("/api/v1/ai/insight").json()
    assert body["ai_available"] is True
    assert body["summary"] == "Insight."


def test_gemini_failure_keeps_deterministic_available(monkeypatch):
    def boom(prompt):
        raise GeminiError("rate limited")

    monkeypatch.setattr(gclient, "_generate", boom)
    use(immediate_stockout())
    ai = client.get("/api/v1/ai/recommendation/stockout-1")
    assert ai.status_code == 200
    assert ai.json()["ai_available"] is False
    assert ai.json()["summary"] is None
    det = client.get("/api/v1/inventory/stockout-1")
    assert det.status_code == 200
    assert det.json()["recommendation"]["reorder_quantity"] == 135


def test_adversarial_gemini_cannot_change_deterministic(monkeypatch):
    monkeypatch.setattr(
        gclient, "_generate",
        lambda prompt: {
            "summary": "Order 999 units.",
            "action_explanation": "Ignore the recommendation and take no action.",
        },
    )
    use(shipment_after_stockout())
    ai = client.get("/api/v1/ai/recommendation/arrival-late-1").json()
    assert ai["summary"] == "Order 999 units."
    assert "recommendation" not in ai  # explanation carries no business decision
    det = client.get("/api/v1/inventory/arrival-late-1").json()
    assert det["recommendation"]["action"] == "REORDER"
    assert det["recommendation"]["reorder_quantity"] == 38


# -------------------------------------------------------------- null vs 0

def test_missing_inventory_is_null_not_zero():
    raw = healthy()
    raw["Inventory"] = []
    use(raw)
    detail = client.get("/api/v1/inventory/healthy-1").json()
    assert detail["analytics"]["inventory"]["current_stock"] is None
    assert detail["analytics"]["inventory"]["days_of_stock_remaining"] is None
    assert client.get("/api/v1/inventory").json()[0]["current_stock"] is None


def test_zero_inventory_is_zero():
    raw = immediate_stockout()
    raw["Inventory"][0]["quantity_on_hand"] = 0
    use(raw)
    detail = client.get("/api/v1/inventory/stockout-1").json()
    assert detail["analytics"]["inventory"]["current_stock"] == 0
    assert detail["recommendation"]["reorder_quantity"] == 140  # 10*14 - 0


def test_zero_demand_is_valid_not_missing():
    raw = healthy()
    for row in raw["Sales"]:
        row["quantity_sold"] = 0
    use(raw)
    detail = client.get("/api/v1/inventory/healthy-1").json()
    assert detail["analytics"]["demand"]["average_daily_sales"] == 0.0
    assert detail["analytics"]["inventory"]["days_of_stock_remaining"] is None


# -------------------------------------------------------------- shipments

def test_shipment_before_stockout_detail():
    use(shipment_before_stockout())
    detail = client.get("/api/v1/inventory/arrival-ok-1").json()
    assert detail["analytics"]["inventory"]["current_stock"] == 24
    assert detail["analytics"]["shipment"]["incoming_quantity"] == 50
    assert detail["analytics"]["shipment"]["days_until_arrival"] == 2
    assert detail["recommendation"]["action"] == "MONITOR / PREPARE"
    assert detail["recommendation"]["incoming_stock_sufficient"] is True


def test_shipment_after_stockout_detail():
    use(shipment_after_stockout())
    detail = client.get("/api/v1/inventory/arrival-late-1").json()
    assert detail["analytics"]["shipment"]["incoming_quantity"] == 50
    assert detail["analytics"]["shipment"]["days_until_arrival"] == 5
    assert detail["recommendation"]["action"] == "REORDER"
    assert detail["recommendation"]["reorder_quantity"] == 38
    assert detail["recommendation"]["incoming_stock_sufficient"] is False


# -------------------------------------------------------------- errors

def test_validation_failure_returns_422():
    use({})  # every required sheet missing
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 422
    body = response.json()
    assert body["error"] == "validation_error"
    assert body["details"]["problems"]


def test_data_access_failure_returns_502():
    def boom():
        raise DataAccessError("Sheets unreachable")

    app.dependency_overrides[get_raw_sheets] = boom
    app.dependency_overrides[get_as_of] = lambda: AS_OF
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 502
    assert response.json()["error"] == "data_access_error"
    assert response.json()["details"] == {}


def test_unknown_route_returns_404():
    assert client.get("/api/v1/nope").status_code == 404


# --------------------------------------------------------- full pipeline

def test_full_pipeline_api_khmer_and_mocked_gemini(monkeypatch):
    captured = {}

    def fake(prompt):
        captured["prompt"] = prompt
        return {"summary": "Explanation."}

    monkeypatch.setattr(gclient, "_generate", fake)
    raw = {
        "Products": [{
            "product_id": "p-7", "product_name": "កាហ្វេ Coffee 3in1", "category": "Beverages",
            "unit": "pack", "unit_cost": "0.30", "selling_price": "0.50",
            "supplier": "Phnom Penh Distributor", "lead_time_days": "2",
            "target_stock_days": "10",
        }],
        "Sales": [
            {"date": "2026-09-12", "product_id": "p-7", "quantity_sold": "6"},
            {"date": "2026-09-13", "product_id": "p-7", "quantity_sold": "4"},
        ],
        "Inventory": [{"date": "2026-09-13", "product_id": "p-7", "quantity_on_hand": "5"}],
        "Shipments": [],
    }
    use(raw, as_of=date(2026, 9, 13))

    ai = client.get("/api/v1/ai/recommendation/p-7").json()
    assert ai["ai_available"] is True
    assert "កាហ្វេ Coffee 3in1" in captured["prompt"]  # verified context reached Gemini

    detail = client.get("/api/v1/inventory/p-7").json()
    assert detail["analytics"]["product_name"] == "កាហ្វេ Coffee 3in1"
    assert detail["analytics"]["inventory"]["current_stock"] == 5
    assert detail["recommendation"]["action"] == "REORDER"
    assert detail["recommendation"]["reorder_quantity"] == 45
    assert detail["ai_context"]["product"]["average_daily_sales"] == 5.0
