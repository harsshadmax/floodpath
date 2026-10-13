# Sources, licences and attribution

Access date for everything below: 2026-10-13. Raw files live in `data/raw/` (gitignored); `python src/fetch_data.py` re-downloads them. Do not commit raw third-party data.

| ID | Dataset | URL | Files used | Licence note | Used for |
|---|---|---|---|---|---|
| D1 | OpenCity: Chennai Floods 2015 Data | https://data.opencity.in/dataset/chennai-floods-2015-data | 7 KML files (see `data/raw/manifest.json`) | The dataset page tags it Public Domain; the OpenCity portal's About page states CC BY-NC-SA 4.0 and ODbL. The two statements conflict. Cite OpenCity and the original sources; ask opencity@oorvani.in which applies | Flood layers (NRSC inundation polygons, GCC stagnation points, GCC hotspots, crowd-sourced flooded street segments) |
| D5 | OpenCity: Chennai health centres | https://data.opencity.in/dataset/chennai-healthcare-uphcs-and-uchcs | `D5__Chennai_Maternity_Hospitals_Map.kml` (5 points). The other D5 KMLs (UPHC, UCHC, TB, VPHC, animal birth control) were downloaded but are not used | Public Domain tag on the dataset page; same portal-level conflict as above | Facility candidates |
| D4 | OpenStreetMap roads (PHASE 2) | via OSMnx and the Overpass API | Road graph for the study zone | ODbL: credit "© OpenStreetMap contributors" | Road network |

## Attribution text to show in the app and README
Flood layers and facility points: OpenCity (Oorvani Foundation), Greater Chennai Corporation; inundation polygons credited to NRSC by OpenCity. Roads: © OpenStreetMap contributors (ODbL).

## Not used in this build (cut by `docs/PLAN_2H.md`)
D2 depth points, D3 UNOSAT flood layers (CC BY-NC-SA 3.0, 67 MB, never committed), D6 NHM CEmONC list (names only), D7 census 2011 wards, D8 DataMeet ward polygons, D9 relief centres.
