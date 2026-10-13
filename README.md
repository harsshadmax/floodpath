# FloodPath-Care

Flood-aware emergency routing to maternal-care facilities: a historical-data-informed **simulation** that compares conventional shortest-path routing with flood-aware routing, using the Chennai 2015 floods as a replay. Built for the Seva First Innovation Challenge (Track A).

**Status: PHASE 0 (scaffold). Nothing here is a working product yet.** See `docs/PLAN_2H.md` for the 2-hour cut and `blueprint.md` for the full specification.

## What it is not
Not live data, not a flood predictor, not a dispatch system. Ambulance data is simulated. The facility list is a proxy and is not a clinical certification. Tamil and Hindi text are **draft translations** until reviewed.

## Standing data gaps
1. No public verified list of FRU/CEmONC facilities with coordinates exists for Chennai.
2. No 108 ambulance data is public; ambulance starts and times are simulated.
3. No open flood extent exists for the 1-4 Dec 2015 peak; the observed scenario is a composite of available layers.
4. Current OpenStreetMap roads differ from 2015 roads.

## Setup
```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest
```
Python note: the blueprint says 3.11; this machine has Python 3.13 only. The pinned packages installed on 3.13 without errors; behaviour on 3.11 is untested.

## Layout
`config.py` (assumptions), `src/` (modules), `i18n/` (English, Tamil, Hindi), `tests/`, `docs/`, `data/raw/` (ignored), `data/processed/`.
