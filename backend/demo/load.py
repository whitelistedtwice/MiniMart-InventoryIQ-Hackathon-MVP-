"""Load the realistic Cambodian demo dataset (kept separate from test fixtures)."""

import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "cambodian_mini_mart.json"


def load_demo_data() -> dict[str, list[dict[str, str]]]:
    """Return the demo dataset shaped exactly like read_sheets() output."""
    with DATA_FILE.open(encoding="utf-8") as handle:
        return json.load(handle)
