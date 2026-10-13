# FloodPath-Care Blueprint

Flood-Aware Ambulance and Maternal Facility Reachability: Prototype Engineering PRD and Single Source of Truth for Claude Code

**Version 2.1 FINAL (Seva First Innovation Challenge prototype: dashboard interface, English, Tamil and Hindi, isolation-priority extra view).** Supersedes Version 1.1 in place (a backup of 1.1 is kept as `blueprint_v1.1_backup.md`). The core product and data design are unchanged. Version 2.0 replaces the interface specification with a dashboard modelled on a supplied reference image (Section 6), adds English, Tamil and Hindi support (Section 6A), and keeps the extra, lower-priority view from Version 1.1: a ranking of neighbourhoods by estimated people in flood-isolated areas (Sections 3.8-3.9, 4.11, 5.7, 6.8, 13.6, PHASE 8). The format follows the Worksetu reference blueprint (document control, verification legend, priority classes, per-feature specifications, phase-gated build order, consistency audit, acceptance checklist).

**Product:** a software-only geospatial decision-support tool that compares conventional shortest-path ambulance routing with flood-aware routing to maternal-care facilities, replaying the Chennai 2015 floods from public data. An extra view ranks wards by the estimated number of people whose road access to any suitable facility is lost or badly delayed under each scenario. It is built only after the core passes (Section 14, PHASE 8).

**Target stack:** Python 3.11 · OSMnx · NetworkX · GeoPandas · Shapely · NumPy · pandas · Streamlit · streamlit-folium (Folium) · pytest, with Altair (installed with Streamlit) for charts and custom CSS for the dashboard theme. No database, no Docker, no LLM calls, no custom JavaScript components. This is a **real, working geospatial analysis system** that runs on real public data and clearly labelled simulated inputs. It is not a mockup, and it is not a live dispatch system.

**Time budget:** about 17.5 hours for the full core (phase times total 16.5 hours, plus about 1 hour for six preview checkpoints; PHASE 0 to PHASE 7 and PHASE 9 to PHASE 12), plus about 1.5 hours for the optional isolation view (PHASE 8). That is more than one working day. **One-day cut line:** build PHASE 0 to PHASE 7, a reduced PHASE 9, PHASE 10, and in PHASE 11 only cards C1 and C2, the Route explorer, and the Data and limits page; translate exactly the Section 6A.3 dictionary (it covers every string on those pages); skip PHASE 8; hold only three previews (after PHASE 3, PHASE 7 and PHASE 11); and record the demo in English with a short Tamil and Hindi switch. Everything cut is listed as planned work in the README.

**Stack change (Version 3.0, user decision 2026-10-13):** the interface is now a **Next.js** app in `web/` (Next.js 16, React 19, TypeScript, Tailwind), replacing Streamlit. Python keeps all analysis and writes precomputed JSON and GeoJSON into `web/public/data/`; the web app only reads those files (no API server). Wherever this document says Streamlit, `st.*`, `ui_theme.py`, `ui_components.py`, `charts.py` or `app.py`, read the Next.js equivalent in Section 6.13. The visual style follows the dashboard reference image in a blue palette (Section 6.13). Rules that do not depend on the framework (data, honesty, i18n, metrics, tests T-01 to T-26) are unchanged.

**Preview rule (Version 2.1):** after every second phase Claude Code must run the app, show the user a screenshot or live preview of the current UI/UX, say what is real and what is a placeholder, and wait for approval before continuing (Section 14.12).

**How Claude Code must use this document:** every requirement is stated as a concrete, testable specification (WHAT / WHERE / WHY / INPUT / OUTPUT / DATA / ERRORS / TESTS where applicable), not as a code listing. Sections 5 to 15 are specification-only by design (Section 0.3). Build in the order of Section 14. Do not start PHASE N until PHASE N-1's verification passes and its commit is made. Where this document and a convenient shortcut disagree, follow this document or ask the user.

---

## Table of Contents

0. Section 0: Document Control, Verification Legend, Priority Classes, Claims Policy
1. Section 1: Product Scope, Users, and Journeys
2. Section 2: Data Catalogue and Provenance
3. Section 3: Data Schemas and Validation Rules
4. Section 4: Architecture and Module Contracts
5. Section 5: Algorithms and Metric Definitions
6. Section 6: Dashboard User Interface Specification
   - 6A. Section 6A: Internationalisation (English, Tamil, Hindi) and UI Dictionary
7. Section 7: Explanation Text and Audit Log
8. Section 8: Error Handling and Edge Cases
9. Section 9: Honesty, Misuse, and Risk Model
10. Section 10: Testing Strategy
11. Section 11: Performance and Caching Targets
12. Section 12: Configuration, Repository, and Documentation Requirements
13. Section 13: Claude Code Implementation Rules (Worked Examples)
14. Section 14: Final Implementation Order (PHASE 0 to PHASE 12)
15. Section 15: Demo Script and Recording Checklist
16. Section 16: Consistency Audit Log, Assumptions Register, Acceptance Checklist

---

## Section 0: Document Control, Verification Legend, Priority Classes, Claims Policy

### 0.1 Verification Status Legend

Every requirement is at exactly one state. Claude Code must update the tag when state changes and must never mark a requirement `DEMO-VERIFIED` merely because it was coded.

| Tag | Meaning |
|---|---|
| `SPECIFICATION COMPLETE` | Fully and unambiguously defined here. No code exists. |
| `IMPLEMENTATION REQUIRED` | Specified and must be built. Default state of every requirement as of this version. |
| `DEMO-VERIFIED` | Code exists, its specified tests pass, and it was exercised in the full demo flow (Section 15) on the final build. |

As of this version, **every requirement is `SPECIFICATION COMPLETE` + `IMPLEMENTATION REQUIRED`**. Nothing described here has been built.

### 0.2 Origin of This Specification

This blueprint was produced from a research session that verified public datasets by fetching them (page, API metadata, small files). Where a dataset's contents were not opened, this document says so (Section 2). The research found four unavoidable data gaps (Section 2.3). The design therefore treats **honest labelling** as a first-class requirement, not an afterthought.

### 0.3 Why Sections 5 to 15 Contain No Source Code

Sections 5 to 15 are specifications: prose, tables, and interface shapes (field names, types, return structures), not function bodies. Claude Code implements them directly. Library function names may be cited where a specific API is intended.

### 0.4 Functional Priority Classification (P0 / P1 / P2 / OUT)

Every feature carries exactly one tag. P0 is built first and never cut. P2 is the first thing dropped if time runs out. `OUT` is not built in this pass.

| Feature | Priority | Acceptance criterion |
|---|---|---|
| Road graph for one small Chennai zone | P0 | Graph builds and a shortest path between two nodes is non-empty (Section 4.3) |
| Flood layers loaded with provenance columns | P0 | Each layer has `source`, `date`, `confidence`, `kind`, `scenario` (Section 3.2) |
| Composite observed layer plus 3 simulated scenarios | P0 | Four GeoJSON scenario files exist and are labelled (Section 4.4) |
| Edge classification: passable / at-risk / blocked | P0 | Worked example in Section 5.2 reproduces exactly |
| Baseline vs flood-aware routing | P0 | Route changes when a route edge is flooded; unreachable handled without crash (Section 4.7) |
| Suitable-facility selection by service | P0 | Chosen facility always has the requested service (Section 4.6) |
| Facility file with verification rules | P0 | No `phone_verified` row without `source` and `verified_on` |
| Five metrics per scenario | P0 | Metrics table produced for all four scenarios (Section 5.5) |
| Dashboard shell: title, persistent banner, left rail, header controls (event pill, focus toggle, scenario control, language selector), five KPI cards | P0 | Section 6.2 to 6.5 checks and U-01 to U-15 pass |
| Overview cards C1 (route map) and C2 (coverage by scenario) with "View data" tables | P0 | Section 6.6 |
| Overview cards C3 to C6 | P1 | Section 6.6 |
| Route explorer, Metrics table, and Data and limits pages | P0 | Sections 6.7 and 6.9 |
| Export page (CSV and JSON) | P1 | Section 6.9 |
| Language switch English, Tamil, Hindi for all P0 pages using at least the Section 6A.3 dictionary | P0 | I18N-1 to I18N-14; T-27 to T-35 |
| Complete translation of every remaining string (chart axes, tooltips, table headers) | P1 | Parity tests pass |
| Fluent-speaker review of the critical Tamil and Hindi strings | P1 | `docs/TRANSLATION_REVIEW.md` completed before the recording |
| Narrow-screen (single-column) layout | P2 | Section 6.12 |
| Preview skeleton page in the final layout, built in PHASE 1 and filled in phase by phase | P0 | Section 14.12 |
| UI/UX preview checkpoints after PHASE 1, 3, 5, 7, 9 and 11, each with an approval gate | P0 | Section 14.12 |
| PDF or image export, dark mode, Tamil or Devanagari numerals, personal greetings or accounts, social links | `OUT` | Not built |
| Observed/simulated badge on every layer | P0 | Visible in map legend and data panel |
| Standing limits banner and data panel | P0 | Banner always visible; panel lists all four gaps |
| Explanation text from computed facts | P1 | Text uses only computed values (Section 7.1) |
| Audit log JSON download | P1 | Contains every field in Section 7.2 |
| Robustness analysis (random flood-extent perturbations) | P1 | Deterministic for a fixed seed (Section 5.6) |
| Population coverage with ward weights | P1 | Real weights if ward join passes; labelled placeholder weights otherwise (Section 2.4) |
| Tunnel/underpass flood sensitivity rule | P2 | Off by default; configurable (Section 5.3) |
| Alternative second-best route display | P2 | Shown as secondary dashed line |
| Isolation priority view: per-ward isolated share, estimated people in isolated areas, ranking, map layer, CSV download | P1 | Built only after the core P0 acceptance items pass; reproduces the Section 5.7.5 worked example; tests T-19 to T-26 pass |
| Isolation validation against a hand-compiled list of reported cut-off areas | P2 | Matches and misses reported; no accuracy figure claimed (Section 5.7.6) |
| Shelters or relief centres as destinations (needs geocoding of the 2024 PDF) | P2 | Optional; hospitals and the maternal facility list are the default destinations |
| Optional UNOSAT layers (67 MB zip) | P2 | Only after the user approves the download |
| Live data, live flood prediction, real-time dispatch | `OUT` | Not built; never implied |
| Real 108 ambulance data or response times | `OUT` | Not available publicly; ambulance data is simulated |
| Clinical certification of facilities | `OUT` | Facility lists are a proxy, never certification |
| Multi-city support, mobile apps, model training | `OUT` | Not built |
| Rainfall- or terrain-driven flood prediction; any claim of "predicting which areas will be cut off" | `OUT` | Not built; the tool assesses observed and simulated scenarios only |
| Database, user accounts, Docker, React/Next.js, LLM features | `OUT` | Not built |

### 0.5 Claims Policy (binding on code, UI text, README, and recordings)

| Allowed | Forbidden |
|---|---|
| "Historical-data-informed simulation of flood-aware routing" | "Reconstructs the real 2015 conditions" |
| "Simulated ambulance starts" | "Real 108 ambulance times" or any real response-time claim |
| "Observed composite of available layers" | "The flood extent on 1-4 Dec 2015" |
| "Facility list is a hand-checked proxy for emergency obstetric capability" | "Verified CEmONC/FRU hospital" without evidence |
| "Indicative decision support" | "Predicts floods", "dispatch system", "accurate to N minutes" |
| "Thresholds and buffers are configurable assumptions" | Presenting any threshold as measured or official |
| "Indicative ranking of neighbourhoods by estimated people in isolated areas" | "Predicts which areas will be cut off", "relief dispatch order", "number of people trapped" |
| "Population is assumed spread evenly within a ward" | Presenting ward-level people counts as measured |
| "Tamil and Hindi text are draft translations pending review" | "Professionally translated" or "verified translation" before a reviewer has signed off |
| The simulation and indicative wording kept in every language | Dropping "simulated", "indicative" or "not a prediction" in a translation |

---

## Section 1: Product Scope, Users, and Journeys

### 1.1 Problem Statement (intent preserved)

Develop a software-based geospatial decision-support system that improves emergency ambulance routing and maternal healthcare accessibility during urban flooding. Combine flood extent, road-network data, and healthcare-facility information to estimate route accessibility under different flood scenarios; identify disrupted road segments; calculate alternative routes; assess travel times to clinically appropriate facilities; explain why a destination or route is recommended; support scenario simulations; quantify accessibility change; and evaluate against conventional shortest-path routing using travel-time increase, route feasibility, facility reachability, population coverage, and routing robustness under uncertain flood conditions. Use public data, communicate limits and uncertainty, and provide an auditable interface without custom hardware.

### 1.2 Users

| Role | Need | Primary screens |
|---|---|---|
| Emergency planner | Compare accessibility across flood severities | Scenario selector, metrics panel |
| Dispatch officer | A route and a reason for one emergency | Origin selector, result panel, map |
| Judge / auditor | Verify every claim is honest and traceable | Data and limits panel, audit log |

### 1.3 Journeys

**1.3.1 Planner journey.** Opens the page; reads the banner; selects a scenario; reads the metrics table (travel-time increase, feasibility, reachability, coverage, robustness); compares scenarios in the comparison table; downloads the audit log.

**1.3.2 Dispatcher journey.** Selects a simulated ambulance start or clicks the map; selects the service; sees the baseline route and the flood-aware route; reads the written reason; reads which facilities are unreachable and why.

**1.3.3 Judge journey.** Opens the data and limits panel; sees each dataset's source, date, licence, observed/simulated badge; sees the four standing gaps; downloads the audit log; sees that no facility is shown as verified without a source and date.

**1.3.4 Isolation view journey (extra view).** The planner opens the "Isolation priority" tab; selects a scenario; sees wards coloured by priority with rank labels; reads the top-ranked wards with estimated people in isolated areas, isolated share and delayed share; downloads the ranking as CSV; reads the standing notes that the ranking is indicative, that population is assumed even within a ward, and that the scenarios are not predictions. The tab appears only if the isolation tables were produced (PHASE 8).

**1.3.5 Language journey.** At any point the user selects English, தமிழ் or हिन्दी in the header. Every visible string, including chart titles, legends, tooltips, buttons and download labels, changes at once; facility and ward names stay as in the source data; the simulation banner remains visible in the chosen language; the choice persists across pages and in the page address.

### 1.4 Run State Model

The application has one linear computation pipeline per `(scenario, origin, service)` selection:

`LOAD_DATA -> BUILD_GRAPH -> LOAD_FLOOD(scenario) -> CLASSIFY_EDGES -> MODIFY_GRAPH -> SELECT_FACILITIES(service) -> ROUTE(baseline, flood-aware) -> METRICS -> [ISOLATION(scenario), optional] -> EXPLAIN -> AUDIT`

Each stage has a defined failure mode (Section 8). No stage may fail silently; every failure surfaces a banner in the UI and an entry in the audit log.

### 1.5 Functional Requirement Index

`SPECIFICATION COMPLETE`. The requirement IDs cited in the module specifications resolve here. Every requirement maps to at least one test or checklist item.

| ID | Requirement | Verified by |
|---|---|---|
| FR1 | Build or load the road graph for the study area | Section 4.3 tests |
| FR2 | Load flood layers with provenance columns | T-07 |
| FR3 | Build one composite observed layer and three simulated scenarios, all labelled | T-06, T-07 |
| FR4 | Classify edges passable, at-risk or blocked | T-04 |
| FR5 | The flood-modified graph never mutates the baseline graph | T-05 |
| FR6 | Compare baseline and flood-aware routes; flag a baseline route that crosses a blocked road | T-01 |
| FR7 | An unreachable origin returns `reachable=False` with a reason, never a crash | T-02 |
| FR8 | The chosen facility always offers the requested service | T-03 |
| FR9 | A facility is `phone_verified` only with a source and a `verified_on` date | T-08 |
| FR10 | Compute the five metrics per scenario | T-10 |
| FR11 | Robustness is deterministic for a fixed seed | T-12 |
| FR12 | Explanation text uses only computed facts | T-13 |
| FR13 | The audit log contains every required field | T-14 |
| FR14 | The UI shows the banner, badges, limits panel and audit download | U-01 to U-09 |
| FR15 | (Extra view, P1) Rank wards by estimated people in isolated areas | T-19 to T-26 |
| FR16 | Dashboard pages, five KPI cards and overview cards per Section 6, with a "View data" table for every chart | T-33, T-34, U-01 to U-15 |
| FR17 | English, Tamil and Hindi interface from dictionaries with key and placeholder parity | T-27 to T-32, T-35, U-10 to U-13 |

---

## Section 2: Data Catalogue and Provenance

### 2.1 Source Datasets

All links opened during research on the dates in Section 16.1. "Opened" means the page, API reply, or file was fetched and read; "Not opened" means only listed.

