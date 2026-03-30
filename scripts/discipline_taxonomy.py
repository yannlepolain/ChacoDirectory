#!/usr/bin/env python3
"""
Helpers for normalizing researcher disciplines to a controlled vocabulary.
"""

from __future__ import annotations


VALID_DISCIPLINES = {
    "Agronomy",
    "Anthropology",
    "Archaeology",
    "Biology",
    "Botany",
    "Conservation Biology",
    "Demography",
    "Ecology",
    "Economics",
    "Education",
    "Environmental Science",
    "Forestry",
    "Geography",
    "Geomorphology",
    "History",
    "Hydrology",
    "Linguistics",
    "Political Ecology",
    "Political Science",
    "Public Health",
    "Remote Sensing",
    "Sociology",
}


DISCIPLINE_ALIASES = {
    "Agroecology": "Agronomy",
    "Agrarian Studies": "Sociology",
    "Agricultural Sciences": "Agronomy",
    "Anthropological Linguistics": "Linguistics",
    "Art History": "History",
    "Biogeochemistry": "Environmental Science",
    "Biogeography": "Geography",
    "Bioarchaeology": "Archaeology",
    "Cultural Anthropology": "Anthropology",
    "Economic Anthropology": "Anthropology",
    "Ecohydrology": "Hydrology",
    "Entomology": "Biology",
    "Environmental History": "History",
    "Ethnic Studies": "Anthropology",
    "Ethnobiology": "Anthropology",
    "Ethnobotany": "Anthropology",
    "Ethnography": "Anthropology",
    "Ethnohistory": "History",
    "Ethnology": "Anthropology",
    "Geology": "Geomorphology",
    "Geomatics": "Geography",
    "Herpetology": "Biology",
    "Human Geography": "Geography",
    "Indigenous Studies": "Anthropology",
    "Landscape Ecology": "Ecology",
    "Latin American History": "History",
    "Medical Anthropology": "Anthropology",
    "Nutrition": "Public Health",
    "Oral History": "History",
    "Physical Geography": "Geography",
    "Political Economy": "Economics",
    "Political History": "History",
    "Public Policy": "Political Science",
    "Regional Geography": "Geography",
    "Remote Sensing & Land Systems": "Remote Sensing",
    "Restoration Ecology": "Ecology",
    "Rural Development": "Sociology",
    "Rural Sociology": "Sociology",
    "Rural Studies": "Sociology",
    "Social Anthropology": "Anthropology",
    "Soil Science": "Environmental Science",
    "Veterinary Science": "Biology",
    "Wildlife Biology": "Conservation Biology",
}


def normalize_discipline(discipline: str, aliases: dict[str, str] | None = None) -> str:
    aliases = aliases or DISCIPLINE_ALIASES
    cleaned = discipline.strip()
    return aliases.get(cleaned, cleaned)


def normalize_disciplines(
    disciplines: list[str],
    aliases: dict[str, str] | None = None,
) -> list[str]:
    aliases = aliases or DISCIPLINE_ALIASES
    normalized: list[str] = []
    seen: set[str] = set()
    for discipline in disciplines:
        cleaned = normalize_discipline(discipline, aliases)
        if cleaned and cleaned not in seen:
            normalized.append(cleaned)
            seen.add(cleaned)
    return normalized
