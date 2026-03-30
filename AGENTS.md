# AGENTS.md

## Model Usage Policy

**Conserve quota aggressively.** Delegate all agent sub-tasks to the cheapest model that can handle them:

- **Haiku**: Web searches, CrossRef API lookups, DOI verification, JSON transforms, data validation, file reads, bulk find-and-replace.
- **Sonnet**: Writing descriptions, code edits with context, reviewing data for errors, translations.
- **Opus**: Architecture decisions, multi-step planning, nuanced judgment, or anything where getting it wrong is costly.

Default to Haiku for any agent doing search/lookup work. If an agent task description doesn't require reasoning or writing, it should be Haiku.

## Project Overview

Bilingual (EN/ES) static web app for discovering researchers in the Gran Chaco region. Vanilla HTML/CSS/JS, no build step, data in `site/data/researchers.json`. Dev server: `cd site && python3 -m http.server 8080`. Tests: open `http://localhost:8080/tests.html`.

## Database Expansion Protocol

### Search strategy (two-pass, Haiku-first)
**Pass 1 — Haiku agent**: Google Scholar search for the researcher + "Chaco". Collect titles, years, journals, DOIs. Target: find what's easy to find.
**Pass 2 — Haiku agent**: Only if Pass 1 found < 5 papers, search CrossRef API and one additional source (ORCID, CONICET Digital, or Semantic Scholar — whichever is most likely for the researcher's country). DOI verification is also Haiku (just a CrossRef API fetch).
**Sonnet agent**: Writes EN+ES descriptions, assigns themes/disciplines/keywords.

Do NOT instruct agents to search all 6 platforms exhaustively. That burns tokens for marginal returns.

### Critical rules
- **Authorship verification**: Always verify researcher is in the author list before assigning a DOI. Use CrossRef API.
- **DOI vs URL**: `doi` field = DOI string only (no prefix). `url` = fallback only when no DOI exists.
- **Title formatting**: Publication titles should not be stored in all caps. Normalize them to standard capitalization during intake.
- **Bilingual titles**: If a journal exposes both English and Spanish titles, keep the canonical `title` and add the Spanish UI form as `title_es` so the Spanish site can display it.
- **Discipline tagging**: Do a quick gut check so `disciplines` capture the clearly stated fields in the description, not just the narrowest anchor discipline.
- **Summary tone**: Research summaries must stay descriptive and neutral. Avoid prestige framing, citation counts, superlatives, or any language explaining why a profile belongs in the database.
- **Quick contact check**: After adding or updating a profile, do one cheap pass for a person-specific institutional email. If it is not easy to verify from an official page, skip it.
- **Webpage audit**: New or changed `webpage` values should be checked with `python3 scripts/report_webpage_audit.py`.
- **Publication link audit**: New or changed publication links and DOI targets should be checked with `python3 scripts/report_link_health.py --include-webpages`.
- **Batch provenance**: Every newly added researcher should be logged in `IMPORT_BATCHES.md` so Codex-added profiles can be compared against the legacy dataset later.
- **Single-writer rule**: Delegated agents may gather evidence or review records, but only the main process should write to `site/data/researchers.json` and the tracking docs. This avoids duplicate or unsynchronized imports.
- **12 valid themes**: `Ecology & Biodiversity`, `Land Use & Deforestation`, `Wildlife & Conservation Biology`, `Social Sciences & Political Ecology`, `History, Culture & Identity`, `Regional Geography`, `Climate, Carbon & Energy`, `Land Tenure & Governance`, `Hydrology & Soils`, `Remote Sensing & Monitoring`, `Agroecology & Rural Development`, `Public Health & Disease Ecology`
- **After adding researchers**: update the count assertion in `tests.html` and counts in `AGENTS.md`/`MEMORY.md`.
- **Batch size**: 5-10 researchers per agent to survive rate limits. Save after each batch.
- **Keyword hygiene**: prefer existing keywords, run `python3 scripts/normalize_keywords.py`, then `python3 scripts/report_keyword_inventory.py`, then `python3 scripts/validate_researchers.py`.

### Scope
**Include**: social/environmental systems (ecology, geography, sociology, anthropology, history, public health, geomorphology). Active since 2000 or deceased within ~20 years. Include researchers studying Chaco peoples/places/ecosystems even without "Chaco" keyword.
**Exclude**: engineering, medical research, toxicology. When unsure, ask.

## Current Stats

- **278 researchers, 1432 publications** (as of 2026-03-29)
