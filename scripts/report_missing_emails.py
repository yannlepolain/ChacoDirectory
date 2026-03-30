#!/usr/bin/env python3
"""
Report profiles that still lack an email address.

This is a cheap prioritization tool, not a crawler. It helps target the quick
manual pass the project now expects during intake: prefer person-specific,
institutional email addresses exposed on official profile pages, and skip rabbit
hunting when the signal is weak.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"

WEAK_DOMAINS = {
    "academia.edu",
    "independent.academia.edu",
    "scholar.google.com",
    "scholar.google.es",
    "researchgate.net",
    "thinklandscape.globallandscapesforum.org",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=50, help="Maximum rows to print")
    parser.add_argument(
        "--official-only",
        action="store_true",
        help="Only show rows with a non-empty webpage on a non-weak domain",
    )
    return parser.parse_args()


def classify_webpage(url: str) -> tuple[str, bool]:
    if not url:
        return "-", False

    host = urlparse(url).netloc.lower()
    host = host[4:] if host.startswith("www.") else host

    if any(host == domain or host.endswith(f".{domain}") for domain in WEAK_DOMAINS):
        return host, False

    return host, True


def main() -> int:
    args = parse_args()
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    rows: list[dict[str, str | bool]] = []
    for researcher in researchers:
        if (researcher.get("email") or "").strip():
            continue

        webpage = (researcher.get("webpage") or "").strip()
        domain, official = classify_webpage(webpage)
        if args.official_only and not official:
            continue

        rows.append(
            {
                "name": researcher.get("name", ""),
                "affiliation": researcher.get("affiliation", ""),
                "domain": domain,
                "official": official,
            }
        )

    rows.sort(key=lambda row: (not bool(row["official"]), str(row["domain"]), str(row["name"])))

    print(f"Dataset: {DATA_PATH}")
    print(f"Missing emails: {len(rows)}")
    print("")

    for row in rows[: max(1, args.limit)]:
        label = "official" if row["official"] else "weak/none"
        print(
            f"{label:<9} | {row['domain']:<35} | "
            f"{row['name']} | {row['affiliation']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
