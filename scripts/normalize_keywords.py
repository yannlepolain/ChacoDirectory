#!/usr/bin/env python3
"""
Normalize researcher keywords using the keyword taxonomy config.
"""

from __future__ import annotations

import json
from pathlib import Path

from keyword_taxonomy import load_keyword_taxonomy, normalize_keywords


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    taxonomy = load_keyword_taxonomy()

    changed = 0
    for researcher in researchers:
        raw_keywords = researcher.get("keywords", [])
        normalized = normalize_keywords(raw_keywords, taxonomy)
        if normalized != raw_keywords:
            researcher["keywords"] = normalized
            changed += 1

    DATA_PATH.write_text(
        json.dumps(researchers, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Normalized keywords for {changed} researchers in {DATA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
