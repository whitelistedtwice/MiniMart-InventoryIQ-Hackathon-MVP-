"""
Data access placeholder.

Phase 2 will implement reading the four MVP Google Sheets tabs.
For now this module only defines the interface contract.
"""

from typing import Any

from app.contracts.data import InventorySnapshot, Product, Sale, Shipment


def read_sheets() -> dict[str, list[dict[str, Any]]]:
    """
    Read raw data from the configured Google Sheets document.

    Returns a mapping of tab name to a list of row dictionaries.
    """
    raise NotImplementedError("Google Sheets integration belongs to Phase 2")


def to_contracts(raw: dict[str, list[dict[str, Any]]]) -> tuple[list[Product], list[Sale], list[InventorySnapshot], list[Shipment]]:
    """Convert raw sheet rows into typed contracts."""
    raise NotImplementedError("Row parsing belongs to Phase 2")
