#!/usr/bin/env python3
"""
Helpers for loading and applying the geographic-focus taxonomy config.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GEO_TAXONOMY_PATH = ROOT / "config" / "geo_taxonomy.json"


def load_geo_taxonomy() -> dict:
    if not GEO_TAXONOMY_PATH.exists():
        return {"aliases": {}}
    with GEO_TAXONOMY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def normalize_geographies(geographies: list[str], taxonomy: dict) -> list[str]:
    aliases = taxonomy.get("aliases", {})

    normalized: list[str] = []
    seen: set[str] = set()

    for geography in geographies:
        cleaned = geography.strip()
        canonical = aliases.get(cleaned, cleaned)
        if canonical not in seen:
            normalized.append(canonical)
            seen.add(canonical)

    return normalized
