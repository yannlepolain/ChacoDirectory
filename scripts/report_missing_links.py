#!/usr/bin/env python3
"""
Report publications that are missing both DOI and fallback URL.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    missing = []
    for researcher in researchers:
        publications = [
            publication
            for publication in researcher.get("publications", [])
            if not publication.get("doi") and not publication.get("url")
        ]
        if publications:
            missing.append((researcher["name"], publications))

    print(f"Researchers with publications missing both DOI and URL: {len(missing)}")
    print(
        "Total publications missing both DOI and URL: "
        f"{sum(len(publications) for _, publications in missing)}"
    )

    for researcher_name, publications in sorted(
        missing,
        key=lambda item: (-len(item[1]), item[0]),
    ):
        print(f"\n{researcher_name} ({len(publications)})")
        for publication in publications:
            print(f"- {publication['year']} | {publication['title']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
