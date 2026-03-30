# Keyword Taxonomy Workflow

## Goal

Keep `keywords` useful as a fine-grained topical vocabulary rather than letting them drift into a noisy mix of case variants, punctuation variants, geography labels, and generic filler terms.

## Current State

- the dataset contains a large keyword inventory
- many duplicates are low-risk formatting drift rather than real taxonomy differences
- some broad terms are probably too vague and should be reviewed before future imports reuse them

## Conservative First Pass

The current keyword normalization policy only applies low-risk changes automatically:

- case normalization for obvious duplicates such as `Biodiversity` -> `biodiversity`
- punctuation normalization for obvious duplicates such as `land-use change` -> `land use change`
- proper-name normalization for labels such as `gran chaco` -> `Gran Chaco`
- agreed semantic consolidation for clearly equivalent labels, for example:
  - `Q-method` -> `Q methodology`
  - `western toba` -> `Toba`
  - `Law 26.331` / `ley de bosques` / `Native forests act` -> `native forest law`
  - `Landsat` / `Sentinel` / `SAR` / `LiDAR` / `UAV` -> `remote sensing`
  - `dry Chaco forest` / `Chaco woodlands` / `tropical dry forests` -> `dry forests`

These rules live in [config/keyword_taxonomy.json](/Users/yannlepolain/Library/CloudStorage/OneDrive-McGillUniversity/Univ/Coding/ChacoMap/config/keyword_taxonomy.json).

## Scripts

- `python3 scripts/report_keyword_inventory.py`
  - reports raw keyword counts, normalized counts, alias usage, and candidate removals
- `python3 scripts/normalize_keywords.py`
  - applies the configured alias map and blocked-keyword rules to the dataset

## Review Queue

The config file also contains a `candidate_removals` list for terms that may be too broad, too geographic, or too close to themes/disciplines.

These should not be deleted automatically without review. Examples include:

- broad geography labels like `Chaco`
- generic topical terms like `conservation`, `forest`, `biodiversity`
- generic methods or umbrella concepts like `modeling`, `monitoring`, `management`

## Intake Rule

For new profiles:

1. prefer an existing keyword before inventing a new one
2. avoid case and punctuation variants of an existing keyword
3. avoid ethnonym-plus-qualifier variants when the group name alone is the intended concept
4. avoid broad filler terms if a more specific keyword is available
5. keep the canonical keyword in the data and maintain the Spanish equivalent in `site/js/i18n.js`
6. run `python3 scripts/normalize_keywords.py`
7. run `python3 scripts/report_keyword_inventory.py`
8. run `python3 scripts/report_keyword_translation_coverage.py`
9. run `python3 scripts/validate_researchers.py`
