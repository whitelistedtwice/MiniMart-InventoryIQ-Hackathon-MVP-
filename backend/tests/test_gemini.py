"""
Phase 7 Gemini integration tests.

All tests use a mocked transport/``_generate``; none require a real API key.
They prove Gemini explains verified context, cannot mutate deterministic
business truth, and fails closed without breaking the pipeline.
"""

import json
from datetime import date, datetime

import httpx
import pytest

from app.ai_context.builder import (
    build_business_brief_context,
    build_insight_context,
    build_product_context,
    build_recommendation_context,
)
from app.analytics.engine import compute_product_analytics
from app.contracts.api import AIExplanationResponse
from app.contracts.recommendation import RecommendationAction
from app.core.errors import GeminiError
from app.gemini import client
from app.processing.pipeline import build_analysis_ready
from app.recommendations.engine import recommend
from tests.fixtures import (
    ALL_SCENARIOS,
    healthy,
    immediate_stockout,
    shipment_after_stockout,
)

AS_OF = date(2026, 9, 14)
GENERATED_AT = datetime(2026, 9, 14, 12, 0)

VALID = {
    "summary": "Two products need attention.",
    "reason": "Stock is low relative to the supplier lead time.",
    "action_explanation": "Reorder to cover the gap.",
    "future_note": "Review again after the next delivery.",
}


def _build(raw, as_of=AS_OF):
    processed = build_analysis_ready(raw)[0]
    analytics = compute_product_analytics(processed, as_of=as_of)
    rec = recommend(processed.product, analytics)
    ctx = build_product_context(processed.product, analytics, rec)
    return processed, analytics, rec, ctx


def _rec_context(raw):
    _, _, rec, ctx = _build(raw)
    return rec, build_recommendation_context(ctx, generated_at=GENERATED_AT)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.request = httpx.Request("POST", "https://example.test")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error", request=self.request, response=self
            )

    def json(self):
        return self._payload


def _gemini_payload(text):
    return {"candidates": [{"content": {"parts": [{"text": text}]}}]}


# ----------------------------------------------------------------- success

def test_explain_recommendation_success(monkeypatch):
    monkeypatch.setattr(client, "_generate", lambda prompt: dict(VALID))
    rec, ctx = _rec_context(immediate_stockout())
    out = client.explain_recommendation(ctx)
    assert out.ai_available is True
    assert out.summary == VALID["summary"]
    assert out.reason == VALID["reason"]
    assert out.action_explanation == VALID["action_explanation"]
    assert out.future_note == VALID["future_note"]
    assert rec.action == RecommendationAction.REORDER
    assert rec.reorder_quantity == 135  # untouched


def test_business_brief_success(monkeypatch):
    monkeypatch.setattr(client, "_generate", lambda prompt: dict(VALID))
    _, _, _, ctx = _build(healthy())
    brief = build_business_brief_context([ctx], generated_at=GENERATED_AT)
    out = client.generate_business_brief(brief)
    assert out.ai_available is True
    assert out.summary == VALID["summary"]


def test_insight_success(monkeypatch):
    monkeypatch.setattr(client, "_generate", lambda prompt: dict(VALID))
    _, _, _, ctx = _build(healthy())
    insight = build_insight_context([ctx], generated_at=GENERATED_AT)
    out = client.generate_insight(insight)
    assert out.ai_available is True
    assert out.summary == VALID["summary"]


def test_optional_fields_may_be_missing(monkeypatch):
    monkeypatch.setattr(client, "_generate", lambda prompt: {"summary": "Only summary"})
    _, ctx = _rec_context(healthy())
    out = client.explain_recommendation(ctx)
    assert out.ai_available is True
    assert out.summary == "Only summary"
    assert out.reason is None
    assert out.action_explanation is None
    assert out.future_note is None


# ----------------------------------------------------------------- failure

