#!/usr/bin/env python3
"""
Report keyword inventory, alias hits, and review candidates.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from keyword_taxonomy import load_keyword_taxonomy, normalize_keywords


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    taxonomy = load_keyword_taxonomy()
    aliases = taxonomy.get("aliases", {})
    blocked = taxonomy.get("blocked_keywords", {})
    candidate_removals = set(taxonomy.get("candidate_removals", []))

    raw_counter: Counter[str] = Counter()
    normalized_counter: Counter[str] = Counter()
    alias_counter: Counter[str] = Counter()
    blocked_counter: Counter[str] = Counter()
    candidate_counter: Counter[str] = Counter()

    for researcher in researchers:
        raw_keywords = researcher.get("keywords", [])
        raw_counter.update(raw_keywords)
        normalized_keywords = normalize_keywords(raw_keywords, taxonomy, drop_blocked=False)
        normalized_counter.update(normalized_keywords)

        for keyword in raw_keywords:
            if keyword in aliases:
                alias_counter[f"{keyword} -> {aliases[keyword]}"] += 1
            normalized = aliases.get(keyword, keyword)
            if normalized in blocked:
                blocked_counter[normalized] += 1
            if normalized in candidate_removals:
                candidate_counter[normalized] += 1

    print(f"Researchers: {len(researchers)}")
    print(f"Raw unique keywords: {len(raw_counter)}")
    print(f"Normalized unique keywords: {len(normalized_counter)}")
    print(f"Raw keyword assignments: {sum(raw_counter.values())}")
    print()

    print("Top normalized keywords:")
    for keyword, count in normalized_counter.most_common(40):
        print(f"  {count:>3}  {keyword}")
    print()

    print("Alias usage:")
    if alias_counter:
        for alias, count in alias_counter.most_common():
            print(f"  {count:>3}  {alias}")
    else:
        print("    none")
    print()

    print("Blocked keyword hits:")
    if blocked_counter:
        for keyword, count in blocked_counter.most_common():
            print(f"  {count:>3}  {keyword}")
    else:
        print("    none")
    print()

    print("Candidate removals to review:")
    if candidate_counter:
        for keyword, count in candidate_counter.most_common():
            print(f"  {count:>3}  {keyword}")
    else:
        print("    none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
