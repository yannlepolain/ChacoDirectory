#!/usr/bin/env python3
"""
Report researchers who look under-covered relative to the rest of the dataset.

This is a heuristic queue generator. It does not prove that a profile is missing
publications; it surfaces candidates that deserve manual audit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-pubs", type=int, default=4, help="Maximum listed publications to include")
    parser.add_argument(
        "--require-null-seed",
        action="store_true",
        help="Only include profiles where total_publications_in_seed is null",
    )
    parser.add_argument("--limit", type=int, default=50, help="Maximum rows to print")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    rows = []
    for researcher in data:
        publications = researcher.get("publications", [])
        pub_count = len(publications)
        seed_total = researcher.get("total_publications_in_seed")

        if pub_count > args.max_pubs:
            continue
        if args.require_null_seed and seed_total is not None:
            continue

        rows.append(
            {
                "name": researcher.get("name", ""),
                "pub_count": pub_count,
                "seed_total": seed_total,
                "year_range": researcher.get("year_range", ""),
                "webpage": bool((researcher.get("webpage") or "").strip()),
            }
        )

    rows.sort(key=lambda row: (row["pub_count"], row["seed_total"] is not None, row["name"]))

    print(f"Dataset: {DATA_PATH}")
    print(f"Candidate profiles: {len(rows)}")
    print("")
    for row in rows[: max(1, args.limit)]:
        print(
            f"{row['pub_count']:>2} pubs | "
            f"seed={str(row['seed_total']):<4} | "
            f"webpage={'yes' if row['webpage'] else 'no '} | "
            f"year_range={row['year_range'] or '-'} | "
            f"{row['name']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
