#!/usr/bin/env python3
"""
Validate the canonical structure of site/data/researchers.json.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

from discipline_taxonomy import DISCIPLINE_ALIASES, VALID_DISCIPLINES, normalize_discipline
from keyword_taxonomy import load_keyword_taxonomy, normalize_keyword


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"

REQUIRED_RESEARCHER_FIELDS = {
    "id": str,
    "name": str,
    "affiliation": str,
    "country": str,
    "webpage": str,
    "email": str,
    "deceased": bool,
    "disciplines": list,
    "themes": list,
    "keywords": list,
    "geographical_focus": list,
    "scales": list,
    "research_description_en": str,
    "research_description_es": str,
    "publications": list,
    "tags_from_seed": list,
    "top_collaborators_from_seed": list,
    "main_collaborators": list,
    "fieldwork_locations": list,
}

OPTIONAL_RESEARCHER_FIELDS = {
    "orcid": str,
    "year_range": str,
    "selected_publications": list,
    "thematic_focus": list,
    "total_publications_in_seed": int,
    "first_author_publications": int,
}

REQUIRED_PUBLICATION_FIELDS = {
    "title": str,
    "year": str,
    "journal": str,
    "is_first_author": bool,
}

OPTIONAL_PUBLICATION_FIELDS = {
    "title_es": str,
    "doi": str,
    "url": str,
}

VALID_THEMES = {
    "Ecology & Biodiversity",
    "Land Use & Deforestation",
    "Wildlife & Conservation Biology",
    "Social Sciences & Political Ecology",
    "History, Culture & Identity",
    "Regional Geography",
    "Climate, Carbon & Energy",
    "Land Tenure & Governance",
    "Hydrology & Soils",
    "Remote Sensing & Monitoring",
    "Agroecology & Rural Development",
    "Public Health & Disease Ecology",
}

YEAR_PATTERN = re.compile(r"^\d{4}$")
DOI_URL_PREFIX = "https://doi.org/"
KEYWORD_TAXONOMY = load_keyword_taxonomy()


def load_dataset() -> list[dict]:
    with DATA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise TypeError(f"{DATA_PATH} must contain a JSON array")
    return data


def typename(expected_type: type) -> str:
    return expected_type.__name__


def validate_value_type(value, expected_type: type) -> bool:
    return isinstance(value, expected_type)


def ensure_list_of_strings(values, path: str, errors: list[str]) -> None:
    if not isinstance(values, list):
        errors.append(f"{path}: expected list, got {type(values).__name__}")
        return
    for index, item in enumerate(values):
        if not isinstance(item, str):
            errors.append(f"{path}[{index}]: expected str, got {type(item).__name__}")


def looks_like_all_caps_title(title: str) -> bool:
    letters = [char for char in title if char.isalpha()]
    if len(letters) < 12:
        return False
    return title.upper() == title


def validate_publication(pub: dict, path: str, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(pub, dict):
        errors.append(f"{path}: expected object, got {type(pub).__name__}")
        return

    for field, expected_type in REQUIRED_PUBLICATION_FIELDS.items():
        if field not in pub:
            errors.append(f"{path}: missing required field '{field}'")
            continue
        if not validate_value_type(pub[field], expected_type):
            errors.append(
                f"{path}.{field}: expected {typename(expected_type)}, got {type(pub[field]).__name__}"
            )

    for field, expected_type in OPTIONAL_PUBLICATION_FIELDS.items():
        if field in pub and not validate_value_type(pub[field], expected_type):
            errors.append(
                f"{path}.{field}: expected {typename(expected_type)}, got {type(pub[field]).__name__}"
            )

    title = pub.get("title")
    if isinstance(title, str) and not title.strip():
        errors.append(f"{path}.title: must not be empty")
    elif isinstance(title, str) and looks_like_all_caps_title(title):
        warnings.append(f"{path}.title: appears to be stored in all caps")

    year = pub.get("year")
    if isinstance(year, str) and not YEAR_PATTERN.match(year):
        errors.append(f"{path}.year: expected 4-digit year, got '{year}'")

    doi = pub.get("doi")
    if isinstance(doi, str):
        if doi.startswith(DOI_URL_PREFIX):
            errors.append(f"{path}.doi: should store DOI only, not a DOI URL")
        if not doi and not pub.get("url"):
            warnings.append(f"{path}: publication has neither DOI nor URL")

    if "doi" not in pub and not pub.get("url"):
        warnings.append(f"{path}: publication has neither DOI nor URL")


def validate_researcher(researcher: dict, index: int, errors: list[str], warnings: list[str]) -> None:
    path = f"researchers[{index}]"

    if not isinstance(researcher, dict):
        errors.append(f"{path}: expected object, got {type(researcher).__name__}")
        return

    for field, expected_type in REQUIRED_RESEARCHER_FIELDS.items():
        if field not in researcher:
            errors.append(f"{path}: missing required field '{field}'")
            continue
        if not validate_value_type(researcher[field], expected_type):
            errors.append(
                f"{path}.{field}: expected {typename(expected_type)}, got {type(researcher[field]).__name__}"
            )

    for field, expected_type in OPTIONAL_RESEARCHER_FIELDS.items():
        if field in researcher and not validate_value_type(researcher[field], expected_type):
            errors.append(
                f"{path}.{field}: expected {typename(expected_type)}, got {type(researcher[field]).__name__}"
            )

    for field in [
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
    ]:
        if field in researcher and field != "publications":
            ensure_list_of_strings(researcher[field], f"{path}.{field}", errors)

    if "thematic_focus" in researcher:
        ensure_list_of_strings(researcher["thematic_focus"], f"{path}.thematic_focus", errors)

    if "selected_publications" in researcher:
        if not isinstance(researcher["selected_publications"], list):
            errors.append(
                f"{path}.selected_publications: expected list, got {type(researcher['selected_publications']).__name__}"
            )

    for theme in researcher.get("themes", []):
        if theme not in VALID_THEMES:
            errors.append(f"{path}.themes: invalid theme '{theme}'")

    seen_disciplines: set[str] = set()
    for discipline in researcher.get("disciplines", []):
        if discipline in DISCIPLINE_ALIASES:
            warnings.append(
                f"{path}.disciplines: '{discipline}' should be normalized to '{DISCIPLINE_ALIASES[discipline]}'"
            )
        normalized_discipline = normalize_discipline(discipline)
        if normalized_discipline not in VALID_DISCIPLINES:
            warnings.append(
                f"{path}.disciplines: '{normalized_discipline}' is outside the controlled vocabulary"
            )
        if normalized_discipline in seen_disciplines:
            warnings.append(
                f"{path}.disciplines: duplicate discipline after normalization '{normalized_discipline}'"
            )
        else:
            seen_disciplines.add(normalized_discipline)

    aliases = KEYWORD_TAXONOMY.get("aliases", {})
    blocked = KEYWORD_TAXONOMY.get("blocked_keywords", {})
    seen_keywords: set[str] = set()
    for keyword in researcher.get("keywords", []):
        if keyword in aliases:
            warnings.append(
                f"{path}.keywords: '{keyword}' should be normalized to '{aliases[keyword]}'"
            )
        normalized_keyword = normalize_keyword(keyword, aliases)
        if normalized_keyword in blocked:
            warnings.append(
                f"{path}.keywords: '{normalized_keyword}' is marked for removal ({blocked[normalized_keyword]})"
            )
        if normalized_keyword in seen_keywords:
            warnings.append(
                f"{path}.keywords: duplicate keyword after normalization '{normalized_keyword}'"
            )
        else:
            seen_keywords.add(normalized_keyword)

    researcher_id = researcher.get("id")
    if isinstance(researcher_id, str) and not researcher_id.strip():
        errors.append(f"{path}.id: must not be empty")

    name = researcher.get("name")
    if isinstance(name, str) and not name.strip():
        errors.append(f"{path}.name: must not be empty")

    en_desc = researcher.get("research_description_en")
    if isinstance(en_desc, str) and not en_desc.strip():
        errors.append(f"{path}.research_description_en: must not be empty")

    es_desc = researcher.get("research_description_es")
    if isinstance(es_desc, str) and not es_desc.strip():
        warnings.append(f"{path}.research_description_es: empty")

    webpage = researcher.get("webpage")
    if isinstance(webpage, str) and webpage and not webpage.startswith(("http://", "https://")):
        warnings.append(f"{path}.webpage: does not look like an absolute URL")

    publications = researcher.get("publications", [])
    if isinstance(publications, list):
        if not publications:
            errors.append(f"{path}.publications: must contain at least one publication")
        for pub_index, publication in enumerate(publications):
            validate_publication(publication, f"{path}.publications[{pub_index}]", errors, warnings)

    selected_publications = researcher.get("selected_publications", [])
    if isinstance(selected_publications, list):
        for pub_index, publication in enumerate(selected_publications):
            validate_publication(
                publication,
                f"{path}.selected_publications[{pub_index}]",
                errors,
                warnings,
            )


def validate_dataset(researchers: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    ids: dict[str, int] = {}
    names: dict[str, int] = {}
    name_signatures: dict[str, tuple[str, int]] = {}

    def normalize_name_fragment(value: str) -> str:
        normalized = "".join(
            char
            for char in unicodedata.normalize("NFD", value.lower())
            if unicodedata.category(char) != "Mn"
        )
        normalized = re.sub(r"[^a-z\s]", " ", normalized)
        return " ".join(normalized.split())

    def name_signature(value: str) -> str:
        if not value.strip():
            return ""
        if "," in value:
            surname_part, given_part = value.split(",", 1)
        else:
            pieces = value.split()
            surname_part = pieces[-1] if pieces else ""
            given_part = " ".join(pieces[:-1])

        surname_tokens = [
            token
            for token in normalize_name_fragment(surname_part).split()
            if token not in {"de", "del", "la", "las", "los", "y", "von"}
        ]
        given_tokens = normalize_name_fragment(given_part).split()
        if not surname_tokens or not given_tokens:
            return ""
        return f"{surname_tokens[0]}::{given_tokens[0]}"

    for index, researcher in enumerate(researchers):
        validate_researcher(researcher, index, errors, warnings)

        researcher_id = researcher.get("id")
        if isinstance(researcher_id, str):
            if researcher_id in ids:
                errors.append(
                    f"researchers[{index}].id: duplicate id '{researcher_id}' also used at index {ids[researcher_id]}"
                )
            else:
                ids[researcher_id] = index

        name = researcher.get("name")
        if isinstance(name, str):
            if name in names:
                warnings.append(
                    f"researchers[{index}].name: duplicate name '{name}' also used at index {names[name]}"
                )
            else:
                names[name] = index

            signature = name_signature(name)
            if signature:
                if signature in name_signatures:
                    previous_name, previous_index = name_signatures[signature]
                    if previous_name != name:
                        warnings.append(
                            "researchers[{idx}].name: possible near-duplicate with "
                            "researchers[{prev_idx}] ('{current}' vs '{previous}')".format(
                                idx=index,
                                prev_idx=previous_index,
                                current=name,
                                previous=previous_name,
                            )
                        )
                else:
                    name_signatures[signature] = (name, index)

    return errors, warnings


def main() -> int:
    researchers = load_dataset()
    errors, warnings = validate_dataset(researchers)

    print(f"Validated {len(researchers)} researchers from {DATA_PATH}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print("\nError details:")
        for error in errors:
            print(f"- {error}")

    if warnings:
        print("\nWarning details:")
        for warning in warnings:
            print(f"- {warning}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
