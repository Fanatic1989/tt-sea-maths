import json
import os
from typing import Any, Dict

DEFAULT_SKILLMAP_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tt_primary_skillmap.json")


def load_skillmap(path: str | None = None) -> Dict[str, Any]:
    p = path or os.getenv("SKILLMAP_PATH") or DEFAULT_SKILLMAP_PATH
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)
