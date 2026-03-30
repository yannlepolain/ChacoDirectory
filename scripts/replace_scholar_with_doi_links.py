#!/usr/bin/env python3
"""
Replace Google Scholar fallback URLs with DOI landing pages when a DOI exists.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"
SCHOLAR_PREFIX = "https://scholar.google.com/scholar?q="


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    updated = 0

    for researcher in researchers:
        for publication in researcher.get("publications", []):
            url = publication.get("url", "")
            doi = publication.get("doi", "")
            if isinstance(url, str) and url.startswith(SCHOLAR_PREFIX) and doi:
                publication["url"] = f"https://doi.org/{doi}"
                updated += 1

    DATA_PATH.write_text(
        json.dumps(researchers, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Replaced {updated} Scholar fallback URLs with DOI landing pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
