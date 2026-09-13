"""
Validation layer (Phase 3).

Turns raw sheet rows (from Phase 2) into typed contracts, applying a
fail-fast policy: ALL problems are collected and reported in one
ValidationError — nothing is silently dropped, defaulted, or fabricated.

Policies (documented, deliberate):
- Blank cell in an optional field  -> None ("unavailable", never 0).
- Blank cell in a required field   -> validation problem.
- Invalid date/number/negative     -> validation problem (contracts enforce
  type coercion and ge=0/gt=0 bounds).
- Duplicate product_id, duplicate product/date sale or inventory record,
  duplicate shipment_id            -> validation problem (never merged).
- Unknown product_id referenced by sales/inventory/shipments -> problem.
- Unknown extra sheets are ignored.
- An empty sheet is valid (no rows = no data, which is different from zero).
"""

from typing import Any

from pydantic import BaseModel, ValidationError as PydanticValidationError

from app.contracts.data import InventorySnapshot, Product, Sale, Shipment
from app.core.errors import ValidationError

REQUIRED_COLUMNS: dict[str, tuple[str, ...]] = {
    "Products": (
        "product_id",
        "product_name",
        "category",
        "unit",
        "unit_cost",
        "selling_price",
        "supplier",
        "lead_time_days",
        "target_stock_days",
    ),
    "Sales": ("date", "product_id", "quantity_sold"),
    "Inventory": ("date", "product_id", "quantity_on_hand"),
    "Shipments": ("shipment_id", "product_id", "quantity", "expected_arrival"),
}

# Fields where a blank cell legitimately means "unavailable" -> None.
OPTIONAL_FIELDS: dict[str, tuple[str, ...]] = {
    "Products": (
        "category",
        "unit",
        "unit_cost",
        "selling_price",
        "supplier",
        "lead_time_days",
        "target_stock_days",
    ),
    "Sales": (),
    "Inventory": (),
    "Shipments": (),
}

SHEET_MODELS: dict[str, type[BaseModel]] = {
    "Products": Product,
    "Sales": Sale,
    "Inventory": InventorySnapshot,
    "Shipments": Shipment,
}


def validate_sheets(
    raw: dict[str, list[dict[str, Any]]],
) -> tuple[list[Product], list[Sale], list[InventorySnapshot], list[Shipment]]:
    """
    Validate raw sheet data and return typed source records.

    Raises ValidationError whose `details["problems"]` lists every issue.
    """
    problems: list[dict[str, Any]] = _check_sheets(raw)
    parsed = _parse_rows(raw, problems)
    _check_duplicates(parsed, problems)
    _check_references(parsed, problems)

    if problems:
        raise ValidationError("Invalid source data", details={"problems": problems})

    return (
        parsed["Products"],
        parsed["Sales"],
        parsed["Inventory"],
        parsed["Shipments"],
    )


def _check_sheets(raw: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    problems: list[dict[str, Any]] = []
    for sheet in REQUIRED_COLUMNS:
        if sheet not in raw:
            problems.append({"sheet": sheet, "problem": "missing required sheet"})
            continue
        rows = raw[sheet]
        # Column presence can only be checked when the sheet has rows.
        if rows:
            for column in REQUIRED_COLUMNS[sheet]:
                if column not in rows[0]:
                    problems.append(
                        {"sheet": sheet, "problem": f"missing required column: {column}"}
                    )
    return problems


def _parse_rows(
    raw: dict[str, list[dict[str, Any]]],
    problems: list[dict[str, Any]],
) -> dict[str, list[BaseModel]]:
    parsed: dict[str, list[BaseModel]] = {name: [] for name in SHEET_MODELS}

    for sheet, model in SHEET_MODELS.items():
        if sheet not in raw:
            continue  # already reported by _check_sheets
        optional = OPTIONAL_FIELDS[sheet]
        required = [c for c in REQUIRED_COLUMNS[sheet] if c not in optional]

        for index, row in enumerate(raw[sheet], start=2):  # +1 for header row
            clean: dict[str, Any] = {}
            for key, value in row.items():
                if isinstance(value, str):
                    value = value.strip()
                # Blank means missing for every field; optional fields keep
                # it as None (unavailable), required ones are reported below.
                clean[key] = None if value == "" else value

            blanks = [c for c in required if clean.get(c) is None]
            if blanks:
                problems.append(
                    {
                        "sheet": sheet,
                        "row": index,
                        "problem": f"missing required value: {', '.join(blanks)}",
                    }
                )
                continue

            try:
                parsed[sheet].append(model(**clean))
            except PydanticValidationError as exc:
                for error in exc.errors():
                    column = ".".join(str(loc) for loc in error.get("loc", ())) or None
                    problems.append(
                        {
                            "sheet": sheet,
                            "row": index,
                            "column": column,
                            "problem": error["msg"],
                        }
                    )
    return parsed


def _check_duplicates(
    parsed: dict[str, list[BaseModel]],
    problems: list[dict[str, Any]],
) -> None:
    seen: set[str] = set()
    for product in parsed["Products"]:
        if product.product_id in seen:
            problems.append(
                {"sheet": "Products", "problem": f"duplicate product_id: {product.product_id}"}
            )
        seen.add(product.product_id)

    seen = set()
    for sale in parsed["Sales"]:
        key = (sale.product_id, sale.date)
        if key in seen:
            problems.append(
                {"sheet": "Sales", "problem": f"duplicate sales record for {sale.product_id} on {sale.date}"}
            )
        seen.add(key)

    seen = set()
    for snapshot in parsed["Inventory"]:
        key = (snapshot.product_id, snapshot.date)
        if key in seen:
            problems.append(
                {"sheet": "Inventory", "problem": f"duplicate inventory record for {snapshot.product_id} on {snapshot.date}"}
            )
        seen.add(key)

    seen = set()
    for shipment in parsed["Shipments"]:
        if shipment.shipment_id in seen:
            problems.append(
                {"sheet": "Shipments", "problem": f"duplicate shipment_id: {shipment.shipment_id}"}
            )
        seen.add(shipment.shipment_id)


def _check_references(
    parsed: dict[str, list[BaseModel]],
    problems: list[dict[str, Any]],
) -> None:
    known = {product.product_id for product in parsed["Products"]}
    checks = (
        ("Sales", [sale.product_id for sale in parsed["Sales"]]),
        ("Inventory", [snapshot.product_id for snapshot in parsed["Inventory"]]),
        ("Shipments", [shipment.product_id for shipment in parsed["Shipments"]]),
    )
    for sheet, product_ids in checks:
        for product_id in product_ids:
            if product_id not in known:
                problems.append(
                    {"sheet": sheet, "problem": f"unknown product_id: {product_id}"}
                )
