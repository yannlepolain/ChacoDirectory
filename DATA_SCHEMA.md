# Chaco Researcher Directory Data Schema

## Goal

This document defines the canonical data contract for `site/data/researchers.json`.

The aim is not to describe every historical variant that exists in the dataset. The aim is to define the shape that application code and future maintenance scripts should target.

## Top-Level Dataset

- File: `site/data/researchers.json`
- Type: array of researcher objects
- Constraint: each researcher must have a unique `id`

## Researcher Object

### Required fields

These fields should exist on every researcher record.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable slug used in profile URLs |
| `name` | string | Display name, usually publication-style |
| `affiliation` | string | Current or latest relevant research affiliation; empty string allowed |
| `country` | string | Affiliation country; empty string allowed only temporarily |
| `webpage` | string | URL or empty string |
| `email` | string | Public contact email or empty string |
| `deceased` | boolean | Whether the researcher is deceased |
| `disciplines` | array of strings | 1-2 broad disciplinary labels when known |
| `themes` | array of strings | Broad controlled-vocabulary themes |
| `keywords` | array of strings | More specific topical keywords |
| `geographical_focus` | array of strings | Regions, countries, provinces, or cross-border areas relevant to Chaco work |
| `scales` | array of strings | Research scales such as `local`, `regional`, `landscape` |
| `research_description_en` | string | English description; expected on every record |
| `research_description_es` | string | Spanish description; may be temporarily empty during enrichment |
| `publications` | array of publication objects | Main Chaco-relevant publication list |
| `tags_from_seed` | array of strings | Historical extraction tags retained for compatibility/search |
| `top_collaborators_from_seed` | array of strings | Historical seed-derived collaborator list |
| `main_collaborators` | array of strings | Curated collaborator list; may be empty |
| `fieldwork_locations` | array of strings | Curated fieldwork locations; may be empty |

### Optional fields

These fields are valid when present, but application logic should not require them.

| Field | Type | Notes |
| --- | --- | --- |
| `orcid` | string | ORCID identifier or empty string |
| `year_range` | string | Activity range for display |
| `selected_publications` | array of publication objects | Optional curated subset for profile display |
| `thematic_focus` | array of strings | Legacy field from earlier data model; preserve for compatibility if present |
| `total_publications_in_seed` | integer | Legacy seed-ingestion metric |
| `first_author_publications` | integer | Legacy seed-ingestion metric |

## Publication Object

### Required fields

| Field | Type | Notes |
| --- | --- | --- |
| `title` | string | Publication title |
| `year` | string | Four-digit year |
| `journal` | string | Journal, book, or source title; empty string allowed |
| `is_first_author` | boolean | Authorship flag verified from source data |

### Optional fields

| Field | Type | Notes |
| --- | --- | --- |
| `title_es` | string | Spanish display title when the source record has a distinct Spanish title |
| `doi` | string | DOI string only, with no `https://doi.org/` prefix |
| `url` | string | Fallback link when DOI is not available |

## Controlled Data Rules

### DOI rule

- `doi` stores the DOI string only
- `url` is the fallback when no DOI exists

### Bilingual title rule

- use `title_es` when a publication needs a distinct Spanish UI title
- keep `title` as the canonical stored title unless there is a strong reason to invert that choice

### Theme rule

`themes` should only use the 12 approved terms:

- `Ecology & Biodiversity`
- `Land Use & Deforestation`
- `Wildlife & Conservation Biology`
- `Social Sciences & Political Ecology`
- `History, Culture & Identity`
- `Regional Geography`
- `Climate, Carbon & Energy`
- `Land Tenure & Governance`
- `Hydrology & Soils`
- `Remote Sensing & Monitoring`
- `Agroecology & Rural Development`
- `Public Health & Disease Ecology`

### Uniqueness rules

- `id` must be unique across researchers
- `name` should also be unique in practice

## Interpretation Notes

- `themes` is the canonical broad thematic taxonomy
- `keywords` is the canonical fine-grained topical taxonomy
- `keywords` should follow the alias and review rules in `config/keyword_taxonomy.json`
- `thematic_focus` should be treated as a legacy compatibility field, not the primary taxonomy
- `selected_publications` is optional because many profiles rely on `publications` only
- empty strings are acceptable for incomplete text/URL fields during curation, but missing keys are not acceptable for required fields

## Current Follow-Up From This Schema

- Normalize records so all required fields are present on every researcher
- Decide whether to backfill legacy optional fields or remove test expectations that still assume they are universal
- Add validation to catch key drift before editing counts, docs, or app logic
