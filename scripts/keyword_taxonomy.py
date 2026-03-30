#!/usr/bin/env python3
"""
Helpers for loading and applying the keyword taxonomy config.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEYWORD_TAXONOMY_PATH = ROOT / "config" / "keyword_taxonomy.json"


def load_keyword_taxonomy() -> dict:
    if not KEYWORD_TAXONOMY_PATH.exists():
        return {"aliases": {}, "blocked_keywords": {}, "candidate_removals": []}
    with KEYWORD_TAXONOMY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def normalize_keyword(keyword: str, aliases: dict[str, str]) -> str:
    normalized = keyword.strip()
    return aliases.get(normalized, normalized)


def normalize_keywords(
    keywords: list[str],
    taxonomy: dict,
    *,
    drop_blocked: bool = True,
) -> list[str]:
    aliases = taxonomy.get("aliases", {})
    blocked = taxonomy.get("blocked_keywords", {})

    normalized: list[str] = []
    seen: set[str] = set()

    for keyword in keywords:
        cleaned = normalize_keyword(keyword, aliases)
        if drop_blocked and cleaned in blocked:
            continue
        if cleaned not in seen:
            normalized.append(cleaned)
            seen.add(cleaned)

    return normalized
