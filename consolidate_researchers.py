#!/usr/bin/env python3
"""
Consolidate batch researcher/publication CSVs into researchers.json.
"""

import json
import csv
import unicodedata
import re
import sys
from pathlib import Path

BASE = Path("/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap")
JSON_PATH = BASE / "site/data/researchers.json"
B1_RES  = BASE / "copilot_outputs/Researchers/researchers_batch_1.csv"
B1_PUBS = BASE / "copilot_outputs/Researchers/publications_batch_1.csv"
B2_RES  = BASE / "copilot_outputs/Researchers/batch2_researchers.csv"
B2_PUBS = BASE / "copilot_outputs/Researchers/batch2_publications.csv"
B3_RES  = BASE / "copilot_outputs/Researchers/batch3_researchers.csv"
B3_PUBS = BASE / "copilot_outputs/Researchers/batch3_publications.csv"


# ── helpers ────────────────────────────────────────────────────────────────────

def strip_accents(s: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

def normalize_name(name: str) -> str:
    """Return (lastname_norm, firstname_initial) for fuzzy matching.
    Handles 'Last, First' and 'First Last' formats.
    """
    name = name.strip()
    if ',' in name:
        parts = name.split(',', 1)
        last = strip_accents(parts[0].strip()).lower()
        first_raw = parts[1].strip()
    else:
        tokens = name.split()
        last = strip_accents(tokens[-1]).lower() if tokens else ''
        first_raw = tokens[0] if len(tokens) > 1 else ''
    first_initial = strip_accents(first_raw[:1]).lower() if first_raw else ''
    return (last, first_initial)

def normalize_name_variants(name: str) -> list[tuple]:
    """Return list of (lastname_norm, firstname_initial) tuples, trying multiple
    parsings for names without commas (handles compound last names like
    'Cuéllar Soto' in 'Erika Cuéllar Soto').
    """
    name = name.strip()
    if ',' in name:
        parts = name.split(',', 1)
        last = strip_accents(parts[0].strip()).lower()
        first_raw = parts[1].strip()
        first_initial = strip_accents(first_raw[:1]).lower() if first_raw else ''
        return [(last, first_initial)]
    else:
        tokens = name.split()
        if not tokens:
            return [('', '')]
        results = []
        # Try: last = last token, first = first token
        last1 = strip_accents(tokens[-1]).lower()
        init1 = strip_accents(tokens[0][:1]).lower() if len(tokens) > 1 else ''
        results.append((last1, init1))
        # Try: last = all tokens except first (compound surname), first = first token
        if len(tokens) >= 3:
            compound_last = strip_accents(' '.join(tokens[1:])).lower()
            init2 = strip_accents(tokens[0][:1]).lower()
            results.append((compound_last, init2))
        # Try: last = last two tokens, first = first token
        if len(tokens) >= 3:
            last2 = strip_accents(' '.join(tokens[-2:])).lower()
            init3 = strip_accents(tokens[0][:1]).lower()
            results.append((last2, init3))
        return results

def name_matches(csv_name: str, db_name: str) -> bool:
    """True if last names match and first initials match (or one is empty).
    Handles compound last names (e.g. 'Cuéllar Soto') in both formats.
    """
    csv_variants = normalize_name_variants(csv_name)
    db_variants = normalize_name_variants(db_name)
    for (c_last, c_init) in csv_variants:
        for (d_last, d_init) in db_variants:
            if c_last != d_last:
                continue
            if c_init and d_init and c_init != d_init:
                continue
            return True
    return False

def make_slug(name: str) -> str:
    """Convert 'Last, First Middle' to 'last-first-middle' slug."""
    s = strip_accents(name)
    s = s.lower()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s,]+', '-', s)
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    return s

def split_semi(value: str) -> list:
    if not value or not value.strip():
        return []
    return [v.strip() for v in value.split(';') if v.strip()]

def normalize_title(t: str) -> str:
    return re.sub(r'\s+', ' ', t.strip().lower())

