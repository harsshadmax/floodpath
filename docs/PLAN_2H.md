# 2-Hour Plan: FloodPath-Care cut build

Supersedes the full 17.5-hour schedule in `blueprint.md` Section 14 for this run. The blueprint's honesty rules (Section 0.5, 12) and data rules still apply in full. Only scope and process are cut.

## What the 2-hour build delivers
- Dashboard in the final layout: banner, left rail, header (event pill, scenario control, language selector), KPI cards K1 to K4 and a light K5, map card C1, coverage-by-scenario card C2, road-class card C4.
- Pages: Overview, Route explorer, Data and limits (with the four gaps and assumptions). Audit log (JSON) download.
- Scenarios: observed composite plus mild, moderate, severe (simulated).
- Routing: conventional vs flood-aware routes to the nearest suitable facility; unreachable handling; explanation text.
- Metrics: travel-time increase, route feasibility, facility reachability, coverage, light robustness (20 runs).
- Languages: English, Tamil, Hindi from the Section 6A.3 dictionary (Tamil and Hindi stay **draft**).

## What is cut (listed as planned work in the README)
- Isolation priority view (PHASE 8), cards C3, C5, C6, Metrics table page, Export page beyond the audit JSON.
- Ward-level population: the ward join is skipped; coverage uses equal weights and shows the placeholder notice (blueprint Section 2.4). It is a share of sample points, not of people.
- The 4 NHM-listed hospitals (no coordinates). Only the 5 GCC 24x7 obstetric units are used, all shown as **unverified** (no phone verification is possible in 2 hours).
- Full test suite. Kept: i18n parity, config validation, and the three critical routing tests (T-01, T-02, T-03), plus T-30 escaping.
- Preview checkpoints: three only (minutes 45, 90, 115), per the blueprint's cut line.

## Timeline (120 minutes)
| Minutes | Work | Output |
|---|---|---|
| 0-10 | Finish PHASE 0: `config.py`, i18n files and `i18n.py`, `requirements.txt`, `.gitignore`, `CLAUDE.md`; create venv and install (needs your approval) | Tests for config and i18n pass |
| 10-25 | Fetch the small OpenCity files; inspect their geometry; pick a small study zone with flood points and facilities; preview skeleton page | Zone chosen; skeleton loads in 3 languages |
| 25-45 | Road graph (cached), flood layers, composite and 3 scenarios | **Preview 1 (min 45):** map with flood layers |
| 45-65 | Edge classification, flood-aware graph, routing, unreachable handling; the three critical tests | Routes work on the real zone |
| 65-90 | Facilities, simulated starts, 20 origins, metrics K1 to K4, light robustness; KPI cards and C2, C4 | **Preview 2 (min 90):** KPI row and cards with real values |
| 90-110 | Route explorer, explanation text in 3 languages, Data and limits page, audit download | All three pages working |
| 110-120 | End-to-end run, README, first commit set, **Preview 3 (min 115)**, optional screen recording | Demo-ready |

## Risks that can break the 2 hours
1. **OSM download or graph size:** keep the zone small (under 150,000 edges); cache the graph.
2. **Flood layer surprises:** the OpenCity KMLs were mostly never opened. If the geometry or coordinates differ from the blueprint, the zone choice and composite step take longer.
3. **Install problems on Python 3.13** (the only version installed; the blueprint says 3.11): geopandas, osmnx or streamlit-folium may need different versions. If so, install Python 3.11 (about 10 extra minutes).
4. **Streamlit icon rail and bordered cards** may need the fallback sidebar from Section 6.2.
5. **No preview tool:** if screenshots cannot be captured, previews fall back to run commands and written descriptions.

## Honest limits of the result
- It is a working simulation on public data with a proxy facility list. Facilities are unverified, ambulances are simulated, and the peak flood is not observed.
- Tamil and Hindi text are drafts until a fluent speaker reviews them.
- Thresholds are assumptions.
