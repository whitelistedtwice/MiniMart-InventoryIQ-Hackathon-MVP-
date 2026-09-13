"""
Validation + processing tests (Phase 3).

`tests.fixtures` provides the canonical business scenarios.
"""

from datetime import date
from decimal import Decimal

import pytest

from app.core.errors import ValidationError
from app.processing.pipeline import build_analysis_ready, process
from app.validation.validator import validate_sheets
from tests.fixtures import ALL_SCENARIOS, healthy, immediate_stockout


def raw_with(products=None, sales=None, inventory=None, shipments=None, base=None):
    """Base fixture with individual sheets overridden."""
    sheets = (base or healthy()).copy()
    for key, value in (
        ("Products", products),
        ("Sales", sales),
        ("Inventory", inventory),
        ("Shipments", shipments),
    ):
        if value is not None:
            sheets[key] = value
    return sheets


# --------------------------------------------------------------- happy path

def test_valid_complete_data_parses_to_typed_contracts():
    products, sales, inventory, shipments = validate_sheets(healthy())
    assert len(products) == 1
    assert products[0].product_name == "Coca-Cola 330ml / កូកា"  # Khmer preserved
    assert products[0].unit_cost is not None
    assert sales[0].date == date(2026, 9, 1)  # "2026-09-01" -> date
    assert sales[0].quantity_sold == 5  # "5" -> int


def test_numbers_and_dates_are_coerced():
    sheets = raw_with(
        products=[
            {
                "product_id": "p1",
                "product_name": "Milk",
                "category": "Dairy",
                "unit": "carton",
                "unit_cost": "12.50",
                "selling_price": "15.00",
                "supplier": "S",
                "lead_time_days": "5",
                "target_stock_days": "10",
            }
        ],
        sales=[{"date": "2026-09-12", "product_id": "p1", "quantity_sold": "3"}],
        inventory=[{"date": "2026-09-12", "product_id": "p1", "quantity_on_hand": "15"}],
    )
    products, sales, inventory, _ = validate_sheets(sheets)
    assert products[0].unit_cost == Decimal("12.50")
    assert sales[0].date == date(2026, 9, 12)
    assert inventory[0].quantity_on_hand == 15


def test_whitespace_is_trimmed():
    sheets = raw_with(
        products=[
            {
                "product_id": " p1 ",
                "product_name": "  Water 1L ",
                "category": "Beverages",
                "unit": "bottle",
                "unit_cost": "0.50",
                "selling_price": "0.75",
                "supplier": "",
                "lead_time_days": "3",
                "target_stock_days": "14",
            }
        ],
        sales=[{"date": " 2026-09-01 ", "product_id": "p1", "quantity_sold": "2"}],
        inventory=[{"date": "2026-09-01", "product_id": "p1", "quantity_on_hand": "10"}],
    )
    products, sales, _, _ = validate_sheets(sheets)
    assert products[0].product_id == "p1"
    assert products[0].product_name == "Water 1L"
    assert sales[0].date == date(2026, 9, 1)


def test_optional_blank_fields_become_none_not_zero():
    sheets = raw_with(
        products=[
            {
                "product_id": "p1",
                "product_name": "Mystery Item",
                "category": "",
                "unit": "",
                "unit_cost": "",
                "selling_price": "",
                "supplier": "",
                "lead_time_days": "",
                "target_stock_days": "",
            }
        ],
        sales=[{"date": "2026-09-01", "product_id": "p1", "quantity_sold": "2"}],
        inventory=[{"date": "2026-09-01", "product_id": "p1", "quantity_on_hand": "10"}],
    )
    products, _, _, _ = validate_sheets(sheets)
    product = products[0]
    assert product.category is None
    assert product.unit_cost is None
    assert product.lead_time_days is None
    # The distinction is preserved: unavailable, not zero.
    assert product.unit_cost != 0


# ------------------------------------------------------------ missing data

def test_missing_sheet_is_reported():
    sheets = healthy()
    del sheets["Shipments"]
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any("missing required sheet" in p["problem"] for p in excinfo.value.details["problems"])


def test_missing_column_is_reported():
    sheets = healthy()
    for row in sheets["Sales"]:
        del row["quantity_sold"]
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any("missing required column: quantity_sold" in p["problem"]
               for p in excinfo.value.details["problems"])


def test_missing_required_value_is_reported():
    sheets = raw_with(
        sales=[{"date": "2026-09-01", "product_id": "healthy-1", "quantity_sold": ""}]
    )
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any("missing required value: quantity_sold" in p["problem"]
               for p in excinfo.value.details["problems"])


def test_missing_inventory_stays_unavailable_not_zero():
    """THE non-negotiable rule: missing inventory ≠ 0."""
    sheets = healthy()
    sheets["Inventory"] = []  # no snapshot at all
    products, _, inventory, _ = validate_sheets(sheets)
    assert inventory == []
    processed = process(products, [], inventory, [])
    assert processed[0].latest_inventory() is None  # not InventorySnapshot(0)