@pytest.mark.parametrize(
    "fake",
    [
        lambda prompt: (_ for _ in ()).throw(GeminiError("timeout")),
        lambda prompt: (_ for _ in ()).throw(GeminiError("rate limited")),
        lambda prompt: (_ for _ in ()).throw(GeminiError("auth failed")),
        lambda prompt: (_ for _ in ()).throw(ValueError("unexpected")),
        lambda prompt: {},
        lambda prompt: {"reason": "no summary"},
        lambda prompt: {"summary": "   "},
        lambda prompt: [1, 2, 3],
    ],
)
def test_failures_return_unavailable(monkeypatch, fake):
    monkeypatch.setattr(client, "_generate", fake)
    _, ctx = _rec_context(immediate_stockout())
    out = client.explain_recommendation(ctx)
    assert out == AIExplanationResponse(ai_available=False)
    assert out.summary is None


# ------------------------------------------- _generate transport handling

def test_generate_valid_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        client.httpx, "post",
        lambda *a, **k: FakeResponse(_gemini_payload(json.dumps(VALID))),
    )
    assert client._generate("prompt") == VALID


def test_generate_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    called = {"n": 0}

    def explode(*a, **k):
        called["n"] += 1
        raise AssertionError("httpx should not be called without a key")

    monkeypatch.setattr(client.httpx, "post", explode)
    with pytest.raises(GeminiError):
        client._generate("prompt")
    assert called["n"] == 0


@pytest.mark.parametrize("status", [401, 429, 500])
def test_generate_http_error(monkeypatch, status):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(client.httpx, "post", lambda *a, **k: FakeResponse({}, status))
    with pytest.raises(GeminiError) as exc:
        client._generate("prompt")
    assert exc.value.details.get("status") == status


def test_generate_timeout(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def timeout(*a, **k):
        raise httpx.TimeoutException("slow")

    monkeypatch.setattr(client.httpx, "post", timeout)
    with pytest.raises(GeminiError) as exc:
        client._generate("prompt")
    assert exc.value.details.get("reason") == "timeout"


def test_generate_connection_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def down(*a, **k):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(client.httpx, "post", down)
    with pytest.raises(GeminiError):
        client._generate("prompt")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"candidates": []},
        {"candidates": [{"content": {"parts": []}}]},
        _gemini_payload("not json"),
        _gemini_payload(""),
    ],
)
def test_generate_malformed(monkeypatch, payload):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(client.httpx, "post", lambda *a, **k: FakeResponse(payload))
    with pytest.raises(GeminiError):
        client._generate("prompt")


# ------------------------------------------------------------- safety

def test_gemini_cannot_change_reorder_quantity(monkeypatch):
    monkeypatch.setattr(
        client, "_generate",
        lambda prompt: {
            "summary": "You should order 100 units.",
            "action_explanation": "Consider ordering only 100 units.",
        },
    )
    rec, ctx = _rec_context(shipment_after_stockout())
    before = rec.model_copy(deep=True)
    out = client.explain_recommendation(ctx)
    assert rec.reorder_quantity == 38  # deterministic value preserved
    assert rec == before
    assert "100" in out.summary  # explanation kept as text, not as truth
    assert isinstance(out, AIExplanationResponse)


def test_gemini_cannot_change_action(monkeypatch):
    monkeypatch.setattr(
        client, "_generate",
        lambda prompt: {"summary": "This product is healthy, take no action."},
    )
    rec, ctx = _rec_context(immediate_stockout())
    before = rec.model_copy(deep=True)
    client.explain_recommendation(ctx)
    assert rec.action == RecommendationAction.REORDER
    assert rec == before


def test_none_is_not_sent_as_zero(monkeypatch):
    captured = {}

    def capture(prompt):
        captured["prompt"] = prompt
        return dict(VALID)

    monkeypatch.setattr(client, "_generate", capture)
    raw = healthy()
    raw["Inventory"] = []  # current_stock becomes None
    rec, ctx = _rec_context(raw)
    assert ctx.product.current_stock is None
    client.explain_recommendation(ctx)
    assert '"current_stock":null' in captured["prompt"]
    assert '"current_stock":0' not in captured["prompt"]


