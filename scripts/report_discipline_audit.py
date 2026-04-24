#!/usr/bin/env python3
"""Report discipline harmonization issues for researcher profiles.

This is a read-only audit. It enforces the current convention:
- disciplines are ordered, with the first as primary;
- profiles should have one primary plus at most two secondary disciplines;
- broad discipline names should not also appear as keywords.
"""

from __future__ import annotations

import collections
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"


def main() -> None:
    researchers = json.loads(DATA_PATH.read_text())

    discipline_counts = collections.Counter(
        len(researcher.get("disciplines") or []) for researcher in researchers
    )
    discipline_frequencies = collections.Counter(
        discipline
        for researcher in researchers
        for discipline in (researcher.get("disciplines") or [])
    )
    primary_frequencies = collections.Counter(
        (researcher.get("disciplines") or [""])[0] for researcher in researchers
    )
    discipline_terms = {
        discipline.lower()
        for researcher in researchers
        for discipline in (researcher.get("disciplines") or [])
    }

    print("Disciplines per profile:")
    for count, total in sorted(discipline_counts.items()):
        print(f"  {count}: {total}")

    print("\nDiscipline frequencies:")
    for discipline, total in discipline_frequencies.most_common():
        print(f"  {total:3}  {discipline}")

    print("\nPrimary discipline frequencies:")
    for discipline, total in primary_frequencies.most_common():
        print(f"  {total:3}  {discipline}")

    missing_or_over_cap = [
        researcher
        for researcher in researchers
        if len(researcher.get("disciplines") or []) == 0
        or len(researcher.get("disciplines") or []) > 3
    ]
    print("\nProfiles with 0 or >3 disciplines:")
    if missing_or_over_cap:
        for researcher in missing_or_over_cap:
            print(
                f"  {researcher['id']}: {researcher['name']} "
                f"{researcher.get('disciplines') or []}"
            )
    else:
        print("  none")

    discipline_keywords = []
    for researcher in researchers:
        hits = [
            keyword
            for keyword in (researcher.get("keywords") or [])
            if keyword.lower() in discipline_terms
        ]
        if hits:
            discipline_keywords.append((researcher, hits))

    print("\nBroad discipline names still used as keywords:")
    if discipline_keywords:
        for researcher, hits in discipline_keywords:
            print(
                f"  {researcher['id']}: {researcher['name']} | "
                f"disciplines={researcher.get('disciplines') or []} | keywords={hits}"
            )
    else:
        print("  none")


if __name__ == "__main__":
    main()
