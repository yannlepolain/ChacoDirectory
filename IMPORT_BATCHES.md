# Import Batches

This file tracks researcher additions made after the migration to the current
Codex-led workflow.

Its purpose is simple: keep post-migration additions distinguishable from the
legacy dataset so quality can be compared later.

## Baseline

- Baseline date: `2026-03-27`
- Researchers already present before Codex import batches: `177`
- Baseline set: everything already in `site/data/researchers.json` before the
  first batch logged below

## Batch Template

For each new batch, record:

- batch id
- date
- researchers added
- queue source
- notes on lookup / verification quality

## Logged Batches

### Batch 1

- date: `2026-03-27`
- researchers added:
  - `Richard, Nicolas`
  - `Balazote, Alejandro`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - first Codex-added researcher batch after the 177-profile legacy baseline
  - lookup work delegated to smaller agents; final summaries and inclusion
    judgment completed in the main model
  - batch kept intentionally conservative to maximize comparability with the
    legacy Claude-era imports

### Batch 2

- date: `2026-03-27`
- researchers added:
  - `Paz, Raúl Gustavo`
  - `Jara, Cristian Emanuel`
  - `Brassiolo, Miguel Marcelo`
  - `Tamburini, Daniela María`
  - `Lipoma, María Lucrecia`
  - `Lenton, Diana Isabel`
  - `Salamanca, Carlos`
  - `Buliubasich, Emiliana Catalina`
  - `Bonetti, Carlos Alberto`
  - `Boaglio, Gabriel Iván`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - lookup work delegated in grouped, low-cost batches; final inclusion
    judgment, tagging, and EN/ES summaries completed in the main model
  - batch favors strong Chaco fit over filling every user-suggested name
  - one live webpage correction applied after audit: `Paz, Raúl Gustavo`

### Batch 3

- date: `2026-03-27`
- researchers added:
  - `Leoni, María Silvia`
  - `Peña-Chocarro, María del Carmen`
  - `Suárez, Mauricio Aníbal`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - batch continued after revision of Batch 2 weak points
  - `José Zanardini` was reviewed but deferred because the quick publication
    trace was still too book-catalog heavy for a clean import
  - summaries and final inclusion judgment completed in the main model

### Batch 4

- date: `2026-03-27`
- researchers added:
  - `Escalada, Cecilia Soledad`
  - `Cosso, Pablo Esteban`
  - `Olmedo, Sofía Irene`
  - `Cardini, Laura Ana`
  - `Busscher, Nienke`
  - `Zanardini, José`
  - `Grünewald, Leif`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - batch completed the follow-on review set after Batch 3
  - `José Zanardini` was re-checked in a second pass and included despite a
    book-heavy record because the Chaco fit is direct and sustained
  - `Xavier Albó`, `Ruth Alison Benítez`, `Kathia Ruiz Acha`, `Elena Belli`,
    `Juan Manuel Engelman`, and `Ricardo Slavutsky` were examined but not
    imported in this pass

### Batch 4

- date: `2026-03-27`
- researchers added:
  - `Escalada, Cecilia Soledad`
  - `Cosso, Pablo Esteban`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - both were imported after a second-pass review of the frontier social-science
    queue
  - `Escalada` leans ecological/rural-development
  - `Cosso` leans anthropology/history of religion and territoriality

### Batch 5

- date: `2026-03-28`
- researchers added:
  - `Albó, Xavier`
  - `Belli, Elena`
  - `Engelman, Juan Manuel`
  - `Valverde, Sebastián`
  - `Magliocca, Nicholas`
  - `Oakley, Luis J.`
  - `Longhi, Fernando`
  - `Gómez-Valencia, Bibiana`
  - `Vale, Laura M.`
  - `Breithoff, Esther`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - batch imported with local-only editing and a duplicate-signature guard in
    `scripts/validate_researchers.py` to prevent variant re-imports
  - publication links were checked in a focused pass and one broken URL was
    replaced (`Belli, Elena`)
  - several thin-fit profiles from the same intake were removed in a later
    review pass rather than retained with padded summaries
  - `Kathia Ruiz Acha` remains deferred pending stronger publication trace

