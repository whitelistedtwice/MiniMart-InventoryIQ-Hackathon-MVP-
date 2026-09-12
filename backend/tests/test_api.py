"""
Lightweight API contract checks.

These prove the FastAPI app starts and that the placeholder routes return
the documented response shapes.
"""

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_contract():
    response = client.get("/api/v1/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert "ai_brief_context" in body
    assert isinstance(body["summary"]["top_priorities"], list)


def test_inventory_list_contract():
    response = client.get("/api/v1/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_product_detail_contract():
    response = client.get("/api/v1/inventory/coke-330")
    assert response.status_code == 200
    body = response.json()
    assert body["product_id"] == "coke-330"
    assert "analytics" in body
    assert "recommendation" in body
    assert "ai_context" in body


def test_analytics_contract():
    response = client.get("/api/v1/analytics")
    assert response.status_code == 200
    body = response.json()
    assert "products" in body
    assert "ai_insight_context" in body


def test_settings_contract():
    response = client.get("/api/v1/settings")
    assert response.status_code == 200
    assert "sheets_connected" in response.json()


def test_ai_fallback_contract():
    response = client.get("/api/v1/ai/business-brief")
    assert response.status_code == 200
    body = response.json()
    assert body["ai_available"] is False
    assert "summary" in body
