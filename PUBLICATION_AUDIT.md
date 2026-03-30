# Publication Audit

## Purpose

This file tracks the trust audit of publication records in `site/data/researchers.json`.

The goal is not just to keep every record structurally valid. The goal is to reduce the risk of:

- misattributed publications
- irrelevant publications attached to the wrong researcher
- fragile or broken URLs
- search-result links that should be replaced with direct publisher, repository, or library pages

## Audit Approach

### High-risk signals

- publication has no DOI
- publication URL is a Google Scholar query
- publication URL is a weak fallback such as a generic bookseller, Google Books, or ResearchGate page
- publication is a book, thesis, chapter, or regional publication where authorship is harder to verify automatically
- `is_first_author` is asserted on a non-DOI or weak-link record where author order has not been independently checked

### Preferred link order

1. DOI landing page
2. Official publisher page
3. Institutional repository or journal page
4. Stable library/catalog page
5. Google Scholar query only as a last fallback

## Resolved During Audit

- Removed a misattributed Vázquez publication:
  - `The agrobusiness of soya in Paraguay: the contradictions of a development model`
- Corrected Vázquez `is_first_author` on:
  - `La frontera argentino-paraguaya ante el espejo. Porosidad y paisaje del Gran Chaco y del Oriente de la República del Paraguay`
- Repaired and strengthened several Dasso links
- Replaced multiple shared Google Scholar fallbacks with direct DOI, publisher, repository, or library URLs
- Replaced many low-effort Scholar links that already had DOIs with direct DOI landing pages

## Current Snapshot

As of 2026-03-27 after the latest audit pass:

- Researchers: **177**
- Publications: **1052**
- Publications without DOI: **139**
- Google Scholar fallback URLs still remaining: **60**

## Highest-Risk Profiles Still To Audit

- Morello, Jorge H.
- Silvetti, Felícitas
- Caceres, Daniel Mario
- Krapovickas, Julieta
- Paolasso, Pablo
- Bazoberry Chali, Oscar
- Dasso, María Cristina
- Adámoli, Jorge
- Altrichter, Mariana
- Araujo-Murakami, Alejandro

## Under-Covered Profiles Queue

Use `python3 scripts/report_undercovered_profiles.py` to identify profiles that may
have too few Chaco publications listed relative to their known body of work.

Current examples already confirmed as under-covered and expanded during this pass:

- Weiler, Andrea
- Canova, Paola
- Díaz, Sandra Myrna
- Cantero, Nicolás
- Cabido, Marcelo Rubén
- Matteucci, Silvia Diana
- Bucher, Enrique H.
- Kunst, Carlos

## Notes

- Many remaining records are older books, edited volumes, local journals, or institutional publications with no DOI.
- For these cases, a stable catalog or repository page can still be a trustworthy improvement over a search-result link.
- Treat live link checks and researcher webpage checks as part of normal intake, not just late-stage cleanup.
- Use `python3 scripts/report_publication_audit.py` to refresh the current risk summary.
- Use `python3 scripts/report_first_author_audit.py` to identify first-author claims that still need manual verification.
- Use `python3 scripts/report_link_health.py --include-webpages` to check live URL and DOI resolution.
- Use `python3 scripts/report_webpage_audit.py` to flag likely researcher-webpage mismatches.
