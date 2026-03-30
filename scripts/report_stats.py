#!/usr/bin/env python3
"""
Print a compact health and coverage report for site/data/researchers.json.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"


def is_populated(value) -> bool:
    if isinstance(value, list):
        return len(value) > 0
    return bool(value)


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    publications = [publication for researcher in researchers for publication in researcher.get("publications", [])]

    print(f"Dataset: {DATA_PATH}")
    print(f"Researchers: {len(researchers)}")
    print(f"Publications: {len(publications)}")
    print(f"Affiliation countries: {len({r.get('country') for r in researchers if r.get('country')})}")

    print("\nResearcher field coverage:")
    researcher_fields = [
        "research_description_en",
        "research_description_es",
        "webpage",
        "email",
        "themes",
        "keywords",
        "disciplines",
        "thematic_focus",
        "geographical_focus",
        "scales",
        "main_collaborators",
        "fieldwork_locations",
    ]
    for field in researcher_fields:
        populated = sum(1 for researcher in researchers if is_populated(researcher.get(field)))
        print(f"- {field}: {populated}/{len(researchers)}")

    print("\nPublication field coverage:")
    publication_fields = ["title", "year", "journal", "doi", "url", "is_first_author"]
    for field in publication_fields:
        if field == "is_first_author":
            populated = sum(1 for publication in publications if field in publication)
        else:
            populated = sum(1 for publication in publications if is_populated(publication.get(field)))
        print(f"- {field}: {populated}/{len(publications)}")

    theme_counter = Counter()
    for researcher in researchers:
        for theme in researcher.get("themes", []):
            theme_counter[theme] += 1

    print("\nTheme usage:")
    for theme, count in theme_counter.most_common():
        print(f"- {theme}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