def test_blank_inventory_cell_is_rejected_not_zeroed():
    sheets = raw_with(
        inventory=[{"date": "2026-09-14", "product_id": "healthy-1", "quantity_on_hand": ""}]
    )
    with pytest.raises(ValidationError):
        validate_sheets(sheets)  # would have become 0 in a sloppy pipeline


# ------------------------------------------------------------- invalid data

def test_invalid_date_is_reported():
    sheets = raw_with(sales=[{"date": "not-a-date", "product_id": "healthy-1", "quantity_sold": "3"}])
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any(p.get("column") == "date" for p in excinfo.value.details["problems"])


def test_invalid_number_is_reported():
    sheets = raw_with(sales=[{"date": "2026-09-01", "product_id": "healthy-1", "quantity_sold": "abc"}])
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any(p.get("column") == "quantity_sold" for p in excinfo.value.details["problems"])


@pytest.mark.parametrize(
    "overrides,column",
    [
        ({"unit_cost": "-1"}, "unit_cost"),
        ({"selling_price": "-0.75"}, "selling_price"),
        ({"lead_time_days": "-3"}, "lead_time_days"),
        ({"target_stock_days": "-14"}, "target_stock_days"),
    ],
)
def test_negative_product_values_are_rejected(overrides, column):
    sheets = raw_with(
        products=[{
            "product_id": "p1", "product_name": "X", "category": "C", "unit": "u",
            "unit_cost": "1", "selling_price": "2", "supplier": "S",
            "lead_time_days": "3", "target_stock_days": "14", **overrides,
        }],
        sales=[{"date": "2026-09-01", "product_id": "p1", "quantity_sold": "1"}],
        inventory=[{"date": "2026-09-01", "product_id": "p1", "quantity_on_hand": "1"}],
    )
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any(p.get("column") == column for p in excinfo.value.details["problems"])


def test_negative_inventory_is_rejected():
    sheets = raw_with(
        inventory=[{"date": "2026-09-01", "product_id": "healthy-1", "quantity_on_hand": "-5"}]
    )
    with pytest.raises(ValidationError):
        validate_sheets(sheets)


def test_negative_sales_and_shipment_quantities_are_rejected():
    sheets = raw_with(
        sales=[{"date": "2026-09-01", "product_id": "healthy-1", "quantity_sold": "-1"}],
        shipments=[{
            "shipment_id": "sh-1", "product_id": "healthy-1",
            "quantity": "-50", "expected_arrival": "2026-09-20",
        }],
    )
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    columns = {p.get("column") for p in excinfo.value.details["problems"]}
    assert "quantity_sold" in columns
    assert "quantity" in columns


def test_zero_demand_is_valid_not_an_error():
    sheets = raw_with(sales=[{"date": "2026-09-01", "product_id": "healthy-1", "quantity_sold": "0"}])
    _, sales, _, _ = validate_sheets(sheets)
    assert sales[0].quantity_sold == 0


def test_all_problems_reported_at_once():
    sheets = raw_with(
        sales=[{"date": "bad", "product_id": "ghost", "quantity_sold": "-1"}],
        inventory=[{"date": "2026-09-01", "product_id": "ghost", "quantity_on_hand": "-1"}],
    )
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    # bad date, unknown product_id (x2), negative quantity, negative inventory
    assert len(excinfo.value.details["problems"]) >= 3


# ---------------------------------------------------------------- duplicates

def test_duplicate_product_id_is_rejected():
    sheets = healthy()
    sheets["Products"].append(dict(sheets["Products"][0]))
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any("duplicate product_id" in p["problem"] for p in excinfo.value.details["problems"])


def test_duplicate_sales_record_for_same_product_and_date_is_rejected():
    sheets = healthy()
    sheets["Sales"].append(dict(sheets["Sales"][0]))
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any("duplicate sales record" in p["problem"] for p in excinfo.value.details["problems"])


def test_duplicate_shipment_id_is_rejected():
    sheets = shipment_fixture_with_duplicate_shipment()
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any("duplicate shipment_id" in p["problem"] for p in excinfo.value.details["problems"])


def shipment_fixture_with_duplicate_shipment():
    sheets = healthy()
    sheets["Shipments"] = [
        {"shipment_id": "sh-1", "product_id": "healthy-1", "quantity": "10", "expected_arrival": "2026-09-20"},
        {"shipment_id": "sh-1", "product_id": "healthy-1", "quantity": "20", "expected_arrival": "2026-09-21"},
    ]
    return sheets


# ----------------------------------------------------------- unknown product

def test_unknown_product_id_is_reported():
    sheets = raw_with(sales=[{"date": "2026-09-01", "product_id": "ghost", "quantity_sold": "1"}])
    with pytest.raises(ValidationError) as excinfo:
        validate_sheets(sheets)
    assert any("unknown product_id: ghost" in p["problem"]
               for p in excinfo.value.details["problems"])


# ------------------------------------------------------------- datasets

def test_empty_dataset_is_valid():
    products, sales, inventory, shipments = validate_sheets(
        {"Products": [], "Sales": [], "Inventory": [], "Shipments": []}
    )
    assert (products, sales, inventory, shipments) == ([], [], [], [])


