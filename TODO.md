# Chaco Research Directory — TODO

## Completed (previous sessions)
- [x] "Suggest an update" button → form (like "Suggest a researcher"), not email
- [x] Remove "Principal investigator" label on profiles
- [x] Check for and remove duplicate publications
- [x] Browse page: alphabetical order by default + sort menu (alpha, most recent pub, total pubs)
- [x] Rename website: ChacoMap → Chaco Researcher Map
- [x] "Selected publications" → "Relevant publications", remove count in parenthesis
- [x] Add AI disclaimer on welcome page + about page (with links to correction forms)
- [x] Translate keywords, geographic focus, and scale to Spanish in ES version

## Completed (2026-03-21)
- [x] Expand database from 50 → 98 researchers (663 publications)
- [x] Add DOIs/URLs to all publications (0 missing both)
- [x] Verify is_first_author via CrossRef for new researchers
- [x] Find emails (31/98) and webpages (98/98)
- [x] Add [Link] fallback on profile page for pubs without DOIs
- [x] Rewrite Copilot-generated descriptions (sycophantic → factual)
- [x] Establish end-to-end pipeline: Haiku search → Sonnet profiles → JSON import
- [x] Broaden inclusion criteria (Chaco peoples/places without "Chaco" keyword)
- [x] Rename website: Chaco Researcher Map → Chaco Research Directory
- [x] Fix search crash (null checks for thematic_focus, geographical_focus, tags_from_seed)
- [x] Fix sort label: "Number of publications" → "Number of publications about the Chaco"
- [x] is_first_author audit for all 98 researchers via CrossRef (~36 corrections)
- [x] Find publications for zero-pub researchers (Villar: 6, García: 5)
- [x] EN/ES description reconciliation (28 fixes: wrong institutions, missing facts, truncations)
- [x] Webpage links cleanup (30 fixes: broken links, 403s, single-paper URLs → ORCID/institutional)
- [x] Publication links: found 40 DOIs for pubs that only had Google Scholar URLs
- [x] ORCID preference for webpages (covered by webpage audit)
- [x] Search autocomplete dropdown on browse page
- [x] Filter checkboxes: first-author publications + published in last 5 years

## Completed (2026-03-22/23)
- [x] Affiliation country filter: reflects current affiliation only (fixed Velilla, Cabral, Campos Krauer)
- [x] About page: updated scope text ("researchers who have conducted research on the Chaco since 2000")
- [x] Biocca: added 3 publications (The Silences of Dispossession + 2 more)
- [x] Morello: added 6 publications (foundational Chaco ecology works 1967–2012, now 9 total)
- [x] Autocomplete now includes keywords and research regions (not just names)
- [x] Added "Discipline" filter dropdown (1-2 disciplines per researcher)
- [x] Renamed "Theme" → "Research Themes" in UI
- [x] Checked for missing research themes across all 98 researchers
- [x] Stricter theme assignment (most researchers now 2-4 themes, down from 6-10)
- [x] Sort label: "Number of publications" (removed "about the Chaco")
- [x] Removed "bioregion" from descriptions, subtitle, and footer
- [x] Research regions filter: grouped by country/cross-border/subnational
- [x] Profile page: publications sorted most recent → oldest
- [x] All dropdown values translated to Spanish (discipline, theme, geo + group labels, affiliation country)

## In Progress
- [ ] Submission forms — Microsoft Forms embed didn't work well, reverted to mailto:. Revisit later.

## Next Batches
- [ ] Continue expanding database (target: hundreds of researchers)
  - Gaps: Bolivian researchers, public health/Chagas, hydrology, demography, rural education
  - Workflow: run a focused researcher-intake pass, for example "find ~30 researchers, focus on X"
  - Candidate queue for later import: see `AUTHOR_EXPANSION_QUEUE.md`
- [ ] Fill main_collaborators + fieldwork_locations for original 50 researchers
- [ ] Fix descriptions re: past affiliations (e.g., Laura Sacchi)

## Future
- [ ] Interactive Leaflet.js map (researcher locations + geographic focus)
- [ ] Activate Spanish content (ES translations ready but not live)
- [ ] Deploy to GitHub Pages
- [ ] Admin workflow for processing submissions
- [ ] Set admin email in site/js/app.js
