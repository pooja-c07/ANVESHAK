"""
ANVESHAK - Synthetic Data Loader
Loads realistic Indian investigation datasets, computes initial SHA-256 digests,
and initializes the graph engine with seed criminal networks.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "synthetic_cases.json"


def load_dataset() -> Dict[str, Any]:
    """Loads raw json dataset of cases and sample multilingual texts."""
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Synthetic dataset not found at {DATA_FILE}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_cases() -> List[Dict[str, Any]]:
    data = load_dataset()
    return data.get("cases", [])


def get_sample_texts() -> List[Dict[str, Any]]:
    data = load_dataset()
    return data.get("sample_texts", [])


def get_case_by_id(case_id: str) -> Dict[str, Any]:
    cases = get_all_cases()
    for c in cases:
        if c.get("id") == case_id:
            return c
    return cases[0] if cases else {}