def test_multiple_products_and_categories():
    sheets = raw_with(
        products=[
            {"product_id": "a", "product_name": "Coke", "category": "Beverages", "unit": "can",
             "unit_cost": "0.5", "selling_price": "0.75", "supplier": "S", "lead_time_days": "3",
             "target_stock_days": "14"},
            {"product_id": "b", "product_name": "Noodles", "category": "Noodles", "unit": "pack",
             "unit_cost": "0.25", "selling_price": "0.5", "supplier": "S", "lead_time_days": "5",
             "target_stock_days": "21"},
        ],
        sales=[
            {"date": "2026-09-01", "product_id": "a", "quantity_sold": "2"},
            {"date": "2026-09-01", "product_id": "b", "quantity_sold": "1"},
        ],
        inventory=[
            {"date": "2026-09-01", "product_id": "a", "quantity_on_hand": "10"},
            {"date": "2026-09-01", "product_id": "b", "quantity_on_hand": "20"},
        ],
    )
    products, sales, inventory, _ = validate_sheets(sheets)
    assert {p.category for p in products} == {"Beverages", "Noodles"}
    assert len(sales) == 2 and len(inventory) == 2


@pytest.mark.parametrize("name", ["ភេសជ្ជៈ", "Coca-Cola 330ml", "នំបុ័ង Bread"])
def test_khmer_english_mixed_names_are_preserved(name):
    sheets = raw_with(
        products=[{
            "product_id": "p1", "product_name": name, "category": "Beverages", "unit": "can",
            "unit_cost": "0.5", "selling_price": "0.75", "supplier": "S",
            "lead_time_days": "3", "target_stock_days": "14",
        }],
        sales=[{"date": "2026-09-01", "product_id": "p1", "quantity_sold": "1"}],
        inventory=[{"date": "2026-09-01", "product_id": "p1", "quantity_on_hand": "5"}],
    )
    products, _, _, _ = validate_sheets(sheets)
    assert products[0].product_name == name


# ---------------------------------------------------------------- processing

def test_process_groups_and_sorts_chronologically():
    products, sales, inventory, shipments = validate_sheets(
        raw_with(
            sales=[
                {"date": "2026-09-03", "product_id": "healthy-1", "quantity_sold": "1"},
                {"date": "2026-09-01", "product_id": "healthy-1", "quantity_sold": "2"},
            ],
            shipments=[{
                "shipment_id": "sh-2", "product_id": "healthy-1",
                "quantity": "10", "expected_arrival": "2026-09-18",
            }],
        )
    )
    # Give shipment_before a later-arriving second shipment to prove sorting.
    processed = process(products, sales, inventory, shipments)[0]
    sale_dates = [s.date for s in processed.sales]
    assert sale_dates == sorted(sale_dates)
    assert processed.shipments[0].expected_arrival == date(2026, 9, 18)
    assert processed.latest_inventory().quantity_on_hand == 70


def test_shipments_stay_separate_from_inventory_after_processing():
    products, sales, inventory, shipments = validate_sheets(shipment_after_stockout_fixture())
    processed = process(products, sales, inventory, shipments)[0]
    assert processed.inventory[0].quantity_on_hand == 24
    assert processed.shipments[0].quantity == 50
    assert processed.inventory[0].quantity_on_hand + processed.shipments[0].quantity == 74
    # The two are distinct record types on the ProcessedProduct object.
    assert processed.inventory[0] is not processed.shipments[0]


def shipment_after_stockout_fixture():
    from tests.fixtures import shipment_after_stockout
    return shipment_after_stockout()


# ---------------------------------------------------------- canonical fixtures

@pytest.mark.parametrize("scenario", list(ALL_SCENARIOS))
def test_canonical_fixtures_pass_validation_and_processing(scenario):
    """Every canonical scenario must produce clean analysis-ready data."""
    processed = build_analysis_ready(ALL_SCENARIOS[scenario]())
    assert len(processed) == 1
    assert processed[0].sales, f"{scenario} fixture must have sales"
    assert processed[0].inventory, f"{scenario} fixture must have inventory"


def test_canonical_fixtures_have_expected_shapes():
    stockout = build_analysis_ready(immediate_stockout())[0]
    assert stockout.inventory[0].quantity_on_hand == 5
    assert stockout.shipments == []  # no shipment -> stockout is unmitigated


# ------------------------------------------------------------ smoke test

def test_pipeline_smoke_raw_to_analysis_ready():
    """Integration: raw sheet rows -> validate -> process -> analysis-ready."""
    raw = healthy()
    # Simulate Phase 2 output exactly: strings, blanks, unsorted rows.
    raw["Products"][0]["unit_cost"] = " 0.50 "
    raw["Sales"].reverse()

    processed = build_analysis_ready(raw)

    assert len(processed) == 1
    product = processed[0]
    assert product.product.product_id == "healthy-1"
    assert product.product.unit_cost == Decimal("0.50")  # typed, trimmed
    assert [s.date for s in product.sales] == sorted(s.date for s in product.sales)
    assert product.latest_inventory().quantity_on_hand == 70
    assert product.shipments == []
