#!/usr/bin/env python3
"""
Report first-author flags that are most likely to need manual verification.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"


def risk_score(publication: dict) -> int:
    score = 0
    doi = publication.get("doi", "") or ""
    url = publication.get("url", "") or ""

    if not publication.get("is_first_author"):
        return 0

    if not doi:
        score += 2
    if url.startswith("https://scholar.google.com/scholar?q="):
        score += 3
    elif url.startswith("https://books.google.com/"):
        score += 2
    elif url.startswith("https://www.llibreriapublics.com/"):
        score += 2
    elif url.startswith("https://www.researchgate.net/"):
        score += 2
    elif not doi and not url:
        score += 4

    journal = (publication.get("journal", "") or "").lower()
    if "book" in journal or "tesis" in journal or "chapter" in journal:
        score += 2

    return score


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    risky = []

    for researcher in researchers:
        for publication in researcher.get("publications", []):
            score = risk_score(publication)
            if score:
                risky.append(
                    (
                        score,
                        researcher["name"],
                        publication["year"],
                        publication["title"],
                        publication.get("doi", ""),
                        publication.get("url", ""),
                    )
                )

    print(f"Dataset: {DATA_PATH}")
    print(f"Risky first-author claims needing review: {len(risky)}")

    for score, researcher, year, title, doi, url in sorted(risky, reverse=True)[:50]:
        print(f"- score={score} | {researcher} | {year} | {title}")
        if doi:
            print(f"  doi={doi}")
        if url:
            print(f"  url={url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