| ID | Dataset | Link | What it provides | Licence note | Research status |
|---|---|---|---|---|---|
| D1 | OpenCity: Chennai Floods 2015 Data | https://data.opencity.in/dataset/chennai-floods-2015-data | Seven KML files: GCC stagnation locations, crowd-sourced flooding locations, GCC area flood hotspots, Tiruvallur/Vellore/Kancheepuram hotspots, floods inundation zone per NRSC | Dataset tagged Public Domain; the portal's About page states CC BY-NC-SA 4.0 and ODbL. Cite OpenCity and the original sources | Dataset page and API metadata opened; only the Vellore KML (29 points) opened |
| D2 | OpenCity: Chennai flooding data | https://data.opencity.in/dataset/chennai-flooding-data | Inundation depth points, 2015 flooding points, return-period flow layers, flood hazard zones map (39.9 MB) | Public Domain tag | Page opened; files not opened |
| D3 | UNOSAT / HDX: flood waters over Chennai, 2015 | https://data.humdata.org/dataset/geodata-of-flood-waters-over-chennai-area-tamil-nadu-state-india-december-04-2015 | Sentinel-1 flood layers for 12 and 24 Nov 2015; a pre-flood layer; 67 MB zip. There is **no layer for the 1-4 Dec peak** despite the "4 Dec" label | CC BY-NC-SA 3.0 (non-commercial, share-alike) | Zip file list read; geometry, fields, CRS not read |
| D4 | OpenStreetMap | via OSMnx; also https://download.geofabrik.de/asia/india/southern-zone-latest.osm.pbf (558 MB) | Current road network | ODbL; credit OpenStreetMap contributors | Counts queried (93,182 road ways in the Chennai bounding box); graph not built |
| D5 | OpenCity: Chennai health centres | https://data.opencity.in/dataset/chennai-healthcare-uphcs-and-uchcs | "Chennai Maternity Hospitals Map" KML: 5 GCC 24x7 emergency obstetric units with coordinates (Shenoy Nagar, Saidapet, Thoraipakkam, Mugalivakkam, Purasaiwalkam) | Public Domain tag | KML opened and parsed |
| D6 | NHM Tamil Nadu CEmONC list | https://www.nhm.tn.gov.in/sites/default/files/documents/CEmONC98.pdf | 4 Chennai CEmONC hospital names, undated, no coordinates (Kilpauk Medical College Hospital; RSRM Lying-in Hospital (Stanley); Institute of Obstetrics and Gynaecology (MMC, Egmore); Kasturba Gandhi Hospital for Women and Children) | Public document | PDF read |
| D7 | OpenCity: Chennai census 2011 | https://data.opencity.in/dataset/chennai-census-2011-data | Ward-level population, 155 wards | Public Domain tag | Metadata opened |
| D8 | DataMeet: Chennai municipal spatial data | https://github.com/datameet/Municipal_Spatial_Data/tree/master/Chennai | Ward polygons, 201 features | CC BY-SA 2.5 India | Readme opened; join with D7 untested |
| D9 | OpenCity: GCC relief centres | https://data.opencity.in/dataset/gcc-relief-centres | A 2024 PDF list; needs geocoding | Public Domain tag | Metadata opened; PDF not parsed. Optional destination layer (P2) |

### 2.2 Data Governance Rules

- DATA-1. Every flood feature and every facility row carries `source` (a dataset ID from the table above or a named URL) and a date field.
- DATA-2. Every dataset is recorded in `SOURCES.md` with ID, URL, licence, access date, attribution text.
- DATA-3. Raw third-party files live in `data/raw/` and are gitignored. The repository commits download scripts, not data. UNOSAT (D3) is non-commercial and share-alike and must never be committed.
- DATA-4. No single download may exceed 100 MB without explicit user approval. D3 and the full OSM PBF are not downloaded in the default build.
- DATA-5. Simulated data carries `kind=simulated` (flood) or `label=simulated` (ambulance starts), always, in the file and in the UI.
- DATA-6. When a source's contents differ from this table (different fields, geometry, or CRS), log the difference and continue only if the code can handle it; otherwise raise `DATA_SHAPE_UNEXPECTED` (Section 8). Never substitute invented data.

### 2.3 Standing Data Gaps (must be shown in the UI and README)

1. No public verified list of FRU/CEmONC facilities with coordinates exists for Chennai. The facility list is a hand-checked proxy.
2. No 108 ambulance station, call, or response-time data is public. All ambulance starts and times are simulated.
3. No open flood extent exists for the 1-4 Dec 2015 peak. The observed scenario is a composite of available layers.
4. No open Chennai flood extent was found for Cyclone Michaung (2023) or Cyclone Fengal (2024). Out of scope here.

Additional standing limits: current OSM roads differ from 2015 roads; radar and crowd-sourced data can miss flooded streets in dense areas; the OpenCity licence statements conflict.

### 2.4 Ward-Join Risk and Fallback

D7 has 155 wards and D8 has 201 features, so they may use different ward schemes. PHASE 1 must test the join on ward identifier and on normalised ward name, and log the match rate.

- **If at least 90% of D7 wards match a D8 polygon:** use real ward population weights; log the unmatched wards in `docs/DATA_LIMITS.md`.
- **Otherwise:** assign every origin an equal `population_weight` and display the notice "Population weights are placeholders (ward join failed). Coverage is a share of sample points, not of people." Never present placeholder coverage as population coverage.

(The 90% cut-off is an assumption, A-12 in Section 16.2.)

The isolation view (Section 5.7) groups road nodes into units. Its population basis follows the same rule: real ward weights if the join passes, placeholders otherwise. If the ward polygons (D8) cannot be loaded at all, use square grid cells of `ISOLATION_FALLBACK_GRID_M` metres as units, with placeholder population weights and the same notice. A grid unit is named `Zone r{row}c{col}` and is never called a ward.

---

## Section 3: Data Schemas and Validation Rules

### 3.1 Files

All files live under `data/processed/` unless stated. Validation is enforced at load time and in tests.

### 3.2 Flood Layers (`flood_observed.geojson`, `flood_mild.geojson`, `flood_moderate.geojson`, `flood_severe.geojson`)

| Field | Type | Rule |
|---|---|---|
| `geometry` | Polygon / MultiPolygon, EPSG:4326 | Valid, non-empty. Points from D1 are buffered into polygons before storage |
| `source` | string | A dataset ID such as `D1` |
| `date` | string | Observation date or `unknown` |
| `confidence` | enum `low`, `medium`, `high` | Crowd-sourced and buffered points are `low`; the NRSC inundation zone is `medium` unless contradicted |
| `kind` | enum `observed`, `composite`, `simulated` | Composite for the union of observed layers; simulated for scenarios |
| `scenario` | enum `observed`, `mild`, `moderate`, `severe` | Matches the filename |

### 3.3 `facilities.csv`

Columns: `facility_id, name, latitude, longitude, service, tier, verification_status, source, verified_on, notes`

| Field | Rule |
|---|---|
| `facility_id` | Unique, stable (for example `F01`) |
| `service` | `emergency_obstetric` or `unknown` |
| `tier` | `A` (name from NHM CEmONC list, geocoded), `B` (GCC 24x7 unit with coordinates), `D` (OSM hospital with maternity-type name) |
| `verification_status` | `unverified`, `source_listed`, `phone_verified` |
| Rule V-1 | `phone_verified` requires non-empty `source` and a valid `verified_on` date. The facility loader raises `FACILITY_VERIFICATION_INVALID` otherwise |
| Rule V-2 | A row with `service = unknown` is never offered as a suitable facility |
| Starter rows | Tier B: the 5 GCC units with D5 coordinates. Tier A: the 4 NHM names geocoded from OSM and marked `unverified` until phoned |

### 3.4 `ambulance_starts.csv`

Columns: `start_id, latitude, longitude, label`. `label` must equal `simulated` on every row; the loader raises `AMBULANCE_LABEL_INVALID` otherwise.

### 3.5 `origins.csv` (demand points for metrics)

Columns: `origin_id, node_id, latitude, longitude, ward_id, population_weight`. Generated by `src/facilities.py` or `src/metrics.py` from seeded random graph nodes (Section 5.5). `population_weight` is from ward data or placeholder 1.0.

### 3.6 `wards_population.csv`

Columns: `ward_id, ward_name, population, source_year` (source year `2011`).

### 3.7 `roads.graphml`

An OSMnx graph with edge attributes `length` (m), `speed_kph`, `travel_time` (s), plus node coordinates. Cached after first build.

### 3.8 `reported_isolated_areas.csv` (optional, in `data/reference/`)

Columns: `area_name, source_url, source_date, unit_id (optional), notes`. Hand-compiled from news reports of areas that were cut off in the replayed event. Every row must have a `source_url` and a `source_date`; a row without them raises `REFERENCE_ROW_INVALID` and is rejected. This file is the only validation reference for the isolation view. It is incomplete by nature, and its absence is not an error.

### 3.9 Isolation output table (`isolation_<scenario>.csv`)

| Column | Meaning |
|---|---|
| `unit_id`, `unit_name` | Ward (or `Zone r{row}c{col}` in the fallback) |
| `population` | Ward population (census 2011) or placeholder weight |
| `population_basis` | `ward_census_2011` or `placeholder` |
| `nodes_total`, `nodes_eligible` | Road nodes in the unit; those not baseline-disconnected |
| `nodes_baseline_disconnected` | Count excluded because no suitable facility is reachable even without flooding (a data issue, not flood isolation) |
| `nodes_isolated`, `nodes_delayed` | Counts per Section 5.7.2 |
| `isolated_share`, `delayed_share` | `I_u` and `D_u` (Section 5.7.3) |
| `estimated_people_isolated` | `population * isolated_share`; never greater than `population` |
| `priority_score`, `rank` | Section 5.7.4 |
| `scenario`, `kind` | Scenario name and its `kind` (observed composite or simulated) |

### 3.10 `i18n/{lang}.json`

Flat map of dotted keys to strings for `en`, `ta`, `hi`, plus a `_meta` block (`language`, `status` = `draft` or `reviewed`, `reviewed_by`, `reviewed_on`). Same key set and same placeholders in all three files (I18N-3, I18N-4). Initial content: Section 6A.3. Strings contain no pipe characters and no raw HTML.

---

## Section 4: Architecture and Module Contracts

### 4.1 Architecture

A single Python process. Data files in, Streamlit page out. No services, no network calls at runtime except the first-time OSMnx download, which is cached.

Module chain: `config` -> `i18n` -> `fetch_data` -> `roads` -> `flood` -> `impact` -> `facilities` -> `route` -> `metrics` -> `isolation` (optional) -> `explain` -> `audit` -> `ui_theme` -> `charts` -> `ui_components` -> `app`.

### 4.2 Directory Layout

```
floodpath-care/
  CLAUDE.md
  README.md
  SOURCES.md
  requirements.txt
  config.py
  app.py
  docs/DATA_LIMITS.md
  data/raw/            (gitignored)
  data/processed/
  data/reference/      (reported_isolated_areas.csv, optional)
  i18n/                (en.json, ta.json, hi.json)
  assets/fonts/        (optional, only with approval)
  src/ fetch_data.py roads.py flood.py impact.py facilities.py route.py metrics.py isolation.py explain.py audit.py i18n.py ui_theme.py charts.py ui_components.py
  tests/ conftest.py test_*.py (including test_i18n.py and test_dashboard_data.py)
  logs/
```

### 4.3 Module: `roads` (build the road graph)

- **WHAT:** build or load the drivable road graph for the study area.
- **WHERE:** `src/roads.py`.
- **WHY:** all routing depends on it (FR1).
- **INPUT:** `STUDY_AREA` from config, as a place name or polygon (never a bounding-box tuple; OSMnx argument order has changed between versions).
- **OUTPUT:** a NetworkX MultiDiGraph in EPSG:4326 with `speed_kph` and `travel_time` on every edge; cached as `roads.graphml`.
- **DATA:** OSM via Overpass, requires a User-Agent header; cached after the first build.
- **ERRORS:** `GRAPH_BUILD_FAILED` (network, rate limit, empty area), `GRAPH_TOO_LARGE` (more than 150,000 edges: ask the user to shrink the zone).
- **TESTS:** graph is non-empty; a shortest path between two sampled nodes is non-empty; every edge has a positive `travel_time`; reloading from cache gives an identical node count.

### 4.4 Module: `flood` (layers and scenarios)

- **WHAT:** load flood layers, build the composite observed layer, build simulated scenarios.
- **WHERE:** `src/flood.py`.
- **WHY:** FR2, FR3. The observed/simulated distinction is central to credibility.
- **INPUT:** D1 KML files in `data/raw/`; config buffer values.
- **OUTPUT:** four scenario GeoJSON files with the Section 3.2 columns.
- **DATA:** in EPSG:32644 for geometry operations; stored in EPSG:4326. Points are buffered by `POINT_BUFFER_M`; polygons are used as given.
- **Rules:**
  - The observed composite is the union of the NRSC inundation zone and the buffered flooding and stagnation points, labelled `kind=composite`, `confidence=low` for any buffered-point component.
  - Scenarios mild, moderate, severe are the composite buffered by `SCENARIO_BUFFER_M[scenario]`, negative values shrinking the extent. They are labelled `kind=simulated`.
- **ERRORS:** `NO_FLOOD_DATA_FOR_AREA` (no flood feature intersects the study area); `DATA_SHAPE_UNEXPECTED` (a KML has a geometry type the loader cannot handle).
- **TESTS:** every output has all Section 3.2 columns with valid enum values; the severe polygon area is greater than or equal to the observed composite, which is greater than or equal to the mild polygon area; the geometries are valid.

### 4.5 Module: `impact` (edge classification and graph modification)

- **WHAT:** classify each road edge by how much of it lies inside the flood polygon, then produce a flood-modified copy of the graph.
- **WHERE:** `src/impact.py`.
- **WHY:** FR4, FR5. Identifies disrupted road segments.
- **INPUT:** the graph and one scenario GeoDataFrame.
- **OUTPUT:** a table `edge_id, flooded_fraction, class` and a new graph `G2` (the original graph is never mutated).
- **Rules:** see Section 5.2 for the classification and cost rules.
- **ERRORS:** `EDGE_GEOMETRY_MISSING` (an edge with no geometry is treated by a straight line between its nodes, and the count is logged).
- **TESTS:** the Section 5.2 worked example reproduces; `G2` differs from `G` only in blocked-edge removal and at-risk cost changes; the original graph is unchanged after the call.

### 4.6 Module: `facilities` (facility and origin handling)

- **WHAT:** load and validate `facilities.csv`, filter by service, snap facilities and origins to graph nodes.
- **WHERE:** `src/facilities.py`.
- **WHY:** FR8, FR9. Facilities must be clinically appropriate and honestly labelled.
- **INPUT:** facilities CSV, graph, service name, `INCLUDE_UNVERIFIED_FACILITIES` flag.
- **OUTPUT:** a table of suitable facilities with snapped `node_id` and snapping distance in metres.
- **Rules:** rows with `service = unknown` are excluded (V-2); snapping distances above `MAX_SNAP_DISTANCE_M` raise a warning and exclude that facility from routing; if the include-unverified flag is false only `phone_verified` and `source_listed` rows are kept.
- **ERRORS:** `FACILITY_VERIFICATION_INVALID`, `NO_SUITABLE_FACILITY` (none left after filtering), `FACILITY_NOT_SNAPPABLE`.
- **TESTS:** V-1 enforced; unknown-service rows never returned; a facility farther than the snap limit is excluded and reported.

### 4.7 Module: `route` (baseline and flood-aware routing)

