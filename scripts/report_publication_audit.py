#!/usr/bin/env python3
"""
Summarize publication-trust audit risk in researchers.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"

SCHOLAR_PREFIX = "https://scholar.google.com/scholar?q="


def score_publication(publication: dict) -> int:
    url = publication.get("url", "") or ""
    doi = publication.get("doi", "") or ""
    score = 0

    if not doi:
        score += 2
    if url.startswith(SCHOLAR_PREFIX):
        score += 3
    elif url.startswith("https://books.google.com/"):
        score += 2
    elif url.startswith("https://www.llibreriapublics.com/"):
        score += 2
    elif url.startswith("https://www.researchgate.net/"):
        score += 2
    elif not doi and not url:
        score += 4

    return score


def domain(url: str) -> str:
    return urlparse(url).netloc.lower() if url else ""


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    publications = [p for r in researchers for p in r.get("publications", [])]

    scholar = 0
    no_doi = 0
    risky_rows = []
    domains: dict[str, int] = {}

    for researcher in researchers:
        risk_sum = 0
        risky_count = 0
        for publication in researcher.get("publications", []):
            url = publication.get("url", "") or ""
            doi = publication.get("doi", "") or ""
            if url:
                domains[domain(url)] = domains.get(domain(url), 0) + 1
            if url.startswith(SCHOLAR_PREFIX):
                scholar += 1
            if not doi:
                no_doi += 1

            score = score_publication(publication)
            if score:
                risk_sum += score
                risky_count += 1

        if risky_count:
            risky_rows.append((risk_sum, risky_count, researcher["name"]))

    print(f"Dataset: {DATA_PATH}")
    print(f"Researchers: {len(researchers)}")
    print(f"Publications: {len(publications)}")
    print(f"Publications without DOI: {no_doi}")
    print(f"Scholar fallback URLs: {scholar}")

    print("\nTop risky profiles:")
    for score, count, name in sorted(risky_rows, reverse=True)[:20]:
        print(f"- {name}: risk_score={score}, risky_publications={count}")

    print("\nTop URL domains:")
    for dom, count in sorted(domains.items(), key=lambda item: (-item[1], item[0]))[:20]:
        print(f"- {dom}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