def read_csv(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k.strip(): v.strip() for k, v in row.items() if k})
    return rows


# ── load existing DB ────────────────────────────────────────────────────────────

with open(JSON_PATH, encoding='utf-8') as f:
    researchers = json.load(f)

# Build lookup: db_name → index
name_to_idx = {}
for i, r in enumerate(researchers):
    name_to_idx[r['name']] = i

def find_researcher(csv_name: str) -> int | None:
    """Return index in researchers list, or None."""
    for db_name, idx in name_to_idx.items():
        if name_matches(csv_name, db_name):
            return idx
    return None


# ── STATS bookkeeping ───────────────────────────────────────────────────────────

new_researchers_added = []   # names
pubs_added_per = {}          # name -> count
pubs_skipped_dup = 0
researchers_skipped = []     # (name, reason)
unmatched_pubs = []          # csv_name strings that couldn't be matched


# ── BATCH 1 researchers ─────────────────────────────────────────────────────────

b1_rows = read_csv(B1_RES)

for row in b1_rows:
    csv_name = row['name']
    idx = find_researcher(csv_name)
    if idx is not None:
        researchers_skipped.append((csv_name, 'already in DB (batch 1)'))
        continue

    # NEW researcher from batch 1 — full profile available
    slug = make_slug(csv_name)
    entry = {
        "id": slug,
        "name": csv_name,
        "total_publications_in_seed": 0,
        "first_author_publications": 0,
        "tags_from_seed": [],
        "top_collaborators_from_seed": [],
        "year_range": "",
        "affiliation": row.get('affiliation', ''),
        "country": row.get('country', ''),
        "webpage": row.get('webpage', ''),
        "email": row.get('email', ''),
        "deceased": row.get('deceased', 'FALSE').strip().upper() == 'TRUE',
        "thematic_focus": split_semi(row.get('themes', '')),
        "geographical_focus": split_semi(row.get('geographical_focus', '')),
        "scales": split_semi(row.get('scales', '')),
        "keywords": split_semi(row.get('keywords', '')),
        "research_description_en": row.get('research_description_en', ''),
        "research_description_es": row.get('research_description_es', ''),
        "main_collaborators": split_semi(row.get('main_collaborators', '')),
        "fieldwork_locations": split_semi(row.get('fieldwork_locations', '')),
        "publications": [],
        "selected_publications": [],
    }
    researchers.append(entry)
    new_idx = len(researchers) - 1
    name_to_idx[csv_name] = new_idx
    new_researchers_added.append(csv_name)
    pubs_added_per[csv_name] = 0


# ── BATCH 2 researchers ─────────────────────────────────────────────────────────

b2_rows = read_csv(B2_RES)

for row in b2_rows:
    csv_name = row.get('researcher_name', '').strip()
    if not csv_name:
        continue
    idx = find_researcher(csv_name)
    if idx is not None:
        researchers_skipped.append((csv_name, 'already in DB (batch 2)'))
        continue

    slug = make_slug(csv_name)
    entry = {
        "id": slug,
        "name": csv_name,
        "total_publications_in_seed": 0,
        "first_author_publications": 0,
        "tags_from_seed": [],
        "top_collaborators_from_seed": [],
        "year_range": "",
        "affiliation": row.get('primary_affiliation', ''),
        "country": row.get('country_base', ''),
        "webpage": '',
        "email": '',
        "deceased": False,
        "thematic_focus": [],
        "geographical_focus": split_semi(row.get('focus_geography', '')),
        "scales": [],
        "keywords": split_semi(row.get('expertise_keywords', '')),
        "research_description_en": '',
        "research_description_es": '',
        "main_collaborators": [],
        "fieldwork_locations": [],
        "publications": [],
        "selected_publications": [],
    }
    researchers.append(entry)
    new_idx = len(researchers) - 1
    name_to_idx[csv_name] = new_idx
    new_researchers_added.append(csv_name)
    pubs_added_per[csv_name] = 0