- **WHAT:** for an origin node, compute (a) the baseline route on the unmodified graph and (b) the flood-aware route on the modified graph, to the nearest suitable facility by travel time; also identify unreachable facilities and whether the baseline route is drivable in the flood scenario.
- **WHERE:** `src/route.py`.
- **WHY:** FR6, FR7. This is the core comparison.
- **INPUT:** `G`, `G2`, origin node, suitable-facilities table, the edge classification table.
- **OUTPUT (structure):** `facility_id`, `path_nodes`, `time_min`, `reachable` (bool), `baseline_facility_id`, `baseline_time_min`, `baseline_blocked_edges` (the baseline path's edges that are blocked in this scenario), `baseline_drivable` (bool), `unreachable_facilities` (list of facility ID with reason).
- **Rules:**
  - Nearest means least travel time. Ties are broken by verification rank (`phone_verified` before `source_listed` before `unverified`), then by `facility_id`.
  - If no suitable facility is reachable on `G2`, return `reachable=False` with the reason `ALL_SUITABLE_FACILITIES_UNREACHABLE`; never raise.
  - `baseline_drivable` is false if any baseline path edge has class `blocked`.
- **ERRORS:** `ORIGIN_OUTSIDE_AREA`, `ORIGIN_NOT_SNAPPABLE`.
- **TESTS:** see the critical tests T-01 to T-03 in Section 10.3.

### 4.8 Module: `metrics`

- **WHAT:** compute the five comparison metrics over an origin set for each scenario.
- **WHERE:** `src/metrics.py`.
- **WHY:** FR10, FR11. Definitions in Section 5.5 and Section 5.6.
- **INPUT:** graphs, scenario layers, facilities, origins with weights, config.
- **OUTPUT:** a per-scenario table and a cross-scenario comparison table.
- **ERRORS:** `ORIGIN_SET_TOO_SMALL` (fewer than `MIN_ORIGINS`), `WEIGHTS_ALL_ZERO`.
- **TESTS:** golden-value test on the synthetic fixture graph (Section 10.2); same seed gives identical output; all metric values are within their valid ranges.

### 4.9 Module: `explain` and `audit`

Specified in Section 7.

### 4.10 Module: `app`

Specified in Section 6.

### 4.11 Module: `isolation` (extra view, P1)

- **WHAT:** for each scenario, find road nodes that lose access to every suitable facility or are badly delayed, group them by ward, and rank wards by estimated people in isolated areas.
- **WHERE:** `src/isolation.py`.
- **WHY:** FR15. It turns the reachability comparison into a planner-facing priority list. It is an extra view and must never displace the P0 core.
- **INPUT:** `G`, `G2`, the suitable-facilities table, the unit polygons with populations (or fallback grid), config.
- **OUTPUT:** the Section 3.9 table for the scenario, a map layer, and a list of non-fatal warnings.
- **DATA:** one multi-source shortest-path pass on the **reversed** graph from all suitable-facility nodes, once for `G` and once for `G2`, giving every node its travel time to the nearest suitable facility. Do not run one route per node.
- **Rules:** node states and scores are defined in Section 5.7; nodes that are disconnected in the baseline graph are excluded and counted, never treated as flood isolation.
- **ERRORS:** `UNITS_NOT_AVAILABLE` (no ward or fallback units), `ISOLATION_NO_ELIGIBLE_NODES` (every node excluded), `ISOLATION_UNIT_EMPTY` (non-fatal: a unit with too few eligible nodes is excluded and logged).
- **TESTS:** T-19 to T-26 (Section 10.3).

### 4.12 Module: `i18n`

- **WHAT:** load the three dictionaries, serve `t(key, **params)`, number and percentage formatting, language selection and fallback, HTML escaping.
- **WHERE:** `src/i18n.py`; dictionaries in `i18n/`.
- **WHY:** FR17; I18N-1 to I18N-14.
- **INPUT:** language code, key, parameters.
- **OUTPUT:** strings with placeholders filled; `fmt_int` (Indian grouping, Western digits), `fmt_pct` (`NN.N%`), `escape_html`.
- **DATA:** `i18n/en.json`, `ta.json`, `hi.json`; the active language in the session and the `lang` query parameter.
- **ERRORS:** `I18N_LANGUAGE_UNSUPPORTED` (fall back to English), `I18N_KEY_MISSING` (fall back to English, then the key; log), `I18N_PLACEHOLDER_MISMATCH` (raised by the parity test, not at runtime).
- **TESTS:** T-27 to T-32.

### 4.13 Modules: `ui_theme` and `ui_components`

- **WHAT:** inject the CSS theme (Section 6.10), and provide reusable building blocks: simulation banner, card container with title and caption, KPI card (value, change line, sparkline, tooltip), ranked-list card, facility badge, "View data" expander.
- **WHERE:** `src/ui_theme.py`, `src/ui_components.py`.
- **WHY:** FR16; keeps every card visually consistent and keeps escaping in one place.
- **INPUT:** already-computed data structures and translated strings; never raw data strings.
- **OUTPUT:** Streamlit elements; any custom HTML is built only from `escape_html` text and static CSS.
- **ERRORS:** a card whose data is missing renders a translated "no data" state, never an exception.
- **TESTS:** T-30 (escaping), U-01 to U-15.

### 4.14 Module: `charts`

- **WHAT:** build the Altair charts: sparkline, bar with conventional tick and change label, class bars, ranked horizontal bars.
- **WHERE:** `src/charts.py`.
- **WHY:** FR16; the data builders are pure functions so they can be tested without a browser.
- **INPUT:** the Section 5.8 aggregation tables and translated strings.
- **OUTPUT:** chart objects plus the underlying table for each "View data" expander. Chart fonts use the Section 6.10 stack so Tamil and Devanagari render.
- **ERRORS:** an empty table renders a translated "no data" state.
- **TESTS:** T-33, T-34.

---

## Section 5: Algorithms and Metric Definitions

All distances and buffers are computed in EPSG:32644 (UTM zone 44N, which covers Chennai). All thresholds below are **assumptions** and are configurable.

### 5.1 Travel Time

Each edge's `travel_time` (seconds) is length divided by speed, using OSMnx's imputed speeds. Free-flow speeds are not realistic for emergency vehicles in flood conditions, so results are comparative, not absolute (A-05).

### 5.2 Edge Flood Classification

For each edge:

`flooded_fraction = (length of the edge geometry inside the flood polygon) / (edge length)`

| Class | Condition | Graph effect on `G2` |
|---|---|---|
| `passable` | `flooded_fraction < FLOOD_FRACTION_AT_RISK` | No change |
| `at_risk` | `FLOOD_FRACTION_AT_RISK <= flooded_fraction < FLOOD_FRACTION_BLOCKED` | `travel_time` multiplied by `AT_RISK_TIME_MULTIPLIER` |
| `blocked` | `flooded_fraction >= FLOOD_FRACTION_BLOCKED` | Edge removed (both directions of a two-way road) |

Defaults: at-risk 0.10, blocked 0.50, multiplier 3.0 (assumptions A-01, A-02, A-03).

**Worked example (illustrative, not measured data):**
- Edge A: length 200 m, 130 m inside the flood polygon. Fraction 0.65. Class `blocked`. Removed.
- Edge B: length 200 m, 40 m inside. Fraction 0.20. Class `at_risk`. If base time is 24 s, new time is 72 s.
- Edge C: length 200 m, 10 m inside. Fraction 0.05. Class `passable`. Unchanged.

### 5.3 Optional Tunnel Rule (P2)

If `TREAT_TUNNELS_AS_FLOOD_SENSITIVE` is true, an edge tagged `tunnel` in OSM is classified `blocked` when any flood feature lies within `TUNNEL_SENSITIVITY_RADIUS_M` (default 50 m, assumption A-08). Default is false. Research found 180 tunnel-tagged ways in the Chennai bounding box; the rule models underpass flooding that polygons often miss.

### 5.4 Facility Selection

Among suitable facilities (Section 4.6), choose the facility with the least travel time on the graph being used. Compute shortest paths to all suitable facilities, not only the nearest, so unreachable facilities can be reported with a reason.

### 5.5 Origin Set and Metrics

**Origin set.** `N_ORIGINS` (default 20, minimum `MIN_ORIGINS` = 10) graph nodes sampled with `RANDOM_SEED`. Stratified: at least `MIN_FLOOD_ADJACENT_ORIGINS` (default 5) must lie within `FLOOD_ADJACENT_RADIUS_M` of the observed composite, so the test is not trivial. If the study area cannot supply enough flood-adjacent nodes, log `ORIGIN_STRATIFICATION_SHORT` and continue.

Let `i` index origins, `w_i` the population weight, `T_base(i)` the baseline travel time, `T_fa(i)` the flood-aware travel time (undefined if unreachable), `D_i` true if the baseline route is drivable in the scenario.

| Metric | Definition |
|---|---|
| M1 Travel-time increase | For origins where both routes exist and the baseline is drivable: `T_fa(i) - T_base(i)`. Report mean, median, maximum in minutes, and the count of origins included |
| M2 Route feasibility | (a) Share of origins whose baseline route is **not** drivable (`1 - mean(D_i)`), called the false-route rate. (b) Share of origins with a flood-aware route (`mean(T_fa defined)`) |
| M3 Facility reachability | For each suitable facility `f`: share of origins that can reach `f` on `G2`. Also: share of origins that can reach at least one suitable facility |
| M4 Population coverage | `C_fa(T) = sum(w_i * [T_fa(i) <= T]) / sum(w_i)` and `C_conv(T) = sum(w_i * [D_i and T_base(i) <= T]) / sum(w_i)`, with `T = COVERAGE_THRESHOLD_MIN` (default 30, assumption A-06). Report the difference |
| M5 Routing robustness | Section 5.6 |

The 30-minute figure is a configurable analysis threshold, **not** an official standard. Do not cite the Karnataka 108 audit's 72% figure as a Tamil Nadu benchmark; it concerns Karnataka, not Tamil Nadu.

### 5.6 Robustness

Flood extent is uncertain. For `K = ROBUSTNESS_RUNS` runs (default 50), with `RANDOM_SEED`:

1. Draw a buffer distance uniformly from `ROBUSTNESS_BUFFER_RANGE_M` (default -100 m to +150 m, assumption A-07).
2. Buffer the observed composite by that distance, classify edges, build `G2_k`.
3. For each origin, record the chosen facility `f_k*(i)` (or `None` if unreachable).

`Robustness_i = (1/K) * sum_k [ f_k*(i) = f_central*(i) ]`, where `f_central*` is the choice under the scenario being evaluated. `None` equals `None` counts as stable. Overall robustness is the mean of `Robustness_i`. Also report the share of origins whose reachability changes in at least one run.

The result is determined by the seed; the same seed must give identical output (test T-12).

### 5.7 Isolation Priority Ranking (extra view, P1)

Built only after the core passes (Section 14, PHASE 8). Everything here is indicative decision support, not prediction.

**5.7.1 Units.** Wards from D8 joined to D7 populations (Section 2.4). If the join fails, the units are still wards but with placeholder weights; if the polygons cannot be loaded, use fallback grid cells.

**5.7.2 Node states.** For every graph node `n`, compute `T_base(n)`, the travel time to the nearest suitable facility on `G`, and `T_fa(n)`, the same on `G2`. Both come from the multi-source passes in Section 4.11.

| State | Condition |
|---|---|
| `baseline_disconnected` | `T_base(n)` undefined. Excluded from the unit's eligible nodes and counted separately, because the node had no access even without flooding |
| `isolated` | `T_base(n)` defined and `T_fa(n)` undefined |
| `delayed` | Both defined and `T_fa(n) - T_base(n) >= ISOLATION_DELAY_MIN` minutes |
| `ok` | Otherwise |

**5.7.3 Shares.** Let `E_u` be the eligible nodes in unit `u` (all states except `baseline_disconnected`). `I_u = isolated / E_u` and `D_u = delayed / E_u`. A unit with `E_u < MIN_ELIGIBLE_NODES_PER_UNIT` is excluded and logged as `ISOLATION_UNIT_EMPTY`.

**5.7.4 Score and rank.** With `Pop_u` the unit population (or placeholder weight):

- `estimated_people_isolated_u = Pop_u * I_u`
- `priority_score_u = Pop_u * (I_u + ISOLATION_DELAY_WEIGHT * D_u)`
- Rank by `priority_score` descending. Ties are broken by larger `I_u`, then larger `Pop_u`, then `unit_id`.

**5.7.5 Worked example (illustrative numbers, not data).** `ISOLATION_DELAY_WEIGHT = 0.5`.

| Unit | Pop | Eligible nodes | Isolated | Delayed | `I_u` | `D_u` | Est. people isolated | Score | Rank |
|---|---|---|---|---|---|---|---|---|---|
| X | 40,000 | 200 | 50 | 30 | 0.25 | 0.15 | 10,000 | 40,000 x (0.25 + 0.5 x 0.15) = 13,000 | 2 |
| Y | 90,000 | 300 | 15 | 0 | 0.05 | 0.00 | 4,500 | 90,000 x 0.05 = 4,500 | 3 |
| Z | 20,000 | 100 | 100 | 0 | 1.00 | 0.00 | 20,000 | 20,000 x 1.00 = 20,000 | 1 |

Test T-22 reproduces this ordering on the synthetic fixture.

**5.7.6 Validation (P2, optional).** If `data/reference/reported_isolated_areas.csv` exists, map each reported area to a unit (by the `unit_id` column or a manual name match) and report: how many reported areas fall within the top `ISOLATION_TOP_K` ranked units, and which do not. Show matches and misses. **Do not state an accuracy percentage;** the reference list is incomplete and ground truth is thin.

**5.7.7 Limits (must appear in the UI and README).**
1. Node share is a proxy for streets and area, not for people.
2. Population is assumed to be spread evenly within a ward (A-15). It is not.
3. Census 2011 populations are old (A-16).
4. Scenarios are observed-composite or simulated; the ranking is not a forecast.
5. Nodes that were already disconnected in the baseline are excluded, so very poorly connected areas may be under-reported.
6. Rankings can change between scenarios; show the change, do not hide it.

### 5.8 Dashboard Aggregations

These definitions feed the KPI cards and overview cards (Sections 6.5 and 6.6). All use the origin set and weights of Section 5.5. `D_i` is whether the conventional route of origin `i` is drivable in the scenario.

| ID | Definition |
|---|---|
| K1 | Median of `T_fa(i) - T_base(i)` over origins with both routes and `D_i` true, in minutes. Secondary: the maximum |
| K2 | Share of origins with a flood-aware route to at least one suitable facility. Change line: K2 minus the conventional drivable share `mean(D_i)`, in percentage points |
| K3 | Mean over suitable facilities `f` of `reach_f`, where `reach_f` is the share of origins with a path to `f` on `G2`. Change line: K3 minus the mean over `f` of `conv_reach_f` |
| `conv_reach_f` | Share of origins whose shortest path to `f` on `G` (the baseline graph) contains no blocked edge in the scenario. Origins with no path on `G` do not count |
| K4 | `C_fa(T)` of Section 5.5. Change line: `C_fa(T) - C_conv(T)` in percentage points |
| K5 | Mean `Robustness_i` of Section 5.6. Secondary: the share of origins whose reachability changed in at least one run. No change line |
| Sparkline | The metric's value for the four scenarios in the fixed order observed, mild, moderate, severe. Not a time series |
| Bar with tick | Bar = the flood-aware value; tick = the conventional-routing counterpart |

**Equivalence note.** "Route feasibility (b)" in Section 5.5 (M2b) and "share reaching at least one suitable facility" (M3, any) are the **same quantity**. The dashboard shows it once, as K2. K3 is the per-facility mean, which is a different number.

**Change-line rule.** The change line is shown only where a conventional counterpart exists (K2, K3, K4). K1 and K5 never show one. A change of exactly zero shows the word for "no change".

---

## Section 6: Dashboard User Interface Specification

`IMPLEMENTATION REQUIRED`. The interface is a dashboard modelled on a supplied reference image (an "Executive Dashboard": left icon rail, header with title, date pill and metric toggles, a row of KPI cards with trend lines and change indicators, and a grid of rounded cards holding a map, bar charts and ranked lists). The reference is a **layout and styling guide only**. Its content (sales, profit, customers) does not apply; every element is adapted to FloodPath-Care's data and honesty rules (Section 6.1). Everything is implemented in Streamlit with custom CSS and Altair charts. No custom JavaScript component is built.

### 6.1 Design Reference and Adaptation

| Reference element | FloodPath-Care adaptation |
|---|---|
| Title "Executive Dashboard" and a personal welcome line | Title "FloodPath-Care" with a translated subtitle. No personal greeting and no user accounts. The persistent simulation banner sits directly under the title |
| Date-range pill ("Jan 01, 2022 - Dec 30, 2022") | **Event pill**: "Chennai floods, 2015 (historical replay)" with the observed layers' dates. Read-only; there is no date filter |
| Toggle buttons Sales / Profit / Orders | **Metric focus toggle**: Reachability / Coverage / Travel time. It changes how the map's origin points are styled and which list the ranked-list card shows (Section 6.6) |
| Four KPI cards: value, change versus prior year, sparkline | **Five KPI cards** (Section 6.5): value, change versus conventional routing where a conventional counterpart exists, and a sparkline across the four scenarios (not a time series) |
| Map "Profit by State" with bubbles | **Route map card** (flood layer, classified roads, facilities, origin, both routes) |
| Bars "Profit by Segment" with a black prior-year tick and a change label | **Coverage by scenario** bars: bar = flood-aware value, black tick = conventional-routing value, label = change in percentage points |
| "Top 10 Products" ranked list with bars | **Top wards by isolation priority** ranked list (extra view); a facility-status card replaces it if the isolation view is not built |
| "Profit by Category" bars | **Road segments by class** (passable, at risk, blocked) per scenario |
| "Profit by Sub-Category" horizontal bars with ticks | **Reachability by facility**: bar = flood-aware, tick = conventional-drivable |
| "Top 10 Customers" ranked list | **Origins with the largest travel-time increase** ranked list |
| Left icon rail (dashboard, table, export PDF, export image, info, social links) | **Left rail**: Overview, Route explorer, Isolation priority, Metrics table, Data and limits, Export, Language, Info. No social links. PDF and image export are `OUT` (use the browser's print function) |
| Teal and dark-grey palette on a light-grey background; white rounded cards with soft shadows | The same tokens (Section 6.10), plus semantic colours for flood data (blue, orange, red) |

### 6.2 Pages and Navigation

| Page | Rail icon label key | Priority | Content |
|---|---|---|---|
| Overview (default) | `nav.overview` | P0 | Banner, header, five KPI cards, six cards (Section 6.4) |
| Route explorer | `nav.route` | P0 | One origin: map, result panel, explanation, unreachable facilities (Section 6.7) |
| Isolation priority | `nav.isolation` | P1 | Ward ranking page (Section 6.8); hidden if the isolation tables do not exist |
| Metrics table | `nav.metrics` | P0 | Full M1 to M5 table and cross-scenario comparison (Section 6.9) |
| Data and limits | `nav.data` | P0 | Datasets, gaps, assumptions, licence notes, translation status (Section 6.9) |
| Export | `nav.export` | P1 | CSV and JSON downloads (Section 6.9) |

Navigation lives in the left rail, built from native Streamlit controls (sidebar with a styled radio or pills, or Streamlit's own multipage navigation) and CSS. Rail icons use Streamlit's Material icon syntax if the pinned Streamlit version supports it; otherwise the rail shows text labels only. A true icon-only rail is a **verify-in-PHASE-10** item; the accepted fallback is a standard sidebar with icon and label.

### 6.3 Header and Global Controls

Shown on every page, in this order:

1. **Title and subtitle** (`app.title`, `app.subtitle`).
2. **Event pill** (`event.chennai_2015`), read-only.
3. **Metric focus toggle** (three buttons): Reachability (default), Coverage, Travel time (`focus.*`).
4. **Scenario control** (segmented): Observed composite, Mild, Moderate, Severe. Scenario names for the three simulated ones always include the word "simulated" in the active language (`scenario.*`).
5. **Language selector**: English, தமிழ், हिन्दी, each shown in its own script, always visible (Section 6A).
6. **Persistent banner** (`banner.simulation`): "Historical-data-informed simulation. Ambulance data is simulated. Not for live dispatch." It is visible on every page and in every state, including errors, and is never truncated.

### 6.4 Overview Layout (desktop, width 1280 px or more)

| Row | Contents |
|---|---|
| 0 | Banner |
| 1 | Header (title, event pill, focus toggle, scenario control, language selector) |
| 2 | Five KPI cards K1 to K5 |
| 3 | Route map card (two columns wide) · Coverage by scenario (C2) · Top wards by isolation priority (C3) |
| 4 | Road segments by class (C4) · Reachability by facility (C5) · Origins with the largest travel-time increase (C6) |

The page uses Streamlit's wide layout. Card titles sit at the top of each card, centred, with a small caption stating the scenario and its `kind`.

### 6.5 KPI Cards

Each card shows: translated label; value; change line; sparkline; tooltip with the definition (from Section 5.8). Formulas are in Section 5.8.

| Card | Label key | Value | Change line | Better direction |
|---|---|---|---|---|
| K1 | `kpi.time_increase` | Median travel-time increase, minutes | None; shows "max X min" as secondary text | Lower |
| K2 | `kpi.feasibility` | Share of origins with a feasible flood-aware route | Percentage points versus the share whose conventional route is drivable | Higher |
| K3 | `kpi.reachability` | Mean share of origins that can reach each suitable facility | Percentage points versus the conventional-drivable equivalent | Higher |
| K4 | `kpi.coverage` | Population coverage within the time limit T, flood-aware | Percentage points versus conventional-drivable coverage | Higher |
| K5 | `kpi.robustness` | Mean robustness across flood-extent variations | None; shows the share of origins whose reachability changed in at least one run as secondary text | Higher |

Rules:
- A change line is always **arrow + signed number + word** ("better" or "worse"), never colour alone. Improvement is teal with an up arrow; deterioration is red with a down arrow; an unchanged value shows "no change".
- The sparkline plots the metric for the four scenarios in the fixed order observed, mild, moderate, severe, with the selected scenario highlighted and the caption `spark.across_scenarios`. **It is not a time series.** Its tooltip lists the four values.
- Values are rounded: minutes to whole numbers, percentages to one decimal, people to whole numbers with Indian digit grouping (Section 6A).
- Every KPI includes an "indicative" qualifier in its tooltip.

### 6.6 Overview Cards

| ID | Card (title key) | Chart | Data | Interaction |
|---|---|---|---|---|
| C1 | Route map (`card.map`) | Folium map | Flood layer; passable, at-risk, blocked roads; facilities; sample origins; both routes for the selected origin | Layer toggles; origin points are styled by the focus toggle: reachability (reachable yes or no), coverage (within T minutes yes or no, sized by weight), travel time (colour bucket by increase) |
| C2 | Coverage by scenario (`card.coverage_by_scenario`) | Vertical bars with tick and change label | `C_fa(T)` per scenario; tick `C_conv(T)` | Selected scenario highlighted |
| C3 | Top wards by isolation priority (`card.isolation_top`) | Ranked list with horizontal bars, top `ISOLATION_TOP_K`, scrollable | Section 3.9 table | Click opens the Isolation page. If the isolation view is not built the card shows facility verification counts by tier and status instead |
| C4 | Road segments by class (`card.edge_classes`) | Grouped bars | Counts of passable, at-risk, blocked edges per scenario | Selected scenario highlighted |
| C5 | Reachability by facility (`card.reach_by_facility`) | Horizontal bars with tick, sorted | `reach_f` flood-aware; tick conventional-drivable (Section 5.8) | Facility verification badge next to the name |
| C6 | Origins with the largest travel-time increase (`card.top_origins`) | Ranked list with bars | Unreachable origins first, then by increase | Click selects the origin in the Route explorer |

Every chart has a **"View data" expander** showing its underlying table with the same translated headers. Charts are not the only way to read a number.

### 6.7 Route Explorer Page (P0)

- **Controls:** scenario, ambulance start (a simulated start or a click on the map), service, "include unverified facilities".
- **Map:** same layers as C1, larger, with the baseline route (dashed grey, with a marker where it crosses a blocked road) and the flood-aware route (solid green).
- **Result panel:** chosen facility (name, tier, verification badge, source and verified-on date), flood-aware time, conventional time, difference, whether the conventional route is drivable, the explanation text in the active language (Section 7.1), and the list of unreachable facilities with reasons.
- **Second-best route** (P2): a secondary dashed line.
- Times are shown in whole minutes with the word "indicative" in the tooltip.

### 6.8 Isolation Priority Page (extra view, P1)

`IMPLEMENTATION REQUIRED` only if PHASE 8 was built; otherwise the rail item is hidden, not shown empty.

- **Map:** ward polygons shaded by `priority_score` quantile, with the rank number printed on each of the top `ISOLATION_TOP_K` wards. Colour is never the only carrier of information: the table lists the same ranks.
- **Table:** rank, ward, population and its basis, isolated share, delayed share, estimated people in isolated areas, priority score. Sortable. CSV download.
- **Scenario comparison:** the top five wards under each scenario side by side, with rank changes marked.
- **Notes (always visible, translated):** `note.indicative`.
- **Placeholders:** if `population_basis = placeholder`, show `label.placeholder_weights` and relabel the people column "share of sample points".
- **Reference check (if the reference file exists):** a panel listing reported cut-off areas inside or outside the top-K wards, with no accuracy percentage.

### 6.9 Metrics Table, Data and Limits, and Export Pages

**Metrics table (P0).** All five metrics for the selected scenario with definitions and assumptions in effect, a cross-scenario comparison table, and a CSV download.

**Data and limits (P0).**
- A dataset table: ID, link, date, licence, observed or simulated badge.
- The four standing gaps (`gap.*`), each with an **"original English"** line beneath the translation so a reader can check the meaning.
- Extra limits: current roads are not 2015 roads; radar and crowd-sourced data can miss flooded streets; basemap labels stay in the tile provider's language and cannot be switched.
- The assumptions table with current values from config.
- The licence conflicts (UNOSAT non-commercial share-alike; OSM ODbL; OpenCity's Public Domain tag versus portal terms).
- **Translation status:** for each language, `draft` or `reviewed`, reviewer and date.

**Export (P1).** Buttons for: audit log (JSON), metrics (CSV), facilities with verification status (CSV), and, if built, isolation ranking (CSV). Files are language-neutral (English column keys) and carry `ui_language`. PDF and image export are `OUT`.

### 6.10 Visual Design Tokens

The colours below approximate the reference image by eye. They are not sampled values (assumption A-21). Any small teal text must use a darker teal that passes a 4.5:1 contrast check; **verify contrast with a checker in PHASE 10**.

| Token | Value | Use |
|---|---|---|
| Page background | light grey, about `#EEF0F2` | Behind cards |
| Card | white, radius 16 px, soft shadow | All cards |
| Primary teal | about `#1F8A84` | Flood-aware values, KPI values (large text), selected controls |
| Secondary dark grey | about `#555B61` | Conventional-routing values, ticks |
| Flood blue | about `#4A90C2` | Flood layer |
| At-risk orange | about `#E08A1E` | At-risk roads |
| Blocked red | about `#C0392B` | Blocked roads, deterioration arrows |
| Text | about `#1D2A33` | Body |
| Font stack | `"Noto Sans", "Noto Sans Tamil", "Noto Sans Devanagari", "Nirmala UI", "Segoe UI", Arial, sans-serif` | All text, including chart text |
| Sizes | Title 28 to 32 px; card title 13 px bold; KPI value 28 px; body 14 px; minimum 12 px | |

### 6.11 UI States

| State | Behaviour |
|---|---|
| Loading | Spinner with the current stage name, translated |
| Missing data files | Banner listing the files to fetch and the command to run |
| `NO_SUITABLE_FACILITY` | Result panel states why; no route |
| Unreachable origin | Translated `result.unreachable`; unreachable facilities listed |
| Ward join failed | Translated `label.placeholder_weights` on every card that uses population |
| Isolation view not built | Rail item and C3 content replaced as in Sections 6.2 and 6.6 |
| Missing translation key | English text shown; `I18N_KEY_MISSING` logged in the audit log |
| Any Section 8 error | Error banner with the code (English) and a translated message; the simulation banner stays visible |

### 6.12 Accessibility and Responsive Behaviour

- Text contrast meets WCAG AA on banners, notes, tables and KPI labels (large KPI values may use the 3:1 large-text threshold); every control has a translated label; meaning is never carried by colour alone (arrows, words, patterns and line styles are used too).
- Every chart has a "View data" table; tables are readable by screen readers.
- Tamil and Hindi text may be 30 to 50 percent longer than English (assumption A-19): cards wrap text and never truncate the banner, notes, limits, KPI labels or button labels.
- Keyboard order follows the visual order: banner, header, rail, KPI cards, cards.
- Width 1280 px or more: layout of Section 6.4. Width 768 to 1279 px: two columns. Width under 768 px: one column (P2). A formal accessibility audit is `OUT`.

### 6.13 Implementation in Next.js (Version 3.0)

`SPECIFICATION COMPLETE`. This section overrides the Streamlit-specific details of Sections 4.13, 4.14, 6.2, 6.10 and 14 (PHASE 1, 10, 11).

| Topic | Streamlit version (earlier text) | Next.js version (now) |
|---|---|---|
| Stack | Streamlit, Altair, Folium | Next.js 16 App Router, React 19, TypeScript, Tailwind 4. Map: Leaflet (added in PHASE 2). Charts: hand-built SVG components, no chart library |
| Data flow | Python modules called by the app | Python writes JSON and GeoJSON to `web/public/data/` (one file set per scenario); `scripts/export_web_i18n.py` and `scripts/export_web_config.py` copy the dictionaries and assumptions into `web/src/` so Python stays the single source of truth. No API server |
| Interactivity limit | Any origin could be computed live | The Route explorer works for the precomputed simulated starts and sample origins only; arbitrary map clicks and live threshold changes are not supported |
| Files | `app.py`, `src/ui_theme.py`, `src/ui_components.py`, `src/charts.py` | `web/src/app/` (layout, page, `globals.css`), `web/src/components/` (`Dashboard.tsx`, `ui.tsx`, `icons.tsx`), `web/src/lib/i18n.ts` |
| Language | Session state plus query parameter | The `lang` query parameter is the single source of truth; unsupported values fall back to English; the page sets `<html lang>` so CSS can disable letter-spacing for Tamil and Hindi |
| HTML safety | `escape_html` before any custom HTML | React escapes text by default; `dangerouslySetInnerHTML` is forbidden (I18N-14) |
| Fonts | System stack | Inter through `next/font` (downloaded once at build or dev time), with Noto Sans Tamil, Noto Sans Devanagari and Nirmala UI as fallbacks for Tamil and Hindi |
| Tests | pytest with Streamlit's AppTest | pytest for Python and the sync tests (`tests/test_web_sync.py`); `tsc --noEmit`, `npm run lint` and `npm run build` for the web app; browser preview at each checkpoint |

**Visual style (final, user request 2026-10-13).** Follow the reference dashboard image: a light-grey gradient page; large white cards (24 px radius) with soft raised shadows; a floating rounded icon rail with a round logo (the letter F) and a thin divider between icon groups; a large grey title; a read-only event pill with a calendar icon at the top right; pill toggles (dark-grey pills for the focus toggle, pale pills for language and scenario) whose selected state is blue; KPI cards with an uppercase label, a change line on the right and a trend area; and an equal 3 x 2 grid of cards. The accent is **blue** instead of the image's teal: accent `#1E64B4` (about 6:1 against white), dark `#174E8F`, soft `#E1ECF8`, deep `#0F3F77`; page `#E7E9EB` to `#F4F5F6`; dark pills and conventional-routing grey `#555B61`; title grey `#5C6166`. These colours override Section 6.10. Data colours stay separate from the accent so a flood layer never looks like a control: flood cyan-blue `#5BB5E0`, at-risk orange `#E08A1E`, blocked red `#C0392B`, improvement green `#1B7F5C` and deterioration red, each with an arrow, a signed number and a word. Font: Inter with Noto Sans Tamil, Noto Sans Devanagari and Nirmala UI as fallbacks. The colours approximate the image by eye (A-21). The reference website shpp3.vercel.app was reviewed, and its thin-border navy style was not adopted (user decision).

**Status.** The PHASE 1 skeleton (rail, header, scenario, language and focus controls, banner, five KPI card frames, six card frames, Data and limits page) is built and checked in a browser in English, Tamil and Hindi. Nothing on the Overview or Route pages shows analysis results yet.

---

## Section 6A: Internationalisation (English, Tamil, Hindi) and UI Dictionary

`IMPLEMENTATION REQUIRED`. The whole interface is available in English, Tamil and Hindi. Language support is a `P0` requirement for the pages marked `P0` in Section 6.2, using at least the dictionary in Section 6A.3. Completing every remaining string (chart axes, tooltips, table headers) in all three languages is `P1`.

### 6A.1 Requirements

| ID | Requirement |
|---|---|
| I18N-1 | Supported languages: `en` (default), `ta`, `hi` |
| I18N-2 | Every user-visible string (labels, buttons, card titles, tooltips, legends, banners, notes, chart titles and axis titles, table headers, download button labels, error messages, explanation templates) comes from `i18n/{lang}.json` through a lookup function `t(key, **params)`. No hard-coded user-visible string appears in code, except proper nouns and codes (checked by a grep test) |
| I18N-3 | The three dictionary files have the **same key set** (test T-27) |
| I18N-4 | For every key, the **same placeholder names** appear in all three languages (test T-28) |
| I18N-5 | The language selector shows each language in its own script (English, தமிழ், हिन्दी). Switching is immediate. The choice is stored in the session and in the URL query parameter `lang`. An unsupported value falls back to English |
| I18N-6 | Fallback chain: selected language, then English, then the key name. A fallback logs `I18N_KEY_MISSING` and never crashes. In tests, a missing key is a failure |
| I18N-7 | Fonts: the font stack in Section 6.10 covers Tamil and Devanagari; "Nirmala UI" (shipped with Windows) is the system fallback. Bundling small OFL-licensed Noto fonts in `assets/fonts/` is optional and needs the user's approval before download. The demo machine must show no missing-glyph boxes (check U-10) |
| I18N-8 | Numbers use Western digits 0 to 9 in all languages, with Indian digit grouping (for example 12,34,567) through `fmt_int` (assumption A-18). Percentages `NN.N%` through `fmt_pct`. Dates in tables and the event pill are numeric ISO `YYYY-MM-DD`, so they need no translation. Tamil and Devanagari numerals are `OUT` |
| I18N-9 | **Not translated:** facility names and ward names (they come from source data), dataset names and IDs, licence names, EPSG codes, error codes (the code stays English and its message is translated), file names, config keys |
| I18N-10 | Text expansion: cards, banners and buttons wrap and never truncate with an ellipsis (assumption A-19) |
| I18N-11 | Charts: titles, axis titles, legends and tooltips come from the dictionary and use the font stack. The map's own legend and popups are translated. **Basemap tile labels stay in the tile provider's language** and cannot be switched; the Data and limits page says so |
| I18N-12 | The audit log and all CSV exports are language-neutral (English keys and column names) and include a `ui_language` field |
| I18N-13 | **Translation review.** All Tamil and Hindi strings start as `draft`, written by an AI assistant. A fluent reviewer marks them `reviewed` in `docs/TRANSLATION_REVIEW.md` (name, date, language, keys checked). The critical keys (banner, notes, gaps, placeholder notice, unreachable message, explanation templates) must be reviewed before the demo is recorded. Until then the README and the Data and limits page say "draft translation" |
| I18N-14 | HTML safety: every dictionary string and every data string (facility and ward names, file contents) is HTML-escaped before it is placed in custom HTML (test T-30). Custom HTML is built only from escaped text and static CSS |

### 6A.2 Dictionary File Structure

Each `i18n/{lang}.json` is a flat map from dotted keys to strings, plus a `_meta` block: `language`, `status` (`draft` or `reviewed`), `reviewed_by`, `reviewed_on`. Keys use the namespaces in 6A.3. Placeholders use `{name}`. Strings must not contain the pipe character or raw HTML.

### 6A.3 Initial Dictionary (the minimum translated set)

These are **draft** Tamil and Hindi translations (I18N-13). Claude Code adds any further key (chart axis titles, tooltips, table headers, additional errors) in all three files in the same commit, following the same pattern, and marks them draft.

| Key | English | Tamil (draft) | Hindi (draft) |
|---|---|---|---|
| `app.title` | FloodPath-Care | FloodPath-Care | FloodPath-Care |
| `app.subtitle` | Flood-aware emergency routing to maternal facilities | மகப்பேறு வசதிகளுக்கான வெள்ளம் அறிந்த அவசர வழித்தட திட்டமிடல் | मातृ-देखभाल सुविधाओं तक बाढ़-जागरूक आपातकालीन मार्ग |
| `banner.simulation` | Historical-data-informed simulation. Ambulance data is simulated. Not for live dispatch. | வரலாற்றுத் தரவை அடிப்படையாகக் கொண்ட உருவகப்படுத்துதல். ஆம்புலன்ஸ் தரவு உருவகப்படுத்தப்பட்டது. நேரடி அனுப்புதலுக்கு அல்ல. | ऐतिहासिक डेटा पर आधारित सिमुलेशन। एम्बुलेंस डेटा सिम्युलेटेड है। लाइव डिस्पैच के लिए नहीं। |
| `event.chennai_2015` | Chennai floods, 2015 (historical replay) | சென்னை வெள்ளம் 2015 (வரலாற்று மறுஇயக்கம்) | चेन्नई बाढ़ 2015 (ऐतिहासिक पुनःप्रदर्शन) |
| `nav.overview` | Overview | மேலோட்டம் | सारांश |
| `nav.route` | Route explorer | வழித்தட ஆய்வு | मार्ग अन्वेषक |
| `nav.isolation` | Isolation priority | தனிமைப்படுத்தல் முன்னுரிமை | अलगाव प्राथमिकता |
| `nav.metrics` | Metrics table | அளவீட்டு அட்டவணை | मीट्रिक तालिका |
| `nav.data` | Data and limits | தரவு மற்றும் வரம்புகள் | डेटा और सीमाएँ |
| `nav.export` | Export | ஏற்றுமதி | निर्यात |
| `nav.language` | Language | மொழி | भाषा |
| `focus.reachability` | Reachability | அணுகல் | पहुँच |
| `focus.coverage` | Coverage | உள்ளடக்கம் | कवरेज |
| `focus.time` | Travel time | பயண நேரம் | यात्रा समय |
| `scenario.observed` | Observed composite | கண்டறியப்பட்ட கூட்டுத் தொகுப்பு | प्रेक्षित संयुक्त परत |
| `scenario.mild` | Mild (simulated) | லேசான (உருவகப்படுத்தப்பட்டது) | हल्का (सिम्युलेटेड) |
| `scenario.moderate` | Moderate (simulated) | மிதமான (உருவகப்படுத்தப்பட்டது) | मध्यम (सिम्युलेटेड) |
| `scenario.severe` | Severe (simulated) | கடுமையான (உருவகப்படுத்தப்பட்டது) | गंभीर (सिम्युलेटेड) |
| `kpi.time_increase` | Travel-time increase | பயண நேர அதிகரிப்பு | यात्रा समय में वृद्धि |
| `kpi.feasibility` | Route feasibility | வழித்தட சாத்தியம் | मार्ग व्यवहार्यता |
| `kpi.reachability` | Facility reachability | வசதி அணுகல் | सुविधा पहुँच |
| `kpi.coverage` | Population coverage | மக்கள் தொகை உள்ளடக்கம் | जनसंख्या कवरेज |
| `kpi.robustness` | Routing robustness | வழித்தட உறுதித்தன்மை | मार्ग मजबूती |
| `kpi.max` | max | அதிகபட்சம் | अधिकतम |
| `kpi.changed_runs` | reachability changed in at least one run | குறைந்தது ஒரு ஓட்டத்தில் அணுகல் மாறியது | कम से कम एक रन में पहुँच बदली |
| `delta.vs_conventional` | vs conventional | வழக்கமான வழித்தடத்துடன் ஒப்பிடுகையில் | पारंपरिक मार्ग की तुलना में |
| `delta.better` | better | மேம்பாடு | बेहतर |
| `delta.worse` | worse | மோசம் | बदतर |
| `delta.none` | no change | மாற்றம் இல்லை | कोई बदलाव नहीं |
| `delta.pp` | percentage points | சதவீதப் புள்ளிகள் | प्रतिशत अंक |
| `spark.across_scenarios` | across scenarios | சூழ்நிலைகள் முழுவதும் | परिदृश्यों में |
| `card.map` | Route map | வழித்தட வரைபடம் | मार्ग मानचित्र |
| `card.coverage_by_scenario` | Coverage by scenario | சூழ்நிலை வாரியாக உள்ளடக்கம் | परिदृश्य के अनुसार कवरेज |
| `card.isolation_top` | Top wards by isolation priority | தனிமைப்படுத்தல் முன்னுரிமையில் முதன்மை வார்டுகள் | अलगाव प्राथमिकता में शीर्ष वार्ड |
| `card.edge_classes` | Road segments by class | சாலைப் பகுதிகள் வகை வாரியாக | श्रेणी के अनुसार सड़क खंड |
| `card.reach_by_facility` | Reachability by facility | வசதி வாரியாக அணுகல் | सुविधा के अनुसार पहुँच |
| `card.top_origins` | Origins with the largest travel-time increase | அதிக நேர அதிகரிப்பு உள்ள தொடக்கப் புள்ளிகள் | सबसे अधिक समय वृद्धि वाले आरंभ बिंदु |
| `card.view_data` | View data | தரவைக் காண்க | डेटा देखें |
| `class.passable` | Passable | கடக்கக்கூடியது | पार करने योग्य |
| `class.at_risk` | At risk | ஆபத்து உள்ளது | जोखिम में |
| `class.blocked` | Blocked | தடைபட்டது | अवरुद्ध |
| `badge.observed` | Observed | கண்டறியப்பட்டது | प्रेक्षित |
| `badge.composite` | Composite | கூட்டுத் தொகுப்பு | संयुक्त |
| `badge.simulated` | Simulated | உருவகப்படுத்தப்பட்டது | सिम्युलेटेड |
| `facility.verified` | Phone-verified | தொலைபேசி மூலம் சரிபார்க்கப்பட்டது | फ़ोन से सत्यापित |
| `facility.source_listed` | Listed in source | மூலத்தில் பட்டியலிடப்பட்டது | स्रोत में सूचीबद्ध |
| `facility.unverified` | Unverified | சரிபார்க்கப்படவில்லை | असत्यापित |
| `label.scenario` | Scenario | சூழ்நிலை | परिदृश्य |
| `label.origin` | Ambulance start (simulated) | ஆம்புலன்ஸ் தொடக்கப் புள்ளி (உருவகப்படுத்தப்பட்டது) | एम्बुलेंस आरंभ बिंदु (सिम्युलेटेड) |
| `label.service` | Service needed | தேவையான சேவை | आवश्यक सेवा |
| `service.emergency_obstetric` | Emergency obstetric care | அவசர மகப்பேறு சிகிச்சை | आपातकालीन प्रसूति देखभाल |
| `label.include_unverified` | Include unverified facilities | சரிபார்க்கப்படாத வசதிகளையும் சேர்க்கவும் | असत्यापित सुविधाएँ शामिल करें |
| `label.rank` | Rank | தரவரிசை | रैंक |
| `label.ward` | Ward | வார்டு | वार्ड |
| `label.est_people_isolated` | Estimated people in isolated areas (indicative) | தனிமைப்படுத்தப்பட்ட பகுதிகளில் மதிப்பிடப்பட்ட மக்கள் (சுட்டிக்காட்டுதல்) | अलग-थलग क्षेत्रों में अनुमानित लोग (सांकेतिक) |
| `label.placeholder_weights` | Population weights are placeholders (ward join failed). Coverage is a share of sample points, not of people. | மக்கள் தொகை எடைகள் தற்காலிகமானவை (வார்டு இணைப்பு தோல்வியடைந்தது). உள்ளடக்கம் என்பது மாதிரிப் புள்ளிகளின் பங்கு; மக்களின் பங்கு அல்ல. | जनसंख्या भार प्लेसहोल्डर हैं (वार्ड जुड़ाव विफल रहा)। कवरेज नमूना बिंदुओं का हिस्सा है, लोगों का नहीं। |
| `route.baseline` | Conventional route | வழக்கமான வழித்தடம் | पारंपरिक मार्ग |
| `route.flood_aware` | Flood-aware route | வெள்ளம் அறிந்த வழித்தடம் | बाढ़-जागरूक मार्ग |
| `unit.minutes` | min | நிமி | मिनट |
| `button.download_audit` | Download audit log | தணிக்கைப் பதிவைப் பதிவிறக்கு | ऑडिट लॉग डाउनलोड करें |
| `button.download_csv` | Download CSV | CSV பதிவிறக்கு | CSV डाउनलोड करें |
| `result.unreachable` | No suitable facility is reachable under this scenario. | இந்தச் சூழ்நிலையில் பொருத்தமான எந்த வசதியையும் அடைய முடியாது. | इस परिदृश्य में कोई उपयुक्त सुविधा पहुँच योग्य नहीं है। |
| `note.indicative` | Indicative ranking. Estimated people assume an even spread within each ward. Scenarios are not predictions. Not an operational dispatch order. | இது சுட்டிக்காட்டும் தரவரிசை மட்டுமே. மதிப்பிடப்பட்ட மக்கள் எண்ணிக்கை ஒவ்வொரு வார்டிலும் சமமாகப் பரவியுள்ளது என்ற அனுமானத்தை அடிப்படையாகக் கொண்டது. சூழ்நிலைகள் முன்கணிப்புகள் அல்ல. இது செயல்பாட்டு அனுப்புதல் உத்தரவு அல்ல. | यह केवल सांकेतिक रैंकिंग है। अनुमानित लोगों की संख्या हर वार्ड में समान वितरण मानकर निकाली गई है। परिदृश्य पूर्वानुमान नहीं हैं। यह परिचालन डिस्पैच आदेश नहीं है। |
| `gap.facility_list` | No public verified list of emergency obstetric facilities with coordinates exists for Chennai. The facility list is a hand-checked proxy. | சென்னைக்கான அவசரகால மகப்பேறு வசதிகளின், ஆயத்தொலைவுகளுடன் கூடிய சரிபார்க்கப்பட்ட பொதுப் பட்டியல் எதுவும் இல்லை. வசதிப் பட்டியல் கையால் சரிபார்க்கப்பட்ட மாற்றுப் பட்டியல் மட்டுமே. | चेन्नई के लिए निर्देशांक सहित आपातकालीन प्रसूति सुविधाओं की कोई सार्वजनिक सत्यापित सूची उपलब्ध नहीं है। सुविधा सूची हाथ से जाँची गई एक प्रॉक्सी सूची है। |
| `gap.ambulance` | No 108 ambulance data is public. Ambulance starts and times are simulated. | 108 ஆம்புலன்ஸ் தரவு எதுவும் பொதுவில் இல்லை. ஆம்புலன்ஸ் தொடக்கப் புள்ளிகளும் நேரங்களும் உருவகப்படுத்தப்பட்டவை. | 108 एम्बुलेंस का कोई डेटा सार्वजनिक नहीं है। एम्बुलेंस के आरंभ बिंदु और समय सिम्युलेटेड हैं। |
| `gap.peak` | No open flood extent exists for the 1-4 Dec 2015 peak. The observed scenario is a composite of available layers. | 2015 டிசம்பர் 1-4 உச்சநிலைக்கான திறந்த வெள்ளப் பரப்புத் தரவு இல்லை. கண்டறியப்பட்ட சூழ்நிலை கிடைக்கும் அடுக்குகளின் கூட்டுத் தொகுப்பாகும். | 1-4 दिसंबर 2015 के चरम के लिए कोई खुला बाढ़ विस्तार डेटा उपलब्ध नहीं है। प्रेक्षित परिदृश्य उपलब्ध परतों का संयुक्त रूप है। |
| `gap.roads` | Roads are current OpenStreetMap roads, not 2015 roads. | சாலைகள் தற்போதைய OpenStreetMap சாலைகள்; 2015 சாலைகள் அல்ல. | सड़कें वर्तमान OpenStreetMap की हैं, 2015 की नहीं। |
| `expl.baseline_blocked` | The conventional route to {baseline_facility} crosses {n_blocked} blocked road segment(s) under the {scenario} scenario, so it is not drivable. | {scenario} சூழ்நிலையில், {baseline_facility} நோக்கிய வழக்கமான வழித்தடம் {n_blocked} தடைபட்ட சாலைப் பகுதி(களை) கடக்கிறது; எனவே அதில் பயணிக்க இயலாது. | {scenario} परिदृश्य में {baseline_facility} तक का पारंपरिक मार्ग {n_blocked} अवरुद्ध सड़क खंड(ों) से गुज़रता है, इसलिए उस पर वाहन नहीं चलाया जा सकता। |
| `expl.reachable_longer` | The nearest reachable facility offering {service} is {facility}, {time} minutes away, {delta} minutes longer than the conventional route. | {service} வழங்கும், அடையக்கூடிய அருகிலுள்ள வசதி {facility}; இது {time} நிமிடங்கள் தொலைவில் உள்ளது, வழக்கமான வழித்தடத்தை விட {delta} நிமிடங்கள் அதிகம். | {service} प्रदान करने वाली निकटतम पहुँच योग्य सुविधा {facility} है, जो {time} मिनट दूर है, पारंपरिक मार्ग से {delta} मिनट अधिक। |
| `expl.reachable_shorter` | The nearest reachable facility offering {service} is {facility}, {time} minutes away, {delta} minutes shorter than the conventional route. | {service} வழங்கும், அடையக்கூடிய அருகிலுள்ள வசதி {facility}; இது {time} நிமிடங்கள் தொலைவில் உள்ளது, வழக்கமான வழித்தடத்தை விட {delta} நிமிடங்கள் குறைவு. | {service} प्रदान करने वाली निकटतम पहुँच योग्य सुविधा {facility} है, जो {time} मिनट दूर है, पारंपरिक मार्ग से {delta} मिनट कम। |
| `expl.unreachable_all` | No suitable facility is reachable from this origin under the {scenario} scenario. | {scenario} சூழ்நிலையில் இந்தத் தொடக்கப் புள்ளியிலிருந்து பொருத்தமான எந்த வசதியையும் அடைய முடியாது. | {scenario} परिदृश्य में इस आरंभ बिंदु से कोई उपयुक्त सुविधा पहुँच योग्य नहीं है। |

### 6A.4 Critical Keys

The following keys are **critical** and must be reviewed by a fluent speaker before the demo is recorded (I18N-13): `banner.simulation`, `note.indicative`, `gap.*`, `label.placeholder_weights`, `result.unreachable`, `expl.*`, `scenario.mild`, `scenario.moderate`, `scenario.severe`. A mistranslation that drops "simulated", "indicative" or "not a prediction" breaks the claims policy (Section 0.5).

### 6A.5 Interface Helpers

`t(key, **params)` returns the string in the active language with placeholders filled. `fmt_int(n)` formats with Indian grouping. `fmt_pct(x)` formats a fraction as `NN.N%`. `escape_html(s)` escapes data strings. All are specified in Section 4.12.

---

## Section 7: Explanation Text and Audit Log

### 7.1 Explanation Text

`IMPLEMENTATION REQUIRED`. Template-based, built only from computed facts. No LLM. Every sentence must map to a value in the result structure (test T-13 checks this). The templates live in the i18n dictionaries (Section 6A.3, keys `expl.*`) in English, Tamil and Hindi; the English wording below is the reference, and every language uses the same placeholders (T-28, T-35). Service and scenario names inserted into a template are themselves translated; facility names are not.

Template (fill values from the result):

- If the baseline is not drivable: "The conventional route to {baseline_facility} crosses {n_blocked} blocked road segment(s) under the {scenario} scenario, so it is not drivable."
- If reachable: "The nearest reachable facility offering {service} is {facility}, {time} minutes away, {delta} minutes {longer/shorter} than the conventional route."
- If facilities unreachable: "{k} facility(ies) are unreachable: {names with reasons}."
- Always: "Facility status: {verification_status}. Flood layer: {kind}, source {source}."
- If unreachable overall: "No suitable facility is reachable from this origin under the {scenario} scenario."
- Isolation view (only if built), a separate text block: "Under the {scenario} scenario, {n_units} ward(s) have an isolated share above zero. The highest priority is {unit}, with an estimated {people} people in isolated areas (indicative, assumes an even spread within the ward). Basis: {population_basis}."

### 7.2 Audit Log

`IMPLEMENTATION REQUIRED`. A JSON document downloadable from the UI. Required fields:

| Field | Content |
|---|---|
| `generated_at` | Timestamp |
| `app_version` | Blueprint version |
| `selection` | scenario, origin ID and coordinates, service, include-unverified flag |
| `config` | every config value in effect (all assumptions) |
| `datasets` | each dataset used: ID, URL, licence, access date, kind |
| `flood_layer` | scenario, `kind`, source list, feature count, area |
| `facilities` | the rows used, with verification status, source, verified-on |
| `result` | chosen facility, times, baseline drivable, blocked edges on baseline, unreachable list |
| `metrics` | M1 to M5 for the scenario |
| `limits` | the four standing gaps and extra limits |
| `warnings` | any non-fatal warnings (ward join, stratification, snapping, isolation units excluded) |
| `isolation` | (only if built) scenario, unit basis, the top `ISOLATION_TOP_K` rows of the Section 3.9 table, counts of baseline-disconnected nodes, the isolation assumptions A-13 to A-17 |
| `ui_language` | The interface language active when the log was exported (`en`, `ta` or `hi`); the log's keys are always English |

---

## Section 8: Error Handling and Edge Cases

Errors are Python exceptions with a code, surfaced in the UI as a banner and recorded in the audit log's `warnings` or `errors`.

| Code | Raised by | Meaning | Handling |
|---|---|---|---|
| `GRAPH_BUILD_FAILED` | roads | OSMnx or Overpass failure, empty area | Banner; suggest retry or smaller zone; use cached graph if present |
| `GRAPH_TOO_LARGE` | roads | Over 150,000 edges | Ask the user to shrink `STUDY_AREA` |
| `NO_FLOOD_DATA_FOR_AREA` | flood | No flood feature intersects the zone | Banner; suggest a different zone |
| `DATA_SHAPE_UNEXPECTED` | flood, facilities | A source file differs from Section 2 | Log; stop; report the file and difference; never invent data |
| `FACILITY_VERIFICATION_INVALID` | facilities | `phone_verified` without source or date | Reject the file |
| `AMBULANCE_LABEL_INVALID` | facilities | A start not labelled `simulated` | Reject the file |
| `NO_SUITABLE_FACILITY` | facilities | None left after filtering | Show message; no route |
| `FACILITY_NOT_SNAPPABLE` | facilities | Snap distance over limit | Exclude and warn |
| `ORIGIN_OUTSIDE_AREA` | route | Click outside the study area | Message; ignore the click |
| `ALL_SUITABLE_FACILITIES_UNREACHABLE` | route | No path on `G2` | Result with `reachable=False` (not an exception) |
| `ORIGIN_SET_TOO_SMALL` | metrics | Fewer than `MIN_ORIGINS` | Stop metrics; explain |
| `WEIGHTS_ALL_ZERO` | metrics | Population weights sum to zero | Use placeholder weights with notice |
| `CONFIG_INVALID` | config | Threshold out of order or non-positive | Stop at start-up with the offending key |
| `UNITS_NOT_AVAILABLE` | isolation | No ward or fallback units can be built | Hide the isolation tab; banner; core unaffected |
| `ISOLATION_NO_ELIGIBLE_NODES` | isolation | Every node excluded as baseline-disconnected | Skip isolation for the scenario; explain; core unaffected |
| `ISOLATION_UNIT_EMPTY` | isolation | A unit has too few eligible nodes | Non-fatal: exclude the unit; list it in `warnings` |
| `REFERENCE_ROW_INVALID` | isolation | A reported-area row lacks `source_url` or `source_date` | Reject the row; continue with the others |
| `I18N_LANGUAGE_UNSUPPORTED` | i18n | The `lang` value is not `en`, `ta` or `hi` | Use English; no banner needed |
| `I18N_KEY_MISSING` | i18n | A key is absent in the active language | Show English (or the key); log in `warnings`; a failure in tests |
| `FONT_FALLBACK_USED` | ui_theme | No Tamil or Devanagari font could be confirmed | Non-fatal note on the Data and limits page; U-10 must be checked by eye |

Edge cases to handle explicitly: one-way streets (blocking removes the directed edge, and both directions for two-way roads); disconnected graph components (reachability false, not an error); duplicate facility coordinates; a facility inside the flood polygon (still routable if its node is reachable; warn); an origin node that is itself in a removed component.

---

## Section 9: Honesty, Misuse, and Risk Model

| # | Risk | Vector | Mitigation | Test |
|---|---|---|---|---|
| R-1 | The demo is mistaken for a live dispatch tool | Viewer reads route and acts | Persistent banner; "indicative decision support" wording; no live data anywhere | UI check U-01 |
| R-2 | Simulated ambulance data is presented as real 108 data | Labels dropped in a screenshot or video | `simulated` on markers, in files, in audit log | T-09, U-02 |
| R-3 | A facility is shown as verified without evidence | Hand-edit of the CSV | V-1 enforced at load; tooltip shows source and date | T-08 |
| R-4 | Simulated scenarios are read as observed floods | Colour or legend confusion | `kind` badge in legend and panel; scenario names say "simulated" | U-03 |
| R-5 | Assumed thresholds are read as measured | Metrics shown without context | Assumptions table in panel and audit log; tooltips | U-04 |
| R-6 | Licence breach | Raw UNOSAT or OpenCity data committed or redistributed | Raw data gitignored; download scripts only; `SOURCES.md` | Phase 10 audit |
| R-7 | Misleading precision | Times shown to the second | Round to whole minutes; show "indicative" | U-05 |
| R-8 | Research figures misapplied | Citing Karnataka's 72% figure for Tamil Nadu | Not used anywhere; documented in Section 5.5 | Review |
| R-9 | Placeholder population weights read as real coverage | Ward join failed | Notice; metric labelled as sample-point share | T-11 |
| R-10 | Privacy | None expected: no personal data is used | No personal data collected; ambulance starts are synthetic | Review |
| R-11 | A wrong ranking misdirects relief | Viewer treats the priority list as an operational order | "Indicative" wording and notes on the tab; no "dispatch order" language; uncertainty shown through scenario comparison | U-08 |
| R-12 | Ward-level people counts read as measured | Even-spread assumption forgotten | Estimated-people label states the assumption; tooltip and tab notes | U-09 |
| R-13 | Baseline-disconnected areas read as flood isolation | OSM fragments or boundary effects | Excluded and counted separately (Section 5.7.2); shown in the audit log | T-20 |
| R-14 | A mistranslation drops "simulated", "indicative" or "not a prediction" | Draft Tamil or Hindi text | Critical keys reviewed before the recording (I18N-13); "original English" line on the Data and limits page; draft notice until reviewed | U-12 |
| R-15 | Longer Tamil or Hindi text hides a disclaimer | Truncation or overflow | Wrap, never truncate (I18N-10) | U-11 |
| R-16 | HTML injection through a facility or ward name | A source file contains markup | Escape every data string (I18N-14) | T-30 |
| R-17 | Missing-glyph boxes in Tamil or Hindi on the demo machine | Font not installed | Font stack with Nirmala UI fallback; optional bundled fonts | U-10 |
| R-18 | The polished dashboard overstates certainty | KPI cards look authoritative | Banner always visible; "indicative" tooltips; sparkline captioned "across scenarios"; no more than one decimal place | U-05, U-12 |

---

## Section 10: Testing Strategy

### 10.1 Test Levels

| Level | Scope | Tooling |
|---|---|---|
| Unit | Each module's pure functions | pytest |
| Integration | Pipeline from graph to metrics on the synthetic fixture and on the real study area | pytest |
| UI smoke | The app starts and renders each scenario | Manual checklist (Section 15) plus an automated import-and-run smoke test where possible |

### 10.2 Synthetic Fixture

A tiny deterministic graph (for example a 5 by 5 grid of nodes with known edge lengths and speeds, three facilities, and one flood polygon that covers a known set of edges). All metric tests use it, so expected values can be computed by hand and written into the tests as golden values.

### 10.3 Test Matrix

| ID | Test | Expected |
|---|---|---|
| T-01 (critical) | Mark an edge on the baseline path as flooded and re-route | The flood-aware path differs and avoids that edge |
| T-02 (critical) | Origin in a component disconnected after flooding | `reachable=False`, reason given, no exception |
| T-03 (critical) | Chosen facility service check | The chosen facility's service equals the requested service; a nearer facility with `service = unknown` is never chosen |
| T-04 | Edge classification on the Section 5.2 worked example | Classes and times reproduce exactly |
| T-05 | Original graph unchanged after `modify` | Node and edge counts and attributes identical |
| T-06 | Scenario ordering | Area(severe) >= Area(observed) >= Area(mild) |
| T-07 | Flood layer schema | All Section 3.2 columns, valid enums, valid geometries |
| T-08 | Facility verification rule V-1 | A `phone_verified` row without source or date raises `FACILITY_VERIFICATION_INVALID` |
| T-09 | Ambulance label rule | A row not labelled `simulated` raises `AMBULANCE_LABEL_INVALID` |
| T-10 | Metrics golden values on the fixture | M1 to M5 match hand-computed values |
| T-11 | Ward join fallback | If the match rate is below the cut-off, weights are 1.0 and the notice flag is set |
| T-12 | Determinism | Same seed gives identical origin set and robustness values |
| T-13 | Explanation grounding | Every number and name in the text appears in the result structure |
| T-14 | Audit log completeness | All Section 7.2 fields present and non-empty where required |
| T-15 | Tie-breaking | Equal-time facilities are chosen by verification rank, then ID |
| T-16 | Config validation | `FLOOD_FRACTION_AT_RISK >= FLOOD_FRACTION_BLOCKED` raises `CONFIG_INVALID` |
| T-17 | Tunnel rule off by default | With the flag false, a tunnel edge near flood is not blocked by this rule |
| T-18 | Download size guard | A file over 100 MB aborts with a clear message |
| T-19 | Node classified `isolated` | On the fixture, a node reachable to a facility on `G` but not on `G2` is `isolated` |
| T-20 | Baseline-disconnected exclusion | A node with no baseline access is excluded from `E_u`, counted in `nodes_baseline_disconnected`, never `isolated` |
| T-21 | Node classified `delayed` | A node whose time increase is exactly `ISOLATION_DELAY_MIN` is `delayed`; one minute less is `ok` |
| T-22 (critical for the isolation view) | Ranking order | The Section 5.7.5 example ranks Z, X, Y; an equal-population fully cut-off unit outranks a partly cut-off one; equal score ties follow the tie-break order |
| T-23 | Placeholder and fallback basis | Failed ward join gives `population_basis = placeholder` and the notice flag; missing polygons give grid units named `Zone r{row}c{col}` |
| T-24 | Determinism and no mutation | Same inputs give identical tables; `G` and `G2` are unchanged by the isolation call |
| T-25 | Bounds | `estimated_people_isolated` is never greater than `population`; shares are within 0 and 1 |
| T-26 | Reference file handling | A missing file gives no error and an empty validation panel; a row without `source_url` raises `REFERENCE_ROW_INVALID` |
| T-27 | Dictionary key parity | `en`, `ta` and `hi` have identical key sets |
| T-28 | Placeholder parity | For every key the set of `{placeholders}` is identical in all three languages |
| T-29 | Completeness | No empty string; every critical key (Section 6A.4) present and non-empty in all three languages |
| T-30 | HTML escaping | A facility name containing markup renders as text in every component that builds HTML |
| T-31 | Number formatting | `fmt_int(1234567)` gives `12,34,567`; `fmt_int(999)` gives `999`; `fmt_pct(0.1234)` gives `12.3%` |
| T-32 | Fallback | A key missing in `ta` returns the English text and logs `I18N_KEY_MISSING`; an unsupported language code falls back to English |
| T-33 | KPI golden values | K1 to K5 and their change lines on the synthetic fixture match hand-computed values; K1 and K5 have no change line |
| T-34 | Chart data builders | Tick values equal the conventional metric; the sparkline order is observed, mild, moderate, severe; unreachable origins sort first in C6 |
| T-35 | Explanation templates | In all three languages the explanation text for a fixture result contains the same facts and no unfilled braces |

### 10.4 UI Checklist Items (manual)

U-01 banner visible on all states; U-02 `simulated` visible on origin marker; U-03 `kind` badge in legend; U-04 assumptions table present; U-05 times rounded to whole minutes; U-06 switching all four scenarios updates map, routes, and metrics; U-07 audit download opens as valid JSON; U-08 (if PHASE 8 built) the isolation tab shows the "indicative" notes and no "dispatch order" wording; U-09 (if PHASE 8 built) the estimated-people column states the even-spread assumption; the tab is hidden when isolation tables are absent; U-10 Tamil and Hindi render with no missing-glyph boxes on the demo machine; U-11 long Tamil and Hindi strings wrap and the banner is never truncated; U-12 the banner and the limits are visible in all three languages; U-13 switching language changes every visible string, including chart titles, legends, tooltips, buttons and download labels; U-14 every chart has a "View data" table; U-15 every KPI change line shows arrow, signed number and a word.

---

## Section 11: Performance and Caching Targets

These are design targets, not load-tested.

| Item | Target |
|---|---|
| App first load (graph cached) | Under 10 s |
| Scenario switch | Under 5 s |
| Metrics for 20 origins, 4 scenarios | Under 60 s total, computed once and cached |
| Robustness (50 runs) | Under 60 s; cache per scenario |
| Graph build (first time, network) | Under 3 min; cached as GraphML |
| Isolation tables, 4 scenarios (two multi-source passes each) | Under 30 s total; cached per scenario |
| Language switch | Under 2 s |
| Overview page with all cards (data cached) | Under 10 s |

Caching: use `st.cache_resource` for the graph and `st.cache_data` for classification tables and metrics, keyed on scenario and config hash. Pre-compute metrics for all four scenarios at start-up or on first demand and store in `data/processed/metrics_*.json`.

---

## Section 12: Configuration, Repository, and Documentation Requirements

### 12.1 `config.py` (all values are assumptions unless noted)

| Key | Default | Note |
|---|---|---|
| `STUDY_AREA` | set by the user | A small zone with flood points and at least 3 candidate facilities |
| `CRS_GEO`, `CRS_METRIC` | EPSG:4326, EPSG:32644 | UTM 44N covers Chennai |
| `FLOOD_FRACTION_AT_RISK` | 0.10 | A-01 |
| `FLOOD_FRACTION_BLOCKED` | 0.50 | A-02 |
| `AT_RISK_TIME_MULTIPLIER` | 3.0 | A-03 |
| `POINT_BUFFER_M` | 75 | A-04: radius applied to flood points |
| `SCENARIO_BUFFER_M` | mild -100, moderate 0, severe +150 | A-09 |
| `ROBUSTNESS_RUNS`, `ROBUSTNESS_BUFFER_RANGE_M` | 50, (-100, 150) | A-07 |
| `COVERAGE_THRESHOLD_MIN` | 30 | A-06, not an official standard |
| `N_ORIGINS`, `MIN_ORIGINS` | 20, 10 | |
| `MIN_FLOOD_ADJACENT_ORIGINS`, `FLOOD_ADJACENT_RADIUS_M` | 5, 300 | A-10 |
| `MAX_SNAP_DISTANCE_M` | 300 | A-11 |
| `TREAT_TUNNELS_AS_FLOOD_SENSITIVE`, `TUNNEL_SENSITIVITY_RADIUS_M` | False, 50 | A-08 |
| `INCLUDE_UNVERIFIED_FACILITIES` | True | Facilities show their status either way |
| `RANDOM_SEED` | 42 | |
| `MAX_DOWNLOAD_MB` | 100 | DATA-4 |
| `ISOLATION_DELAY_MIN` | 15 | A-13: extra minutes at which a node counts as delayed |
| `ISOLATION_DELAY_WEIGHT` | 0.5 | A-14: weight of the delayed share in the score |
| `ISOLATION_TOP_K` | 10 | Rows shown, and the K used in validation |
| `ISOLATION_FALLBACK_GRID_M` | 1000 | Grid cell size if ward polygons are unavailable |
| `MIN_ELIGIBLE_NODES_PER_UNIT` | 5 | A-17 |
| `REFERENCE_AREAS_PATH` | `data/reference/reported_isolated_areas.csv` | Optional |
| `DEFAULT_LANGUAGE`, `SUPPORTED_LANGUAGES` | `en`, (`en`, `ta`, `hi`) | I18N-1 |
| `FONT_STACK` | Section 6.10 stack | Used by CSS and charts |
| `BUNDLE_FONTS` | False | True only after the user approves the font download |
| `THEME` | Section 6.10 tokens | Approximate by eye (A-21) |

### 12.2 Required Documentation

| File | Contents | Priority |
|---|---|---|
| `README.md` | What it is and is not, run instructions, observed vs simulated, the four gaps, link to `SOURCES.md` | P0 |
| `SOURCES.md` | Per dataset: ID, URL, licence, access date, attribution | P0 |
| `docs/DATA_LIMITS.md` | Standing gaps, ward-join result, licence conflicts, assumption table | P0 |
| `CLAUDE.md` | The rules in Section 13.1 | P0 |
| `requirements.txt` | Pinned library versions, including a Streamlit version that supports bordered containers and Material icons (confirm in PHASE 0) and the Altair version installed with it | P0 |
| `docs/DEMO_SCRIPT.md` | Section 15 | P1 |
| `docs/ARCHITECTURE.md` | Short pointer to Section 4 of this blueprint | P2 |
| `docs/TRANSLATION_REVIEW.md` | For each of `ta` and `hi`: reviewer name, date, keys checked, corrections made, status | P1 (critical keys before the recording) |
| `docs/PREVIEW_LOG.md` | One entry per preview checkpoint: date, checkpoint, what was shown, the user's decision, changes made | P0 |

---

## Section 13: Claude Code Implementation Rules (Worked Examples)

### 13.1 Project Rules (paste into `CLAUDE.md`)

- Python 3.11; osmnx, networkx, geopandas, shapely, numpy, pandas, streamlit, streamlit-folium, folium, altair (installed with Streamlit), pytest only.
- No database, Docker, LLM calls, or JavaScript frontend.
- Every data feature carries source, date, and an observed or simulated flag.
- Never present simulated ambulance data as real 108 data.
- A facility is `phone_verified` only with a source and `verified_on` date.
- Never create fake data and present it as real. Synthetic data carries `label=simulated`.
- Do not download any file over 100 MB without asking.
- Keep raw third-party data out of git; commit download scripts.
- One small Chennai zone; each step runs in under 30 seconds.
- Write and run tests for each step before the next. Ask before installing packages or changing the stack.
- Every user-visible string comes from `i18n/{en,ta,hi}.json` through `t()`. Add any new key to all three files in the same commit and mark it draft.
- Escape every data string (facility names, ward names, file contents) before placing it in HTML.
- Tamil and Hindi strings are drafts until a reviewer signs off in `docs/TRANSLATION_REVIEW.md`; never describe them as professionally translated.
- Never drop "simulated", "indicative" or "not a prediction" from any language.
- At every preview checkpoint (Section 14.12) run the app, show a screenshot or live preview, state what is real and what is a placeholder, log it in `docs/PREVIEW_LOG.md`, and stop until the user approves. Never present a mockup as a real screenshot.

### 13.2 Worked Example: `classify_edges`

- **WHAT:** compute each edge's flooded fraction and class for one scenario.
- **WHERE:** `src/impact.py`.
- **WHY:** FR4; the basis of every route difference.
- **INPUT:** the graph, a scenario GeoDataFrame, config thresholds.
- **OUTPUT:** a table `edge_id, flooded_fraction, class` for every edge, in a stable order.
- **DATA:** both inputs are projected to EPSG:32644 before geometry operations; the flood polygon is merged to one geometry first for speed.
- **ERRORS:** `EDGE_GEOMETRY_MISSING` handled by a straight-line fallback with a logged count; `CONFIG_INVALID` if thresholds are out of order.
- **TESTS:** T-04, T-05, T-16; an edge exactly at 0.50 is `blocked`; an edge with 0.0 is `passable`.

### 13.3 Worked Example: `flood_aware_route`

- **WHAT:** compute the flood-aware route and unreachable facility list from one origin.
- **WHERE:** `src/route.py`.
- **WHY:** FR6, FR7, FR8.
- **INPUT:** `G`, `G2`, origin node, suitable facilities, the edge classification.
- **OUTPUT:** the structure in Section 4.7.
- **DATA:** shortest paths computed to all suitable facility nodes with `travel_time` weights.
- **ERRORS:** `ORIGIN_NOT_SNAPPABLE`; no exception for unreachable facilities.
- **TESTS:** T-01, T-02, T-03, T-15.

### 13.4 Worked Example: `compute_metrics`

- **WHAT:** compute M1 to M5 for one scenario.
- **WHERE:** `src/metrics.py`.
- **WHY:** FR10, FR11.
- **INPUT:** graphs, scenario layers, facilities, origins with weights, config.
- **OUTPUT:** a dictionary of metrics and the origin-level details used for each.
- **DATA:** population weights from `wards_population.csv` or placeholders (Section 2.4).
- **ERRORS:** `ORIGIN_SET_TOO_SMALL`, `WEIGHTS_ALL_ZERO`.
- **TESTS:** T-10, T-11, T-12.

### 13.5 Worked Example: `load_facilities`

- **WHAT:** load and validate `facilities.csv`.
- **WHERE:** `src/facilities.py`.
- **WHY:** FR9; protects the project's credibility (R-3).
- **INPUT:** the CSV path and the include-unverified flag.
- **OUTPUT:** a validated table with `node_id` and snap distance for each facility.
- **ERRORS:** `FACILITY_VERIFICATION_INVALID`, `NO_SUITABLE_FACILITY`, `FACILITY_NOT_SNAPPABLE`.
- **TESTS:** T-03, T-08.

### 13.6 Worked Example: `compute_isolation` (extra view)

- **WHAT:** produce the ward-level isolation table for one scenario.
- **WHERE:** `src/isolation.py`.
- **WHY:** FR15; R-11, R-12, R-13.
- **INPUT:** `G`, `G2`, suitable facilities, unit polygons with populations, config.
- **OUTPUT:** the Section 3.9 table, stable-ordered, plus warnings.
- **DATA:** two multi-source shortest-path passes on the reversed graphs, one per graph; nodes assigned to units by point-in-polygon in EPSG:32644.
- **ERRORS:** `UNITS_NOT_AVAILABLE`, `ISOLATION_NO_ELIGIBLE_NODES`; `ISOLATION_UNIT_EMPTY` as a warning.
- **TESTS:** T-19 to T-25; the ranking must reproduce the Section 5.7.5 example.

### 13.7 Worked Example: `t` (translation lookup)

- **WHAT:** return the interface string for a key in the active language, with placeholders filled.
- **WHERE:** `src/i18n.py`.
- **WHY:** FR17; I18N-2, I18N-6.
- **INPUT:** a dotted key and keyword parameters.
- **OUTPUT:** a string. Placeholders are filled with already-escaped or numeric values.
- **DATA:** the loaded dictionaries and the active language.
- **ERRORS:** `I18N_KEY_MISSING` falls back to English, then to the key, and logs; a missing placeholder parameter raises a clear error in tests, never a blank in the UI.
- **TESTS:** T-27 to T-32, T-35.

### 13.8 Worked Example: `render_kpi_card`

- **WHAT:** draw one KPI card with label, value, optional change line and sparkline.
- **WHERE:** `src/ui_components.py`, data from `src/charts.py`.
- **WHY:** FR16; R-18.
- **INPUT:** the KPI id (K1 to K5), the four scenario values, the selected scenario, the active language.
- **OUTPUT:** a card with the value (rounded per Section 6.5), a change line of arrow, signed number and word where Section 5.8 defines one, and a sparkline captioned `spark.across_scenarios`.
- **ERRORS:** missing values render a translated no-data state.
- **TESTS:** T-33, T-34, U-15.

### 13.9 Interaction Rules for Claude Code

1. Read this whole document. Do one phase only, then stop and report.
2. After each phase: run tests, show results, list deviations from this document, wait for approval.
3. Ask before: installing packages (conda fallback included), any download over 100 MB, changing the stack.
4. If a source file is missing or different from Section 2, report it and do not substitute invented data.
5. At each preview checkpoint (Section 14.12), run the app, show the preview, say what is real and what is a placeholder, and wait for approval.

---

## Section 14: Final Implementation Order (PHASE 0 to PHASE 12)

`SPECIFICATION COMPLETE`. Thirteen dependency-ordered phases (PHASE 8 is optional and gated). Each has a Goal, Required work (mapped to sections), a Verification step, and a mandatory commit. **Claude Code does not start PHASE N until PHASE N-1's Verification passes and its commit is made.** Phase times total about 16.5 hours for the core phases, plus about 1 hour for the six preview checkpoints (Section 14.12), plus 1.5 hours for the optional PHASE 8. If only one working day is available, follow the one-day cut line in the header and add PHASE 8 only if time remains.

### PHASE 0: Scaffold, Rules, and i18n Skeleton (1 h)

- **Goal:** project skeleton and rules in place.
- **Required work:** folder layout (Section 4.2); `CLAUDE.md` (Section 13.1); `requirements.txt`; `.gitignore` excluding `data/raw/`, `logs/`, `.venv`; empty module files; `config.py` skeleton (Section 12.1) with validation; `i18n/en.json`, `ta.json`, `hi.json` seeded from Section 6A.3 with `_meta` blocks marked `draft`; `src/i18n.py` with `t()`, `fmt_int`, `fmt_pct`, `escape_html` (Section 4.12); confirm the pinned Streamlit version supports bordered containers and Material icons.
- **Verification:** the virtual environment installs; `python -c "import osmnx, geopandas, streamlit"` runs; `pytest` collects zero tests without error; config validation test T-16 passes; i18n tests T-27 to T-29, T-31 and T-32 pass.
- **Git commit:** `git add . && git commit -m "phase-0: scaffold, rules, and config"`.

### PHASE 1: Data Fetch, Sources, Ward-Join Check, and Preview Skeleton (2 h)

- **Goal:** the small datasets are local and documented.
- **Required work:** `fetch_data.py` for D1, D5, D7, D8 (Section 2); `SOURCES.md`; the 100 MB guard (T-18); the ward-join test and result in `docs/DATA_LIMITS.md` (Section 2.4); the **preview skeleton page** (`app.py` with `ui_theme.py` and `ui_components.py`): the banner, left rail, header with the language selector and event pill, five KPI cards and six overview cards showing translated "not built yet" placeholders, so every later checkpoint shows real progress inside the final layout (Section 14.12).
- **Verification:** files exist, total under 100 MB; `SOURCES.md` has a row per dataset; the match rate is logged and the fallback decision is recorded; the skeleton page loads and switches between English, Tamil and Hindi.
- **Preview checkpoint CP-1 (Section 14.12):** show the skeleton page in the final layout, in English, Tamil and Hindi; wait for approval before PHASE 2.
- **Git commit:** `git add . && git commit -m "phase-1: data fetch, sources, ward-join check"`.

### PHASE 2: Road Graph (1 h)

- **Goal:** a cached road graph for the study area.
- **Required work:** `roads.py` (Section 4.3); the synthetic fixture (Section 10.2).
- **Verification:** T-fixture tests pass; real-area graph builds; a path between two nodes is non-empty; the cache reloads identically.
- **Git commit:** `git add . && git commit -m "phase-2: road graph and synthetic fixture"`.

### PHASE 3: Flood Layers and Scenarios (1.5 h)

- **Goal:** four labelled scenario files.
- **Required work:** `flood.py` (Section 4.4); inspect each D1 KML's geometry type and log it (DATA-6).
- **Verification:** T-06, T-07 pass; four GeoJSON files exist with provenance columns; the log lists the geometry type of each source file.
- **Preview checkpoint CP-2 (Section 14.12):** show card C1 with the real flood layers for each scenario, labelled observed, composite or simulated; wait for approval before PHASE 4.
- **Git commit:** `git add . && git commit -m "phase-3: flood layers and scenarios"`.

### PHASE 4: Edge Impact and Graph Modification (1 h)

- **Goal:** classified edges and a flood-modified graph.
- **Required work:** `impact.py` (Sections 4.5, 5.2, 5.3).
- **Verification:** T-04, T-05, T-17 pass.
- **Git commit:** `git add . && git commit -m "phase-4: edge classification and graph modification"`.

### PHASE 5: Facilities, Simulated Starts, Origins (1 h)

- **Goal:** validated facility list and labelled simulated starts.
- **Required work:** `facilities.py` (Section 4.6); `facilities.csv` starter rows (Section 3.3); `ambulance_starts.csv`; origin sampling.
- **Verification:** T-08, T-09, T-03 (facility part) pass; every facility row has a verification status.
- **Preview checkpoint CP-3 (Section 14.12):** show the map with facilities and their verification badges, simulated starts and sample origins; wait for approval before PHASE 6.
- **Git commit:** `git add . && git commit -m "phase-5: facilities, simulated starts, origins"`.

### PHASE 6: Routing and Critical Tests (1.5 h)

- **Goal:** the core comparison works.
- **Required work:** `route.py` (Sections 4.7, 5.4).
- **Verification:** T-01, T-02, T-03, T-15 pass on the fixture and the real area.
- **Git commit:** `git add . && git commit -m "phase-6: baseline and flood-aware routing"`.

### PHASE 7: Metrics and Robustness (1.5 h)

- **Goal:** the five metrics per scenario.
- **Required work:** `metrics.py` (Sections 4.8, 5.5, 5.6).
- **Verification:** T-10, T-11, T-12 pass; a metrics table exists for all four scenarios.
- **Preview checkpoint CP-4 (Section 14.12):** show the KPI cards with real values and sparklines, card C2, and the Metrics table page; wait for approval before PHASE 8 or PHASE 9.
- **Git commit:** `git add . && git commit -m "phase-7: metrics and robustness"`.

### PHASE 8: Isolation Priority View (1.5 h, optional, P1)

- **Goal:** a ward-level isolation ranking for each scenario.
- **Gate:** start only after PHASE 7 passes and the core P0 items of Section 16.4 (1 to 4 and 7 to 8) hold on the core build. If the gate fails or time is short, skip this phase without renumbering, state "isolation view planned, not built" in the README, and let PHASE 9 depend on PHASE 7.
- **Required work:** `isolation.py` (Sections 4.11, 5.7); output tables (Section 3.9); optional reference validation (Sections 3.8, 5.7.6).
- **Verification:** T-19 to T-26 pass; the fixture reproduces the Section 5.7.5 ranking; tables exist for all four scenarios.
- **Git commit:** `git add . && git commit -m "phase-8: isolation priority view"`.

### PHASE 9: Explanation and Audit (1.5 h)

- **Goal:** grounded text and a complete log.
- **Required work:** `explain.py`, `audit.py` (Section 7); explanation templates in English, Tamil and Hindi from the dictionary; the audit `ui_language` field; include the isolation text block and the audit `isolation` field only if PHASE 8 was built.
- **Verification:** T-13, T-14, T-35 pass.
- **Preview checkpoint CP-5 (Section 14.12):** show the Route explorer with both routes, the explanation text in all three languages, the audit download, and the isolation page if PHASE 8 was built; wait for approval before PHASE 10.
- **Git commit:** `git add . && git commit -m "phase-9: explanation text and audit log"`.

### PHASE 10: Real KPI Values, Sparklines, and Polish (1 h)

- **Goal:** the dashboard shell built in PHASE 1 shows real values in all three languages.
- **Required work:** wire the five KPI cards K1 to K5 to real values (Sections 5.8 and 6.5); `charts.py` sparklines; the metric focus toggle and the scenario control working across pages (Section 6.3); language persistence in session and query parameter (I18N-5); polish of the theme (Section 6.10) and the small-text contrast check.
- **Verification:** T-27 to T-35 pass; U-10, U-11, U-12, U-13 and U-15 pass for the shell and KPI row; the contrast of small teal text is checked; the banner is visible on every page in all three languages.
- **Git commit:** `git add . && git commit -m "phase-10: real kpi values, sparklines, and polish"`.

### PHASE 11: Cards and Pages (2.5 h)

- **Goal:** every page and card of Section 6 exists.
- **Required work:** cards C1 and C2 first, then C3 to C6 (Section 6.6) each with a "View data" expander; the Route explorer (6.7); the Isolation page only if PHASE 8 was built (6.8); the Metrics table, Data and limits and Export pages (6.9); all UI states (6.11); complete the remaining translations for every string on these pages.
- **Verification:** U-01 to U-15 pass (U-08 and U-09 only if PHASE 8 was built); load and switch times are within Section 11; the "original English" lines appear on the Data and limits page.
- **Preview checkpoint CP-6 (Section 14.12):** show every page and card in all three languages; wait for approval before PHASE 12.
- **Git commit:** `git add . && git commit -m "phase-11: dashboard cards and pages"`.

### PHASE 12: Documentation, Translation Review, Audit, and Recording (1 h)

- **Goal:** the repository is demo-ready and honest about what is draft.
- **Required work:** `README.md`, `docs/DATA_LIMITS.md`, `docs/DEMO_SCRIPT.md`, `docs/TRANSLATION_REVIEW.md` (Section 12.2); send the critical Tamil and Hindi keys (Section 6A.4) to fluent reviewers and record the result; re-run the Section 16 audit against the finished build; record the 3-minute demo (Section 15).
- **Verification:** every item of Section 16.4 is checked PASS or logged as a known gap with a reason; the demo is run once, start to finish, without a manual fix; the README says "draft translation" for any language not yet reviewed.
- **Git commit:** `git add . && git commit -m "phase-12: documentation, translation review, and final acceptance audit"`.

### 14.11 Git Safety Rules

- One commit per phase, made only after that phase's Verification passes.
- Commit messages follow `phase-N: <description>`; never `wip` or `update`.
- A phase is never committed in a known-broken state.
- Earlier phase commits are never rewritten, squashed, or force-pushed.
- A defect in an earlier phase found later is fixed in a new commit (for example `fix: correct phase-4 tunnel rule found during phase-7 testing`), not by amending history.
- Never commit anything in `data/raw/` or any UNOSAT file.

### 14.12 UI/UX Preview Checkpoints (every two phases)

`SPECIFICATION COMPLETE`. The user must see the interface grow, not only at the end. After every second phase Claude Code runs the app and shows a preview. The preview skeleton built in PHASE 1 makes this possible from the start: the final layout exists early and fills in as phases complete.

| Checkpoint | After | The preview must show | Real or placeholder |
|---|---|---|---|
| CP-1 | PHASE 1 | The skeleton page in the final layout: banner, left rail, header (title, event pill, focus toggle, scenario control, language selector), five KPI cards and six overview cards with translated "not built yet" placeholders, in English, Tamil and Hindi | Layout, theme and language switch are real; all data is placeholder |
| CP-2 | PHASE 3 | Card C1 with the real flood layers for each scenario, each labelled observed, composite or simulated, and the road graph outline | Flood layers real or simulated; no routes yet |
| CP-3 | PHASE 5 | The map with facilities and their verification badges, simulated ambulance starts and sample origins; the facility status card | Facility list is a proxy; starts are simulated |
| CP-4 | PHASE 7 | The five KPI cards with real values and sparklines, card C2 with ticks, and the Metrics table page | Values are real for the study zone; thresholds are assumptions |
| CP-5 | PHASE 9 | The Route explorer with both routes, the explanation text in all three languages, the audit download, and the isolation page if PHASE 8 was built | Tamil and Hindi text are draft |
| CP-6 | PHASE 11 | Every page and card in all three languages, including Data and limits and Export | The full dashboard |

**Procedure at every checkpoint:**

1. Finish the Verification steps of the two phases first.
2. Run the app. Capture a screenshot of each page that exists at desktop width (1280 px or more) in English, and in Tamil and Hindi for the pages that changed.
3. Show the screenshots or the live preview to the user. If the environment has no screenshot or preview tool, say so, give the exact command to run the app, and describe each screen in words. **Never draw or generate a mockup and present it as a real screenshot.** A static mockup is allowed only if it is labelled "static mockup".
4. List explicitly: what is real, what is a placeholder, what is observed and what is simulated, and anything that deviates from this blueprint.
5. Check and report: the banner is visible, the language switch changes every visible string, no text is truncated, and Tamil and Hindi show no missing-glyph boxes.
6. Record the checkpoint in `docs/PREVIEW_LOG.md`: date, checkpoint, what was shown, the user's decision (approved or changes requested), and the changes made.
7. **Stop and wait.** Do not start the next phase until the user approves or gives changes. Requested changes are made in a new commit before continuing.

**One-day cut line:** keep only CP-2, CP-4 and CP-6.

---

## Section 15: Demo Script and Recording Checklist

### 15.1 Three-Minute Script

1. (20 s) Problem: a normal route can cross a flooded road, and a pregnant patient's ambulance loses time.
2. (30 s) Overview page, observed scenario: read the five KPI cards and the change versus conventional routing; point out the banner.
3. (40 s) Switch to the severe scenario: KPI changes, blocked roads on the map, coverage bars with the conventional tick.
4. (40 s) Route explorer: pick a simulated start; show the conventional route and the flood-aware route, the new facility and the written reason.
5. (25 s, only if PHASE 8 was built) Isolation page: the ranked wards, with the indicative notes and the scenario comparison.
6. (25 s) Switch the language to Tamil and then Hindi on the same page: every label, chart title and the banner change; facility names stay as in the source.
7. (20 s) Data and limits page and Export: state what is simulated, what is unverified, and that the Tamil and Hindi text is draft or reviewed (whichever is true).

### 15.2 Recording Checklist

- [ ] The banner and the `simulated` labels are visible in the frames, in every language shown.
- [ ] The scenario badges say simulated for mild, moderate and severe.
- [ ] No facility shows as phone-verified unless the CSV has a source and a date.
- [ ] Tamil and Hindi render without missing-glyph boxes.
- [ ] The narration never says "real ambulance times", "live", "predicts floods" or "professionally translated" (unless true).
- [ ] The final frames show the standing limits.

---

## Section 16: Consistency Audit Log, Assumptions Register, Acceptance Checklist

`SPECIFICATION COMPLETE`.

### 16.1 Pre-Build Consistency Checks Already Performed (from the research session)

| # | Finding | Resolution in this blueprint |
|---|---|---|
| 1 | Census 2011 lists 155 wards but the DataMeet file has 201 features | Ward-join test and fallback (Section 2.4) |
| 2 | OpenCity's dataset-level "Public Domain" tag conflicts with the portal's CC BY-NC-SA 4.0 and ODbL statement | Cite OpenCity and original sources; ask opencity@oorvani.in (Section 2.1, 12.2) |
| 3 | The "72% within 30 minutes" ambulance figure comes from a Karnataka audit, not Tamil Nadu | Not used; explicit rule in Section 5.5 and R-8 |
| 4 | The UNOSAT record labelled "4 Dec" has no layer for the 1-4 Dec peak | Documented in D3 and Section 2.3 |
| 5 | Some research links pointed to API addresses, not readable pages | Dataset pages used in Section 2.1 |
| 6 | One research agent downloaded the 67 MB UNOSAT zip by mistake and deleted it unread | D3 geometry, fields and CRS are unverified; the build defaults to not downloading it |
| 7 | Most dataset files were never opened; only metadata or one KML was read | Per-dataset "Research status" column; DATA-6 and `DATA_SHAPE_UNEXPECTED` |
| 8 | The isolation-ranking idea said the tool would "predict" areas that lose access, but no rainfall or terrain flood model exists in this build | Prediction claim removed; the view assesses observed and simulated scenarios only (Sections 0.4, 0.5, 5.7.7) |
| 9 | A naive isolation count would treat nodes that are already disconnected in OSM as flood-isolated | Baseline-disconnected exclusion rule (Section 5.7.2), test T-20 |
| 10 | The earlier time budget in Version 1.0 said about 12 hours, but its phase times add to 13 hours | Corrected in Version 1.1; revised again in 2.0 (see row 15) |
| 11 | In the dashboard, "route feasibility" and "reachability of at least one suitable facility" would show the same number | K2 is the any-facility share; K3 is the per-facility mean; M2b and M3 (any) documented as one quantity (Section 5.8) |
| 12 | The reference dashboard's "change versus prior year" has no direct equivalent | Replaced by "change versus conventional routing" only where a conventional counterpart exists (Section 5.8) |
| 13 | The reference's sparkline is a time series; the scenarios are not | Sparkline defined across the four scenarios in fixed order and captioned "across scenarios" |
| 14 | The Tamil and Hindi strings in Section 6A.3 were written by an AI assistant | Marked draft; review required (I18N-13, checklist item 38) |
| 15 | The Version 1.1 time budget did not include the dashboard and language work | Revised to about 16 hours core plus 1.5 hours optional, with a one-day cut line |
| 16 | Basemap tile labels cannot follow the interface language | Stated as a limit on the Data and limits page (I18N-11) |
| 17 | With the dashboard shell planned for PHASE 10, early UI previews would show nothing | A preview skeleton page moves into PHASE 1 and fills in phase by phase (Section 14.12); budget revised to about 17.5 hours |

### 16.2 Assumptions Register

| ID | Assumption | Where used |
|---|---|---|
| A-01 | At-risk threshold 0.10 of edge length flooded | Section 5.2 |
| A-02 | Blocked threshold 0.50 | Section 5.2 |
| A-03 | At-risk time multiplier 3.0 | Section 5.2 |
| A-04 | Point buffer radius 75 m | Section 4.4 |
| A-05 | OSMnx imputed speeds represent comparative, not absolute, travel times | Section 5.1 |
| A-06 | 30-minute coverage threshold is an analysis parameter, not a standard | Section 5.5 |
| A-07 | Robustness buffer range -100 m to +150 m | Section 5.6 |
| A-08 | Tunnel sensitivity radius 50 m | Section 5.3 |
| A-09 | Scenario buffers mild -100 m, moderate 0 m, severe +150 m | Section 4.4 |
| A-10 | Flood-adjacent origin radius 300 m, minimum 5 origins | Section 5.5 |
| A-11 | Maximum snap distance 300 m | Section 4.6 |
| A-12 | 90% ward-join match rate to use real weights | Section 2.4 |
| A-13 | A node counts as delayed at 15 or more extra minutes | Section 5.7.2 |
| A-14 | The delayed share counts at half the weight of the isolated share | Section 5.7.4 |
| A-15 | Population is spread evenly across a ward's road nodes | Section 5.7.7 |
| A-16 | Census 2011 ward populations are an acceptable, if old, population basis | Section 5.7.7 |
| A-17 | A unit needs at least 5 eligible nodes to be ranked | Section 5.7.3 |
| A-18 | Indian digit grouping with Western digits is used in all three languages | I18N-8 |
| A-19 | Tamil and Hindi text can be 30 to 50 percent longer than English | I18N-10, Section 6.12 |
| A-20 | The sparkline over four scenarios in a fixed order is a fair compact summary | Section 5.8 |
| A-21 | The theme colours approximate the reference image by eye; they are not sampled values | Section 6.10 |

None of these is measured or sourced from an official standard. The UI and audit log must display them.

### 16.3 Known Remaining Simplifications (Intentional, Not Defects)

One study zone, one service type, historical data only, simulated ambulances, a proxy facility list, current (not 2015) roads, no traffic or road-capacity modelling, no flood depth modelling beyond the polygon rule, no live feeds.

### 16.4 Acceptance Criteria Checklist

- [ ] 1. `pytest` passes, including the critical tests T-01, T-02, T-03.
- [ ] 2. All tests T-04 to T-18 pass (and T-19 to T-26 if PHASE 8 was built).
- [ ] 3. `streamlit run app.py` loads in under 10 seconds on the default scenario.
- [ ] 4. Switching among the four scenarios changes the map, routes, and metrics.
- [ ] 5. Every flood layer shows source, date, `kind`, and a badge in the UI.
- [ ] 6. Every dataset in the data panel shows ID, link, licence, and date.
- [ ] 7. No facility is displayed as phone-verified without a source and `verified_on`.
- [ ] 8. Every ambulance start shows `simulated`.
- [ ] 9. The banner is visible in every state, including errors.
- [ ] 10. The data and limits panel lists all four standing gaps and the current assumptions.
- [ ] 11. The five metrics appear for each scenario with their definitions available.
- [ ] 12. Robustness output is identical on two runs with the same seed.
- [ ] 13. Explanation text contains no value absent from the result structure.
- [ ] 14. The audit log downloads as valid JSON containing every Section 7.2 field.
- [ ] 15. A disconnected origin shows a clear message and no crash.
- [ ] 16. The ward-join result is recorded; the notice appears if placeholders are used.
- [ ] 17. `SOURCES.md` lists licence, URL, and access date for every dataset used.
- [ ] 18. No raw third-party data and no UNOSAT file is in git.
- [ ] 19. `README.md` states what is simulated, what is unverified, and the four gaps.
- [ ] 20. The claims policy (Section 0.5) is satisfied in the UI text and README.
- [ ] 21. No download over 100 MB was made without approval.
- [ ] 22. The demo was run end to end once without a manual fix mid-run.
- [ ] 23. A 3-minute recording exists and passes the Section 15.2 checklist.
- [ ] 24. Every phase has exactly one commit with the `phase-N:` convention.
- [ ] 25. Every requirement's status tag is updated honestly (`DEMO-VERIFIED` only if exercised in the demo flow).
- [ ] 26. (If PHASE 8 built) Tests T-19 to T-26 pass, including the Section 5.7.5 ranking.
- [ ] 27. (If PHASE 8 built) Nodes already disconnected in the baseline are excluded and counted, never reported as flood isolation.
- [ ] 28. (If PHASE 8 built) The isolation tab shows the "indicative" and even-spread notes and no "predicts" or "dispatch order" wording.
- [ ] 29. (If PHASE 8 built) Placeholder population shows the notice and relabels the people column.
- [ ] 30. (If PHASE 8 built) The audit log contains the `isolation` field with assumptions A-13 to A-17.
- [ ] 31. (If PHASE 8 skipped) The README states "isolation view planned, not built" and the tab is absent.
- [ ] 32. The Overview page has the banner, left rail, header controls and five KPI cards.
- [ ] 33. Each KPI shows value, a tooltip definition and a sparkline across scenarios; K2 to K4 show a change line (arrow, signed number, word); K1 and K5 show none.
- [ ] 34. Cards C1 and C2 exist (C3 to C6 if built), each with a "View data" table.
- [ ] 35. The language selector switches English, Tamil and Hindi and updates every visible string, including chart titles, legends, tooltips, buttons and download labels (U-13).
- [ ] 36. Tests T-27 to T-29 pass and a grep finds no hard-coded user-visible string in code.
- [ ] 37. Tamil and Hindi render without missing-glyph boxes on the demo machine (U-10).
- [ ] 38. The critical strings were reviewed by fluent speakers and recorded in `docs/TRANSLATION_REVIEW.md`, or the README and the Data and limits page say "draft translation".
- [ ] 39. Data strings (facility and ward names) are HTML-escaped (T-30).
- [ ] 40. Numbers use Western digits with Indian grouping in all three languages (T-31).
- [ ] 41. Exports (audit JSON, metrics CSV, facilities CSV) are language-neutral and include `ui_language`.
- [ ] 42. The Data and limits page lists the basemap-label limitation and the translation status.
- [ ] 43. A preview was shown to the user after each of PHASE 1, 3, 5, 7, 9 and 11 (or the three cut-line checkpoints), with the decision logged in `docs/PREVIEW_LOG.md`.
- [ ] 44. Every preview stated what was real and what was a placeholder, and no mockup was presented as a real screenshot.
- [ ] 45. The skeleton page loads in all three languages from PHASE 1 onward.

### 16.5 Open Decisions for the User (Claude Code must ask, not assume)

1. Which small Chennai zone is `STUDY_AREA`? It must contain flood points and at least 3 candidate facilities.
2. Which facilities are phone-verified, and who made the calls, on which date?
3. May the optional 67 MB UNOSAT layers be downloaded (P2)?
4. Is the final deliverable run locally with a screen recording, or deployed? (A free Streamlit hosting option exists; its limits were not verified.)
5. Who compiles `reported_isolated_areas.csv` (P2), from which news sources, and on what date? Without it the isolation view has no validation reference.
6. Who reviews the Tamil strings and who reviews the Hindi strings, and by what date?
7. May the Noto Sans Tamil and Noto Sans Devanagari fonts (small OFL-licensed files) be downloaded and bundled, or should the demo rely on system fonts such as Nirmala UI?
8. Must the demo run offline? Map tiles and the first road-graph download need internet unless cached beforehand.
