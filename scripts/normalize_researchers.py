#!/usr/bin/env python3
"""
Normalize site/data/researchers.json toward the canonical schema.
"""

from __future__ import annotations

import json
from pathlib import Path

from discipline_taxonomy import normalize_disciplines
from geo_taxonomy import load_geo_taxonomy, normalize_geographies
from keyword_taxonomy import load_keyword_taxonomy, normalize_keywords


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"

REQUIRED_STRING_FIELDS = [
    "id",
    "name",
    "affiliation",
    "country",
    "webpage",
    "email",
    "research_description_en",
    "research_description_es",
]

REQUIRED_LIST_FIELDS = [
    "disciplines",
    "themes",
    "keywords",
    "geographical_focus",
    "scales",
    "publications",
    "tags_from_seed",
    "top_collaborators_from_seed",
    "main_collaborators",
    "fieldwork_locations",
]

OPTIONAL_STRING_FIELDS = [
    "orcid",
    "year_range",
]

OPTIONAL_LIST_FIELDS = [
    "selected_publications",
    "thematic_focus",
]

OPTIONAL_INT_FIELDS = [
    "total_publications_in_seed",
    "first_author_publications",
]

PUBLICATION_STRING_FIELDS = [
    "title",
    "year",
    "journal",
    "doi",
    "url",
]

DOI_URL_PREFIX = "https://doi.org/"


def normalize_string(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def normalize_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def normalize_publication(publication: dict) -> dict:
    normalized = dict(publication)

    for field in PUBLICATION_STRING_FIELDS:
        normalized[field] = normalize_string(normalized.get(field, ""))

    if normalized["doi"].startswith(DOI_URL_PREFIX):
        normalized["doi"] = normalized["doi"][len(DOI_URL_PREFIX):]

    normalized["is_first_author"] = bool(normalized.get("is_first_author", False))
    return normalized


def normalize_researcher(researcher: dict) -> dict:
    normalized = dict(researcher)
    taxonomy = load_keyword_taxonomy()
    geo_taxonomy = load_geo_taxonomy()

    for field in REQUIRED_STRING_FIELDS:
        normalized[field] = normalize_string(normalized.get(field, ""))

    for field in REQUIRED_LIST_FIELDS:
        normalized[field] = normalize_list(normalized.get(field, []))

    for field in OPTIONAL_STRING_FIELDS:
        if field in normalized:
            normalized[field] = normalize_string(normalized.get(field, ""))

    for field in OPTIONAL_LIST_FIELDS:
        if field in normalized:
            normalized[field] = normalize_list(normalized.get(field, []))

    for field in OPTIONAL_INT_FIELDS:
        if field in normalized and normalized[field] is None:
            del normalized[field]

    normalized["deceased"] = bool(normalized.get("deceased", False))
    normalized["disciplines"] = normalize_disciplines(normalized["disciplines"])
    normalized["keywords"] = normalize_keywords(normalized["keywords"], taxonomy)
    normalized["geographical_focus"] = normalize_geographies(
        normalized["geographical_focus"],
        geo_taxonomy,
    )
    normalized["publications"] = [
        normalize_publication(publication)
        for publication in normalized["publications"]
    ]

    if "selected_publications" in normalized:
        normalized["selected_publications"] = [
            normalize_publication(publication)
            for publication in normalized["selected_publications"]
        ]

    return normalized


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    normalized = [normalize_researcher(researcher) for researcher in researchers]
    DATA_PATH.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Normalized {len(normalized)} researchers in {DATA_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