# ── BATCH 3 researchers — all skipped ─────────────────────────────────────────

b3_rows = read_csv(B3_RES)
for row in b3_rows:
    csv_name = row.get('researcher_name', '').strip()
    if not csv_name:
        continue
    # Check if they've been added via batches 1/2 already
    idx = find_researcher(csv_name)
    if idx is not None:
        researchers_skipped.append((csv_name, 'duplicate — batch 3 (skipping researcher creation)'))
    else:
        # Unexpected new researcher in batch 3 — log it but don't add
        researchers_skipped.append((csv_name, 'unexpected new in batch 3 (not added per instructions)'))


# ── build title-lookup per researcher for dedup ────────────────────────────────

def get_pub_titles(idx: int) -> set:
    return {normalize_title(p['title']) for p in researchers[idx].get('publications', [])}


# ── process publications helper ────────────────────────────────────────────────

def add_pub(csv_name: str, pub: dict, skip_bad_year: bool = True):
    global pubs_skipped_dup
    year = pub.get('year', '').strip()
    if skip_bad_year and (not year or year.lower() == 'unknown'):
        return
    # Skip talk/profile
    if pub.get('publication_type', '').lower() in ('talk/profile',):
        return

    idx = find_researcher(csv_name)
    if idx is None:
        if csv_name not in unmatched_pubs:
            unmatched_pubs.append(csv_name)
        return

    existing_titles = get_pub_titles(idx)
    t_norm = normalize_title(pub['title'])
    if t_norm in existing_titles:
        pubs_skipped_dup += 1
        return

    researchers[idx]['publications'].append(pub)
    existing_titles.add(t_norm)  # keep set in sync for this session
    r_name = researchers[idx]['name']
    pubs_added_per[r_name] = pubs_added_per.get(r_name, 0) + 1


# ── BATCH 1 publications ───────────────────────────────────────────────────────

# Build title→is_first_author map from batch 1 for use in batches 2/3
b1_pub_rows = read_csv(B1_PUBS)
b1_title_first_author = {}  # normalized_title -> bool

for row in b1_pub_rows:
    csv_name = row.get('researcher_name', '').strip()
    title = row.get('title', '').strip()
    year  = row.get('year', '').strip()
    journal = row.get('journal', '').strip()
    doi = row.get('doi', '').strip()
    is_fa_raw = row.get('is_first_author', 'FALSE').strip().upper()
    is_fa = is_fa_raw == 'TRUE'

    t_norm = normalize_title(title)
    if t_norm and is_fa:
        b1_title_first_author[t_norm] = True
    elif t_norm and t_norm not in b1_title_first_author:
        b1_title_first_author[t_norm] = False

    pub = {
        "title": title,
        "year": year,
        "journal": journal,
        "doi": doi,
        "is_first_author": is_fa,
    }
    add_pub(csv_name, pub)


# ── BATCH 2 publications ───────────────────────────────────────────────────────

b2_pub_rows = read_csv(B2_PUBS)

for row in b2_pub_rows:
    csv_name = row.get('researcher_name', '').strip()
    title = row.get('title', '').strip()
    year  = row.get('year', '').strip()
    venue = row.get('venue', '').strip()
    pub_type = row.get('publication_type', '').strip().lower()
    doi = row.get('doi_or_identifier', '').strip()

    if pub_type == 'talk/profile':
        continue

    t_norm = normalize_title(title)
    is_fa = b1_title_first_author.get(t_norm, False)

    pub = {
        "title": title,
        "year": year,
        "journal": venue,
        "doi": doi,
        "is_first_author": is_fa,
    }
    add_pub(csv_name, pub)


# ── BATCH 3 publications ───────────────────────────────────────────────────────

b3_pub_rows = read_csv(B3_PUBS)

