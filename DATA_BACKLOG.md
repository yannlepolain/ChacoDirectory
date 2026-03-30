# Data Backlog

## Current Priority

The dataset now validates structurally with `0` errors. The remaining cleanup work is content-oriented.

## Open Warning Class

At present, the canonical validator reports **0 warnings**.

The missing-link class that existed on 2026-03-27 was cleared by adding fallback Google Scholar title-query URLs where neither DOI nor URL was available.

## Current Monitoring Focus

- Replace Google Scholar fallback links with more stable publisher, repository, or institutional URLs when better sources are found
- Continue improving sparse metadata such as emails, collaborators, and fieldwork locations
- Continue discovering stable researcher profile pages for the remaining blank `webpage` fields
  Current state on 2026-03-27: `35` researchers still have no verified profile page

## Notes

- Many of these are likely older regional publications, books, chapters, or local journals where a DOI may not exist.
- For these cases, a stable fallback URL is still valuable.
- Use `python3 scripts/report_missing_links.py` to confirm whether any no-link records reappear after future edits.
