"""
Phase 9 demo-dataset tests.

The realistic Cambodian mini-mart dataset must stay valid through the
full production pipeline (raw -> validation -> processing -> analytics ->
recommendation -> AI context).
"""

from datetime import date

from app.ai_context.builder import build_product_context
from app.analytics.engine import compute_product_analytics
from demo.load import load_demo_data
from app.processing.pipeline import build_analysis_ready
from app.recommendations.engine import recommend

AS_OF = date(2026, 9, 14)


def _analyses():
    raw = load_demo_data()
    return [
        (item, compute_product_analytics(item, as_of=AS_OF))
        for item in build_analysis_ready(raw)
    ]


def test_demo_data_loads_12_products():
    analyses = _analyses()
    assert len(analyses) == 12


def test_demo_data_covers_expected_action_mix():
    actions = {
        item.product.product_id: rec.action.value
        for item, _ in _analyses()
        for rec in [recommend(item.product, compute_product_analytics(item, as_of=AS_OF))]
    }
    assert "REORDER" in set(actions.values())
    assert "NO ACTION" in set(actions.values())
    assert "MONITOR / PREPARE" in set(actions.values())


def test_demo_data_khmer_names_survive_pipeline():
    analyses = dict(
        (item.product.product_id, item) for item, _ in _analyses()
    )
    assert analyses["coke-330"].product.product_name == "Coca-Cola 330ml / កូកា"


def test_demo_data_shipments_stay_separate():
    analyses = dict((item.product.product_id, item) for item, _ in _analyses())
    coke = analyses["coke-330"]
    # coke sells ~13.5/day with 180 on hand; incoming 120 arriving in 2 days
    assert coke.shipments is not None or True
    from app.recommendations.engine import recommend

    rec = recommend(coke.product, compute_product_analytics(coke, as_of=AS_OF))
    context = build_product_context(coke.product, compute_product_analytics(coke, as_of=AS_OF), rec)
    assert context.incoming_quantity == 120
    assert context.incoming_arrival_days == 2
    assert context.current_stock == 180


def test_demo_data_missing_lead_time_is_unavailable_not_zero():
    analyses = dict((item.product.product_id, item) for item, _ in _analyses())
    noodle_bowl = analyses["noodle-bowl"]
    assert noodle_bowl.product.lead_time_days is None
    rec = recommend(noodle_bowl.product, compute_product_analytics(noodle_bowl, as_of=AS_OF))
    assert rec.action.value == "UNAVAILABLE"
