"""
Data-access tests (Phase 2).

These use a fake spreadsheet object patched over `_open_spreadsheet`, so
they never touch a real Google account or credentials.
"""

import json

import pytest
import gspread

from app.data_access import sheets
from app.core.errors import DataAccessError


class FakeWorksheet:
    def __init__(self, records, fail=False):
        self._records = records
        self._fail = fail

    def get_all_records(self):
        if self._fail:
            raise RuntimeError("boom")
        return self._records


class FakeSpreadsheet:
    def __init__(self, worksheets):
        self._worksheets = worksheets

    def worksheet(self, name):
        try:
            return self._worksheets[name]
        except KeyError:
            raise gspread.WorksheetNotFound(name)


def sample_sheets():
    return {
        "Products": [
            {
                "product_id": "coke-330",
                "product_name": "Coca-Cola 330ml",
                "category": "Beverages",
                "unit": "can",
                "unit_cost": "0.50",
                "selling_price": "0.75",
                "supplier": "Coke Distributor",
                "lead_time_days": "3",
                "target_stock_days": "14",
            },
            {
                "product_id": "indomie",
                "product_name": "Indomie Chicken",
                "category": "Instant Noodles",
                "unit": "pack",
                "unit_cost": "",
                "selling_price": "0.60",
                "supplier": "",
                "lead_time_days": "",
                "target_stock_days": "21",
            },
        ],
        "Sales": [
            {"date": "2026-09-01", "product_id": "coke-330", "quantity_sold": "8"},
            {"date": "2026-09-02", "product_id": "coke-330", "quantity_sold": "6"},
            {"date": "2026-09-01", "product_id": "indomie", "quantity_sold": "2"},
        ],
        "Inventory": [
            {"date": "2026-09-10", "product_id": "coke-330", "quantity_on_hand": "15"},
        ],
        "Shipments": [
            {
                "shipment_id": "sh-1",
                "product_id": "coke-330",
                "quantity": "50",
                "expected_arrival": "2026-09-15",
            },
        ],
    }


@pytest.fixture
def fake_spreadsheet(monkeypatch):
    spreadsheet = FakeSpreadsheet(
        {name: FakeWorksheet(records) for name, records in sample_sheets().items()}
    )
    monkeypatch.setattr(sheets, "_open_spreadsheet", lambda: spreadsheet)
    return spreadsheet


def test_reads_all_four_sheets(fake_spreadsheet):
    raw = sheets.read_sheets()
    assert list(raw) == ["Products", "Sales", "Inventory", "Shipments"]
    assert len(raw["Products"]) == 2


def test_headers_map_to_dict_keys(fake_spreadsheet):
    raw = sheets.read_sheets()
    product = raw["Products"][0]
    assert product["product_id"] == "coke-330"
    assert product["product_name"] == "Coca-Cola 330ml"


def test_multiple_rows_are_preserved(fake_spreadsheet):
    raw = sheets.read_sheets()
    assert len(raw["Sales"]) == 3


def test_empty_sheet_returns_empty_list(monkeypatch):
    spreadsheet = FakeSpreadsheet(
        {
            "Products": FakeWorksheet([]),
            "Sales": FakeWorksheet([]),
            "Inventory": FakeWorksheet([]),
            "Shipments": FakeWorksheet([]),
        }
    )
    monkeypatch.setattr(sheets, "_open_spreadsheet", lambda: spreadsheet)
    raw = sheets.read_sheets()
    assert raw == {"Products": [], "Sales": [], "Inventory": [], "Shipments": []}


def test_missing_sheet_raises_clear_error(monkeypatch):
    spreadsheet = FakeSpreadsheet(
        {
            "Products": FakeWorksheet([]),
            "Sales": FakeWorksheet([]),
            "Inventory": FakeWorksheet([]),
        }
    )
    monkeypatch.setattr(sheets, "_open_spreadsheet", lambda: spreadsheet)
    with pytest.raises(DataAccessError, match="Missing required sheet: Shipments"):
        sheets.read_sheets()


def test_read_failure_raises_clear_error(monkeypatch):
    spreadsheet = FakeSpreadsheet(
        {
            "Products": FakeWorksheet([], fail=True),
            "Sales": FakeWorksheet([]),
            "Inventory": FakeWorksheet([]),
            "Shipments": FakeWorksheet([]),
        }
    )
    monkeypatch.setattr(sheets, "_open_spreadsheet", lambda: spreadsheet)
    with pytest.raises(DataAccessError, match="Could not read sheet 'Products'"):
        sheets.read_sheets()


def test_missing_sheet_id_raises_clear_error(monkeypatch):
    monkeypatch.delenv("GOOGLE_SHEET_ID", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)
    with pytest.raises(DataAccessError, match="GOOGLE_SHEET_ID is not set"):
        sheets._open_spreadsheet()