### Batch 6

- date: `2026-03-28`
- researchers removed after post-import review:
  - `Slavutsky, Ricardo`
  - `von Bernard, Tamara`
  - `de Bremond, Ariane`
  - `Ellicott, Evan`
  - `Benítez, Ruth Alison`
- notes:
  - removed after a stricter review of summary quality and Chaco fit
  - each had either a single edge-case coauthored Chaco paper or too little
    title-level evidence to justify a durable profile
  - retained borderline profiles were rewritten with fuller summaries that
    explain how Chaco work fits within broader research trajectories

### Batch 7

- date: `2026-03-28`
- researchers added:
  - `Boffa, Natalia`
  - `Iñigo Carrera, Valeria`
  - `Matarrese, Marina`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added only after a stricter fit audit confirmed sustained Chaco-centered work
  - `Boffa` and `Matarrese` are strong Chaco-region fits through repeated work on Wichí / Pilagá territorial history and social organization
  - `Iñigo Carrera` was kept because the Formosa / Qom line is substantial rather than a one-off collaboration
  - validation was rerun after the import and the batch was cleaned to remove geography terms from keywords

### Batch 8

- date: `2026-03-28`
- researchers added:
  - `Hecht, Ana Carolina`
  - `Lorenzetti, Mariana`
  - `Censabella, Marisa Inés`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added only after a stricter fit audit confirmed sustained Chaco-centered work
  - `Hecht` was kept for long-term qom / wichí work on indigenous education and language socialization in Chaco and Salta
  - `Lorenzetti` was kept for a sustained Chaco salteño research line on indigenous health, care, and state intervention
  - `Censabella` was kept for long-running work on Gran Chaco languages, qom/toba, and language policy
  - the batch also included a local cleanup of summary tone for `Iñigo Carrera, Valeria` and `Matarrese, Marina`

### Batch 9

- date: `2026-03-28`
- researchers added:
  - `Medina, Mónica Marisel`
  - `Messineo, María Cristina`
  - `Ossola, María Macarena`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after a strict fit pass focused on sustained Chaco work rather than peripheral coauthorship
  - `Medina` was kept for repeated work on qom language practices, bilingual education, and language policy in Chaco
  - `Messineo` was kept for long-term research on qom/toba and other Gran Chaco indigenous languages
  - `Ossola` was kept for sustained work on wichí and qom educational trajectories in Chaco and Salta
  - official personal emails found in source traces were not copied when they were personal rather than institutional

### Batch 10

- date: `2026-03-28`
- researchers added:
  - `Aliata, María Soledad`
  - `Mancinelli, Gloria`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after a strict fit pass focused on sustained Chaco-centered work
  - `Aliata` was kept for repeated work on qom and wichí teachers, socioeducational trajectories, and intercultural bilingual education in Chaco and Salta
  - `Mancinelli` was kept for sustained work on Wichí territoriality, higher education, and intercultural health in the Chaco salteño
  - `Noelia María Enriz` was reviewed in the same pass and not retained because the Chaco-facing work looked collaborative and secondary to a stronger Misiones-centered trajectory

### Batch 11

- date: `2026-03-28`
- researchers added:
  - `Leavy, Pía`
  - `Zurlo, Adriana Alicia`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after a strict fit pass focused on sustained Chaco-centered work
  - `Leavy` was kept for repeated work on child care, nutrition, and indigenous health in Chaco-salteño and Orán contexts
  - `Zurlo` was kept for sustained work on qom/toba linguistics and bilingual schooling in Chaco
  - `Mariana Esther Espinosa` was reviewed in the same pass and not retained because the stronger trajectory looked NOA-wide rather than Chaco-centered

### Batch 12

