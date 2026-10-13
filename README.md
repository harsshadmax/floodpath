# FloodPath-Care

Flood-aware emergency routing to maternal-care facilities: a historical-data-informed **simulation** that compares conventional shortest-path routing with flood-aware routing, using the Chennai 2015 floods as a replay. Built for the Seva First Innovation Challenge (Track A).

**Status: PHASE 2 done (road graph, flood layers, scenarios, map). Not yet a working product: routes, facilities, metrics and KPI values are not built; those cards say "Not built yet".** See `docs/PLAN_2H.md` for the 2-hour cut and `blueprint.md` for the full specification.

## What it is not
Not live data, not a flood predictor, not a dispatch system. Ambulance data is simulated. The facility list is a proxy and is not a clinical certification. Tamil and Hindi text are **draft translations** until reviewed.

## Standing data gaps
1. No public verified list of FRU/CEmONC facilities with coordinates exists for Chennai.
2. No 108 ambulance data is public; ambulance starts and times are simulated.
3. No open flood extent exists for the 1-4 Dec 2015 peak; the observed scenario is a composite of available layers.
4. Current OpenStreetMap roads differ from 2015 roads.

## Setup
Python analysis (tests and, later, the pipeline that writes the data the web app reads):
```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest
```
Data for the map (PHASE 2): download the small OpenCity files, then build the road graph, flood layers and scenarios (needs internet once; the graph is cached):
```
.venv\Scripts\python src\fetch_data.py
.venv\Scripts\python scripts\build_phase2.py
```
This writes `data/processed/` and `web/public/data/` (both gitignored). Without it the map card shows a "run build_phase2.py" message.

Web app (Next.js, in `web/`):
```
cd web
npm install
npm run dev        # http://localhost:3000  (add ?lang=ta or ?lang=hi)
npm run lint
npm run build
```
After changing `i18n/*.json` or `config.py` run `python scripts/export_web_i18n.py` and `python scripts/export_web_config.py` (tests fail if the web copies drift).

Python note: the blueprint says 3.11; this machine has Python 3.13 only. The pinned packages installed on 3.13 without errors; behaviour on 3.11 is untested. The web app uses Node 24 and npm 11; `next/font` downloads Inter and IBM Plex Mono once at dev or build time (needs internet).

## Layout
`config.py` (assumptions), `src/` (Python modules), `i18n/` (English, Tamil, Hindi, the source of truth), `web/` (Next.js interface), `tests/`, `docs/`, `data/raw/` (ignored), `data/processed/`.

## Interface style
The interface follows a supplied reference dashboard image (floating icon rail with a round logo, large raised cards, pill toggles, KPI cards, 3 x 2 card grid) in a **blue** palette instead of the image's teal. A second reference website (shpp3.vercel.app) was reviewed and its thin-border style was not adopted. See blueprint Section 6.13.
