#!/usr/bin/env python3
"""
Report under-keyworded profiles with evidence-backed keyword candidates.

This is a lightweight audit helper. It does not edit researchers.json; it only
flags profiles where descriptions or publication titles mention controlled
candidate terms that are missing from the profile's keywords.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"

KEYWORD_PATTERNS: dict[str, str] = {
    "Ayoreo": r"\bayoreo\b",
    "Criollos": r"\bcrioll[oa]s?\b",
    "Qom": r"\bqom\b|\btoba\b",
    "Toba": r"\btoba\b",
    "Pilagá": r"\bpilag[aá]\b",
    "Wichí": r"\bwich[ií]\b",
    "Nivaclé": r"\bnivacl[eé]\b",
    "Guaraní": r"\bguaran[ií]\b",
    "Mennonites": r"\bmennonit",
    "borderlands": r"\bborderlands?\b|tierras fronterizas",
    "Chaco War": r"chaco war|guerra del chaco",
    "missionization": r"missionization|misionalizaci[oó]n|misi[oó]n",
    "land tenure": r"land[- ]tenure|tenencia",
    "land governance": r"land governance|governance|gobernanza",
    "land control": r"land control|control de la tierra|control territorial",
    "territorial conflicts": r"territorial conflicts?|conflictos? territorial",
    "large-scale land acquisitions": r"large[- ]scale land acquisitions|adquisiciones de tierras|large land transactions",
    "native forest law": r"forest law|ley de bosques|native forest zoning|forest zoning",
    "cattle ranching": r"cattle|ranching|ganader|livestock",
    "soybeans": r"\bsoy\b|soja|soybean",
    "silvopastoral systems": r"silvopast",
    "smallholders": r"smallholders?|small[- ]scale|campesin|criollo families|pequeñ[oa]s productores",
    "agricultural expansion": r"agricultural expansion|expansi[oó]n agr[ií]cola|expansión agropecuaria",
    "agricultural frontier": r"agricultural frontier|frontera agr[ií]cola|frontier expansion",
    "commodity frontiers": r"commodity frontiers?|commodity agriculture|commodities",
    "land use change": r"land[- ]use change|land[- ]cover change|cambio de uso",
    "deforestation": r"deforestation|deforestaci[oó]n|sin bosques",
    "dry forests": r"dry forests?|bosques? secos?|chaco sin bosques",
    "landscape ecology": r"landscape ecology|ecolog[ií]a de paisajes?",
    "biogeography": r"biogeography|biogeograf[ií]a",
    "ecological planning": r"ecological planning|planificaci[oó]n ecol[oó]gica",
    "remote sensing": r"remote sensing|teledetecci[oó]n|landsat|satellite|spatially explicit",
    "GIS": r"\bGIS\b|\bSIG\b",
    "participatory mapping": r"participatory mapping|cartograf[ií]a participativa|mapeo participativo",
    "ethnography": r"ethnograph|etnograf",
    "political ecology": r"political ecology|ecolog[ií]a pol[ií]tica",
    "puma": r"\bpuma\b|Puma concolor",
    "carbon storage": r"carbon storage|almacenamiento de carbono",
    "enclosure": r"enclosure|cercamiento|fenced off|alambrad",
}


def profile_text(researcher: dict) -> str:
    parts = [
        researcher.get("research_description_en", ""),
        researcher.get("research_description_es", ""),
    ]
    for publication in researcher.get("publications", []):
        parts.append(publication.get("title", ""))
        parts.append(publication.get("title_es", ""))
        parts.append(publication.get("journal", ""))
    return " ".join(parts)


def main() -> int:
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    flagged = []

    for researcher in researchers:
        keywords = set(researcher.get("keywords", []))
        if len(keywords) >= 3:
            continue

        text = profile_text(researcher)
        candidates = [
            keyword
            for keyword, pattern in KEYWORD_PATTERNS.items()
            if keyword not in keywords and re.search(pattern, text, re.IGNORECASE)
        ]

        if candidates:
            flagged.append((researcher, candidates))

    print(f"Under-keyworded profiles with candidates: {len(flagged)}")
    for researcher, candidates in flagged:
        print()
        print(f"{researcher['name']} ({researcher['id']})")
        print(f"  current: {', '.join(researcher.get('keywords', [])) or '(none)'}")
        print(f"  candidates: {', '.join(candidates)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
