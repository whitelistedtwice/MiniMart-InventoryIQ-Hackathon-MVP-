"""
Canonical business-scenario fixtures (Phase 3).

Raw sheet data shaped exactly like `read_sheets()` output, reusable by
analytics (Phase 4), recommendations (Phase 5), and E2E tests.

Each fixture documents its inputs and expected high-level outcome.
Dates are fixed so scenarios stay deterministic.
"""

from typing import Any

D0 = "2026-09-01"  # first sales day


def _sales_row(day: int, product_id: str, qty: int) -> dict[str, Any]:
    return {"date": f"2026-09-{day:02d}", "product_id": product_id, "quantity_sold": qty}


def _inventory_row(day: int, product_id: str, qty: int) -> dict[str, Any]:
    return {"date": f"2026-09-{day:02d}", "product_id": product_id, "quantity_on_hand": qty}


def _product(product_id: str, name: str, category: str, **overrides: Any) -> dict[str, Any]:
    row = {
        "product_id": product_id,
        "product_name": name,
        "category": category,
        "unit": "unit",
        "unit_cost": "0.50",
        "selling_price": "0.75",
        "supplier": "Supplier A",
        "lead_time_days": "3",
        "target_stock_days": "14",
    }
    row.update(overrides)
    return row


def _sheets(products: list[dict[str, Any]], sales: list[dict[str, Any]],
            inventory: list[dict[str, Any]], shipments: list[dict[str, Any]] | None = None
            ) -> dict[str, list[dict[str, Any]]]:
    return {
        "Products": products,
        "Sales": sales,
        "Inventory": inventory,
        "Shipments": shipments or [],
    }


def healthy() -> dict[str, list[dict[str, Any]]]:
    """Steady 5/day demand, 70 units on hand (~14 days cover).

    Expected: healthy product, no action needed.
    """
    product = _product("healthy-1", "Coca-Cola 330ml / កូកា", "Beverages")
    sales = [_sales_row(day, "healthy-1", 5) for day in range(1, 15)]
    inventory = [_inventory_row(14, "healthy-1", 70)]
    return _sheets([product], sales, inventory)


def immediate_stockout() -> dict[str, list[dict[str, Any]]]:
    """10/day demand, only 5 units on hand, lead time 3 days, no shipment.

    Expected: stockout within ~1 day, well before a reorder could arrive.
    """
    product = _product("stockout-1", "Instant Noodles", "Instant Noodles")
    sales = [_sales_row(day, "stockout-1", 10) for day in range(1, 15)]
    inventory = [_inventory_row(14, "stockout-1", 5)]
    return _sheets([product], sales, inventory)


def shipment_before_stockout() -> dict[str, list[dict[str, Any]]]:
    """8/day demand, 24 units (~3 days), shipment of 50 arriving in 2 days.

    Expected: shipment covers the gap before stock runs out.
    """
    product = _product("arrival-ok-1", "Pepsi 330ml", "Beverages")
    sales = [_sales_row(day, "arrival-ok-1", 8) for day in range(1, 15)]
    inventory = [_inventory_row(14, "arrival-ok-1", 24)]
    shipments = [
        {
            "shipment_id": "sh-before-1",
            "product_id": "arrival-ok-1",
            "quantity": "50",
            "expected_arrival": "2026-09-16",  # 2 days after last inventory date
        }
    ]
    return _sheets([product], sales, inventory, shipments)


def shipment_after_stockout() -> dict[str, list[dict[str, Any]]]:
    """8/day demand, 24 units (~3 days), shipment arriving in 5 days.

    Expected: stock runs out ~2 days before the shipment arrives.
    """
    product = _product("arrival-late-1", "ABC Soy Milk", "Beverages")
    sales = [_sales_row(day, "arrival-late-1", 8) for day in range(1, 15)]
    inventory = [_inventory_row(14, "arrival-late-1", 24)]
    shipments = [
        {
            "shipment_id": "sh-after-1",
            "product_id": "arrival-late-1",
            "quantity": "50",
            "expected_arrival": "2026-09-19",  # 5 days after last inventory date
        }
    ]
    return _sheets([product], sales, inventory, shipments)


def excess_slow_moving() -> dict[str, list[dict[str, Any]]]:
    """1/day demand, 100 units on hand against a 14-day target.

    Expected: excess stock, cash tied up.
    """
    product = _product("excess-1", "Canned Sardines", "Canned Goods", target_stock_days="14")
    sales = [_sales_row(day, "excess-1", 1) for day in range(1, 15)]
    inventory = [_inventory_row(14, "excess-1", 100)]
    return _sheets([product], sales, inventory)


def increasing_demand() -> dict[str, list[dict[str, Any]]]:
    """Demand ramps 2/day -> 8/day over two weeks; moderate stock.

    Expected: increasing trend; consider preparing more stock.
    """
    product = _product("trend-up-1", "Milk 1L", "Dairy")
    sales = [_sales_row(day, "trend-up-1", 2 if day <= 7 else 8) for day in range(1, 15)]
    inventory = [_inventory_row(14, "trend-up-1", 40)]
    return _sheets([product], sales, inventory)


ALL_SCENARIOS = {
    "healthy": healthy,
    "immediate_stockout": immediate_stockout,
    "shipment_before_stockout": shipment_before_stockout,
    "shipment_after_stockout": shipment_after_stockout,
    "excess_slow_moving": excess_slow_moving,
    "increasing_demand": increasing_demand,
}