- date: `2026-03-28`
- researchers added:
  - `Harder Horst, René`
  - `Lamenza, Guillermo Nicolás`
  - `Salceda, Susana Alicia`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after a strict fit pass focused on sustained Chaco-centered work
  - `Harder Horst` was kept for Paraguayan indigenous history, the Chaco War, and state formation in Paraguay
  - `Lamenza` was kept for long-running Chaco Meridional archaeology and Paraguay-Paraná work
  - `Salceda` was kept for the same archaeological cluster, with sustained work on Chaco and adjacent river systems
  - the remaining queue is now limited to lower-confidence second-tier names and one deferred candidate

### Batch 13

- date: `2026-03-28`
- researchers added:
  - `Suárez, María Eugenia`
  - `Kamienkowski, Nicolás Martín`
  - `Arenas Rodríguez, Pastor`
  - `Reyero, Alejandra Paola Yanina`
  - `Guillán, María Isabel`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after a stricter second-wave discovery pass that reopened ethnobotany, visual culture, and border linguistics
  - all five were kept only after confirming a sustained Chaco line rather than one or two peripheral coauthored papers
  - summaries were written locally and kept descriptive, with no rationale-for-inclusion wording
  - `Arqueros, Guadalupe`, `Cantero, José Emanuel`, and `Solís Carnicer, María del Mar` were reviewed in the same pass and excluded as borderline non-core fits
  - one official webpage was added (`Suárez`); no institutional emails were added because none were easy to verify from official person-level sources

### Batch 14

- date: `2026-03-28`
- researchers added:
  - `Córdoba, Gisela Soledad`
  - `Guevara, Aranzazú`
  - `Camardelli, María Cristina`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after a stricter pass over the Chaco Salteño land-degradation cluster
  - `Córdoba` and `Camardelli` were clear long-running fits; `Guevara` was kept because the Chaco Salteño line is substantial even though her broader trajectory extends into dryland plant ecology beyond the Chaco
  - `Castrillo, Silvana Alejandra` was reviewed in the same pass and held back because the visible public publication trace is still thinner than the other three
  - official profile pages were added where a clean person-level CONICET or repository author page was easy to verify; personal yahoo/gmail/hotmail addresses listed on group pages were not copied

### Batch 15

- date: `2026-03-28`
- researchers added:
  - `Maertens, Michiel`
  - `De Lannoy, Gabriëlle J. M.`
  - `Vincent, Frederike`
  - `Vanacker, Veerle`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after a stricter pass over the Dry Chaco salinity / land-surface modeling cluster
  - all four were kept because the Chaco line repeats across journal and conference outputs and is more than a single shared paper
  - `Maertens` and `Vincent` were treated as narrower but still substantial Chaco-focused lines grounded in the same multi-output research program
  - current affiliation was updated for `Vanacker` to Wageningen University & Research based on the official profile page rather than older paper affiliations
  - a clean official staff page and institutional email were added only for `De Lannoy`; no speculative contact fields were added for the others

### Batch 16

- date: `2026-03-28`
- researchers added:
  - `Cuyckens, Griet An Erica`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after a strict second-tier review rather than as part of the main queue, because her broader trajectory extends well beyond the Chaco
  - kept because the Chaco line is still substantive: Dry Chaco conservation planning, Mountain Chaco mammal restoration, and species-distribution work under land-use change
  - `Reimer`, `Núñez Cobo`, and `Smeenk` were reviewed in the same pass and not retained because the visible Paraguayan salinity trace remained too thin and coauthorship-driven
  - `Castrillo`, `Glatzle`, and `Musálem` were left unresolved at the end of that pass

### Batch 17

- date: `2026-03-28`
- researchers added:
  - `Glatzle, Albrecht`
  - `Musálem, Karim`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after an explicit scope update from the user to include more agronomic profiles when the land-use component is substantial enough
  - `Glatzle` was imported as an applied but sustained Paraguayan Chaco profile focused on pastures, groundwater salinity, and land-use change
  - `Musálem` was imported as an applied environmental profile spanning ecosystem services, sustainability assessment, and groundwater salinity across the Paraguayan Chaco
  - the previous second-tier decision on `Musálem` was intentionally overridden by the updated inclusion rule

