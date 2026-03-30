#!/usr/bin/env python3
"""
Report keyword translation coverage for the live dataset.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "site" / "data" / "researchers.json"
I18N_PATH = ROOT / "site" / "js" / "i18n.js"


IDENTITY_OK = {
    "ArgVeg database",
    "Ayoreo",
    "Bolivia",
    "Carlos Casado",
    "Chané",
    "Chorote",
    "Criollos",
    "Fabaceae",
    "GeoForPy",
    "Gran Chaco societies",
    "Guaraní",
    "Guaraní communities",
    "Guaraní peoples",
    "Guyra Paraguay",
    "IPBES",
    "Izoceño",
    "Jesuit missions",
    "Kaa-Iya",
    "La Plata",
    "Landsat",
    "Law 26.331",
    "LiDAR",
    "Latin America",
    "MOCASE",
    "Mapuche",
    "Mar Chiquita",
    "Mataco",
    "Mennonite colonies",
    "Mocoví",
    "Modelos productivos",
    "Moqoít",
    "Napalpí",
    "Nivaclé",
    "Pantanal",
    "Pilcomayo River",
    "Qom",
    "SAR",
    "Schinopsis",
    "Schinopsis balansae",
    "Sentinel",
    "Toba",
    "Triatoma infestans",
    "UAV",
    "Wichí",
    "Wichí communities",
    "Wichí peoples",
    "Wichí properties",
    "Yshir",
    "Yshiro",
    "Yungas",
}


def load_translation_keys(block_name: str) -> set[str]:
    text = I18N_PATH.read_text(encoding="utf-8")
    match = re.search(rf"const {block_name} = \{{(.*?)\n  \}};", text, re.S)
    if not match:
        raise RuntimeError(f"{block_name} block not found")
    keys = set()
    for raw_key in re.findall(r"'((?:\\'|[^'])+)':", match.group(1)):
        keys.add(raw_key.replace("\\'", "'"))
    return keys


def is_identity_ok(keyword: str) -> bool:
    if keyword in IDENTITY_OK:
        return True
    if re.fullmatch(r"[A-Z0-9\-]+", keyword):
        return True
    if any(ch in keyword for ch in "áéíóúñÁÉÍÓÚÑ"):
        return True
    return False


def main() -> int:
    keyword_translation_keys = load_translation_keys("keywordTranslations")
    geo_translation_keys = load_translation_keys("geoTranslations")
    country_translation_keys = load_translation_keys("countryTranslations")
    translation_keys = keyword_translation_keys | geo_translation_keys | country_translation_keys
    researchers = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    counter: Counter[str] = Counter()
    for researcher in researchers:
        counter.update(researcher.get("keywords", []))

    missing = [
        (count, keyword)
        for keyword, count in counter.most_common()
        if keyword not in translation_keys and not is_identity_ok(keyword)
    ]

    print(f"Dataset keywords: {len(counter)}")
    print(f"Translated keywords: {sum(1 for k in counter if k in translation_keys)}")
    print(f"Identity-ok keywords: {sum(1 for k in counter if k not in translation_keys and is_identity_ok(k))}")
    print(f"Missing translation entries needing review: {len(missing)}")
    print()

    for count, keyword in missing[:200]:
        print(f"{count:>3}  {keyword}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