def test_zero_is_sent_as_zero(monkeypatch):
    captured = {}

    def capture(prompt):
        captured["prompt"] = prompt
        return dict(VALID)

    monkeypatch.setattr(client, "_generate", capture)
    raw = immediate_stockout()
    raw["Inventory"][0]["quantity_on_hand"] = 0
    _, _, _, ctx = _build(raw)
    assert ctx.current_stock == 0
    client.explain_recommendation(
        build_recommendation_context(ctx, generated_at=GENERATED_AT)
    )
    assert '"current_stock":0' in captured["prompt"]


def test_shipment_timing_sent_exactly(monkeypatch):
    captured = {}

    def capture(prompt):
        captured["p"] = prompt
        return dict(VALID)

    monkeypatch.setattr(client, "_generate", capture)
    _, ctx = _rec_context(shipment_after_stockout())
    client.explain_recommendation(ctx)
    assert '"incoming_quantity":50' in captured["p"]
    assert '"incoming_arrival_days":5' in captured["p"]
    assert '"current_stock":24' in captured["p"]


def test_khmer_name_sent_verbatim(monkeypatch):
    captured = {}

    def capture(prompt):
        captured["p"] = prompt
        return dict(VALID)

    monkeypatch.setattr(client, "_generate", capture)
    _, ctx = _rec_context(healthy())
    client.explain_recommendation(ctx)
    assert "កូកា" in captured["p"]


def test_currency_sent_in_context_and_guarded_in_instruction(monkeypatch):
    captured = {}

    def capture(prompt):
        captured["p"] = prompt
        return dict(VALID)

    monkeypatch.setattr(client, "_generate", capture)
    _, _, _, ctx = _build(healthy())
    client.explain_recommendation(
        build_recommendation_context(ctx, generated_at=GENERATED_AT, currency="KHR")
    )
    assert '"currency":"KHR"' in captured["p"]
    # The instruction forbids naming/symbolizing any other currency and
    # forbids adding one when the context does not state it.
    assert "currency" in client._SYSTEM_INSTRUCTION
    assert "Never name or symbolize any currency other than that value" in (
        client._SYSTEM_INSTRUCTION
    )


def test_currency_absent_is_explicit_null_in_prompt(monkeypatch):
    captured = {}

    def capture(prompt):
        captured["p"] = prompt
        return dict(VALID)

    monkeypatch.setattr(client, "_generate", capture)
    _, ctx = _rec_context(healthy())
    client.explain_recommendation(ctx)
    assert '"currency":null' in captured["p"]


# --------------------------------------------------------- integration

def test_full_pipeline_mocked_gemini(monkeypatch):
    monkeypatch.setattr(client, "_generate", lambda prompt: dict(VALID))
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
    processed, analytics, rec, ctx = _build(raw, as_of=date(2026, 9, 13))
    out = client.explain_recommendation(
        build_recommendation_context(ctx, generated_at=GENERATED_AT)
    )
    # deterministic truth unchanged through the AI layer
    assert rec.action == RecommendationAction.REORDER
    assert rec.reorder_quantity == 45
    assert ctx.product_name == "កាហ្វេ Coffee 3in1"
    assert out.ai_available is True
    assert out.summary == VALID["summary"]


@pytest.mark.parametrize("scenario", list(ALL_SCENARIOS))
def test_canonical_scenarios_preserve_recommendation(monkeypatch, scenario):
    monkeypatch.setattr(
        client, "_generate",
        lambda prompt: {"summary": "Explanation.", "action_explanation": "Order differently."},
    )
    rec, ctx = _rec_context(ALL_SCENARIOS[scenario]())
    before = rec.model_copy(deep=True)
    out = client.explain_recommendation(ctx)
    assert out.ai_available is True
    assert rec == before  # recommendation preserved for every scenario