### Batch 18

- date: `2026-03-28`
- researchers added:
  - `Laino, Luis Domingo`
  - `Laino, Rafaela`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after an agronomy-focused saturation search surfaced a small Paraguayan Humid Chaco production / conservation cluster
  - `Luis Domingo Laino` was kept for a sustained line on agricultural economics, conservation-compatible ranching, and productive landscapes in the Paraguayan Chaco
  - `Rafaela Laino` was kept for sustained ecohydrology, biodiversity, and forest-island work in the Humid Chaco
  - `Merenciano González, Ana María` and `Caballero-Gini, Andrea` remain in the queue as thinner hold cases

### Batch 19

- date: `2026-03-28`
- researchers added:
  - `Merenciano González, Ana María`
  - `Caballero-Gini, Andrea`
- queue source:
  - `AUTHOR_EXPANSION_QUEUE.md`
- notes:
  - added after a user-directed decision to include the remaining Paraguayan Humid Chaco hold cases
  - `Merenciano González` was imported despite a relatively small visible publication trace because the work is directly centered on ecosystem-based management in the Humid Chaco
  - `Caballero-Gini` was imported for recurring Humid Chaco biodiversity, camera-trap, and forest-island work, while noting that her broader trajectory extends beyond the Chaco
  - this pass effectively exhausts the current active queue

### Batch 20

- date: `2026-03-28`
- researchers added:
  - `Glauser, Marcos`
- queue source:
  - direct user request
- notes:
  - added after a direct user instruction to include Marcos Glauser from Paraguay
  - profile anchored on sustained Chaco work on indigenous territoriality, deforestation, land-use change, and political ecology in the Paraguayan Chaco
  - no person-specific official webpage or institutional email was added because a clean official source was not quickly verifiable

### Batch 21

- date: `2026-03-28`
- researchers added:
  - `Chacoff, Natacha Paola`
  - `Galetto, Leonardo`
  - `Calviño, Ana Alejandra`
  - `Ashworth, Lorena`
  - `Aguilar, Ramiro`
  - `Powell, Priscila Ana`
  - `Banegas, Natalia R.`
  - `Viruel, Emilce`
- queue source:
  - focused `IER Tucumán` / `IMBIV Córdoba` / `IIACS-INTA` discovery pass
- notes:
  - added after completing the previously requested institute-based review rather than a general queue sweep
  - the batch combines sustained Chaco Serrano, Dry Chaco, and Chaco Semiárido lines across pollination, fragmentation, vegetation dynamics, carbon stocks, and silvopastoral soils
  - official CONICET person pages were added where a clean person-level profile existed; no speculative emails or generic institute pages were added for the remaining records
  - the batch was normalized and validated locally after import, with no schema errors or warnings
  - this pass reinforces the current saturation reading: the obvious institute-based omissions have now largely been closed

### Batch 22

- date: `2026-03-28`
- researchers added:
  - `Ledesma, Roxana Ramona`
  - `Navall, Jorge Marcelo`
  - `Coria, Rubén Darío`
  - `Gamarra Lezcano, Cynthia Carolina`
  - `Díaz Lezcano, Maura Isabel`
  - `Peralta-Rivero, Carmelo`
  - `Cuellar-Álvarez, Néstor`
- queue source:
  - Ptolemy agronomy-focused discovery pass
- notes:
  - added after the user explicitly approved Ptolemy's strong candidates as worth importing
  - the batch extends agronomy and land-use coverage across western Chaco silvopastoral management in Argentina, soil-focused silvopastoral work in the Paraguayan Chaco, and livestock-sustainability work in the Bolivian Chaco
  - one generic repository browse page for `Navall` was removed after audit; only the remaining cleaner webpage and one easy official institutional email were kept
  - the Paraguayan soil paper was stored once per profile with a Spanish `title_es`, rather than duplicated as separate EN/ES records
  - the batch was normalized and validated locally with no errors or warnings

