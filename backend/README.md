> InventoryIQ backend (FastAPI)

## Setup

```
py -V:3.14 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

## Run

```
.venv\Scripts\uvicorn main:app --reload --port 8000
```

Health check: http://localhost:8000/health

## Environment

Copy `.env.example` to `.env` and fill in:

| Variable | Purpose |
|---|---|
| `GOOGLE_SHEET_ID` | ID of the InventoryIQ spreadsheet (from its URL) |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Path to the Google service-account JSON key file |

`.env` and service-account JSON files are gitignored. Never commit credentials.

To connect a real sheet:
1. Create a Google Cloud service account and download its JSON key.
2. Share the spreadsheet with the service-account email (Viewer is enough
   for Phase 2 reads).
3. Set the two variables above and run the backend.

## Google Sheets structure

The workbook must contain exactly these sheets (first row = headers):

- `Products`: product_id, product_name, category, unit, unit_cost,
  selling_price, supplier, lead_time_days, target_stock_days
- `Sales`: date, product_id, quantity_sold
- `Inventory`: date, product_id, quantity_on_hand
- `Shipments`: shipment_id, product_id, quantity, expected_arrival

Blank cells are read as empty strings and are never converted to zeros.
Inventory and shipments are always read separately.

## Data access

`app.data_access.sheets.read_sheets()` returns raw, header-mapped rows:

```python
{
    "Products": [{"product_id": "coke-330", ...}, ...],
    "Sales": [...],
    "Inventory": [...],
    "Shipments": [...],
}
```

No validation, typing, or business calculations happen here; that is Phase 3.

## Tests

```
.venv\Scripts\python -m pytest -q
```

Data-access tests use a fake spreadsheet and need no real credentials.