for row in b3_pub_rows:
    csv_name = row.get('researcher_name', '').strip()
    title = row.get('title', '').strip()
    year  = row.get('year', '').strip()
    venue = row.get('venue', '').strip()
    pub_type = row.get('publication_type', '').strip().lower()
    doi = row.get('doi_or_identifier', '').strip()

    if pub_type == 'talk/profile':
        continue

    t_norm = normalize_title(title)
    is_fa = b1_title_first_author.get(t_norm, False)

    pub = {
        "title": title,
        "year": year,
        "journal": venue,
        "doi": doi,
        "is_first_author": is_fa,
    }
    add_pub(csv_name, pub)


# ── post-processing: sort pubs, update stats ────────────────────────────────────

for r in researchers:
    pubs = r.get('publications', [])
    if not pubs:
        continue

    def year_key(p):
        try:
            return int(p.get('year', 0))
        except (ValueError, TypeError):
            return 0

    pubs.sort(key=year_key, reverse=True)
    r['publications'] = pubs

    years = []
    for p in pubs:
        try:
            years.append(int(p.get('year', '')))
        except (ValueError, TypeError):
            pass

    r['total_publications_in_seed'] = len(pubs)
    r['first_author_publications'] = sum(1 for p in pubs if p.get('is_first_author'))
    if years:
        r['year_range'] = f"{min(years)}-{max(years)}"
    # else leave existing year_range


# ── write output ───────────────────────────────────────────────────────────────

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(researchers, f, indent=2, ensure_ascii=False)


# ── summary ────────────────────────────────────────────────────────────────────

total_pubs = sum(len(r.get('publications', [])) for r in researchers)

print("=" * 60)
print("CONSOLIDATION SUMMARY")
print("=" * 60)

print(f"\n✓ NEW RESEARCHERS ADDED ({len(new_researchers_added)}):")
for name in new_researchers_added:
    count = pubs_added_per.get(name, 0)
    print(f"    {name}  [{count} pubs]")

print(f"\n✓ NEW PUBLICATIONS ADDED PER RESEARCHER (existing + new):")
# Show all researchers that got at least 1 new pub
for name, cnt in sorted(pubs_added_per.items(), key=lambda x: -x[1]):
    if cnt > 0:
        print(f"    {cnt:3d}  {name}")

# Show existing researchers that got new pubs (not in new_researchers_added)
print(f"\n✓ EXISTING RESEARCHERS THAT RECEIVED NEW PUBS:")
for name, cnt in sorted(pubs_added_per.items(), key=lambda x: -x[1]):
    if cnt > 0 and name not in new_researchers_added:
        print(f"    {cnt:3d}  {name}")
if not any(cnt > 0 and name not in new_researchers_added
           for name, cnt in pubs_added_per.items()):
    print("    (none — all new pubs went to newly-added researchers)")

print(f"\n✓ DUPLICATE PUBLICATIONS SKIPPED: {pubs_skipped_dup}")

print(f"\n✓ RESEARCHERS SKIPPED AS DUPLICATES/EXISTING:")
batch3_skipped = [n for n, r in researchers_skipped if 'batch 3' in r]
print(f"    Batch 3 (all expected duplicates): {len(batch3_skipped)}")
for name, reason in researchers_skipped:
    if 'batch 3' in reason:
        print(f"        {name}")
batch1_2_skipped = [(n, r) for n, r in researchers_skipped if 'batch 3' not in r]
if batch1_2_skipped:
    print(f"    Batches 1/2 (already in DB):")
    for name, reason in batch1_2_skipped:
        print(f"        {name}  ({reason})")

print(f"\n✓ UNMATCHED RESEARCHER NAMES (couldn't match to DB):")
if unmatched_pubs:
    for name in unmatched_pubs:
        print(f"    {name}")
else:
    print("    (none — all researchers matched)")

print(f"\n{'=' * 60}")
print(f"TOTALS:")
print(f"  Total researchers in final DB : {len(researchers)}")
print(f"  Total publications in final DB: {total_pubs}")
print("=" * 60)