### Batch 23

- date: `2026-03-28`
- researchers added:
  - `Gómez-Lende, Sebastián`
  - `Gómez, César Abel`
  - `Damborsky, Miryam Pieri`
  - `Ibarra-Polesel, Mario Gabriel`
  - `Solís Neffa, Viviana Griselda`
  - `Via Do Pico, Gisela Mariel`
  - `Orfeo, Oscar`
  - `Carpio, María Belén`
- queue source:
  - direct user suggestions plus focused `UNNE` / `IBONE` / `IIGHI` follow-up scan
- notes:
  - added after a direct user request to check `Sebastián Gómez-Lende`, `César Abel Gómez`, and additional strong-fit profiles at the Universidad Nacional del Nordeste
  - the batch combines Chaco deforestation/political-ecology work, indigenous territorial and linguistic research, Humid Chaco insect ecology, and Chaco plain hydrology/geomorphology
  - weak generic webpage additions were avoided; official CONICET person pages were used where cleanly available, and only one easy institutional email was added (`Ibarra-Polesel`)
  - one non-scholarly media item initially used during drafting was replaced before validation with a stronger repository-backed research output
  - keyword drift introduced by the batch was cleaned locally so validation finished with no errors or warnings and translation coverage returned to the prior baseline

### Batch 24

- date: `2026-03-28`
- researchers added:
  - `de la Cruz, Luis María`
- queue source:
  - direct user request
- notes:
  - added after a direct user instruction to include `Luis María de la Cruz`
  - profile anchored on sustained Gran Chaco work on indigenous territorial rights, participatory monitoring and governance in the Pilcomayo basin, and environmental/legal dimensions of Chaco territorial processes
  - no webpage or email was added because a clean official person-level source was not easy to verify quickly
  - the initial geography-like keyword issue was resolved during normalization, and the final validated record passed with no warnings

### Batch 25

- date: `2026-03-28`
- researchers added:
  - `Rousseau, Antoine`
  - `Capdevila, Luc`
- queue source:
  - direct user request plus focused French-institutions scan (`CNRS`, `CIRAD`, `IRD`)
- notes:
  - added after a targeted pass for French researchers working on the Chaco, with `Antoine Rousseau` requested explicitly by the user
  - `Rousseau` was imported for a sustained Pilcomayo / Gran Chaco environmental-history and borderlands line
  - `Capdevila` was imported for sustained Chaco War and indigenous-history work tied to French academic networks
  - no clean official page was kept for `Rousseau`; `Capdevila` retained a stable institutional page
  - during the same pass, a previously added `Gómez-Lende` webpage was removed after audit because the official link was returning HTTP 502
  - keyword translations introduced by the batch were added locally so translation coverage returned to the previous baseline

### Batch 26

- date: `2026-03-29`
- researchers added:
  - `Colussi, Carlina Leila`
  - `Flores Klarik, Mónica`
  - `Mendicino, Diego Antonio`
  - `Ortega Insaurralde, Carlos`
  - `Renison, Daniel`
  - `Salas Barboza, Ariela Griselda Judith`
- queue source:
  - direct user-requested names plus focused follow-up scans at `UNSa`, `UNC` (non-IMBIV), and `UNL`
- notes:
  - `Mosciaro, María Jesús` was already present in the dataset and was not re-imported
  - `Silvina M. Manrique` was reviewed in the same pass and not retained because the visible Chaco line remained too thin relative to a broader vegetation / paleoenvironment trajectory
  - the batch adds Chaco-salteño land-governance and territorial-conflict work (`Ortega Insaurralde`, `Salas Barboza`, `Flores Klarik`), Chaco Serrano restoration ecology (`Renison`), and southern Gran Chaco Chagas epidemiology (`Mendicino`, `Colussi`)
  - read-only university discovery work was delegated; all dataset writes, summaries, and final inclusion decisions were completed in the main process
  - institutional webpages were kept only when person-level official sources were easy to verify; otherwise webpage/email fields were left blank
