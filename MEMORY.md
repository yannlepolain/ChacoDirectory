# Chaco Research Directory — Memory / Handoff

## Current State

- Dataset status as of 2026-04-14:
  - `279` researchers
  - `1442` publications
  - validator clean: `0 errors, 0 warnings`
- Main data file:
  - [site/data/researchers.json](/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap/site/data/researchers.json)
- Stats synced in:
  - [AGENTS.md](/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap/AGENTS.md)
  - [site/tests.html](/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap/site/tests.html)

## Deployment State

- GitHub repo created:
  - [yannlepolain/ChacoDirectory](https://github.com/yannlepolain/ChacoDirectory)
- GitHub Pages workflow exists at:
  - [.github/workflows/pages.yml](/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap/.github/workflows/pages.yml)
- The site is intended to be deployed from the `site/` directory, not repo root.
- Expected public Pages URL:
  - [https://yannlepolain.github.io/ChacoDirectory/](https://yannlepolain.github.io/ChacoDirectory/)
- Planned cleaner URL:
  - custom subdomain under `lendevlab.com` such as `chaco.lendevlab.com`, `granchaco.lendevlab.com`, or `researchers.lendevlab.com`
- Important deployment note:
  - custom-domain configuration in GitHub Pages may not appear until Pages is enabled and the first deploy has completed

## Data / Content Decisions To Preserve

- Single-writer rule for dataset edits:
  - delegated agents can do read-only search/verification
  - only the main process writes `researchers.json` and tracking docs
- Profile summaries must stay factual and non-promotional.
- Do not include “why this researcher is relevant to the database” in profile summaries.
- Avoid evaluative framing like “more applied than most profiles in the dataset”.
- Use official webpage/email when easy to verify; otherwise leave blank.
- For publications:
  - `doi` field contains DOI only
  - `url` is fallback when no DOI exists
- User prefers serious fit checks before adding researchers:
  - significant Chaco line, not just one incidental coauthored paper

## Taxonomy / Normalization Rules Now In Place

- Keywords are controlled via:
  - [config/keyword_taxonomy.json](/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap/config/keyword_taxonomy.json)
- Regions are controlled via:
  - [config/geo_taxonomy.json](/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap/config/geo_taxonomy.json)
- Spanish/English keyword and region coverage should stay parallel.
- Search/autocomplete is accent-insensitive (e.g. `Musalem` matches `Musálem`).
- Current keyword inventory has already been heavily consolidated; avoid reintroducing near-duplicates.

## Recent Important Content Fixes

- Fabricio Vázquez profile expanded substantially and now includes:
  - 2026 SciELO article on agropecuary cycles in the Paraguayan Chaco
  - 2023 `Evolución del mundo rural paraguayo`
  - 2013 `Geografía humana del Chaco paraguayo`
  - additional Chaco publications from 2005, 2007, 2009, 2010
- Deliberate exclusion:
  - `El Chaco en transición...` was not added because no sufficiently stable public bibliographic trace was verified

## Queue / Saturation Status

- The earlier expansion queue has been largely exhausted.
- Remaining discovery work is now saturation-level work:
  - smaller, more selective searches
  - institute-based clusters
  - discipline-based gap checks
- Recent search directions that proved useful:
  - IMBIV
  - IER Tucumán
  - UNNE
  - French researchers (CNRS / CIRAD / IRD)
  - agronomy / land-use researchers in Paraguay, Bolivia, Argentina

## Open Work Worth Returning To Later

- Do a retrospective completeness pass on recent imports:
  - official webpages
  - institutional emails
  - missing journal values
- Continue publication-link trust audit:
  - especially older books, chapters, local journals, and fallback URLs
- Keep checking for promotional phrasing in older imported summaries.
- Consider further medium-granularity consolidation only if clearly useful:
  - some `forest-*`
  - some `water-*`
  - some governance/territorial clusters
- Potential future site work:
  - custom domain for Pages deployment
  - admin workflow for submissions
  - optional interactive map

## Practical Resume Point

- If resuming data work:
  1. run `python3 scripts/validate_researchers.py`
  2. run `python3 scripts/report_stats.py`
  3. inspect `git status`
  4. choose either:
     - saturation-level researcher discovery
     - retrospective quality audit on recent imports
     - deployment/custom-domain finish work
