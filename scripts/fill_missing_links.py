#!/usr/bin/env python3
"""
Fill missing publication fallback URLs with Google Scholar title queries.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"


def scholar_url(title: str) -> str:
    query = quote(f'"{title}"')
    return f"https://scholar.google.com/scholar?q={query}"


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    updated = 0

    for researcher in researchers:
        for publication in researcher.get("publications", []):
            if not publication.get("doi") and not publication.get("url"):
                publication["url"] = scholar_url(publication["title"])
                updated += 1

    DATA_PATH.write_text(
        json.dumps(researchers, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Filled {updated} missing fallback URLs in {DATA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
