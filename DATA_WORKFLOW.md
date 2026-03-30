# Data Workflow

## Purpose

This runbook describes the safest maintenance path for `site/data/researchers.json`.

It is intended to keep the dataset, tests, and project notes synchronized as the directory grows.

## Core Rule

Treat `site/data/researchers.json` as the operational source of truth, but never edit it blindly. Always run validation before and after meaningful changes.

## Canonical Workflow

### 1. Inspect the current baseline

Run:

```bash
python3 scripts/report_stats.py
python3 scripts/validate_researchers.py
```

Use this to confirm the live counts and understand whether the dataset already has warnings or errors before starting work.

### 2. Normalize before judging the data

If a batch import or manual edit introduces type drift or `null` values, run:

```bash
python3 scripts/normalize_researchers.py
python3 scripts/validate_researchers.py
```

Normalization is for structural cleanup. Validation is for checking whether real data-quality issues remain.
Validation also warns on probable near-duplicate names (accent-insensitive surname + first given-name signature) to catch variant re-imports before they persist.

### 3. Make data changes in small batches

- Add or revise a limited number of researchers at a time
- Prefer 5-10 researcher batches
- Delegated agents may do read-only evidence gathering, but keep a single writer:
  only the main process should modify `site/data/researchers.json` or tracking docs
- Verify authorship before assigning DOI-based metadata
- Preserve the DOI rule: `doi` stores the DOI only, `url` is fallback only

### 4. Validate after every batch

Run:

```bash
python3 scripts/normalize_researchers.py
python3 scripts/validate_researchers.py
python3 scripts/report_stats.py
```

Do not update project notes or tests until this passes cleanly enough for the intended change.

### 5. Run the quick contact and link audit

Run:

```bash
python3 scripts/report_missing_emails.py --official-only --limit 20
python3 scripts/report_webpage_audit.py
python3 scripts/report_link_health.py --include-webpages
```

Use this as a cheap manual QA pass for each batch:

- add an email only when it is clearly person-specific and institution-linked
- prefer official staff, faculty, or lab profile pages over scraped directories
- if an email or webpage requires a rabbit hole, skip it and move on
- replace broken publication links or weak webpage targets while the batch is still small
- normalize publication titles out of all-caps formatting before closing the batch
- when a journal provides both English and Spanish titles, store the alternate Spanish title as `title_es` and use it for the Spanish UI
- do a quick gut check on `disciplines` so clearly signaled secondary fields in the description are not omitted
- keep research summaries descriptive and neutral: avoid prestige language, citation counts, superlatives, or any rationale-for-inclusion phrasing

### 6. Reconcile docs and tests

After confirmed data changes:

- update count assertions in `site/tests.html` if the expected researcher total changed
- update counts in `AGENTS.md`
- log any newly added researchers in `IMPORT_BATCHES.md` so post-migration additions
  remain distinguishable from the legacy dataset

## What Counts As An Error vs Warning

### Errors

Errors are structural issues that should block further work, for example:

- missing required keys
- wrong value types
- duplicate researcher IDs
- invalid theme values
- malformed DOI storage
- researchers with no publications

### Warnings

Warnings are content-quality gaps that may be temporarily acceptable during curation, for example:

- missing Spanish descriptions
- publications with neither DOI nor fallback URL
- sparse collaborator or fieldwork metadata

Warnings should be reduced over time, but they do not necessarily block a small batch merge.

## Current Interpretation Notes

- `themes` is the canonical broad taxonomy
- `keywords` is the canonical fine-grained taxonomy
- `thematic_focus` is legacy compatibility data, not the primary thematic field
- `selected_publications` is optional
- `email` should prefer a person-specific institutional address when one is easy to verify
- `keywords` should reuse existing controlled terms where possible and should be normalized with `python3 scripts/normalize_keywords.py`
- keyword translation coverage should be checked with `python3 scripts/report_keyword_translation_coverage.py`
- keyword import rule: keep one canonical keyword list in the data, and maintain the Spanish UI in parallel through `site/js/i18n.js`
- `geographical_focus` should also use a controlled vocabulary through [config/geo_taxonomy.json](/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap/config/geo_taxonomy.json)
- before adding a new keyword, check whether it is really just:
  - an ethnonym variant (`western toba` vs `Toba`)
  - a law/policy synonym (`Law 26.331` vs `native forest law`)
  - a sensor/platform label that should collapse into a broader method (`Landsat` vs `remote sensing`)
  - a biome label that should collapse into an existing umbrella term (`tropical dry forests` vs `dry forests`)
- before adding a new geographic focus term, check whether it is really just:
  - a casing variant (`western Paraguay` vs `Western Paraguay`)
  - a translated duplicate (`Chaco Seco` vs `Dry Chaco`)
  - a verbose phrase that should collapse into an existing region (`Dry Chaco (biome-wide, including Paraguay)` vs `Dry Chaco`)

## Recommended Near-Term Cleanup

- reduce validator warnings by filling missing Spanish descriptions
- identify publications that still lack both DOI and URL
- reduce missing institutional emails with quick official-page checks
- decide whether legacy optional fields should be backfilled or retired from older maintenance assumptions
- review `candidate_removals` in [config/keyword_taxonomy.json](/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap/config/keyword_taxonomy.json) before introducing new broad or redundant keywords
