# Data limits and PHASE 1 findings

Everything here was observed by opening the downloaded files on 2026-10-13 (`scripts/inspect_kml.py`, `scripts/choose_zone.py`, `scripts/zone_check2.py`).

## Standing gaps (always shown in the app)
1. No public verified list of FRU/CEmONC facilities with coordinates exists for Chennai. The facility list is a hand-checked proxy and not a clinical certification.
2. No 108 ambulance data is public. Ambulance starts and times are simulated.
3. No open flood extent exists for the 1-4 Dec 2015 peak. The "observed" scenario is a composite of available layers.
4. OpenStreetMap roads are current roads, not 2015 roads.

## What the files actually contain (differences from the blueprint's assumptions)
| Finding | Detail | How the build handles it |
|---|---|---|
| The crowd-sourced flooding layer is **lines**, not points | 7,894 features: 7,856 LineString and 38 MultiLineString; read as flooded street segments | Buffered by `LINE_BUFFER_M` (assumption A-22), not `POINT_BUFFER_M` |
| **No dates** on any flood layer | The `timestamp`, `begin` and `end` fields are empty in all files | Flood layer `date` is recorded as "2015 event (day unknown)" |
| The NRSC inundation layer covers far more than Chennai | 4,001 MultiPolygons spanning 79.35-80.32 E, 12.52-13.33 N; its observation date and sensor are not stated in the file | Clipped to the study zone |
| District hotspot files contain stray points | The Tiruvallur "hotspots" span 78.56-80.33 E and 9.67-13.53 N (it reaches southern Tamil Nadu) | Clipped to the study zone; points outside are ignored |
| The maternity file has **no facility names** | The `Name` field is empty. The file has `ADDRESS`, `ASSET_NAME` (all "UCHC"), `FINAL_CODE` (EOCU_GCHM1 to EOCU_GCHM5) and `TYPE` ("MATERNITY HOSPITALS/EMERGENCY OBSTETRIC CARE UNITS(24 X 7)") | Facility names are derived from the address locality plus the code; the original address is kept in `notes` |
| Only 3 of 5 maternity points fall in the study zone | Shenoy Nagar, Saidapet and Purasaiwalkam are inside; Thoraipakkam and Mugalivakkam are outside | Zone satisfies the "at least 3 facilities" rule |

## Study zone chosen
Central Chennai, bbox W 80.205, S 13.010, E 80.270, N 13.100 (about 70 km2). Inside it: 3 facilities, 217 GCC stagnation points, 87 GCC hotspots, 2,139 crowd-sourced flooded street segments, and about 39% of its area lies within NRSC inundation polygons. Compared with larger zones the coverage of flood data is higher and the road graph is smaller (zone A south corridor 187 km2, 21% inundated; zone B central 132 km2, 31%). This is a decision the user can change at the first preview.

## Decisions taken under the 2-hour plan
- **Ward population join skipped.** Census 2011 (155 wards) and DataMeet ward polygons (201 features) were not downloaded or joined. Population coverage therefore uses equal sample-point weights and shows the placeholder notice (blueprint Section 2.4). It is a share of sample points, not of people.
- **Only the 5 GCC emergency obstetric units are candidate facilities** (3 inside the zone). The 4 NHM-listed CEmONC hospitals are not included (no coordinates). All facilities are `unverified`; no phone verification was done.

## Licence conflicts
See `SOURCES.md`: OpenCity's dataset-level Public Domain tag versus its portal-wide CC BY-NC-SA 4.0 and ODbL statement.