def test_missing_credentials_env_raises_clear_error(monkeypatch):
    monkeypatch.setenv("GOOGLE_SHEET_ID", "abc123")
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)
    with pytest.raises(
        DataAccessError,
        match="Neither GOOGLE_SERVICE_ACCOUNT_JSON nor GOOGLE_SERVICE_ACCOUNT_FILE is set",
    ):
        sheets._open_spreadsheet()


def test_bad_credentials_path_raises_clear_error(monkeypatch):
    monkeypatch.setenv("GOOGLE_SHEET_ID", "abc123")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", "does-not-exist.json")
    with pytest.raises(DataAccessError, match="Could not open Google Sheet"):
        sheets._open_spreadsheet()


def test_blank_cells_are_not_fabricated(fake_spreadsheet):
    raw = sheets.read_sheets()
    indomie = raw["Products"][1]
    assert indomie["unit_cost"] == ""
    assert indomie["lead_time_days"] == ""
    assert indomie["unit_cost"] != 0


def test_inventory_and_shipments_stay_separate(fake_spreadsheet):
    raw = sheets.read_sheets()
    assert raw["Inventory"][0]["quantity_on_hand"] == "15"
    assert raw["Shipments"][0]["quantity"] == "50"
    assert "Shipments" not in raw["Inventory"]


# --------------------------------------------------------- Phase 16 deployment

@pytest.fixture(autouse=True)
def _clear_sheets_connection_cache():
    yield
    sheets._connection_cache.clear()


def test_demo_mode_loads_demo_dataset(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.delenv("GOOGLE_SHEET_ID", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)
    raw = sheets.read_sheets()
    assert "Products" in raw
    assert "Sales" in raw
    assert "Inventory" in raw
    assert "Shipments" in raw
    assert any(p["product_id"] == "coke-330" for p in raw["Products"])


def test_open_spreadsheet_uses_service_account_json_env(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-id")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_JSON", '{"client_email": "x"}')
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)

    from_dict_calls = []

    class FakeClient:
        def open_by_key(self, key):
            self._key = key
            return self

    def fake_from_dict(info):
        from_dict_calls.append(info)
        return FakeClient()

    monkeypatch.setattr(sheets.gspread, "service_account_from_dict", fake_from_dict)
    result = sheets._open_spreadsheet()
    assert from_dict_calls == [{"client_email": "x"}]
    assert result is not None


def test_open_spreadsheet_falls_back_to_service_account_file(monkeypatch, tmp_path):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-id")
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)
    creds_file = tmp_path / "creds.json"
    creds_file.write_text(json.dumps({"client_email": "x"}))
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(creds_file))

    file_calls = []

    class FakeClient:
        def open_by_key(self, key):
            self._key = key
            return self

    def fake_service_account(filename):
        file_calls.append(filename)
        return FakeClient()

    monkeypatch.setattr(sheets.gspread, "service_account", fake_service_account)
    result = sheets._open_spreadsheet()
    assert str(creds_file) in file_calls
    assert result is not None


def test_connection_state_not_configured(monkeypatch):
    monkeypatch.delenv("GOOGLE_SHEET_ID", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_FILE", raising=False)
    monkeypatch.delenv("GOOGLE_SERVICE_ACCOUNT_JSON", raising=False)
    state = sheets.get_sheets_connection_state()
    assert state["state"] == "not_configured"
    assert state["error"] is None
    assert state["last_checked"] is None


def test_connection_state_connected(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-id")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", "creds.json")
    monkeypatch.setattr(sheets, "_probe_connection", lambda **kwargs: (True, None))
    state = sheets.get_sheets_connection_state(force=True)
    assert state["state"] == "connected"
    assert state["error"] is None
    assert state["last_checked"] is not None


def test_connection_state_error(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-id")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", "creds.json")
    monkeypatch.setattr(
        sheets, "_probe_connection", lambda **kwargs: (False, "bad creds")
    )
    state = sheets.get_sheets_connection_state(force=True)
    assert state["state"] == "error"
    assert state["error"] == "bad creds"


def test_connection_state_configured_on_timeout(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-id")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", "creds.json")
    monkeypatch.setattr(
        sheets,
        "_probe_connection",
        lambda **kwargs: (False, "probe timed out after 3s"),
    )
    state = sheets.get_sheets_connection_state(force=True)
    assert state["state"] == "configured"


def test_connection_state_cache_avoids_repeated_probes(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-id")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", "creds.json")
    calls = []
    monkeypatch.setattr(
        sheets,
        "_probe_connection",
        lambda **kwargs: (calls.append(1) or (True, None)),
    )
    sheets.get_sheets_connection_state(force=True)
    sheets.get_sheets_connection_state()
    assert len(calls) == 1


def test_connection_state_force_bypasses_cache(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet-id")
    monkeypatch.setenv("GOOGLE_SERVICE_ACCOUNT_FILE", "creds.json")
    calls = []
    monkeypatch.setattr(
        sheets,
        "_probe_connection",
        lambda **kwargs: (calls.append(1) or (True, None)),
    )
    sheets.get_sheets_connection_state(force=True)
    sheets.get_sheets_connection_state(force=True)
    assert len(calls) == 2
